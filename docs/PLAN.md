# PLAN — Architecture & Staged Execution

> **STATUS: STAGE 0.** This is the plan and proposed architecture. No implementation
> exists yet. Concrete interfaces are sketched as design intent, not committed code.

- **Related:** `PRD.md`, `TODO.md`, `REQUIREMENTS_AUDIT.md`, `DECISIONS.md`, `RISKS.md`, `HARDWARE.md`

---

## 0. Hardware-calibrated constraints (Stage 1A WSL + Stage 1B host — measured)

Captured 2026-06-19 (`docs/HARDWARE.md`). Per **ADR-0009**, the plan is calibrated to the
**execution environment**, not the larger host. Evidence boundary:

- **Physical host (context only):** Windows 11, ASUS Vivobook S 14, Ryzen AI 9 HX 370,
  ≈ 24 GB RAM, AMD Radeon 890M iGPU (no NVIDIA), ~1 TB **NVMe SSD**.
- **Execution environment (binding):** Ubuntu 24.04 on **WSL2**.
  - **CPU:** 24 threads, AVX-512 + VNNI (good CPU-inference ISA).
  - **RAM:** ≈ **11.24 GiB** (WSL2 cap of ~24 GB host) + 3 GiB swap → the "larger-than-memory"
    target is sized against ~11 GiB.
  - **GPU:** host iGPU exists (DX12_2) but **no compute path usable in WSL2** (no CUDA/ROCm;
    OpenGL = `llvmpipe`; 0 MB dedicated VRAM) → **CPU-only** working assumption; peak-VRAM
    likely `N/A`. DirectML feasibility under review (`GPU_FEASIBILITY.md`, ADR-0010).
  - **Disk:** 933 GB free ext4 on an **NVMe-backed** WSL VHDX → media is favorable, but the
    VHDX/9p overhead means I/O must be **measured**, not assumed (suspected AirLLM bottleneck).
- **Tooling:** Python 3.12.3, `uv` 0.11.9 available.

---

## 1. Strategy

Start small, prove the pipeline end-to-end on a tiny model, then scale to the deliberately
oversized model. Measurement infrastructure is built and validated **before** the expensive
runs, so that when the big model runs (slowly, possibly failing), the harness is trusted and
every number is reproducible. Documentation and the audit trail evolve continuously, not at
the end.

## 2. Proposed architecture (C4-style, design intent)

The guidelines require a layered, SDK-fronted design (G §4.1). Proposed layers:

```
            ┌───────────────────────────────────────────────────────┐
  Level 1   │  Consumers:  CLI experiment runner  /  analysis script │  thin, no logic
  (Context) └───────────────────────────────┬───────────────────────┘
                                             │ calls only
            ┌────────────────────────────────▼──────────────────────┐
  Level 2   │  SDK  (single entry point for ALL logic)               │
  (Container)│  run_baseline() · run_airllm() · sweep_quant()        │
            │  collect_metrics() · analyze_costs() · make_report()   │
            └───────────────┬───────────────────────┬───────────────┘
                            │                        │
        ┌───────────────────▼─────────┐   ┌──────────▼───────────────────┐
  Level 3│  Domain services            │   │  Cost / analysis services     │
 (Component)│ - ModelLoader (HF/AirLLM) │   │ - CostModel (API vs On-Prem)  │
        │ - InferenceRunner (prefill/  │   │ - EnergyEstimator             │
        │   decode timing)            │   │ - BreakEvenSolver             │
        │ - MetricsCollector          │   │ - Plotter (figures)           │
        │ - QuantizationManager       │   └───────────────────────────────┘
        └───────────────┬─────────────┘
                        │
        ┌───────────────▼───────────────────────────────────────────┐
  Level 4│  Infrastructure                                            │
 (Code)  │ - HardwareProbe (lscpu/free/nvidia-smi/df wrappers)        │
        │ - FileStore (results JSON/CSV)                              │
        │ - ApiGatekeeper (rate-limit, retry, queue, log)  ← all API  │
        │ - ConfigLoader (config/*.json + os.environ secrets)         │
        └────────────────────────────────────────────────────────────┘
```

**Architectural rules carried from the guidelines:**
- All business logic behind the **SDK**; CLI/analysis layers are thin (R-ARCH-SDK).
- Every external API call goes through **ApiGatekeeper** — no direct calls (R-ARCH-GATEKEEPER).
- OOP, DRY, each file ≤150 lines (R-ARCH-OOP, R-FILELEN); split via helper/mixin/constants.
- No hardcoded values; config in `config/*.json`, secrets via `os.environ` (R-NOHARDCODE, R-CONFIG-ARCH).
- Versioning from `1.00` (R-VERSION); `uv` only (R-UV).

