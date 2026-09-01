# OOD Generalization: Family Holdout (docs.md §22)

_Generated 2026-09-01T22-22-00Z (UTC)_

## Method

docs.md §22/§27: does the Meta-Predictor (and the training-free zero-cost
heuristic) generalize to a genuinely unseen task *family*, or does it just
memorize which init wins for each of the 3 synthetic families this project
uses (linear, nonlinear_interaction, nonlinear_product)? Every prior
evaluation split tasks randomly *within* the same pool, where all 3
families appear on both sides -- that tests interpolation only.

3-fold family holdout: each fold trains on the other two families' tasks
(pooling both original TRAIN and TEST splits as raw material -- a different
question from the original locked-split evaluation, so this does not
corrupt it) and tests only on the held-out family's tasks.

## Results

| held-out family | n tasks | reduced_rf acc | reduced_rf regret | zc_jacobcov acc | zc_jacobcov regret |
|---|---:|---:|---:|---:|---:|
| linear | 104 | 37% | +7.6 | 42% | +3.8 |
| nonlinear_interaction | 104 | 41% | +18.2 | 44% | +23.2 |
| nonlinear_product | 104 | 32% | +73.6 | 49% | +31.7 |

## Summary: OOD vs in-distribution (ID)

| candidate | OOD accuracy | OOD mean regret | ID accuracy | ID mean regret | regret collapse (>1.5x)? |
|---|---:|---:|---:|---:|---|
| reduced_rf | 37% | +33.1 | 47% | +32.9 | no |
| zc_jacobcov | 45% | +19.6 | 47% | +14.6 | no |

## Verdict

Neither candidate's regret collapses on held-out families (within 1.5x of in-distribution) -- weak evidence that the signal generalizes past the 3 specific synthetic families in the meta-dataset, though 3 folds is a small, low-power test and the families themselves are close cousins (all synthetic MLP regression tasks), so this should not be read as evidence of general trainability signal beyond this task universe.
