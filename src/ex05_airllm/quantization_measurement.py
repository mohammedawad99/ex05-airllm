"""Pure helpers for the Stage 9C Route A quantization measurement (no model, no network).

Compares an FP32 reference against a **PyTorch dynamic INT8** version of the *same* cached model.
This is **dynamic INT8 only** — NOT GGUF, NOT Q4, NOT Q8. The helpers here are pure (variant
labels, run-id, output-preview truncation, fp32-vs-int8 comparison summary) so they are unit-tested
with **fake data only**; no torch/transformers import. See ``docs/QUANTIZATION_PREFLIGHT.md`` and
``docs/MEASUREMENT_RUNS.md``.
"""

from __future__ import annotations

from typing import Any

VARIANT_FP32 = "fp32_reference"
VARIANT_INT8 = "int8_dynamic"
VARIANTS = (VARIANT_FP32, VARIANT_INT8)
PREVIEW_CHARS = 160
QUANT_NOTE = (
    "PyTorch dynamic INT8 (torch.ao.quantization.quantize_dynamic on Linear modules) vs FP32 "
    "reference, same cached Qwen2-0.5B, CPU. Dynamic INT8 only — NOT GGUF, NOT Q4, NOT Q8."
)


MODEL_ID = "Qwen/Qwen2-0.5B"
BACKEND = "transformers"
ENVIRONMENT = "wsl_cpu"

RECORD_COLUMNS = (
    "run_id",
    "variant",
    "timestamp",
    "backend",
    "model_id",
    "environment",
    "prompt_id",
    "prompt",
    "quantization",
    "repeat",
    "success",
    "failure_reason",
    "load_seconds",
    "quantization_seconds",
    "generation_seconds",
    "total_runtime_seconds",
    "output_tokens",
    "tokens_per_second",
    "approximate_tpot_seconds",
    "peak_ram_mb",
    "param_mb_estimate",
    "output_preview",
    "notes",
)


def make_run_id(variant: str, prompt_id: str, repeat: int) -> str:
    """Stable, deterministic run id for one quantization run."""
    return f"tfcpu-int8q-qwen2_0_5b-{variant}-{prompt_id}-r{repeat}"


def build_record(
    variant: str, prompt_id: str, repeat: int, *, success: bool, **fields: Any
) -> dict:
    """Assemble a complete, column-ordered record dict (pure; fixed fields + None defaults)."""
    rec: dict[str, Any] = dict.fromkeys(RECORD_COLUMNS)
    rec.update(
        run_id=make_run_id(variant, prompt_id, repeat),
        variant=variant,
        backend=BACKEND,
        model_id=MODEL_ID,
        environment=ENVIRONMENT,
        prompt_id=prompt_id,
        repeat=repeat,
        quantization=("none" if variant == VARIANT_FP32 else "int8_dynamic"),
        success=success,
        failure_reason="",
        notes=QUANT_NOTE,
    )
    rec.update(fields)
    return rec


def output_preview(text: str | None, limit: int = PREVIEW_CHARS) -> str:
    """Single-line, length-capped preview of generated text (qualitative evidence)."""
    if not text:
        return ""
    flat = " ".join(str(text).split())
    return flat if len(flat) <= limit else flat[:limit].rstrip() + "…"


def _mean(values: list[float]) -> float | None:
    clean = [v for v in values if v is not None]
    return round(sum(clean) / len(clean), 4) if clean else None


def _variant_means(rows: list[dict[str, Any]]) -> dict[str, float | None]:
    def col(key: str) -> list[float]:
        out = []
        for r in rows:
            v = r.get(key)
            if v not in (None, "", "None"):
                out.append(float(v))
        return out

    return {
        "runs": len(rows),
        "mean_generation_seconds": _mean(col("generation_seconds")),
        "mean_total_runtime_seconds": _mean(col("total_runtime_seconds")),
        "mean_tokens_per_second": _mean(col("tokens_per_second")),
        "mean_peak_ram_mb": _mean(col("peak_ram_mb")),
        "mean_output_tokens": _mean(col("output_tokens")),
    }


def comparison_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Aggregate fp32-vs-int8 means + a relative throughput/RAM delta (descriptive, honest)."""
    ok = [r for r in rows if r.get("success") in (True, "True")]
    fp32 = [r for r in ok if r.get("variant") == VARIANT_FP32]
    int8 = [r for r in ok if r.get("variant") == VARIANT_INT8]
    summary: dict[str, Any] = {
        "variant_count": {VARIANT_FP32: len(fp32), VARIANT_INT8: len(int8)},
        VARIANT_FP32: _variant_means(fp32),
        VARIANT_INT8: _variant_means(int8),
        "note": QUANT_NOTE,
    }
    summary["deltas"] = _deltas(summary[VARIANT_FP32], summary[VARIANT_INT8])
    return summary


def _ratio(new: float | None, base: float | None) -> float | None:
    if new is None or base in (None, 0):
        return None
    return round(new / base, 4)


def _deltas(
    fp32: dict[str, float | None], int8: dict[str, float | None]
) -> dict[str, float | None]:
    """INT8-relative-to-FP32 ratios (>1 throughput = faster; <1 RAM = smaller). Descriptive only."""
    return {
        "int8_vs_fp32_throughput_ratio": _ratio(
            int8["mean_tokens_per_second"], fp32["mean_tokens_per_second"]
        ),
        "int8_vs_fp32_peak_ram_ratio": _ratio(int8["mean_peak_ram_mb"], fp32["mean_peak_ram_mb"]),
        "int8_vs_fp32_generation_ratio": _ratio(
            int8["mean_generation_seconds"], fp32["mean_generation_seconds"]
        ),
    }