> This is a **proposal**. Component boundaries are confirmed and the per-mechanism PRDs
> (`PRD_airllm_pipeline.md`, `PRD_measurement.md`) written in Stage 2 before code (Stage 3).

## 3. Proposed data flow

```
hardware specs ──► model selection ──► [baseline run] ─┐
                                       [airllm run]    ├─► metrics (JSON) ─► analysis ─►
                                       [quant sweep]  ─┘        │              figures + tables
                                                                 └─► cost model ─► break-even ─► README
```

## 4. Staged plan (0–7)

Each stage has an entry condition, the work, and an explicit **Definition of Done (DoD)**.
Detailed tasks live in `TODO.md`. The requirements audit is re-checked at every stage close.

### Stage 0 — Requirements & repository foundation  *(current)*
- **Work:** Capture requirements; build traceability audit; draft PRD/PLAN/TODO; set up
  RISKS, DECISIONS, AI_WORKFLOW, PROMPTS, QUALITY, COSTS, SUBMISSION_CHECKLIST; `.gitignore`;
  Stage-0 README; directory scaffold.
- **DoD:** All Stage-0 docs exist with real content; no code, no results, no secrets; audit
  lists every requirement and all `NEEDED_USER_INPUT`; validation greps are clean.

### Stage 1 — PRD / PLAN / TODO approval
- **Entry:** Stage 0 complete.
- **Work:** Review with user; resolve open questions that don't need hardware; **collect the
  `NEEDED_USER_INPUT` hardware specs**; freeze PRD v1.0.
- **DoD:** User approves PRD/PLAN/TODO; hardware specs supplied (U-OS…U-DISK-FREE) and
  recorded; group code, repo URL, HF-access confirmation captured.

### Stage 2 — Measurement architecture & model selection
- **Entry:** Hardware known ✅ (Stage 1A complete; `docs/HARDWARE.md`).

**Stage 2A — Dependency skeleton & measurement design ✅ (done):**
- Created `pyproject.toml` + `uv.lock` (reproducible env), **pinning the AirLLM matrix** from
  1D (`airllm==2.11.0`, `transformers==4.44.2`, `optimum==1.23.3`, `sentencepiece`, CPU `torch`
  wheel via the `pytorch-cpu` index; R-AIRLLM-DEPS); minimal `src/ex05_airllm` package
  (`version.py`, `constants.py`) + version-consistency test; `ruff`/`pytest`/coverage configured;
  `docs/MEASUREMENT_DESIGN.md` (metrics, result schema, reproducibility rules); versioned
  `config/experiment.example.toml` (placeholder model id). DoD met: `uv sync` resolves, tests
  pass, `ruff` clean, coverage ≥85%, all files ≤150 lines — **no model, no inference, no benchmark.**

**Stage 2B — Model shortlist & selection plan ✅ (planning done):**
- Built the **metadata-verified** shortlist (`docs/MODEL_SELECTION.md`,
  `config/model_candidates.example.toml`) — no weights downloaded. Recommended for
  verification: tiny `Qwen/Qwen2-0.5B`, main + direct baseline `Qwen/Qwen2-7B` (fp16 ~15.24 GB
  > ~11.24 GiB RAM), both apache-2.0 + ungated; Mistral-7B-Instruct-v0.2 deferred backup,
  Qwen2-72B deferred stretch. Wrote `PRD_measurement.md` and `PRD_airllm_pipeline.md`; recorded
  model-selection strategy (ADR-0101a); ADR-0101 → SHORTLISTED.
- **Remaining (user-gated):** final model pick + **download approval** (T2.6), then the
  quantization-route ADR (R-QUANT-CPU) and `.env-example` only if a token is ever needed.
- **DoD:** shortlist + strategy recorded as ADRs (✅); **final pick + any download await explicit
  approval and the Stage 3 smoke run** — nothing downloaded in Stage 2.

### Stage 3 — Small pipeline proof (TDD)
- **Entry:** Architecture & tooling ready.

