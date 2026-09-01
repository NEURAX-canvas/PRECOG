#!/usr/bin/env python3
"""Gate 3b (docs.md §9.8, §17 P3/P4): does *restricting* the search to the
Meta-Predictor's recommended init_method (not just seeding one trial with
it, see gate3_search_efficiency.py's weak result) actually find near-optimal
hyperparameters, and does it do so more efficiently than a cold joint
search?

Four arms per locked-TEST task, same trial budget (15) except the
reference:
  - reference (40 trials, joint LR x init search): the "near-optimal"
    ground truth this experiment checks the others against.
  - cold (15 trials, joint LR x init search): the honest baseline.
  - informed_restricted (15 trials, LR only, init FIXED to the
    Meta-Predictor's recommended_init): the actual object of this test.
  - universal_restricted (15 trials, LR only, init FIXED to the universal-
    config baseline's init): isolates whether *any* fixed init helps
    (H4-style) from whether the *task-conditional* recommendation
    specifically helps (H1-style) -- same logic as every H1-vs-H4 check
    earlier in this project.
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
from precog.model import Activation, InitMethod, ModelArchitecture, architecture_from_row
from precog.modes import Mode, TrainingConfig, TrainProtocol, train
from precog.reporting import export_csv_snapshots, write_report
from precog.search_engine import SearchEngine
from precog.taskgen import generate, task_config_from_row

FIXED_OPTIMIZER = "adam"
FIXED_BATCH_SIZE = 32
FULL_MAX_STEPS = 800
FULL_LOSS_THRESHOLD = 0.05
TARGET_STEPS = 150.0
N_TRIALS = 15
N_TRIALS_REFERENCE = 40
NON_CONVERGENCE_PENALTY = FULL_MAX_STEPS * 2


def main() -> None:
    train_df = load_dataframe(split="train")
    train_df["steps_to_threshold"] = train_df["steps_to_threshold"].fillna(NON_CONVERGENCE_PENALTY)
    test_df = load_dataframe(split="test")
    test_df["steps_to_threshold"] = test_df["steps_to_threshold"].fillna(NON_CONVERGENCE_PENALTY)

    mkb = MetaKnowledgeBase(k=5)
    mkb.fit(train_df)
    engineered_rows = [engineer_features(row.to_frame().T, mkb) for _, row in train_df.iterrows()]
    predictor = MetaPredictor(feature_columns=REDUCED_FEATURE_COLUMNS)  # evidenced winner, see compare_meta_predictors
    predictor.fit(pd.concat(engineered_rows, ignore_index=True), train_df["training.init_method"],
                  train_df["steps_to_threshold"])

    best_per_train_task = train_df.loc[train_df.groupby("seed")["steps_to_threshold"].idxmin()]
    universal_init = InitMethod(best_per_train_task["training.init_method"].mode()[0])
    print(f"Universal init: {universal_init.value}")

    rows = []
    for seed, group in test_df.groupby("seed"):
        task_row = group.iloc[0]
        task_config = task_config_from_row(task_row)
        architecture = architecture_from_row(task_row)
        x, y = generate(task_config)[:2]

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

        run_label = "gate3b_restricted_search"
        reference = SearchEngine(seed=0).search(
            objective_fn, None, N_TRIALS_REFERENCE, TARGET_STEPS, log_run=(run_label, int(seed), "reference")
        )
        cold = SearchEngine(seed=1).search(
            objective_fn, None, N_TRIALS, TARGET_STEPS, log_run=(run_label, int(seed), "cold")
        )
        informed_restricted = SearchEngine(seed=1).search(
            objective_fn, recommendation, N_TRIALS, TARGET_STEPS, fixed_init=recommendation.recommended_init,
            log_run=(run_label, int(seed), "informed_restricted"),
        )
        universal_restricted = SearchEngine(seed=1).search(
            objective_fn, None, N_TRIALS, TARGET_STEPS, fixed_init=universal_init,
            log_run=(run_label, int(seed), "universal_restricted"),
        )

        rows.append({
            "seed": seed,
            "true_best_init": group.loc[group["steps_to_threshold"].idxmin(), "training.init_method"],
            "recommended_init": recommendation.recommended_init.value,
            "reference_best": reference.best_steps,
            "cold_best": cold.best_steps,
            "informed_restricted_best": informed_restricted.best_steps,
            "universal_restricted_best": universal_restricted.best_steps,
        })
        print(f"seed={seed:<5} reference={reference.best_steps:<6.0f} cold={cold.best_steps:<6.0f} "
              f"informed_restricted={informed_restricted.best_steps:<6.0f} "
              f"universal_restricted={universal_restricted.best_steps:<6.0f} "
              f"recommended_init={recommendation.recommended_init.value}")

    df = pd.DataFrame(rows)
    # "Near-optimal" = within 20% of the 40-trial reference search's result.
    for arm in ["cold_best", "informed_restricted_best", "universal_restricted_best"]:
        df[f"{arm}_near_optimal"] = df[arm] <= df["reference_best"] * 1.2

    print(f"\n--- Gate 3b: restricted search vs {N_TRIALS_REFERENCE}-trial reference "
          f"({len(df)} test tasks, {N_TRIALS} trials/restricted search) ---")
    summary_rows = []
    for arm, label in [("cold_best", "cold (joint search)"),
                        ("informed_restricted_best", "informed_restricted (Meta-Predictor init)"),
                        ("universal_restricted_best", "universal_restricted (H4 baseline init)")]:
        near_optimal_rate = df[f"{arm}_near_optimal"].mean()
        mean_ratio = (df[arm] / df["reference_best"]).mean()
        print(f"{label:<45} near-optimal rate={near_optimal_rate:.0%}  mean ratio to reference={mean_ratio:.2f}x")
        summary_rows.append((label, near_optimal_rate, mean_ratio))

    informed_near_optimal = df["informed_restricted_best_near_optimal"].mean()
    cold_near_optimal = df["cold_best_near_optimal"].mean()
    universal_near_optimal = df["universal_restricted_best_near_optimal"].mean()

    gate_pass = informed_near_optimal >= 0.8
    print(f"\nGate check (near-optimal rate >= 80% for informed_restricted): "
          f"{'PASS' if gate_pass else 'NOT YET MET'} ({informed_near_optimal:.0%})")

    record_gate_evaluation(
        generation="v1-search-engine-restricted", gate_number=3,
        metric_name="informed_restricted_near_optimal_rate",
        metric_value=informed_near_optimal, threshold=0.8, n_samples=len(df),
        notes=f"cold={cold_near_optimal:.2f}, universal_restricted={universal_near_optimal:.2f}, "
              f"reference={N_TRIALS_REFERENCE} trials, restricted={N_TRIALS} trials",
    )

    detail_rows = "\n".join(
        f"| {r.seed} | {r.true_best_init} | {r.recommended_init} | {r.reference_best:.0f} | "
        f"{r.cold_best:.0f} | {r.informed_restricted_best:.0f} | {r.universal_restricted_best:.0f} |"
        for r in df.itertuples()
    )
    verdict = (
        "The Meta-Predictor's recommendation, used to *restrict* the search (not just seed it), "
        "finds near-optimal hyperparameters as reliably as informed_restricted's rate shows, and "
        + ("outperforms" if informed_near_optimal > universal_near_optimal else "does not outperform")
        + " restricting to the context-free universal baseline instead -- "
        + ("H1 supported over H4 for this use of the recommendation." if informed_near_optimal > universal_near_optimal
           else "H4 not refuted: a fixed, task-independent init restriction does as well or better.")
    )
    report = f"""## Method

