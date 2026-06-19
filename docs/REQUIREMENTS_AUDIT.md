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
| R-MODEL-01 | Select a Hugging Face model **deliberately larger** than local memory, justified against the hardware (params, format, size) | A §5.1 | PLANNED | docs/DECISIONS.md (ADR), reports/model_selection.md | R-MODELSIZE, R-AIRLLM-COMPAT | Choice intentionally deferred until R-HW-01 is resolved. |
| R-BASE-01 | Attempt a **direct baseline** (Ollama or HF `transformers`); document live behavior incl. failure/slowdown | A §5.2 | PLANNED | results/baseline/*.json, reports/baseline.md | R-NONREPRO | The baseline is the reference the other runs are compared against. |
| R-AIR-01 | Run the same task with **AirLLM** (layer-wise loading) | A §5.3 | PLANNED | results/airllm/*.json, reports/airllm.md | R-AIRLLM-COMPAT, R-PYENV | Show how it changes resource allocation vs paging. |
| R-QUANT-01 | Apply and compare **quantization** levels (e.g. FP16, Q8, Q4) and document the effect of each | A §5.3 | PLANNED | results/quant/*.json, figures/quant_pareto.* | R-AIRLLM-COMPAT | At least two precisions compared. |
| R-MEAS-TTFT | Measure **TTFT** (Time To First Token) — prefill + KV-cache build cost | A §5.4 | PLANNED | results/**/metrics.json | R-NONREPRO | Methodology in QUALITY.md. |
| R-MEAS-TPOT | Measure **TPOT / ITL** (per-output-token latency / inter-token latency) | A §5.4 | PLANNED | results/**/metrics.json | R-NONREPRO | Decode-phase, memory-movement bound. |
| R-MEAS-THRU | Measure **throughput** (tokens/sec) | A §5.4 | PLANNED | results/**/metrics.json | R-IO | — |
| R-MEAS-MEM | Measure **peak RAM** and **peak VRAM** (VRAM only if a GPU is usable for compute) | A §5.4 | PLANNED | results/**/metrics.json | R-OVERCLAIM | VRAM may be `N/A_WITH_RATIONALE` if no usable GPU compute backend (host iGPU exists; feasibility under review — `GPU_FEASIBILITY.md`). |
| R-MEAS-TIME | Measure **total runtime** (wall clock) | A §5.4 | PLANNED | results/**/metrics.json | — | — |
| R-MEAS-ENERGY | Provide **estimated energy use** with stated assumptions | A §5.4 | PLANNED | results/**/energy.json, COSTS.md | R-OVERCLAIM | Estimation method + assumptions documented; flagged as estimate. |
| R-MEAS-QUAL | **Qualitative** assessment of output quality per quantization level | A §5.4 | PLANNED | reports/quality_samples.md | — | Sample outputs preserved as evidence. |
| R-COST-API | Compute external-API cost per request (input+output tokens) for a chosen provider | A §5.5 | PLANNED | reports/costs.md, figures/breakeven.* | R-OVERCLAIM | Provider pricing dated & cited. |
| R-COST-ONPREM | Compute On-Prem cost: CAPEX amortized + OPEX (electricity, maintenance) per request | A §5.5 | PLANNED | reports/costs.md | R-OVERCLAIM | All assumptions explicit & reproducible. |
| R-COST-BREAKEVEN | Find and graph the **break-even point** (requests/tokens) On-Prem vs API | A §5.5 | PLANNED | figures/breakeven.*, reports/costs.md | R-OVERCLAIM | Plotted on one comparison graph. |
| R-COST-GPU-OPT | *(Optional)* Add a third line: cloud GPU rental cost on the break-even graph | A §5.5 (optional) | PLANNED | figures/breakeven.* | — | Optional enhancement; include if time permits. |
| R-CONCEPT-01 | Explain lecture concepts and link each to measured results: CPU vs GPU, VRAM, Prefill/Decode, KV cache, quantization, SafeTensors/GGUF, virtual memory, paging, mmap, AirLLM layer-wise loading | A §5.6, A §4 | PLANNED | reports/concepts.md, README | — | Concepts must connect to *our* evidence, not be generic. |
| R-CONCEPT-ROOFLINE | Classify each phase as **compute-bound vs memory-bound** (Roofline-style argument) | A §3 | PLANNED | reports/concepts.md, figures/bottleneck_map.* | R-NONREPRO | Central analytical claim of the report. |
| R-EXT-01 | Deliver **≥1 original extension** (bottleneck-shift map / quant Pareto frontier / AirLLM decision matrix / break-even simulator / LoRA-QLoRA / multi-model compare) | A §5.7 | PLANNED | reports/extension.md, figures/* | — | Exactly which extension chosen → ADR in DECISIONS.md. |
| R-RQ-01 | Explicitly answer the assignment's Research Questions (bottleneck cause, AirLLM vs paging, quant trade-offs, prefill/decode→TTFT/TPOT, price of running big locally, when API is better) | A §4 | PLANNED | README, reports/concepts.md | — | Each RQ answered with evidence references. |

## B. Deliverable, documentation & quality requirements (assignment + guidelines)

| requirement_id | requirement | source | status | evidence_path | risk | notes |
| --- | --- | --- | --- | --- | --- | --- |
| R-README-01 | README is the **technical report**: hardware, experiment, baseline vs AirLLM/quant summary, cost summary, concept↔result links, tables, graphs, reproduction steps, honest limitations, links to reports | A §8, G §2.1 | PLANNED | README.md | — | Tables & figures embedded in README itself. |
| R-DOC-PRD | `docs/PRD.md` present: context, user/problem, KPIs, acceptance criteria, functional & non-functional reqs, constraints | G §2.2 | PLANNED | docs/PRD.md | — | Stage 0 draft created; finalized Stage 1. |
| R-DOC-PLAN | `docs/PLAN.md` present: architecture (C4-style), data flow, ADR pointers, trade-offs, milestones | G §2.2 | PLANNED | docs/PLAN.md | — | Stage 0 draft created. |
| R-DOC-TODO | `docs/TODO.md` present: detailed tasks, priority, status, phases, owner, definition-of-done | G §2.2 | PLANNED | docs/TODO.md | — | Staged ledger created. |
| R-DOC-PRD-MECH | Per-mechanism PRD for the central algorithm (e.g. `docs/PRD_airllm_pipeline.md`, `docs/PRD_measurement.md`) | G §2.3 | PLANNED | docs/PRD_*.md | — | Authored in Stage 2 once measurement design is fixed. |
| R-ARCH-SDK | Layered architecture: single **SDK entry point** for all logic; GUI/CLI are thin layers | G §4.1 | PLANNED | src/, docs/PLAN.md | R-PYENV | Design in PLAN; code in Stage 3+. |
| R-ARCH-OOP | OOP, **no code duplication** (DRY); shared logic factored to base/mixin | G §4.2 | PLANNED | src/, code review | — | Enforced from Stage 3. |
| R-ARCH-GATEKEEPER | All external API calls route through a central **API Gatekeeper** (rate limit, retry, queue, logging); no direct calls bypass it | G §5 | PLANNED | src/.../gatekeeper.py, config/rate_limits.json | R-SECRETS | Needed for API-cost calls in Stage 4/6. |
| R-FILELEN | Every code file ≤ **150 lines** (excl. blanks/comments); split if exceeded | G §3.2 | PLANNED | src/, tests/ | — | Checked in final audit. |
| R-LINT | `ruff check` passes with **zero errors**; config `line-length=100`, `target=py310`, rule set per guidelines | G §7.1 | PLANNED | pyproject.toml, CI/log | — | Config added in Stage 3. |
| R-TDD | TDD (red-green-refactor); every module has a matching test file; happy + error paths | G §6.1 | PLANNED | tests/ | — | From Stage 3. |
| R-COVERAGE | Test coverage **≥ 85%**; `fail_under=85`; suite fails below threshold | G §6.2 | PLANNED | pyproject.toml, htmlcov/ | — | `.coverage`/`htmlcov` git-ignored. |
| R-NOHARDCODE | No magic/hardcoded config values (URLs, limits, timeouts) in source; read from `config/` or env | G §7.2 | PLANNED | src/, config/ | R-SECRETS | Constants in `constants.py`/Enum. |
| R-CONFIG-ARCH | Config hierarchy: `config/*.json` (versioned), `.env` (ignored), `.env-example` (committed) | G §7.3 | PLANNED | config/, .env-example | R-SECRETS | `.env-example` added when secrets first needed. |
| R-VERSION | Version tracking starts at `1.00` in code + config + rate-limit config | G §8.1 | PLANNED | src/.../version.py, config/*.json | — | — |
| R-UV | Dependencies managed **only with `uv`** (`uv sync`/`uv add`/`uv run`); `pyproject.toml` + `uv.lock` committed; no `pip`/`python -m` | G §8.4 | PLANNED | pyproject.toml, uv.lock | R-PYENV | No deps installed in Stage 0. |
| R-PROMPTLOG | Maintain a **prompt engineering log** of significant prompts, context, outcomes, iterations | G §8.3 | PLANNED (started) | docs/PROMPTS.md | — | Prompt 001 recorded in Stage 0. |
| R-GIT-HISTORY | Clean, meaningful git history; branches per feature; descriptive commits; no `git add .` of junk | G §8.2, U | NEEDED_USER_INPUT | git log (later) | R-SECRETS | Repo not yet a git repo; user controls init/commit/push. |
| R-SECRETS-POLICY | No secrets/tokens committed ever; `.gitignore` covers `.env`, keys, credentials; secrets via `os.environ` | A §6.2, G §7.4 | PLANNED | .gitignore, .env-example | R-SECRETS | `.gitignore` in place; verified each audit. |
| R-NOFAKE | No fabricated results, graphs, hardware specs, or unsupported claims; negative results reported honestly | A §2, A §6.2, U | PLANNED | whole repo (audited) | R-OVERCLAIM, R-NONREPRO | Enforced by SUBMISSION_CHECKLIST + QUALITY gates. |
| R-REPRO | All runs reproducible: documented assumptions, seeds, commands, environment; numbers regenerate from scripts | A §5.5, A §10, G §9 | PLANNED | README "Reproduction", experiments/ | R-NONREPRO | Reproduction section is mandatory. |
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
