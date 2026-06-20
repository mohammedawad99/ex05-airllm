"""Unit tests for the Stage 10A GGUF runner helpers (pure; no llama_cpp, no model, no network)."""

from __future__ import annotations

import csv
import json

import ex05_airllm.run_gguf_quantization_measurement as rg
from ex05_airllm.gguf_measurement import VARIANT_FILES, build_record


def test_runner_constants() -> None:
    assert rg.MAX_TOKENS == 32
    assert rg.REPEATS == 2
    assert rg.VARIANT_ORDER == ("f16_reference", "q8_0", "q4_k_m")
    assert len(rg.PROMPT_IDS) == 3


def test_rss_mb_is_positive_float() -> None:
    value = rg._rss_mb()
    assert isinstance(value, float)
    assert value > 0


def _patch_out(monkeypatch, tmp_path):
    monkeypatch.setattr(rg, "OUT_DIR", tmp_path)
    monkeypatch.setattr(rg, "SUMMARY_CSV", tmp_path / "summary.csv")


def test_write_emits_json_and_csv_with_single_header(monkeypatch, tmp_path) -> None:
    _patch_out(monkeypatch, tmp_path)
    rec1 = build_record("q8_0", "os_definition", 1, success=True, ttft_seconds=0.4)
    rec2 = build_record("q4_k_m", "os_definition", 1, success=True, ttft_seconds=0.3)
    rg._write(rec1, "hello world")
    rg._write(rec2, "second")

    saved = json.loads((tmp_path / f"{rec1['run_id']}.json").read_text(encoding="utf-8"))
    assert saved["output_text"] == "hello world"
    assert saved["quantization_variant"] == "q8_0"

    rows = list(csv.DictReader((tmp_path / "summary.csv").open(newline="", encoding="utf-8")))
    assert len(rows) == 2  # header written exactly once
    assert {r["quantization_variant"] for r in rows} == {"q8_0", "q4_k_m"}


def test_available_variants_filters_to_present_files(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(rg, "GGUF_DIR", tmp_path)
    (tmp_path / VARIANT_FILES["q8_0"]).write_text("x", encoding="utf-8")
    (tmp_path / VARIANT_FILES["q4_k_m"]).write_text("x", encoding="utf-8")
    # f16 file intentionally absent
    found = rg._available_variants()
    assert [v for v, _ in found] == ["q8_0", "q4_k_m"]
    assert all(path.exists() for _, path in found)


def test_available_variants_empty_when_no_files(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(rg, "GGUF_DIR", tmp_path)
    assert rg._available_variants() == []
