use anyhow::Result;
use candle_core::{DType, Device, Tensor, Var};
use candle_nn::init::Init;
use candle_nn::optim::{AdamW, Optimizer as _, ParamsAdamW, SGD};
use pretrainopt_core::{
    Activation, InitMethod, ModelArchitecture, ModelFeatures, Optimizer, TrainingConfig,
    TrialProtocol,
};
use rand::{seq::SliceRandom, SeedableRng};
use rand_chacha::ChaCha8Rng;
use std::time::Instant;

struct DenseLayer {
    weight: Var,
    bias: Var,
    activation: Option<Activation>,
}

impl DenseLayer {
    fn new(
        in_dim: usize,
        out_dim: usize,
        init: InitMethod,
        activation: Option<Activation>,
        device: &Device,
    ) -> Result<Self> {
        let std = match init {
            InitMethod::Xavier => (2.0 / (in_dim + out_dim) as f64).sqrt(),
            InitMethod::He => (2.0 / in_dim as f64).sqrt(),
        };
        let weight = Init::Randn {
            mean: 0.0,
            stdev: std,
        }
        .var((out_dim, in_dim), DType::F32, device)?;
        let bias = Init::Const(0.0).var(out_dim, DType::F32, device)?;
        Ok(Self {
            weight,
            bias,
            activation,
        })
    }

    fn forward(&self, x: &Tensor) -> Result<Tensor> {
        let w = self.weight.as_tensor();
        let b = self.bias.as_tensor();
        let z = x.matmul(&w.t()?)?.broadcast_add(b)?;
        let out = match self.activation {
            Some(Activation::Relu) => z.relu()?,
            Some(Activation::Tanh) => z.tanh()?,
            None => z,
        };
        Ok(out)
    }

    fn vars(&self) -> [Var; 2] {
        [self.weight.clone(), self.bias.clone()]
    }

    fn weight_l2_norm(&self) -> Result<f64> {
        Ok(self
            .weight
            .as_tensor()
            .sqr()?
            .sum_all()?
            .to_scalar::<f32>()?
            .sqrt() as f64)
    }
}

struct Mlp {
    layers: Vec<DenseLayer>,
}

impl Mlp {
    fn new(architecture: &ModelArchitecture, init: InitMethod, device: &Device) -> Result<Self> {
        let mut layers = Vec::with_capacity(architecture.depth + 1);
        let mut in_dim = architecture.input_dim;
        for _ in 0..architecture.depth {
            layers.push(DenseLayer::new(
                in_dim,
                architecture.width,
                init,
                Some(architecture.activation),
                device,
            )?);
            in_dim = architecture.width;
        }
        // Output head: regression -> single scalar, no activation.
        layers.push(DenseLayer::new(in_dim, 1, init, None, device)?);
        Ok(Self { layers })
    }

    fn forward(&self, x: &Tensor) -> Result<Tensor> {
        let mut h = x.clone();
        for layer in &self.layers {
            h = layer.forward(&h)?;
        }
        Ok(h)
    }

    fn vars(&self) -> Vec<Var> {
        self.layers.iter().flat_map(|l| l.vars()).collect()
    }

    fn n_params(&self) -> usize {
        self.layers
            .iter()
            .map(|l| l.weight.elem_count() + l.bias.elem_count())
            .sum()
    }

    fn weight_norm_stats(&self) -> Result<(f64, f64)> {
        let norms: Vec<f64> = self
            .layers
            .iter()
            .map(|l| l.weight_l2_norm())
            .collect::<Result<_>>()?;
        let mean = norms.iter().sum::<f64>() / norms.len() as f64;
        let var = norms.iter().map(|n| (n - mean).powi(2)).sum::<f64>() / norms.len() as f64;
        Ok((mean, var.sqrt()))
    }
}

pub struct TrainOutcome {
    pub model_features: ModelFeatures,
    pub steps_to_threshold: Option<usize>,
    pub initial_loss: f64,
    pub final_loss: f64,
    pub converged: bool,
    pub diverged: bool,
    pub grad_norm_initial: f64,
    pub grad_norm_final: f64,
    pub wall_clock_ms: u128,
}

enum AnyOptimizer {
    Sgd(SGD),
    AdamW(AdamW),
}

impl AnyOptimizer {
    fn step(&mut self, grads: &candle_core::backprop::GradStore) -> Result<()> {
        match self {
            AnyOptimizer::Sgd(o) => o.step(grads)?,
            AnyOptimizer::AdamW(o) => o.step(grads)?,
        }
        Ok(())
    }
}

fn build_optimizer(vars: Vec<Var>, training: &TrainingConfig) -> Result<AnyOptimizer> {
    Ok(match training.optimizer {
        Optimizer::Sgd => AnyOptimizer::Sgd(SGD::new(vars, training.learning_rate)?),
        Optimizer::Adam => AnyOptimizer::AdamW(AdamW::new(
            vars,
            ParamsAdamW {
                lr: training.learning_rate,
                weight_decay: 0.0,
                ..Default::default()
            },
        )?),
        Optimizer::AdamW => AnyOptimizer::AdamW(AdamW::new(
            vars,
            ParamsAdamW {
                lr: training.learning_rate,
                weight_decay: training.weight_decay,
                ..Default::default()
            },
        )?),
    })
}

