"""Lightweight, privacy-safe environment metadata for run reproducibility.

Captures only non-sensitive facts (Python/platform/torch/cuda/project version). It
deliberately excludes usernames, absolute private paths, tokens, and secrets.
"""

from __future__ import annotations

import platform
import sys

from ex05_airllm.version import __version__


def _torch_info() -> tuple[str | None, bool | None]:
    try:
        import torch
    except Exception:
        return None, None
    try:
        return torch.__version__, bool(torch.cuda.is_available())
    except Exception:
        return getattr(torch, "__version__", None), None


def environment_metadata() -> dict[str, object]:
    """Return a small dict of reproducibility metadata (no secrets / no private paths)."""
    torch_version, cuda_available = _torch_info()
    return {
        "python_version": platform.python_version(),
        "python_implementation": platform.python_implementation(),
        "platform": platform.system(),
        "platform_release": platform.release(),
        "machine": platform.machine(),
        "torch_version": torch_version,
        "cuda_available": cuda_available,
        "project_version": __version__,
        "executable_present": bool(sys.executable),
    }
