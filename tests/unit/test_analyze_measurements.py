"""Unit tests for measurement analysis (synthetic tmp data; no models, no network)."""

from __future__ import annotations

import csv
import json

from ex05_airllm import analyze_measurements as a
from ex05_airllm.cost_model import estimate

_COLS = [
    "success",
    "prompt_id",
    "total_runtime_seconds",
    "tokens_per_second",
    "peak_ram_mb",
    "output_tokens",
    "input_tokens_est",
]


def _write_csv(path, rows) -> None:
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=_COLS)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def _rows():
    return [
        {
            "success": "True",
            "prompt_id": "os_definition",
            "total_runtime_seconds": "6.0",
            "tokens_per_second": "4.0",
            "peak_ram_mb": "4000.0",
            "output_tokens": "28",
            "input_tokens_est": "9",
        },
        {
            "success": "True",
            "prompt_id": "os_definition",
            "total_runtime_seconds": "5.0",
            "tokens_per_second": "5.0",
            "peak_ram_mb": "4010.0",
            "output_tokens": "30",
            "input_tokens_est": "9",
        },
        {
            "success": "True",
            "prompt_id": "ai_agent_short",
            "total_runtime_seconds": "5.0",
            "tokens_per_second": "5.0",
            "peak_ram_mb": "4020.0",
            "output_tokens": "30",
            "input_tokens_est": "8",
        },
        {
            "success": "False",
            "prompt_id": "memory_management_short",
            "total_runtime_seconds": "0.1",
            "tokens_per_second": "",
            "peak_ram_mb": "",
            "output_tokens": "",
            "input_tokens_est": "",
        },
    ]


def test_summary_stats_counts_and_ranges(tmp_path) -> None:
    csv_path = tmp_path / "summary.csv"
    _write_csv(csv_path, _rows())
    stats = a.summary_stats(a.load_rows(csv_path))
    assert stats["run_count"] == 4
    assert stats["success_count"] == 3  # failed row excluded from metrics
    runtime = stats["metrics"]["total_runtime_seconds"]
    assert runtime["min"] == 5.0 and runtime["max"] == 6.0 and runtime["n"] == 3
    assert "TTFT unavailable" in stats["ttft_note"]


def test_per_prompt_means(tmp_path) -> None:
    csv_path = tmp_path / "summary.csv"
    _write_csv(csv_path, _rows())
    per = a.per_prompt_means(a.load_rows(csv_path))
    assert per["os_definition"]["runs"] == 2
    assert per["os_definition"]["mean_runtime_seconds"] == 5.5  # (6 + 5) / 2
    assert per["memory_management_short"]["runs"] == 0  # only a failed run → no means
    assert per["memory_management_short"]["mean_runtime_seconds"] is None


def test_airllm_summary_never_marks_success(tmp_path) -> None:
    f1 = tmp_path / "a.json"
    f2 = tmp_path / "b.json"
    f1.write_text(
        json.dumps({"success": False, "failure_reason": "AssertionError: index"}), encoding="utf-8"
    )
    f2.write_text(
        json.dumps({"success": False, "failure_reason": "RuntimeError: meta"}), encoding="utf-8"
    )
    summary = a.airllm_failure_summary([("3A", f1), ("3B", f2)])
    assert summary["any_success"] is False
    assert summary["attempt_count"] == 2
    assert len(summary["attempts"]) == 2
    assert all(item["success"] is False for item in summary["attempts"])
    assert "negative result" in summary["conclusion"]


def test_report_markdown_is_honest(tmp_path) -> None:
    csv_path = tmp_path / "summary.csv"
    _write_csv(csv_path, _rows())
    loaded = a.load_rows(csv_path)
    stats = a.summary_stats(loaded)
    per = a.per_prompt_means(loaded)
    airllm = {"attempts": [], "any_success": False, "conclusion": "negative result."}
    cost = estimate(5.5, 9.0, 29.0)
    md = a.build_report_markdown(stats, per, airllm, cost)
    assert "not** a benchmark" in md
    assert "any success: **False**" in md
    assert "assumption" in md.lower()
