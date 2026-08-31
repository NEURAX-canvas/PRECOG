#!/usr/bin/env python3
"""
Builds the Meta-Dataset (§22, "direct H* prediction" formulation) from the
Experiment Database, trains a gradient-boosting meta-model (§14 recommendation
for the MVP), and runs the decision experiment from Annexe B / experiment #3:

    Train on 80% of synthetic tasks, predict H* on the held-out 20%, and check
    whether the predicted configuration beats the naive default baseline
    (Adam, lr=3e-4, batch=32, no weight decay, He init) on real held-out
    training runs. This is the experiment that decides whether H1 holds on
    this restricted scope, or whether the project needs to pivot.

Usage:
    python3 python/train_meta_model.py
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

import lightgbm as lgb
import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder

REPO_ROOT = Path(__file__).resolve().parents[1]
TRIAL_BINARY = REPO_ROOT / "target" / "release" / "pretrainopt-trial"
EXPERIMENT_DB = REPO_ROOT / "data" / "experiment_database.jsonl"

TASK_FEATURE_COLS = [
    "task_features.input_dim",
    "task_features.noise_level",
    "task_features.n_samples",
    "task_features.target_variance",
    "task_features.feature_correlation_mean",
]
# Deliberately excludes model_features.weight_norm_* and .init_method: those
# depend on the very hyperparameter (init method) we are trying to predict,
# and using them as inputs would leak the answer.
MODEL_FEATURE_COLS = ["model_features.depth", "model_features.width", "model_features.n_params"]
FEATURE_COLS = TASK_FEATURE_COLS + MODEL_FEATURE_COLS

TARGETS_REGRESSION = ["training.learning_rate", "training.weight_decay"]
TARGETS_CLASSIFICATION = ["training.batch_size", "training.optimizer", "training.init_method"]

BASELINE_TRAINING = {
    "learning_rate": 3e-4,
    "batch_size": 32,
    "optimizer": "Adam",
    "weight_decay": 0.0,
    "init_method": "He",
}


def load_meta_dataset() -> pd.DataFrame:
    records = [json.loads(line) for line in EXPERIMENT_DB.open()]
    df = pd.json_normalize(records)
    df = df[df["converged"]]
    # Best H* per task = lowest steps_to_threshold among converged trials.
    best = df.loc[df.groupby("task_id")["steps_to_threshold"].idxmin()].reset_index(drop=True)
    return best


def run_trial_for_task(task_row: pd.Series, training: dict, seed: int) -> dict:
    spec = {
        "task": {
            "function": task_row["task_id"].split("_")[2],
            "input_dim": int(task_row["task_features.input_dim"]),
            "noise_level": float(task_row["task_features.noise_level"]),
            "n_samples": int(task_row["task_features.n_samples"]),
            "seed": seed,
        },
        "architecture": {
            "input_dim": int(task_row["task_features.input_dim"]),
            "depth": int(task_row["model_features.depth"]),
            "width": int(task_row["model_features.width"]),
            "activation": task_row["model_features.activation"],
        },
        "training": training,
        "protocol": {"loss_threshold": 0.05, "max_steps": 800, "seed": seed},
    }
    proc = subprocess.run(
        [str(TRIAL_BINARY)], input=json.dumps(spec), capture_output=True, text=True, timeout=120
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr)
    return json.loads(proc.stdout)


def main() -> None:
    df = load_meta_dataset()
    n_tasks = len(df)
    print(f"meta-dataset: {n_tasks} tasks with a converged best trial")
    if n_tasks < 10:
        raise SystemExit("not enough converged tasks yet -- run python/run_search.py first")

    df = df.sample(frac=1.0, random_state=0).reset_index(drop=True)
    n_test = max(1, int(0.2 * n_tasks))
    test_df = df.iloc[:n_test]
    train_df = df.iloc[n_test:]

    x_train = train_df[FEATURE_COLS]
    x_test = test_df[FEATURE_COLS]

    encoders: dict[str, LabelEncoder] = {}
    models: dict[str, object] = {}

    for col in TARGETS_REGRESSION:
        y = np.log(train_df[col].astype(float))
        model = lgb.LGBMRegressor(n_estimators=100, min_child_samples=3, verbosity=-1)
        model.fit(x_train, y)
        models[col] = model

    for col in TARGETS_CLASSIFICATION:
        enc = LabelEncoder()
        y = enc.fit_transform(train_df[col].astype(str))
        model = lgb.LGBMClassifier(n_estimators=100, min_child_samples=3, verbosity=-1)
        model.fit(x_train, y)
        models[col] = model
        encoders[col] = enc

    print("\n--- Decision experiment (Annexe B #3): predicted H* vs default baseline ---")
    wins, ties, losses, failures = 0, 0, 0, 0
    for idx, row in test_df.iterrows():
        features_row = x_test.loc[[idx]]
        predicted = {
            "learning_rate": float(np.exp(models["training.learning_rate"].predict(features_row)[0])),
            "weight_decay": float(np.exp(models["training.weight_decay"].predict(features_row)[0])),
            "batch_size": int(
                encoders["training.batch_size"].inverse_transform(
                    models["training.batch_size"].predict(features_row)
                )[0]
            ),
            "optimizer": str(
                encoders["training.optimizer"].inverse_transform(
                    models["training.optimizer"].predict(features_row)
                )[0]
            ),
            "init_method": str(
                encoders["training.init_method"].inverse_transform(
                    models["training.init_method"].predict(features_row)
                )[0]
            ),
        }

        predicted_result = run_trial_for_task(row, predicted, seed=99)
        baseline_result = run_trial_for_task(row, BASELINE_TRAINING, seed=99)

        p_steps = predicted_result["steps_to_threshold"] if predicted_result["converged"] else None
        b_steps = baseline_result["steps_to_threshold"] if baseline_result["converged"] else None

        print(f"task={row['task_id']:<40} predicted_steps={p_steps} baseline_steps={b_steps}")

        if p_steps is None:
            failures += 1
        elif b_steps is None or p_steps < b_steps:
            wins += 1
        elif p_steps == b_steps:
            ties += 1
        else:
            losses += 1

    print(f"\nwins={wins} ties={ties} losses={losses} predictor_failed_to_converge={failures} "
          f"(out of {len(test_df)} held-out tasks)")
    print("H1 verdict: meta-model beats default baseline on "
          f"{wins}/{len(test_df)} held-out tasks "
          f"({'PASS, see §24 success criterion (>=60%)' if wins / len(test_df) >= 0.6 else 'below the 60% MVP threshold -- see §24/§35'})")


if __name__ == "__main__":
    main()
