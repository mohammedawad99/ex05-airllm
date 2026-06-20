"""Unit tests for Stage 9C Route A quantization helpers (pure; no model, no network)."""

from __future__ import annotations

from ex05_airllm.quantization_measurement import (
    QUANT_NOTE,
    RECORD_COLUMNS,
    VARIANT_FP32,
    VARIANT_INT8,
    build_record,
    comparison_summary,
    make_run_id,
    output_preview,
)


def test_variant_labels_are_int8_dynamic_not_gguf() -> None:
    assert VARIANT_FP32 == "fp32_reference"
    assert VARIANT_INT8 == "int8_dynamic"
    # honesty: the note must NOT claim GGUF/Q4/Q8
    low = QUANT_NOTE.lower()
    assert "not gguf" in low and "not q4" in low and "not q8" in low


def test_make_run_id() -> None:
    assert make_run_id("int8_dynamic", "os_definition", 2) == (
        "tfcpu-int8q-qwen2_0_5b-int8_dynamic-os_definition-r2"
    )


def test_output_preview_truncates_and_flattens() -> None:
    assert output_preview(None) == ""
    assert output_preview("  hello\n  world ") == "hello world"
    long = "x " * 200
    prev = output_preview(long, limit=20)
    assert len(prev) <= 21 and prev.endswith("…")


def test_build_record_fills_fixed_fields_and_quant_label() -> None:
    rec = build_record(VARIANT_FP32, "os_definition", 1, success=True, tokens_per_second=5.0)
    assert set(RECORD_COLUMNS).issubset(rec)
    assert rec["model_id"] == "Qwen/Qwen2-0.5B" and rec["backend"] == "transformers"
    assert rec["quantization"] == "none" and rec["variant"] == "fp32_reference"
    int8 = build_record(VARIANT_INT8, "os_definition", 1, success=True)
    assert int8["quantization"] == "int8_dynamic"


def test_comparison_summary_means_and_deltas() -> None:
    rows = [
        {
            "variant": VARIANT_FP32,
            "success": True,
            "tokens_per_second": 4.0,
            "peak_ram_mb": 4000.0,
            "generation_seconds": 6.0,
            "output_tokens": 30,
        },
        {
            "variant": VARIANT_FP32,
            "success": True,
            "tokens_per_second": 6.0,
            "peak_ram_mb": 4000.0,
            "generation_seconds": 4.0,
            "output_tokens": 30,
        },
        {
            "variant": VARIANT_INT8,
            "success": True,
            "tokens_per_second": 5.0,
            "peak_ram_mb": 2000.0,
            "generation_seconds": 5.0,
            "output_tokens": 30,
        },
    ]
    s = comparison_summary(rows)
    assert s["variant_count"] == {VARIANT_FP32: 2, VARIANT_INT8: 1}
    assert s[VARIANT_FP32]["mean_tokens_per_second"] == 5.0
    assert s[VARIANT_INT8]["mean_peak_ram_mb"] == 2000.0
    # INT8 throughput 5.0 / FP32 mean 5.0 = 1.0; RAM 2000/4000 = 0.5
    assert s["deltas"]["int8_vs_fp32_throughput_ratio"] == 1.0
    assert s["deltas"]["int8_vs_fp32_peak_ram_ratio"] == 0.5


def test_comparison_summary_excludes_failed_int8_records() -> None:
    rows = [
        {
            "variant": VARIANT_FP32,
            "success": True,
            "tokens_per_second": 5.0,
            "peak_ram_mb": 4000.0,
            "generation_seconds": 5.0,
            "output_tokens": 30,
        },
        {
            "variant": VARIANT_INT8,
            "success": False,
            "tokens_per_second": None,
            "peak_ram_mb": None,
            "generation_seconds": None,
            "output_tokens": None,
        },
    ]
    s = comparison_summary(rows)
    assert s["variant_count"] == {VARIANT_FP32: 1, VARIANT_INT8: 0}
    assert s[VARIANT_INT8]["mean_tokens_per_second"] is None
    # no INT8 data → ratio is None, never fabricated
    assert s["deltas"]["int8_vs_fp32_throughput_ratio"] is None
