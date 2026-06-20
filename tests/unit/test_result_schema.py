"""Unit tests for the measurement result schema (no model, no network)."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from ex05_airllm.constants import RESULT_SCHEMA_COLUMNS
from ex05_airllm.result_schema import MeasurementResult, schema_field_names

_MINIMAL = {
    "run_id": "r1",
    "timestamp": "2026-06-20T00:00:00+00:00",
    "environment": "wsl2-ubuntu",
    "backend": "transformers",
    "model_id": "Qwen/Qwen2-0.5B",
    "prompt_id": "os_definition",
    "prompt": "Define an operating system in one short sentence.",
}


def test_defaults_do_not_imply_success() -> None:
    result = MeasurementResult(**_MINIMAL)
    assert result.success is False  # never successful unless explicitly set
    assert result.failure_reason == ""
    # unavailable metrics are None, not fake zeros
    for field in ("ttft_seconds", "tokens_per_second", "peak_ram_mb", "output_tokens"):
        assert getattr(result, field) is None


def test_ordered_dict_covers_canonical_columns() -> None:
    ordered = MeasurementResult(**_MINIMAL).ordered_dict()
    for column in RESULT_SCHEMA_COLUMNS:
        assert column in ordered
    assert list(ordered)[: len(RESULT_SCHEMA_COLUMNS)] == list(RESULT_SCHEMA_COLUMNS)


def test_schema_field_names_includes_all_required() -> None:
    names = schema_field_names()
    for field in ("run_id", "prompt", "load_seconds", "generation_seconds", "success"):
        assert field in names


def test_extra_fields_forbidden() -> None:
    with pytest.raises(ValidationError):
        MeasurementResult(**_MINIMAL, surprise="x")
