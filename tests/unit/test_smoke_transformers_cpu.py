"""Unit tests for the transformers-CPU smoke helpers (no model load, no network)."""

from __future__ import annotations

import json

from ex05_airllm import smoke_transformers_cpu as s


def test_build_result_has_required_keys() -> None:
    result = s.build_result()
    for key in (
        "model_id",
        "backend",
        "device",
        "prompt",
        "start_timestamp",
        "end_timestamp",
        "total_runtime_seconds",
        "load_seconds",
        "generation_seconds",
        "peak_rss_mb",
        "success",
        "failure_reason",
        "output_text",
        "output_tokens_est",
    ):
        assert key in result
    assert result["model_id"] == "Qwen/Qwen2-0.5B"
    assert result["backend"] == "transformers"
    assert result["device"] == "cpu"
    assert result["success"] is False  # default until a real run proves otherwise


def test_build_result_overrides() -> None:
    result = s.build_result(success=True, output_text="ok", output_tokens_est=3)
    assert result["success"] is True
    assert result["output_text"] == "ok"
    assert result["output_tokens_est"] == 3


def test_write_json_roundtrip(tmp_path) -> None:
    path = tmp_path / "td" / "out.json"
    s.write_json(path, {"x": 1, "ok": True})
    assert json.loads(path.read_text(encoding="utf-8")) == {"x": 1, "ok": True}


def test_peak_rss_mb_is_positive() -> None:
    assert s.peak_rss_mb() > 0
