# Meta-Predictor Comparison (4 designs, locked test split)

_Generated 2026-09-01T22-10-28Z (UTC)_

## Method

Four Meta-Predictor designs (docs.md §9.7, §19 ablation methodology), all
trained on the identical TRAIN split (828 rows,
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
| full_rf | 47% (28/60) | 0.59 | +0.12 | +35.7 | +20% |
| reduced_rf | 47% (28/60) | 0.30 | -0.16 | +31.7 | +25% |
| zc_jacobcov | 47% (28/60) | nan | +nan | +14.6 | +18% |
| gp_reduced | 42% (25/60) | 0.22 | -0.20 | +36.5 | +24% |
| log_rf | 40% (24/60) | 0.57 | +0.17 | +41.5 | +22% |
| zc_gradnormvar | 38% (23/60) | nan | +nan | +41.1 | +23% |
| knn | 35% (21/60) | 0.54 | +0.19 | +45.5 | +30% |

## Winner: `zc_jacobcov`

Selected by accuracy first, then by the lowest mean regret (the
practically meaningful tiebreaker), then by the smallest confidence/accuracy
calibration gap (docs.md §23 "poorly calibrated uncertainty" risk) as a
last resort. Beats the
universal-config baseline on accuracy (38%), and
beats it on regret
(+22.2 mean steps).

| seed | true best init | predicted | confidence | hit | regret (steps) |
|---|---|---|---:|---|---:|
| 100 | xavier | orthogonal | nan | False | 10 |
| 107 | orthogonal | orthogonal | nan | True | 0 |
| 120 | orthogonal | xavier | nan | False | 24 |
| 131 | xavier | xavier | nan | True | 0 |
| 132 | xavier | xavier | nan | True | 0 |
| 137 | orthogonal | xavier | nan | False | 7 |
| 141 | orthogonal | xavier | nan | False | 2 |
| 146 | orthogonal | orthogonal | nan | True | 0 |
| 147 | xavier | xavier | nan | True | 0 |
| 148 | he | orthogonal | nan | False | 1 |
| 150 | he | xavier | nan | False | 4 |
| 151 | orthogonal | orthogonal | nan | True | 0 |
| 155 | orthogonal | xavier | nan | False | 54 |
| 171 | orthogonal | orthogonal | nan | True | 0 |
| 172 | he | xavier | nan | False | 10 |
| 175 | orthogonal | xavier | nan | False | 3 |
| 197 | xavier | xavier | nan | True | 0 |
| 204 | xavier | xavier | nan | True | 0 |
| 211 | orthogonal | xavier | nan | False | 1 |
| 213 | xavier | xavier | nan | True | 0 |
| 222 | orthogonal | orthogonal | nan | True | 0 |
| 224 | xavier | xavier | nan | True | 0 |
| 228 | xavier | xavier | nan | True | 0 |
| 232 | he | xavier | nan | False | 8 |
| 233 | orthogonal | xavier | nan | False | 71 |
| 244 | xavier | xavier | nan | True | 0 |
| 249 | he | orthogonal | nan | False | 55 |
| 254 | orthogonal | orthogonal | nan | True | 0 |
| 255 | orthogonal | orthogonal | nan | True | 0 |
| 258 | xavier | orthogonal | nan | False | 7 |
| 261 | xavier | xavier | nan | True | 0 |
| 263 | orthogonal | xavier | nan | False | 66 |
| 266 | orthogonal | xavier | nan | False | 26 |
| 269 | orthogonal | xavier | nan | False | 9 |
| 270 | he | xavier | nan | False | 8 |
| 281 | he | xavier | nan | False | 9 |
| 283 | orthogonal | orthogonal | nan | True | 0 |
| 297 | orthogonal | xavier | nan | False | 46 |
| 304 | orthogonal | orthogonal | nan | True | 0 |
| 307 | orthogonal | xavier | nan | False | 8 |
| 315 | xavier | xavier | nan | True | 0 |
| 322 | orthogonal | xavier | nan | False | 1 |
| 326 | xavier | xavier | nan | True | 0 |
| 329 | xavier | xavier | nan | True | 0 |
| 341 | xavier | xavier | nan | True | 0 |
| 344 | orthogonal | xavier | nan | False | 131 |
| 348 | he | orthogonal | nan | False | 18 |
| 350 | orthogonal | xavier | nan | False | 218 |
| 352 | xavier | xavier | nan | True | 0 |
| 358 | he | orthogonal | nan | False | 8 |
| 360 | he | xavier | nan | False | 5 |
| 361 | orthogonal | xavier | nan | False | 6 |
| 366 | xavier | orthogonal | nan | False | 7 |
| 372 | xavier | orthogonal | nan | False | 3 |
| 378 | orthogonal | orthogonal | nan | True | 0 |
| 380 | xavier | xavier | nan | True | 0 |
| 382 | xavier | xavier | nan | True | 0 |
| 386 | xavier | orthogonal | nan | False | 0 |
| 390 | xavier | xavier | nan | True | 0 |
| 398 | orthogonal | xavier | nan | False | 48 |

## Verdict

H1 supported over H4 at this scale: the best Meta-Predictor design conditions on task/model features and beats a single universal init choice.

Regret analysis agrees with accuracy: the winner is also the practically cheaper choice on average, not just the more often-correct one.
