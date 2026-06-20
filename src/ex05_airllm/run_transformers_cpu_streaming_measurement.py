"""Stage 9B — streaming TTFT measurement (HF Transformers CPU, cached Qwen/Qwen2-0.5B).

Measures **real TTFT** by observing the first token through a ``TextIteratorStreamer`` (running
``generate`` in a worker thread), on the **already-cached** model, offline (``local_files_only``,
CPU, deterministic). Writes a *separate* result set under
``results/measurements/transformers_cpu_streaming_qwen2_0_5b/`` — it does **not** touch the Stage 5B
data. Not AirLLM, not a benchmark, no download, no Qwen2-7B, no quantization.

Run: ``HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 uv run python -m
ex05_airllm.run_transformers_cpu_streaming_measurement``.
"""

from __future__ import annotations

import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ex05_airllm.prompts import get_prompt
from ex05_airllm.result_schema import MeasurementResult
from ex05_airllm.result_writer import append_csv, write_json
from ex05_airllm.streaming_measurement import (
    STREAM_NOTE,
    compute_streaming_metrics,
    make_run_id,
)

MODEL_ID = "Qwen/Qwen2-0.5B"  # the only (already-cached) model; never downloaded here
BACKEND = "transformers"
ENVIRONMENT = "wsl_cpu"
DEVICE = "cpu"
MODEL_SIZE_LABEL = "0.5B"
QUANTIZATION = "none"
MAX_NEW_TOKENS = 32
REPEATS = 2
PROMPT_IDS = ("os_definition", "ai_agent_short", "memory_management_short")

_REPO_ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = _REPO_ROOT / "results" / "measurements" / "transformers_cpu_streaming_qwen2_0_5b"
SUMMARY_CSV = OUT_DIR / "summary.csv"


def build_result(
    *, success: bool, failure_reason: str = "", notes: str = STREAM_NOTE, **fields: Any
) -> MeasurementResult:
    """Construct a schema-valid streaming record (testable; no model)."""
    return MeasurementResult(
        environment=ENVIRONMENT,
        backend=BACKEND,
        model_id=MODEL_ID,
        model_size_label=MODEL_SIZE_LABEL,
        quantization=QUANTIZATION,
        success=success,
        failure_reason=failure_reason,
        notes=notes,
        **fields,
    )


def _rss_mb() -> float:
    import psutil

    return round(psutil.Process().memory_info().rss / 1_000_000, 1)


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


def _stream_generate(model, inputs, streamer) -> dict:  # pragma: no cover - real generation
    import threading

    import torch

    holder: dict[str, Any] = {}

    def _worker() -> None:
        with torch.no_grad():
            holder["out"] = model.generate(
                **inputs, max_new_tokens=MAX_NEW_TOKENS, do_sample=False, streamer=streamer
            )

    thread = threading.Thread(target=_worker)
    t_start = time.perf_counter()
    thread.start()
    t_first: float | None = None
    for chunk in streamer:
        if t_first is None and chunk:
            t_first = time.perf_counter()
    thread.join()
    t_end = time.perf_counter()
    return {"t_start": t_start, "t_first": t_first, "t_end": t_end, "out": holder.get("out")}


def _run_one(
    tokenizer, model, prompt_id, repeat, load_seconds
) -> MeasurementResult:  # pragma: no cover
    from transformers import TextIteratorStreamer

    spec = get_prompt(prompt_id)
    run_id = make_run_id(prompt_id, repeat)
    common = {
        "run_id": run_id,
        "timestamp": datetime.now(UTC).isoformat(),
        "prompt_id": prompt_id,
        "prompt": spec.text,
        "load_seconds": load_seconds,
    }
    peak = _rss_mb()
    try:
        inputs = tokenizer(spec.text, return_tensors="pt")
        input_len = int(inputs["input_ids"].shape[1])
        streamer = TextIteratorStreamer(tokenizer, skip_prompt=True, skip_special_tokens=True)
        timings = _stream_generate(model, inputs, streamer)
        out = timings["out"]
        out_tokens = max(0, int(out[0].shape[0]) - input_len)
        m = compute_streaming_metrics(
            timings["t_start"], timings["t_first"], timings["t_end"], out_tokens
        )
        peak = max(peak, _rss_mb())
        if not m["first_token_observed"]:
            return build_result(
                success=False,
                failure_reason="streamer yielded no token; first-token time not observed",
                **common,
                input_tokens_est=input_len,
                output_tokens=out_tokens,
            )
        return build_result(
            success=True,
            **common,
            input_tokens_est=input_len,
            output_tokens=out_tokens,
            ttft_seconds=m["ttft_seconds"],
            generation_seconds=m["generation_seconds"],
            total_runtime_seconds=m["generation_seconds"],
            tpot_seconds=m["tpot_seconds"],
            tokens_per_second=m["tokens_per_second"],
            peak_ram_mb=peak,
        )
    except Exception as exc:
        return build_result(success=False, failure_reason=f"{type(exc).__name__}: {exc}", **common)


def main() -> int:  # pragma: no cover - orchestrates the real measurement
    import torch

    torch.manual_seed(0)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    tokenizer, model, load_seconds = _load()
    total = REPEATS * len(PROMPT_IDS)
    ok = 0
    for repeat in range(1, REPEATS + 1):
        for prompt_id in PROMPT_IDS:
            torch.manual_seed(0)
            result = _run_one(tokenizer, model, prompt_id, repeat, load_seconds)
            write_json(result, OUT_DIR / f"{result.run_id}.json")
            append_csv(result, SUMMARY_CSV)
            ok += int(result.success)
            print(f"{result.run_id} success={result.success} ttft={result.ttft_seconds}")
    print(f"done: {ok}/{total} ok -> {SUMMARY_CSV}")
    return 0 if ok == total else 1


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
