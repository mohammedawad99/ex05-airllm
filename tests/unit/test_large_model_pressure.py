"""Unit tests for Stage 10B large-model pressure helpers (pure; no model, no network)."""

from __future__ import annotations

import pytest

from ex05_airllm.large_model_pressure import (
    ATTEMPT_TYPE,
    CACHE_SNAPSHOT_MISSING,
    CHILD_MEMORY_LIMIT_MB,
    MEMORY_BUDGET_EXCEEDED,
    MEMORY_GUARD_UNAVAILABLE,
    MODEL_ID,
    RECORD_COLUMNS,
    build_record,
    classify_outcome,
    find_local_snapshot,
    is_memory_budget_signature,
    output_preview,
    summarize,
    truncate_tail,
    validate_row,
)


def test_classify_success() -> None:
    assert classify_outcome(0, False, True) == (True, None)


def test_classify_oom_killed_negative_returncode() -> None:
    # SIGKILL from the OOM killer surfaces as returncode -9
    assert classify_outcome(-9, False, False) == (False, "oom_or_killed")


def test_classify_timeout() -> None:
    assert classify_outcome(None, True, False) == (False, "timeout_or_thrash")


def test_classify_nonzero_and_incomplete() -> None:
    assert classify_outcome(3, False, False) == (False, "load_error_or_nonzero_exit")
    assert classify_outcome(0, False, False) == (False, "incomplete_no_generation")
    assert classify_outcome(None, False, False) == (False, "no_returncode")


def test_classify_memory_budget_exceeded_from_output() -> None:
    # The guarded child raises at the RLIMIT_AS cap -> nonzero exit + a memory signature in output.
    assert classify_outcome(3, False, False, "Traceback ... MemoryError") == (
        False,
        MEMORY_BUDGET_EXCEEDED,
    )
    assert classify_outcome(1, False, False, "OSError: [Errno 12] Cannot allocate memory") == (
        False,
        MEMORY_BUDGET_EXCEEDED,
    )
    assert classify_outcome(1, False, False, "RuntimeError: out of memory") == (
        False,
        MEMORY_BUDGET_EXCEEDED,
    )
    # A nonzero exit without a memory signature stays a plain load error.
    assert classify_outcome(3, False, False, "ValueError: bad config") == (
        False,
        "load_error_or_nonzero_exit",
    )
    # A signal kill (negative returncode) is oom_or_killed even if memory text is present.
    assert classify_outcome(-9, False, False, "MemoryError") == (False, "oom_or_killed")
    # Success path is unaffected by extra output text.
    assert classify_outcome(0, False, True, "MemoryError noise") == (True, None)


def test_is_memory_budget_signature() -> None:
    assert is_memory_budget_signature("here is a MemoryError trace")
    assert is_memory_budget_signature("Cannot allocate memory")
    assert is_memory_budget_signature("std::bad_alloc")
    assert not is_memory_budget_signature("clean output")
    assert not is_memory_budget_signature(None)


def test_truncate_tail_keeps_last_chars() -> None:
    assert truncate_tail(None) == ""
    assert truncate_tail("short") == "short"
    long = "x" * 5000
    out = truncate_tail(long, limit=100)
    assert out.startswith("…") and len(out) == 101


def test_output_preview() -> None:
    assert output_preview(None) == ""
    assert output_preview("  a\n b ") == "a b"
    assert output_preview("y" * 200, limit=10).endswith("…")


def test_build_record_negative_sets_structured_flag() -> None:
    rec = build_record(
        success=False,
        failure_class="oom_or_killed",
        timestamp="t",
        download_completed=True,
        load_completed=False,
        generation_completed=False,
    )
    assert rec["model_id"] == MODEL_ID and rec["attempt_type"] == ATTEMPT_TYPE
    assert rec["success"] is False and rec["structured_negative_result"] is True
    assert rec["failure_class"] == "oom_or_killed"