fn grad_norm(vars: &[Var], grads: &candle_core::backprop::GradStore) -> Result<f64> {
    let mut total = 0.0f64;
    for v in vars {
        if let Some(g) = grads.get(v.as_tensor()) {
            total += g.sqr()?.sum_all()?.to_scalar::<f32>()? as f64;
        }
    }
    Ok(total.sqrt())
}

/// Trains an MLP on a synthetic regression dataset, instrumented per §10/§21.
pub fn train(
    x: &[Vec<f32>],
    y: &[f32],
    architecture: &ModelArchitecture,
    training: &TrainingConfig,
    protocol: &TrialProtocol,
) -> Result<TrainOutcome> {
    let device = Device::Cpu;
    let n_samples = x.len();
    let input_dim = architecture.input_dim;

    let mlp = Mlp::new(architecture, training.init_method, &device)?;
    let (weight_norm_mean, weight_norm_std) = mlp.weight_norm_stats()?;
    let model_features = ModelFeatures {
        depth: architecture.depth,
        width: architecture.width,
        n_params: mlp.n_params(),
        activation: architecture.activation,
        init_method: training.init_method,
        weight_norm_mean,
        weight_norm_std,
    };

    let x_flat: Vec<f32> = x.iter().flatten().copied().collect();
    let x_tensor = Tensor::from_vec(x_flat, (n_samples, input_dim), &device)?;
    let y_tensor = Tensor::from_vec(y.to_vec(), (n_samples, 1), &device)?;

    let vars = mlp.vars();
    let mut optimizer = build_optimizer(vars.clone(), training)?;

    let batch_size = training.batch_size.min(n_samples).max(1);
    let batches_per_epoch = (n_samples / batch_size).max(1);

    let mut rng = ChaCha8Rng::seed_from_u64(protocol.seed);
    let mut order: Vec<usize> = (0..n_samples).collect();
    order.shuffle(&mut rng);

    let mut steps_to_threshold = None;
    let mut initial_loss = f64::NAN;
    let mut final_loss = f64::NAN;
    let mut diverged = false;
    let mut grad_norm_initial = 0.0;
    let mut grad_norm_final = 0.0;

    let start = Instant::now();

    for step in 0..protocol.max_steps {
        if step > 0 && step % batches_per_epoch == 0 {
            order.shuffle(&mut rng);
        }
        let batch_idx = step % batches_per_epoch;
        let indices = &order[batch_idx * batch_size..(batch_idx + 1) * batch_size];

        let batch_x = x_tensor.index_select(
            &Tensor::from_vec(
                indices.iter().map(|i| *i as u32).collect(),
                indices.len(),
                &device,
            )?,
            0,
        )?;
        let batch_y = y_tensor.index_select(
            &Tensor::from_vec(
                indices.iter().map(|i| *i as u32).collect(),
                indices.len(),
                &device,
            )?,
            0,
        )?;

        let pred = mlp.forward(&batch_x)?;
        let diff = pred.sub(&batch_y)?;
        let loss = diff.sqr()?.mean_all()?;

        let loss_value = loss.to_scalar::<f32>()? as f64;
        if step == 0 {
            initial_loss = loss_value;
        }

        if !loss_value.is_finite() {
            diverged = true;
            final_loss = loss_value;
            break;
        }

        let grads = loss.backward()?;
        let g_norm = grad_norm(&vars, &grads)?;
        if step == 0 {
            grad_norm_initial = g_norm;
        }
        grad_norm_final = g_norm;

        optimizer.step(&grads)?;

        final_loss = loss_value;
        if steps_to_threshold.is_none() && loss_value < protocol.loss_threshold {
            steps_to_threshold = Some(step + 1);
            break;
        }
    }

    let wall_clock_ms = start.elapsed().as_millis();
    let converged = steps_to_threshold.is_some();

    Ok(TrainOutcome {
        model_features,
        steps_to_threshold,
        initial_loss,
        final_loss,
        converged,
        diverged,
        grad_norm_initial,
        grad_norm_final,
        wall_clock_ms,
    })
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn training_reduces_loss_on_a_trivial_task() {
        let (x, y) = pretrainopt_taskgen_test_helper();

        let architecture = ModelArchitecture {
            input_dim: 4,
            depth: 1,
            width: 16,
            activation: Activation::Relu,
        };
        let training = TrainingConfig {
            learning_rate: 0.01,
            batch_size: 16,
            optimizer: Optimizer::AdamW,
            weight_decay: 0.0,
            init_method: InitMethod::He,
        };
        let protocol = TrialProtocol {
            loss_threshold: 1e-6,
            max_steps: 200,
            seed: 0,
        };

        let outcome = train(&x, &y, &architecture, &training, &protocol).unwrap();

        assert!(outcome.final_loss.is_finite());
        assert!(!outcome.diverged);
        assert!(outcome.grad_norm_final <= outcome.grad_norm_initial);
        assert!(outcome.model_features.n_params > 0);
    }

    /// Minimal deterministic dataset (y = x1 + x2) without depending on the
    /// taskgen crate, to keep this crate's tests self-contained.
    fn pretrainopt_taskgen_test_helper() -> (Vec<Vec<f32>>, Vec<f32>) {
        let mut x = Vec::new();
        let mut y = Vec::new();
        for i in 0..128 {
            let row = vec![
                (i as f32 * 0.037).sin(),
                (i as f32 * 0.071).cos(),
                (i as f32 * 0.013).sin(),
                (i as f32 * 0.091).cos(),
            ];
            y.push(row[0] + row[1]);
            x.push(row);
        }
        (x, y)
    }
}
