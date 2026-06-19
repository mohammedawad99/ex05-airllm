"""Unit tests for the re-shard preparation helpers (no model load, no network)."""

from __future__ import annotations

import json

from ex05_airllm import prepare_sharded_model as p


def test_build_prepare_record_has_required_keys() -> None:
    record = p.build_prepare_record()
    for key in (
        "stage",
        "model_id",
        "max_shard_size",
        "sharded_dir",
        "index_present",
        "timestamp",
        "success",
        "failure_reason",
    ):
        assert key in record
    assert record["model_id"] == "Qwen/Qwen2-0.5B"
    assert record["success"] is False  # default until a real prepare proves otherwise
    assert record["index_present"] is False


def test_build_prepare_record_overrides() -> None:
    record = p.build_prepare_record(success=True, index_present=True)
    assert record["success"] is True
    assert record["index_present"] is True


def test_write_json_roundtrip(tmp_path) -> None:
    path = tmp_path / "prep.json"
    p.write_json(path, {"k": "v", "n": 2})
    assert json.loads(path.read_text(encoding="utf-8")) == {"k": "v", "n": 2}
