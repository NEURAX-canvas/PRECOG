use anyhow::Result;
use clap::Parser;
use pretrainopt_core::{TrialResult, TrialSpec};
use std::io::Read;
use std::path::PathBuf;

/// Runs a single PreTrainOpt trial: generates a synthetic task, trains an MLP
/// with the given hyperparameters, and prints the outcome as JSON on stdout.
///
/// This binary is the "single trial" unit called in a loop by the Python-side
/// Optuna orchestrator (see python/run_search.py) to build the experiment
/// database (§8, §21).
#[derive(Parser)]
struct Args {
    /// Path to a JSON TrialSpec file. If omitted, reads JSON from stdin.
    #[arg(long)]
    config: Option<PathBuf>,
}

fn main() -> Result<()> {
    let args = Args::parse();

    let spec_json = match args.config {
        Some(path) => std::fs::read_to_string(path)?,
        None => {
            let mut buf = String::new();
            std::io::stdin().read_to_string(&mut buf)?;
            buf
        }
    };

    let spec: TrialSpec = serde_json::from_str(&spec_json)?;

    let (dataset, task_features) = pretrainopt_taskgen::generate(&spec.task);

    let outcome = pretrainopt_model::train(
        &dataset.x,
        &dataset.y,
        &spec.architecture,
        &spec.training,
        &spec.protocol,
    )?;

    let result = TrialResult {
        task_features,
        model_features: outcome.model_features,
        training: spec.training,
        steps_to_threshold: outcome.steps_to_threshold,
        initial_loss: outcome.initial_loss,
        final_loss: outcome.final_loss,
        converged: outcome.converged,
        diverged: outcome.diverged,
        grad_norm_initial: outcome.grad_norm_initial,
        grad_norm_final: outcome.grad_norm_final,
        wall_clock_ms: outcome.wall_clock_ms,
    };

    println!("{}", serde_json::to_string(&result)?);
    Ok(())
}
