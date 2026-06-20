"""Stage 6A — analyze committed measurement evidence (no model runs, no downloads).

Reads the Stage 5B Transformers CPU `summary.csv` (+ the AirLLM failure JSONs via
``analysis_stats``) and writes analysis JSON, a markdown report, and plain-matplotlib figures.
AirLLM is summarized as a negative result; nothing here implies AirLLM succeeded. All inputs are
already-committed data — this script computes, it does not run any model.

Run: ``uv run python -m ex05_airllm.analyze_measurements``.
"""

from __future__ import annotations

import json
from pathlib import Path
from statistics import mean
from typing import Any

from ex05_airllm.analysis_stats import (
    PROMPT_ORDER,
    airllm_failure_summary,
    build_report_markdown,
    default_airllm_entries,
    load_rows,
    per_prompt_means,
    summary_stats,
    vals,
)
from ex05_airllm.cost_model import estimate

_REPO = Path(__file__).resolve().parents[2]
ANALYSIS_DIR = _REPO / "results" / "analysis"
FIGURES_DIR = _REPO / "figures"
REPORTS_DIR = _REPO / "reports"


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False, default=str), encoding="utf-8")


def _bar(
    labels: list[str], values: list[Any], title: str, ylabel: str, path: Path
) -> None:  # pragma: no cover
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots()
    ax.bar(labels, values)
    ax.set_title(title)
    ax.set_ylabel(ylabel)
    fig.autofmt_xdate(rotation=20)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def _breakeven(cost: dict, path: Path) -> None:  # pragma: no cover
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    requests = list(range(0, 2001, 100))
    hardware = float(cost["assumptions"]["hardware_cost_usd"])
    local = [hardware + n * cost["per_run_local_electricity_usd"] for n in requests]
    api = [n * cost["per_run_api_cost_usd_estimate"] for n in requests]
    fig, ax = plt.subplots()
    ax.plot(requests, local, label="On-Prem (CPU electricity, assumed)")
    ax.plot(requests, api, label="External API (assumed pricing)")
    ax.set_xlabel("requests")
    ax.set_ylabel("cumulative USD (assumption-based)")
    ax.set_title("Break-even estimate - illustrative, NOT verified pricing")
    ax.legend()
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def _figures(per_prompt: dict, cost: dict) -> None:  # pragma: no cover
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    labels = list(PROMPT_ORDER)
    suffix = "(Qwen2-0.5B, Transformers CPU)"
    _bar(
        labels,
        [per_prompt[p]["mean_runtime_seconds"] for p in labels],
        f"Mean runtime by prompt {suffix}",
        "seconds",
        FIGURES_DIR / "transformers_cpu_runtime_by_prompt.png",
    )
    _bar(
        labels,
        [per_prompt[p]["mean_tokens_per_second"] for p in labels],
        f"Mean throughput by prompt {suffix}",
        "tokens/sec",
        FIGURES_DIR / "transformers_cpu_throughput_by_prompt.png",
    )
    _bar(
        labels,
        [per_prompt[p]["mean_peak_ram_mb"] for p in labels],
        f"Mean peak RAM by prompt {suffix}",
        "MB",
        FIGURES_DIR / "transformers_cpu_peak_ram_by_prompt.png",
    )
    _breakeven(cost, FIGURES_DIR / "cost_break_even_estimate.png")


def main() -> int:  # pragma: no cover - reads committed data, writes tables/figures
    rows = load_rows()
    ok = [r for r in rows if r.get("success") == "True"]
    stats = summary_stats(rows)
    per_prompt = per_prompt_means(rows)
    airllm = airllm_failure_summary(default_airllm_entries())
    cost = estimate(
        stats["metrics"]["total_runtime_seconds"]["mean"] or 0.0,
        mean(vals(ok, "input_tokens_est")) if ok else 0.0,
        stats["metrics"]["output_tokens"]["mean"] or 0.0,
    )
    _write_json(
        ANALYSIS_DIR / "transformers_cpu_qwen2_0_5b_summary_stats.json",
        {**stats, "per_prompt": per_prompt},
    )
    _write_json(ANALYSIS_DIR / "airllm_failure_summary.json", airllm)
    _write_json(ANALYSIS_DIR / "cost_energy_assumptions.json", cost["assumptions"])
    _write_json(ANALYSIS_DIR / "cost_energy_estimate.json", cost)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    (REPORTS_DIR / "measurement_summary.md").write_text(
        build_report_markdown(stats, per_prompt, airllm, cost), encoding="utf-8"
    )
    _figures(per_prompt, cost)
    done = f"{stats['success_count']}/{stats['run_count']}"
    print(f"analysis complete: {done} runs; figures + tables written")
    return 0


if __name__ == "__main__":  # pragma: no cover
    import sys

    sys.exit(main())
