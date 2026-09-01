# Results

Every test run in this project writes here, in two complementary forms:

- **`experiments.csv`** — a full snapshot of the meta-dataset (docs.md §12): one row per (task, model, hardware, regime, hyperparameters, zero-cost features, outcome), refreshed each time a script calls `precog.reporting.export_csv_snapshots()`. Directly loadable in pandas/Excel/DuckDB without touching the underlying SQLite DB (`data/meta_dataset.db`).
- **`gate_evaluations.csv`** — the full history of every progression-gate check (docs.md §17): generation, gate number, metric, value, threshold, pass/fail, timestamp. Lets you compare a gate's result across runs/generations instead of only ever seeing the latest console output.
- **`reports/`** — one timestamped, human-readable Markdown report per test run: method, parameters, full results table, and an explicit verdict (including honest negative results and calibration warnings, not just passes).

## How this gets populated

`scripts/gate1_ranking.py` and `scripts/train_meta_predictor.py` both call `export_csv_snapshots()` and `write_report()` (see `precog/reporting.py`) at the end of their run. Any new evaluation script should do the same, so results stay in one place instead of scattered across terminal scrollback.

## Reading the reports

Reports are named `<UTC timestamp>_<slug>.md`, sorted chronologically by filename. The two current slugs:

- `gate1_ranking` — Gate 1 (§17): does the Trainability Engine's PURE-mode score rank initialization quality the way FULL_TRAINING eventually would?
- `meta_predictor_eval` — the Meta-Predictor (§9.7) evaluated once on the locked TEST split, against the universal-config and random baselines.
