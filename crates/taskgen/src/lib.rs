use pretrainopt_core::{TaskConfig, TaskFeatures, TaskFunction};
use rand::{Rng, SeedableRng};
use rand_chacha::ChaCha8Rng;

pub struct SyntheticDataset {
    /// n_samples rows x input_dim columns.
    pub x: Vec<Vec<f32>>,
    pub y: Vec<f32>,
}

fn standard_normal(rng: &mut ChaCha8Rng) -> f64 {
    // Box-Muller, avoids pulling in rand_distr for a single distribution.
    let u1: f64 = rng.gen_range(1e-12..1.0);
    let u2: f64 = rng.gen_range(0.0..1.0);
    (-2.0 * u1.ln()).sqrt() * (2.0 * std::f64::consts::PI * u2).cos()
}

fn eval_function(function: TaskFunction, x: &[f32]) -> f64 {
    let x: Vec<f64> = x.iter().map(|v| *v as f64).collect();
    match function {
        TaskFunction::Linear => x[0] + x[1],
        TaskFunction::NonlinearInteraction => x[0].sin() + 0.5 * x[1].powi(2) - x[2] * x[3],
        TaskFunction::NonlinearProduct => (x[0] * x[1]).sin() + (-x[2]).exp(),
    }
}

fn min_input_dim(function: TaskFunction) -> usize {
    match function {
        TaskFunction::Linear => 2,
        TaskFunction::NonlinearInteraction => 4,
        TaskFunction::NonlinearProduct => 3,
    }
}

/// Generates a synthetic regression dataset and its task-side features (§13, §21).
pub fn generate(config: &TaskConfig) -> (SyntheticDataset, TaskFeatures) {
    assert!(
        config.input_dim >= min_input_dim(config.function),
        "input_dim too small for {:?}: need >= {}",
        config.function,
        min_input_dim(config.function)
    );

    let mut rng = ChaCha8Rng::seed_from_u64(config.seed);

    let mut x = Vec::with_capacity(config.n_samples);
    let mut y = Vec::with_capacity(config.n_samples);

    for _ in 0..config.n_samples {
        let row: Vec<f32> = (0..config.input_dim)
            .map(|_| standard_normal(&mut rng) as f32)
            .collect();
        let noise = standard_normal(&mut rng) * config.noise_level;
        let target = eval_function(config.function, &row) + noise;
        x.push(row);
        y.push(target as f32);
    }

    let target_variance = variance(&y);
    let feature_correlation_mean = mean_abs_pairwise_correlation(&x);

    let features = TaskFeatures {
        input_dim: config.input_dim,
        noise_level: config.noise_level,
        n_samples: config.n_samples,
        target_variance,
        feature_correlation_mean,
    };

    (SyntheticDataset { x, y }, features)
}

fn variance(values: &[f32]) -> f64 {
    let n = values.len() as f64;
    let mean = values.iter().map(|v| *v as f64).sum::<f64>() / n;
    values
        .iter()
        .map(|v| (*v as f64 - mean).powi(2))
        .sum::<f64>()
        / n
}

fn mean_abs_pairwise_correlation(x: &[Vec<f32>]) -> f64 {
    let n = x.len();
    let dim = x[0].len();
    if dim < 2 {
        return 0.0;
    }
    let cols: Vec<Vec<f64>> = (0..dim)
        .map(|j| x.iter().map(|row| row[j] as f64).collect())
        .collect();

    let mut sum_abs_corr = 0.0;
    let mut pairs = 0usize;
    for i in 0..dim {
        for j in (i + 1)..dim {
            sum_abs_corr += pearson(&cols[i], &cols[j], n).abs();
            pairs += 1;
        }
    }
    if pairs == 0 {
        0.0
    } else {
        sum_abs_corr / pairs as f64
    }
}

fn pearson(a: &[f64], b: &[f64], n: usize) -> f64 {
    let mean_a = a.iter().sum::<f64>() / n as f64;
    let mean_b = b.iter().sum::<f64>() / n as f64;
    let mut cov = 0.0;
    let mut var_a = 0.0;
    let mut var_b = 0.0;
    for i in 0..n {
        let da = a[i] - mean_a;
        let db = b[i] - mean_b;
        cov += da * db;
        var_a += da * da;
        var_b += db * db;
    }
    if var_a == 0.0 || var_b == 0.0 {
        0.0
    } else {
        cov / (var_a.sqrt() * var_b.sqrt())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn config(function: TaskFunction, input_dim: usize, seed: u64) -> TaskConfig {
        TaskConfig {
            function,
            input_dim,
            noise_level: 0.1,
            n_samples: 128,
            seed,
        }
    }

    #[test]
    fn generates_expected_shapes() {
        let (dataset, features) = generate(&config(TaskFunction::NonlinearInteraction, 6, 1));
        assert_eq!(dataset.x.len(), 128);
        assert_eq!(dataset.y.len(), 128);
        assert!(dataset.x.iter().all(|row| row.len() == 6));
        assert_eq!(features.input_dim, 6);
        assert_eq!(features.n_samples, 128);
    }

    #[test]
    fn same_seed_is_reproducible() {
        let (a, _) = generate(&config(TaskFunction::Linear, 4, 42));
        let (b, _) = generate(&config(TaskFunction::Linear, 4, 42));
        assert_eq!(a.x, b.x);
        assert_eq!(a.y, b.y);
    }

    #[test]
    fn different_seeds_differ() {
        let (a, _) = generate(&config(TaskFunction::Linear, 4, 1));
        let (b, _) = generate(&config(TaskFunction::Linear, 4, 2));
        assert_ne!(a.y, b.y);
    }

    #[test]
    #[should_panic(expected = "input_dim too small")]
    fn rejects_input_dim_below_minimum() {
        generate(&config(TaskFunction::NonlinearInteraction, 2, 1));
    }

    #[test]
    fn zero_noise_matches_analytic_function_exactly() {
        let mut cfg = config(TaskFunction::Linear, 4, 5);
        cfg.noise_level = 0.0;
        let (dataset, _) = generate(&cfg);
        for (row, &y) in dataset.x.iter().zip(dataset.y.iter()) {
            let expected = row[0] + row[1];
            assert!((expected - y).abs() < 1e-5);
        }
    }
}
