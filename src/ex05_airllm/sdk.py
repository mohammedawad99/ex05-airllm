"""Thin, stable SDK facade over the existing ex05-airllm modules.

This is a single, documented entry point for the project's *pure* logic — version, prompts,
committed-measurement loading, summary statistics, and the assumption-based cost/energy estimate.
It **delegates** to the existing modules (no business logic is duplicated here) and performs
**no model loading and no network I/O**, so it is safe to import and call when only inspecting
committed results. See ``docs/PLAN.md`` and ``docs/DECISIONS.md`` (ADR-0004).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ex05_airllm import analysis_stats, cost_model, prompts
from ex05_airllm.version import __version__

_RowsOrPath = str | Path | list[dict[str, str]]


def package_version() -> str:
    """Return the installed package version (single source of truth, R-VERSION)."""
    return __version__


def available_prompt_ids() -> tuple[str, ...]:
    """Return the registered deterministic prompt ids, in registry order."""
    return prompts.prompt_ids()


def get_prompt(prompt_id: str) -> prompts.PromptSpec:
    """Return the :class:`PromptSpec` for ``prompt_id`` (delegates to ``prompts``)."""
    return prompts.get_prompt(prompt_id)


def default_summary_path() -> Path:
    """Path to the committed Stage 5B Transformers-CPU summary CSV."""
    return analysis_stats.SUMMARY_CSV


def load_measurement_summary(path: str | Path | None = None) -> list[dict[str, str]]:
    """Load committed measurement rows from ``summary.csv`` (no model/network)."""
    return analysis_stats.load_rows(Path(path) if path is not None else analysis_stats.SUMMARY_CSV)


def _as_rows(rows_or_path: _RowsOrPath | None) -> list[dict[str, str]]:
    if rows_or_path is None or isinstance(rows_or_path, (str, Path)):
        return load_measurement_summary(rows_or_path)
    return rows_or_path


def compute_summary_stats(rows_or_path: _RowsOrPath | None = None) -> dict[str, Any]:
    """Summary stats from rows or a CSV path (delegates to ``analysis_stats``)."""
    return analysis_stats.summary_stats(_as_rows(rows_or_path))


def compute_per_prompt_means(rows_or_path: _RowsOrPath | None = None) -> dict[str, Any]:
    """Per-prompt means from rows or a CSV path (delegates to ``analysis_stats``)."""
    return analysis_stats.per_prompt_means(_as_rows(rows_or_path))


def airllm_failure_summary(
    entries: list[tuple[str, Path]] | None = None,
) -> dict[str, Any]:
    """Aggregate the AirLLM negative-result evidence (never marks success)."""
    return analysis_stats.airllm_failure_summary(
        entries if entries is not None else analysis_stats.default_airllm_entries()
    )


def estimate_cost_energy(
    mean_runtime_seconds: float,
    mean_input_tokens: float,
    mean_output_tokens: float,
    assumptions: dict[str, object] | None = None,
) -> dict[str, object]:
    """Assumption-based per-run energy/cost estimate (delegates to ``cost_model``).

    The result is illustrative under documented assumptions; it is **not** market-verified pricing.
    """
    return cost_model.estimate(
        mean_runtime_seconds, mean_input_tokens, mean_output_tokens, assumptions
    )


__all__ = [
    "package_version",
    "available_prompt_ids",
    "get_prompt",
    "default_summary_path",
    "load_measurement_summary",
    "compute_summary_stats",
    "compute_per_prompt_means",
    "airllm_failure_summary",
    "estimate_cost_energy",
]
