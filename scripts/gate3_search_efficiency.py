#!/usr/bin/env python3
"""Gate 3 (docs.md §17): how much compute does a Meta-Predictor-informed
search save over a cold one? Target: >= 50% reduction (docs.md §16, P4
Compute protocol, §15).

For each task in the locked TEST split, runs the Search Engine (§9.8) twice
with an identical trial budget and RNG seed:
  - "informed": warm-started from the Meta-Predictor's (§9.7) recommended
    init_method,
  - "cold": no warm start, otherwise identical.
Compares trials-to-target (first trial reaching a fixed steps_to_threshold
target) between the two -- fewer trials for equal quality is the compute
saving docs.md §24 requires PRECOG to demonstrate net of its own overhead.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd

from precog.experiment_db import load_dataframe, record_gate_evaluation
from precog.meta_knowledge_base import MetaKnowledgeBase
from precog.meta_predictor import (
    REDUCED_FEATURE_COLUMNS,
    MetaPredictor,
    compute_candidate_zero_cost,
    engineer_features,
)
from precog.model import Activation, InitMethod, ModelArchitecture
from precog.modes import Mode, TrainingConfig, TrainProtocol, train
from precog.reporting import export_csv_snapshots, write_report
from precog.search_engine import SearchEngine
from precog.taskgen import TaskConfig, TaskFunction, generate

FIXED_OPTIMIZER = "adam"
FIXED_BATCH_SIZE = 32
FULL_MAX_STEPS = 800
FULL_LOSS_THRESHOLD = 0.05
TARGET_STEPS = 150.0  # "good enough" convergence target for this search-efficiency test
N_TRIALS = 15
NON_CONVERGENCE_PENALTY = FULL_MAX_STEPS * 2


def main() -> None:
    train_df = load_dataframe(split="train")
    train_df["steps_to_threshold"] = train_df["steps_to_threshold"].fillna(NON_CONVERGENCE_PENALTY)
    test_df = load_dataframe(split="test")
    test_df["steps_to_threshold"] = test_df["steps_to_threshold"].fillna(NON_CONVERGENCE_PENALTY)

    mkb = MetaKnowledgeBase(k=5)
    mkb.fit(train_df)
    engineered_rows = [engineer_features(row.to_frame().T, mkb) for _, row in train_df.iterrows()]
    # scripts/compare_meta_predictors.py's evidence (results/reports/*_compare_meta_predictors.md):
    # reduced_rf (only the §21-validated zero-cost proxies) beat full_rf, log_rf, and knn
    # on accuracy AND calibration -- not the default full-feature RandomForest.
    predictor = MetaPredictor(feature_columns=REDUCED_FEATURE_COLUMNS)
    predictor.fit(pd.concat(engineered_rows, ignore_index=True), train_df["training.init_method"],
                  train_df["steps_to_threshold"])

    rows = []
    for seed, group in test_df.groupby("seed"):
        task_row = group.iloc[0]
        task_config = TaskConfig(
            function=TaskFunction(task_row["task.function"]),
            input_dim=int(task_row["task.input_dim"]),
            noise_level=float(task_row["task.noise_level"]),
            n_samples=int(task_row["task.n_samples"]),
            seed=int(task_row["task.seed"]),
        )
        x, y, _ = generate(task_config)
        architecture = ModelArchitecture(
            input_dim=task_config.input_dim, depth=2, width=32, activation=Activation.RELU
        )

        def objective_fn(lr: float, init_method: InitMethod, architecture=architecture, x=x, y=y) -> float:
            training = TrainingConfig(
                learning_rate=lr, batch_size=FIXED_BATCH_SIZE, optimizer=FIXED_OPTIMIZER,
                weight_decay=1e-5, init_method=init_method,
            )
            protocol = TrainProtocol(
                mode=Mode.FULL_TRAINING, max_steps=FULL_MAX_STEPS, loss_threshold=FULL_LOSS_THRESHOLD, seed=0
            )
            result = train(architecture, x, y, training, protocol)
            return result.steps_to_threshold if result.converged else NON_CONVERGENCE_PENALTY

        features_row = group.iloc[[0]]
        engineered = engineer_features(features_row, mkb)
        zc_by_candidate = compute_candidate_zero_cost(architecture, task_config.input_dim, x, y)
        recommendation = predictor.recommend(engineered, zc_by_candidate)

        run_label = "gate3_search_efficiency"
        informed = SearchEngine(seed=0).search(
            objective_fn, recommendation, N_TRIALS, TARGET_STEPS, log_run=(run_label, int(seed), "informed")
        )
        cold = SearchEngine(seed=0).search(
            objective_fn, None, N_TRIALS, TARGET_STEPS, log_run=(run_label, int(seed), "cold")
        )

        rows.append({
            "seed": seed, "informed_trials_to_target": informed.trials_to_target,
            "cold_trials_to_target": cold.trials_to_target,
            "informed_best_steps": informed.best_steps, "cold_best_steps": cold.best_steps,
        })
        print(f"seed={seed:<5} informed_trials_to_target={informed.trials_to_target} "
              f"cold_trials_to_target={cold.trials_to_target} "
              f"informed_best={informed.best_steps:.0f} cold_best={cold.best_steps:.0f}")

    both_reached = [r for r in rows if r["informed_trials_to_target"] and r["cold_trials_to_target"]]
    if both_reached:
        reductions = [
            1 - r["informed_trials_to_target"] / r["cold_trials_to_target"] for r in both_reached
        ]
        mean_reduction = float(np.mean(reductions))
    else:
        mean_reduction = float("nan")

    only_informed_reached = sum(
        1 for r in rows if r["informed_trials_to_target"] and not r["cold_trials_to_target"]
    )
    neither_reached = sum(
        1 for r in rows if not r["informed_trials_to_target"] and not r["cold_trials_to_target"]
    )

    print(f"\n--- Gate 3: search compute reduction ({len(rows)} test tasks, {N_TRIALS} trials/search) ---")
    print(f"Both reached target: {len(both_reached)}/{len(rows)}, mean trial reduction: {mean_reduction:.0%}")
    print(f"Informed reached target but cold didn't: {only_informed_reached}/{len(rows)}")
    print(f"Neither reached target: {neither_reached}/{len(rows)}")

    gate3_pass = mean_reduction >= 0.5
    print(f"\nGate 3 (docs.md §17, target >= 50% compute reduction): "
          f"{'PASS' if gate3_pass else 'NOT YET MET'} ({mean_reduction:.0%})")

    record_gate_evaluation(
        generation="v1-search-engine", gate_number=3, metric_name="mean_trial_reduction_informed_vs_cold",
        metric_value=mean_reduction if not np.isnan(mean_reduction) else 0.0, threshold=0.5,
        n_samples=len(both_reached),
        notes=f"{len(rows)} test tasks, {N_TRIALS} trials/search, target_steps={TARGET_STEPS}, "
              f"only_informed_reached={only_informed_reached}, neither_reached={neither_reached}",
    )

    detail_rows = "\n".join(
        f"| {r['seed']} | {r['informed_trials_to_target']} | {r['cold_trials_to_target']} | "
        f"{r['informed_best_steps']:.0f} | {r['cold_best_steps']:.0f} |"
        for r in rows
    )
    report = f"""## Method

Search Engine (docs.md §9.8): Optuna TPE warm-started from the
Meta-Predictor's (§9.7) recommended init_method ("informed") vs an
identical cold search with no warm start, {N_TRIALS} trials each, same RNG
seed, on all {len(rows)} locked TEST-split tasks. Target: reach
steps_to_threshold <= {TARGET_STEPS}.

## Results

| seed | informed trials-to-target | cold trials-to-target | informed best steps | cold best steps |
|---|---:|---:|---:|---:|
{detail_rows}

Both reached target: {len(both_reached)}/{len(rows)} (mean trial reduction: {mean_reduction:.0%})
Informed reached but cold didn't: {only_informed_reached}/{len(rows)}
Neither reached: {neither_reached}/{len(rows)}

## Verdict

Gate 3 (docs.md §17, target >= 50% compute reduction): **{'PASS' if gate3_pass else 'NOT YET MET'}** ({mean_reduction:.0%})
"""
    export_csv_snapshots()
    report_path = write_report("gate3_search_efficiency", "Gate 3 — Search Engine Compute Reduction", report)
    print(f"\nReport written to {report_path.relative_to(report_path.parents[2])}")


if __name__ == "__main__":
    main()
