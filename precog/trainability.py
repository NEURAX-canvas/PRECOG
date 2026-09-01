"""Trainability Engine (docs.md §9.4, §11): zero-cost proxies computed
without ever calling optimizer.step() -- strict PURE mode (§5, ΔW = 0).

§9.4 names four things explicitly, all implemented here:
  1. Zero-Cost Proxies: SynFlow, SNIP, GraSP, Jacob-Cov, gradient and
     activation statistics on one or a few mini-batches.
  2. NEAR: effective rank of activations, as an expressivity indicator.
  3. Initialization analysis: activation/gradient variance, Jacobian
     singular values, conditioning kappa(J) = sigma_max/sigma_min.
  4. Curvature (when cheaply measurable): local Hessian approximation.

Formulas (standard references, see /source.md pillars 3, 4 and 7):
  synflow (Tanaka et al., 2020) -- data-independent: take |theta|, forward an
    all-ones input, backprop the summed output, score = sum(theta * grad).
  snip (Lee et al., 2019) -- loss-sensitivity per weight on one minibatch:
    score = sum(|grad_i * theta_i|).
  grasp (Wang et al., 2020) -- Hessian-gradient product via the double-
    backward trick d(g^T g)/dtheta = 2*H@g:
    score = -sum(theta_i * (H@g)_i).
  jacob_cov / NASWOT (Mellor et al., 2021) -- binarize each activation unit
    (active/inactive) per sample into a code c_i, build the kernel
    K = C@C.T + (1-C)@(1-C).T, score = log|det(K)|: samples whose
    activation patterns are more distinguishable give a higher score.
  effective_rank / NEAR -- singular values of a hidden layer's activations,
    erank = exp(entropy(sigma_i / sum(sigma))) (Roy & Vetterli effective
    rank, as used by NEAR to estimate expressivity without training).
  jacobian_conditioning -- singular values of the trunk's input-output
    Jacobian (torch.func.jacrev + vmap, per stack.md §1), condition number
    kappa = sigma_max / sigma_min as a dynamical-isometry proxy (§11.2).
  gradient_activation_stats -- gradient norm on a real minibatch, per-sample
    gradient-norm variance, and activation mean/variance (§11.2 signals).
  hessian_trace -- Hutchinson estimator tr(H) ~= E[v^T H v] for Rademacher
    v, a cheap curvature approximation (§9.4 "when cheaply measurable").

No proxy is trusted alone (docs.md §9.4 "never an isolated score", H2):
zero_cost_features() below returns all of them together, combined only by
a downstream learned meta-predictor, never by picking a single winner.
"""
from __future__ import annotations

import copy

import torch
import torch.nn as nn
from torch.func import jacrev, vmap

_ACTIVATION_MODULES = (nn.ReLU, nn.Tanh)


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


def jacob_cov(model: nn.Sequential, x: torch.Tensor) -> float:
    """NASWOT score (Mellor et al., 2021): log|det(K)| of the binary
    activation-pattern kernel. Defined for ReLU-style (0/1) activations in
    the original paper; generalized here to any activation via sign(out)>0,
    which reduces to the standard definition for ReLU."""
    model = copy.deepcopy(model)
    codes = []
    handles = []

    def hook(_module, _inp, out):
        codes.append((out > 0).float().reshape(out.shape[0], -1))

    for module in model:
        if isinstance(module, _ACTIVATION_MODULES):
            handles.append(module.register_forward_hook(hook))
    with torch.no_grad():
        model(x)
    for h in handles:
        h.remove()

    c = torch.cat(codes, dim=1)
    kernel = c @ c.T + (1.0 - c) @ (1.0 - c).T
    # Standard numerical stabilization: with more samples than activation
    # units, two samples can share an identical binary code, making K
    # singular (logdet = -inf). A small ridge on the diagonal is the usual
    # fix in NASWOT implementations.
    kernel = kernel + 1e-4 * torch.eye(kernel.shape[0])
    _sign, logabsdet = torch.linalg.slogdet(kernel)
    return float(logabsdet.item())


def effective_rank(model: nn.Sequential, x: torch.Tensor) -> float:
    """NEAR-style expressivity proxy: effective rank (Roy & Vetterli) of the
    last hidden layer's activations, erank = exp(entropy(normalized
    singular values)). Higher = activations span more independent
    directions = more expressive representation."""
    trunk = model[:-1]
    with torch.no_grad():
        activations = trunk(x)
    singular_values = torch.linalg.svdvals(activations)
    p = (singular_values / singular_values.sum()).clamp_min(1e-12)
    entropy = -(p * p.log()).sum()
    return float(torch.exp(entropy).item())


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