**Stage 3A — tiny AirLLM CPU smoke probe (done; failed honestly):**
- Ran `smoke_airllm.py` on the approved `Qwen/Qwen2-0.5B` (CPU). Result: **FAILED** at AirLLM's
  layer-sharding step — `model.safetensors.index.json should exist` (R-AIRLLM-SHARD): AirLLM
  needs a multi-shard safetensors checkpoint, but the tiny model ships as a single file. Only
  ~12 MB metadata/tokenizer reached the external HF cache; **no weights in the repo**; no
  Qwen2-7B download. Evidence: `docs/SMOKE_RUN.md`, `results/stage3_smoke_airllm_qwen2_0_5b.json`.
**Stage 3B — re-sharded tiny AirLLM CPU smoke (done; format fixed, runtime failed):**
- Re-sharded Qwen2-0.5B locally (37 shards + index, git-ignored) and **untied** its tied
  embeddings (added `lm_head.weight`). AirLLM then **accepted** the model, split all layers, and
  **started** the CPU forward pass — but failed with `RuntimeError: Tensor on device cpu ...
  meta!` (R-AIRLLM-META: AirLLM's meta-device lazy loading on CPU, aggravated by torch 2.12.1).
  Smoke **not** successful (no output). Evidence: `SMOKE_RUN.md` §6,
  `results/stage3b_smoke_airllm_qwen2_0_5b_resharded.json`.
**Stage 3C — torch-pin retest (done; torch ruled out):**
- Pinned `torch==2.4.1+cpu` and reran the smoke on the existing re-sharded model → **identical**
  meta-device error. Torch version is **not** the cause; AirLLM leaves Qwen2's top-level
  `rotary_emb` on `meta` (R-AIRLLM-META). `torch==2.4.1` kept as the project pin. Evidence:
  `SMOKE_RUN.md` §7, `results/stage3c_smoke_airllm_qwen2_0_5b_torch241.json`.
**Stage 3D — Transformers CPU fallback smoke (done; SUCCEEDED):**
- Direct HF `transformers` CPU `generate` on the cached Qwen2-0.5B (offline, `local_files_only`)
  **succeeded** with coherent output → **measurement pipeline proven** (schema-valid record with
  load/gen/runtime/RSS/token metrics; ADR-0016 EVIDENCED, R-REPRO partially evidenced). It is
  **not** AirLLM and **not** a benchmark. Evidence: `SMOKE_RUN.md` §8,
  `results/stage3d_smoke_transformers_qwen2_0_5b_cpu.json`.
- **AirLLM CPU stays blocked** (R-AIRLLM-META, R-AIR-01 PLANNED). The remaining Stage 3 work
  (full SDK/MetricsCollector/gatekeeper) builds on this proven writer.

### Stage 4A — AirLLM Qwen2 CPU patch feasibility (done; minimal shim infeasible)
- Implemented + tested a local, fail-closed Qwen2 rotary shim (`src/ex05_airllm/airllm_compat.py`,
  no site-packages edits) and ran a patched smoke on the local model → **still failed**. A
  no-download diagnostic **disproved the rotary hypothesis** and showed the meta tensor is a
  running decoder layer's **parameter** (`input_layernorm.weight`) — AirLLM's *core* per-layer
  meta→CPU streaming. A minimal safe shim is **infeasible** (ADR-0017).
- **Decision:** AirLLM CPU (Qwen2) is a **documented limitation**; the experiment proceeds on the
  proven **HF `transformers` CPU** pipeline (Stage 3D). AirLLM remains not evidenced; no Qwen2-7B
  download (same core CPU path). Evidence: `docs/AIRLLM_PATCH_FEASIBILITY.md`, `results/stage4a_*`.

**Stage 3 (full) — Work:** Implement SDK skeleton, HardwareProbe, MetricsCollector, FileStore,
ConfigLoader, ApiGatekeeper, and the runner — exercised end-to-end on a **tiny** model, TDD.
- **DoD:** End-to-end tiny-model run produces a valid metrics JSON; tests pass; coverage ≥85%;
  `ruff` clean; files ≤150 lines. **No claims about the big model.**

### Stage 4 — Baseline experiment
- **Entry:** Pipeline proven.
- **Work:** Run the **direct baseline** (Ollama/HF) on the real task with the selected model;
  document live behavior including any failure/slowdown; capture metrics + sample outputs.
- **DoD:** Baseline results stored in `results/baseline/`; behavior (incl. failure mode)
  documented in `reports/baseline.md` with evidence.

### Stage 5 — Measurement SDK + repeatable Transformers CPU measurement  *(revised per ADR-0018)*
- **Entry:** Stage 4B revision approved. AirLLM CPU/Qwen2 is a documented limitation, not the
  main run.

**Stage 5A — measurement SDK & result schema ✅ (done; no inference):**
- Implemented `result_schema.py` (typed `MeasurementResult`), `metrics.py` (`MetricsCollector`,
  injectable clock/RSS), `result_writer.py` (`write_json`/`append_csv`, stable header),
  `prompts.py`, `env.py` — all TDD, files ≤150 lines, 38 unit tests (no model/network).
  Optional metrics default to `None` and `success` to `False` (no fake values).

**Stage 5B — repeatable Transformers CPU measurement ✅ (done; 6/6 runs):**
- `run_transformers_cpu_measurement.py` wires the SDK around a real HF `transformers` CPU
  `generate` on the local **Qwen2-0.5B** (offline, `local_files_only`, `manual_seed(0)`,
  `do_sample=False`). Ran the **3 prompts × 2 repeats = 6 runs, all successful**, writing 6
  schema-valid JSONs + `summary.csv` to `results/measurements/transformers_cpu_qwen2_0_5b/`
  (`environment=wsl_cpu`). Measured: runtime ~5.2–6.6 s, throughput ~4.4–5.3 tok/s, peak RAM
  ~4.0 GB, load ~5.4 s; **TTFT = None** (no streaming hook), **TPOT approximate** (documented).
  Evidence:
  `docs/MEASUREMENT_RUNS.md`. **No AirLLM, no Qwen2-7B download.**
- **Next (Stage 6):** analysis/plots *from* `summary.csv`, cost/energy estimate, and the final
  report — folding the AirLLM failure JSONs in as structured evidence (not success).
- **DoD:** `results/` has repeatable Transformers-CPU measurement records (schema-valid) + the
  AirLLM failure evidence; tests pass, coverage ≥85%, `ruff` clean, files ≤150 lines; raw vs
  summary separated (raw git-ignored). **No AirLLM success claimed; no benchmark of a model we
  didn't run.**

> *(Former Stage 5 "Run via AirLLM + quantization sweep" is superseded: AirLLM CPU is blocked
> here — see `docs/EXPERIMENT_REVISION.md`. AirLLM compression/quantization is GPU/bitsandbytes-
> bound and out of scope on this CPU path; quantization, if shown, uses GGUF via the baseline.)*

### Stage 6 — Analysis, graphs, costs & extension
- **Entry:** All runs complete.
- **Work:** Generate tables/figures (TTFT/TPOT/throughput/memory, quant Pareto, bottleneck
  map); compute energy estimates; build cost model + break-even graph (+ optional cloud-GPU
  line); implement the chosen **original extension**; answer Research Questions.
- **DoD:** Figures in `figures/`, long-form analysis in `reports/`, extension delivered;
  every concept tied to evidence.

### Stage 7 — Final audit & submission
- **Entry:** Analysis complete.
- **Work:** Assemble README as the full technical report (tables, graphs, evidence map,
  reproduction, limitations, links); re-run `SUBMISSION_CHECKLIST.md`; final requirements
  re-audit; clean git history; user-initiated push.
- **DoD:** Checklist 100% green; audit all `DONE`/`N/A_WITH_RATIONALE` with evidence; user
  approves; push performed **only on explicit user request**.

## 5. Milestones

| Milestone | Gate |
| --- | --- |
| M0 Foundation | Stage 0 DoD met |
| M1 Approved & hardware-known | Stage 1 DoD met |
| M2 Design + model locked | Stage 2 DoD met |
| M3 Pipeline proven small | Stage 3 DoD met |
| M4 Evidence gathered | Stages 4–5 DoD met |
| M5 Analysis & report | Stage 6 DoD met |
| M6 Submission | Stage 7 DoD met |

## 6. Key trade-offs (to be recorded as ADRs in `DECISIONS.md`)

- Model size vs feasibility (large enough to exceed ~11 GiB, small enough to finish on CPU).
- Quantization precision vs output quality — **and** the CPU route itself (GGUF Q4/Q8 vs
  `bitsandbytes`/CUDA, R-QUANT-CPU).
- Ollama vs HF `transformers` for the baseline.
- ~~GPU vs CPU execution path~~ → **resolved by Stage 1A evidence toward CPU-only** (no
  compute GPU detected); revisit only if a GPU stack is later enabled.
- Measurement granularity vs runtime overhead (instrumentation must not distort timings).

## 7. Time estimates (planning aid, not measurements)

From the assignment's realistic-estimate appendix (Vibe Coding): roughly **6.5–11h
end-to-end**, of which **~2–3h** is active engineering time, the rest physical
compute/download. These are estimates and will not be reported as actual durations.
