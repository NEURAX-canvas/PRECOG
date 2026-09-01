#!/usr/bin/env python3
"""
Calibrates the few-step probe formula (§15, H5) before trusting it anywhere.

The idea to test: instead of predicting optimizer/init_method blindly from
static pre-training features (§10/§21) -- which we measured beats a majority-
class baseline on 0 of 3 categorical targets -- run each candidate (optimizer,
init_method) combo for a *few* steps and rank them by how fast the loss drops.
That's cheap (a few steps vs. hundreds) but only useful if the ranking it
produces actually agrees with the ranking you'd get from training to
convergence.

This script measures exactly that agreement, for several probe budgets and
two candidate scoring formulas, so the probe used later is chosen by evidence
rather than by assumption:

  formula A: raw loss after T probe steps (lower is better)
  formula B: loss_T / loss_0  -- normalized by the initial loss, meant to
             correct for the fact that different init methods start at
             different loss scales (He vs Xavier give different weight norms)

IMPORTANT -- v2 of this script fixes a validity gap in v1: the first version
fixed learning_rate/weight_decay/batch_size at each task's *real* best-found
H* (from Optuna) while calibrating, then the probe was deployed downstream
using the meta-model's *predicted* (noisier, ~52% within 2x of true) values
instead. That mismatch is almost certainly why the probe, calibrated at
Spearman rho=0.56, produced zero net improvement once wired into the actual
pipeline: it was calibrated under easier conditions than it was asked to run
under.

This version closes that gap: it carves the training tasks into an inner
training set (used to fit the exact same meta-model as train_meta_model.py)
and a held-out calibration set, then evaluates the probe using each
calibration task's *predicted* learning_rate/weight_decay/batch_size --
exactly what it will see in production. The 20% final test set from
train_meta_model.py is never touched here.

For each calibration task, at its predicted (lr, weight_decay, batch_size):
  1. runs full training (800 steps) for all 6 optimizer x init combos to get
     the true ranking (by steps_to_threshold, non-convergence penalized), and
  2. runs short probes at several budgets for both formulas,
then reports, per budget x formula, the average per-task Spearman rank
correlation with the true ranking.

Usage:
    python3 python/calibrate_probe.py --n-tasks 30
"""
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

from train_meta_model import FEATURE_COLS, fit_meta_models, load_meta_dataset, predict_config

REPO_ROOT = Path(__file__).resolve().parents[0].parent
TRIAL_BINARY = REPO_ROOT / "target" / "release" / "pretrainopt-trial"

OPTIMIZERS = ["Sgd", "Adam", "AdamW"]
INIT_METHODS = ["Xavier", "He"]
PROBE_BUDGETS = [5, 10, 20, 40, 80, 160]
FULL_MAX_STEPS = 800
FULL_LOSS_THRESHOLD = 0.05
NON_CONVERGENCE_PENALTY = FULL_MAX_STEPS * 2


