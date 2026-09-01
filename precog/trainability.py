"""Trainability Engine (docs.md §9.4, §11): zero-cost proxies computed
without ever calling optimizer.step() -- strict PURE mode (§5).

Formulas (standard references, see /source.md pillar 3 and 7):
  synflow (Tanaka et al., 2020) -- data-independent: take |theta|, forward an
    all-ones input, backprop the summed output, score = sum(theta * grad).
  snip (Lee et al., 2019) -- loss-sensitivity per weight on one minibatch:
    score = sum(|grad_i * theta_i|).
  grasp (Wang et al., 2020) -- Hessian-gradient product via the double-
    backward trick d(g^T g)/dtheta = 2*H@g:
    score = -sum(theta_i * (H@g)_i).
  jacobian_conditioning -- singular values of the trunk's input-output
  Jacobian (torch.func.jacrev + vmap, per stack.md §1), condition number
  kappa = sigma_max / sigma_min as a dynamical-isometry proxy (§9.4, §11.2).

No proxy is trusted alone (docs.md §9.4 "jamais un score isolé", H2): callers
should combine these into a feature vector, not pick a single winner.
"""
from __future__ import annotations

import copy

import torch
import torch.nn as nn
from torch.func import jacrev, vmap


@torch.no_grad()
def _linearize(model: nn.Sequential) -> list[torch.Tensor]:
    """Replaces every parameter with its absolute value in place, returns the
    original signs so the caller can restore them afterward."""
    signs = []
    for p in model.parameters():
        signs.append(p.sign())
        p.abs_()
    return signs


@torch.no_grad()
def _restore_signs(model: nn.Sequential, signs: list[torch.Tensor]) -> None:
    for p, sign in zip(model.parameters(), signs):
        p.mul_(sign)


def synflow(model: nn.Sequential, input_dim: int) -> float:
    """Data-independent proxy: no real batch needed, hence usable even
    before the Data Encoder has produced a single sample (docs.md §9.4)."""
    model = copy.deepcopy(model)
    for p in model.parameters():
        p.requires_grad_(True)
    signs = _linearize(model)

    ones_input = torch.ones((1, input_dim))
    output = model(ones_input)
    output.sum().backward()

    score = sum((p * p.grad).sum() for p in model.parameters() if p.grad is not None)
    _restore_signs(model, signs)
    return float(score.item())


def snip(model: nn.Sequential, x: torch.Tensor, y: torch.Tensor, loss_fn) -> float:
    model = copy.deepcopy(model)
    for p in model.parameters():
        p.requires_grad_(True)
    loss = loss_fn(model(x), y)
    grads = torch.autograd.grad(loss, list(model.parameters()))
    score = sum((g.abs() * p.abs()).sum() for g, p in zip(grads, model.parameters()))
    return float(score.item())


def grasp(model: nn.Sequential, x: torch.Tensor, y: torch.Tensor, loss_fn) -> float:
    model = copy.deepcopy(model)
    params = list(model.parameters())
    for p in params:
        p.requires_grad_(True)

    loss = loss_fn(model(x), y)
    grads = torch.autograd.grad(loss, params, create_graph=True)
    grad_sq_sum = sum((g * g).sum() for g in grads)
    hg = torch.autograd.grad(grad_sq_sum, params)

    score = sum(-(p.detach() * h).sum() for p, h in zip(params, hg))
    return float(score.item())


def jacobian_conditioning(model: nn.Sequential, x: torch.Tensor) -> dict:
    """Condition number of the trunk's (all layers but the final regression
    head) input-output Jacobian, computed per-sample via vmap(jacrev(.))
    (stack.md §1) then aggregated over the batch."""
    trunk = model[:-1]

    def f(single_x: torch.Tensor) -> torch.Tensor:
        return trunk(single_x.unsqueeze(0)).squeeze(0)

    jacobians = vmap(jacrev(f))(x)  # (batch, hidden_dim, input_dim)
    singular_values = torch.linalg.svdvals(jacobians)  # (batch, min(hidden_dim, input_dim))

    sigma_max = singular_values[:, 0]
    sigma_min = singular_values[:, -1].clamp_min(1e-12)
    condition_numbers = sigma_max / sigma_min

    return {
        "jacobian_condition_mean": float(condition_numbers.mean().item()),
        "jacobian_condition_median": float(condition_numbers.median().item()),
        "jacobian_sigma_max_mean": float(sigma_max.mean().item()),
    }


def zero_cost_features(model: nn.Sequential, input_dim: int, x: torch.Tensor, y: torch.Tensor) -> dict:
    """Score_ZC = f(S_1, ..., S_n) (docs.md §9.4): the combined feature
    vector meant to feed the meta-predictor, never a single proxy alone."""
    loss_fn = nn.functional.mse_loss
    features = {
        "synflow": synflow(model, input_dim),
        "snip": snip(model, x, y, loss_fn),
        "grasp": grasp(model, x, y, loss_fn),
    }
    features.update(jacobian_conditioning(model, x))
    return features
