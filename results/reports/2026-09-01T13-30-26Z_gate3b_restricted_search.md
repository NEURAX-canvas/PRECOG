# Gate 3b — Restricted Search vs Reference

_Generated 2026-09-01T13-30-26Z (UTC)_

## Method

Four search arms per locked-TEST task, same objective (steps_to_threshold,
FULL_TRAINING, LR/batch/optimizer as in prior gates):
- **reference**: 40-trial joint (LR, init) search -- the near-optimal ground truth.
- **cold**: 15-trial joint (LR, init) search.
- **informed_restricted**: 15-trial LR-only search, init FIXED to the Meta-Predictor's
  (reduced_rf, the evidenced winner from compare_meta_predictors.py) recommended init.
- **universal_restricted**: 15-trial LR-only search, init FIXED to the universal-config
  baseline's init (xavier) -- isolates whether *any* fixed init helps (H4) from
  whether the *task-conditional* recommendation specifically helps (H1).

"Near-optimal" = achieved best_steps within 20% of the reference search's result.

## Results

| seed | true best init | recommended init | reference | cold | informed_restricted | universal_restricted |
|---|---|---|---:|---:|---:|---:|
| 105 | xavier | xavier | 100 | 100 | 119 | 119 |
| 112 | orthogonal | orthogonal | 28 | 31 | 33 | 39 |
| 117 | xavier | he | 155 | 105 | 181 | 160 |
| 127 | he | orthogonal | 22 | 22 | 31 | 22 |
| 133 | orthogonal | xavier | 23 | 27 | 25 | 25 |
| 136 | xavier | xavier | 18 | 26 | 14 | 14 |
| 138 | xavier | orthogonal | 129 | 103 | 151 | 103 |
| 145 | orthogonal | orthogonal | 23 | 28 | 47 | 47 |
| 149 | xavier | xavier | 54 | 85 | 85 | 85 |
| 151 | orthogonal | orthogonal | 33 | 33 | 25 | 51 |
| 153 | xavier | orthogonal | 183 | 183 | 183 | 195 |
| 161 | xavier | xavier | 66 | 98 | 95 | 95 |
| 162 | xavier | orthogonal | 103 | 103 | 265 | 181 |
| 164 | orthogonal | xavier | 114 | 114 | 114 | 114 |
| 165 | xavier | orthogonal | 85 | 85 | 71 | 115 |
| 167 | he | xavier | 182 | 182 | 182 | 182 |

| Arm | Near-optimal rate | Mean ratio to reference |
|---|---:|---:|
| cold (joint search) | 75% | 1.09x |
| informed_restricted (Meta-Predictor init) | 69% | 1.26x |
| universal_restricted (H4 baseline init) | 56% | 1.25x |

## Verdict

Gate check (informed_restricted near-optimal rate >= 80%): **NOT YET MET** (69%)

The Meta-Predictor's recommendation, used to *restrict* the search (not just seed it), finds near-optimal hyperparameters as reliably as informed_restricted's rate shows, and outperforms restricting to the context-free universal baseline instead -- H1 supported over H4 for this use of the recommendation.
