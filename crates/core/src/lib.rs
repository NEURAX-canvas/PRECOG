use serde::{Deserialize, Serialize};

/// One of the 3-5 synthetic regression generative functions (§13).
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum TaskFunction {
    /// y = x1 + x2
    Linear,
    /// y = sin(x1) + 0.5*x2^2 - x3*x4 + eps
    NonlinearInteraction,
    /// y = sin(x1*x2) + e^(-x3)
    NonlinearProduct,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TaskConfig {
    pub function: TaskFunction,
    pub input_dim: usize,
    pub noise_level: f64,
    pub n_samples: usize,
    pub seed: u64,
}

/// Task-side features (§21 experiment schema), computed from the generated data.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TaskFeatures {
    pub input_dim: usize,
    pub noise_level: f64,
    pub n_samples: usize,
    pub target_variance: f64,
    pub feature_correlation_mean: f64,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum Activation {
    Relu,
    Tanh,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum InitMethod {
    Xavier,
    He,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ModelArchitecture {
    pub input_dim: usize,
    pub depth: usize,
    pub width: usize,
    pub activation: Activation,
}

/// Model-side features (§21 experiment schema), computed at/near initialization.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ModelFeatures {
    pub depth: usize,
    pub width: usize,
    pub n_params: usize,
    pub activation: Activation,
    pub init_method: InitMethod,
    pub weight_norm_mean: f64,
    pub weight_norm_std: f64,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum Optimizer {
    Sgd,
    Adam,
    AdamW,
}

/// The 5 hyperparameters covered by the MVP (Annexe B) = H, the search/prediction target.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TrainingConfig {
    pub learning_rate: f64,
    pub batch_size: usize,
    pub optimizer: Optimizer,
    pub weight_decay: f64,
    pub init_method: InitMethod,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TrialProtocol {
    pub loss_threshold: f64,
    pub max_steps: usize,
    pub seed: u64,
}

/// Full input to one trial run (what the `cli` binary reads from stdin/file).
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TrialSpec {
    pub task: TaskConfig,
    pub architecture: ModelArchitecture,
    pub training: TrainingConfig,
    pub protocol: TrialProtocol,
}

/// Outcome of one trial (§21 "Outcome" + "Dynamics" fields, flattened for MVP).
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TrialResult {
    pub task_features: TaskFeatures,
    pub model_features: ModelFeatures,
    pub training: TrainingConfig,
    pub steps_to_threshold: Option<usize>,
    pub final_loss: f64,
    pub converged: bool,
    pub diverged: bool,
    pub grad_norm_initial: f64,
    pub grad_norm_final: f64,
    pub wall_clock_ms: u128,
}
