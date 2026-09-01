#!/usr/bin/env python3
"""Trains the Meta-Predictor (docs.md §9.7) on the TRAIN split of the
meta-dataset built by build_meta_dataset.py, then evaluates it exactly once
on the locked TEST split (§12, §15.1) -- P1/P2-style protocol (§15) adapted
to a 3-way init_method choice: top-1 accuracy (Recall@1) against a random
baseline (33%) and against the "always predict the training set's most
common best init" baseline (H4-style universal-config check, matching the
methodology validated in the archived v0 prototype).

Pipeline order matches docs.md §8/§9 exactly: Model/Data/Hardware Encoders
and Regime Detector already ran when the meta-dataset was built; this
script adds the Meta-Knowledge Base (§9.6, built here on TRAIN only, never
on TEST) before the Meta-Predictor (§9.7) queries it for a neighborhood
prior.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd

from precog.experiment_db import load_dataframe, record_gate_evaluation
from precog.meta_knowledge_base import MetaKnowledgeBase
from precog.meta_predictor import MetaPredictor, engineer_features

NON_CONVERGENCE_PENALTY = 800 * 2


def _prepare(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["steps_to_threshold"] = df["steps_to_threshold"].fillna(NON_CONVERGENCE_PENALTY)
    return df


def main() -> None:
    train_df = _prepare(load_dataframe(split="train"))
    test_df = _prepare(load_dataframe(split="test"))
    print(f"train: {len(train_df)} rows ({train_df['seed'].nunique()} tasks) | "
          f"test (locked): {len(test_df)} rows ({test_df['seed'].nunique()} tasks)")

    # §9.6 Meta-Knowledge Base: fit on TRAIN only -- the neighborhood prior
    # for a test task must never see other test tasks, or the "unseen data"
    # guarantee (§12, §15.1) is broken.
    mkb = MetaKnowledgeBase(k=5)
    mkb.fit(train_df)

    engineered_rows = [engineer_features(row.to_frame().T, mkb) for _, row in train_df.iterrows()]
    train_engineered = pd.concat(engineered_rows, ignore_index=True)

    predictor = MetaPredictor()
    predictor.fit(train_engineered, train_df["training.init_method"], train_df["steps_to_threshold"])

    # Universal-config baseline (H4-style, per the v0 prototype's methodology):
    # the single most common best-init across training tasks, applied blindly.
    best_per_train_task = train_df.loc[train_df.groupby("seed")["steps_to_threshold"].idxmin()]
    universal_init = best_per_train_task["training.init_method"].mode()[0]
    print(f"Universal init (mode of best-init across {len(best_per_train_task)} training tasks): {universal_init}")

    hits, universal_hits, confidences = 0, 0, []
    n_test_tasks = 0
    detail_rows = []
    for seed, group in test_df.groupby("seed"):
        n_test_tasks += 1
        features_row = group.iloc[[0]]
        engineered = engineer_features(features_row, mkb)
        true_best_init = group.loc[group["steps_to_threshold"].idxmin(), "training.init_method"]

        rec = predictor.recommend(engineered)
        hit = rec.recommended_init.value == true_best_init
        hits += int(hit)
        universal_hits += int(universal_init == true_best_init)
        confidences.append(rec.confidence)
        detail_rows.append(
            f"| {seed} | {true_best_init} | {rec.recommended_init.value} | {rec.confidence:.2f} | "
            f"{rec.expected_steps:.0f} | {rec.steps_range[0]:.0f}-{rec.steps_range[1]:.0f} | {hit} |"
        )

        print(f"seed={seed:<5} true_best={true_best_init:<11} predicted={rec.recommended_init.value:<11} "
              f"confidence={rec.confidence:.2f} expected_steps={rec.expected_steps:.0f} "
              f"range={rec.steps_range[0]:.0f}-{rec.steps_range[1]:.0f} hit={hit}")

    accuracy = hits / n_test_tasks
    universal_accuracy = universal_hits / n_test_tasks
    random_baseline = 1 / 3

    print(f"\n--- Meta-Predictor evaluation on the locked TEST split ({n_test_tasks} tasks) ---")
    print(f"Meta-Predictor top-1 accuracy : {accuracy:.0%} ({hits}/{n_test_tasks})")
    print(f"Universal-config baseline     : {universal_accuracy:.0%} ({universal_hits}/{n_test_tasks})")
    print(f"Random baseline (3 classes)   : {random_baseline:.0%}")
    print(f"Mean confidence               : {np.mean(confidences):.2f}")

    if accuracy > universal_accuracy:
        print("\n-> H1 supported over H4 at this scale: conditioning on task/model features "
              "beats a single universal init choice.")
    else:
        print("\n-> H4 not refuted here: the universal init does at least as well as the "
              "learned Meta-Predictor on this test set.")

    # §17: Gate 2 is specified as Recall@10; with only 3 candidate init
    # methods, top-1 accuracy is the closest well-defined analogue (Recall@3
    # would be trivially 100%), so it's logged as an explicitly-noted
    # adapted version of Gate 2, not a literal Recall@10.
    record_gate_evaluation(
        generation="v1-meta-predictor",
        gate_number=2,
        metric_name="top1_accuracy_init_method_adapted_recall_at_10",
        metric_value=accuracy,
        threshold=0.80,
        n_samples=n_test_tasks,
        notes=f"adapted Gate 2 (3-way choice, not 10): universal baseline={universal_accuracy:.2f}, "
              f"random baseline={random_baseline:.2f}, mean confidence={np.mean(confidences):.2f}",
    )

    from precog.reporting import export_csv_snapshots, write_report

    verdict = ("H1 supported over H4 at this scale: conditioning on task/model features beats a "
               "single universal init choice." if accuracy > universal_accuracy else
               "H4 not refuted here: the universal init does at least as well as the learned "
               "Meta-Predictor on this test set.")
    calibration_flag = (
        "**Calibration warning (§23 'poorly calibrated uncertainty')**: mean confidence "
        f"({np.mean(confidences):.2f}) is well above the actual accuracy ({accuracy:.2f}) -- "
        "the confidence score should not be trusted at this meta-dataset size."
        if np.mean(confidences) - accuracy > 0.15 else ""
    )
    report = f"""## Method

