"""Pure helpers for the Stage 9B streaming TTFT measurement (no model, no network).

These functions turn raw wall-clock stamps from a genuine streaming run (start / first-token /
end) plus the generated-token count into the schema metrics. They are kept separate from the
runner so the metric math is unit-testable with **fake timings only** — no torch/transformers
import here. See ``docs/MEASUREMENT_DESIGN.md`` (streaming TTFT) and ``docs/MEASUREMENT_RUNS.md``.

TTFT is the elapsed time from just before generation to the **first new token observed by the
streamer** — never estimated from total runtime. ``generation_seconds`` is the full generate
window (start→end); decode time is ``generation_seconds − ttft_seconds`` and
``tpot_seconds = (generation_seconds − ttft_seconds) / (output_tokens − 1)``.
"""

from __future__ import annotations

STREAM_NOTE = (
    "streaming TTFT measurement via TextIteratorStreamer (real first-token observation); "
    "supersedes Stage 5B for TTFT/TPOT interpretation. Stage 5B remains valid for "
    "non-streaming total-runtime/throughput evidence."
)


def make_run_id(prompt_id: str, repeat: int) -> str:
    """Stable, deterministic run id for a streaming run (repeat encoded as r{n})."""
    return f"tfcpu-stream-qwen2_0_5b-{prompt_id}-r{repeat}"


def _round(value: float | None, ndigits: int = 6) -> float | None:
    return None if value is None else round(value, ndigits)


def compute_streaming_metrics(
    t_start: float,
    t_first: float | None,
    t_end: float,
    output_tokens: int | None,
) -> dict[str, float | None]:
    """Compute TTFT / generation / TPOT / throughput from real stream timings.

    ``t_first is None`` means the streamer never yielded a token → TTFT/TPOT stay ``None`` and
    the caller should mark the run unsuccessful (never fabricate a first-token time).
    """
    generation = t_end - t_start
    if t_first is None:
        return {
            "ttft_seconds": None,
            "generation_seconds": _round(generation, 4),
            "tpot_seconds": None,
            "tokens_per_second": _round(_throughput(output_tokens, generation), 4),
            "first_token_observed": False,
        }
    ttft = t_first - t_start
    decode = generation - ttft
    tpot = decode / (output_tokens - 1) if output_tokens and output_tokens > 1 else None
    return {
        "ttft_seconds": _round(ttft),
        "generation_seconds": _round(generation, 4),
        "tpot_seconds": _round(tpot),
        "tokens_per_second": _round(_throughput(output_tokens, generation), 4),
        "first_token_observed": True,
    }


def _throughput(output_tokens: int | None, generation: float | None) -> float | None:
    if not output_tokens or output_tokens <= 0 or not generation or generation <= 0:
        return None
    return output_tokens / generation


def mmm(values: list[float]) -> dict[str, float | None]:
    """min / mean / max over a list of floats (None-safe; empty → all None)."""
    clean = [v for v in values if v is not None]
    if not clean:
        return {"min": None, "mean": None, "max": None, "n": 0}
    return {
        "min": round(min(clean), 4),
        "mean": round(sum(clean) / len(clean), 4),
        "max": round(max(clean), 4),
        "n": len(clean),
    }
