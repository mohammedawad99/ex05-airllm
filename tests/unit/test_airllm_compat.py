"""Unit tests for the experimental AirLLM/Qwen2 CPU rotary shim (no model download)."""

from __future__ import annotations

import types

import pytest
import torch
from transformers.models.qwen2.modeling_qwen2 import Qwen2RotaryEmbedding

from ex05_airllm import airllm_compat as c


def _module_with_rotary(device: str | None) -> torch.nn.Module:
    parent = torch.nn.Module()
    block = torch.nn.Module()
    block.rotary_emb = Qwen2RotaryEmbedding(
        8, max_position_embeddings=16, base=10000, device=device
    )
    parent.add_module("block", block)
    return parent


def test_is_meta_helper() -> None:
    assert c._is_meta(torch.empty(2, device="meta")) is True
    assert c._is_meta(torch.zeros(2)) is False
    assert c._is_meta(None) is False


def test_rebuild_moves_meta_rotary_to_cpu() -> None:
    model = _module_with_rotary("meta")
    assert model.block.rotary_emb.inv_freq.is_meta
    rebuilt = c.rebuild_qwen2_rotary_on_cpu(model)
    assert rebuilt == 1
    assert not model.block.rotary_emb.inv_freq.is_meta
    assert model.block.rotary_emb.inv_freq.device.type == "cpu"


def test_rebuild_skips_cpu_rotary() -> None:
    model = _module_with_rotary(None)  # already on CPU
    assert c.rebuild_qwen2_rotary_on_cpu(model) == 0  # found, but nothing to rebuild


def test_rebuild_fails_closed_without_rotary() -> None:
    with pytest.raises(ValueError):
        c.rebuild_qwen2_rotary_on_cpu(torch.nn.Module())


def test_patch_fails_closed_on_non_qwen2() -> None:
    fake = types.SimpleNamespace(config=types.SimpleNamespace(model_type="llama"))
    with pytest.raises(ValueError):
        c.patch_airllm_qwen2_cpu(fake)


def test_patch_wraps_init_model_and_rebuilds() -> None:
    calls = {"n": 0}

    class FakeAirLLM:
        def __init__(self) -> None:
            self.config = types.SimpleNamespace(model_type="qwen2")
            self.model = _module_with_rotary("meta")

        def init_model(self) -> None:
            calls["n"] += 1

    fake = FakeAirLLM()
    c.patch_airllm_qwen2_cpu(fake)
    fake.init_model()  # patched: original init + rotary rebuild on CPU
    assert calls["n"] == 1
    assert not fake.model.block.rotary_emb.inv_freq.is_meta
