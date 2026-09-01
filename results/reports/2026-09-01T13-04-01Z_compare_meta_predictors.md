# Meta-Predictor Comparison (4 designs, locked test split)

_Generated 2026-09-01T13-04-01Z (UTC)_

## Method

Four Meta-Predictor designs (docs.md §9.7, §19 ablation methodology), all
trained on the identical TRAIN split (228 rows,
76 tasks) and evaluated exactly once on the
identical locked TEST split (48 rows, 16
tasks): `full_rf` (all features), `reduced_rf` (only §21-validated zero-cost
proxies), `log_rf` (all features, log1p target), `knn` (Meta-Knowledge Base
neighbor vote alone, no learned model).

Baselines: universal-config = 56%, random = 33%.

## Results

| candidate | accuracy | mean confidence | calibration gap |
|---|---:|---:|---:|
| reduced_rf | 44% (7/16) | 0.33 | -0.11 |
| knn | 38% (6/16) | 0.45 | +0.08 |
| full_rf | 25% (4/16) | 0.66 | +0.41 |
| log_rf | 12% (2/16) | 0.68 | +0.56 |

## Winner: `reduced_rf`

Selected by accuracy first, then by the smallest confidence/accuracy
calibration gap (docs.md §23 "poorly calibrated uncertainty" risk) as
tiebreaker. Does NOT beat the
universal-config baseline (56%).

| seed | true best init | predicted | confidence | hit |
|---|---|---|---:|---|
| 105 | xavier | xavier | 0.65 | True |
| 112 | orthogonal | orthogonal | 0.54 | True |
| 117 | xavier | he | 0.23 | False |
| 127 | he | orthogonal | 0.23 | False |
| 133 | orthogonal | xavier | 0.26 | False |
| 136 | xavier | xavier | 0.18 | True |
| 138 | xavier | orthogonal | 0.45 | False |
| 145 | orthogonal | orthogonal | 0.44 | True |
| 149 | xavier | xavier | 0.01 | True |
| 151 | orthogonal | orthogonal | 0.44 | True |
| 153 | xavier | orthogonal | 0.39 | False |
| 161 | xavier | xavier | 0.32 | True |
| 162 | xavier | orthogonal | 0.20 | False |
| 164 | orthogonal | xavier | 0.00 | False |
| 165 | xavier | orthogonal | 0.48 | False |
| 167 | he | xavier | 0.43 | False |

## Verdict

H4 not refuted: even the best of four tested Meta-Predictor designs does not beat the universal-config baseline at this meta-dataset size (76 training tasks). The bottleneck is data volume, not model choice -- see docs.md §27 'the meta-dataset's quality intrinsically bounds the meta-predictor's quality.'
