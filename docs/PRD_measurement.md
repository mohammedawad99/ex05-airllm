# PRD — Measurement Subsystem

> Per-mechanism PRD (guidelines §2.3) for the component that records every experiment metric.
> Design only — no runner is implemented in Stage 2. Companion to `docs/MEASUREMENT_DESIGN.md`.

## 1. Purpose

Provide a single, reusable subsystem that wraps any inference run (baseline / AirLLM / DirectML)
and produces **one reproducible result record** per run, so that all comparisons rest on
identically-defined, file-backed numbers (no manual readings).

## 2. Inputs / outputs

- **Inputs:** a run config (model id, backend, environment, quantization, prompt set,
  `max_new_tokens`, seed — see `config/experiment.example.toml`) and a callable that performs the
  generation while exposing first-token and per-token timing hooks.
- **Outputs:** a raw per-run JSON written to `results/raw/` (git-ignored) and an appended row in
  a curated `results/*.csv|json` (tracked). Sample output text is persisted separately for the
  qualitative metric.

## 3. Result schema (authoritative)

The columns are defined once in `src/ex05_airllm/constants.py::RESULT_SCHEMA_COLUMNS` and mirror
`docs/MEASUREMENT_DESIGN.md` §4: `run_id, timestamp, environment, backend, model_id,
model_size_label, quantization, prompt_id, input_tokens_est, output_tokens, ttft_seconds,
tpot_seconds, tokens_per_second, total_runtime_seconds, peak_ram_mb, peak_vram_mb, disk_read_mb,
disk_write_mb, success, failure_reason, notes`. Types per `MEASUREMENT_DESIGN.md` §4.

## 4. Metrics

- **TTFT** (prefill + KV build), **TPOT/ITL** (decode), **tokens/sec**, **total runtime** —
  monotonic Python timers around the generation call / token stream.
- **peak RAM** — `psutil` RSS sampling + `resource.getrusage` cross-check.
- **peak VRAM** — only when a GPU backend is used; otherwise `null` / `N/A_WITH_RATIONALE`.
- **disk read/write** — `psutil.disk_io_counters()` deltas (AirLLM shard streaming).
- **estimated energy** — derived later from `avg_power_watts × runtime` (labelled estimate).
- **qualitative quality** — sample text persisted; scored by a short rubric.

## 5. Validation criteria

- Each run writes a schema-valid record; missing required fields fail validation.
- Re-running the same config reproduces metrics within a documented tolerance (variance noted).
- Timers use monotonic clocks; instrumentation overhead must not materially distort results.
- `success=False` runs still emit a record with a `failure_reason` (e.g. `OOM`).

## 6. No manual-only metrics (hard rule)

Every reported number must originate from a written artifact under `results/`. Console-only or
eyeballed values are **not** acceptable as primary data; screenshots are supporting evidence only.

## 7. Future tests (Stage 3+, TDD)

- Schema validation: a record with all `RESULT_SCHEMA_COLUMNS` passes; a missing column fails.
- Timer math: TTFT/TPOT/throughput derivations from synthetic token timestamps.
- Serialization round-trip: write → read JSON/CSV yields identical values.
- Memory sampler returns a positive peak for a small allocation (mocked where needed).
- All tests mock external dependencies (no model, no network); files stay ≤150 code lines.

## 8. Boundaries

No model download, no inference, and no benchmark are part of this PRD; it specifies the
contract the Stage 3 implementation must satisfy.
