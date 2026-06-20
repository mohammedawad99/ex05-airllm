# Requirements Audit & Traceability — EX05 (AirLLM)

**Stage:** 0 (requirements capture)
**Purpose:** A single source of truth mapping every requirement to its source, current
status, the evidence that will prove it, the controlling risk, and notes. This table is
re-audited at the end of every stage (see `PLAN.md`) and is the backbone of the final
submission audit (`SUBMISSION_CHECKLIST.md`).

## Status legend

| Status | Meaning |
| --- | --- |
| `PLANNED` | Accepted requirement, not yet started; scheduled in a later stage. |
| `EVIDENCED` | Fully backed by captured terminal evidence (intake facts). Distinct from `DONE`, which is reserved for completed experimental work with an output artifact. |
| `PARTIALLY_EVIDENCED` | Real terminal evidence captured for part of the requirement; capture incomplete or dependent on a tool/input still missing. |
| `NEEDED_USER_INPUT` | Blocked: requires information or an action only the user can provide. |
| `N/A_WITH_RATIONALE` | Deliberately out of scope; rationale recorded. |

> No experimental requirement (model selection, baseline, AirLLM, quantization, benchmarks)
> is marked `DONE`. `DONE` is reserved for later audits and must always point to a concrete
> `evidence_path`. `PARTIALLY_EVIDENCED` (introduced in Stage 1A) marks requirements where
> some real evidence now exists but the requirement is not complete.

## Sources

- **A** = the assignment brief (lecture 08 guidance).
- **G** = the course software guidelines.
- **U** = User / course context provided for this Stage 0 task.

---

## A. Core experiment requirements (from the assignment)