def test_validate_row_negative_ok_and_success_requires_preview() -> None:
    neg = build_record(
        success=False,
        failure_class="oom_or_killed",
        download_completed=True,
        generation_completed=False,
    )
    validate_row(neg)  # ok
    bad_success = build_record(success=True, failure_class=None, generation_completed=False)
    with pytest.raises(ValueError):
        validate_row(bad_success)
    good_success = build_record(
        success=True,
        failure_class=None,
        generation_completed=True,
        output_preview="hi",
    )
    validate_row(good_success)  # ok


def test_cache_snapshot_missing_constant() -> None:
    assert CACHE_SNAPSHOT_MISSING == "cache_snapshot_missing"


def test_guard_constants() -> None:
    assert CHILD_MEMORY_LIMIT_MB == 13312  # 13 GiB address-space budget (< ~15.24 GB 7B fp16)
    assert MEMORY_GUARD_UNAVAILABLE == "memory_guard_unavailable"
    assert MEMORY_BUDGET_EXCEEDED == "memory_budget_exceeded"


def test_schema_includes_guard_columns() -> None:
    assert "local_snapshot_found" in RECORD_COLUMNS
    assert "child_memory_limit_mb" in RECORD_COLUMNS
    rec = build_record(
        success=False,
        failure_class=MEMORY_BUDGET_EXCEEDED,
        local_snapshot_found=True,
        child_memory_limit_mb=CHILD_MEMORY_LIMIT_MB,
        generation_completed=False,
    )
    assert rec["local_snapshot_found"] is True
    assert rec["child_memory_limit_mb"] == CHILD_MEMORY_LIMIT_MB


def test_validate_row_allows_guarded_memory_negatives() -> None:
    for failure_class in (MEMORY_BUDGET_EXCEEDED, MEMORY_GUARD_UNAVAILABLE):
        row = build_record(
            success=False,
            failure_class=failure_class,
            local_snapshot_found=True,
            child_memory_limit_mb=CHILD_MEMORY_LIMIT_MB,
            generation_completed=False,
        )
        validate_row(row)  # guarded structured negative result is valid


def test_helper_module_has_no_heavy_deps() -> None:
    # The pure helper must never pull torch/transformers into its namespace (no model, no net).
    import ex05_airllm.large_model_pressure as mod

    assert not hasattr(mod, "torch")
    assert not hasattr(mod, "transformers")


def test_runner_resource_guard_and_child_parsing() -> None:
    # Importing the runner stays light (no torch at module scope); guard + parse helpers are pure.
    from ex05_airllm import run_large_model_pressure_baseline as runner

    assert runner._resource_available() is True  # Linux/WSL exposes resource + RLIMIT_AS
    marker = runner._CHILD_MARK + '{"generation_completed": true, "child_maxrss_mb": 12.3}'
    parsed = runner._parse_child("startup noise\n" + marker)
    assert parsed["generation_completed"] is True and parsed["child_maxrss_mb"] == 12.3
    assert runner._parse_child("no marker emitted") == {}


def test_find_local_snapshot_detects_config(tmp_path) -> None:
    snap = tmp_path / "hub" / "models--Qwen--Qwen2.5-7B-Instruct" / "snapshots" / "deadbeef"
    snap.mkdir(parents=True)
    (snap / "config.json").write_text("{}", encoding="utf-8")
    assert find_local_snapshot(tmp_path) == snap


def test_find_local_snapshot_missing_returns_none(tmp_path) -> None:
    # Cache dir present but no config.json under the expected snapshot path -> None.
    (tmp_path / "hub" / "models--Qwen--Qwen2.5-7B-Instruct" / "snapshots").mkdir(parents=True)
    assert find_local_snapshot(tmp_path) is None
    assert find_local_snapshot(tmp_path / "does-not-exist") is None


def test_summarize_single_attempt() -> None:
    rows = [build_record(success=False, failure_class="oom_or_killed", elapsed_seconds=42.0)]
    s = summarize(rows)
    assert s["attempts"] == 1 and s["failure_class"] == "oom_or_killed"
    assert s["elapsed_seconds"] == 42.0
