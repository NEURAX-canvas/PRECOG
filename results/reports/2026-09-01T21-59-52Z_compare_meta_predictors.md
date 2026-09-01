# Meta-Predictor Comparison (4 designs, locked test split)

_Generated 2026-09-01T21-59-52Z (UTC)_

## Method

Four Meta-Predictor designs (docs.md §9.7, §19 ablation methodology), all
trained on the identical TRAIN split (792 rows,
252 tasks) and evaluated exactly once on the
identical locked TEST split (180 rows, 60
tasks): `full_rf` (all features), `reduced_rf` (only §21-validated zero-cost
proxies), `log_rf` (all features, log1p target), `knn` (Meta-Knowledge Base
neighbor vote alone, no learned model).

Baselines: universal-config = 38% (mean_regret=+22.2 steps),
random = 33% (mean_regret=+43.2 steps).

Alongside top-1 accuracy, this run also reports **regret** = steps(predicted
init) - steps(true best init) per test task, and its task-scale-normalized
form relative_regret = regret / steps(true best init) -- a wrong top-1 call
that costs 5 extra steps and one that costs 700 extra steps are both
"misses" under accuracy alone, but very different practical outcomes.

## Results

| candidate | accuracy | mean confidence | calibration gap | mean regret (steps) | mean relative regret |
|---|---:|---:|---:|---:|---:|
| reduced_rf | 47% (28/60) | 0.32 | -0.15 | +18.2 | +25% |
| zc_jacobcov | 47% (28/60) | nan | +nan | +14.6 | +18% |
| zc_gradnormvar | 38% (23/60) | nan | +nan | +41.1 | +23% |
| log_rf | 35% (21/60) | 0.59 | +0.24 | +37.9 | +24% |
| knn | 35% (21/60) | 0.54 | +0.19 | +43.2 | +31% |
| full_rf | 33% (20/60) | 0.59 | +0.26 | +40.0 | +22% |

## Winner: `reduced_rf`

Selected by accuracy first, then by the smallest confidence/accuracy
calibration gap (docs.md §23 "poorly calibrated uncertainty" risk) as
tiebreaker. Beats the
universal-config baseline on accuracy (38%), and
beats it on regret
(+22.2 mean steps).

| seed | true best init | predicted | confidence | hit | regret (steps) |
|---|---|---|---:|---|---:|
| 100 | xavier | orthogonal | 0.42 | False | 10 |
| 107 | orthogonal | xavier | 0.50 | False | 12 |
| 120 | orthogonal | xavier | 0.43 | False | 24 |
| 131 | xavier | xavier | 0.13 | True | 0 |
| 132 | xavier | orthogonal | 0.47 | False | 0 |
| 137 | orthogonal | orthogonal | 0.20 | True | 0 |
| 141 | orthogonal | xavier | 0.48 | False | 2 |
| 146 | orthogonal | xavier | 0.39 | False | 21 |
| 147 | xavier | xavier | 0.50 | True | 0 |
| 148 | he | orthogonal | 0.27 | False | 1 |
| 150 | he | he | 0.25 | True | 0 |
| 151 | orthogonal | orthogonal | 0.00 | True | 0 |
| 155 | orthogonal | orthogonal | 0.52 | True | 0 |
| 171 | orthogonal | xavier | 0.45 | False | 96 |
| 172 | he | xavier | 0.00 | False | 10 |
| 175 | orthogonal | xavier | 0.28 | False | 3 |
| 197 | xavier | xavier | 0.53 | True | 0 |
| 204 | xavier | xavier | 0.60 | True | 0 |
| 211 | orthogonal | xavier | 0.33 | False | 1 |
| 213 | xavier | he | 0.48 | False | 147 |
| 222 | orthogonal | he | 0.00 | False | 86 |
| 224 | xavier | he | 0.00 | False | 149 |
| 228 | xavier | xavier | 0.27 | True | 0 |
| 232 | he | xavier | 0.21 | False | 8 |
| 233 | orthogonal | orthogonal | 0.40 | True | 0 |
| 244 | xavier | orthogonal | 0.20 | False | 1 |
| 249 | he | he | 0.39 | True | 0 |
| 254 | orthogonal | orthogonal | 0.59 | True | 0 |
| 255 | orthogonal | he | 0.00 | False | 51 |
| 258 | xavier | he | 0.44 | False | 14 |
| 261 | xavier | xavier | 0.33 | True | 0 |
| 263 | orthogonal | orthogonal | 0.50 | True | 0 |
| 266 | orthogonal | orthogonal | 0.16 | True | 0 |
| 269 | orthogonal | orthogonal | 0.15 | True | 0 |
| 270 | he | he | 0.30 | True | 0 |
| 281 | he | xavier | 0.08 | False | 9 |
| 283 | orthogonal | orthogonal | 0.54 | True | 0 |
| 297 | orthogonal | orthogonal | 0.49 | True | 0 |
| 304 | orthogonal | xavier | 0.18 | False | 9 |
| 307 | orthogonal | he | 0.34 | False | 11 |
| 315 | xavier | xavier | 0.22 | True | 0 |
| 322 | orthogonal | orthogonal | 0.00 | True | 0 |
| 326 | xavier | orthogonal | 0.00 | False | 4 |
| 329 | xavier | orthogonal | 0.52 | False | 9 |
| 341 | xavier | he | 0.50 | False | 8 |
| 344 | orthogonal | xavier | 0.52 | False | 131 |
| 348 | he | he | 0.06 | True | 0 |
| 350 | orthogonal | xavier | 0.19 | False | 218 |
| 352 | xavier | he | 0.00 | False | 10 |
| 358 | he | orthogonal | 0.45 | False | 8 |
| 360 | he | xavier | 0.37 | False | 5 |
| 361 | orthogonal | orthogonal | 0.23 | True | 0 |
| 366 | xavier | he | 0.40 | False | 32 |
| 372 | xavier | orthogonal | 0.23 | False | 3 |
| 378 | orthogonal | orthogonal | 0.27 | True | 0 |
| 380 | xavier | orthogonal | 0.60 | False | 1 |
| 382 | xavier | xavier | 0.15 | True | 0 |
| 386 | xavier | xavier | 0.48 | True | 0 |
| 390 | xavier | xavier | 0.49 | True | 0 |
| 398 | orthogonal | orthogonal | 0.53 | True | 0 |

## Verdict

H1 supported over H4 at this scale: the best Meta-Predictor design conditions on task/model features and beats a single universal init choice.

Regret analysis agrees with accuracy: the winner is also the practically cheaper choice on average, not just the more often-correct one.
