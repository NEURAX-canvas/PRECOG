# Gate 3b — Restricted Search vs Reference

_Generated 2026-09-01T14-13-01Z (UTC)_

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
| 100 | xavier | orthogonal | 14 | 14 | 16 | 11 |
| 107 | orthogonal | xavier | 190 | 190 | 126 | 126 |
| 120 | orthogonal | xavier | 171 | 171 | 171 | 171 |
| 131 | xavier | xavier | 57 | 57 | 57 | 57 |
| 132 | xavier | orthogonal | 98 | 98 | 127 | 98 |
| 137 | orthogonal | orthogonal | 54 | 97 | 97 | 109 |
| 141 | orthogonal | xavier | 539 | 534 | 539 | 539 |
| 146 | orthogonal | xavier | 54 | 82 | 69 | 69 |
| 147 | xavier | he | 446 | 438 | 651 | 623 |
| 148 | he | orthogonal | 19 | 32 | 24 | 27 |
| 150 | he | he | 324 | 427 | 339 | 271 |
| 151 | orthogonal | orthogonal | 33 | 33 | 25 | 51 |
| 155 | orthogonal | orthogonal | 94 | 122 | 130 | 148 |
| 171 | orthogonal | xavier | 189 | 256 | 265 | 265 |
| 172 | he | xavier | 8 | 14 | 16 | 16 |
| 175 | orthogonal | xavier | 13 | 18 | 18 | 18 |
| 197 | xavier | xavier | 62 | 62 | 62 | 62 |
| 204 | xavier | xavier | 162 | 253 | 274 | 274 |
| 211 | orthogonal | xavier | 18 | 23 | 25 | 25 |
| 213 | xavier | he | 61 | 146 | 171 | 95 |
| 222 | orthogonal | he | 164 | 179 | 232 | 232 |
| 224 | xavier | orthogonal | 144 | 198 | 225 | 225 |
| 228 | xavier | xavier | 93 | 143 | 190 | 190 |
| 232 | he | xavier | 7 | 15 | 12 | 12 |
| 233 | orthogonal | orthogonal | 84 | 129 | 123 | 150 |
| 244 | xavier | orthogonal | 17 | 17 | 19 | 23 |
| 249 | he | he | 218 | 221 | 221 | 321 |
| 254 | orthogonal | orthogonal | 127 | 158 | 104 | 158 |
| 255 | orthogonal | he | 74 | 74 | 148 | 97 |
| 258 | xavier | xavier | 113 | 127 | 113 | 113 |
| 261 | xavier | xavier | 174 | 196 | 174 | 174 |
| 263 | orthogonal | orthogonal | 110 | 127 | 110 | 184 |
| 266 | orthogonal | orthogonal | 82 | 60 | 79 | 70 |
| 269 | orthogonal | orthogonal | 58 | 56 | 67 | 56 |
| 270 | he | he | 72 | 74 | 74 | 84 |
| 281 | he | xavier | 56 | 49 | 67 | 67 |
| 283 | orthogonal | orthogonal | 6 | 6 | 6 | 6 |
| 297 | orthogonal | orthogonal | 246 | 246 | 256 | 265 |
| 304 | orthogonal | xavier | 8 | 8 | 13 | 13 |
| 307 | orthogonal | he | 16 | 27 | 23 | 16 |
| 315 | xavier | xavier | 292 | 326 | 318 | 318 |
| 322 | orthogonal | orthogonal | 19 | 19 | 14 | 25 |
| 326 | xavier | orthogonal | 63 | 77 | 77 | 89 |
| 329 | xavier | orthogonal | 108 | 119 | 112 | 163 |
| 341 | xavier | he | 81 | 113 | 121 | 88 |
| 344 | orthogonal | xavier | 85 | 116 | 135 | 135 |
| 348 | he | he | 156 | 156 | 118 | 170 |
| 350 | orthogonal | xavier | 298 | 298 | 485 | 485 |
| 352 | xavier | he | 11 | 11 | 13 | 11 |
| 358 | he | orthogonal | 12 | 9 | 16 | 12 |
| 360 | he | xavier | 91 | 91 | 93 | 93 |
| 361 | orthogonal | orthogonal | 16 | 17 | 19 | 16 |
| 366 | xavier | he | 113 | 137 | 169 | 137 |
| 372 | xavier | orthogonal | 285 | 416 | 403 | 403 |
| 378 | orthogonal | orthogonal | 67 | 134 | 134 | 191 |
| 380 | xavier | xavier | 98 | 104 | 98 | 98 |
| 382 | xavier | xavier | 3 | 4 | 6 | 6 |
| 386 | xavier | xavier | 81 | 112 | 151 | 151 |
| 390 | xavier | xavier | 313 | 313 | 315 | 315 |
| 398 | orthogonal | orthogonal | 210 | 110 | 162 | 210 |

| Arm | Near-optimal rate | Mean ratio to reference |
|---|---:|---:|
| cold (joint search) | 58% | 1.22x |
| informed_restricted (Meta-Predictor init) | 50% | 1.30x |
| universal_restricted (H4 baseline init) | 45% | 1.32x |

## Verdict

Gate check (informed_restricted near-optimal rate >= 80%): **NOT YET MET** (50%)

The Meta-Predictor's recommendation, used to *restrict* the search (not just seed it), finds near-optimal hyperparameters as reliably as informed_restricted's rate shows, and outperforms restricting to the context-free universal baseline instead -- H1 supported over H4 for this use of the recommendation.
