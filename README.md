# PreTrainOpt
## Founding Document — Research, Technical Architecture & Product Strategy

**Subtitle:** *Predicting, before training, the conditions that make a model converge faster, with less data and less compute.*

**Status:** working document — research hypotheses not yet validated, to be tested experimentally.

---

## Table of Contents

1. Executive Summary
2. Problem Statement
3. Scientific Motivation
4. Research Questions
5. Hypotheses
6. State of the Art
7. Existing Projects
8. Google Vizier — Analysis
9. Theoretical Foundations
10. Training Dynamics
11. Hyperparameter Taxonomy
12. Initialization
13. Synthetic Learning Laboratory
14. Meta-Learning
15. Causal Experimental Framework
16. Mathematical Formulation
17. Optimization Objectives
18. System Architecture
19. Software Architecture
20. Data Architecture
21. Experiment Database
22. Meta-Dataset
23. Algorithms
24. Experimental Protocol
25. Baselines
26. Ablation Studies
27. Evaluation Metrics
28. Statistical Analysis
29. Production Architecture
30. API Design
31. MLOps
32. Distributed Computing
33. Security / Reliability
34. Failure Modes
35. Research Risks
36. Open Research Questions
37. Scientific Positioning
38. Roadmap
39. MVP
40. Future Extensions
41. Potential Scientific Contributions
42. Potential Industrial Applications
43. Open-source Strategy
44. Product Strategy
45. Final Research Thesis

Appendix A — Project Identity (names, tagline, mission)
Appendix B — Final Recommendation (prototype, priority experiments, 3 hypotheses to test first)

---

## 1. Executive Summary

Training a neural network today is driven by a **trial-and-error** cycle: pick a configuration (learning rate, optimizer, batch size, initialization…), train, observe the loss, adjust. Tools like **Google Vizier**, **Optuna**, or **Hyperband** automate this cycle, but don't change its nature: they remain *configuration → training → metric → new configuration* loops, where every iteration costs a training run (full or partial).

**PreTrainOpt** starts from a different question:

> Can we, from properties observable **before** training or with a minimal amount of real training (model architecture, task statistics, local loss geometry around initialization), **predict** a training configuration that converges faster, with less data and less compute — rather than *discovering* it through successive trials?

This document:

- poses the research question and breaks it down into testable sub-questions;
- explicitly distinguishes what is **established**, what is **plausible but unproven**, and what constitutes **our own hypothesis**;
- proposes a causal (not merely correlational) experimental methodology grounded in a **synthetic task laboratory**;
- defines a software architecture (Rust + Python) to build this laboratory, run thousands of controlled experiments on it, and extract a **predictive meta-model**;
- proposes an 8-version roadmap, from an MLP prototype to a production API;
- concludes with a concrete recommendation for the first prototype to build.

The project is deliberately designed to be able to **fail cleanly**: if the central hypothesis doesn't hold (pre-training properties are insufficient to predict learning dynamics), the synthetic laboratory and *experiment database* built along the way remain useful contributions in their own right (empirical study of training dynamics, HPO baseline benchmark, etc.).

---

## 2. Problem Statement

**Observation.** The cost of training a model heavily depends on a set of decisions made *before* the first gradient step: initialization, learning rate, optimizer, batch size, architecture, schedule. These decisions are currently chosen by:

- heuristics inherited from the literature (e.g. He init for ReLU, LR ≈ 3e-4 for Adam);
- expensive automated searches (grid/random search, Bayesian optimization, Vizier) requiring many full or partial training runs;
- engineering intuition, hard to transfer and reproduce.

**Problem.** There is currently no system that, from the sole description of a model and a task (before any significant training), **predicts** a near-optimal configuration — instead of *searching* for it by trial.

**Formulation.** We seek to replace, or at least intelligently seed, the classic loop:

$$
H \rightarrow \mathrm{Train}(H) \rightarrow \mathrm{Performance}
$$

with a prediction function:

$$
X_{model}, X_{task}, X_{data} \;\longrightarrow\; \widehat{H^*}
$$

where \(\widehat{H^*}\) is a training configuration (initialization, LR, optimizer, batch, schedule, etc.) obtained **without** — or with a training budget far below — a classic hyperparameter search.

**What this project is not.** It is not one more *hyperparameter tuner*. A tuner *searches*; we want to **predict**, possibly correcting afterward with a minimal training budget ("few-step probing", see §15).

---

## 3. Scientific Motivation

Three observations motivate the project:

1. **Transfer learning works.** A pre-trained model learns a new task with vastly less data than a fresh model, because it starts from a better region of parameter space. This proves that *the starting point* matters as much as the optimization algorithm.
2. **The local loss geometry is computable without full training.** The gradient and curvature approximations (Hessian, NTK) are observable right at initialization, in one or a few *forward/backward passes*. If these quantities are informative about future dynamics, they constitute a *cheap* signal.
3. **Current HPO tools ignore the structure of the problem.** Vizier and Optuna treat training as a black box \(f(x)\); they reuse no knowledge from one task to the next (except via manual warm-start heuristics). A meta-learning system trained across thousands of tasks could, in theory, generalize this knowledge.

These three observations do not *prove* our approach will work — they only justify that it is **worth testing rigorously**.

---

## 4. Research Questions

**Main question (RQ0)**

> To what extent can we predict the training conditions (initialization, hyperparameters) that enable fast convergence and strong *sample efficiency*, from information available before full training?

**Sub-questions**

| # | Question | Expected answer type |
|---|---|---|
| Q1 | Can we predict an effective learning rate without full training? | Correlation, then predictive model |
| Q2 | Can we predict the appropriate optimizer (SGD/Adam/AdamW/Lion…)? | Classification |
| Q3 | Can we predict the batch size? | Regression / ordinal classification |
| Q4 | Can we predict weight decay, warmup, LR schedule? | Multi-output regression |
| Q5 | Can we find a better initialization strategy than standard heuristics? | Comparative study |
| Q6 | Can we predict the number of samples needed to reach a target performance? | Regression (local scaling law) |
| Q7 | Can we predict the number of steps needed to reach a target loss? | Regression |
| Q8 | Do the properties of the untrained model (spectrum, norms, architecture) predict its future dynamics? | Feature-importance analysis |
| Q9 | Are synthetic tasks sufficient to learn these relationships? | Transferability study |
| Q10 | Does this knowledge transfer to real models and data? | External (out-of-distribution) validation |

Each sub-question is tied to a dedicated experiment in the protocol (§24).

---

## 5. Hypotheses

Stated explicitly to be **falsifiable**.

- **H1 (pre-training signal).** The characteristics of the untrained model and of the task (before any significant training) carry statistically exploitable information about the optimal training configuration.
- **H2 (synthetic → real transferability).** A relationship learned on synthetic tasks produces better predictions than default heuristics on comparable real tasks.
- **H3 (prediction cost ≪ training cost).** The computational cost of the prediction (features + meta-model inference, possibly + a short *probe*) is far below the cost of a classic hyperparameter search, for a comparable or better performance gain.
- **H4 (non-universality).** There is **no** universal configuration; the optimal configuration jointly depends on the architecture, the task, and the data — so a *conditional* predictor is required, not a simple global empirical rule.
- **H5 (diminishing returns of probing).** Beyond a certain *few-step probing* budget (~0.1–1% of training), the marginal information gain about the optimal configuration drops sharply.

