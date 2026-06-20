# Stage 11A — reproducible final-analysis pipeline (reads committed measurements only).
#
# Reads the committed Stage 5B/9B/9C/10A/10B CSV+JSON artifacts and emits a combined evidence
# summary, a Roofline-style qualitative classification, the v2 cost model, and four final figures.
# It NEVER runs a model, downloads, or mutates any raw result file — it only reads/computes and
# writes new analysis JSON + figures. matplotlib only; no seaborn; default colors; no subplots.
# Run: ``uv run python -m ex05_airllm.analysis_pipeline``. See docs/ANALYSIS.md / MEASUREMENT_RUNS.

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from ex05_airllm import gguf_measurement as gguf
from ex05_airllm import large_model_pressure as lmp
from ex05_airllm import quantization_measurement as quant
from ex05_airllm.cost_model import build_cost_model_v2

REPO = Path(__file__).resolve().parents[2]
MEAS = REPO / "results" / "measurements"
ANALYSIS = REPO / "results" / "analysis"
FIGURES = REPO / "figures"
CSV = {
    "5B": MEAS / "transformers_cpu_qwen2_0_5b" / "summary.csv",
    "9B": MEAS / "transformers_cpu_streaming_qwen2_0_5b" / "summary.csv",
    "9C": MEAS / "transformers_cpu_int8_quantization_qwen2_0_5b" / "summary.csv",
    "10A": MEAS / "gguf_quantization_qwen2_5_0_5b" / "summary.csv",
    "10B": MEAS / "large_model_pressure_qwen2_5_7b" / "summary.csv",
}
_PJSON = "transformers_7b_direct_cpu_baseline_os_definition.json"


def read_rows(path: Path) -> list[dict[str, Any]]:
    """Read a committed summary CSV into dict rows (no mutation, no model, no network)."""
    with Path(path).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _col(rows: list[dict], key: str) -> list[float]:
    return [
        float(r[key])
        for r in rows
        if r.get("success") in (True, "True") and r.get(key) not in (None, "", "None")
    ]


def _mean(values: list[float]) -> float | None:
    return round(sum(values) / len(values), 4) if values else None


def baseline_summary(rows: list[dict]) -> dict[str, Any]:
    """Mean runtime/throughput/RAM/tokens/TTFT/TPOT over successful rows (5B/9B columns)."""
    keys = (
        "total_runtime_seconds",
        "tokens_per_second",
        "peak_ram_mb",
        "output_tokens",
        "ttft_seconds",
        "tpot_seconds",
    )
    out: dict[str, Any] = {"runs": len([r for r in rows if r.get("success") in (True, "True")])}
    for k in keys:
        out[f"mean_{k}"] = _mean(_col(rows, k))
    return out


def build_evidence_summary() -> dict[str, Any]:
    """Combined five-group evidence summary from committed artifacts (pure read+compute)."""
    pressure = lmp.summarize(read_rows(CSV["10B"]))
    pjson = MEAS / "large_model_pressure_qwen2_5_7b" / _PJSON
    if pjson.exists():
        pressure["error"] = json.loads(pjson.read_text(encoding="utf-8")).get("stdout_tail")
    return {
        "5B_baseline_transformers_cpu": baseline_summary(read_rows(CSV["5B"])),
        "9B_streaming_ttft_tpot": baseline_summary(read_rows(CSV["9B"])),
        "9C_dynamic_int8": quant.comparison_summary(read_rows(CSV["9C"])),
        "10A_gguf_q8_q4": gguf.summarize(read_rows(CSV["10A"])),
        "10B_large_model_pressure": pressure,
        "notes": [
            "9C dynamic INT8 (Transformers) and 10A GGUF Q8/Q4 (llama.cpp) are SEPARATE "
            "quantization experiments on different models/runtimes — not cross-comparable.",
            "10B is a guarded memory-pressure structured negative, NOT a full 7B benchmark; "
            "AirLLM remains blocked/not evidenced.",
        ],
    }


def build_roofline(evidence: dict[str, Any]) -> dict[str, Any]:
    """Roofline-style qualitative classification from measured evidence (not a HW roofline)."""
    return {
        "label": "Roofline-style qualitative classification from measured evidence (not a formal "
        "hardware roofline benchmark); throughput/TTFT anchors in final_evidence_summary.json",
        "classifications": {
            "5B_baseline_transformers_cpu": "memory/CPU constrained, moderate throughput",
            "9B_streaming": "prefill latency visible (TTFT); decode TPOT stable",
            "9C_dynamic_int8": "speed up, quality regresses; small RAM savings (Linear-only)",
            "10A_gguf_q4_q8": "memory footprint improves with Q4 at near-equal throughput",
            "10B_7b_fp16_direct": "memory-capacity bound; budget exceeded before generation",
        },
    }


