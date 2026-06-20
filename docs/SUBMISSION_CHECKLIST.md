# Submission Checklist (Final Audit)

> **STATUS: STAGE 7B — pre-submission audit.** This is the gate the project must pass before
> submission. Each item carries an explicit status with an evidence path. **Honesty rules:** AirLLM
> generation is **not** marked DONE (blocked); quantization is **not** marked DONE (not a measured
> run); `Qwen2-7B` is **not** marked DONE (not downloaded/approved); the overall submission is
> **not** marked DONE until the final audit + user-controlled push are complete.

Status legend: **DONE** (complete, evidenced) · **PARTIAL** (real evidence, not complete) ·
**BLOCKED** (investigated, cannot complete in this environment) · **TODO** (not started) ·
**N/A** (justified out of scope).

---

## A. Repository foundation
- **DONE** — `README.md` is the submission-facing technical report (13 sections, tables, embedded
  figures, reproduction, limitations) — *evidence: README.md*
- **DONE** — `.gitignore` excludes secrets, model weights, caches, `.coverage`, `htmlcov`, large
  artifacts — *evidence: .gitignore*
- **DONE** — `docs/REQUIREMENTS_AUDIT.md` full traceability table incl. all `NEEDED_USER_INPUT` —
  *evidence: docs/REQUIREMENTS_AUDIT.md*
