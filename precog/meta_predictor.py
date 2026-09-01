"""Meta-Predictor (docs.md §9.7): takes model/task/hardware/regime/zero-cost
features for a *candidate configuration* and predicts its expected outcome,
never as a single value but as a distribution with an attached confidence
(§7.3, §20). Per §9.7's own input list:

    X = [X_model, X_data, X_ZC, X_NEAR, X_init, X_regime]

X_regime comes from the Regime Detector (§9.5); the Meta-Knowledge Base's
neighborhood prior (§9.6, §13's "Prior Knowledge") is added as an extra,
literature-consistent way to inject "similar tasks" experience alongside
the model's own features.

For V1 scope (§25: Learning Rate, Batch Size, Optimizer, Initialization),
this first version predicts one head -- T_hat, expected steps_to_threshold
-- for a candidate init_method, since §21's controlled experiment (see
scripts/gate1_ranking.py) is the one axis validated so far to carry a
signal the untrained model can actually explain (zero-cost proxies are
computed under a specific init and can't describe a not-yet-chosen
optimizer/LR/batch_size -- see that script's closing note).

Uncertainty is produced by ensembling (§9.7, §20's first suggested method):
a random forest's per-tree predictions give a natural, cheap ensemble
without hand-rolling bootstrap resampling.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor

from precog.meta_knowledge_base import MetaKnowledgeBase
from precog.model import InitMethod
from precog.regime import _bucket_noise, _bucket_volume

BASE_FEATURE_COLUMNS = [
    "task.input_dim",
    "task.noise_level",
    "task.n_samples",
    "task.target_variance",
    "task.target_entropy_estimate",
    "task.feature_correlation_mean",
    "task.redundancy",
    "model.depth",
    "model.width",
    "model.n_params",
    "model.flops",
]
_NOISE_BUCKETS = ["clean", "moderate", "noisy"]
_VOLUME_BUCKETS = ["low", "medium", "high"]
REGIME_COLUMNS = [f"regime_noise.{b}" for b in _NOISE_BUCKETS] + [f"regime_volume.{b}" for b in _VOLUME_BUCKETS]
PRIOR_COLUMNS = ["neighborhood_prior_steps_mean"]
FEATURE_COLUMNS = BASE_FEATURE_COLUMNS + REGIME_COLUMNS + PRIOR_COLUMNS

CANDIDATE_INIT_METHODS = [InitMethod.XAVIER, InitMethod.HE, InitMethod.ORTHOGONAL]


def engineer_features(features_row: pd.DataFrame, mkb: MetaKnowledgeBase) -> pd.DataFrame:
    """Adds X_regime (§9.5, one-hot -- recomputed from raw task stats rather
    than trusting a stored regime label, so this also works for a brand new
    task never logged in the meta-dataset) and the Meta-Knowledge Base's
    neighborhood prior (§9.6, §13) to the base task/model features."""
    row = features_row.copy()
    noise_bucket = _bucket_noise(row["task.noise_level"].iloc[0])
    volume_bucket = _bucket_volume(row["task.n_samples"].iloc[0])
    for b in _NOISE_BUCKETS:
        row[f"regime_noise.{b}"] = float(b == noise_bucket)
    for b in _VOLUME_BUCKETS:
        row[f"regime_volume.{b}"] = float(b == volume_bucket)

    prior = mkb.neighborhood_prior(features_row)
    row["neighborhood_prior_steps_mean"] = prior["neighborhood_prior_steps_mean"]
    return row


def _with_candidate_init(features_row: pd.DataFrame, init_method: InitMethod) -> pd.DataFrame:
    row = features_row.copy()
    for candidate in CANDIDATE_INIT_METHODS:
        row[f"candidate_init.{candidate.value}"] = float(candidate == init_method)
    return row


def _candidate_columns() -> list[str]:
    return [f"candidate_init.{c.value}" for c in CANDIDATE_INIT_METHODS]


@dataclass
class Recommendation:
    """docs.md §9.7's output format: never a point value alone."""

    recommended_init: InitMethod
    expected_steps: float
    steps_range: tuple[float, float]  # +/- 1 std across the ensemble
    confidence: float  # 1 - (relative spread), clamped to [0, 1]
    per_candidate: dict[str, dict]  # every candidate's own prediction, for transparency


class MetaPredictor:
    """One head for now (T_hat = expected steps_to_threshold); additional
    heads (A_hat, C_hat, N_hat, docs.md §9.7) are a straightforward
    extension of the same ensemble once their ground truth is logged."""

    def __init__(self, n_estimators: int = 300, random_state: int = 0):
        self.model = RandomForestRegressor(
            n_estimators=n_estimators, random_state=random_state, min_samples_leaf=2
        )
        self._fitted_columns: list[str] | None = None

    def fit(self, features: pd.DataFrame, init_methods: pd.Series, steps_to_threshold: pd.Series) -> None:
        rows = []
        for (_, feat_row), init_value in zip(features.iterrows(), init_methods):
            row = _with_candidate_init(feat_row.to_frame().T, InitMethod(init_value))
            rows.append(row)
        x_train = pd.concat(rows, ignore_index=True)[FEATURE_COLUMNS + _candidate_columns()]
        self._fitted_columns = list(x_train.columns)
        self.model.fit(x_train, steps_to_threshold.to_numpy())

    def _predict_with_uncertainty(self, x_row: pd.DataFrame) -> tuple[float, float]:
        x_row = x_row[self._fitted_columns].to_numpy()
        tree_predictions = np.array([tree.predict(x_row)[0] for tree in self.model.estimators_])
        return float(tree_predictions.mean()), float(tree_predictions.std())

    def recommend(self, features_row: pd.DataFrame) -> Recommendation:
        """docs.md §9.7: 'for each candidate configuration, a multi-head
        prediction' -- query every candidate init, keep the best, but report
        all of them (the Rank/Optimize step, §18 diagram, needs the full
        set, not just the winner). `features_row` must already carry the
        engineered regime/prior columns (see engineer_features())."""
        per_candidate = {}
        for candidate in CANDIDATE_INIT_METHODS:
            x_row = _with_candidate_init(features_row, candidate)
            mean_steps, std_steps = self._predict_with_uncertainty(x_row)
            per_candidate[candidate.value] = {"expected_steps": mean_steps, "std_steps": std_steps}

        best_init_name = min(per_candidate, key=lambda k: per_candidate[k]["expected_steps"])
        best = per_candidate[best_init_name]
        relative_spread = best["std_steps"] / max(best["expected_steps"], 1e-6)
        confidence = float(np.clip(1.0 - relative_spread, 0.0, 1.0))

        return Recommendation(
            recommended_init=InitMethod(best_init_name),
            expected_steps=best["expected_steps"],
            steps_range=(
                max(0.0, best["expected_steps"] - best["std_steps"]),
                best["expected_steps"] + best["std_steps"],
            ),
            confidence=confidence,
            per_candidate=per_candidate,
        )