Four search arms per locked-TEST task, same objective (steps_to_threshold,
FULL_TRAINING, LR/batch/optimizer as in prior gates):
- **reference**: {N_TRIALS_REFERENCE}-trial joint (LR, init) search -- the near-optimal ground truth.
- **cold**: {N_TRIALS}-trial joint (LR, init) search.
- **informed_restricted**: {N_TRIALS}-trial LR-only search, init FIXED to the Meta-Predictor's
  (reduced_rf, the evidenced winner from compare_meta_predictors.py) recommended init.
- **universal_restricted**: {N_TRIALS}-trial LR-only search, init FIXED to the universal-config
  baseline's init ({universal_init.value}) -- isolates whether *any* fixed init helps (H4) from
  whether the *task-conditional* recommendation specifically helps (H1).

"Near-optimal" = achieved best_steps within 20% of the reference search's result.

## Results

| seed | true best init | recommended init | reference | cold | informed_restricted | universal_restricted |
|---|---|---|---:|---:|---:|---:|
{detail_rows}

| Arm | Near-optimal rate | Mean ratio to reference |
|---|---:|---:|
{chr(10).join(f"| {label} | {rate:.0%} | {ratio:.2f}x |" for label, rate, ratio in summary_rows)}

## Verdict

Gate check (informed_restricted near-optimal rate >= 80%): **{'PASS' if gate_pass else 'NOT YET MET'}** ({informed_near_optimal:.0%})

{verdict}
"""
    export_csv_snapshots()
    report_path = write_report("gate3b_restricted_search", "Gate 3b — Restricted Search vs Reference", report)
    print(f"\nReport written to {report_path.relative_to(report_path.parents[2])}")


if __name__ == "__main__":
    main()