Meta-Predictor (docs.md §9.7) trained on {len(train_df)} rows ({train_df['seed'].nunique()} tasks)
from the TRAIN split, evaluated exactly once on the locked TEST split
({len(test_df)} rows, {test_df['seed'].nunique()} tasks) per §12/§15.1.
Pipeline order: Model/Data/Hardware Encoders + Regime Detector (already
logged when the meta-dataset was built) -> Meta-Knowledge Base (§9.6, fit
on TRAIN only) -> Meta-Predictor (§9.7, random-forest ensemble, one head:
expected steps_to_threshold per candidate init_method).

## Results

| seed | true best init | predicted | confidence | expected steps | range | hit |
|---|---|---|---:|---:|---|---|
{chr(10).join(detail_rows)}

| Method | Accuracy |
|---|---:|
| Meta-Predictor (top-1) | {accuracy:.0%} ({hits}/{n_test_tasks}) |
| Universal-config baseline | {universal_accuracy:.0%} ({universal_hits}/{n_test_tasks}) |
| Random baseline (3 classes) | {random_baseline:.0%} |

Mean confidence: {np.mean(confidences):.2f}

## Verdict

{verdict}

{calibration_flag}
"""
    export_csv_snapshots()
    report_path = write_report("meta_predictor_eval", "Meta-Predictor Evaluation (Locked Test Split)", report)
    print(f"\nReport written to {report_path.relative_to(report_path.parents[2])}")
    print("Meta-dataset snapshot refreshed in results/experiments.csv and results/gate_evaluations.csv")


if __name__ == "__main__":
    main()
