"""Stage 10A — GGUF CPU low-bit quantization sweep (Qwen2.5-0.5B-Instruct-GGUF via llama-cpp).

Runs a controlled CPU sweep over the **downloaded** GGUF variants (Q8_0, Q4_K_M, and F16 only if
present) of `Qwen/Qwen2.5-0.5B-Instruct-GGUF`, same prompts as prior stages, deterministic, with
**real streaming TTFT**. Writes a *separate* result set under
``results/measurements/gguf_quantization_qwen2_5_0_5b/`` — it does **not** touch any prior run. This
is a separate small-model low-bit sweep — **not AirLLM, not a large-model baseline**. GGUF weights
stay git-ignored under ``.local_models/`` and are never committed.

Run: ``uv run python -m ex05_airllm.run_gguf_quantization_measurement`` (no network needed once the
files are present).
"""

from __future__ import annotations

import csv
import json
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

from ex05_airllm.gguf_measurement import (
    RECORD_COLUMNS,
    VARIANT_FILES,
    build_record,
    compute_metrics,
    format_chat_messages,
    output_preview,
)
from ex05_airllm.prompts import get_prompt

MAX_TOKENS = 32
REPEATS = 2
N_CTX = 1024
PROMPT_IDS = ("os_definition", "ai_agent_short", "memory_management_short")
VARIANT_ORDER = ("f16_reference", "q8_0", "q4_k_m")
_REPO_ROOT = Path(__file__).resolve().parents[2]
GGUF_DIR = _REPO_ROOT / ".local_models" / "gguf" / "qwen2_5_0_5b_instruct"
OUT_DIR = _REPO_ROOT / "results" / "measurements" / "gguf_quantization_qwen2_5_0_5b"
SUMMARY_CSV = OUT_DIR / "summary.csv"


def _rss_mb() -> float:
    import psutil

    return round(psutil.Process().memory_info().rss / 1_000_000, 1)


def _write(record: dict, output_text: str) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / f"{record['run_id']}.json").write_text(
        json.dumps(
            {**record, "output_text": output_text}, indent=2, ensure_ascii=False, default=str
        ),
        encoding="utf-8",
    )
    is_new = not SUMMARY_CSV.exists() or SUMMARY_CSV.stat().st_size == 0
    with SUMMARY_CSV.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(RECORD_COLUMNS), extrasaction="ignore")
        if is_new:
            writer.writeheader()
        writer.writerow(
            {k: ("" if record.get(k) is None else record.get(k)) for k in RECORD_COLUMNS}
        )


def _load(path: Path):  # pragma: no cover - loads a real GGUF model
    from llama_cpp import Llama

    start = time.perf_counter()
    llm = Llama(model_path=str(path), n_ctx=N_CTX, seed=0, n_threads=4, verbose=False)
    return llm, round(time.perf_counter() - start, 4)


def _stream(llm, prompt_text: str):  # pragma: no cover - real generation
    t_start = time.perf_counter()
    t_first: float | None = None
    text = ""
    for chunk in llm.create_chat_completion(
        messages=format_chat_messages(prompt_text),
        max_tokens=MAX_TOKENS,
        temperature=0.0,
        top_p=1.0,
        seed=0,
        stream=True,
    ):
        piece = chunk["choices"][0].get("delta", {}).get("content")
        if piece:
            if t_first is None:
                t_first = time.perf_counter()
            text += piece
    return t_start, t_first, time.perf_counter(), text


def _run_one(llm, variant, prompt_id, repeat, load_s, file_mb):  # pragma: no cover
    spec = get_prompt(prompt_id)
    common = {
        "timestamp": datetime.now(UTC).isoformat(),
        "prompt": spec.text,
        "load_seconds": load_s,
        "estimated_model_file_mb": file_mb,
    }
    peak = _rss_mb()
    try:
        t_start, t_first, t_end, text = _stream(llm, spec.text)
        out_tokens = len(llm.tokenize(text.encode("utf-8"), add_bos=False)) if text else 0
        prompt_tokens = len(llm.tokenize(spec.text.encode("utf-8")))
        m = compute_metrics(t_start, t_first, t_end, out_tokens)
        peak = max(peak, _rss_mb())
        return build_record(
            variant,
            prompt_id,
            repeat,
            success=True,
            **common,
            ttft_seconds=m["ttft_seconds"],
            generation_seconds=m["generation_seconds"],
            total_runtime_seconds=m["generation_seconds"],
            tpot_seconds=m["tpot_seconds"],
            itl_seconds=m["itl_seconds"],
            tokens_per_second=m["tokens_per_second"],
            prompt_tokens=prompt_tokens,
            output_tokens=out_tokens,
            peak_ram_mb=peak,
            output_preview=output_preview(text),
        ), text
    except Exception as exc:
        return build_record(
            variant,
            prompt_id,
            repeat,
            success=False,
            failure_reason=f"{type(exc).__name__}: {exc}",
            **common,
        ), ""


def _available_variants() -> list[tuple[str, Path]]:
    out = []
    for variant in VARIANT_ORDER:
        path = GGUF_DIR / VARIANT_FILES[variant]
        if path.exists():
            out.append((variant, path))
    return out


def main() -> int:  # pragma: no cover - orchestrates the real measurement
    variants = _available_variants()
    if not variants:
        print(f"no GGUF files found under {GGUF_DIR}")
        return 1
    print(f"variants present: {[v for v, _ in variants]}")
    total = ok = 0
    for variant, path in variants:
        file_mb = round(path.stat().st_size / 1_000_000, 1)
        llm, load_s = _load(path)
        for repeat in range(1, REPEATS + 1):
            for prompt_id in PROMPT_IDS:
                record, text = _run_one(llm, variant, prompt_id, repeat, load_s, file_mb)
                _write(record, text)
                total += 1
                ok += int(bool(record["success"]))
                print(
                    f"{record['run_id']} success={record['success']} ttft={record['ttft_seconds']}"
                )
    print(f"done: {ok}/{total} ok -> {SUMMARY_CSV}")
    return 0 if ok == total else 1


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
