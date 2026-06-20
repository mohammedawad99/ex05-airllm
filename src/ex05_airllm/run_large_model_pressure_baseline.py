# Stage 10B — guarded Qwen2.5-7B-Instruct Transformers memory-pressure baseline (CPU).
#
# Parent/child design: the parent stays lightweight — it resolves the already-cached model snapshot
# on disk (offline, no network, no re-download), then launches a child subprocess (strict timeout).
# The child applies an explicit address-space cap (resource.setrlimit(RLIMIT_AS, ...),
# CHILD_MEMORY_LIMIT_MB) BEFORE importing torch/transformers, loads the model from that filesystem
# path and attempts ONE tiny generation; the parent writes a structured JSON/CSV even if the child
# hits the budget or is OOM-killed. A 7B fp16 model (~15.24 GB) is expected to exceed the ~13 GiB
# budget here, so a MemoryError/OOM/kill/timeout is an expected structured negative result (not
# AirLLM success, not 100-ready). If the local snapshot/config.json is absent the parent records
# cache_snapshot_missing and stops (no download); if resource is missing it records
# memory_guard_unavailable and stops. No model artifacts are committed; weights live under
# git-ignored .hf_cache/. Run with HF_HOME / HF_HUB_CACHE / TRANSFORMERS_CACHE pointed at .hf_cache:
# `uv run python -m ex05_airllm.run_large_model_pressure_baseline`.

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

from ex05_airllm import large_model_pressure as lmp
from ex05_airllm.prompts import get_prompt

MAX_NEW_TOKENS = 8
CHILD_TIMEOUT_S = 1200
_REPO_ROOT = Path(__file__).resolve().parents[2]
CACHE_ROOT = _REPO_ROOT / ".hf_cache"
OUT_DIR = _REPO_ROOT / "results" / "measurements" / "large_model_pressure_qwen2_5_7b"
SUMMARY_CSV = OUT_DIR / "summary.csv"
RESULT_JSON = OUT_DIR / f"{lmp.ATTEMPT_TYPE}_{lmp.PROMPT_ID}.json"
_CHILD_MARK = "__CHILD_RESULT__"


def _child() -> int:  # pragma: no cover - guarded real 7B load under an address-space cap
    # Apply the RLIMIT_AS budget BEFORE importing torch/transformers so their allocations count
    # against the cap and a blow-up surfaces as MemoryError, not a parent kill.
    try:
        import resource
    except ImportError:  # platform without resource (e.g. Windows): cannot guard -> signal up
        print(_CHILD_MARK + json.dumps({"error": "resource_unavailable", "guard_applied": False}))
        return 5
    limit_bytes = lmp.CHILD_MEMORY_LIMIT_MB * 1024 * 1024
    try:
        resource.setrlimit(resource.RLIMIT_AS, (limit_bytes, limit_bytes))
    except (ValueError, OSError) as exc:
        info = {"error": f"setrlimit_failed: {exc}", "guard_applied": False}
        print(_CHILD_MARK + json.dumps(info))
        return 5

    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    out: dict = {"load_completed": False, "generation_completed": False, "output_preview": ""}
    src = os.environ["EX05_MODEL_PATH"]  # explicit local snapshot dir resolved by the parent
    start = time.perf_counter()
    try:
        tok = AutoTokenizer.from_pretrained(src, local_files_only=True, trust_remote_code=False)
        model = AutoModelForCausalLM.from_pretrained(
            src, local_files_only=True, trust_remote_code=False, torch_dtype=torch.float16
        )
        model.eval()
        out["load_completed"] = True
        msgs = [{"role": "user", "content": get_prompt(lmp.PROMPT_ID).text}]
        text = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
        inputs = tok(text, return_tensors="pt")
        with torch.no_grad():
            gen = model.generate(**inputs, max_new_tokens=MAX_NEW_TOKENS, do_sample=False)
        new = gen[0][inputs["input_ids"].shape[1] :]
        out["generation_completed"] = True
        out["output_preview"] = lmp.output_preview(tok.decode(new, skip_special_tokens=True))
    except Exception as exc:  # noqa: BLE001 - report, never raise raw logs
        out["error"] = f"{type(exc).__name__}: {exc}"[:300]
    out["child_elapsed_seconds"] = round(time.perf_counter() - start, 2)
    out["child_maxrss_mb"] = round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024, 1)
    print(_CHILD_MARK + json.dumps(out))
    return 0 if out["generation_completed"] else 3


def _parse_child(stdout: str) -> dict:
    for line in reversed(stdout.splitlines()):
        if line.startswith(_CHILD_MARK):
            return json.loads(line[len(_CHILD_MARK) :])
    return {}


