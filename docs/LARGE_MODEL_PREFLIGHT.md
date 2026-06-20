# Large-Model Memory-Pressure Preflight — Stage 10B-0

> **Planning/audit only.** No download, no model run, no dependency change, no `uv add`, no
> `pyproject.toml`/`uv.lock` edit happens in this stage. This document verifies hardware/storage
> constraints and decides whether a **Qwen 7B Transformers memory-pressure baseline** is safe to
> *attempt* in a future, explicitly-approved Stage 10B.

## 1. Status

> **Update — Stage 10B executed (2026-06-20).** This preflight has since been acted on under explicit
> approval. The guarded attempt ran and produced a **structured negative result**
> (`failure_class=memory_budget_exceeded`): the `Qwen/Qwen2.5-7B-Instruct` fp16 weights were found in
> the local (git-ignored) HF cache, a child subprocess capped at **13312 MiB** `RLIMIT_AS` began the
> load and hit **`Cannot allocate memory`** (`DefaultCPUAllocator`) **during model load** — before any
> generation (`load_completed=false`, `generation_completed=false`, `returncode=3`, not timed out).
> Evidence: `results/measurements/large_model_pressure_qwen2_5_7b/` (summary.csv + result JSON). This
> **attempts and evidences** the direct large-model (>RAM) pressure baseline as a guarded
> memory-budget structured negative — **not a full benchmark, not a success**. AirLLM stays **blocked /
> not evidenced**; no model artifacts are committed (weights stay git-ignored under `.hf_cache/`). The
> sections below are the original preflight plan, preserved for the record.

- **Large-model memory-pressure baseline: NOT_DONE** *(as written at preflight time; now **ATTEMPTED &
  EVIDENCED** as a structured negative — see the update box above).* At preflight this was a
  feasibility decision, not an execution.
- **HEAD:** `ee038ca`. Working tree clean except ignored artifacts. Model artifacts are git-ignored
  (`.local_models/`, `.hf_cache/`, `*.safetensors`, `*.bin`, `*.gguf`, `*.pt`, `*.pth`).
- **`Qwen2-7B` remains not downloaded / not approved** *(at preflight; Stage 10B later downloaded
  `Qwen/Qwen2.5-7B-Instruct` to the ignored HF cache under explicit approval — never committed).*
  AirLLM remains **blocked / not evidenced**.

## 2. Why this stage exists

The last remaining experimental gap is a **large-model (>RAM) baseline** — the assignment's
"deliberately larger than memory" demonstration. Everything else is measured: a Transformers CPU
baseline (5B), real streaming TTFT (9B), and quantization two ways — dynamic INT8 (9C) and GGUF
Q8/Q4 (10A). This preflight scopes the 7B pressure test **before** committing to a ~15 GB download.

## 3. Current hardware/storage snapshot

Captured 2026-06-20 (WSL2; values are environment-specific, not a benchmark):

| item | value |
| --- | --- |
| OS / kernel | Linux WSL2, `6.6.87.2-microsoft-standard-WSL2`, x86_64 |
| CPU | AMD Ryzen AI 9 HX 370 — 24 logical CPUs (12 cores × 2), AVX-512/VNNI |
| **RAM** | **11 GiB total**, ~9.6 GiB available, **+3 GiB swap** (`free -h`) |
| Disk (`.`) | 1007 GB volume, **924 GB free** (NVMe-backed VHDX) |
| `~/.cache` | same volume (924 GB free) |
| Python / uv | Python 3.12.3 (via `uv run`), uv 0.11.9 |
| local caches | `.local_models/` ≈ 4.1 GB (cached Qwen2-0.5B + GGUF Q8/Q4); `.hf_cache/` n/a |

## 4. Existing measured evidence already completed