def gradient_activation_stats(
    model: nn.Sequential, x: torch.Tensor, y: torch.Tensor, loss_fn, max_samples: int = 16
) -> dict:
    """Gradient norm + per-sample gradient-norm variance on a real
    minibatch, and activation mean/variance at every activation layer
    (docs.md §9.4 "gradient and activation statistics", §11.2)."""
    model = copy.deepcopy(model)
    params = list(model.parameters())
    for p in params:
        p.requires_grad_(True)

    activations: dict[int, torch.Tensor] = {}
    handles = []

    def make_hook(key):
        def hook(_module, _inp, out):
            activations[key] = out.detach()

        return hook

    for i, module in enumerate(model):
        if isinstance(module, _ACTIVATION_MODULES):
            handles.append(module.register_forward_hook(make_hook(i)))

    loss = loss_fn(model(x), y)
    batch_grads = torch.autograd.grad(loss, params)
    for h in handles:
        h.remove()
    batch_grad_norm = torch.sqrt(sum((g**2).sum() for g in batch_grads))

    n = min(x.shape[0], max_samples)
    per_sample_norms = []
    for i in range(n):
        for p in params:
            p.grad = None
        sample_loss = loss_fn(model(x[i : i + 1]), y[i : i + 1])
        sample_grads = torch.autograd.grad(sample_loss, params)
        per_sample_norms.append(torch.sqrt(sum((g**2).sum() for g in sample_grads)).item())
    grad_norm_variance = float(torch.tensor(per_sample_norms).var(unbiased=False).item())

    act_means = [a.mean().item() for a in activations.values()]
    act_vars = [a.var(unbiased=False).item() for a in activations.values()]

    return {
        "gradient_norm": float(batch_grad_norm.item()),
        "gradient_norm_variance": grad_norm_variance,
        "activation_mean": sum(act_means) / len(act_means),
        "activation_variance": sum(act_vars) / len(act_vars),
    }


def hessian_trace(
    model: nn.Sequential, x: torch.Tensor, y: torch.Tensor, loss_fn, num_probes: int = 5
) -> float:
    """Hutchinson trace estimator tr(H) ~= E[v^T H v] for Rademacher v
    (docs.md §9.4 "curvature, when cheaply measurable"; cf. legacy Rust
    prototype's identical use of this estimator for the same purpose)."""
    model = copy.deepcopy(model)
    params = list(model.parameters())
    for p in params:
        p.requires_grad_(True)

    loss = loss_fn(model(x), y)
    grads = torch.autograd.grad(loss, params, create_graph=True)

    estimates = []
    for _ in range(num_probes):
        v = [torch.randint(0, 2, p.shape).float() * 2 - 1 for p in params]
        grad_dot_v = sum((g * vi).sum() for g, vi in zip(grads, v))
        hv = torch.autograd.grad(grad_dot_v, params, retain_graph=True)
        estimates.append(sum((hvi * vi).sum() for hvi, vi in zip(hv, v)).item())
    return float(sum(estimates) / len(estimates))


def zero_cost_features(
    model: nn.Sequential, input_dim: int, x: torch.Tensor, y: torch.Tensor, minibatch_size: int = 64
) -> dict:
    """Score_ZC = f(S_1, ..., S_n) (docs.md §9.4): the full combined feature
    vector meant to feed the meta-predictor -- every proxy named in §9.4,
    never a single one alone.

    Uses "one or a few mini-batches" (§9.4), not the whole dataset: proxies
    like jacob_cov build a kernel whose rank is bounded by the number of
    activation units, so feeding it hundreds of samples makes it singular
    for no benefit -- a genuine mini-batch is both truer to the spec and
    numerically better behaved.
    """
    n = min(minibatch_size, x.shape[0])
    x, y = x[:n], y[:n]
    loss_fn = nn.functional.mse_loss
    features = {
        "synflow": synflow(model, input_dim),
        "snip": snip(model, x, y, loss_fn),
        "grasp": grasp(model, x, y, loss_fn),
        "jacob_cov": jacob_cov(model, x),
        "effective_rank": effective_rank(model, x),
        "hessian_trace": hessian_trace(model, x, y, loss_fn),
    }
    features.update(jacobian_conditioning(model, x))
    features.update(gradient_activation_stats(model, x, y, loss_fn))
    return features
