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

v2 of this script fixed a validity gap in v1: the first version fixed
learning_rate/weight_decay/batch_size at each task's *real* best-found H*
while calibrating, then the probe was deployed downstream using the
meta-model's *predicted* (noisier) values instead. v2 closed that gap by
evaluating under predicted H on a disjoint calibration split -- correlation
actually improved (rho=0.66 @ 80 steps) but the probe *still* made the real
pipeline significantly worse (fewer correct optimizer/init picks, slower
convergence, p=0.027). That rules out the calibration/deployment mismatch as
the cause.

v3 (this version) tests the remaining hypothesis: a *single-seed* probe is
too noisy to use as a per-task argmin decision, even though its rank
correlation averaged over many tasks looks reasonable. Every combo gets
re-initialized randomly (candle has no init seeding), so one 80-step probe
per combo is really "one noisy sample" of that combo's typical behavior.
Averaging the probe score over K independent seeds before ranking should
reduce that per-decision noise -- if it doesn't, the probe idea itself (not
just its calibration) is the problem.

For each calibration task, at its predicted (lr, weight_decay, batch_size),
for the already-identified best budget/formula (80 steps, raw loss):
  1. runs full training (800 steps) for all 6 optimizer x init combos to get
     the true ranking, and
  2. runs 10 independent 80-step probes per combo (different seeds),
then for K in {1, 3, 5, 10}, averages the first K probe scores per combo and
reports both the Spearman rank correlation AND the top-1 accuracy (does the
K-seed argmin match the true best combo?) against the true ranking -- top-1
accuracy is what the pipeline actually depends on, correlation is a proxy.

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
PROBE_BUDGET = 80  # best single-seed budget found by v1/v2 of this script
SEED_COUNTS = [1, 3, 5, 10]
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

    max_k = max(SEED_COUNTS)
    # correlations[K] / top1_hits[K] accumulate across calibration tasks
    correlations: dict[int, list[float]] = {k: [] for k in SEED_COUNTS}
    top1_hits: dict[int, int] = {k: 0 for k in SEED_COUNTS}
    n_ranked_tasks = 0

    for _, task_row in calib_tasks.iterrows():
        features_row = pd.DataFrame([task_row[FEATURE_COLS]])
        predicted = predict_config(features_row, models, encoders)
        base_training = {
            "learning_rate": predicted["learning_rate"],
            "weight_decay": predicted["weight_decay"],
            "batch_size": predicted["batch_size"],
        }

        true_steps = {}
        # per_seed_scores[combo] = list of max_k independent probe scores
        per_seed_scores: dict[tuple, list[float]] = {}

        for optimizer in OPTIMIZERS:
            for init_method in INIT_METHODS:
                combo = (optimizer, init_method)
                training = {**base_training, "optimizer": optimizer, "init_method": init_method}

                full = run(task_row, training, FULL_MAX_STEPS, FULL_LOSS_THRESHOLD, seed=0)
                true_steps[combo] = (
                    full["steps_to_threshold"] if full["converged"] else NON_CONVERGENCE_PENALTY
                )

                scores = []
                for seed in range(max_k):
                    probe = run(task_row, training, PROBE_BUDGET, -1.0, seed=seed)
                    loss_t = probe["final_loss"]
                    scores.append(loss_t if np.isfinite(loss_t) else float("inf"))
                per_seed_scores[combo] = scores

        combos = list(true_steps.keys())
        true_rank = [true_steps[c] for c in combos]
        true_best = min(true_steps, key=true_steps.get)
        if len(set(true_rank)) <= 1:
            # All 6 combos tied (typically: none of them converged within the
            # full budget) -- there is nothing to rank, and this task can't
            # contribute evidence either way. Skip it rather than record a NaN.
            print(f"task={task_row['task_id']:<40} true_best=TIE (no usable ranking, skipped)")
            continue

        n_ranked_tasks += 1
        for k in SEED_COUNTS:
            avg_scores = [float(np.mean(per_seed_scores[c][:k])) for c in combos]
            if len(set(avg_scores)) > 1:
                correlations[k].append(spearmanr(avg_scores, true_rank).statistic)
            picked = combos[int(np.argmin(avg_scores))]
            top1_hits[k] += int(picked == true_best)

        print(f"task={task_row['task_id']:<40} true_best={true_best}")

    print(f"\n--- Multi-seed probe calibration ({n_ranked_tasks} usable tasks, "
          f"budget={PROBE_BUDGET} steps, raw_loss) ---")
    print(f"{'K seeds':>8} {'Spearman rho (mean±std)':>26} {'top-1 accuracy':>16}")
    for k in SEED_COUNTS:
        vals = correlations[k]
        acc = 100 * top1_hits[k] / n_ranked_tasks
        print(f"{k:>8} {np.mean(vals):>12.2f} ± {np.std(vals):<10.2f} {acc:>14.0f}%")

    print("\n(for reference: picking a combo at random would average "
          f"{100 / (len(OPTIMIZERS) * len(INIT_METHODS)):.0f}% top-1 accuracy)")


if __name__ == "__main__":
    main()
