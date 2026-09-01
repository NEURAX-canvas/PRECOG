# Gate 3 — Search Engine Compute Reduction

_Generated 2026-09-01T12-58-15Z (UTC)_

## Method

Search Engine (docs.md §9.8): Optuna TPE warm-started from the
Meta-Predictor's (§9.7) recommended init_method ("informed") vs an
identical cold search with no warm start, 15 trials each, same RNG
seed, on all 16 locked TEST-split tasks. Target: reach
steps_to_threshold <= 150.0.

## Results

| seed | informed trials-to-target | cold trials-to-target | informed best steps | cold best steps |
|---|---:|---:|---:|---:|
| 105 | 11 | 11 | 82 | 124 |
| 112 | 1 | 1 | 28 | 28 |
| 117 | None | None | 155 | 155 |
| 127 | 1 | 1 | 31 | 22 |
| 133 | 1 | 1 | 23 | 27 |
| 136 | 1 | 1 | 21 | 21 |
| 138 | None | None | 166 | 166 |
| 145 | 1 | 1 | 57 | 46 |
| 149 | 2 | 1 | 54 | 54 |
| 151 | 1 | 1 | 40 | 45 |
| 153 | None | None | 183 | 183 |
| 161 | 5 | 4 | 95 | 95 |
| 162 | 13 | 12 | 103 | 103 |
| 164 | 11 | None | 114 | 229 |
| 165 | 11 | 12 | 130 | 93 |
| 167 | None | None | 182 | 182 |

Both reached target: 11/16 (mean trial reduction: -11%)
Informed reached but cold didn't: 1/16
Neither reached: 4/16

## Verdict

Gate 3 (docs.md §17, target >= 50% compute reduction): **NOT YET MET** (-11%)
