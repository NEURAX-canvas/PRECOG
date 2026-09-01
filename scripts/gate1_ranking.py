#!/usr/bin/env python3
"""Gate 1 (docs.md §17): does the Trainability Engine's PURE-mode score rank
configurations the way FULL TRAINING eventually would? Target: Spearman
rho >= 0.70 (docs.md §16, P1 Ranking protocol, §15).

For a batch of synthetic tasks (V1 curriculum level 1, docs.md §25) x
candidate (optimizer, init_method) combinations, this:
  1. computes zero-cost features in PURE mode (ΔW = 0, strictly enforced --
     see precog/trainability.py, which never imports precog/modes.py),
  2. runs FULL_TRAINING to get the real steps_to_threshold as ground truth,
  3. reports the Spearman correlation between each individual proxy (and a
     naive combination) and real convergence speed.

This is the first, cheapest possible test of H1 for the new architecture --
run before investing in the Meta-Predictor, Search Engine, or any of the
heavier V2+ components.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import torch
from scipy.stats import spearmanr

from precog.model import Activation, InitMethod, ModelArchitecture, build_mlp, model_features
from precog.modes import Mode, TrainingConfig, TrainProtocol, train
from precog.taskgen import TaskConfig, TaskFunction, generate
from precog.trainability import zero_cost_features

OPTIMIZERS = ["sgd", "adam", "adamw"]
INIT_METHODS = [InitMethod.XAVIER, InitMethod.HE, InitMethod.ORTHOGONAL]
LEARNING_RATE = 0.02  # fixed for this first gate: V1 isolates init/optimizer signal (docs.md §25)
BATCH_SIZE = 32
FULL_MAX_STEPS = 800
FULL_LOSS_THRESHOLD = 0.05
NON_CONVERGENCE_PENALTY = FULL_MAX_STEPS * 2

TASKS = [
    TaskConfig(TaskFunction.LINEAR, input_dim=4, noise_level=0.1, n_samples=256, seed=1),
    TaskConfig(TaskFunction.NONLINEAR_INTERACTION, input_dim=6, noise_level=0.1, n_samples=512, seed=2),
    TaskConfig(TaskFunction.NONLINEAR_PRODUCT, input_dim=5, noise_level=0.1, n_samples=384, seed=3),
    TaskConfig(TaskFunction.LINEAR, input_dim=4, noise_level=0.3, n_samples=256, seed=4),
    TaskConfig(TaskFunction.NONLINEAR_INTERACTION, input_dim=6, noise_level=0.0, n_samples=512, seed=5),
    TaskConfig(TaskFunction.NONLINEAR_PRODUCT, input_dim=5, noise_level=0.2, n_samples=768, seed=6),
]


def main() -> None:
    rows = []

    for task_config in TASKS:
        x, y, task_feat = generate(task_config)

        for optimizer in OPTIMIZERS:
            for init_method in INIT_METHODS:
                architecture = ModelArchitecture(
                    input_dim=task_config.input_dim, depth=2, width=32, activation=Activation.RELU
                )
                training = TrainingConfig(
                    learning_rate=LEARNING_RATE,
                    batch_size=BATCH_SIZE,
                    optimizer=optimizer,
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
                    f"task={task_config.function.value:<22} optimizer={optimizer:<6} "
                    f"init={init_method.value:<11} true_steps={true_steps:<5} "
                    f"synflow={zc['synflow']:.3g} snip={zc['snip']:.3g} grasp={zc['grasp']:.3g} "
                    f"jac_cond={zc['jacobian_condition_mean']:.3g}"
                )

    proxies = ["synflow", "snip", "grasp", "jacobian_condition_mean"]
    true_steps_arr = np.array([r["true_steps"] for r in rows])

    print(f"\n--- Gate 1: ranking correlation (n={len(rows)} task x config pairs) ---")
    print("(lower true_steps = better/faster; a good proxy should correlate negatively")
    print(" with true_steps if higher-proxy-value means better trainability, or positively")
    print(" if higher means worse -- sign isn't assumed, magnitude is what matters here.)")

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
    print(f"\nGate 1 (docs.md §17, target |rho| >= 0.70): "
          f"{'PASS' if gate1_pass else 'NOT YET MET'} (|rho|={abs(rho_combined):.3f})")


if __name__ == "__main__":
    main()