- **DONE** — Planning/process docs present (`PRD.md`, `PLAN.md`, `TODO.md`, `AI_WORKFLOW.md`,
  `PROMPTS.md`, `DECISIONS.md`, `RISKS.md`, `QUALITY.md`, `COSTS.md`) — *evidence: docs/*
- **DONE** — No forbidden placeholder/self-defeating phrases in README/docs — *evidence: text audit*

## B. Documentation completeness
- **DONE** — README is a full technical report: hardware, baseline-vs-AirLLM summary, cost summary,
  concept↔result links, tables, figures, reproduction, limitations, links to reports — *evidence:
  README.md, reports/final_report.md, docs/FINAL_GAP_AUDIT.md*
- **PARTIAL** — Per-mechanism design docs: `docs/MEASUREMENT_DESIGN.md` present; formal
  `PRD_measurement.md` / `PRD_airllm_pipeline.md` still to finalize — *evidence: docs/*
- **PARTIAL** — ADRs recorded with rationale (through ADR-0019); some deferred decisions
  (license/extension/provider) remain open — *evidence: docs/DECISIONS.md*
- **DONE** — Prompt log covers all significant prompts (through Prompt 021); decisions log current —
  *evidence: docs/PROMPTS.md, docs/DECISIONS.md*
- **PARTIAL** — README has a **License & credits** section. Project license not explicitly declared;
  the repository includes attribution/credits and no model weights (ADR-0106 left undecided; no
  license invented) — *evidence: README.md, docs/DECISIONS.md*

## C. Experiment evidence
- **DONE** — Hardware documented from the real machine (OS/CPU/RAM/GPU/VRAM/disk/free), host + WSL2
  — *evidence: docs/HARDWARE.md*
- **PARTIAL** — Model selected & justified vs hardware; final large pick deferred (ADR-0101a/0018) —
  *evidence: docs/MODEL_SELECTION.md*
- **PARTIAL** — Direct local baseline run (HF `transformers` CPU on `Qwen2-0.5B`, 6/6); baseline on
  a larger/selected model not done — *evidence: results/measurements/transformers_cpu_qwen2_0_5b/,
  docs/MEASUREMENT_RUNS.md*
- **BLOCKED** — AirLLM run completed → **not achieved**; investigated and root-caused (meta-device
  defect), structured failure evidence kept — *evidence: results/stage3*, results/stage4a*,
  results/analysis/airllm_failure_summary.json, docs/AIRLLM_PATCH_FEASIBILITY.md*
- **DONE (small model)** — Quantization compared **two ways**: Stage 9C **dynamic INT8 vs FP32**
  (Transformers) and Stage 10A **GGUF Q8_0 vs Q4_K_M** (`llama.cpp`, `Qwen2.5-0.5B-Instruct-GGUF`,
  12/12) — Q4 ~13% less RAM / 27% smaller file at ~equal throughput, coherent output. F16 GGUF
  excluded (>~1.2 GB cap). Small-model only; no large-model quant — *evidence:
  results/measurements/transformers_cpu_int8_quantization_qwen2_0_5b/,
  results/measurements/gguf_quantization_qwen2_5_0_5b/, docs/MEASUREMENT_RUNS.md §9–§10*
- **PARTIAL** — Metrics captured: runtime/throughput/peak-RAM **measured**; **TTFT measured**
  (Stage 9B streaming run) and **TPOT decode-only**; peak VRAM **N/A** (no GPU); energy
  **estimated** — *evidence: results/measurements/transformers_cpu_streaming_qwen2_0_5b/,
  docs/MEASUREMENT_RUNS.md §8, docs/ANALYSIS.md §3b*
- **TODO** — Qualitative output samples per config preserved — *evidence: reports/quality_samples.md
  (not yet created)*

## D. Analysis
- **DONE** — Tables + 4 figures generated from real committed data — *evidence: figures/,
  docs/ANALYSIS.md*
- **PARTIAL** — Compute- vs memory-bound (Roofline) argument made in prose; not a separate figure —
  *evidence: README.md §9, reports/final_report.md §5*
- **PARTIAL** — Cost model: API vs On-Prem + break-even figure under **assumed** pricing
  (`pricing_status=assumption_not_live_verified`); not market-verified — *evidence:
  results/analysis/cost_energy_estimate.json, figures/cost_break_even_estimate.png, docs/COSTS.md*
- **PARTIAL** — Required concepts explained and tied to evidence (measured-vs-discussed markers) —
  *evidence: README.md §9, reports/final_report.md §5*
- **PARTIAL** — Research Questions explicitly answered with honest gaps — *evidence:
  reports/final_report.md §6*
- **TODO** — ≥1 original extension delivered (candidate: break-even simulator, ADR-0105) —
  *evidence: reports/extension.md (not yet created)*

## E. Quality gates (see QUALITY.md)
- **DONE** — `ruff check .` zero errors; `ruff format --check .` clean — *evidence: run log*
- **DONE** — Tests pass (happy + error paths); coverage ≥85% — *evidence: pytest (84 passed, ~88%)*
- **DONE** — Every source file ≤150 code lines — *evidence: line-count audit*
- **DONE** — Config hierarchy: versioned `config/*.example.*`, `.env` git-ignored, **`.env-example`
  committed** (dummy values only) — *evidence: .env-example, config/*
- **DONE** — Thin **SDK facade** (`sdk.py`) fronts the pure logic (delegates, no duplication);
  no hardcoded secrets (env/config) — *evidence: src/ex05_airllm/sdk.py, tests/unit/test_sdk.py*
- **N/A** — Central **API gatekeeper**: no live external API is called anywhere; a fail-closed,
  disabled-by-default `ApiGatekeeper` guard is implemented + tested for any future path —
  *evidence: src/ex05_airllm/api_gatekeeper.py, config/rate_limits.example.json*
- **DONE** — Versioning starts at `1.0.0` (code + config, test-enforced) — *evidence:
  src/ex05_airllm/version.py*
- **DONE** — `uv` only; `pyproject.toml` + `uv.lock` committed — *evidence: repo root*

## F. Integrity & security
- **DONE** — No fabricated specs, numbers, or graphs anywhere — *evidence: text audit, every number
  traces to committed data*
- **DONE** — Estimates labelled as estimates; assumptions explicit (cost/energy/TPOT/TTFT) —
  *evidence: README §7–8, docs/ANALYSIS.md*
- **DONE** — No secrets/tokens committed; no model weights/shards tracked — *evidence: .gitignore,
  model-artifact audit*
- **DONE** — All reported numbers reproducible from documented commands — *evidence: README §10*
- **PARTIAL** — `REQUIREMENTS_AUDIT.md` re-audited each stage; final transition to DONE/N-A pending
  remaining experiment gaps — *evidence: docs/REQUIREMENTS_AUDIT.md, docs/FINAL_GAP_AUDIT.md*

## G. Submission mechanics (user-controlled)
- **N/A (repo)** — Group code is **handled manually by the student in the course submission system**;
  deliberately **not** stored in this repository and **does not block** repository readiness
- **DONE** — GitHub repo URL set; history clean/meaningful (per-stage commits, no `git add .`);
  Stages 0–7B committed + pushed through `e3d8537` — *evidence: git log, origin/main*
- **DONE** — Submission is **inspectable without any Hugging Face token** — committed
  results/analysis/figures + README explain the result with no model download — *evidence:
  results/, figures/, README §10*
- **TODO** — User confirms their own HF access (token-free) for any *optional* model re-download —
  *USER_INPUT_REQUIRED (not needed to inspect the submission)*
- **TODO** — Final push performed **only on explicit user request** (Stages 7A/7B already committed
  + pushed; only the final post-Stage-8 submission confirmation remains)

---

## Overall submission readiness: **READY_FOR_HONEST_SUBMISSION (with known limitations)** — Stage 9A

The repository is internally consistent, honest, and reproducible for the **measured Transformers
CPU path**, with AirLLM presented as a structured **negative result**. The report / checklist / gap
audit are complete and the submission is **inspectable with no Hugging Face token**. It is **not**
submitted, **not** 100% complete, and is **explicitly not claimed as ready for a self-assessment-100
grade** — the experimental gaps below remain open. The student completes submission manually.

**Closed since (Stages 9B/9C/10A):** **TTFT measured** (Stage 9B streaming, no download); **quantization
measured two ways** — dynamic INT8 vs FP32 (Stage 9C) and **GGUF Q8_0 vs Q4_K_M** (Stage 10A,
user-approved download; F16 excluded by the ~1.2 GB cap). Prior raw data unchanged; GGUF weights
git-ignored.

**Not ready for a self-assessment-100 claim until this is closed** (needs work / approval):
- **Large-model baseline / memory-pressure case — NOT_DONE** (no >RAM model run); requires explicit
  user approval before any `Qwen2-7B` download (Stage 10B).

Standing on the rest:
- **Stage 9A closures (DONE):** `.env-example` committed (dummy only); thin **SDK facade**
  (`sdk.py`); **API gatekeeper** is `N/A_WITH_RATIONALE` (no live API) with a fail-closed
  disabled-by-default guard implemented + tested.
- **Handled manually (outside the repo):** the course **group code** (entered in the course
  submission system; not stored here; does not block readiness).
- **ACCEPTABLE_LIMITATION (documented, not overstated):** AirLLM generation **BLOCKED**; TPOT
  approximate / VRAM N/A; cost/energy assumption-based.
- **OPTIONAL:** a Roofline figure and a broader qualitative table. One coherent committed smoke
  sample is surfaced in README §7 / `reports/final_report.md` §4. Original analytical extensions =
  AirLLM forensic analysis + assumption-based break-even (neither a measured AirLLM success).
- **License:** not explicitly declared; attribution/credits present, no model weights, none invented
  (ADR-0106).

No item above overstates: no AirLLM success, no `Qwen2-7B` run/download, no market-verified pricing,
no fabricated results, not submitted, not 100% complete, not claimed self-assessment-100 ready.
