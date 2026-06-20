"""Unit tests for the ResultWriter (tmp_path only; no model, no network)."""

from __future__ import annotations

import csv
import json

from ex05_airllm.result_schema import MeasurementResult, schema_field_names
from ex05_airllm.result_writer import append_csv, write_json

_BASE = {
    "run_id": "r1",
    "timestamp": "2026-06-20T00:00:00+00:00",
    "environment": "wsl2-ubuntu",
    "backend": "transformers",
    "model_id": "Qwen/Qwen2-0.5B",
    "prompt_id": "os_definition",
    "prompt": "Define an operating system in one short sentence.",
}


def test_write_json_roundtrip_creates_dirs(tmp_path) -> None:
    result = MeasurementResult(**_BASE, success=True, output_tokens=4)
    path = write_json(result, tmp_path / "sub" / "r1.json")
    loaded = json.loads(path.read_text(encoding="utf-8"))
    assert loaded["run_id"] == "r1"
    assert loaded["success"] is True
    assert loaded["ttft_seconds"] is None  # unavailable stays null, not a fake 0


def test_failure_result_is_not_successful(tmp_path) -> None:
    result = MeasurementResult(**_BASE, success=False, failure_reason="OOM")
    loaded = json.loads(write_json(result, tmp_path / "f.json").read_text(encoding="utf-8"))
    assert loaded["success"] is False
    assert loaded["failure_reason"] == "OOM"


def test_append_csv_writes_header_once_and_appends(tmp_path) -> None:
    path = tmp_path / "runs.csv"
    append_csv(MeasurementResult(**{**_BASE, "run_id": "a"}), path)
    append_csv(MeasurementResult(**{**_BASE, "run_id": "b"}), path)
    rows = list(csv.reader(path.read_text(encoding="utf-8").splitlines()))
    assert rows[0] == list(schema_field_names())  # stable header, written once
    assert len(rows) == 3  # header + two data rows
    assert rows[1][0] == "a" and rows[2][0] == "b"


def test_csv_none_is_empty_cell(tmp_path) -> None:
    path = tmp_path / "n.csv"
    append_csv(MeasurementResult(**_BASE), path)
    reader = csv.DictReader(path.read_text(encoding="utf-8").splitlines())
    row = next(reader)
    assert row["ttft_seconds"] == ""  # None renders as empty, not "0" or "None"
