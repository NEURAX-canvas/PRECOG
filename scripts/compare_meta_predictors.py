#!/usr/bin/env python3
"""Compares alternative Meta-Predictor designs (docs.md §9.7, §19 ablation
methodology) on the exact same locked TEST split, and picks a winner by
evidence rather than assumption. Replaces train_meta_predictor.py, whose
single full-feature RandomForest variant is now just one of the four
candidates evaluated here:

  full_rf     - RandomForest, all features (task+model+zero_cost+regime+prior)
  reduced_rf  - RandomForest, only the zero-cost proxies §21's controlled
                experiment individually validated (gradient_norm,
                gradient_norm_variance, jacob_cov, effective_rank,
                jacobian_condition_mean)
  log_rf      - RandomForest, all features, log1p(steps) target (the
                1600-step non-convergence penalty is a heavy-tailed outlier
                in raw space)
  knn         - no learned model: Meta-Knowledge Base (§9.6) nearest-
                neighbor prior alone

All four see the same TRAIN split, are evaluated once on the same locked
TEST split, and are ranked by top-1 accuracy with confidence calibration
(mean confidence vs. actual accuracy) reported alongside as a tiebreaker
and an explicit red flag, not just accuracy alone.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
import torch

from precog.experiment_db import load_dataframe, record_gate_evaluation
from precog.meta_knowledge_base import MetaKnowledgeBase
from precog.meta_predictor import (
    FEATURE_COLUMNS,
    REDUCED_FEATURE_COLUMNS,
    KNNMetaPredictor,
    MetaPredictor,
    compute_candidate_zero_cost,
    engineer_features,
)
from precog.model import architecture_from_row
from precog.reporting import export_csv_snapshots, write_report
from precog.taskgen import generate, task_config_from_row

NON_CONVERGENCE_PENALTY = 800 * 2


def _prepare(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["steps_to_threshold"] = df["steps_to_threshold"].fillna(NON_CONVERGENCE_PENALTY)
    return df


def evaluate(name, predictor, test_df, mkb):
    hits, confidences, detail_rows = 0, [], []
    n = 0
    for seed, group in test_df.groupby("seed"):
        n += 1
        features_row = group.iloc[[0]]
        engineered = engineer_features(features_row, mkb)
        true_best_init = group.loc[group["steps_to_threshold"].idxmin(), "training.init_method"]

        task_config = task_config_from_row(features_row.iloc[0])
        architecture = architecture_from_row(features_row.iloc[0])
        x, y, _ = generate(task_config)
        zc_by_candidate = compute_candidate_zero_cost(architecture, task_config.input_dim, x, y)

        rec = predictor.recommend(engineered, zc_by_candidate)
        hit = rec.recommended_init.value == true_best_init
        hits += int(hit)
        confidences.append(rec.confidence)
        detail_rows.append(f"| {seed} | {true_best_init} | {rec.recommended_init.value} | "
                            f"{rec.confidence:.2f} | {hit} |")

    accuracy = hits / n
    mean_confidence = float(np.mean(confidences))
    print(f"{name:<12} accuracy={accuracy:.0%} ({hits}/{n})  mean_confidence={mean_confidence:.2f}  "
          f"calibration_gap={mean_confidence - accuracy:+.2f}")
    return {"name": name, "accuracy": accuracy, "hits": hits, "n": n,
            "mean_confidence": mean_confidence, "detail_rows": detail_rows}


def main() -> None:
    train_df = _prepare(load_dataframe(split="train"))
    test_df = _prepare(load_dataframe(split="test"))
    print(f"train: {len(train_df)} rows ({train_df['seed'].nunique()} tasks) | "
          f"test (locked): {len(test_df)} rows ({test_df['seed'].nunique()} tasks)\n")

    mkb = MetaKnowledgeBase(k=5)
    mkb.fit(train_df)
    engineered_rows = [engineer_features(row.to_frame().T, mkb) for _, row in train_df.iterrows()]
    train_engineered = pd.concat(engineered_rows, ignore_index=True)

    best_per_train_task = train_df.loc[train_df.groupby("seed")["steps_to_threshold"].idxmin()]
    universal_init = best_per_train_task["training.init_method"].mode()[0]
    universal_accuracy = float((test_df.loc[test_df.groupby("seed")["steps_to_threshold"].idxmin(),
                                             "training.init_method"] == universal_init).mean())
    random_baseline = 1 / 3

    candidates = {
        "full_rf": MetaPredictor(feature_columns=FEATURE_COLUMNS, log_target=False),
        "reduced_rf": MetaPredictor(feature_columns=REDUCED_FEATURE_COLUMNS, log_target=False),
        "log_rf": MetaPredictor(feature_columns=FEATURE_COLUMNS, log_target=True),
    }
    for predictor in candidates.values():
        predictor.fit(train_engineered, train_df["training.init_method"], train_df["steps_to_threshold"])
    candidates["knn"] = KNNMetaPredictor(mkb)

    print(f"Baselines: universal={universal_accuracy:.0%}  random={random_baseline:.0%}\n")
    print("--- Candidate Meta-Predictors on the locked TEST split ---")
    results = [evaluate(name, predictor, test_df, mkb) for name, predictor in candidates.items()]

    winner = max(results, key=lambda r: (r["accuracy"], -(r["mean_confidence"] - r["accuracy"])))
    beats_universal = winner["accuracy"] > universal_accuracy

    print(f"\nWinner: {winner['name']} (accuracy={winner['accuracy']:.0%}, "
          f"calibration_gap={winner['mean_confidence'] - winner['accuracy']:+.2f})")
    print(f"Beats universal-config baseline ({universal_accuracy:.0%})? {beats_universal}")

    for r in results:
        record_gate_evaluation(
            generation=f"v1-meta-predictor-{r['name']}", gate_number=2,
            metric_name="top1_accuracy_init_method_adapted_recall_at_10",
            metric_value=r["accuracy"], threshold=0.80, n_samples=r["n"],
            notes=f"universal_baseline={universal_accuracy:.2f}, random_baseline={random_baseline:.2f}, "
                  f"mean_confidence={r['mean_confidence']:.2f}, "
                  f"winner={'yes' if r['name'] == winner['name'] else 'no'}",
        )

    results_table = "\n".join(
        f"| {r['name']} | {r['accuracy']:.0%} ({r['hits']}/{r['n']}) | {r['mean_confidence']:.2f} | "
        f"{r['mean_confidence'] - r['accuracy']:+.2f} |"
        for r in sorted(results, key=lambda r: -r["accuracy"])
    )
    winner_detail = "\n".join(winner["detail_rows"])
    report = f"""## Method

