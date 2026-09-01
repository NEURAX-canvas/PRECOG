# Results

Every test run in this project writes here, in complementary forms:

- **`experiments.csv`** — a full snapshot of the meta-dataset (docs.md §12): one row per (task, model, hardware, regime, hyperparameters, zero-cost features, outcome), refreshed each time a script calls `precog.reporting.export_csv_snapshots()`. Directly loadable in pandas/Excel/DuckDB without touching the underlying SQLite DB (`data/meta_dataset.db`). This is the *controlled* meta-dataset (fixed search-space points, train/test split locked, §15.1) -- never mixed with search trials (see below).
- **`gate_evaluations.csv`** — the full history of every progression-gate check (docs.md §17): generation, gate number, metric, value, threshold, pass/fail, timestamp. Lets you compare a gate's result across runs/generations instead of only ever seeing the latest console output.
- **`search_trials.csv`** — every trial run by the Search Engine (§9.8), across every arm (cold/informed/restricted/reference) of every comparison script. Kept in a separate table/file from `experiments.csv` on purpose: a search trial is a candidate configuration explored during a search, not a controlled meta-dataset observation, and mixing the two would silently corrupt the train/test split every other script assumes (see `precog/experiment_db.py`'s schema comment).
- **`reports/`** — one timestamped, human-readable Markdown report per test run: method, parameters, full results table, and an explicit verdict (including honest negative results and calibration warnings, not just passes).

## How this gets populated

Every gate/comparison script calls `export_csv_snapshots()` and `write_report()` (see `precog/reporting.py`) at the end of its run, and `precog.search_engine.SearchEngine.search()` logs each trial via `record_search_trial()` when called with `log_run=(...)`. Any new evaluation script should do the same, so results stay in one place instead of scattered across terminal scrollback.

## Reading the reports

Reports are named `<UTC timestamp>_<slug>.md`, sorted chronologically by filename. Current slugs:

- `gate1_ranking` — Gate 1 (§17): does the Trainability Engine's PURE-mode score rank initialization quality the way FULL_TRAINING eventually would?
- `compare_meta_predictors` — four Meta-Predictor designs (§9.7, §19 ablation) compared on the same locked test split; picks a winner by evidence.
- `gate3_search_efficiency` — does warm-starting (seeding one trial) the Search Engine with the Meta-Predictor's recommendation reduce trials-to-target vs a cold search?
- `gate3b_restricted_search` — does *restricting* the search to the recommended init_method (not just seeding it) find near-optimal hyperparameters, and does it beat both a cold search and a restriction to the context-free universal baseline?