def _write_json(path: Path, data: Any) -> None:  # pragma: no cover - file IO
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False, default=str), encoding="utf-8")


def _ax(title, ylabel):  # pragma: no cover - matplotlib axes (default colors, no subplots)
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots()
    ax.set(title=title, ylabel=ylabel)
    return plt, fig, ax


def _save(plt, fig, name) -> None:  # pragma: no cover - finalize one figure
    fig.tight_layout()
    fig.savefig(FIGURES / name)
    plt.close(fig)


def _figures(evidence: dict) -> None:  # pragma: no cover - bar figures from measured evidence
    FIGURES.mkdir(parents=True, exist_ok=True)
    q9 = evidence["9C_dynamic_int8"]
    g10 = evidence["10A_gguf_q8_q4"]["variants"]
    var = [q9["fp32_reference"], q9["int8_dynamic"], g10["q8_0"], g10["q4_k_m"]]
    tps = [d["mean_tokens_per_second"] for d in var]
    plt, fig, ax = _ax(
        "Quantization tok/s + peak RAM - HF vs llama.cpp (different runtimes, NOT comparable)",
        "tokens/sec (peak RAM MB labelled)",
    )
    bars = ax.bar(["fp32 HF", "int8 HF", "q8_0 gguf", "q4_k_m gguf"], tps)
    for bar, d in zip(bars, var, strict=False):
        ax.text(bar.get_x(), bar.get_height(), f"{d['mean_peak_ram_mb']:.0f}MB")
    _save(plt, fig, "final_quantization_speed_ram.png")
    ttfts = _col(read_rows(CSV["9B"]), "ttft_seconds")
    plt, fig, ax = _ax("Streaming TTFT per run (Qwen2-0.5B, Transformers CPU)", "TTFT seconds")
    ax.bar([f"run{i + 1}" for i in range(len(ttfts))], ttfts)
    _save(plt, fig, "final_ttft_tpot.png")
    plt, fig, ax = _ax("Roofline-style tok/s by stage (10B OOM at load=0)", "tokens/sec")
    ax.bar(["5B fp32", "9C int8", "10A q4", "10B 7B"], [tps[0], tps[1], tps[3], 0])
    _save(plt, fig, "final_roofline_classification.png")


def write_cost_artifacts() -> int:  # pragma: no cover - reads committed CSV, writes JSON + figure
    model = build_cost_model_v2(_mean(_col(read_rows(CSV["5B"]), "tokens_per_second")) or 5.0)
    _write_json(ANALYSIS / "cost_model_v2.json", model)
    FIGURES.mkdir(parents=True, exist_ok=True)
    sc = model["scenarios"]
    reqs = [s["requests_per_month"] for s in sc]
    series = {
        "Local amortized (CAPEX+elec)": [s["amortized_local_usd"] for s in sc],
        "Local electricity-only": [s["electricity_only_local_usd"] for s in sc],
    }
    for m in model["assumptions"]["api_prices_usd_per_1m"]:
        series[f"API {m} (assumed)"] = [s["api_usd"][m] for s in sc]
    plt, fig, ax = _ax(
        "Cost model v2 break-even - assumption-based, NOT guaranteed pricing",
        "monthly USD (dated assumptions)",
    )
    for label, ys in series.items():
        ax.loglog(reqs, ys, marker="o", label=label)
    ax.set_xlabel("requests per month")
    ax.legend()
    fig.tight_layout()
    fig.savefig(FIGURES / "final_cost_break_even.png")
    plt.close(fig)
    return 0


def main() -> int:  # pragma: no cover - writes all Stage 11A analysis artifacts from committed data
    evidence = build_evidence_summary()
    _write_json(ANALYSIS / "final_evidence_summary.json", evidence)
    _write_json(ANALYSIS / "roofline_classification.json", build_roofline(evidence))
    _figures(evidence)
    write_cost_artifacts()
    print("analysis_pipeline complete: evidence + roofline + cost JSON + 4 figures written")
    return 0


if __name__ == "__main__":  # pragma: no cover
    import sys

    sys.exit(main())
