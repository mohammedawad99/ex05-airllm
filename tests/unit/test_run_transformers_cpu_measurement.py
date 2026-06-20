"""Unit tests for the Transformers CPU measurement runner helpers (no model, no network)."""

from __future__ import annotations

from ex05_airllm import run_transformers_cpu_measurement as r


def test_make_run_id_is_stable_and_deterministic() -> None:
    assert r.make_run_id("os_definition", 1) == "tfcpu-qwen2_0_5b-os_definition-r1"
    assert r.make_run_id("ai_agent_short", 2) == r.make_run_id("ai_agent_short", 2)


def test_output_tokens_from_ids() -> None:
    assert r.output_tokens_from_ids(40, 8) == 32
    assert r.output_tokens_from_ids(8, 8) == 0
    assert r.output_tokens_from_ids(5, 8) == 0  # never negative


def test_approx_tpot_handles_missing_or_zero() -> None:
    assert r.approx_tpot(2.0, 8) == 0.25
    assert r.approx_tpot(None, 8) is None
    assert r.approx_tpot(2.0, 0) is None
    assert r.approx_tpot(0.0, 8) is None


def test_config_defaults() -> None:
    assert r.MODEL_ID == "Qwen/Qwen2-0.5B"
    assert r.BACKEND == "transformers"
    assert r.ENVIRONMENT == "wsl_cpu"
    assert r.DEVICE == "cpu"
    assert r.MAX_NEW_TOKENS <= 32
    assert r.REPEATS == 2
    assert r.PROMPT_IDS == ("os_definition", "ai_agent_short", "memory_management_short")
    assert len(r.PROMPT_IDS) * r.REPEATS == 6


def test_build_result_success_record() -> None:
    result = r.build_result(
        success=True,
        notes=r.TPOT_NOTE,
        run_id="tfcpu-qwen2_0_5b-os_definition-r1",
        timestamp="2026-06-20T00:00:00+00:00",
        prompt_id="os_definition",
        prompt="Define an operating system in one short sentence.",
        load_seconds=4.0,
        input_tokens_est=10,
        output_tokens=8,
        generation_seconds=2.0,
        total_runtime_seconds=2.3,
        tokens_per_second=4.0,
        peak_ram_mb=2500.0,
    )
    assert result.success is True
    assert result.backend == "transformers"
    assert result.environment == "wsl_cpu"
    assert result.model_id == "Qwen/Qwen2-0.5B"
    assert result.ttft_seconds is None  # no streaming hook
    assert result.tpot_seconds == 0.25  # 2.0 / 8 (documented approximation)
    assert "approx" in result.notes


def test_build_result_failure_is_not_successful() -> None:
    result = r.build_result(
        success=False,
        failure_reason="RuntimeError: boom",
        run_id="tfcpu-qwen2_0_5b-os_definition-r1",
        timestamp="2026-06-20T00:00:00+00:00",
        prompt_id="os_definition",
        prompt="x",
        load_seconds=4.0,
        total_runtime_seconds=0.1,
    )
    assert result.success is False
    assert result.failure_reason == "RuntimeError: boom"
    assert result.output_tokens is None  # no fake value
    assert result.tpot_seconds is None
