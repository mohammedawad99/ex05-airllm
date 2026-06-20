# Measurement Design — Stage 2A

> The measurement architecture for the experiment: what we measure, how results are shaped,
> and the rules that keep every number reproducible. This is **design**, not data.

## 1. Status

- **Stage 2A design only** — no runner, plotter, or cost model implemented yet.
- **No model selected** — the final model is chosen in Stage 2B (after this design is approved).
- **No model downloaded**; **no benchmark run**; **no inference performed.**
- Calibrated to the measured environment (`docs/HARDWARE.md` §B): CPU-only, ~11.24 GiB RAM,
  NVMe-backed 933 GB disk; GPU only via optional Windows-native DirectML (`GPU_FEASIBILITY.md`).

## 2. Measurement goals

Compare the **same task** across configurations and explain *where the time/memory goes*:

1. **Baseline direct run** — load the chosen model the naïve way (HF `transformers`, and/or
   Ollama) and record what happens, **including expected OOM/slowdown** on ~11 GiB.
2. **AirLLM CPU run** — the same task via AirLLM layer-wise loading (`device='cpu'`,
   uncompressed), the project's main path (ADR-0011).
3. **Quantization comparison** — ≥2 precisions (e.g. FP16 vs GGUF Q8/Q4 on the CPU route;
   AirLLM `compression` only if a CUDA path is ever available — see R-QUANT-CPU).
4. **Optional Windows DirectML GPU baseline/extension** — a small GPU-vs-CPU comparison on
   Windows-native Python 3.11 (`GPU_FEASIBILITY.md` §3d); supporting, not the core result.

## 3. Metrics

| metric | definition | primary source |
| --- | --- | --- |
| **TTFT** | time from request to first output token (prefill + KV-cache build) | Python monotonic timer around generate/stream |
| **TPOT / ITL** | mean time per output token after the first (decode/inter-token latency) | timer over streamed tokens |
| **tokens/sec** | throughput = output_tokens / decode_time | derived |
| **total runtime** | wall-clock for the whole run | `time.perf_counter()` |
| **peak RAM** | max resident memory during the run (MB) | `psutil` (RSS sampling) + `resource.getrusage` |
| **peak VRAM / DirectML GPU memory** | GPU memory if a GPU backend is used (MB) | DirectML/host tooling; `N/A_WITH_RATIONALE` for CPU/WSL runs |
| **disk read/write / shard I/O** | bytes read/written during AirLLM layer streaming (MB) | `psutil.disk_io_counters()` deltas / proc IO |
| **estimated energy** | `avg_power_W × runtime_s / 3.6e6` (kWh), labelled *estimate* | power assumptions in `config/` (see COSTS.md) |
| **qualitative output quality** | short rubric + sample outputs per config | persisted sample text |

All timing uses monotonic clocks; instrumentation must be light enough not to distort the
measurement (a stated risk, §8).

## 4. Result schema

> **Stage 5A — implemented & tested (no inference run):** the schema is a typed
> `pydantic` model `src/ex05_airllm/result_schema.py::MeasurementResult` (optional metrics
> default to `None`, `success` defaults to `False` — never a fake value). Timing/memory come
> from `metrics.py::MetricsCollector` (injectable clock + RSS, unit-tested with a controlled
> clock); records are persisted by `result_writer.py` (`write_json` / `append_csv`, stable
> header). Prompts: `prompts.py`; reproducibility metadata: `env.py` (no secrets/private paths).
>
> **Stage 5B — these powered a real 6-run Transformers CPU measurement** on the local Qwen2-0.5B
> (`run_transformers_cpu_measurement.py` → `results/measurements/transformers_cpu_qwen2_0_5b/`;
> see `docs/MEASUREMENT_RUNS.md`). TTFT recorded `None` (no streaming hook), TPOT approximate.

Every run emits one record with these columns (authoritative copy:
`src/ex05_airllm/constants.py::RESULT_SCHEMA_COLUMNS`). Raw per-run JSON in
`results/raw/` (git-ignored); curated rows aggregated to CSV/JSON in `results/`.

