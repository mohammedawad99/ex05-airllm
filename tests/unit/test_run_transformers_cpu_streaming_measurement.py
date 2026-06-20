"""Unit tests for Stage 9B streaming TTFT helpers (fake timings; no model, no network)."""

from __future__ import annotations

from ex05_airllm import run_transformers_cpu_streaming_measurement as runner
from ex05_airllm.streaming_measurement import (
    STREAM_NOTE,
    compute_streaming_metrics,
    make_run_id,
    mmm,
)


def test_make_run_id_encodes_prompt_and_repeat() -> None:
    rid = make_run_id("os_definition", 2)
    assert rid == "tfcpu-stream-qwen2_0_5b-os_definition-r2"


def test_compute_metrics_real_first_token() -> None:
    # start=10.0, first token at 10.5 (TTFT=0.5), end at 13.5 (generation=3.5), 8 output tokens
    m = compute_streaming_metrics(10.0, 10.5, 13.5, 8)
    assert m["first_token_observed"] is True
    assert m["ttft_seconds"] == 0.5
    assert m["generation_seconds"] == 3.5
    # decode = 3.5 - 0.5 = 3.0 over (8-1)=7 tokens
    assert m["tpot_seconds"] == round(3.0 / 7, 6)
    assert m["tokens_per_second"] == round(8 / 3.5, 4)
    assert 0 < m["ttft_seconds"] <= m["generation_seconds"]


def test_compute_metrics_single_token_has_no_tpot() -> None:
    m = compute_streaming_metrics(0.0, 0.2, 1.0, 1)
    assert m["ttft_seconds"] == 0.2
    assert m["tpot_seconds"] is None  # needs >1 output token


def test_compute_metrics_no_first_token_marks_unobserved() -> None:
    m = compute_streaming_metrics(0.0, None, 2.0, 5)
    assert m["first_token_observed"] is False
    assert m["ttft_seconds"] is None
    assert m["tpot_seconds"] is None
    assert m["generation_seconds"] == 2.0


def test_mmm_basic_and_empty() -> None:
    assert mmm([1.0, 2.0, 3.0]) == {"min": 1.0, "mean": 2.0, "max": 3.0, "n": 3}
    assert mmm([])["n"] == 0


def test_build_result_success_is_schema_valid_and_streaming_noted() -> None:
    r = runner.build_result(
        success=True,
        run_id="rid",
        timestamp="t",
        prompt_id="os_definition",
        prompt="p",
        input_tokens_est=9,
        output_tokens=8,
        ttft_seconds=0.5,
        generation_seconds=3.5,
        total_runtime_seconds=3.5,
        tpot_seconds=0.4,
        tokens_per_second=2.3,
        peak_ram_mb=4000.0,
    )
    assert r.success is True
    assert r.backend == "transformers"
    assert r.model_id == "Qwen/Qwen2-0.5B"
    assert r.environment == "wsl_cpu"
    assert r.ttft_seconds == 0.5
    assert "stream" in r.notes.lower()
    assert STREAM_NOTE in r.notes


def test_build_result_failure_records_reason() -> None:
    r = runner.build_result(
        success=False,
        failure_reason="streamer yielded no token; first-token time not observed",
        run_id="rid",
        timestamp="t",
        prompt_id="os_definition",
        prompt="p",
    )
    assert r.success is False
    assert "first-token" in r.failure_reason
