"""Pure analysis helpers for committed measurement evidence (no I/O of models, no network).

Computes summary statistics, per-prompt means, the AirLLM negative-result aggregation, and a
markdown report string. Used by ``analyze_measurements``. AirLLM is summarized as a negative
result; nothing here implies AirLLM succeeded.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from statistics import mean
from typing import Any

_REPO = Path(__file__).resolve().parents[2]
SUMMARY_CSV = _REPO / "results" / "measurements" / "transformers_cpu_qwen2_0_5b" / "summary.csv"
PROMPT_ORDER = ("os_definition", "ai_agent_short", "memory_management_short")
_METRICS = ("total_runtime_seconds", "tokens_per_second", "peak_ram_mb", "output_tokens")
AIRLLM_EVIDENCE = (
    ("3A", "results/stage3_smoke_airllm_qwen2_0_5b.json"),
    ("3B", "results/stage3b_smoke_airllm_qwen2_0_5b_resharded.json"),
    ("3C", "results/stage3c_smoke_airllm_qwen2_0_5b_torch241.json"),
    ("4A", "results/stage4a_smoke_airllm_qwen2_0_5b_patched.json"),
)


def load_rows(path: Path = SUMMARY_CSV) -> list[dict[str, str]]:
    with Path(path).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def vals(rows: list[dict[str, str]], key: str) -> list[float]:
    return [float(r[key]) for r in rows if r.get(key, "") not in ("", "None")]


def _mmm(values: list[float]) -> dict[str, Any]:
    if not values:
        return {"min": None, "mean": None, "max": None, "n": 0}
    return {
        "min": round(min(values), 4),
        "mean": round(mean(values), 4),
        "max": round(max(values), 4),
        "n": len(values),
    }


def summary_stats(rows: list[dict[str, str]]) -> dict[str, Any]:
    ok = [r for r in rows if r.get("success") == "True"]
    return {
        "run_count": len(rows),
        "success_count": len(ok),
        "ttft_note": "TTFT unavailable (None): HF generate() was not token-streamed in this runner",
        "metrics": {m: _mmm(vals(ok, m)) for m in _METRICS},
    }


def per_prompt_means(rows: list[dict[str, str]]) -> dict[str, Any]:
    ok = [r for r in rows if r.get("success") == "True"]
    out: dict[str, Any] = {}
    for pid in PROMPT_ORDER:
        sub = [r for r in ok if r.get("prompt_id") == pid]
        out[pid] = {
            "runs": len(sub),
            "mean_runtime_seconds": round(mean(vals(sub, "total_runtime_seconds")), 4)
            if sub
            else None,
            "mean_tokens_per_second": round(mean(vals(sub, "tokens_per_second")), 4)
            if sub
            else None,
            "mean_peak_ram_mb": round(mean(vals(sub, "peak_ram_mb")), 1) if sub else None,
        }
    return out


def airllm_failure_summary(entries: list[tuple[str, Path]]) -> dict[str, Any]:
    items = []
    for stage, path in entries:
        path = Path(path)
        if not path.exists():
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        items.append(
            {
                "stage": stage,
                "file": path.name,
                "success": bool(data.get("success", False)),
                "failure_reason": (data.get("failure_reason") or "")[:160],
            }
        )
    return {
        "attempts": items,
        "attempt_count": len(items),
        "any_success": any(item["success"] for item in items),
        "conclusion": (
            "AirLLM CPU/Qwen2 is blocked in this environment; a negative result, not a success."
        ),
    }


def default_airllm_entries() -> list[tuple[str, Path]]:
    return [(stage, _REPO / rel) for stage, rel in AIRLLM_EVIDENCE]


def _metric_row(name: str, d: dict) -> str:
    return f"| {name} | {d['min']} | {d['mean']} | {d['max']} |"


def _prompt_row(pid: str, v: dict) -> str:
    runtime, throughput, ram = (
        v["mean_runtime_seconds"],
        v["mean_tokens_per_second"],
        v["mean_peak_ram_mb"],
    )
    return f"| {pid} | {v['runs']} | {runtime} | {throughput} | {ram} |"


def build_report_markdown(stats: dict, per_prompt: dict, airllm: dict, cost: dict) -> str:
    head = (
        f"Transformers CPU on Qwen/Qwen2-0.5B — {stats['success_count']}/{stats['run_count']} "
        f"runs succeeded. Small repeatable measurement, **not** a benchmark. {stats['ttft_note']}."
    )
    air_line = (
        f"- attempts: {len(airllm['attempts'])}; any success: "
        f"**{airllm['any_success']}**. {airllm['conclusion']}"
    )
    cost_line = (
        f"- per-run energy ≈ {cost['per_run_energy_kwh']} kWh; local electricity ≈ "
        f"${cost['per_run_local_electricity_usd']}; assumed API ≈ "
        f"${cost['per_run_api_cost_usd_estimate']}. {cost['caveat']}"
    )
    lines = ["# Measurement Summary (generated)", "", head, ""]
    lines += ["| metric | min | mean | max |", "| --- | --- | --- | --- |"]
    lines += [_metric_row(name, stats["metrics"][name]) for name in _METRICS]
    lines += ["", "## Per-prompt means", ""]
    lines += ["| prompt_id | runs | mean_runtime_s | mean_tok/s | mean_peak_ram_mb |"]
    lines += ["| --- | --- | --- | --- | --- |"]
    lines += [_prompt_row(pid, vals_) for pid, vals_ in per_prompt.items()]
    lines += ["", "## AirLLM (negative result)", air_line, ""]
    lines += ["## Cost & energy (assumption-based, illustrative)", cost_line]
    return "\n".join(lines) + "\n"
