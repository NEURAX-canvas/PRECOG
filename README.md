# PRECOG
## Predictive Configuration & Trainability Engine

**Central statement:** PRECOG does not search for the best hyperparameters after training many configurations; it seeks to learn the relationship between a model's initial state, the properties of the problem, and the learning conditions, in order to predict — before any real training — which configurations have the highest probability of leading to fast, efficient convergence.

**Status:** research project under active reconstruction (V1 — Foundations). No numerical value in this project is an established result yet; see the methodological disclaimer at the top of `docs.md`.

---

## Reference documents

This repository is structured around three documents, meant to be read in this order:

1. **[`docs.md`](./docs.md)** — the full scientific specification: hypotheses (H1-H6), the three-mode PURE/PROBE/FULL TRAINING contract (§5, the project's single most important methodological constraint), the full architecture (Trainability Engine, Meta-Predictor, Search Engine, Causal Discovery, OOD Detection), test protocols, progression gates, and the V1→V6 roadmap.
2. **[`stack.md`](./stack.md)** — the recommended technical stack and its rationale: PyTorch + `torch.func` for computation (batched Jacobians without a Python loop), GPyTorch + BoTorch/Ax as the Bayesian search engine, NATS-Bench/NAS-Bench-Suite-Zero/JAHS-Bench as benchmarks (not NAS-Bench-201/HPOBench, which are deprecated), Rust (Burn/tch-rs) reserved for the production port **once** the meta-predictor has been validated — not before.
3. **[`source.md`](./source.md)** — the reference bibliography (zero-cost proxies, dynamical isometry, meta-learning for HPO, active learning) that informed the specification.

This README does not duplicate their content — it is an entry point.

---

## What this project is not

- Not a NAS in the strict sense (fine-grained architecture is not the main target).
- Not a wrapper around Vizier/Optuna: those engines remain **exploration arms**, not the system's brain.
- Not a performance guarantee: PRECOG is a probabilistic system that must express its uncertainty, never a point value presented as certain.

---

## Where the code stands

The repository was fully rebuilt for V1 (see `docs.md` §25) after a first prototype (Rust + Optuna + LightGBM, kept in `legacy/precog-v0-rust-optuna/` for reference — it produced real empirical results that directly motivated the current Trainability Engine's design, see `legacy/precog-v0-rust-optuna/NOTE.md`).

```
precog/
├── taskgen.py        # synthetic laboratory (§15.2) — controlled task generation
├── model.py           # Model Encoder (§9.1) — parametrizable MLP + Xavier/He/Orthogonal init
├── trainability.py    # Trainability Engine (§9.4) — zero-cost proxies, strict PURE mode
├── modes.py            # PURE / PROBE / FULL TRAINING contract (§5), non-negotiable
└── experiment_db.py   # meta-dataset (§12)
```

The whole research stack is **Python + PyTorch** (`stack.md` §1/§7) — no Rust before the meta-predictor is scientifically validated.

## Getting started

```
python3 -m venv .venv
.venv/bin/pip install torch --index-url https://download.pytorch.org/whl/cpu
.venv/bin/pip install -r requirements.txt
```

See `docs.md` §25 (roadmap) and §17 (progression gates) for what comes next: the first gate to clear (Gate 1, §17) is a ranking correlation ρ ≥ 0.70 between the Trainability Engine's PURE score and the real convergence speed measured in FULL TRAINING, on the synthetic laboratory.