Each hypothesis is tested independently (§24, §26); the failure of one hypothesis does not doom the others.

---

## 6. State of the Art

| Established (literature) | Used industrially | Plausible but unproven | Our own hypothesis |
|---|---|---|---|
| Xavier/He init reduce gradient explosion/vanishing | AdamW + cosine schedule + warmup as standard for LLMs | Spectral statistics at init predict the optimal LR | A meta-model trained on synthetic tasks transfers to real tasks |
| The NTK describes the dynamics of infinitely wide networks | Bayesian optimization (Vizier, Optuna) for HPO | The NTK at initialization is a usable proxy in practice (finite width) | A probing budget of 0.1–1% suffices to correct a *zero-shot* prediction |
| *Scaling laws* relate model size/data/compute to loss | Transfer learning / fine-tuning from pre-trained checkpoints | Local (small-scale) scaling laws predict larger-scale behavior | An architecture-aware + data-aware initialization beats standard heuristics in a generalizable way |
| Batch size interacts with the optimal LR (empirical linear rule) | Gradient clipping, LR warmup to stabilize Transformers | Directional gradient consistency (successive cosine) correlates with convergence speed | Task + model features suffice, without access to the real target-task data |

This table must be kept up to date as the project progresses — every right-hand cell that moves to the left is a publishable result.

---

## 7. Existing Projects

- **Google Vizier** — black-box optimization service (Bayesian optimization + bandits), used internally at Google. Detailed analysis in §8.
- **OSS Vizier / "Towards Learning Universal Hyperparameter Optimizers with Transformers" (Google, 2022)** — an evolution of the Vizier lineage toward a learned model (Transformer) trained on thousands of past studies to steer the search in a new study. An important signal: even Vizier's "black box" philosophy is drifting toward a bet structurally close to H1 (a relationship learned across tasks transfers) — applied *during* the search rather than zero-shot before it, as PreTrainOpt aims to do. The disagreement with Vizier is therefore not philosophical but empirical: at what point is structural knowledge worth more than the cost of ignoring it? (see empirical postscript, §8).
- **Optuna** — open-source HPO framework, TPE (Tree-structured Parzen Estimator), built-in pruning (early stopping of unpromising trials).
- **Ray Tune / Hyperband / ASHA** — large-scale search with aggressive early stopping of unpromising trials (successive halving).
- **Population Based Training (PBT, DeepMind)** — a hybrid of evolution and search, mutates hyperparameters *during* training rather than between separate trials.
- **AutoML-Zero, NAS (Neural Architecture Search)** — automated architecture search, close but orthogonal (we assume the architecture is given).
- **µP (maximal update parametrization, Microsoft/Tensor Programs)** — a reparametrization that makes the optimal LR quasi-invariant to network width: a concrete example that a *structural* property of the model can drastically reduce the need for hyperparameter search. **A direct and serious reference for PreTrainOpt.**
- **DeepMind "Scaling Laws" / Chinchilla** — empirical laws relating model size, dataset size, and optimal compute; close in spirit (predicting *before* having trained fully) but at a different scale (across-run, not within-run dynamics).

**Positioning.** PreTrainOpt sits between µP (structural, theoretical guarantees but narrow scope) and Vizier (empirical, broad scope but costly). Our bet: combine a structural signal (like µP) with a learned meta-model (like Vizier learns from a history of trials), but upstream of training rather than during it.

---

## 8. Google Vizier — Analysis

**Philosophy.** The opening sentence of the Vizier paper's abstract (Golovin et al., 2017) sums up its entire position: *"Any sufficiently complex system acts as a black box when it becomes easier to experiment with than to understand."* This is not an admission of defeat but a deliberate pragmatic choice: rather than understanding why a system behaves the way it does, treat it as an opaque function \(f(x)\) and optimize through experimentation.

