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
from scipy.stats import wilcoxon
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


def universal_config(train_df: pd.DataFrame) -> dict:
    """The single best 'no features needed' config (§24/H4): median/mode of
    H* across training tasks, applied blindly regardless of task features.

    This is the baseline that actually separates H1 from H4: if the
    conditional meta-model cannot beat *this*, task-conditioning isn't
    pulling its weight and a single universal config would do just as well.
    """
    return {
        "learning_rate": float(train_df["training.learning_rate"].median()),
        "weight_decay": float(train_df["training.weight_decay"].median()),
        "batch_size": int(train_df["training.batch_size"].mode()[0]),
        "optimizer": str(train_df["training.optimizer"].mode()[0]),
        "init_method": str(train_df["training.init_method"].mode()[0]),
    }


def fit_meta_models(train_df: pd.DataFrame) -> tuple[dict, dict]:
    """Trains the gradient-boosting meta-model (§14) on `train_df`. Shared by
    train_meta_model.py's decision experiment and calibrate_probe.py, so both
    always predict H* the exact same way."""
    x_train = train_df[FEATURE_COLS]
    encoders: dict[str, LabelEncoder] = {}
    models: dict[str, object] = {}

    for col in TARGETS_REGRESSION:
        y = np.log(train_df[col].astype(float))
        model = lgb.LGBMRegressor(n_estimators=100, min_child_samples=3, verbosity=-1, random_state=0)
        model.fit(x_train, y)
        models[col] = model

    for col in TARGETS_CLASSIFICATION:
        enc = LabelEncoder()
        y = enc.fit_transform(train_df[col].astype(str))
        model = lgb.LGBMClassifier(n_estimators=100, min_child_samples=3, verbosity=-1, random_state=0)
        model.fit(x_train, y)
        models[col] = model
        encoders[col] = enc

    return models, encoders


def predict_config(features_row: pd.DataFrame, models: dict, encoders: dict) -> dict:
    """Predicts a full H from one row of FEATURE_COLS using fitted meta-models."""
    return {
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


def load_meta_dataset() -> pd.DataFrame:
    records = [json.loads(line) for line in EXPERIMENT_DB.open()]
    df = pd.json_normalize(records)
    df = df[df["converged"]]
    # Best H* per task = lowest steps_to_threshold among converged trials.
    best = df.loc[df.groupby("task_id")["steps_to_threshold"].idxmin()].reset_index(drop=True)
    return best


def run_trial_for_task(
    task_row: pd.Series,
    training: dict,
    seed: int,
    max_steps: int = 800,
    loss_threshold: float = 0.05,
) -> dict:
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
        [str(TRIAL_BINARY)], input=json.dumps(spec), capture_output=True, text=True, timeout=120
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr)
    return json.loads(proc.stdout)


# Calibrated in python/calibrate_probe.py, v2: raw loss after 80 steps gave
# the best rank correlation (Spearman rho=0.66) with the true full-training
# ranking when evaluated under the meta-model's *predicted* (not real) H --
# the same noisy inputs this probe actually sees in the pipeline below.
# Clearly better than normalizing by the initial loss; correlation degrades
# again at 160 steps.
PROBE_BUDGET = 80
PROBE_OPTIMIZERS = ["Sgd", "Adam", "AdamW"]
PROBE_INIT_METHODS = ["Xavier", "He"]


def probe_pick_optimizer_init(
    task_row: pd.Series, learning_rate: float, weight_decay: float, batch_size: int
) -> tuple[str, str]:
    """Picks (optimizer, init_method) by running a cheap 40-step probe for
    each of the 6 combinations and keeping the one with the lowest raw loss
    after the probe -- rather than the static classifier, which measured
    worse than a majority-class baseline for both of these targets."""
    best_combo, best_score = None, float("inf")
    for optimizer in PROBE_OPTIMIZERS:
        for init_method in PROBE_INIT_METHODS:
            training = {
                "learning_rate": learning_rate,
                "weight_decay": weight_decay,
                "batch_size": batch_size,
                "optimizer": optimizer,
                "init_method": init_method,
            }
            result = run_trial_for_task(
                task_row, training, seed=0, max_steps=PROBE_BUDGET, loss_threshold=-1.0
            )
            score = result["final_loss"] if np.isfinite(result["final_loss"]) else float("inf")
            if score < best_score:
                best_score, best_combo = score, (optimizer, init_method)
    return best_combo