def run(task_row: pd.Series, training: dict, max_steps: int, loss_threshold: float, seed: int) -> dict:
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
        "protocol": {"loss_threshold": loss_threshold, "max_steps": max_steps, "seed": seed},
    }
    proc = subprocess.run(
        [str(TRIAL_BINARY)], input=json.dumps(spec), capture_output=True, text=True, timeout=60
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr)
    return json.loads(proc.stdout)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-tasks", type=int, default=30)
    args = parser.parse_args()

    df = load_meta_dataset()
    df = df.sample(frac=1.0, random_state=0).reset_index(drop=True)
    # Mirror train_meta_model's outer split exactly so the final 20% test set
    # is never touched here, then carve the remaining 80% into an inner
    # training set (fits the meta-model) and a calibration set (evaluated
    # under that meta-model's *predicted* H, not the real one).
    n_test = max(1, int(0.2 * len(df)))
    train_df = df.iloc[n_test:].reset_index(drop=True)

    n_calib = min(args.n_tasks, max(1, int(0.3 * len(train_df))))
    calib_tasks = train_df.sample(n=n_calib, random_state=2)
    inner_train_df = train_df.drop(calib_tasks.index)
    print(f"inner_train={len(inner_train_df)} calib={len(calib_tasks)} "
          f"(final held-out test set of {n_test} tasks untouched)")

    models, encoders = fit_meta_models(inner_train_df)

    # correlations[budget][formula] = list of per-task Spearman rho
    correlations: dict[int, dict[str, list[float]]] = {
        b: {"raw_loss": [], "ratio": []} for b in PROBE_BUDGETS
    }

    for _, task_row in calib_tasks.iterrows():
        features_row = pd.DataFrame([task_row[FEATURE_COLS]])
        predicted = predict_config(features_row, models, encoders)
        base_training = {
            "learning_rate": predicted["learning_rate"],
            "weight_decay": predicted["weight_decay"],
            "batch_size": predicted["batch_size"],
        }

        true_steps = {}
        probes: dict[int, dict] = {b: {} for b in PROBE_BUDGETS}

        for optimizer in OPTIMIZERS:
            for init_method in INIT_METHODS:
                combo = (optimizer, init_method)
                training = {**base_training, "optimizer": optimizer, "init_method": init_method}

                full = run(task_row, training, FULL_MAX_STEPS, FULL_LOSS_THRESHOLD, seed=0)
                true_steps[combo] = (
                    full["steps_to_threshold"] if full["converged"] else NON_CONVERGENCE_PENALTY
                )

                for budget in PROBE_BUDGETS:
                    probe = run(task_row, training, budget, -1.0, seed=0)
                    loss_0 = probe["initial_loss"]
                    loss_t = probe["final_loss"]
                    if not np.isfinite(loss_t) or not np.isfinite(loss_0) or loss_0 == 0:
                        raw_score, ratio_score = float("inf"), float("inf")
                    else:
                        raw_score = loss_t
                        ratio_score = loss_t / loss_0
                    probes[budget][combo] = (raw_score, ratio_score)

        combos = list(true_steps.keys())
        true_rank = [true_steps[c] for c in combos]
        if len(set(true_rank)) <= 1:
            # All 6 combos tied (typically: none of them converged within the
            # full budget) -- there is nothing to rank, and this task can't
            # contribute evidence either way. Skip it rather than record a NaN.
            print(f"task={task_row['task_id']:<40} true_best=TIE (no usable ranking, skipped)")
            continue

        for budget in PROBE_BUDGETS:
            raw_rank = [probes[budget][c][0] for c in combos]
            ratio_rank = [probes[budget][c][1] for c in combos]
            if len(set(raw_rank)) > 1:
                correlations[budget]["raw_loss"].append(spearmanr(raw_rank, true_rank).statistic)
            if len(set(ratio_rank)) > 1:
                correlations[budget]["ratio"].append(spearmanr(ratio_rank, true_rank).statistic)

        print(f"task={task_row['task_id']:<40} true_best={min(true_steps, key=true_steps.get)}")

    print(f"\n--- Probe formula calibration ({len(calib_tasks)} training tasks, "
          f"{len(OPTIMIZERS) * len(INIT_METHODS)} combos/task) ---")
    print("Spearman rank correlation between probe ranking and true full-training ranking")
    print(f"{'budget':>8} {'raw_loss (mean±std)':>24} {'ratio loss_T/loss_0 (mean±std)':>32}")
    best_budget, best_formula, best_corr = None, None, -2.0
    for budget in PROBE_BUDGETS:
        for formula in ["raw_loss", "ratio"]:
            vals = correlations[budget][formula]
            if vals and np.mean(vals) > best_corr:
                best_corr, best_budget, best_formula = np.mean(vals), budget, formula
        raw = correlations[budget]["raw_loss"]
        ratio = correlations[budget]["ratio"]
        print(f"{budget:>8} {np.mean(raw):>10.2f} ± {np.std(raw):<10.2f} "
              f"{np.mean(ratio):>14.2f} ± {np.std(ratio):<10.2f}")

    print(f"\nBest formula: {best_formula} at budget={best_budget} steps "
          f"(mean Spearman rho={best_corr:.2f})")


if __name__ == "__main__":
    main()