- **Stage 5B** Transformers CPU baseline (Qwen2-0.5B, non-streaming) — `transformers_cpu_qwen2_0_5b/`.
- **Stage 9B** streaming **real TTFT/TPOT** (Qwen2-0.5B) — `transformers_cpu_streaming_qwen2_0_5b/`.
- **Stage 9C** dynamic **INT8 vs FP32** (Qwen2-0.5B, Transformers) —
  `transformers_cpu_int8_quantization_qwen2_0_5b/`.
- **Stage 10A** **GGUF Q8_0 vs Q4_K_M** (Qwen2.5-0.5B-Instruct-GGUF, `llama.cpp`) —
  `gguf_quantization_qwen2_5_0_5b/`.
- **AirLLM** — structured **negative result** (blocked), `results/stage3*` / `stage4a*`.

## 5. Candidate large-model baseline

- **Recommended candidate:** `Qwen/Qwen2.5-7B-Instruct` (HF Transformers safetensors, fp16 ≈ **15.2
  GB**), consistent with the Qwen2.5 family used in Stage 10A. `Qwen/Qwen2-7B-Instruct` (the
  originally-shortlisted 7B) is an equivalent alternative — the final pick is confirmed at Stage 10B
  approval time. **Neither is downloaded.**
- **Backend:** HF `transformers`, CPU, offline after the one approved download. This is the genuine
  *memory-pressure* path (full fp16 weights resident), distinct from a GGUF runtime.

## 6. Expected memory-pressure rationale

- fp16 7B weights (~15 GB) **exceed total RAM (11 GiB)** and even RAM+swap (~14 GiB). Loading is
  therefore expected to **OOM** or thrash heavily on swap with extremely slow CPU inference.
- This is **the point**: it demonstrates *why* a 7B model does not fit on this machine and motivates
  layer-streaming/quantization. A successful generation is **not expected and not required** — a
  well-analyzed **OOM/structured negative result** is a valid, in-spec outcome.
- This is **separate** from the GGUF small-model quantization sweep (Stage 10A): a GGUF Q4 7B (~4.5
  GB) would *fit* and run, so it would **not** create memory pressure and would not serve as the
  pressure baseline — it would be a different (quantized-large) experiment, only if separately
  approved.

## 7. Risks

- **OOM / process kill** during load (most likely) — must be caught as a structured negative result.
- **Heavy swap thrashing** → multi-minute or stuck inference; needs a strict timeout.
- **~15 GB download** time/space (disk is fine at 924 GB free; network time is the cost).
- **System impact:** memory pressure could slow the whole WSL session; keep `max_new_tokens` tiny and
  attempt **one prompt only** first.

## 8. Approval required before download

Stage 10B must not download or run anything until the user provides this **exact** approval text:

> Approved: Stage 10B — download and attempt a guarded Qwen 7B Transformers memory-pressure baseline, with no model artifacts committed.

## 9. Proposed Stage 10B execution guardrails

- Download the chosen 7B **only** into a git-ignored path under `.local_models/` (e.g.
  `.local_models/hf/qwen2_5_7b_instruct/`); **no Git-tracked weights**, ever.
- Attempt **one prompt only** first (`os_definition`), `do_sample=False`, **`max_new_tokens` ≤ 8–16**,
  `torch.manual_seed(0)`, CPU, `local_files_only=True` after download.
- **Strict timeout** (e.g. wrap load+generate; abort after a documented wall-clock cap) so a thrash
  never hangs the session.
- Measure: `success`/`failure`, `error_type`, `load_seconds`, `peak_ram_mb`, `elapsed_seconds`,
  and (if it generates) tokens/throughput + an output preview.
- **If OOM or impossible:** record a **structured negative-result JSON** (honest), stop. **Do not
  retry**, **do not** attempt a full benchmark, **do not** escalate to fp32 or multiple prompts.
- Results go to a **new** dir (e.g. `results/measurements/transformers_cpu_qwen2_5_7b_pressure/`);
  prior measurement dirs are never edited.

## 10. Success criteria (Stage 10B)

- A clear, reproducible outcome is recorded — **either** a minimal guarded generation **or** a
  structured OOM/failure result — with load time, peak RAM, error type, and elapsed time.
