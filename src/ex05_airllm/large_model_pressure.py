# Pure helpers for the Stage 10B guarded large-model memory-pressure baseline (no model, no net).
#
# A 7B fp16 model (~15 GB) is expected to exceed this machine's RAM/budget, so an OOM/kill/timeout/
# MemoryError is the expected, in-spec structured negative result — not a project failure. These
# helpers classify the child outcome, truncate captured output, and build/validate the result
# record. They are pure (no torch/transformers/network import) and unit-tested with fake data.
# See docs/LARGE_MODEL_PREFLIGHT.md and docs/MEASUREMENT_RUNS.md §11.

from __future__ import annotations

from pathlib import Path
from typing import Any

MODEL_ID = "Qwen/Qwen2.5-7B-Instruct"
BACKEND = "transformers"
ENVIRONMENT = "wsl_cpu"
ATTEMPT_TYPE = "transformers_7b_direct_cpu_baseline"
PROMPT_ID = "os_definition"
TAIL_CHARS = 2000
# Local HF snapshot for the 7B model (offline, no network): hub/<repo>/snapshots/<hash>/config.json
SNAPSHOT_GLOB = "hub/models--Qwen--Qwen2.5-7B-Instruct/snapshots/*/config.json"
CACHE_SNAPSHOT_MISSING = "cache_snapshot_missing"
MEMORY_GUARD_UNAVAILABLE = "memory_guard_unavailable"
MEMORY_BUDGET_EXCEEDED = "memory_budget_exceeded"
# Child address-space cap (RLIMIT_AS). This WSL host has ~11 GiB RAM + ~3 GiB swap (~14 GiB total);
# the 7B fp16 weights are ~15.24 GB, so a 13 GiB budget sits deliberately below the model footprint.
# The guarded child is therefore expected to hit the cap and raise MemoryError ("Cannot allocate
# memory") — a structured negative — instead of letting the OOM killer SIGKILL the parent.
CHILD_MEMORY_LIMIT_MB = 13312
# Substrings (matched case-insensitively) that mark a child memory-exhaustion failure.
MEMORY_SIGNATURES = (
    "memoryerror",
    "cannot allocate memory",
    "out of memory",
    "allocation error",
    "bad_alloc",
)


def find_local_snapshot(cache_root: Path | str) -> Path | None:
    """Resolve the local HF snapshot dir (the one holding ``config.json``) for the 7B model.

    Pure filesystem lookup — **never** touches the network. Returns the snapshot directory if a
    ``config.json`` exists under ``<cache_root>/hub/.../snapshots/<hash>/``, else ``None`` so the
    caller can record ``cache_snapshot_missing`` instead of attempting a (forbidden) re-download.
    """
    for config in sorted(Path(cache_root).glob(SNAPSHOT_GLOB)):
        if config.is_file():
            return config.parent
    return None


RECORD_COLUMNS = (
    "run_id",
    "timestamp",
    "model_id",
    "prompt_id",
    "attempt_type",
    "backend",
    "environment",
    "success",
    "structured_negative_result",
    "failure_class",
    "returncode",
    "timed_out",
    "download_completed",
    "local_snapshot_found",
    "child_memory_limit_mb",
    "load_completed",
    "generation_completed",
    "elapsed_seconds",
    "child_elapsed_seconds",
    "max_new_tokens",
    "peak_rss_mb",
    "child_maxrss_mb",
    "stdout_tail",
    "stderr_tail",
    "output_preview",
    "notes",
)


def truncate_tail(text: str | None, limit: int = TAIL_CHARS) -> str:
    """Keep only the last ``limit`` chars of captured output (one field, never a raw log file)."""
    if not text:
        return ""
    flat = str(text)
    return flat if len(flat) <= limit else "…" + flat[-limit:]


def is_memory_budget_signature(text: str | None) -> bool:
    """True if captured child output carries a memory-exhaustion signature (RLIMIT_AS cap / OOM)."""
    low = (text or "").lower()
    return any(sig in low for sig in MEMORY_SIGNATURES)


def classify_outcome(
    returncode: int | None,
    timed_out: bool,
    child_generation_completed: bool,
    output_text: str | None = "",
) -> tuple[bool, str | None]:
    """Map (returncode, timeout, child flag, captured output) → (success, failure_class).

    success only when the child exited cleanly **and** generation completed. A negative returncode
    means the child was killed by a signal (e.g. SIGKILL -9 from the OOM killer). A nonzero exit
    whose captured output carries a memory signature (the guarded child raising MemoryError /
    "Cannot allocate memory" at the RLIMIT_AS cap) is the guarded ``memory_budget_exceeded``.
    """
    if timed_out:
        return False, "timeout_or_thrash"
    if returncode is None:
        return False, "no_returncode"
    if returncode < 0:
        return False, "oom_or_killed"
    if returncode == 0:
        if not child_generation_completed:
            return False, "incomplete_no_generation"
        return True, None
    if is_memory_budget_signature(output_text):
        return False, MEMORY_BUDGET_EXCEEDED
    return False, "load_error_or_nonzero_exit"


def output_preview(text: str | None, limit: int = 160) -> str:
    """Single-line, length-capped preview of generated text."""
    if not text:
        return ""
    flat = " ".join(str(text).split())
    return flat if len(flat) <= limit else flat[:limit].rstrip() + "…"


def build_record(*, success: bool, failure_class: str | None, **fields: Any) -> dict:
    """Assemble a complete, column-ordered record (pure; fixed fields + None defaults)."""
    rec: dict[str, Any] = dict.fromkeys(RECORD_COLUMNS)
    rec.update(
        run_id=f"{ATTEMPT_TYPE}_{PROMPT_ID}",
        model_id=MODEL_ID,
        prompt_id=PROMPT_ID,
        attempt_type=ATTEMPT_TYPE,
        backend=BACKEND,
        environment=ENVIRONMENT,
        success=success,
        structured_negative_result=(not success),
        failure_class=failure_class,
    )
    rec.update(fields)
    return rec


def validate_row(row: dict[str, Any]) -> None:
    """Sanity-check a result row (raises ValueError on an inconsistent record)."""
    if row.get("model_id") != MODEL_ID:
        raise ValueError(f"bad model_id: {row.get('model_id')}")
    if row.get("attempt_type") != ATTEMPT_TYPE:
        raise ValueError(f"bad attempt_type: {row.get('attempt_type')}")
    success = row.get("success") in (True, "True")
    if success:
        if row.get("generation_completed") not in (True, "True"):
            raise ValueError("success requires generation_completed")
        if not row.get("output_preview"):
            raise ValueError("success requires output_preview")
    else:
        if row.get("structured_negative_result") not in (True, "True"):
            raise ValueError("failure must set structured_negative_result=True")
        if not row.get("failure_class"):
            raise ValueError("failure must set failure_class")


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Tiny summary of the single attempt (descriptive; never fabricated)."""
    row = rows[0] if rows else {}
    return {
        "attempts": len(rows),
        "success": row.get("success"),
        "failure_class": row.get("failure_class"),
        "child_memory_limit_mb": row.get("child_memory_limit_mb"),
        "download_completed": row.get("download_completed"),
        "load_completed": row.get("load_completed"),
        "generation_completed": row.get("generation_completed"),
        "elapsed_seconds": row.get("elapsed_seconds"),
        "note": "7B fp16 direct CPU baseline; OOM/kill/timeout is an expected structured negative.",
    }
