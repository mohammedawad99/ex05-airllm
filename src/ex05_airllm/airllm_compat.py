"""EXPERIMENTAL, repo-local compatibility shim for AirLLM + Qwen2 on CPU.

AirLLM 2.11.0 builds the model under accelerate's ``init_empty_weights`` (everything on the
``meta`` device) and streams each decoder layer's *parameters* from disk shards. In
transformers 4.44.2 each ``Qwen2Attention`` owns a ``Qwen2RotaryEmbedding`` whose
``inv_freq``/``cos_cached``/``sin_cached`` are **non-persistent** buffers — they are not saved
in the shards, so they remain on ``meta`` and trigger
``RuntimeError: Tensor on device cpu is not on the expected device meta!`` during the CPU
forward pass (see ``docs/SMOKE_RUN.md`` / ``docs/AIRLLM_PATCH_FEASIBILITY.md``).

This shim rebuilds those rotary modules on CPU after each AirLLM ``init_model()``. It is an
**experimental** compatibility patch scoped to Qwen2 CPU only: it does NOT edit site-packages,
makes NO claim of upstream correctness, is applied per-instance (not globally), and **fails
closed** if the expected structure is not found.
"""

from __future__ import annotations

import torch


def _is_meta(tensor: object) -> bool:
    return isinstance(tensor, torch.Tensor) and tensor.is_meta


def rebuild_qwen2_rotary_on_cpu(hf_model: torch.nn.Module) -> int:
    """Replace any meta-device Qwen2 rotary embedding with a freshly-built CPU one.

    Returns the number of rotary modules rebuilt. **Fails closed**: raises ``ValueError`` if no
    ``Qwen2RotaryEmbedding`` is found at all (structure not as expected). Rotary modules already
    on CPU are left untouched (counted as found, not rebuilt).
    """
    from transformers.models.qwen2.modeling_qwen2 import Qwen2RotaryEmbedding

    found = 0
    rebuilt = 0
    for module in hf_model.modules():
        rotary = getattr(module, "rotary_emb", None)
        if not isinstance(rotary, Qwen2RotaryEmbedding):
            continue
        found += 1
        if _is_meta(getattr(rotary, "inv_freq", None)):
            module.rotary_emb = Qwen2RotaryEmbedding(
                rotary.dim,
                max_position_embeddings=rotary.max_position_embeddings,
                base=rotary.base,
                device="cpu",
            )
            rebuilt += 1
    if found == 0:
        raise ValueError("no Qwen2RotaryEmbedding found; AirLLM/Qwen2 structure not as expected")
    return rebuilt


def _is_qwen2_airllm(model: object) -> bool:
    config = getattr(model, "config", None)
    return getattr(config, "model_type", None) == "qwen2"


def patch_airllm_qwen2_cpu(model: object) -> None:
    """Wrap an AirLLM Qwen2 model so each ``init_model()`` rebuilds rotary buffers on CPU.

    Instance-scoped (no global monkeypatch, no site-packages edit). **Fails closed** if the model
    is not a Qwen2 AirLLM model or lacks the expected ``init_model`` / ``model`` structure.
    """
    if not _is_qwen2_airllm(model):
        raise ValueError("patch_airllm_qwen2_cpu: not a Qwen2 AirLLM model (fail closed)")
    original_init_model = getattr(model, "init_model", None)
    if not callable(original_init_model):
        raise ValueError("patch_airllm_qwen2_cpu: model has no init_model() (fail closed)")

    def patched_init_model() -> None:
        original_init_model()
        inner = getattr(model, "model", None)
        if inner is None:
            raise ValueError("patched init_model: AirLLM did not build .model (fail closed)")
        rebuild_qwen2_rotary_on_cpu(inner)

    model.init_model = patched_init_model
