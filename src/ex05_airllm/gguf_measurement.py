"""Pure helpers for the Stage 10A GGUF CPU quantization sweep (no model, no network).

Compares low-bit GGUF variants (Q8_0, Q4_K_M, optionally F16) of a small **Qwen2.5-0.5B-Instruct-
GGUF** model via `llama-cpp-python`. This is a **separate** small-model low-bit sweep — it is NOT
AirLLM, NOT the Transformers Qwen2-0.5B runs, and NOT a large-model baseline. The helpers here are
pure (variant labels, chat formatting, metric math, preview, aggregation) so they are unit-tested
with **fake data only**; no `llama_cpp` import. See ``docs/MEASUREMENT_RUNS.md`` §10.
"""

from __future__ import annotations

from typing import Any

MODEL_ID = "Qwen/Qwen2.5-0.5B-Instruct-GGUF"
BACKEND = "llama_cpp_gguf"
ENVIRONMENT = "wsl_cpu"

VARIANT_F16 = "f16_reference"
VARIANT_Q8 = "q8_0"
VARIANT_Q4 = "q4_k_m"

VARIANT_FILES = {
    VARIANT_F16: "qwen2.5-0.5b-instruct-fp16.gguf",
    VARIANT_Q8: "qwen2.5-0.5b-instruct-q8_0.gguf",
    VARIANT_Q4: "qwen2.5-0.5b-instruct-q4_k_m.gguf",
}
PREVIEW_CHARS = 160
GGUF_NOTE = (
    "GGUF CPU low-bit quantization sweep (llama-cpp-python) on Qwen2.5-0.5B-Instruct-GGUF. "
    "Separate small-model sweep — NOT AirLLM, NOT the Transformers Qwen2-0.5B runs, "
    "NOT a large-model baseline."
)

RECORD_COLUMNS = (
    "run_id",
    "quantization_variant",
    "gguf_filename",
    "timestamp",
    "backend",
    "model_id",
    "environment",
    "prompt_id",
    "prompt",
    "repeat",
    "success",
    "failure_reason",
    "load_seconds",
    "ttft_seconds",
    "generation_seconds",
    "total_runtime_seconds",
    "prompt_tokens",
    "output_tokens",
    "tokens_per_second",
    "tpot_seconds",
    "itl_seconds",
    "peak_ram_mb",
    "estimated_model_file_mb",
    "output_preview",
    "notes",
)


def normalize_variant(name: str) -> str:
    """Map a filename or loose label to a canonical variant id (raises if unknown)."""
    low = name.lower()
    if "fp16" in low or "f16" in low:
        return VARIANT_F16
    if "q8_0" in low or "q8" in low:
        return VARIANT_Q8
    if "q4_k_m" in low or "q4" in low:
        return VARIANT_Q4
    raise ValueError(f"Unrecognized GGUF variant for '{name}'")


def format_chat_messages(prompt_text: str) -> list[dict[str, str]]:
    """Qwen2.5 chat messages (the llama-cpp chat handler applies the template)."""
    return [{"role": "user", "content": prompt_text}]


def make_run_id(variant: str, prompt_id: str, repeat: int) -> str:
    """Stable, deterministic run id for one GGUF run."""
    return f"gguf-qwen2_5_0_5b-{variant}-{prompt_id}-r{repeat}"


def output_preview(text: str | None, limit: int = PREVIEW_CHARS) -> str:
    """Single-line, length-capped preview of generated text."""
    if not text:
        return ""
    flat = " ".join(str(text).split())
    return flat if len(flat) <= limit else flat[:limit].rstrip() + "…"


def _round(value: float | None, ndigits: int = 6) -> float | None:
    return None if value is None else round(value, ndigits)


def compute_metrics(
    t_start: float, t_first: float | None, t_end: float, output_tokens: int | None
) -> dict[str, Any]:
    """TTFT / generation / TPOT / throughput from stream timings (TTFT None if not observed)."""
    generation = t_end - t_start
    tps = round(output_tokens / generation, 4) if output_tokens and generation > 0 else None
    if t_first is None:
        return {
            "ttft_seconds": None,
            "generation_seconds": _round(generation, 4),
            "tpot_seconds": None,
            "itl_seconds": None,
            "tokens_per_second": tps,
            "first_token_observed": False,
        }
    ttft = t_first - t_start
    decode = generation - ttft
    tpot = decode / (output_tokens - 1) if output_tokens and output_tokens > 1 else None
    return {
        "ttft_seconds": _round(ttft),
        "generation_seconds": _round(generation, 4),
        "tpot_seconds": _round(tpot),
        "itl_seconds": _round(tpot),
        "tokens_per_second": tps,
        "first_token_observed": True,
    }


def build_record(
    variant: str, prompt_id: str, repeat: int, *, success: bool, **fields: Any
) -> dict:
    """Assemble a complete, column-ordered GGUF record dict (pure; fixed fields + None defaults)."""
    rec: dict[str, Any] = dict.fromkeys(RECORD_COLUMNS)
    rec.update(
        run_id=make_run_id(variant, prompt_id, repeat),
        quantization_variant=variant,
        gguf_filename=VARIANT_FILES.get(variant),
        backend=BACKEND,
        model_id=MODEL_ID,
        environment=ENVIRONMENT,
        prompt_id=prompt_id,
        repeat=repeat,
        success=success,
        failure_reason="",
        notes=GGUF_NOTE,
    )
    rec.update(fields)
    return rec


def _mean(values: list[float]) -> float | None:
    clean = [v for v in values if v is not None]
    return round(sum(clean) / len(clean), 4) if clean else None


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Per-variant means over the successful rows (descriptive; never fabricated)."""
    ok = [r for r in rows if r.get("success") in (True, "True")]
    out: dict[str, Any] = {"note": GGUF_NOTE, "variants": {}}

    def col(rs: list[dict], key: str) -> list[float]:
        return [float(r[key]) for r in rs if r.get(key) not in (None, "", "None")]

    for variant in (VARIANT_F16, VARIANT_Q8, VARIANT_Q4):
        rs = [r for r in ok if (r.get("quantization_variant") or r.get("variant")) == variant]
        if not rs:
            continue
        out["variants"][variant] = {
            "runs": len(rs),
            "mean_ttft_seconds": _mean(col(rs, "ttft_seconds")),
            "mean_tpot_seconds": _mean(col(rs, "tpot_seconds")),
            "mean_tokens_per_second": _mean(col(rs, "tokens_per_second")),
            "mean_generation_seconds": _mean(col(rs, "generation_seconds")),
            "mean_peak_ram_mb": _mean(col(rs, "peak_ram_mb")),
            "mean_estimated_model_file_mb": _mean(col(rs, "estimated_model_file_mb")),
        }
    return out
