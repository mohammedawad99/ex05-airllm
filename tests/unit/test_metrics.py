"""Unit tests for MetricsCollector with a controlled clock (no model, no real timing)."""

from __future__ import annotations

from collections.abc import Callable

import pytest

from ex05_airllm.metrics import MetricsCollector


def _clock(times: list[float]) -> Callable[[], float]:
    iterator = iter(times)
    return lambda: next(iterator)


def _fixed_rss(mb: float) -> Callable[[], int]:
    return lambda: int(mb * 1_000_000)


def test_full_run_with_first_token() -> None:
    # clock is read at: start, first_token, finish
    collector = MetricsCollector(clock=_clock([10.0, 10.5, 12.5]), rss_bytes=_fixed_rss(100))
    collector.start()
    collector.mark_first_token()
    metrics = collector.finish(output_tokens=5)
    assert metrics["total_runtime_seconds"] == 2.5
    assert metrics["ttft_seconds"] == 0.5
    assert metrics["generation_seconds"] == 2.0
    assert metrics["tpot_seconds"] == 0.5  # 2.0 / (5 - 1)
    assert metrics["tokens_per_second"] == 2.5  # 5 / 2.0
    assert metrics["peak_ram_mb"] == 100.0


def test_run_without_first_token_falls_back_to_total() -> None:
    collector = MetricsCollector(clock=_clock([0.0, 4.0]), rss_bytes=_fixed_rss(50))
    collector.start()
    metrics = collector.finish(output_tokens=8)
    assert metrics["ttft_seconds"] is None
    assert metrics["generation_seconds"] is None
    assert metrics["tpot_seconds"] is None  # needs first-token timing
    assert metrics["tokens_per_second"] == 2.0  # 8 / total 4.0


def test_zero_output_tokens_has_no_throughput() -> None:
    collector = MetricsCollector(clock=_clock([0.0, 1.0]), rss_bytes=_fixed_rss(10))
    collector.start()
    metrics = collector.finish(output_tokens=0)
    assert metrics["tokens_per_second"] is None
    assert metrics["tpot_seconds"] is None


def test_marks_before_start_raise() -> None:
    collector = MetricsCollector(clock=_clock([0.0]), rss_bytes=_fixed_rss(10))
    with pytest.raises(RuntimeError):
        collector.mark_first_token()
    with pytest.raises(RuntimeError):
        collector.finish(output_tokens=1)