- No model weights committed; no prior data altered; honest framing (pressure test, not a benchmark).

## 11. Failure criteria (Stage 10B)

- OOM / killed / timeout → **expected, acceptable** → captured as a structured negative result (this
  is still a valid deliverable, not a project failure).
- Unacceptable only if: weights get committed, retries hammer the machine, claims overstate the
  result, or prior raw data is edited — none of which are permitted.

## 12. Files allowed in Stage 10B (when approved)

- `src/ex05_airllm/run_transformers_cpu_large_model_pressure.py` (+ a small pure helper if needed to
  stay ≤150 lines), `tests/unit/test_*` (pure, fake data only).
- New results dir `results/measurements/transformers_cpu_qwen2_5_7b_pressure/` (JSON [+ summary]).
- Docs: `MEASUREMENT_RUNS.md`, `MEASUREMENT_DESIGN.md`, `FINAL_GAP_AUDIT.md`,
  `SUBMISSION_CHECKLIST.md`, `REQUIREMENTS_AUDIT.md`, `TODO.md`, `PLAN.md`, `QUALITY.md`,
  `PROMPTS.md`, `README.md`, `reports/final_report.md`. (`pyproject.toml`/`uv.lock` only if a new dep
  is separately approved — none is anticipated; Transformers is already present.)

## 13. Files forbidden in Stage 10B

- Any model weights/shards (`*.safetensors`, `*.bin`, `*.pt`, `*.pth`, `*.gguf`), `.local_models/`,
  `.hf_cache/`. Prior raw measurement dirs, `results/analysis/*.json`, `figures/*.png`,
  `reports/measurement_summary.md` (no edits). The local course-materials directory, secrets/tokens,
  site-packages.

## 14. Submission impact

- This is the **last** open experimental gap. Closing it (as a real run **or** a structured
  OOM/negative result) would make the local-memory-management story complete end-to-end. Until then
  the repo stays **honest, reproducible, and explicitly NOT self-assessment-100-ready**; AirLLM stays
  a blocked negative result; quantization (INT8 + GGUF Q8/Q4) stays measured; `Qwen2-7B` stays not
  downloaded/not approved.
- **Update:** Stage 10B has since **attempted & evidenced** the direct fp16 7B pressure baseline as a
  guarded structured negative (`memory_budget_exceeded`); §15 below scopes the *next* optional step — a
  **GGUF-Q4 7B** run that might actually *fit and generate* — as a separate, approval-gated Stage 12B.

## 15. Stage 12B-0 — GGUF Q4 7B preflight (PLAN ONLY; no download, no run, no dependency)

> **Planning/audit only.** Nothing here downloads, runs a model, adds a dependency, or edits a result.
> Unlike Stage 10B (direct fp16 7B → expected OOM), a **Q4_K_M 7B (~4.5 GB)** plausibly **fits** the
> WSL budget and could **generate**, turning the large-model story from "OOM negative" into a possible
> *successful quantized large-model* run. This stays **gated** behind explicit user approval.

**1. Candidate model**
- Preferred: **`Qwen/Qwen2.5-7B-Instruct-GGUF`**, file **`qwen2.5-7b-instruct-q4_k_m.gguf`** (Q4_K_M),
  via `llama-cpp-python` (the same runtime/family as the Stage 10A 0.5B GGUF sweep — consistent,
  `llama.cpp`-compatible). The exact repo/file name and size are inferred from the Stage 10A naming
  pattern; the **precise filename and on-disk size are TODO_REQUIRES_APPROVAL_AND_LOOKUP** at Stage 12B
  approval time (no metadata is fetched now). **Not downloaded.**

