#!/usr/bin/env python3
"""
Builds the Experiment Database (§21) by running Optuna (Bayesian optimization,
TPE) as the reference hyperparameter search on a batch of synthetic tasks
(§13), calling the Rust `pretrainopt-trial` binary once per trial.

Optuna here plays the role described in §8: it is a ground-truth generator
used offline, not the final predictor. Every single trial (not just the best)
is appended to data/experiment_database.jsonl, so the resulting dataset
supports both meta-dataset formulations from §22:
  - regression of the outcome for a given H (all trials)
  - direct prediction of H* (best trial per task)

Usage:
    python3 python/run_search.py --n-tasks 10 --trials-per-task 60
"""
from __future__ import annotations

import argparse
import json
import random
import subprocess
import time
from pathlib import Path

import optuna

REPO_ROOT = Path(__file__).resolve().parents[1]
TRIAL_BINARY = REPO_ROOT / "target" / "release" / "pretrainopt-trial"
EXPERIMENT_DB = REPO_ROOT / "data" / "experiment_database.jsonl"

# Fixed architecture for the MVP (Annexe B: "MLP uniquement", architecture given
# not searched -- NAS is explicitly out of scope, §7/§40).
ARCHITECTURE = {"depth": 2, "width": 32, "activation": "Relu"}
PROTOCOL_LOSS_THRESHOLD = 0.05
PROTOCOL_MAX_STEPS = 800

TASK_FUNCTIONS = ["Linear", "NonlinearInteraction", "NonlinearProduct"]


def build_tasks(n_tasks: int) -> list[dict]:
    """Generates a diverse batch of synthetic task configs (§13) to search over.

    Draws noise/dimension/sample-size continuously from a per-task RNG rather
    than cycling a small fixed grid: a fixed grid repeats every
    lcm(len(functions), len(noise), len(n_samples)) tasks, which caps real
    task diversity and lets a meta-model "memorize" a handful of buckets
    instead of learning a genuine task -> H* relationship (§35 meta-overfitting risk).
    """
    tasks = []
    for i in range(n_tasks):
        rng = random.Random(2000 + i)
        function = TASK_FUNCTIONS[i % len(TASK_FUNCTIONS)]
        min_dim = {"Linear": 2, "NonlinearInteraction": 4, "NonlinearProduct": 3}[function]
        input_dim = rng.randint(min_dim, min_dim + 6)
        noise_level = round(rng.uniform(0.0, 0.4), 3)
        n_samples = rng.choice([128, 256, 384, 512, 768, 1024, 1536])
        tasks.append(
            {
                "task_id": f"task_{i:03d}_{function}_noise{noise_level}_n{n_samples}",
                "function": function,
                "input_dim": input_dim,
                "noise_level": noise_level,
                "n_samples": n_samples,
                "seed": 1000 + i,
            }
        )
    return tasks


def run_trial(task: dict, training: dict, protocol_seed: int) -> dict:
    spec = {
        "task": {
            "function": task["function"],
            "input_dim": task["input_dim"],
            "noise_level": task["noise_level"],
            "n_samples": task["n_samples"],
            "seed": task["seed"],
        },
        "architecture": {"input_dim": task["input_dim"], **ARCHITECTURE},
        "training": training,
        "protocol": {
            "loss_threshold": PROTOCOL_LOSS_THRESHOLD,
            "max_steps": PROTOCOL_MAX_STEPS,
            "seed": protocol_seed,
        },
    }
    proc = subprocess.run(
        [str(TRIAL_BINARY)],
        input=json.dumps(spec),
        capture_output=True,
        text=True,
        timeout=120,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"trial failed: {proc.stderr}")
    return json.loads(proc.stdout)


def make_objective(task: dict, db_file, trial_counter: list[int]):
    def objective(trial: optuna.Trial) -> float:
        training = {
            "learning_rate": trial.suggest_float("learning_rate", 1e-5, 1e-1, log=True),
            "batch_size": trial.suggest_categorical("batch_size", [16, 32, 64, 128]),
            "optimizer": trial.suggest_categorical("optimizer", ["Sgd", "Adam", "AdamW"]),
            "weight_decay": trial.suggest_float("weight_decay", 1e-6, 1e-2, log=True),
            "init_method": trial.suggest_categorical("init_method", ["Xavier", "He"]),
        }

        result = run_trial(task, training, protocol_seed=trial_counter[0])
        trial_counter[0] += 1

        record = {
            "task_id": task["task_id"],
            "optuna_trial": trial.number,
            **result,
        }
        db_file.write(json.dumps(record) + "\n")
        db_file.flush()

        if result["diverged"] or not result["converged"]:
            return float(PROTOCOL_MAX_STEPS * 2)
        return float(result["steps_to_threshold"])

    return objective


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-tasks", type=int, default=10)
    parser.add_argument("--trials-per-task", type=int, default=60)
    args = parser.parse_args()

    if not TRIAL_BINARY.exists():
        raise SystemExit(
            f"binary not found at {TRIAL_BINARY} -- run `cargo build --release` first"
        )

    EXPERIMENT_DB.parent.mkdir(parents=True, exist_ok=True)
    tasks = build_tasks(args.n_tasks)

    optuna.logging.set_verbosity(optuna.logging.WARNING)

    with EXPERIMENT_DB.open("a") as db_file:
        for task in tasks:
            print(f"[{time.strftime('%H:%M:%S')}] searching task={task['task_id']}")
            trial_counter = [0]
            study = optuna.create_study(direction="minimize")
            study.optimize(
                make_objective(task, db_file, trial_counter),
                n_trials=args.trials_per_task,
                show_progress_bar=False,
            )
            print(
                f"  best steps_to_threshold={study.best_value} "
                f"params={study.best_params}"
            )

    print(f"done. experiment database at {EXPERIMENT_DB}")


if __name__ == "__main__":
    main()
