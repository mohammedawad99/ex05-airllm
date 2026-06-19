"""Stage 3D — direct Hugging Face Transformers CPU fallback smoke (Qwen/Qwen2-0.5B).

Proves the measurement / result-writing pipeline end-to-end using plain `transformers` on CPU
(no AirLLM, no meta-device streaming) with the **already-downloaded** Qwen2-0.5B. This is a
fallback smoke, **not** an AirLLM success and **not** a benchmark. Loads from cache only
(``local_files_only=True``); never downloads.

Run offline: ``HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 uv run python -m
ex05_airllm.smoke_transformers_cpu``.
"""

from __future__ import annotations

import json
import resource
import sys
import time
import traceback
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ex05_airllm.constants import ENV_WSL2

MODEL_ID = "Qwen/Qwen2-0.5B"  # only the already-downloaded model; cache only
BACKEND = "transformers"
DEVICE = "cpu"
PROMPT = "Define an operating system in one short sentence."
MAX_NEW_TOKENS = 16

_REPO_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_PATH = _REPO_ROOT / "results" / "stage3d_smoke_transformers_qwen2_0_5b_cpu.json"


def peak_rss_mb() -> float:
    """Peak resident memory of this process in MB (ru_maxrss is KB on Linux)."""
    return round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024, 1)


def build_result(**fields: Any) -> dict[str, Any]:
    """Assemble the result record with all required keys (testable, no model load)."""
    base: dict[str, Any] = {
        "stage": "3D-transformers-cpu",
        "model_id": MODEL_ID,
        "backend": BACKEND,
        "environment": ENV_WSL2,
        "device": DEVICE,
        "prompt": PROMPT,
        "max_new_tokens": MAX_NEW_TOKENS,
        "start_timestamp": None,
        "end_timestamp": None,
        "total_runtime_seconds": None,
        "load_seconds": None,
        "generation_seconds": None,
        "peak_rss_mb": None,
        "success": False,
        "failure_reason": "",
        "output_text": None,
        "output_tokens_est": None,
        "note": "transformers CPU fallback smoke, not AirLLM and not a benchmark",
    }
    base.update(fields)
    return base


def write_json(path: Path, result: dict[str, Any]) -> None:
    """Write a result dict to ``path`` as pretty JSON (creates parent dirs)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")


def _run() -> dict[str, Any]:  # pragma: no cover - loads the cached model + generates on CPU
    start = time.perf_counter()
    started_at = datetime.now(UTC).isoformat()
    try:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer

        load_start = time.perf_counter()
        tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, local_files_only=True)
        model = AutoModelForCausalLM.from_pretrained(
            MODEL_ID, local_files_only=True, torch_dtype=torch.float32
        )
        model.eval()
        load_seconds = round(time.perf_counter() - load_start, 2)

        inputs = tokenizer(PROMPT, return_tensors="pt")
        gen_start = time.perf_counter()
        with torch.no_grad():
            out = model.generate(**inputs, max_new_tokens=MAX_NEW_TOKENS, do_sample=False)
        generation_seconds = round(time.perf_counter() - gen_start, 2)

        new_tokens = out[0][inputs["input_ids"].shape[1] :]
        text = tokenizer.decode(new_tokens, skip_special_tokens=True)
        return build_result(
            start_timestamp=started_at,
            end_timestamp=datetime.now(UTC).isoformat(),
            total_runtime_seconds=round(time.perf_counter() - start, 2),
            load_seconds=load_seconds,
            generation_seconds=generation_seconds,
            peak_rss_mb=peak_rss_mb(),
            success=True,
            output_text=text,
            output_tokens_est=int(new_tokens.shape[0]),
        )
    except Exception as exc:
        return build_result(
            start_timestamp=started_at,
            end_timestamp=datetime.now(UTC).isoformat(),
            total_runtime_seconds=round(time.perf_counter() - start, 2),
            peak_rss_mb=peak_rss_mb(),
            success=False,
            failure_reason=f"{type(exc).__name__}: {exc}",
            traceback_summary=traceback.format_exc()[-1800:],
        )


def main() -> int:  # pragma: no cover - orchestration around the real run
    result = _run()
    write_json(OUTPUT_PATH, result)
    print(f"transformers-cpu smoke success={result['success']} -> {OUTPUT_PATH}")
    return 0 if result["success"] else 1


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