| requirement_id | requirement | source | status | evidence_path | risk | notes |
| --- | --- | --- | --- | --- | --- | --- |
| R-HW-01 | Document exact local hardware: OS, CPU model+cores, RAM, GPU, VRAM, disk type, free disk | A §5.1 | PARTIALLY_EVIDENCED | docs/HARDWARE.md | R-DISK, R-WSL-MEM, R-WSL-DISK, R-NOGPU, R-OVERCLAIM | Stage 1A (WSL) + Stage 1B (Windows host via CIM). OS/CPU/RAM/disk-free/disk-type now EVIDENCED on both layers (host ≈24 GB RAM, NVMe SSD; experiment ≈11.24 GiB, ext4-on-VHDX). **GPU/VRAM stay PARTIALLY_EVIDENCED**: host has an AMD Radeon 890M iGPU (no NVIDIA), but CUDA/ROCm compute is **not** available inside WSL2 → CPU-only. See §C and HARDWARE.md §A/§B. |
| R-MODEL-01 | Select a Hugging Face model **deliberately larger** than local memory, justified against the hardware (params, format, size) | A §5.1 | PARTIALLY_EVIDENCED | docs/MODEL_SELECTION.md, config/model_candidates.example.toml, DECISIONS.md ADR-0101/0101a | R-MODELSIZE, R-AIRLLM-COMPAT, R-MODEL-LICENSE | Stage 2B: metadata-verified shortlist (no download); main `Qwen/Qwen2-7B` fp16 15.24 GB > 11.24 GiB. **Final pick + download await approval** (T2.6) → not DONE. |
| R-BASE-01 | Attempt a **direct baseline** (Ollama or HF `transformers`); document live behavior incl. failure/slowdown | A §5.2 | PARTIALLY_EVIDENCED | results/measurements/transformers_cpu_qwen2_0_5b/summary.csv, results/measurements/large_model_pressure_qwen2_5_7b/, docs/MEASUREMENT_RUNS.md §11, docs/LARGE_MODEL_PREFLIGHT.md | R-NONREPRO | Stage 5B: a **direct HF `transformers` CPU** baseline on Qwen2-0.5B ran 6× successfully (full measured path). **Direct large-model (>RAM) pressure baseline — ATTEMPTED & EVIDENCED (structured negative):** Stage 10B ran a **guarded** `Qwen/Qwen2.5-7B-Instruct` fp16 Transformers CPU attempt under a **13312 MiB** `RLIMIT_AS` child budget; local snapshot found (weights git-ignored, never committed), the child hit `Cannot allocate memory` **during load** → `memory_budget_exceeded` (`success=false`, `returncode=3`, not timed out, no generation). Documents live failure behavior under memory pressure. **A guarded memory-budget attempt, not a full benchmark; no large-model performance claimed.** AirLLM is a separate (blocked) path. |
| R-AIR-01 | Run the same task with **AirLLM** (layer-wise loading) | A §5.3 | PLANNED (BLOCKED) | results/stage3*/stage4a* JSONs, docs/AIRLLM_PATCH_FEASIBILITY.md, docs/EXPERIMENT_REVISION.md | R-AIRLLM-SHARD, R-AIRLLM-TIED, R-AIRLLM-META, R-GRADE-AIRLLM | 3A format fail → 3B re-shard+untie fixed format → 3B/3C/4A CPU forward **fails** (meta-device; torch & rotary ruled out; core param-streaming defect). **PLANNED/BLOCKED, NOT evidenced** (no generation). **Stage 4B (ADR-0018):** AirLLM kept as documented failure analysis; Qwen2-7B deferred; runnable path = HF `transformers` CPU. |
| R-QUANT-01 | Apply and compare **quantization** levels (e.g. FP16, Q8, Q4) and document the effect of each | A §5.3 | EVIDENCED (small model) | results/measurements/transformers_cpu_int8_quantization_qwen2_0_5b/, results/measurements/gguf_quantization_qwen2_5_0_5b/, docs/MEASUREMENT_RUNS.md §9–§10 | R-AIRLLM-COMPAT | Two measured comparisons: Stage 9C **FP32 vs dynamic INT8** (Transformers; INT8 faster but quality degraded) and Stage 10A **GGUF Q8_0 vs Q4_K_M** (`llama.cpp`, `Qwen2.5-0.5B-Instruct-GGUF`, 12/12; Q4 ~13% less RAM / 27% smaller file at ~equal throughput, coherent). **F16 GGUF excluded** (1266 MB > ~1.2 GB cap). Small-model only; the two runtimes are **not** cross-comparable; no large-model quant. |
| R-MEAS-TTFT | Measure **TTFT** (Time To First Token) — prefill + KV-cache build cost | A §5.4 | PARTIALLY_EVIDENCED | results/measurements/transformers_cpu_streaming_qwen2_0_5b/summary.csv, docs/MEASUREMENT_RUNS.md §8 | R-NONREPRO | Stage 9B: **real TTFT measured** via `TextIteratorStreamer` (6/6, cached Qwen2-0.5B, CPU, offline, no download) — mean ≈0.41 s (skewed by cold first run; steady ≈0.25–0.27 s). Supersedes Stage 5B's `None`; measured, not estimated. Single small model only → PARTIALLY. |
| R-MEAS-TPOT | Measure **TPOT / ITL** (per-output-token latency / inter-token latency) | A §5.4 | PARTIALLY_EVIDENCED | results/measurements/transformers_cpu_streaming_qwen2_0_5b/summary.csv, docs/MEASUREMENT_RUNS.md §8 | R-NONREPRO | Stage 9B: **decode-only** TPOT = (generation_seconds − ttft_seconds)/(output_tokens − 1) ≈ 0.19 s/token, now that TTFT is measured (streaming). Stage 5B's approximate TPOT remains for the non-streaming run. |
| R-MEAS-THRU | Measure **throughput** (tokens/sec) | A §5.4 | PARTIALLY_EVIDENCED | results/measurements/transformers_cpu_qwen2_0_5b/summary.csv, docs/MEASUREMENT_RUNS.md | R-IO | Stage 5B: measured ~4.4–5.3 tok/s (Qwen2-0.5B, CPU). Descriptive, not a benchmark. |
| R-MEAS-MEM | Measure **peak RAM** and **peak VRAM** (VRAM only if a GPU is usable for compute) | A §5.4 | PARTIALLY_EVIDENCED | results/measurements/transformers_cpu_qwen2_0_5b/summary.csv, docs/MEASUREMENT_RUNS.md | R-OVERCLAIM | Stage 5B: peak RSS measured (~4.0 GB, Qwen2-0.5B CPU). **VRAM `N/A_WITH_RATIONALE`** (no usable GPU compute in WSL2). |
| R-MEAS-TIME | Measure **total runtime** (wall clock) | A §5.4 | PARTIALLY_EVIDENCED | results/measurements/transformers_cpu_qwen2_0_5b/summary.csv, docs/MEASUREMENT_RUNS.md | — | Stage 5B: per-run total + load + generation seconds measured (Qwen2-0.5B, CPU). |
| R-MEAS-ENERGY | Provide **estimated energy use** with stated assumptions | A §5.4 | PARTIALLY_EVIDENCED | results/analysis/cost_energy_estimate.json, figures/cost_break_even_estimate.png, docs/ANALYSIS.md | R-OVERCLAIM | Stage 6A: per-run energy estimated from measured runtime + assumed CPU watts (`cost_model.py`); labelled estimate, not metered. |
| R-MEAS-QUAL | **Qualitative** assessment of output quality per quantization level | A §5.4 | EVIDENCED (small model) | results/measurements/transformers_cpu_int8_quantization_qwen2_0_5b/*.json, results/measurements/gguf_quantization_qwen2_5_0_5b/*.json, docs/MEASUREMENT_RUNS.md §9–§10 | — | Per-variant `output_preview`/`output_text` committed for both sweeps: Stage 9C (FP32 coherent vs **INT8 degraded**) and Stage 10A (GGUF **Q8_0 and Q4_K_M both coherent**). Honest per-level quality evidence on a small model. |
| R-COST-API | Compute external-API cost per request (input+output tokens) for a chosen provider | A §5.5 | PARTIALLY_EVIDENCED | results/analysis/cost_energy_estimate.json, figures/cost_break_even_estimate.png, docs/ANALYSIS.md | R-OVERCLAIM | Stage 6A: API cost computed from measured token counts × **assumed** per-1M prices. **Not** verified live pricing — must be sourced/dated before any claim. |
| R-COST-ONPREM | Compute On-Prem cost: CAPEX amortized + OPEX (electricity, maintenance) per request | A §5.5 | PARTIALLY_EVIDENCED | results/analysis/cost_energy_estimate.json, figures/cost_break_even_estimate.png, docs/ANALYSIS.md | R-OVERCLAIM | Stage 6A: OPEX (electricity) per run computed under assumptions; CAPEX = sensitivity-only (`hardware_cost_usd=0`). Assumption-based, not verified. |
| R-COST-BREAKEVEN | Find and graph the **break-even point** (requests/tokens) On-Prem vs API | A §5.5 | PARTIALLY_EVIDENCED | results/analysis/cost_energy_estimate.json, figures/cost_break_even_estimate.png, docs/ANALYSIS.md | R-OVERCLAIM | Stage 6A: illustrative break-even graph under **assumed** pricing (`cost_break_even_estimate.png`). NOT verified market pricing. |
| R-COST-GPU-OPT | *(Optional)* Add a third line: cloud GPU rental cost on the break-even graph | A §5.5 (optional) | PLANNED | figures/breakeven.* | — | Optional enhancement; include if time permits. |
| R-CONCEPT-01 | Explain lecture concepts and link each to measured results: CPU vs GPU, VRAM, Prefill/Decode, KV cache, quantization, SafeTensors/GGUF, virtual memory, paging, mmap, AirLLM layer-wise loading | A §5.6, A §4 | PARTIALLY_EVIDENCED | README.md §9, reports/final_report.md §5 | — | Stage 7A: concepts mapped to *our* evidence with explicit measured-vs-discussed markers. Some (quantization, prefill/decode split) discussed not measured; honest. |
| R-CONCEPT-ROOFLINE | Classify each phase as **compute-bound vs memory-bound** (Roofline-style argument) | A §3 | PLANNED | reports/concepts.md, figures/bottleneck_map.* | R-NONREPRO | Central analytical claim of the report. |
| R-EXT-01 | Deliver **≥1 original extension** (bottleneck-shift map / quant Pareto frontier / AirLLM decision matrix / break-even simulator / LoRA-QLoRA / multi-model compare) | A §5.7 | PLANNED | reports/extension.md, figures/* | — | Exactly which extension chosen → ADR in DECISIONS.md. |
| R-RQ-01 | Explicitly answer the assignment's Research Questions (bottleneck cause, AirLLM vs paging, quant trade-offs, prefill/decode→TTFT/TPOT, price of running big locally, when API is better) | A §4 | PARTIALLY_EVIDENCED | reports/final_report.md §6, README.md §9 | — | Stage 7A: each RQ answered with evidence refs; gaps (quant trade-off, prefill/decode split) stated honestly as discussed-not-measured. |

## B. Deliverable, documentation & quality requirements (assignment + guidelines)

| requirement_id | requirement | source | status | evidence_path | risk | notes |
| --- | --- | --- | --- | --- | --- | --- |
| R-README-01 | README is the **technical report**: hardware, experiment, baseline vs AirLLM/quant summary, cost summary, concept↔result links, tables, graphs, reproduction steps, honest limitations, links to reports | A §8, G §2.1 | PARTIALLY_EVIDENCED | README.md, reports/final_report.md, docs/FINAL_GAP_AUDIT.md | — | Stage 7A: README rewritten as the 13-section technical report (tables + embedded figures + repro + limitations); extended companion + gap audit added. Completes once the experiment gaps (AirLLM/quant/7B) are closed or finalized as N/A. |
| R-DOC-PRD | `docs/PRD.md` present: context, user/problem, KPIs, acceptance criteria, functional & non-functional reqs, constraints | G §2.2 | PLANNED | docs/PRD.md | — | Stage 0 draft created; finalized Stage 1. |
| R-DOC-PLAN | `docs/PLAN.md` present: architecture (C4-style), data flow, ADR pointers, trade-offs, milestones | G §2.2 | PLANNED | docs/PLAN.md | — | Stage 0 draft created. |
| R-DOC-TODO | `docs/TODO.md` present: detailed tasks, priority, status, phases, owner, definition-of-done | G §2.2 | PLANNED | docs/TODO.md | — | Staged ledger created. |
| R-DOC-PRD-MECH | Per-mechanism PRD for the central algorithm (e.g. `docs/PRD_airllm_pipeline.md`, `docs/PRD_measurement.md`) | G §2.3 | PARTIALLY_EVIDENCED | docs/MEASUREMENT_DESIGN.md, docs/PRD_*.md | — | Stage 2A: `MEASUREMENT_DESIGN.md` written (metrics + result schema). Formal `PRD_measurement.md`/`PRD_airllm_pipeline.md` in Stage 2B. |
| R-ARCH-SDK | Layered architecture: single **SDK entry point** for all logic; GUI/CLI are thin layers | G §4.1 | PARTIALLY_EVIDENCED | src/ex05_airllm/sdk.py, tests/unit/test_sdk.py | R-PYENV | Stage 9A: a thin `sdk.py` facade exposes stable entry points (version, prompts, measurement loading, summary stats, cost/energy estimate) by **delegating** to existing modules — no logic duplicated, no model/network. Unit-tested; ≤150 lines. |
| R-ARCH-OOP | OOP, **no code duplication** (DRY); shared logic factored to base/mixin | G §4.2 | PLANNED | src/, code review | — | Enforced from Stage 3. |
| R-ARCH-GATEKEEPER | All external API calls route through a central **API Gatekeeper** (rate limit, retry, queue, logging); no direct calls bypass it | G §5 | N/A_WITH_RATIONALE (guard present) | src/ex05_airllm/api_gatekeeper.py, config/rate_limits.example.json, tests/unit/test_api_gatekeeper.py | R-SECRETS | Stage 9A: **no live external API is called anywhere** — On-Prem-vs-API cost is assumption-based (`COSTS.md`), not queried. A **fail-closed, disabled-by-default** `ApiGatekeeper` is implemented + unit-tested as the single choke point any *future* live path must use; it performs no network I/O. So the requirement is N/A today, with a guard in place. |
| R-FILELEN | Every code file ≤ **150 lines** (excl. blanks/comments); split if exceeded | G §3.2 | PARTIALLY_EVIDENCED | src/, tests/ | — | Stage 2A: all Python files pass the ≤150 check; re-verified as code grows. |
| R-LINT | `ruff check` passes with **zero errors**; config `line-length=100`, `target=py312`, rule set per guidelines | G §7.1 | PARTIALLY_EVIDENCED | pyproject.toml | — | Stage 2A: ruff configured; `ruff check .` + `format --check` clean on the skeleton. |
| R-TDD | TDD (red-green-refactor); every module has a matching test file; happy + error paths | G §6.1 | PARTIALLY_EVIDENCED | tests/ | — | Stage 2A: `tests/unit/test_version.py` (4 tests). Full happy/error coverage from Stage 3. |
| R-COVERAGE | Test coverage **≥ 85%**; `fail_under=85`; suite fails below threshold | G §6.2 | PARTIALLY_EVIDENCED | pyproject.toml | — | Stage 2A: `fail_under=85` configured; **100%** on the skeleton. `.coverage`/`htmlcov` git-ignored. |
| R-NOHARDCODE | No magic/hardcoded config values (URLs, limits, timeouts) in source; read from `config/` or env | G §7.2 | PARTIALLY_EVIDENCED | src/constants.py, config/ | R-SECRETS | Stage 2A: labels/schema centralized in `constants.py`; config template added. |
| R-CONFIG-ARCH | Config hierarchy: versioned `config/*` , `.env` (ignored), `.env-example` (committed) | G §7.3 | EVIDENCED | config/, .env-example | R-SECRETS | Stage 9A: **`.env-example` committed** (dummy values only; tokens optional, blank; explains committed results are inspectable without credentials). Versioned `config/*.example.*` present; `.env` git-ignored (`!.env-example` un-ignored). |
| R-VERSION | Version tracking starts at `1.0.0` in code + config | G §8.1 | PARTIALLY_EVIDENCED | src/ex05_airllm/version.py, config/ | — | Stage 2A: `1.0.0` in `version.py` + `pyproject` + config; consistency test-enforced. |
| R-UV | Dependencies managed **only with `uv`** (`uv sync`/`uv add`/`uv run`); `pyproject.toml` + `uv.lock` committed; no `pip`/`python -m` | G §8.4 | PARTIALLY_EVIDENCED | pyproject.toml, uv.lock | R-PYENV | Stage 2A: `pyproject.toml` + `uv.lock` created; `uv sync --extra dev` resolves (no conflicts). |
| R-PROMPTLOG | Maintain a **prompt engineering log** of significant prompts, context, outcomes, iterations | G §8.3 | PLANNED (started) | docs/PROMPTS.md | — | Prompt 001 recorded in Stage 0. |
| R-GIT-HISTORY | Clean, meaningful git history; branches per feature; descriptive commits; no `git add .` of junk | G §8.2, U | NEEDED_USER_INPUT | git log (later) | R-SECRETS | Repo not yet a git repo; user controls init/commit/push. |
| R-SECRETS-POLICY | No secrets/tokens committed ever; `.gitignore` covers `.env`, keys, credentials; secrets via `os.environ` | A §6.2, G §7.4 | PLANNED | .gitignore, .env-example | R-SECRETS | `.gitignore` in place; verified each audit. |
| R-NOFAKE | No fabricated results, graphs, hardware specs, or unsupported claims; negative results reported honestly | A §2, A §6.2, U | PLANNED | whole repo (audited) | R-OVERCLAIM, R-NONREPRO | Enforced by SUBMISSION_CHECKLIST + QUALITY gates. |
| R-REPRO | All runs reproducible: documented assumptions, seeds, commands, environment; numbers regenerate from scripts | A §5.5, A §10, G §9 | PARTIALLY_EVIDENCED | src/ex05_airllm/{result_schema,metrics,result_writer,prompts,env}.py + tests; results/stage3d_*.json | R-NONREPRO | 3D proved the writer end-to-end. **Stage 5A:** typed schema + `MetricsCollector` (TTFT/TPOT/throughput/runtime/peak-RAM, controlled-clock tested) + `ResultWriter` (stable header) + deterministic prompts + safe env metadata — the **measurement SDK is implemented & unit-tested** (no inference). Stage 5B runs real measurements. |
| R-LICENSE | README declares license & credits; course materials attributed | G §2.1 | PLANNED | README, DECISIONS.md | — | License decided before any public push. |

## C. Intake items — status after Stage 1A/1B

Hardware items were probed on 2026-06-19: Stage 1A inside Ubuntu WSL2, Stage 1B from the
Windows host via CIM (evidence: `docs/HARDWARE.md`). Items still marked `NEEDED_USER_INPUT`
**must never be guessed**. The `host` / `experiment` columns enforce the evidence boundary.

| id | input | status | host evidence (§A) | experiment (WSL) evidence | note |
| --- | --- | --- | --- | --- | --- |
| U-OS | OS & version | **EVIDENCED** | Windows 11 Pro 26200 | Ubuntu 24.04.4 LTS, WSL2 | both layers known |
| U-CPU | CPU model & threads | **EVIDENCED** | Ryzen AI 9 HX 370, 12c/24t | 24 threads, AVX-512/VNNI | same silicon, fully exposed |
| U-RAM | Total RAM | **EVIDENCED** | ≈ 24 GB physical | ≈ **11.24 GiB** (WSL2 cap) + 3 GiB swap | experiment budget = ~11 GiB |
| U-GPU | GPU usable for compute? | **PARTIALLY_EVIDENCED** | AMD Radeon 890M iGPU; no NVIDIA | no CUDA/ROCm; `llvmpipe` | host GPU exists but **not usable in WSL2** → CPU-only |
| U-VRAM | Total VRAM | **PARTIALLY_EVIDENCED** | iGPU shares RAM | 0 MB dedicated, none measurable | peak-VRAM → `N/A_WITH_RATIONALE` |
| U-DISK-TYPE | Physical disk type | **EVIDENCED** | **NVMe SSD** (~1 TB, Get-PhysicalDisk) | ext4 on WSL VHDX | media known; I/O speed still must be measured |
| U-DISK-FREE | Free disk space | **EVIDENCED** | ~1 TB device | **933 GB free** ext4 | ample for shards |
| U-GROUP | Course group code | **NEEDED_USER_INPUT** | — | — | required submission metadata |
| U-REPO-URL | GitHub repo URL | **PROVIDED** | — | — | `https://github.com/mohammedawad99/ex05-airllm` (`origin`, `main`) |
| U-HF-ACCESS | HF access **without a stored token** | **NEEDED_USER_INPUT** | — | — | confirm env-var / interactive login |
| U-ELEC | Electricity tariff (per kWh) | **NEEDED_USER_INPUT** | — | — | OPEX in Stage 6 cost model |
| U-HWCOST | Hardware cost / depreciation | **NEEDED_USER_INPUT** | — | — | CAPEX amortization / break-even |

## D. Items deliberately deferred (not yet `N/A`)

- **Final model identity** — deferred, not skipped. Decided in Stage 2 against the measured
  ~11.24 GiB RAM / CPU-only profile (R-HW-01 now PARTIALLY_EVIDENCED).
- **VRAM/GPU-specific requirements (R-MEAS-MEM VRAM part, R-COST-GPU-OPT)** — Stage 1A
  evidence shows no compute GPU and 0 MB dedicated VRAM, pointing toward
  `N/A_WITH_RATIONALE`; the formal determination is recorded in Stage 2 (kept open here
  because `lspci` was unavailable to fully enumerate hardware).
- **Quantization route on CPU (R-QUANT-CPU)** — AirLLM's `bitsandbytes` 4/8-bit path
  typically needs CUDA (unavailable); the CPU-compatible route (e.g., GGUF Q4/Q8) is an
  open Stage 2 design question.
- **Which original extension (R-EXT-01)** — candidate set listed; selection → ADR in Stage 6.

---

*Re-audit checkpoints: end of Stage 0 (this), and at the close of every subsequent stage.
Each transition to `DONE` must cite a real `evidence_path`.*