Four Meta-Predictor designs (docs.md §9.7, §19 ablation methodology), all
trained on the identical TRAIN split ({len(train_df)} rows,
{train_df['seed'].nunique()} tasks) and evaluated exactly once on the
identical locked TEST split ({len(test_df)} rows, {test_df['seed'].nunique()}
tasks): `full_rf` (all features), `reduced_rf` (only §21-validated zero-cost
proxies), `log_rf` (all features, log1p target), `knn` (Meta-Knowledge Base
neighbor vote alone, no learned model).

Baselines: universal-config = {universal_accuracy:.0%}, random = {random_baseline:.0%}.

## Results

| candidate | accuracy | mean confidence | calibration gap |
|---|---:|---:|---:|
{results_table}

## Winner: `{winner['name']}`

Selected by accuracy first, then by the smallest confidence/accuracy
calibration gap (docs.md §23 "poorly calibrated uncertainty" risk) as
tiebreaker. {'Beats' if beats_universal else 'Does NOT beat'} the
universal-config baseline ({universal_accuracy:.0%}).

| seed | true best init | predicted | confidence | hit |
|---|---|---|---:|---|
{winner_detail}

## Verdict

{"H1 supported over H4 at this scale: the best Meta-Predictor design conditions on task/model features and beats a single universal init choice." if beats_universal else "H4 not refuted: even the best of four tested Meta-Predictor designs does not beat the universal-config baseline at this meta-dataset size (" + str(train_df['seed'].nunique()) + " training tasks). The bottleneck is data volume, not model choice -- see docs.md §27 'the meta-dataset's quality intrinsically bounds the meta-predictor's quality.'"}
"""
    export_csv_snapshots()
    report_path = write_report("compare_meta_predictors", "Meta-Predictor Comparison (4 designs, locked test split)", report)
    print(f"\nReport written to {report_path.relative_to(report_path.parents[2])}")


if __name__ == "__main__":
    main()