This philosophy is honest about its limits and coherent with its goal: Vizier makes no assumption about the structure of the problem, which makes it *universal* (it becomes the default tuning engine at Google, reused all the way into Google Cloud ML's HyperTune) — a system that works for any \(f(x)\) has enormous engineering value precisely because it presupposes nothing. It is a *systems engineering* paper applied to optimization (robustness, scalability, a service shared across thousands of teams with heterogeneous problems), not a paper that seeks to unravel learning dynamics.

The corresponding structural limitation — and the exact point where PreTrainOpt positions itself in opposition — is that "black box" means discarding structural information at every new search. Vizier doesn't know that a 12-layer Transformer and a 24-layer Transformer share a related loss geometry (which µP exploits explicitly, §9); every new task starts from scratch, barring manual warm-start. "Easier to experiment with than to understand" is true at engineering scale — a rational choice when you have to serve thousands of internal teams under product time constraints — but it freezes the research question: you optimize, you never seek to know *why* a given region of hyperparameter space works. That is precisely the blind spot H1 targets.

**Principle.** Vizier treats training as a black-box function \(f(x)\) to optimize:

```
Search Space → Vizier → Hyperparameters → Training → Metric → Vizier → ...
```

**Key components:**

- *Search space*: domains (often log-scale for LR, weight decay) and types (continuous, discrete, categorical) of the hyperparameters.
- *Objective*: one or more metrics to optimize (e.g. validation loss, or a composite objective).
- *Trials*: each trial = a tested configuration + its result.
- *Bayesian optimization*: a probabilistic model (often a Gaussian process or a TPE-type model) learns the surface \(f(x)\) from past trials and proposes the next point, arbitrating exploration vs. exploitation.
- *Early stopping*: stopping unpromising trials before training completes (compute savings).
- *Multi-objective*: Pareto-front search when several metrics trade off against each other (e.g. accuracy vs. latency).

**Fundamental limitation for our objective.** Vizier **always trains** to evaluate a configuration — even partially. It has no notion of reusable "model/task characteristics" from one search to another: every new task restarts (barring manual warm-start).

**Difference with PreTrainOpt:**

```
Vizier :        Configuration → Training → Metric
PreTrainOpt :    Model/Task analysis → Prediction → Configuration → (Minimal probe) → Validation
```

**Vizier's role in our project.** It is not a competitor to replace outright but a **tool for building the meta-dataset**: during the research phase (synthetic laboratory), Vizier (or an equivalent Bayesian optimization method) is used to find the near-optimal *real* configuration for each synthetic task — that result becomes a training example for our meta-model. Vizier is thus used **offline**, as ground-truth generation, not as a component of the final system.

**Empirical postscript (MVP, Rust/Optuna/LightGBM prototype from §39).** The first prototype built as part of this document gave a concrete, small-scale illustration of this black-box-vs-structure trade-off:

- Structural signal exists but is weak and uneven across hyperparameters. On 110 synthetic tasks (MLP, regression), a gradient-boosting meta-model predicts the optimal learning rate with a modest correlation (rho ≈ 0.36, 52% of predictions within 2x of the true value) — a real signal, far from sufficient on its own. For optimizer/init_method, by contrast, the same meta-model predicted **worse than a trivial rule** (always answer the majority class): 33-57% accuracy versus 43-67% for the naive baseline.
- Trying to exploit more structure (a *few-step probe* inspired by Vizier's early stopping — a few dozen real steps before choosing optimizer/init) first **actively hurt**: calibrated with a single seed, it made predictions significantly worse (p = 0.027) than ignoring the probe. The cause: every trial starts from a different random initialization, so a single-seed probe per candidate is a noisy measurement, not a reliable verdict.
- Averaging the probe over 10 independent seeds fixed the raw accuracy (45% → 62% correct optimizer/init answers) without producing a net, significant gain in convergence speed (8 wins / 13 losses across 21 held-out tasks, p = 0.19) — a sign that the "best config" label itself is noisy (the quality landscape across combinations is likely fairly flat for many tasks).

This is neither a validation nor a refutation of H1: it is the empirical demonstration, in miniature, of this section's thesis — exploiting structure instead of the black box is possible but costs real methodological rigor (calibration, replication, seeds), and can actively backfire if done poorly. The black box doesn't win because it's better; it wins by default until structure-exploitation has been properly mastered.

---

## 9. Theoretical Foundations

- **Gradient descent and the role of the LR.** \(\theta_{t+1} = \theta_t - \eta \nabla_\theta L\) — the LR controls the step size; too small → slow convergence; too large → divergence/oscillation. The stable region depends on the local curvature (see Hessian).
- **Neural Tangent Kernel (NTK).** In the infinite-width limit, the dynamics of a network trained by gradient descent are equivalent to a linear model in a feature space fixed by the tangent kernel at initialization \(K(x,x') = \nabla_\theta f(x)^\top \nabla_\theta f(x')\). At finite width, the NTK evolves during training, but its spectrum at initialization remains an indicator used in the literature to analyze "trainability".
- **µP (maximal update parametrization).** A per-layer reparametrization of weights and LR such that the learning dynamics (to first order) become invariant to network width — allowing the LR to be tuned on a small model and transferred directly to a large one. It is the most concrete proof, to date, that a structural property **known before training** can replace a hyperparameter search.
- **Scaling laws.** Empirical relations \(L(N, D, C) \approx\) a power-law function of model size \(N\), data \(D\), and compute \(C\). Useful for extrapolation, but defined *between* complete runs, not *within* a run's dynamics — indirect relevance to PreTrainOpt (as methodological inspiration).
- **Hessian analysis / sharpness.** The local curvature \(\nabla^2 L(\theta_0)\) bounds the stable step size (analogous to the stability condition \(\eta < 2/\lambda_{max}\) in quadratic convex optimization). Exact computation is expensive (\(O(P^2)\)); approximations (Hutchinson trace estimator, power iteration on the Hessian-vector product) are usable at \(O(P)\) cost per evaluation.
- **Fisher information.** \(F = \mathbb{E}[\nabla \log p(y|x;\theta)\nabla \log p(y|x;\theta)^\top]\) — relates loss geometry to curvature; used by natural-gradient optimizers (K-FAC) and as a proxy for "exploitable information quantity" from the data.

**Section conclusion.** *Partial* theoretical foundations exist that make hypothesis H1 plausible (NTK, µP, local Hessian) — but none currently provide a general-purpose predictor covering all hyperparameters (optimizer, batch, schedule). This is precisely the space PreTrainOpt explores empirically.

---

## 10. Training Dynamics

Variables to instrument at every step (or at regular intervals) during the laboratory's training runs:

$$
L_t,\quad \|\nabla L_t\|,\quad \|\theta_t\|,\quad \|\Delta\theta_t\|,\quad \frac{\|\nabla L_t\|}{\|\theta_t\|},\quad \cos(g_t, g_{t-1})
$$

| Signal | Usefulness | Cost | Computable before full training? |
|---|---|---|---|
| Gradient norm \(\|\nabla L\|\) | Detects vanishing/exploding gradients | Low (already computed) | Yes — from the 1st backward pass |
| Successive cosine \(\cos(g_t,g_{t-1})\) | Directional consistency ≈ proxy for "quality" of the learning signal | Low | Requires ≥ 2 steps |
| Gradient variance (across a batch's samples) | Estimation noise, linked to the optimal batch size | Medium | Yes, over a few batches |
| Update norm \(\|\Delta\theta\|\) | Effective displacement speed | Low | After 1 step |
| Activation statistics (mean/variance per layer) | Detects saturation, dead ReLUs | Low | Yes — 1 forward pass |
| Weight statistics (per-layer norm, distribution) | Initialization quality | None (weights already known) | Yes — before any training |
| Curvature approximation (Hutchinson trace, power iteration) | Stability, theoretical max LR | Medium to high | Yes — a few extra backward passes |
| NTK (approximated spectrum, condition number) | Theoretical "trainability" | High (approximations needed in practice) | Yes at init, expensive at scale |
| Sharpness (loss around \(\theta\) after perturbation) | Link to generalization | High | Requires several forward passes |

**Ranking for a "cheap" system (priority candidates):** weight/activation statistics at init, gradient norm and variance over a few batches, successive cosine over a short window. **Expensive candidates to defer to V2+:** full NTK, full Hessian, exhaustive perturbation-based sharpness.

---

## 11. Hyperparameter Taxonomy

### Optimization
learning rate · optimizer (SGD/Adam/AdamW/Lion…) · momentum · β1 · β2 · ε · weight decay · gradient clipping

### Training
batch size · gradient accumulation · epochs · warmup (duration, shape) · scheduler (cosine/exponential/step/constant) · mixed precision

### Architecture
depth · width · activation · normalization (BatchNorm/LayerNorm/RMSNorm) · residual connections · attention configuration · initialization method

### Initialization
Xavier/Glorot · He/Kaiming · orthogonal · normal/uniform · scaled init · *architecture-aware* (e.g. µP) · *data-aware* (calibrated on a data sample)

### Data
dataset size · noise · diversity · redundancy · distribution · entropy · complexity · class imbalance · curriculum · augmentation

For **each** hyperparameter, the standard analysis grid to apply (documented once, applied systematically in the meta-dataset):

1. functional role;
2. influence on the gradient (norm, variance, direction);
3. influence on convergence (speed, stability);
4. known interactions with other hyperparameters (e.g. LR ↔ batch size, LR ↔ width via µP);
5. how to measure it empirically in the laboratory;
6. which pre-training signal(s) could predict it;
7. which search algorithm optimizes it best as *ground truth* (Bayesian opt, grid, etc.).

---

## 12. Initialization

Methods to compare systematically (mandatory baselines for the initialization benchmark):

- **Xavier/Glorot** — variance calibrated for linear/tanh activations.
- **He/Kaiming** — variance calibrated for ReLU and its variants.
- **Orthogonal** — preserves norm during propagation, useful in deep RNNs.
- **Simple normal / uniform** — naive baselines.
- **Scaled init** (e.g. GPT-2 style: scaling by \(1/\sqrt{2L}\) for deep residual layers).
- **Architecture-aware (µP)** — per-layer LR and initialization variance explicitly dependent on width, to make the dynamics scale-invariant.
- **Data-aware init** — calibrated from a sample (LSUV — *Layer-Sequential Unit-Variance*, or activation normalization measured on a mini-batch before training).
- **New candidate methods (to explore, unvalidated)** — initialization conditioned on task features predicted by our own meta-model (Q5).

---

## 13. Synthetic Learning Laboratory

The project's central component: a generator of **controlled tasks**, allowing one factor to be varied at a time (necessary for causal inference, §15).

**Typical generative functions:**

$$
y = x_1 + x_2 \qquad y = \sin(x_1) + 0.5x_2^2 - x_3x_4 + \epsilon \qquad y = \sin(x_1x_2) + e^{-x_3}
$$

**Controllable parameters:**

- input dimension;
- noise level \(\epsilon\);
- complexity (degree of nonlinearity, number of interaction terms);
- redundancy (fraction of correlated/duplicated features);
- diversity / distribution (uniform, Gaussian, mixture);
- dataset size;
- class imbalance (for classification tasks).

**Architectures covered in V0.1:** MLP (synthetic regression/classification). Planned extension: CNN on procedurally generated synthetic images (parametric shapes, textures), miniature Transformer on synthetic sequences (copy, sort, parity tasks — inspired by algorithmic-reasoning benchmarks).

**Why synthetic rather than real from the start?** Because we control exactly the variable being varied — a necessary condition to distinguish correlation from causation (§15). A real dataset systematically confounds several factors (noise, redundancy, distribution) that cannot be isolated.

---

## 14. Meta-Learning

**Problem formulation:**

$$
(X_{model}, X_{task}, X_{data}) \;\longrightarrow\; \mathrm{OptimalTrainingConfiguration}
$$

**Candidate approaches, compared:**

| Approach | Expected accuracy | Cost | Implementation complexity | Scalability | Suited to the 1st prototype? |
|---|---|---|---|---|---|
| Simple supervised model (gradient boosting / random forest on tabular features) | Medium | Low | Low | Good | **Yes — recommended** |
| Gaussian Processes (surrogate) | Good in low dimension | Medium | Medium | Poor (scales as \(O(n^3)\)) | No (V2+) |
| Bayesian optimization (per task, not meta) | Good but expensive per task | High (real training runs) | Low (existing Optuna/Vizier) | Good | Used for ground-truth generation, not as the final predictor |
| Neural network (MLP on features) | Good if enough meta-data | Medium | Medium | Good | V0.3+ once the meta-dataset is large enough |
| Graph Neural Network (architecture represented as a graph) | Potentially the best cross-architecture generalization | High | High | Medium | V0.4+ (once several architecture families are covered) |
| Transformers for meta-learning (over sequences of trials) | Promising but data-hungry | High | High | Good at scale | Exploratory research, not a priority |
| Learned optimizers (meta-learning the update rule itself) | Ambitious, out of initial scope | Very high | Very high | Poor at the current state of the art | No — a separate track (§27) |

**Recommendation for the prototype (V0.2):** a **gradient boosting** model (LightGBM/XGBoost type) on tabular features (model statistics + task statistics). Rationale: interpretable (feature importance directly usable for Q8), needs little data compared to a neural network, fast to iterate on, a robust tabular-data standard.

---

## 15. Causal Experimental Framework

**Principle.** Don't settle for correlations observed on the meta-dataset — verify, through controlled experimentation, that changing a factor actually *causes* a change in dynamics.

```
Controlled experiment
        ↓
Change ONE SINGLE factor
        ↓
Measure the effect (steps-to-threshold, etc.)
        ↓
Repeat (other random seeds)
        ↓
Analyze interactions (2 factors at a time)
        ↓
Causal hypothesis
```

**Methods to mobilize:**

- **Factorial experimental designs** — vary \(k\) factors at 2 or 3 levels simultaneously, with replication, to estimate main effects and interactions at a lower cost than an exhaustive sweep.
- **Ablation studies** — remove a system component (feature, module) and measure the performance loss (see §26).
- **Sensitivity analysis / Sobol indices** — decompose the output metric's variance by factor and by interaction, to quantify (not just rank) each factor's importance.
- **ANOVA** — statistical significance test for main effects/interactions in a factorial design.
- **SHAP (SHapley Additive exPlanations)** — on the final meta-model, to explain *which features* drive each prediction (useful for Q8, and for product trust).
- **Causal graphs (DAGs) + intervention experiments** — beyond observational correlation, formalize causal hypotheses (e.g. "width → optimal LR" rather than the reverse) and test them through direct intervention (fix width, vary the rest).

**Relative relevance.** Factorial designs + ANOVA/Sobol are **indispensable** from Phase 1 onward (cheap, rigorous). SHAP is useful on an ongoing basis on the meta-model. Formal causal graphs are an additional layer of rigor to introduce once the main empirical relationships have stabilized (Phase 3+).

---

## 16. Mathematical Formulation

**General problem.**

$$
H^* = \arg\min_H \; \mathbb{E}\big[\mathcal{C}(H, \mathrm{Model}, \mathrm{Task})\big]
$$

where \(\mathcal{C}\) is a cost combining performance, convergence speed, and compute budget (see §17).

**Direct prediction target:**

$$
T_\epsilon = \min\{t : L_t < \epsilon\}
$$

the number of steps needed to reach a target loss \(\epsilon\). We seek a model \(g\) such that:

$$
\widehat{T_\epsilon} = g\big(X_{model}, X_{task}, H\big) \approx T_\epsilon
$$

**Reformulating the classic optimization problem as a prediction problem:**

$$
\underbrace{H \rightarrow \mathrm{Train}(H) \rightarrow \mathrm{Performance}}_{\text{classic approach (Vizier)}}
\qquad\Longrightarrow\qquad
\underbrace{X_{model}, X_{task}, X_{data} \rightarrow \mathrm{Predict}(H^*)}_{\text{PreTrainOpt}}
$$

**Multi-criteria objective (see §17):**

$$
\min\big(T_\epsilon,\; N_\epsilon,\; \mathrm{FLOPs}_\epsilon\big) \quad \text{subject to} \quad \mathrm{Accuracy} \geq \mathrm{threshold}
$$

---

## 17. Optimization Objectives

Don't limit ourselves to the final validation loss. Target metrics:

- \(T_\epsilon\) — **steps** needed to reach a target loss \(\epsilon\);
- \(N_\epsilon\) — **samples** needed to reach a target performance (*sample efficiency*);
- \(C_\epsilon\) — **compute** (FLOPs) needed;
- \(E_\epsilon\) — **energy** consumed (proxy: FLOPs × hardware factor, or a direct measurement if the infrastructure allows it);
- \(\mathrm{AUC} = \int L(t)\,dt\) — area under the learning curve, summarizes the whole trajectory as a scalar.

**Composite objective:**

$$
\mathrm{Efficiency} = f(\mathrm{Performance}, N_\epsilon, T_\epsilon, C_\epsilon, \mathrm{Memory}, E_\epsilon)
$$

In practice, we formulate a **multi-objective** problem (Pareto front between convergence speed, sample efficiency, and final performance) rather than a single arbitrary scalar — the weighting between objectives is a product choice, not a scientific fact, and must remain explicit and adjustable.

---

## 18. System Architecture

```
                    Model
                      │
                      ↓
              Model Analyzer
                      │
                      ↓
             Feature Extraction
                      │
          ┌───────────┴───────────┐
          ↓                       ↓
     Model Features          Task Features
          │                       │
          └───────────┬───────────┘
                      ↓
                Meta Predictor
                      ↓
             Candidate Configs
                      ↓
               Rank / Optimize
                      ↓
             Recommended Config
                      ↓
             Optional Probe (few-step)
                      ↓
             Final Configuration
                      ↓
                  Training
                      ↓
              Feedback / Logs
                      ↓
             Meta-dataset update
```

**Components:**

- **Model Analyzer** — inspects the architecture (parameter count, depth, width, layer types, normalization) without running any training.
- **Feature Extraction** — computes model features (weight statistics at init, approximated spectrum) and task features (sampled dataset statistics: dimension, estimated noise, entropy, redundancy).
- **Meta Predictor** — the meta-model (§14), produces one or more candidate configurations with a confidence score.
- **Rank/Optimize** — if multiple candidates, arbitration (possibly via a local mini-search around the prediction).
- **Optional Probe** — a few real training steps to correct the *zero-shot* prediction if the budget allows (§15; see also the dedicated "zero-training or minimal-training" regimes).
- **Feedback loop** — the real outcome of the full training run is fed back into the *experiment database*, to periodically retrain the meta-model (continual meta-learning, §23 and the Roadmap below).

---

## 19. Software Architecture

Main language: **Rust** (performance, memory safety, consistent with the ecosystem already used elsewhere) with **Python integration** for the ML ecosystem (PyTorch/JAX, analysis notebooks, rapid meta-model prototyping).

```
pretrainopt/
├── core/           # shared types, config, errors, common traits
├── model/          # model definition and introspection (MLP, CNN, Transformer)
├── taskgen/        # parametric synthetic task generator
├── analysis/       # feature extraction (spectral, jacobian, curvature, statistics)
├── initialization/ # initialization strategies (standard + architecture/data-aware)
├── optimization/   # optimizers, schedulers, gradient clipping
├── meta/           # meta-model: features → configuration prediction
├── experiments/    # experiment runner, trial orchestration
├── benchmark/      # baselines (random/grid/Bayesian/Vizier/Optuna), comparators
├── storage/        # experiment database / meta-dataset persistence
├── api/            # inference service (configuration prediction)
├── cli/            # command-line interface
└── dashboard/      # experiment visualization, curves, feature importance
```

**Detailed responsibilities:**

- `core`: configuration types (`TrainingConfig`, `ModelFeatures`, `TaskFeatures`), `Trainable`, `Measurable` traits.
- `model`: construction of parametrizable models (number of layers, width, activation) + introspection (parameter counting, layer traversal).
- `taskgen`: generative functions, control of noise/complexity/redundancy, reproducible sampling (explicit seeds).
- `analysis`: computation of the §10 signals (norms, gradient variance, successive cosine, curvature approximations via Hutchinson/power-iteration).
- `initialization`: Xavier/He/orthogonal/scaled/µP implementations + hook for learned strategies.
- `optimization`: SGD/Adam/AdamW/Lion, schedulers (cosine/step/exponential), warmup, clipping.
- `meta`: meta-model training and inference (features → configuration), interface with a Python backend (gradient boosting) via FFI or a separate service.
- `experiments`: run orchestration (sequential or parallel), seed management, writing to the *experiment database*.
- `benchmark`: baseline implementations/wrappers (Optuna interfacing in Python; Vizier via API if accessible; native Rust grid/random).
- `storage`: data schema (§20-22), backend (see technology stack below).
- `api`: prediction endpoint (see §30).
- `cli`: commands to launch task generation, laboratory training, or configuration inference.
- `dashboard`: visualization (loss curves, SHAP feature importance, baseline comparison).

---

## 20. Data Architecture

Three families of data to model:

1. **Task Registry** — definition of the generated synthetic tasks (generative parameters, seed, computed statistics).
2. **Experiment Database** — one record per training trial (see §21).
3. **Meta-Dataset** — an aggregated view of the Experiment Database, structured as a supervised learning dataset for the meta-model (see §22).

Flow:

```
Task Registry ──┐
                 ├──► Experiment Runner ──► Experiment Database ──► Meta-Dataset ──► Meta-Model
Model Registry ──┘                                  ▲                                   │
                                                     └───────────── Feedback loop ◄──────┘
```

---

## 21. Experiment Database

Schema (per experiment):

```text
experiment_id
timestamp
seed

# Model features
model_type, depth, width, n_params, activation, normalization,
init_method, weight_norm_stats, spectral_stats

# Task features
task_id, input_dim, noise_level, complexity_score, redundancy,
n_samples, distribution_type, class_imbalance

# Hyperparameters (= H, the tested input)
learning_rate, optimizer, batch_size, weight_decay,
warmup_steps, scheduler_type, gradient_clip

# Dynamics (time series or summary statistics)
loss_curve[], grad_norm[], grad_cosine_similarity[],
param_update_norm[], activation_stats[]

# Compute
flops, wall_clock_time, peak_memory, device

# Outcome (= the ground truth to predict)
steps_to_threshold, samples_to_threshold, final_loss,
final_accuracy, converged (bool), diverged (bool)
```

This schema serves both as an experiment log (reproducibility) and as a source for building the meta-dataset.

---

## 22. Meta-Dataset

A derived view of the Experiment Database, one row = one (pre-training features, tested configuration, result) tuple:

$$
\big(X_{model},\, X_{task},\, H\big) \;\longrightarrow\; \big(T_\epsilon,\, N_\epsilon,\, \mathrm{Accuracy}\big)
$$

To train the meta-model **predictive of \(H^*\)** (rather than merely predictive of a given \(H\)'s outcome), for each task/model we keep the **best configuration found** by the reference Bayesian search (§8) as the target:

$$
\big(X_{model},\, X_{task}\big) \;\longrightarrow\; H^*_{found\;by\;Vizier/Optuna}
$$

Two formulations are therefore useful and complementary: an **outcome regression** model (useful for causal analysis, §15) and a **direct optimal-configuration prediction** model (useful for the final product, §29-30).

---

## 23. Algorithms

Algorithms to implement/integrate, by category:

- **Task generation**: reproducible parametric sampling (generative functions + controlled noise).
- **Reference search (ground-truth generation)**: Bayesian optimization (TPE via Optuna, or GP-based), Successive Halving/Hyperband to accelerate meta-dataset generation at lower cost.
- **Feature extraction**: Hutchinson trace estimator (approx. of \(\mathrm{tr}(H)\)), power iteration (approx. of \(\lambda_{max}\) of the Hessian or NTK), weight/activation statistics (mean, variance, norm, kurtosis).
- **Meta-model**: gradient boosting (baseline), then MLP/GNN as it evolves (§14).
- **Explanation**: SHAP for feature attribution.
- **Causal optimization**: factorial designs, ANOVA, Sobol indices (§15).

---

## 24. Experimental Protocol

| Phase | Subject | Hypothesis tested | Variables | Baseline | Success criterion |
|---|---|---|---|---|---|
| **1** | MLP + synthetic tasks | H1, Q1-Q7 | LR, optimizer, batch, init, 5 hyperparameters | Standard defaults (Adam LR=3e-4) | Meta-model beats the baseline on ≥ 60% of synthetic test tasks |
| **2** | CNN + synthetic tasks (procedural images) | H1, H2 (generalization to another architecture family) | + architecture (depth/width/kernel) | Same + standard CNN heuristics | The meta-model trained in Phase 1 (or retrained) transfers with moderate degradation |
| **3** | Miniature Transformer | H1, H2, µP as reference | + attention config | µP + standard AdamW | Comparable to or better than µP alone on *steps-to-threshold* |
| **4** | Real datasets (small scale: e.g. tabular/simple-image classification) | H2, H3 | Same + real data statistics | Vizier/Optuna with an equivalent budget | \(N_{ours} \le N_{baseline}\) and \(T_{ours} \le T_{baseline}\) at equal performance |
| **5** | Pre-trained models (fine-tuning) | H2, H3 | Fine-tuning LR/schedule | Standard fine-tuning heuristics | Measurable reduction in fine-tuning steps at equal performance |
| **6** | Larger models | H4, H5 (scaling limits) | Probing budget (0% / 0.1% / 1%) | Naively extrapolated Phase 4/5 | Identify the breaking point where *zero-shot* prediction becomes insufficient |

Each phase produces a report: hypothesis, result, hypothesis confirmed/refuted/partial, updated risks.

---

## 25. Baselines

Mandatory comparisons, at every phase:

- default hyperparameters (e.g. Adam LR=3e-4, no warmup);
- manual tuning by an experienced engineer (if possible, to calibrate the gap with human expertise);
- random search;
- grid search;
- Bayesian optimization (Optuna);
- Google Vizier (if access is available);
- Hyperband/ASHA;
- classic initialization methods alone (without the rest of the system), to isolate initialization's contribution from the other hyperparameters.

**Decision rule.** PreTrainOpt is considered "performant" on a phase only if it dominates (or matches at a much lower cost) the best baseline **at a comparable or lower compute budget**.

---

## 26. Ablation Studies

```
Full system
  − without initialization predictor
  − without task features
  − without model features
  − without gradient/curvature features
  − without meta-learning (back to pure Bayesian opt)
  − without synthetic tasks (direct training on little real data)
  − without short probing (pure zero-shot)
```

For each variant: measure the degradation on the §27 metrics. Goal: identify **which component actually carries the value** — a necessary condition for prioritizing engineering effort (V0.3 vs V0.4, etc.) and for any credible scientific publication.

---

## 27. Evaluation Metrics

- **StepsToThreshold** \(T_\epsilon\) — sensitive to the choice of \(\epsilon\), to be defined per task relative to a well-trained model's loss.
- **SamplesToThreshold** \(N_\epsilon\) — captures sample efficiency independently of compute speed.
- **ComputeToThreshold** \(C_\epsilon\) — FLOPs, comparable independently of hardware.
- **AreaUnderLearningCurve** — summarizes the whole trajectory, robust to arbitrary thresholds but less directly interpretable.
- **Meta-model prediction accuracy** — gap between the predicted \(H^*\) and the real \(H^*\) (found by exhaustive search), and the performance gap between the two configurations.
- **Confidence calibration** — does the system's returned confidence score match the real success frequency (uncertainty reliability, essential in production, §29)?

**Advantages/limits.** \(T_\epsilon\) and \(N_\epsilon\) are intuitive but depend on the chosen threshold; AUC is more robust but aggregates training phases of different natures (fast transient vs. slow fine-tuning) — both metric families should be reported together.

---

## 28. Statistical Analysis

- **Mandatory replication** — every experiment (especially in cheap Phases 1-3) repeated over ≥ 5 random seeds; report both mean **and** dispersion (standard deviation, confidence intervals).
- **Significance testing** — baseline comparisons via appropriate tests (e.g. a paired Wilcoxon test rather than a simple mean delta, to account for inter-seed variance).
- **ANOVA / Sobol** — variance decomposition for factorial designs (§15).
- **Multiple-comparison correction** — whenever many hyperparameters/tasks are compared simultaneously (e.g. Bonferroni correction or False Discovery Rate) to avoid false positives.
- **Feature importance report (SHAP)** — systematic on every meta-model version, versioned alongside the corresponding model.

---

## 29. Production Architecture

The service receives:

```json
{
  "model": "...",
  "task_metadata": "...",
  "dataset_statistics": "...",
  "compute_budget": "...",
  "target_metric": "..."
}
```

and returns:

```json
{
  "recommended_initialization": "...",
  "recommended_optimizer": "...",
  "recommended_lr": 0.0007,
  "recommended_batch_size": 64,
  "recommended_scheduler": "cosine",
  "expected_convergence": { "steps": 3800, "loss_threshold": 0.1 },
  "confidence_score": 0.78
}
```

The **confidence score** is a first-order requirement: a system that doesn't know *when it doesn't know* is dangerous to integrate into a production pipeline. Recommended approach: quantile regression or meta-model ensembles (inter-model variance as an uncertainty proxy).

---

## 30. API Design

- `POST /v1/analyze-model` — introspects a supplied model (blank checkpoint or architecture definition), returns \(X_{model}\).
- `POST /v1/analyze-task` — statistics computed on a data/task sample, returns \(X_{task}\).
- `POST /v1/predict-config` — input \(X_{model}, X_{task}\) (+ budget, target metric) → recommended configuration + confidence.
- `POST /v1/probe` — launches an optional *few-step probing* run and returns a refined configuration.
- `POST /v1/feedback` — submits the real outcome of a full training run, feeds the meta-dataset (§23 feedback loop).
- `GET /v1/experiments/{id}` — consults a logged experiment.

Simple REST design in V1; gRPC conceivable in V2 if integration into low-latency training pipelines justifies it.

---

## 31. MLOps

- **Versioning**: of the meta-model (with its validation metrics), of the meta-dataset (dated snapshot), of the code (SemVer).
- **CI/CD**: regression tests on a fixed subset of synthetic tasks ("smoke benchmark") before every meta-model deployment.
- **Monitoring**: production tracking of the prediction/reality gap (model drift), alerting if confidence calibration degrades.
- **Periodic retraining**: automated pipeline triggered when the volume of new feedback exceeds a threshold (continual meta-learning, §23).
- **Reproducibility**: explicit random seeds, environment capture (library versions, hardware) for every experiment.

---

## 32. Distributed Computing

The synthetic laboratory must be able to run **thousands of short training runs in parallel** — an *embarrassingly parallel batch scheduling* problem rather than classic distributed training (a single training run across multiple GPUs).

- **Orchestration**: Kubernetes (or Ray for a lighter, ML-native option) to distribute the laboratory's runs across a pool of CPU/GPU workers.
- **Shared storage**: object storage (S3-compatible) for checkpoints and raw logs; a structured database for the Experiment Database.
- **Adaptive scheduling**: favor ASHA/Hyperband to stop uninformative synthetic tasks early and reallocate compute budget.

This component is only needed once the volume of experiments exceeds the capacity of a single machine (typically V0.3-V0.4, not for the MVP).

---

## 33. Security / Reliability

- **Run isolation** — each laboratory training run in an isolated environment (container), to prevent a numerical divergence (NaN, memory explosion) from affecting other runs.
- **Divergence detection** — automatic termination of runs that produce NaN/Inf or exceed a memory/time budget, with the failure logged as useful data (a failure is information, not just a rejection).
- **API input validation** — bounding requested compute budgets on the production side, to prevent a request from triggering disproportionate probing.
- **Traceability** — every production prediction must be linked to the exact meta-model and meta-dataset version that produced it (auditability).

---

## 34. Failure Modes

| Failure mode | Symptom | Detection | Mitigation |
|---|---|---|---|
| Numerical divergence during a laboratory run | Loss = NaN | Automated monitoring | Stop + log as an informative failure |
| Meta-model overfitting on synthetic tasks | Good synthetic test performance, poor on real data | Strict train/val/test split + external validation (Phase 4+) | Regularization, increase synthetic task diversity |
| Distribution drift in production | High confidence but degraded real results | Feedback loop (§23) + calibration monitoring | Periodic retraining, automated alerting |
| Underestimated laboratory compute cost | Budget exhausted before reaching a usable meta-dataset | Per-phase budget tracking | Prioritize Hyperband/ASHA, reduce the number of seeds in the exploratory phase |
| Expensive features (NTK, full Hessian) too costly to be useful in production | Unacceptable API latency | Per-feature latency benchmark | Only keep in production the features validated as *worth it* (§26 ablation) |

---

## 35. Research Risks

| Risk | Description | Experiment to test it |
|---|---|---|
| Optimality strongly dataset-dependent | \(H^*\) varies too much from one task to another to be generalizable | Measure the variance of \(H^*\) across *nearby* synthetic tasks (same family, neighboring parameters) |
| Poor synthetic → real transferability | The meta-model trained on synthetic data doesn't generalize | Phase 4: strict external validation, hold-out of never-seen real tasks |
| Architecture space too vast | Impossible to cover enough architectural diversity | Limit the initial scope (MLP → CNN → miniature Transformer), measure degradation per family |
| Inability to precisely predict convergence | The pre-training signal is too weak | Early feature-importance study (Q8), with a pre-defined abandonment threshold |
| Prohibitive feature cost (NTK, Hessian) | The system costs almost as much as it saves | Cost-vs-added-value benchmark per feature (ablation §26) |
| Distribution shift between research phase and production | Real tasks differ too much from the synthetic laboratory | Progressively widen the task generator's diversity |
| Meta-overfitting | The meta-model memorizes the meta-dataset's tasks rather than learning a generalizable relationship | Strict cross-validation at the *task* level (not the trial level), fully disjoint test tasks |
| Non-stationary hyperparameters | The optimal configuration changes over the course of training itself (justifies schedules) | Compare a static prediction vs. a dynamically predicted schedule |
| No universal architecture ↔ optimal-configuration relationship | H1 is simply false | This is the project's central risk — tested from Phase 1 with an explicit abandonment/pivot threshold |

**Guiding principle.** Every risk has an assigned experiment in the protocol (§24) — no risk remains "to explore later" without a concrete planned test.

---

## 36. Open Research Questions

Beyond the initial scope, leads to keep in reserve, each assessed for relevance:

| Concept | Short explanation | Link to the project | Integrate? | Proposed experiment |
|---|---|---|---|---|
| **Learned initialization** | Directly learn a function that generates the initial weights | Direct extension of §12 | Yes, V0.3+ | Compare learned init vs. µP vs. He in Phase 2-3 |
| **Learned optimizers** | Replace the update rule itself with a learned model | Orthogonal, more ambitious | Not a priority | Separate track, isolated from the project's core |
| **Neural scaling laws** | Power laws relating size/data/compute to loss | Methodological inspiration | Yes, in the background (Phase 6) | Check whether our predictions remain valid across scales |
| **Neural Tangent Kernel** | See §9 | Direct candidate feature | Yes | Compare an approximated NTK spectrum as a feature vs. without |
| **Loss landscape geometry / dynamical isometry** | Global/local properties of the loss surface | Linked to §9 (Hessian) | Yes, as a feature | Test the sharpness ↔ generalization correlation in the laboratory |
| **Spectral initialization** | Initialization calibrated on the expected activation/gradient spectrum | Extension of §12 | Yes | Compare against Xavier/He |
| **Gradient flow** | Continuous (ODE) analysis of gradient-descent dynamics | Theoretical foundation | Background only | — |
| **Fisher information** | See §9 | Candidate feature (link to K-FAC) | Yes, V0.4+ | Compare cost/value vs. approximated Hessian |
| **Grokking** | Late, sudden generalization after a long apparent-memorization phase | Interesting edge case to test the robustness of \(T_\epsilon\) predictions | Yes, as a case study | Synthetic tasks known to produce grokking (modular arithmetic) |
| **Lottery ticket hypothesis** | Trainable sub-networks isolable right at initialization | Indirect link to "initialization quality" | Exploratory | Test whether a "good" sub-network's features also predict a good \(H^*\) |
| **Pruning / distillation** | Model reduction during or after training | Peripheral | Not a priority | — |
| **Curriculum learning** | See source doc #1 | Already in the data taxonomy (§11) | Yes | Compare naive ordering vs. curriculum on synthetic tasks with parametric difficulty |
| **Active learning / data selection / dataset valuation** | Select which data to train on first/with priority | Link to sample efficiency (§17) | Yes, V0.5+ (real data) | Compare random selection vs. meta-model-guided selection |
| **Synthetic data generation (beyond the laboratory)** | Generate synthetic training data for the target task itself (not just for meta-research) | Distinct from the Synthetic Learning Laboratory | Separate track | — |
| **Neural Architecture Search** | Automated architecture search | Orthogonal (we assume the architecture is given) | No — explicitly out of scope | — |
| **Learned HPO (meta-learning the search algorithm itself)** | Going one step further than our meta-predictor | Long-term vision | Exploratory research, V2.0 | — |

---

## 37. Scientific Positioning

Relevant research fields:

- **AutoML** (Automated Machine Learning) — the general framework.
- **Hyperparameter Optimization** — the historically closest field, but our approach differs by predicting *a priori* rather than searching.
- **Meta-Learning** — the methodological core (learning across tasks).
- **Optimization Theory** — foundations (NTK, Hessian, µP).
- **Training Dynamics** — the central object of empirical study.
- **Neural Architecture Search** — a neighbor, explicitly out of initial scope.
- **Efficient Deep Learning** — motivation (reducing cost/data/energy).
- **Sample-Efficient Learning** — one of the two main metric axes (with speed).
- **AI Systems** — the project's engineering/infrastructure dimension.

**Potential contribution.** At the intersection of Training Dynamics (usually studied descriptively/post-hoc) and Meta-Learning applied to HPO (usually treated as a black box): a system that explicitly links **pre-training structural properties** to **dynamics predictions**, validated through a **causal** methodology rather than a purely correlational one.

---

## 38. Roadmap

| Version | Content | Experiments | Success criteria | Difficulty | Main risks |
|---|---|---|---|---|---|
| **MVP** | MLP laboratory + 5 hyperparameters + reference Bayesian search | Partial Phase 1 | A coherent, usable meta-dataset of ≥ 1000 trials | Low-Medium | Underestimated compute cost |
| **V0.1** | Full Synthetic Learning Laboratory (parametric generative functions, noise/complexity/redundancy control) | Generation of ≥ 100 tasks | Sufficient task diversity (verified via task-feature clustering) | Medium | Insufficiently diverse generator |
| **V0.2** | Hyperparameter predictor (gradient boosting) | Full Phase 1 | Beats the default baseline on ≥ 60% of test tasks | Medium | H1 insufficiently verified |
| **V0.3** | Initialization predictor + curvature features (Hutchinson, power iteration) | Partial §26 ablation | Measurable gain specifically attributable to the predicted initialization | Medium-High | Compute cost of curvature features |
| **V0.4** | CNN/miniature Transformer extension | Phase 2-3 | Meta-model transfers with "acceptable" degradation (threshold defined a priori) | High | Architecture space too broad |
| **V0.5** | Real datasets | Phase 4 | \(N_{ours} \le N_{baseline}\), \(T_{ours} \le T_{baseline}\) at equal performance | High | Poor synthetic→real transferability (central risk) |
| **V1.0** | Production API (§29-30) + calibrated confidence score | Calibration validation | Confidence correlated with real success frequency | High | Latency, real-world reliability |
| **V2.0** | Large-scale meta-learning (GNN over architectures, continuous feedback loop) | Phase 5-6 | Measurable continuous improvement from production feedback | Very high | Meta-overfitting, drift |

---

## 39. MVP — Details

The MVP must remain **deliberately small**:

```
MLP
  ↓
Synthetic regression tasks (3-5 generative functions)
  ↓
5 hyperparameters (learning_rate, batch_size, optimizer, weight_decay, initialization)
  ↓
~1000 configurations tested (reference Bayesian search, via Optuna)
  ↓
Convergence measurement (steps_to_threshold)
  ↓
Meta-dataset construction
  ↓
First predictive model (gradient boosting)
```

**Expected MVP output:** a quantified answer, even a negative one, to the first hypothesis (H1) on a restricted scope — not a usable product.

---

## 40. Future Extensions

- Extension to additional architecture families (RNN/SSM, GNN, multimodal models).
- Prediction of LLM *fine-tuning* configurations (LoRA/PEFT — rank, adapter learning rate) as a high-value practical use case.
- Integration of an adaptive probing budget (the system itself decides whether it needs more signal before answering, rather than a fixed budget).
- A "convergence profile" marketplace — a library of validated configurations per task family, fed by the community (open-source track, §43).

---

## 41. Potential Scientific Contributions

- An open-source **Synthetic Learning Laboratory**, reusable independently of the central hypothesis's success (a methodological contribution in its own right).
- A public **Experiment/Meta-Database** of controlled training dynamics, useful to the training-dynamics community beyond PreTrainOpt.
- A rigorous (causal, not merely correlational) empirical evaluation of the relative importance of pre-training factors on convergence — publishable independently of the final product's success.
- If H1-H3 are validated: a paper demonstrating that a meta-predictor beats standard HPO baselines at a far lower compute budget.

---

## 42. Potential Industrial Applications

- Reduced tuning cost for ML teams without deep HPO expertise (democratization).
- Accelerated LLM fine-tuning in production (a high-value use case, with high experimentation cost for practitioners).
- Upstream integration into existing MLOps platforms (Kubeflow, SageMaker, Vertex AI) as a recommendation step before launching a training job.
- Reduced energy footprint of model training (a concrete ESG argument if \(E_\epsilon\) is indeed reduced).

---

## 43. Open-source Strategy

- The **Synthetic Learning Laboratory** (task generator) and the **Experiment Database** published as open source starting at V0.1 — building scientific credibility and attracting external contributions (new task families, new architectures).
- The **trained meta-model** and the **prediction API** can remain proprietary (product differentiation) even if the laboratory's code is open — a classic "open-core" model.
- Publication of a paper (workshop, then conference) as soon as Phase 1-2 produce a solid result, to establish scientific legitimacy before the product phase.

---

## 44. Product Strategy

- **Research phase (V0.x)**: no product, publication and scientific credibility as the goal.
- **Early access phase (V1.0)**: API restricted to a few pilot users (internal ML teams or partners), to validate H3 (the cost/benefit ratio) under real conditions.
- **Product phase (V1.0+)**: a configuration-recommendation API SaaS, integrable into existing training pipelines; pricing indexed to the compute saved (a "value-based pricing" model consistent with the value proposition).
- **Enterprise infrastructure phase (V2.0)**: on-premise deployment for organizations whose confidentiality constraints prevent using an external API (particularly relevant for large proprietary models).

---

## 45. Final Research Thesis

> **A significant part of a model's future learning dynamics is determined by properties observable before full training — architecture, task statistics, initialization statistics — and this relationship, learned on a laboratory of controlled synthetic tasks, transfers to real models and data with a net gain (measured in steps, samples, and compute) over classic hyperparameter search methods.**

This thesis is **not** presented as established. It is the conclusion that the experimental protocol (§24) is built to confirm, qualify, or refute — with, in all three cases, a scientific contribution and a technical foundation (laboratory, experiment database) that remain useful.

---

## Appendix A — Project Identity

**Proposed names** (working as an open-source project, research framework, SaaS product, and enterprise infrastructure):

1. **PreTrainOpt** — descriptive, direct, easy to index technically.
2. **Vantage** — evokes the vantage point taken *before* committing to training.
3. **Primer** — in the sense of "priming" a training run with a good starting configuration.
4. **Convergo** — directly evokes convergence, international-sounding.
5. **Nascent** — the model's state before training, scientific connotation.
6. **Priora** — from "a priori", predictive/Bayesian connotation.

**Recommendation:** **PreTrainOpt** for the technical/repo name (immediate clarity for an ML audience), with **Vantage** or **Priora** held in reserve for a more memorable future commercial product name.

**Tagline:** *"Know your training before you run it."*

**Mission:** Reduce the data, compute, and time cost of neural network training by replacing hyperparameter search with a prediction grounded in the properties of the model and the task.

**Vision:** A future where launching a training run starts with a reliable, explained recommendation, not a blind trial.

**Problem:** Hyperparameter tuning consumes a significant — and largely avoidable — share of the compute budget and engineering time in machine learning.

**Solution:** A meta-learning system, trained on a laboratory of controlled synthetic tasks, that predicts a near-optimal training configuration before, or with a minimum of, real compute.

**Value proposition:** Less data, less compute, less engineering time — for equal or better performance, with an explicit confidence score rather than a blind promise.

---

## Appendix B — Final Recommendation

### Recommended architecture for the first prototype

- **Scope**: MLP only, synthetic regression tasks (3-5 generative functions of increasing complexity).
- **Hyperparameters covered**: learning rate, batch size, optimizer (Adam/AdamW/SGD), weight decay, initialization method (Xavier/He/orthogonal) — deliberately limited to 5 to remain interpretable.
- **Ground-truth generation**: Optuna (TPE) as the reference Bayesian search, not Vizier directly (simpler to integrate in Rust/Python for a prototype).
- **Meta-model**: gradient boosting (LightGBM), tabular features only in V1 (no NTK/Hessian at the MVP stage — too costly for the first iteration, to be introduced in V0.3 once H1 is partially validated).
- **Infrastructure**: local/single-machine execution for the MVP, no Kubernetes before the volume of experiments genuinely justifies it.

### Priority experiments (in order)

1. **Calibration experiment** — for a fixed synthetic task, sweep the learning rate alone (all else equal, 5 seeds) and verify that a U-shaped curve consistent with theory (§9) is recovered. *Goal: validate the instrumentation before anything else.*
2. **LR × batch size factorial experiment** — on 3-4 synthetic tasks of increasing complexity, to test the known LR↔batch interaction (empirical linear rule) and calibrate the factorial methodology (§15) on a case where the expected answer is already known.
3. **First test of H1** — train the meta-model on 80% of the generated synthetic tasks, evaluate on the remaining 20% (never-seen tasks): does the meta-model beat the default configuration? This is the experiment that decides whether the project continues as-is or pivots.

### Three hypotheses to test first

1. **H1** — pre-training features (model + task) carry an exploitable signal about \(H^*\) — tested by experiment #3 above.
2. **H4** — there is no universal configuration — tested by measuring the variance of \(H^*\) found by Optuna across synthetic tasks (if the variance is low, H4 is refuted and the problem is simpler than expected; if it is high, this confirms the need for a conditional predictor).
3. **H5** — diminishing returns of probing — tested by comparing, on the best model resulting from the MVP, prediction accuracy at 0%, 0.1%, and 1% of probing budget.

**Do not start coding the production API, the dashboard, or the distributed architecture before H1 (experiment #3) has been settled.** The rest of this document (§18 to §45) is the trajectory *if* the signal exists — not a list of tasks to execute in parallel from day one.
