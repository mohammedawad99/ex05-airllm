"""Unit tests for Stage 10A GGUF quantization helpers (pure; no GGUF load, no network)."""

from __future__ import annotations

import pytest

from ex05_airllm.gguf_measurement import (
    BACKEND,
    MODEL_ID,
    VARIANT_Q4,
    VARIANT_Q8,
    build_record,
    compute_metrics,
    format_chat_messages,
    make_run_id,
    normalize_variant,
    output_preview,
    summarize,
)


def test_normalize_variant() -> None:
    assert normalize_variant("qwen2.5-0.5b-instruct-q8_0.gguf") == VARIANT_Q8
    assert normalize_variant("qwen2.5-0.5b-instruct-q4_k_m.gguf") == VARIANT_Q4
    assert normalize_variant("qwen2.5-0.5b-instruct-fp16.gguf") == "f16_reference"
    with pytest.raises(ValueError):
        normalize_variant("something-else.gguf")


def test_format_chat_messages_is_qwen_user_turn() -> None:
    msgs = format_chat_messages("hi")
    assert msgs == [{"role": "user", "content": "hi"}]


def test_make_run_id_and_preview() -> None:
    assert make_run_id("q4_k_m", "os_definition", 2) == "gguf-qwen2_5_0_5b-q4_k_m-os_definition-r2"
    assert output_preview(None) == ""
    assert output_preview("  a\n b ") == "a b"
    assert output_preview("x" * 200, limit=10).endswith("…")


def test_compute_metrics_tpot_formula() -> None:
    m = compute_metrics(10.0, 10.4, 13.4, 16)  # ttft 0.4, gen 3.4, decode 3.0 over 15
    assert m["first_token_observed"] is True
    assert m["ttft_seconds"] == 0.4
    assert m["generation_seconds"] == 3.4
    assert m["tpot_seconds"] == round(3.0 / 15, 6)
    assert m["itl_seconds"] == m["tpot_seconds"]
    assert m["tokens_per_second"] == round(16 / 3.4, 4)


def test_compute_metrics_missing_ttft_not_fabricated() -> None:
    m = compute_metrics(0.0, None, 2.0, 8)
    assert m["first_token_observed"] is False
    assert m["ttft_seconds"] is None and m["tpot_seconds"] is None
    assert m["generation_seconds"] == 2.0 and m["tokens_per_second"] == round(8 / 2.0, 4)


def test_build_record_fixed_fields() -> None:
    rec = build_record(VARIANT_Q8, "os_definition", 1, success=True, tokens_per_second=20.0)
    assert rec["backend"] == BACKEND and rec["model_id"] == MODEL_ID
    assert rec["quantization_variant"] == "q8_0"
    assert rec["gguf_filename"] == "qwen2.5-0.5b-instruct-q8_0.gguf"


def test_summarize_per_variant_means() -> None:
    rows = [
        {
            "quantization_variant": VARIANT_Q8,
            "success": True,
            "tokens_per_second": 20.0,
            "ttft_seconds": 0.5,
            "peak_ram_mb": 800.0,
            "tpot_seconds": 0.05,
            "generation_seconds": 1.0,
        },
        {
            "quantization_variant": VARIANT_Q4,
            "success": True,
            "tokens_per_second": 30.0,
            "ttft_seconds": 0.4,
            "peak_ram_mb": 600.0,
            "tpot_seconds": 0.03,
            "generation_seconds": 0.8,
        },
        {"quantization_variant": VARIANT_Q4, "success": False, "tokens_per_second": None},
    ]
    s = summarize(rows)
    assert set(s["variants"]) == {VARIANT_Q8, VARIANT_Q4}
    assert s["variants"][VARIANT_Q8]["mean_tokens_per_second"] == 20.0
    assert s["variants"][VARIANT_Q4]["runs"] == 1  # failed row excluded
    assert s["variants"][VARIANT_Q4]["mean_peak_ram_mb"] == 600.0
