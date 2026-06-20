"""Unit tests for the Stage 11A analysis pipeline (pure read/compute; no model, no network)."""

from __future__ import annotations

from ex05_airllm.analysis_pipeline import (
    _col,
    _mean,
    baseline_summary,
    build_evidence_summary,
    build_roofline,
    read_rows,
)

EVIDENCE_GROUPS = (
    "5B_baseline_transformers_cpu",
    "9B_streaming_ttft_tpot",
    "9C_dynamic_int8",
    "10A_gguf_q8_q4",
    "10B_large_model_pressure",
)


def test_read_rows_reads_a_csv(tmp_path) -> None:
    csv = tmp_path / "s.csv"
    csv.write_text("a,b\n1,2\n3,4\n", encoding="utf-8")
    rows = read_rows(csv)
    assert rows == [{"a": "1", "b": "2"}, {"a": "3", "b": "4"}]


def test_col_filters_failures_and_blanks() -> None:
    rows = [
        {"success": "True", "tokens_per_second": "5.0"},
        {"success": "False", "tokens_per_second": "9.9"},  # excluded: not successful
        {"success": "True", "tokens_per_second": ""},  # excluded: blank
        {"success": "True", "tokens_per_second": "None"},  # excluded: sentinel
        {"success": True, "tokens_per_second": "7.0"},  # bool True accepted
    ]
    assert _col(rows, "tokens_per_second") == [5.0, 7.0]
    assert _mean([5.0, 7.0]) == 6.0
    assert _mean([]) is None


def test_baseline_summary_means() -> None:
    rows = [
        {
            "success": "True",
            "total_runtime_seconds": "4",
            "tokens_per_second": "5",
            "peak_ram_mb": "100",
            "output_tokens": "10",
            "ttft_seconds": "0.4",
            "tpot_seconds": "0.2",
        },
        {
            "success": "True",
            "total_runtime_seconds": "6",
            "tokens_per_second": "7",
            "peak_ram_mb": "200",
            "output_tokens": "20",
            "ttft_seconds": "0.6",
            "tpot_seconds": "0.2",
        },
    ]
    out = baseline_summary(rows)
    assert out["runs"] == 2
    assert out["mean_total_runtime_seconds"] == 5.0
    assert out["mean_tokens_per_second"] == 6.0
    assert out["mean_ttft_seconds"] == 0.5


def test_build_evidence_summary_has_five_groups_from_committed_data() -> None:
    ev = build_evidence_summary()
    for group in EVIDENCE_GROUPS:
        assert group in ev, group
    assert ev["10B_large_model_pressure"]["failure_class"] == "memory_budget_exceeded"
    assert "Cannot allocate memory" in (ev["10B_large_model_pressure"].get("error") or "")
    assert set(ev["10A_gguf_q8_q4"]["variants"]) == {"q8_0", "q4_k_m"}
    assert any("not cross-comparable" in n for n in ev["notes"])


def test_build_roofline_covers_all_five_groups_and_labels_qualitative() -> None:
    ev = {
        "5B_baseline_transformers_cpu": {"mean_tokens_per_second": 5.0, "mean_peak_ram_mb": 4000.0},
        "9B_streaming_ttft_tpot": {"mean_ttft_seconds": 0.41, "mean_tpot_seconds": 0.19},
    }
    rf = build_roofline(ev)
    assert "Roofline-style qualitative classification" in rf["label"]
    assert set(rf["classifications"]) == {
        "5B_baseline_transformers_cpu",
        "9B_streaming",
        "9C_dynamic_int8",
        "10A_gguf_q4_q8",
        "10B_7b_fp16_direct",
    }
    assert "memory-capacity bound" in rf["classifications"]["10B_7b_fp16_direct"]