def main() -> None:
    df = load_meta_dataset()
    n_tasks = len(df)
    print(f"meta-dataset: {n_tasks} tasks with a converged best trial")

    print("\n--- H4 check: how much does H* vary across tasks? ---")
    lr = df["training.learning_rate"]
    print(
        f"learning_rate: mean={lr.mean():.4g} std={lr.std():.4g} "
        f"coefficient_of_variation={lr.std() / lr.mean():.2f} "
        f"min={lr.min():.4g} max={lr.max():.4g}"
    )
    for col in ["training.optimizer", "training.init_method", "training.batch_size"]:
        print(f"{col}: {df[col].value_counts(normalize=True).round(2).to_dict()}")
    if n_tasks < 10:
        raise SystemExit("not enough converged tasks yet -- run python/run_search.py first")

    df = df.sample(frac=1.0, random_state=0).reset_index(drop=True)
    n_test = max(1, int(0.2 * n_tasks))
    test_df = df.iloc[:n_test]
    train_df = df.iloc[n_test:]

    x_test = test_df[FEATURE_COLS]
    models, encoders = fit_meta_models(train_df)

    # §28: replication is not optional -- a single training run per config/task
    # confounds meta-model skill with plain training-run variance.
    n_seeds = 5
    max_steps_penalty = 800 * 2

    universal = universal_config(train_df)
    print(f"\nUniversal config (median/mode of H* across {len(train_df)} training tasks): {universal}")

    print(f"\n--- Decision experiment (Annexe B #3): predicted vs universal vs default baseline ({n_seeds} seeds/task) ---")
    print("(wins/ties/losses below are PREDICTED vs UNIVERSAL -- the actual H1-vs-H4 test;")
    print(" both are also compared against the naive default baseline for context.)")
    wins, ties, losses = 0, 0, 0
    probe_wins, probe_ties, probe_losses = 0, 0, 0
    classifier_correct, probe_correct = 0, 0
    all_predicted_steps: list[float] = []
    all_universal_steps: list[float] = []
    all_baseline_steps: list[float] = []
    all_probed_steps: list[float] = []
    for idx, row in test_df.iterrows():
        features_row = x_test.loc[[idx]]
        predicted = predict_config(features_row, models, encoders)

        probed_optimizer, probed_init = probe_pick_optimizer_init(
            row, predicted["learning_rate"], predicted["weight_decay"], predicted["batch_size"]
        )
        probed = {**predicted, "optimizer": probed_optimizer, "init_method": probed_init}

        classifier_correct += (predicted["optimizer"] == row["training.optimizer"]) + (
            predicted["init_method"] == row["training.init_method"]
        )
        probe_correct += (probed["optimizer"] == row["training.optimizer"]) + (
            probed["init_method"] == row["training.init_method"]
        )

        p_runs = [run_trial_for_task(row, predicted, seed=s) for s in range(n_seeds)]
        pr_runs = [run_trial_for_task(row, probed, seed=s) for s in range(n_seeds)]
        u_runs = [run_trial_for_task(row, universal, seed=s) for s in range(n_seeds)]
        b_runs = [run_trial_for_task(row, BASELINE_TRAINING, seed=s) for s in range(n_seeds)]

        def penalized_steps(runs: list[dict]) -> list[float]:
            return [
                r["steps_to_threshold"] if r["converged"] else max_steps_penalty for r in runs
            ]

        p_steps = penalized_steps(p_runs)
        pr_steps = penalized_steps(pr_runs)
        u_steps = penalized_steps(u_runs)
        b_steps = penalized_steps(b_runs)
        all_predicted_steps.extend(p_steps)
        all_probed_steps.extend(pr_steps)
        all_universal_steps.extend(u_steps)
        all_baseline_steps.extend(b_steps)
        p_mean, p_conv = float(np.mean(p_steps)), sum(r["converged"] for r in p_runs)
        pr_mean, pr_conv = float(np.mean(pr_steps)), sum(r["converged"] for r in pr_runs)
        u_mean, u_conv = float(np.mean(u_steps)), sum(r["converged"] for r in u_runs)
        b_mean, b_conv = float(np.mean(b_steps)), sum(r["converged"] for r in b_runs)

        print(
            f"task={row['task_id']:<40} "
            f"predicted={p_mean:.0f}({p_conv}/{n_seeds})  "
            f"probed={pr_mean:.0f}({pr_conv}/{n_seeds})  "
            f"universal={u_mean:.0f}({u_conv}/{n_seeds})  "
            f"baseline={b_mean:.0f}({b_conv}/{n_seeds})  "
            f"predicted_config={predicted}  probed_opt_init={(probed_optimizer, probed_init)}  "
            f"true_opt_init=({row['training.optimizer']}, {row['training.init_method']})"
        )

        if p_mean < u_mean:
            wins += 1
        elif p_mean == u_mean:
            ties += 1
        else:
            losses += 1

        if pr_mean < p_mean:
            probe_wins += 1
        elif pr_mean == p_mean:
            probe_ties += 1
        else:
            probe_losses += 1

    n = len(test_df)

    def report_pair(name_a, steps_a, name_b, steps_b, wins_count=None):
        diffs = np.array(steps_a) - np.array(steps_b)
        if np.all(diffs == 0):
            print(f"{name_a} vs {name_b}: identical on every pair, skipping test")
            return
        stat, p_value = wilcoxon(steps_a, steps_b)
        sig = "significant at p<0.05" if p_value < 0.05 else "NOT significant at p<0.05"
        extra = f" wins={wins_count}/{n}" if wins_count is not None else ""
        print(f"{name_a} vs {name_b} (n={len(diffs)} paired task-seed runs):{extra} "
              f"Wilcoxon statistic={stat:.1f} p_value={p_value:.4g} ({sig})")

    print(f"\n--- Verdicts (§24/§28), {n_seeds} seeds x {n} held-out tasks ---")

    print("\n[H1 vs H4] Does task-conditional prediction beat a single universal config?")
    print(f"predicted beats universal on {wins}/{n} tasks (ties={ties}, losses={losses})")
    report_pair("predicted", all_predicted_steps, "universal", all_universal_steps, wins)
    if wins / n >= 0.6:
        print("-> H1 supported over H4 at this scale: conditioning on task features earns its keep.")
    else:
        print("-> H4 not refuted: a single fixed config does about as well as the conditional "
              "predictor here -- the extra complexity of task-conditioning isn't paying off yet.")

    print("\n[sanity] Does the universal config alone already beat the naive default baseline?")
    report_pair("universal", all_universal_steps, "baseline", all_baseline_steps)

    print("\n[headline, same as before] predicted vs naive default baseline:")
    report_pair("predicted", all_predicted_steps, "baseline", all_baseline_steps)

    print(f"\n[few-step probe, §15/H5] optimizer/init_method: static classifier vs 40-step probe")
    print(f"exact-match hits out of {2 * n} (optimizer + init_method per task):")
    print(f"  static classifier: {classifier_correct}/{2 * n} ({100 * classifier_correct / (2 * n):.0f}%)")
    print(f"  probe-corrected:   {probe_correct}/{2 * n} ({100 * probe_correct / (2 * n):.0f}%)")
    print(f"probe-corrected config beats classifier-only config on {probe_wins}/{n} tasks "
          f"(ties={probe_ties}, losses={probe_losses})")
    report_pair("probed", all_probed_steps, "predicted", all_predicted_steps, probe_wins)


if __name__ == "__main__":
    main()