| column | type | notes |
| --- | --- | --- |
| `run_id` | str | unique per run |
| `timestamp` | str (ISO-8601) | stamped at run time (not in this design) |
| `environment` | str | `wsl2-ubuntu` \| `windows-native` |
| `backend` | str | `baseline-hf` \| `baseline-ollama` \| `airllm-cpu` \| `directml-gpu` |
| `model_id` | str | HF id / local path (set in Stage 2B) |
| `model_size_label` | str | e.g. `tiny`, `~7B`, `~70B` |
| `quantization` | str | `none` \| `fp16` \| `q8` \| `q4` |
| `prompt_id` | str | references a fixed prompt set |
| `input_tokens_est` | int | estimated input token count |
| `output_tokens` | int | generated token count |
| `ttft_seconds` | float | Time To First Token |
| `tpot_seconds` | float | Time Per Output Token / ITL |
| `tokens_per_second` | float | throughput |
| `total_runtime_seconds` | float | wall-clock |
| `peak_ram_mb` | float | peak resident memory |
| `peak_vram_mb` | float\|null | null/`N/A` when no GPU backend |
| `disk_read_mb` | float | read during run |
| `disk_write_mb` | float | written during run |
| `success` | bool | did the run complete |
| `failure_reason` | str | e.g. `OOM`, `unsupported-arch`, empty if success |
| `notes` | str | free-text observations |

## 5. Experiment matrix draft (categories only — no final model)

| category | purpose | constraint anchor | status |
| --- | --- | --- | --- |
| **Tiny smoke model** | prove the pipeline end-to-end (Stage 3) on CPU/AirLLM | fits easily in ~11 GiB | placeholder — chosen in Stage 2B/3 |
| **Main AirLLM candidate** | the "larger-than-memory" stress model | larger than ~11 GiB RAM; shards fit in 933 GB | **shortlist in Stage 2B** |
| **Optional DirectML small model** | GPU-vs-CPU baseline on Windows Py3.11 | small enough for the iGPU/shared-RAM path | optional |

> Concrete model IDs have a **metadata-verified shortlist** in `docs/MODEL_SELECTION.md`
> (Stage 2B). **Stage 4B revision (ADR-0018):** AirLLM CPU/Qwen2 is blocked, so the **runnable
> measurement path is HF `transformers` CPU on the local `Qwen/Qwen2-0.5B`** (Stage 3D proven).
> The `Qwen/Qwen2-7B` AirLLM main run is **deferred** (`download_approved=false`); AirLLM appears
> as structured **failure evidence**, not a successful run. See `docs/EXPERIMENT_REVISION.md`.

## 6. Measurement tools

- **Python timers** — `time.perf_counter()` / monotonic for TTFT, TPOT, total runtime.
- **`psutil`** — RSS for peak RAM; `disk_io_counters()` for read/write deltas.
- **`resource`** (Linux/WSL) — `getrusage(RUSAGE_SELF).ru_maxrss` as a cross-check on peak RAM.
- **Windows/DirectML observation** — GPU memory via host tooling only when a DirectML run is
  executed; treated as best-effort (§8).
- **Manual observations / screenshots** — *supporting evidence only*, never the primary
  recorded metric.

## 7. Reproducibility rules

- Every run **writes a raw result JSON/CSV** — no metric exists only in console output.
- **No manual-only metrics** — anything reported must come from a written artifact.
- **Configs live in `config/`** (versioned example: `config/experiment.example.toml`); real
  run configs reference a model id chosen in Stage 2B.
- **Outputs live in `results/`** (raw under `results/raw/`, git-ignored; curated tracked).
- **Figures are generated from `results/`** — never hand-drawn (R-NOFAKE).
- Fixed seeds and the exact command/environment are recorded per run.

## 8. Risks (measurement-specific; see also `docs/RISKS.md`)

- **Token counting approximation** — `input_tokens_est` is tokenizer-dependent; document the
  tokenizer used and mark estimates as estimates.
- **AirLLM streaming/token hooks may be limited** — TTFT/TPOT may need a custom streaming
  hook; if per-token timing isn't exposed, fall back to coarser TTFT + average TPOT and say so.
- **DirectML metrics may not expose VRAM cleanly** — GPU memory may be unavailable/approximate;
  record `N/A_WITH_RATIONALE` rather than guessing.
- **CPU quantization differs from bitsandbytes CUDA** — Q4/Q8 via GGUF is not bit-identical to
  bitsandbytes; compare like-for-like and state the route (R-QUANT-CPU).
- **WSL filesystem I/O may differ from host NVMe** — VHDX/9p overhead means disk numbers are
  WSL-relative; attribute carefully (R-WSL-DISK).

## 9. Acceptance criteria for Stage 2B

- A **model shortlist matrix** is prepared (params, format, on-disk size vs 933 GB, RAM vs
  ~11 GiB, AirLLM family support).
- A **final candidate is chosen with written rationale** (ADR), sized to the constraints.
- **No download occurs before the model decision is approved.**
