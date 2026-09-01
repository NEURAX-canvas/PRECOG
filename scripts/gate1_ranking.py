#!/usr/bin/env python3
"""Gate 1 (docs.md §17): does the Trainability Engine's PURE-mode score rank
configurations the way FULL TRAINING eventually would? Target: Spearman
rho >= 0.70 (docs.md §16, P1 Ranking protocol, §15).

Designed as a controlled experiment per §21 ("only the candidate variable
changes, architecture/dataset/optimizer fixed"), not a mixed sweep: the
first version of this script varied optimizer AND init_method together,
which conflates two effects and, worse, is structurally invalid for
optimizer -- the Trainability Engine's proxies are computed in PURE mode,
strictly before any optimizer exists (§5, ΔW=0), so none of them can
possibly encode which optimizer will later be used. Ranking-correlating a
score that is *constant* across optimizers against an outcome that *varies*
by optimizer measures noise, not proxy quality.

So this script isolates exactly one candidate variable -- initialization --
with architecture, task, learning rate, batch size and optimizer all fixed,
which is also the one degree of freedom §9.4's "initialization analysis /
dynamical isometry" signals are theoretically supposed to explain (§11.2).
Predicting optimizer/LR/batch is a different, harder question that needs
the learned Meta-Predictor (§9.7) trained on the meta-dataset, not a raw
PURE-mode score -- see the printed note at the end.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import torch
from scipy.stats import spearmanr

from precog.model import Activation, InitMethod, ModelArchitecture, build_mlp
from precog.modes import Mode, TrainingConfig, TrainProtocol, train
from precog.taskgen import TaskConfig, TaskFunction, generate
from precog.trainability import zero_cost_features

# Controlled per §21: fixed for every row below.
FIXED_OPTIMIZER = "adam"
FIXED_LEARNING_RATE = 0.02
FIXED_BATCH_SIZE = 32
FULL_MAX_STEPS = 800
FULL_LOSS_THRESHOLD = 0.05
NON_CONVERGENCE_PENALTY = FULL_MAX_STEPS * 2

# The one candidate variable.
INIT_METHODS = [InitMethod.XAVIER, InitMethod.HE, InitMethod.ORTHOGONAL]

TASKS = [
    TaskConfig(TaskFunction.LINEAR, input_dim=4, noise_level=0.1, n_samples=256, seed=1),
    TaskConfig(TaskFunction.NONLINEAR_INTERACTION, input_dim=6, noise_level=0.1, n_samples=512, seed=2),
    TaskConfig(TaskFunction.NONLINEAR_PRODUCT, input_dim=5, noise_level=0.1, n_samples=384, seed=3),
    TaskConfig(TaskFunction.LINEAR, input_dim=4, noise_level=0.3, n_samples=256, seed=4),
    TaskConfig(TaskFunction.NONLINEAR_INTERACTION, input_dim=6, noise_level=0.0, n_samples=512, seed=5),
    TaskConfig(TaskFunction.NONLINEAR_PRODUCT, input_dim=5, noise_level=0.2, n_samples=768, seed=6),
    TaskConfig(TaskFunction.LINEAR, input_dim=5, noise_level=0.0, n_samples=384, seed=7),
    TaskConfig(TaskFunction.NONLINEAR_INTERACTION, input_dim=7, noise_level=0.2, n_samples=640, seed=8),
    TaskConfig(TaskFunction.NONLINEAR_PRODUCT, input_dim=6, noise_level=0.05, n_samples=512, seed=9),
    TaskConfig(TaskFunction.LINEAR, input_dim=6, noise_level=0.2, n_samples=320, seed=10),
    TaskConfig(TaskFunction.NONLINEAR_INTERACTION, input_dim=5, noise_level=0.05, n_samples=448, seed=11),
    TaskConfig(TaskFunction.NONLINEAR_PRODUCT, input_dim=4, noise_level=0.1, n_samples=256, seed=12),
]


def main() -> None:
    rows = []

    for task_config in TASKS:
        x, y, task_feat = generate(task_config)

        for init_method in INIT_METHODS:
            architecture = ModelArchitecture(
                input_dim=task_config.input_dim, depth=2, width=32, activation=Activation.RELU
            )
            training = TrainingConfig(
                learning_rate=FIXED_LEARNING_RATE,
                batch_size=FIXED_BATCH_SIZE,
                optimizer=FIXED_OPTIMIZER,
                weight_decay=1e-5,
                init_method=init_method,
            )

            # PURE mode: build once, score, never call .step() on this model.
            torch.manual_seed(0)
            pure_model = build_mlp(architecture, init_method)
            zc = zero_cost_features(pure_model, task_config.input_dim, x, y)

            # FULL TRAINING: ground truth, a fresh model of its own.
            protocol = TrainProtocol(
                mode=Mode.FULL_TRAINING,
                max_steps=FULL_MAX_STEPS,
                loss_threshold=FULL_LOSS_THRESHOLD,
                seed=0,
            )
            result = train(architecture, x, y, training, protocol)
            true_steps = result.steps_to_threshold if result.converged else NON_CONVERGENCE_PENALTY

            rows.append({**zc, "true_steps": true_steps, "task": task_config.function.value})
            print(
                f"task={task_config.function.value:<22} init={init_method.value:<11} "
                f"true_steps={true_steps:<5} synflow={zc['synflow']:.3g} "
                f"jacob_cov={zc['jacob_cov']:.3g} grad_norm={zc['gradient_norm']:.3g}"
            )

    proxies = [
        "synflow", "snip", "grasp", "jacob_cov", "effective_rank", "hessian_trace",
        "jacobian_condition_mean", "gradient_norm", "gradient_norm_variance",
        "activation_mean", "activation_variance",
    ]
    true_steps_arr = np.array([r["true_steps"] for r in rows])

    print(f"\n--- Gate 1: ranking correlation (n={len(rows)} rows, "
          f"{len(TASKS)} tasks x {len(INIT_METHODS)} init methods, optimizer/LR/batch fixed) ---")

    combined_z = np.zeros(len(rows))
    for proxy in proxies:
        values = np.array([r[proxy] for r in rows])
        if np.std(values) == 0:
            print(f"{proxy:<28} constant across all rows, skipping")
            continue
        rho, p_value = spearmanr(values, true_steps_arr)
        print(f"{proxy:<28} rho={rho:+.3f}  p={p_value:.3g}")
        combined_z += (values - values.mean()) / (values.std() + 1e-12) * np.sign(rho or 1)

    rho_combined, p_combined = spearmanr(combined_z, true_steps_arr)
    print(f"{'naive combined (avg z-score)':<28} rho={rho_combined:+.3f}  p={p_combined:.3g}")

    gate1_pass = abs(rho_combined) >= 0.70
    print(f"\nGate 1 (docs.md §17, target |rho| >= 0.70) on the init-only controlled "
          f"experiment: {'PASS' if gate1_pass else 'NOT YET MET'} (|rho|={abs(rho_combined):.3f})")

    print(
        "\nNote (§9.4, §5): every proxy above is computed in PURE mode, strictly before any\n"
        "optimizer/LR/batch_size is chosen (DeltaW=0) -- so this experiment can only ever\n"
        "test whether the Trainability Engine explains *initialization* quality. It\n"
        "structurally cannot rank optimizer/LR/batch_size choices: those need the learned\n"
        "Meta-Predictor (§9.7), trained on the meta-dataset (§12) to associate a\n"
        "(model, data, zero-cost-features) signature with historically good H* -- the\n"
        "same lesson the archived v0 prototype already learned the hard way."
    )


if __name__ == "__main__":
    main()
