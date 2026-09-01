# Meta-Predictor Comparison (4 designs, locked test split)

_Generated 2026-09-01T14-24-40Z (UTC)_

## Method

Four Meta-Predictor designs (docs.md §9.7, §19 ablation methodology), all
trained on the identical TRAIN split (756 rows,
252 tasks) and evaluated exactly once on the
identical locked TEST split (180 rows, 60
tasks): `full_rf` (all features), `reduced_rf` (only §21-validated zero-cost
proxies), `log_rf` (all features, log1p target), `knn` (Meta-Knowledge Base
neighbor vote alone, no learned model).

Baselines: universal-config = 38%, random = 33%.

## Results

| candidate | accuracy | mean confidence | calibration gap |
|---|---:|---:|---:|
| reduced_rf | 48% (29/60) | 0.30 | -0.18 |
| zc_jacobcov | 47% (28/60) | nan | +nan |
| full_rf | 38% (23/60) | 0.59 | +0.20 |
| log_rf | 38% (23/60) | 0.56 | +0.18 |
| knn | 38% (23/60) | 0.54 | +0.16 |
| zc_gradnormvar | 38% (23/60) | nan | +nan |

## Winner: `reduced_rf`

Selected by accuracy first, then by the smallest confidence/accuracy
calibration gap (docs.md §23 "poorly calibrated uncertainty" risk) as
tiebreaker. Beats the
universal-config baseline (38%).

| seed | true best init | predicted | confidence | hit |
|---|---|---|---:|---|
| 100 | xavier | orthogonal | 0.43 | False |
| 107 | orthogonal | xavier | 0.48 | False |
| 120 | orthogonal | xavier | 0.43 | False |
| 131 | xavier | xavier | 0.16 | True |
| 132 | xavier | orthogonal | 0.44 | False |
| 137 | orthogonal | orthogonal | 0.17 | True |
| 141 | orthogonal | xavier | 0.49 | False |
| 146 | orthogonal | xavier | 0.39 | False |
| 147 | xavier | he | 0.55 | False |
| 148 | he | orthogonal | 0.27 | False |
| 150 | he | he | 0.25 | True |
| 151 | orthogonal | orthogonal | 0.00 | True |
| 155 | orthogonal | orthogonal | 0.54 | True |
| 171 | orthogonal | xavier | 0.50 | False |
| 172 | he | xavier | 0.01 | False |
| 175 | orthogonal | xavier | 0.25 | False |
| 197 | xavier | xavier | 0.47 | True |
| 204 | xavier | xavier | 0.58 | True |
| 211 | orthogonal | xavier | 0.33 | False |
| 213 | xavier | he | 0.46 | False |
| 222 | orthogonal | he | 0.01 | False |
| 224 | xavier | orthogonal | 0.06 | False |
| 228 | xavier | xavier | 0.19 | True |
| 232 | he | xavier | 0.22 | False |
| 233 | orthogonal | orthogonal | 0.00 | True |
| 244 | xavier | orthogonal | 0.00 | False |
| 249 | he | he | 0.25 | True |
| 254 | orthogonal | orthogonal | 0.60 | True |
| 255 | orthogonal | he | 0.00 | False |
| 258 | xavier | xavier | 0.32 | True |
| 261 | xavier | xavier | 0.37 | True |
| 263 | orthogonal | orthogonal | 0.49 | True |
| 266 | orthogonal | orthogonal | 0.14 | True |
| 269 | orthogonal | orthogonal | 0.00 | True |
| 270 | he | he | 0.33 | True |
| 281 | he | xavier | 0.11 | False |
| 283 | orthogonal | orthogonal | 0.58 | True |
| 297 | orthogonal | orthogonal | 0.42 | True |
| 304 | orthogonal | xavier | 0.20 | False |
| 307 | orthogonal | he | 0.38 | False |
| 315 | xavier | xavier | 0.24 | True |
| 322 | orthogonal | orthogonal | 0.00 | True |
| 326 | xavier | orthogonal | 0.00 | False |
| 329 | xavier | orthogonal | 0.56 | False |
| 341 | xavier | he | 0.48 | False |
| 344 | orthogonal | xavier | 0.57 | False |
| 348 | he | he | 0.07 | True |
| 350 | orthogonal | xavier | 0.12 | False |
| 352 | xavier | he | 0.02 | False |
| 358 | he | orthogonal | 0.51 | False |
| 360 | he | xavier | 0.42 | False |
| 361 | orthogonal | orthogonal | 0.21 | True |
| 366 | xavier | he | 0.41 | False |
| 372 | xavier | orthogonal | 0.23 | False |
| 378 | orthogonal | orthogonal | 0.29 | True |
| 380 | xavier | xavier | 0.50 | True |
| 382 | xavier | xavier | 0.22 | True |
| 386 | xavier | xavier | 0.46 | True |
| 390 | xavier | xavier | 0.46 | True |
| 398 | orthogonal | orthogonal | 0.50 | True |

## Verdict

H1 supported over H4 at this scale: the best Meta-Predictor design conditions on task/model features and beats a single universal init choice.
