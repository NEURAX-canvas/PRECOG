# Getting Started

Implementation of the MVP scope described in the founding document (`README.md`,
Annexe B): MLP + synthetic regression tasks + 5 hyperparameters, Optuna as the
reference search, gradient boosting as the meta-model.

## Layout

```
crates/core/      shared types (TrialSpec, TrainingConfig, ModelFeatures, TaskFeatures, TrialResult)
crates/taskgen/    synthetic regression task generator (§13)
crates/model/      MLP (candle) + instrumented training loop (§10)
crates/cli/        `pretrainopt-trial` binary: one trial in, one JSON result out
python/            Optuna orchestration + gradient boosting meta-model (§8, §14, §22)
data/              experiment_database.jsonl (generated, gitignored)
```

Rust and Python are decoupled through a single JSON contract (`TrialSpec` in →
`TrialResult` JSON out on stdout), not FFI: the CLI binary runs one trial,
Python calls it in a loop. Each piece is testable alone.

## Build

```
cargo build --release
```

## Run a single trial

```
echo '{
  "task": {"function": "NonlinearInteraction", "input_dim": 6, "noise_level": 0.1, "n_samples": 512, "seed": 42},
  "architecture": {"input_dim": 6, "depth": 2, "width": 32, "activation": "Relu"},
  "training": {"learning_rate": 0.003, "batch_size": 32, "optimizer": "AdamW", "weight_decay": 0.0001, "init_method": "He"},
  "protocol": {"loss_threshold": 0.05, "max_steps": 500, "seed": 7}
}' | ./target/release/pretrainopt-trial
```

## Build the experiment database (§8, §21)

```
python3 -m venv .venv
.venv/bin/pip install -r python/requirements.txt
.venv/bin/python python/run_search.py --n-tasks 10 --trials-per-task 30
```

Runs Optuna (TPE) as the reference Bayesian search over the 5 MVP
hyperparameters, on a batch of synthetic tasks, logging every trial to
`data/experiment_database.jsonl`.

## Train the meta-model and run the H1 decision experiment (Annexe B, exp. #3)

```
.venv/bin/python python/train_meta_model.py
```

Trains gradient boosting (LightGBM) on 80% of the tasks to predict H* directly
from task/model features, then compares its prediction against the naive
default baseline (Adam, lr=3e-4) on the held-out 20% — the experiment that
decides whether H1 holds on this restricted scope (success criterion from
§24: meta-model beats the baseline on >= 60% of held-out tasks).

## What's deliberately not built yet

Per the roadmap (§38): no NTK/Hessian features, no CNN/Transformer, no
distributed execution, no API/dashboard, no persistent storage beyond a flat
JSONL file. All of that is V0.3+, once H1 has a first empirical answer.
