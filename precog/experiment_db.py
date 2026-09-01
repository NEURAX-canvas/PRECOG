"""The meta-dataset: PRECOG's scientific memory (docs.md §12).

Every experiment -- including every failure -- is recorded. Backed by SQLite
here (a local stand-in for the Postgres + MLflow combination stack.md §5
recommends for the production cluster this sandbox doesn't have access to);
the schema is what matters, not the specific database engine.

Strict separation (docs.md §12): rows are tagged with a `split` column
(train/validation/test) at insertion time, and the test split must never be
queried while developing or tuning the meta-predictor -- only for final,
one-shot evaluation (§15.1, §26).
"""
from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[1] / "data" / "meta_dataset.db"

_SCHEMA = """
CREATE TABLE IF NOT EXISTS experiments (
    experiment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL DEFAULT (datetime('now')),
    split TEXT NOT NULL CHECK (split IN ('train', 'validation', 'test')),
    seed INTEGER NOT NULL,
    mode TEXT NOT NULL CHECK (mode IN ('probe', 'full_training')),

    -- Model (docs.md §9.1)
    model_json TEXT NOT NULL,

    -- Dataset / task (docs.md §9.2)
    task_json TEXT NOT NULL,

    -- Hardware (docs.md §9.3)
    hardware_json TEXT NOT NULL,

    -- Regime (docs.md §9.5)
    regime_json TEXT NOT NULL,

    -- Hyperparameters under test (docs.md §10.1)
    training_json TEXT NOT NULL,

    -- Zero-cost descriptors, PURE mode (docs.md §9.4)
    zero_cost_json TEXT,

    -- Outcome / ground truth (docs.md §12 "Ground truth")
    initial_loss REAL,
    final_loss REAL,
    steps_to_threshold INTEGER,
    converged INTEGER NOT NULL,
    diverged INTEGER NOT NULL,
    wall_clock_s REAL,
    delta_w_norm REAL
);
"""


@contextmanager
def connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute(_SCHEMA)
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def record_experiment(
    *,
    split: str,
    seed: int,
    mode: str,
    model_features: dict,
    task_features: dict,
    hardware_features: dict,
    regime: dict,
    training_config: dict,
    outcome,  # precog.modes.TrainResult
    zero_cost_features: dict | None = None,
) -> int:
    with connect() as conn:
        cursor = conn.execute(
            """
            INSERT INTO experiments (
                split, seed, mode, model_json, task_json, hardware_json, regime_json,
                training_json, zero_cost_json, initial_loss, final_loss, steps_to_threshold,
                converged, diverged, wall_clock_s, delta_w_norm
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                split,
                seed,
                mode,
                json.dumps(model_features),
                json.dumps(task_features),
                json.dumps(hardware_features),
                json.dumps(regime),
                json.dumps(training_config),
                json.dumps(zero_cost_features) if zero_cost_features else None,
                outcome.initial_loss,
                outcome.final_loss,
                outcome.steps_to_threshold,
                int(outcome.converged),
                int(outcome.diverged),
                outcome.wall_clock_s,
                outcome.delta_w_norm,
            ),
        )
        return cursor.lastrowid


def load_dataframe(split: str | None = None):
    import pandas as pd

    query = "SELECT * FROM experiments"
    params = ()
    if split is not None:
        query += " WHERE split = ?"
        params = (split,)
    with connect() as conn:
        df = pd.read_sql_query(query, conn, params=params)
    for col in ("model_json", "task_json", "hardware_json", "regime_json", "training_json", "zero_cost_json"):
        expanded = pd.json_normalize(df[col].apply(lambda s: json.loads(s) if s else {}))
        expanded.columns = [f"{col.removesuffix('_json')}.{c}" for c in expanded.columns]
        df = pd.concat([df.drop(columns=[col]), expanded], axis=1)
    return df
