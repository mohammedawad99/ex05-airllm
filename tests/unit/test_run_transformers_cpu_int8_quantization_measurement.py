"""Unit tests for the Stage 9C INT8 runner helpers (pure; no torch/transformers, no model)."""

from __future__ import annotations

import csv
import json

import ex05_airllm.run_transformers_cpu_int8_quantization_measurement as ri
from ex05_airllm.quantization_measurement import VARIANT_FP32, VARIANT_INT8, build_record


def test_runner_constants() -> None:
    assert ri.MAX_NEW_TOKENS == 32
    assert ri.REPEATS == 2
    assert len(ri.PROMPT_IDS) == 3


def test_rss_mb_is_positive_float() -> None:
    value = ri._rss_mb()
    assert isinstance(value, float)
    assert value > 0


def _patch_out(monkeypatch, tmp_path):
    monkeypatch.setattr(ri, "OUT_DIR", tmp_path)
    monkeypatch.setattr(ri, "SUMMARY_CSV", tmp_path / "summary.csv")


def test_write_emits_json_and_csv_with_single_header(monkeypatch, tmp_path) -> None:
    _patch_out(monkeypatch, tmp_path)
    rec1 = build_record(VARIANT_FP32, "os_definition", 1, success=True, tokens_per_second=4.8)
    rec2 = build_record(VARIANT_INT8, "os_definition", 1, success=True, tokens_per_second=17.3)
    ri._write(rec1, "fp32 text")
    ri._write(rec2, "int8 text")

    saved = json.loads((tmp_path / f"{rec1['run_id']}.json").read_text(encoding="utf-8"))
    assert saved["output_text"] == "fp32 text"
    assert saved["variant"] == VARIANT_FP32

    rows = list(csv.DictReader((tmp_path / "summary.csv").open(newline="", encoding="utf-8")))
    assert len(rows) == 2  # header written exactly once
    assert {r["variant"] for r in rows} == {VARIANT_FP32, VARIANT_INT8}


def test_write_handles_none_values_as_blank(monkeypatch, tmp_path) -> None:
    _patch_out(monkeypatch, tmp_path)
    rec = build_record(VARIANT_FP32, "ai_agent_short", 2, success=False, failure_reason="boom")
    ri._write(rec, "")
    rows = list(csv.DictReader((tmp_path / "summary.csv").open(newline="", encoding="utf-8")))
    assert rows[0]["failure_reason"] == "boom"
    assert rows[0]["tokens_per_second"] == ""  # None serialized to blank
