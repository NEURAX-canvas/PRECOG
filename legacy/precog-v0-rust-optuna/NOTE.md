# Archived: PreTrainOpt v0 (Rust + Optuna + LightGBM)

This is the first MVP prototype of the project, built before the project was
reframed as **PRECOG** (see `/docs.md`, `/stack.md`, `/source.md` at the repo
root). It is kept here for reference and because it produced real empirical
results (see `README-v0.md`), not because it is still the active codebase.

Key findings from this prototype, carried forward into PRECOG's design:
- A gradient-boosting meta-model predicts learning rate from task/model
  features with a real but modest signal (Spearman rho ≈ 0.36).
- The same meta-model predicted optimizer/init_method *worse* than a
  majority-class baseline from static features alone.
- A single-seed few-step probe to correct that was calibrated carefully and
  still made things significantly worse; averaging over 10 seeds fixed the
  raw accuracy (45% → 62%) without producing a significant net speed gain.
- This is direct empirical motivation for PRECOG's Trainability Engine
  (zero-cost proxies computed from the model itself, not just task
  statistics) and its explicit PURE/PROBE mode contract.

To run this legacy prototype: see `GETTING_STARTED.md` in this directory.
