# Meta-Predictor Evaluation (Locked Test Split)

_Generated 2026-09-01T12-48-15Z (UTC)_

## Method

Meta-Predictor (docs.md §9.7) trained on 228 rows (76 tasks)
from the TRAIN split, evaluated exactly once on the locked TEST split
(48 rows, 16 tasks) per §12/§15.1.
Pipeline order: Model/Data/Hardware Encoders + Regime Detector (already
logged when the meta-dataset was built) -> Meta-Knowledge Base (§9.6, fit
on TRAIN only) -> Meta-Predictor (§9.7, random-forest ensemble, one head:
expected steps_to_threshold per candidate init_method).

## Results

| seed | true best init | predicted | confidence | expected steps | range | hit |
|---|---|---|---:|---:|---|---|
| 105 | xavier | orthogonal | 0.67 | 121 | 81-161 | False |
| 112 | orthogonal | orthogonal | 0.85 | 260 | 220-300 | True |
| 117 | xavier | orthogonal | 0.80 | 236 | 188-284 | False |
| 127 | he | orthogonal | 0.70 | 166 | 116-216 | False |
| 133 | orthogonal | xavier | 0.60 | 84 | 51-117 | False |
| 136 | xavier | xavier | 0.60 | 91 | 55-128 | True |
| 138 | xavier | xavier | 0.53 | 116 | 61-170 | True |
| 145 | orthogonal | orthogonal | 0.75 | 180 | 135-225 | True |
| 149 | xavier | orthogonal | 0.44 | 95 | 42-149 | False |
| 151 | orthogonal | orthogonal | 0.76 | 180 | 136-223 | True |
| 153 | xavier | he | 0.68 | 230 | 155-305 | False |
| 161 | xavier | orthogonal | 0.65 | 116 | 75-157 | False |
| 162 | xavier | orthogonal | 0.76 | 382 | 290-474 | False |
| 164 | orthogonal | orthogonal | 0.92 | 248 | 228-269 | True |
| 165 | xavier | orthogonal | 0.47 | 115 | 54-175 | False |
| 167 | he | orthogonal | 0.85 | 262 | 224-300 | False |

| Method | Accuracy |
|---|---:|
| Meta-Predictor (top-1) | 38% (6/16) |
| Universal-config baseline | 56% (9/16) |
| Random baseline (3 classes) | 33% |

Mean confidence: 0.69

## Verdict

H4 not refuted here: the universal init does at least as well as the learned Meta-Predictor on this test set.

**Calibration warning (§23 'poorly calibrated uncertainty')**: mean confidence (0.69) is well above the actual accuracy (0.38) -- the confidence score should not be trusted at this meta-dataset size.
