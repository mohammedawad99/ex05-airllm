"""Unit tests for the SDK facade (pure delegation; no models, no network)."""

from __future__ import annotations

import csv

from ex05_airllm import __version__, sdk

_COLS = [
    "success",
    "prompt_id",
    "total_runtime_seconds",
    "tokens_per_second",
    "peak_ram_mb",
    "output_tokens",
]


def _write_csv(path) -> None:
    rows = [
        {
            "success": "True",
            "prompt_id": "os_definition",
            "total_runtime_seconds": "6.0",
            "tokens_per_second": "4.0",
            "peak_ram_mb": "4000.0",
            "output_tokens": "28",
        },
        {
            "success": "True",
            "prompt_id": "ai_agent_short",
            "total_runtime_seconds": "5.0",
            "tokens_per_second": "5.0",
            "peak_ram_mb": "4010.0",
            "output_tokens": "30",
        },
    ]
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=_COLS)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def test_package_version_matches() -> None:
    assert sdk.package_version() == __version__


def test_available_prompt_ids_nonempty() -> None:
    ids = sdk.available_prompt_ids()
    assert isinstance(ids, tuple) and len(ids) >= 1
    # get_prompt delegates and resolves a real spec
    assert sdk.get_prompt(ids[0]).prompt_id == ids[0]


def test_load_and_summary_from_path(tmp_path) -> None:
    csv_path = tmp_path / "summary.csv"
    _write_csv(csv_path)
    rows = sdk.load_measurement_summary(csv_path)
    assert len(rows) == 2
    stats = sdk.compute_summary_stats(csv_path)  # path form
    assert stats["run_count"] == 2 and stats["success_count"] == 2
    stats2 = sdk.compute_summary_stats(rows)  # rows form
    assert stats2["run_count"] == 2
    per = sdk.compute_per_prompt_means(rows)
    assert per["os_definition"]["runs"] == 1


def test_estimate_cost_energy_delegates() -> None:
    out = sdk.estimate_cost_energy(6.0, 9.0, 30.0)
    assert out["per_run_energy_kwh"] > 0
    assert "not current verified market pricing" in out["caveat"]


def test_default_summary_path_and_airllm_summary() -> None:
    assert sdk.default_summary_path().name == "summary.csv"
    air = sdk.airllm_failure_summary([])  # empty entries → no success
    assert air["any_success"] is False
