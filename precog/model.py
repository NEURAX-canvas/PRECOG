"""Model definition + Model Encoder (docs.md §9.1): a parametrizable MLP and
the static descriptors X_model extractable from its architecture alone, with
no data and no training."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

import torch
import torch.nn as nn


class Activation(str, Enum):
    RELU = "relu"
    TANH = "tanh"


class InitMethod(str, Enum):
    XAVIER = "xavier"
    HE = "he"
    ORTHOGONAL = "orthogonal"


_ACTIVATION_MODULES = {Activation.RELU: nn.ReLU, Activation.TANH: nn.Tanh}


@dataclass
class ModelArchitecture:
    input_dim: int
    depth: int
    width: int
    activation: Activation


def build_mlp(architecture: ModelArchitecture, init_method: InitMethod) -> nn.Sequential:
    layers: list[nn.Module] = []
    in_dim = architecture.input_dim
    for _ in range(architecture.depth):
        linear = nn.Linear(in_dim, architecture.width)
        _init_layer(linear, init_method, nonlinearity=architecture.activation)
        layers.append(linear)
        layers.append(_ACTIVATION_MODULES[architecture.activation]())
        in_dim = architecture.width
    head = nn.Linear(in_dim, 1)
    _init_layer(head, init_method, nonlinearity=None)
    layers.append(head)
    return nn.Sequential(*layers)


def _init_layer(layer: nn.Linear, init_method: InitMethod, nonlinearity: Activation | None) -> None:
    gain = nn.init.calculate_gain(nonlinearity.value if nonlinearity else "linear")
    if init_method == InitMethod.XAVIER:
        nn.init.xavier_normal_(layer.weight, gain=gain)
    elif init_method == InitMethod.HE:
        nonlin_name = "relu" if nonlinearity == Activation.RELU else "tanh"
        nn.init.kaiming_normal_(layer.weight, nonlinearity=nonlin_name)
    elif init_method == InitMethod.ORTHOGONAL:
        nn.init.orthogonal_(layer.weight, gain=gain)
    nn.init.zeros_(layer.bias)


def model_features(model: nn.Sequential, architecture: ModelArchitecture, init_method: InitMethod) -> dict:
    """X_model (docs.md §9.1): architecture-only descriptors, no data, no training."""
    n_params = sum(p.numel() for p in model.parameters())
    # FLOPs for one forward pass of an MLP: 2 * in * out per Linear layer (mul+add).
    flops = 0
    in_dim = architecture.input_dim
    for _ in range(architecture.depth):
        flops += 2 * in_dim * architecture.width
        in_dim = architecture.width
    flops += 2 * in_dim * 1

    weight_norms = [
        layer.weight.detach().norm().item() for layer in model if isinstance(layer, nn.Linear)
    ]
    return {
        "depth": architecture.depth,
        "width": architecture.width,
        "n_params": n_params,
        "flops": flops,
        "activation": architecture.activation.value,
        "init_method": init_method.value,
        "weight_norm_mean": sum(weight_norms) / len(weight_norms),
        "weight_norm_std": torch.tensor(weight_norms).std(unbiased=False).item(),
    }