**2. Expected resource footprint**
- **Model file size:** Q4_K_M 7B ≈ **4.3–4.9 GB** (TODO confirm at lookup).
- **RAM risk (WSL ~11 GiB RAM + ~3 GiB swap):** Q4 weights (~4.5 GB) + KV cache + runtime overhead are
  expected to **fit** with a small context; **moderate** risk (much lower than fp16's ~15 GB). With
  **mmap** the weights are paged from disk, lowering resident RSS further.
- **Disk-space risk:** **low** — ~5 GB download onto the 924 GB-free volume.
- **mmap:** **use mmap** (`use_mmap=True`, llama.cpp default) so weights are demand-paged.
- **n_ctx:** limit to **512** (or 1024 max) to bound KV-cache memory.
- **max_new_tokens:** small — **32** (single short generation).

**3. Measurement schema**
- **Result dir:** `results/measurements/gguf_7b_quantized_q4_pressure/` (new; never edit prior dirs).
- **CSV/JSON fields:** `model_id`, `quantization_variant`, `backend=llama_cpp`, `environment=wsl_cpu`,
  `success`, `structured_negative_result`, `failure_class`, `ttft_seconds`, `tpot_seconds`,
  `throughput_tokens_per_second`, `peak_rss_mb`, `model_file_size_mb`, `load_seconds`,
  `generation_seconds`, `prompt_id`, `output_preview`, `quality_label`, `notes`.

**4. Success criteria**
- **Success:** `success=True` and `generation_completed=True` with a **non-empty `output_preview`** →
  the headline becomes a *successful quantized large-model generation* (coherent or labelled via
  `quality_label`).
- **Failure (still a valid deliverable):** memory/timeout failure → `structured_negative_result=True`
  with `failure_class ∈ {memory_budget_exceeded, oom_or_killed, timeout_or_thrash}`.

**5. Safety**
- **One run only** initially (single prompt, e.g. `os_definition`), deterministic (`temperature=0`,
  `seed=0`). **No external APIs. No AirLLM.** **No model artifact tracked** (weights git-ignored under
  `.local_models/`). A **hard timeout owned by the parent process** (subprocess + wall-clock cap, like
  Stage 10B's guarded runner), **not** a shell `timeout`. **Write the result JSON/CSV even on failure.**

**6. Files needed in a future Stage 12B (when approved)**
- **Code:** `src/ex05_airllm/gguf_7b_pressure.py` (pure helpers: schema/classify/summarize) +
  `src/ex05_airllm/run_gguf_7b_quantized_pressure.py` (guarded parent/child runner). Each ≤150 code
  lines; reuse `gguf_measurement` helpers where possible.
- **Tests:** `tests/unit/test_gguf_7b_pressure.py` (pure, fake records, monkeypatched paths — no
  llama_cpp import, no network).
- **Docs:** `MEASUREMENT_RUNS.md`, `MEASUREMENT_DESIGN.md`, `FINAL_GAP_AUDIT.md`,
  `SUBMISSION_CHECKLIST.md`, `REQUIREMENTS_AUDIT.md`, `TODO.md`, `PLAN.md`, `QUALITY.md`, `PROMPTS.md`,
  `README.md`, `reports/final_report.md`.
- **Figures/analysis:** extend `analysis_pipeline.py` to fold the 7B-Q4 row into
  `final_evidence_summary.json` + the roofline; optionally a small new figure. (`pyproject.toml`/
  `uv.lock` only if `llama-cpp-python` is not already present — it is, from Stage 10A, so **no new
  dependency expected**.)

**7. Go / no-go recommendation**
- **Benefit:** a successful Q4 7B generation would materially strengthen the big-model story (fits-and-
  runs vs fp16 OOM). **Risk:** ~5 GB download + a chance of thrash/OOM on the 11 GiB host; modest time.
- **Recommendation: STOP-AND-SUBMIT-NOW is defensible** — the repo already has a complete, honest
  large-model-pressure story (Stage 10B negative) plus measured small-model quantization. **Proceed to
  Stage 12B only after explicit user approval that includes the model download**; it is **optional
  upside**, not a prerequisite for an honest submission. No 100-ready / 100%-complete claim either way.
