"""Unit tests for the smoke-probe helpers (no model load, no network)."""

from __future__ import annotations

import json

from ex05_airllm import smoke_airllm as s

_REQUIRED_KEYS = (
    "model_id",
    "backend",
    "device",
    "prompt",
    "start_timestamp",
    "end_timestamp",
    "total_runtime_seconds",
    "peak_rss_mb",
    "success",
    "failure_reason",
    "output_text",
)


def test_build_smoke_result_has_required_keys() -> None:
    result = s.build_smoke_result()
    for key in _REQUIRED_KEYS:
        assert key in result
    assert result["model_id"] == "Qwen/Qwen2-0.5B"
    assert result["device"] == "cpu"
    assert result["success"] is False  # default until a real run proves otherwise


def test_build_smoke_result_overrides() -> None:
    result = s.build_smoke_result(success=True, output_text="hi", failure_reason="")
    assert result["success"] is True
    assert result["output_text"] == "hi"


def test_write_json_roundtrip(tmp_path) -> None:
    path = tmp_path / "sub" / "out.json"
    s.write_json(path, {"a": 1, "ok": True})
    loaded = json.loads(path.read_text(encoding="utf-8"))
    assert loaded == {"a": 1, "ok": True}


def test_peak_rss_mb_is_positive() -> None:
    assert s.peak_rss_mb() > 0