def _write(record: dict) -> None:
    import csv

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    RESULT_JSON.write_text(json.dumps(record, indent=2, ensure_ascii=False, default=str), "utf-8")
    with SUMMARY_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(lmp.RECORD_COLUMNS), extrasaction="ignore")
        writer.writeheader()
        writer.writerow(
            {k: ("" if record.get(k) is None else record.get(k)) for k in lmp.RECORD_COLUMNS}
        )


def _run_child(model_path: str) -> tuple[int | None, bool, str, str]:  # pragma: no cover
    try:
        proc = subprocess.run(
            [sys.executable, "-m", "ex05_airllm.run_large_model_pressure_baseline", "--child"],
            capture_output=True,
            text=True,
            timeout=CHILD_TIMEOUT_S,
            cwd=str(_REPO_ROOT),
            env={**os.environ, "EX05_MODEL_PATH": model_path},
        )
        return proc.returncode, False, proc.stdout, proc.stderr
    except subprocess.TimeoutExpired as exc:
        out, err = (exc.stdout or ""), (exc.stderr or "")
        dec = lambda v: v.decode(errors="replace") if isinstance(v, bytes) else v  # noqa: E731
        return None, True, dec(out), dec(err)


def _resource_available() -> bool:
    # True if the RLIMIT_AS memory budget can be enforced on the child (stdlib resource; Unix).
    try:
        import resource
    except ImportError:
        return False
    return hasattr(resource, "RLIMIT_AS")


def main() -> int:  # pragma: no cover - resolves local snapshot + guarded child attempt
    if "--child" in sys.argv:
        return _child()
    wall = time.perf_counter()
    fields: dict = {
        "timestamp": datetime.now(UTC).isoformat(),
        "max_new_tokens": MAX_NEW_TOKENS,
        "download_completed": False,
        "load_completed": False,
        "generation_completed": False,
    }
    # Offline resolution: never touches the network, never re-downloads (snapshot already cached).
    snapshot = lmp.find_local_snapshot(CACHE_ROOT)
    if snapshot is None:
        fields["download_completed"] = CACHE_ROOT.exists()
        fields["local_snapshot_found"] = False
        fields["elapsed_seconds"] = round(time.perf_counter() - wall, 2)
        fields["notes"] = (
            "local 7B snapshot/config.json not found; no re-download, model unchanged."
        )
        _write(lmp.build_record(success=False, failure_class=lmp.CACHE_SNAPSHOT_MISSING, **fields))
        print("blocker: local snapshot/config.json not found under", CACHE_ROOT)
        return 1
    fields["download_completed"] = True
    fields["local_snapshot_found"] = True
    fields["child_memory_limit_mb"] = lmp.CHILD_MEMORY_LIMIT_MB
    # No way to enforce the budget -> record an honest guard-unavailable negative; do NOT attempt.
    if not _resource_available():
        fields["elapsed_seconds"] = round(time.perf_counter() - wall, 2)
        fields["notes"] = "resource/RLIMIT_AS unavailable; cannot enforce memory budget; not run."
        rec = lmp.build_record(success=False, failure_class=lmp.MEMORY_GUARD_UNAVAILABLE, **fields)
        _write(rec)
        print("blocker: resource/RLIMIT_AS unavailable; cannot guard child memory budget")
        return 1
    rc, timed_out, out, err = _run_child(str(snapshot))
    child = _parse_child(out)
    success, failure_class = lmp.classify_outcome(
        rc, timed_out, bool(child.get("generation_completed")), f"{out}\n{err}"
    )
    fields.update(
        load_completed=bool(child.get("load_completed")),
        generation_completed=bool(child.get("generation_completed")),
        returncode=rc,
        timed_out=timed_out,
        elapsed_seconds=round(time.perf_counter() - wall, 2),
        child_elapsed_seconds=child.get("child_elapsed_seconds"),
        child_maxrss_mb=child.get("child_maxrss_mb"),
        stdout_tail=lmp.truncate_tail(out),
        stderr_tail=lmp.truncate_tail(err),
        output_preview=child.get("output_preview", ""),
        notes=f"guarded {lmp.CHILD_MEMORY_LIMIT_MB} MiB RLIMIT_AS 7B fp16 CPU baseline; "
        "MemoryError/OOM/kill/timeout is an expected structured negative.",
    )
    _write(lmp.build_record(success=success, failure_class=failure_class, **fields))
    print(f"done: success={success} failure_class={failure_class} rc={rc} timed_out={timed_out}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
