"""Stage 5B — repeatable HF Transformers CPU measurement runner for Qwen/Qwen2-0.5B.

Thin runner over the Stage 5A SDK (schema/metrics/writer). Loads the **already-cached**
Qwen2-0.5B once (offline, `local_files_only=True`, CPU, deterministic), then measures a fixed
matrix of prompts × repeats, writing one schema-valid JSON per run + a CSV summary. This is the
runnable measurement path (ADR-0018); it is **not** AirLLM and **not** a full benchmark. No
download, no AirLLM, no Qwen2-7B.

Run: ``HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 uv run python -m
ex05_airllm.run_transformers_cpu_measurement``.
"""

from __future__ import annotations

import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ex05_airllm.metrics import MetricsCollector
from ex05_airllm.prompts import get_prompt
from ex05_airllm.result_schema import MeasurementResult
from ex05_airllm.result_writer import append_csv, write_json

MODEL_ID = "Qwen/Qwen2-0.5B"  # the only (already-cached) model; never downloaded here
BACKEND = "transformers"
ENVIRONMENT = "wsl_cpu"  # CPU-only WSL2 measurement environment label
DEVICE = "cpu"
MODEL_SIZE_LABEL = "0.5B"
QUANTIZATION = "none"
MAX_NEW_TOKENS = 32
REPEATS = 2
PROMPT_IDS = ("os_definition", "ai_agent_short", "memory_management_short")
TPOT_NOTE = "tpot_seconds ~= generation_seconds/output_tokens (approx; no TTFT/streaming hook)"

_REPO_ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = _REPO_ROOT / "results" / "measurements" / "transformers_cpu_qwen2_0_5b"
SUMMARY_CSV = OUT_DIR / "summary.csv"


def make_run_id(prompt_id: str, repeat: int) -> str:
    """Stable, deterministic run id."""
    return f"tfcpu-qwen2_0_5b-{prompt_id}-r{repeat}"


def output_tokens_from_ids(total_len: int, input_len: int) -> int:
    """Generated-token count = total sequence length minus the prompt length."""
    return max(0, int(total_len) - int(input_len))


def approx_tpot(generation_seconds: float | None, output_tokens: int | None) -> float | None:
    """Approximate per-token decode time when TTFT/streaming is unavailable."""
    if not generation_seconds or not output_tokens or output_tokens <= 0:
        return None
    return round(generation_seconds / output_tokens, 6)


def build_result(
    *, success: bool, failure_reason: str = "", notes: str = "", **fields: Any
) -> MeasurementResult:
    """Construct a schema-valid record (testable; no model). Fills fixed config fields."""
    return MeasurementResult(
        environment=ENVIRONMENT,
        backend=BACKEND,
        model_id=MODEL_ID,
        model_size_label=MODEL_SIZE_LABEL,
        quantization=QUANTIZATION,
        ttft_seconds=None,
        tpot_seconds=approx_tpot(fields.get("generation_seconds"), fields.get("output_tokens")),
        success=success,
        failure_reason=failure_reason,
        notes=notes,
        **fields,
    )


def _load() -> tuple[Any, Any, float]:  # pragma: no cover - loads the cached model
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    start = time.perf_counter()
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, local_files_only=True)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID, local_files_only=True, torch_dtype=torch.float32
    )
    model.eval()
    return tokenizer, model, round(time.perf_counter() - start, 4)


def _run_one(
    tokenizer, model, prompt_id: str, repeat: int, load_seconds: float
) -> MeasurementResult:  # pragma: no cover
    import torch

    spec = get_prompt(prompt_id)
    run_id = make_run_id(prompt_id, repeat)
    started = datetime.now(UTC).isoformat()
    wall = time.perf_counter()
    common = {
        "run_id": run_id,
        "timestamp": started,
        "prompt_id": prompt_id,
        "prompt": spec.text,
        "load_seconds": load_seconds,
    }
    try:
        inputs = tokenizer(spec.text, return_tensors="pt")
        input_len = int(inputs["input_ids"].shape[1])
        collector = MetricsCollector(clock=time.perf_counter)
        collector.start()
        with torch.no_grad():
            out = model.generate(**inputs, max_new_tokens=MAX_NEW_TOKENS, do_sample=False)
        out_tokens = output_tokens_from_ids(int(out[0].shape[0]), input_len)
        metrics = collector.finish(out_tokens)
        return build_result(
            success=True,
            notes=TPOT_NOTE,
            **common,
            input_tokens_est=input_len,
            output_tokens=out_tokens,
            generation_seconds=metrics["total_runtime_seconds"],
            total_runtime_seconds=round(time.perf_counter() - wall, 4),
            tokens_per_second=metrics["tokens_per_second"],
            peak_ram_mb=metrics["peak_ram_mb"],
        )
    except Exception as exc:
        return build_result(
            success=False,
            failure_reason=f"{type(exc).__name__}: {exc}",
            **common,
            total_runtime_seconds=round(time.perf_counter() - wall, 4),
        )


def main() -> int:  # pragma: no cover - orchestrates the real measurement
    import torch

    torch.manual_seed(0)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    tokenizer, model, load_seconds = _load()
    total = REPEATS * len(PROMPT_IDS)
    ok = 0
    for repeat in range(1, REPEATS + 1):
        for prompt_id in PROMPT_IDS:
            result = _run_one(tokenizer, model, prompt_id, repeat, load_seconds)
            write_json(result, OUT_DIR / f"{result.run_id}.json")
            append_csv(result, SUMMARY_CSV)
            ok += int(result.success)
            print(f"{result.run_id} success={result.success}")
    print(f"done: {ok}/{total} ok -> {SUMMARY_CSV}")
    return 0 if ok == total else 1


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
