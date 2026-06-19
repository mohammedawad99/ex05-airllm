"""Stage 3A/3B — tiny AirLLM CPU smoke probe (Qwen/Qwen2-0.5B).

Smallest honest end-to-end AirLLM check on CPU; writes a raw JSON result. This is a SMOKE
probe, **not** a benchmark: it does not measure performance, does not generalize to larger
models, and never fabricates success.

- Stage 3A: tried the upstream single-file model → failed (no shard index; see SMOKE_RUN.md).
- Stage 3B: if a locally re-sharded copy exists (``.local_models/qwen2_0_5b_sharded`` with
  ``model.safetensors.index.json``, produced by ``prepare_sharded_model.py``), load from there.

Run: ``uv run python -m ex05_airllm.smoke_airllm``.
"""

from __future__ import annotations

import json
import os
import resource
import sys
import time
import traceback
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ex05_airllm.constants import BACKEND_AIRLLM_CPU, ENV_WSL2

MODEL_ID = "Qwen/Qwen2-0.5B"  # the only model approved for download
DEVICE = "cpu"
PROMPT = "Define an operating system in one short sentence."
MAX_NEW_TOKENS = 16

_REPO_ROOT = Path(__file__).resolve().parents[2]
LOCAL_SHARDED_DIR = _REPO_ROOT / ".local_models" / "qwen2_0_5b_sharded"  # git-ignored
_AIRLLM_LAYERS = _REPO_ROOT / ".local_models" / "qwen2_0_5b_airllm_layers"  # git-ignored
OUTPUT_PATH_UPSTREAM = _REPO_ROOT / "results" / "stage3_smoke_airllm_qwen2_0_5b.json"
OUTPUT_PATH_RESHARDED = _REPO_ROOT / "results" / "stage3b_smoke_airllm_qwen2_0_5b_resharded.json"


def peak_rss_mb() -> float:
    """Peak resident memory of this process in MB (ru_maxrss is KB on Linux)."""
    return round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024, 1)


def build_smoke_result(**fields: Any) -> dict[str, Any]:
    """Assemble the smoke record with all required keys (testable, no model load)."""
    base: dict[str, Any] = {
        "stage": "3-smoke",
        "model_id": MODEL_ID,
        "local_model_path": None,
        "backend": BACKEND_AIRLLM_CPU,
        "environment": ENV_WSL2,
        "device": DEVICE,
        "prompt": PROMPT,
        "max_new_tokens": MAX_NEW_TOKENS,
        "start_timestamp": None,
        "end_timestamp": None,
        "total_runtime_seconds": None,
        "peak_rss_mb": None,
        "success": False,
        "failure_reason": "",
        "output_text": None,
        "note": "smoke probe, not a benchmark",
    }
    base.update(fields)
    return base


def write_json(path: Path, result: dict[str, Any]) -> None:
    """Write a result dict to ``path`` as pretty JSON (creates parent dirs)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")


def _run(model_source: str, local_model_path: str | None) -> dict[str, Any]:  # pragma: no cover
    start = time.perf_counter()
    started_at = datetime.now(UTC).isoformat()
    patched = bool(os.environ.get("EX05_AIRLLM_PATCH"))  # experimental Qwen2 CPU shim
    try:
        from airllm import AutoModel

        # AirLLM's check_space() calls disk_usage() on this path before creating it.
        _AIRLLM_LAYERS.mkdir(parents=True, exist_ok=True)
        model = AutoModel.from_pretrained(
            model_source, device=DEVICE, layer_shards_saving_path=str(_AIRLLM_LAYERS)
        )
        if patched:
            from ex05_airllm.airllm_compat import patch_airllm_qwen2_cpu

            patch_airllm_qwen2_cpu(model)
        tokens = model.tokenizer(PROMPT, return_tensors="pt")
        out = model.generate(tokens["input_ids"], max_new_tokens=MAX_NEW_TOKENS)
        text = model.tokenizer.decode(out[0], skip_special_tokens=True)
        return build_smoke_result(
            local_model_path=local_model_path,
            patched=patched,
            start_timestamp=started_at,
            end_timestamp=datetime.now(UTC).isoformat(),
            total_runtime_seconds=round(time.perf_counter() - start, 2),
            peak_rss_mb=peak_rss_mb(),
            success=True,
            output_text=text,
        )
    except Exception as exc:
        return build_smoke_result(
            local_model_path=local_model_path,
            patched=patched,
            start_timestamp=started_at,
            end_timestamp=datetime.now(UTC).isoformat(),
            total_runtime_seconds=round(time.perf_counter() - start, 2),
            peak_rss_mb=peak_rss_mb(),
            success=False,
            failure_reason=f"{type(exc).__name__}: {exc}",
            traceback_summary=traceback.format_exc()[-1800:],
        )


def main() -> int:  # pragma: no cover - orchestration around the real run
    if (LOCAL_SHARDED_DIR / "model.safetensors.index.json").exists():
        result = _run(str(LOCAL_SHARDED_DIR), str(LOCAL_SHARDED_DIR))
        default_out = OUTPUT_PATH_RESHARDED
    else:
        result = _run(MODEL_ID, None)
        default_out = OUTPUT_PATH_UPSTREAM
    # Allow an explicit output path (e.g. Stage 3C) so prior failure evidence is not overwritten.
    override = os.environ.get("EX05_SMOKE_OUTPUT")
    out_path = Path(override) if override else default_out
    write_json(out_path, result)
    print(f"smoke success={result['success']} -> {out_path}")
    return 0 if result["success"] else 1


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
