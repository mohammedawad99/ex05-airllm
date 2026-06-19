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
- **Work:** Write `PRD_measurement.md` (precise metric definitions & timing method) and
  `PRD_airllm_pipeline.md`; **select & justify the model** (ADR) against the measured profile
  (~11.24 GiB RAM, CPU-only, 933 GB disk; AirLLM families verified in 1D: Llama2/Mistral/
  Mixtral/QWen2); **resolve the CPU quantization route** (AirLLM `bitsandbytes` needs CUDA →
  likely GGUF Q4/Q8 on CPU — R-QUANT-CPU); define `config/` schema (versioned), `.env-example`;
  set up `pyproject.toml` + `uv` + `ruff` + coverage config — **pinning the AirLLM dependency
  matrix** evidenced in 1D (`transformers==4.44.2`, `optimum==1.23.3`, `sentencepiece`, CPU
  `torch` wheel; R-AIRLLM-DEPS).
- **DoD:** Measurement design + model choice approved as ADRs; tooling configured; still no
  experiment code beyond config.

### Stage 3 — Small pipeline proof (TDD)
- **Entry:** Architecture & tooling ready.
- **Work:** Implement SDK skeleton, HardwareProbe, MetricsCollector, FileStore, ConfigLoader,
  ApiGatekeeper, and a runner — exercised end-to-end on a **tiny** model. TDD throughout.
- **DoD:** End-to-end run on a small model produces a valid metrics JSON; tests pass; coverage
  ≥85% on implemented modules; `ruff` clean; files ≤150 lines. **No claims about the big model.**

### Stage 4 — Baseline experiment
- **Entry:** Pipeline proven.
- **Work:** Run the **direct baseline** (Ollama/HF) on the real task with the selected model;
  document live behavior including any failure/slowdown; capture metrics + sample outputs.
- **DoD:** Baseline results stored in `results/baseline/`; behavior (incl. failure mode)
  documented in `reports/baseline.md` with evidence.

### Stage 5 — AirLLM + quantization
- **Entry:** Baseline documented.
- **Work:** Run the same task via AirLLM; sweep ≥2 quantization levels; collect all metrics
  and qualitative samples per configuration.
- **DoD:** `results/airllm/` and `results/quant/` populated; per-config metrics + samples
  captured; raw vs summary results separated (raw git-ignored).

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
