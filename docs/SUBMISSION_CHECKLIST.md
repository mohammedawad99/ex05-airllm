# Submission Checklist (Final Audit)

> **STATUS: STAGE 0.** This is the gate the project must pass before submission. In Stage 0
> only the foundation items are checkable; the rest are listed so the bar is known from day
> one. Mark `[x]` only with a real evidence path. Nothing is pre-checked as passing.

Legend: `[ ]` not done · `[~]` in progress · `[x]` done (with evidence) · `[N/A]` justified.

---

## A. Repository foundation (Stage 0)
- [x] `README.md` present, states Stage 0 / no results / not submission-ready / next input = hardware — *evidence: README.md*
- [x] `.gitignore` excludes secrets, model weights, caches, `.coverage`, `htmlcov`, large artifacts — *evidence: .gitignore*
- [x] `docs/REQUIREMENTS_AUDIT.md` with full traceability table + all `NEEDED_USER_INPUT` — *evidence: docs/REQUIREMENTS_AUDIT.md*
- [x] `docs/PRD.md`, `docs/PLAN.md` (stages 0–7), `docs/TODO.md` present — *evidence: docs/*
- [x] `docs/AI_WORKFLOW.md`, `docs/PROMPTS.md` (Prompt 001), `docs/DECISIONS.md` present — *evidence: docs/*
- [x] `docs/RISKS.md` (incl. all 8 required risks), `docs/QUALITY.md`, `docs/COSTS.md` present — *evidence: docs/*
- [x] No forbidden placeholder phrases in README/docs/.gitignore — *evidence: validation grep*
- [x] No implementation code, no model downloads, no dependencies installed, no secrets, no commit/push in Stage 0

## B. Documentation completeness (final)
- [ ] README is a full technical report: hardware, experiment, baseline vs AirLLM/quant summary, cost summary, concept↔result links, tables, graphs, reproduction, limitations, links to reports
- [ ] Per-mechanism PRDs present (`PRD_airllm_pipeline.md`, `PRD_measurement.md`)
- [ ] All ADRs recorded with rationale; deferred decisions resolved
- [ ] Prompt log covers all significant prompts; decisions log current
- [ ] License & credits declared

## C. Experiment evidence (final)
- [ ] Hardware documented from the real machine (OS/CPU/RAM/GPU/VRAM/disk/free) — *evidence: reports/hardware.md*
- [ ] Model selected & justified vs hardware (ADR)
- [ ] Direct baseline run; behavior incl. any failure documented — *evidence: results/baseline/, reports/baseline.md*
- [ ] AirLLM run completed — *evidence: results/airllm/*
- [ ] Quantization sweep (≥2 levels) — *evidence: results/quant/*
- [ ] Metrics captured per config: TTFT, TPOT/ITL, throughput, peak RAM, peak VRAM*, runtime, energy estimate — *evidence: results/**/metrics.json*
- [ ] Qualitative output samples per config — *evidence: reports/quality_samples.md*

## D. Analysis (final)
- [ ] Tables + figures generated from real data — *evidence: figures/*
- [ ] Compute- vs memory-bound (Roofline) classification — *evidence: reports/concepts.md*
- [ ] Cost model: API vs On-Prem + break-even graph (+ optional cloud GPU) — *evidence: figures/breakeven.*, reports/costs.md*
- [ ] All required concepts explained and tied to evidence
- [ ] Research Questions explicitly answered
- [ ] ≥1 original extension delivered — *evidence: reports/extension.md*

## E. Quality gates (final — see QUALITY.md)
- [ ] `ruff check` zero errors; `ruff format --check` clean
- [ ] Tests pass (happy + error paths); coverage ≥85% (`fail_under=85`)
- [ ] Every source file ≤150 lines
- [ ] No hardcoded config values; secrets via `os.environ`
- [ ] Layered/SDK architecture; all API calls via gatekeeper; OOP/DRY
- [ ] Versioning starts at `1.00`
- [ ] `uv` only; `pyproject.toml` + `uv.lock` committed

## F. Integrity & security (every stage)
- [ ] No fabricated specs, numbers, or graphs anywhere
- [ ] Estimates labelled as estimates; assumptions explicit
- [ ] No secrets/tokens committed; `.env-example` placeholders only
- [ ] All numbers reproducible from documented commands
- [ ] `REQUIREMENTS_AUDIT.md` fully re-audited: every requirement `DONE`/`N/A_WITH_RATIONALE` with evidence

## G. Submission mechanics (Stage 7 — user-controlled)
- [ ] Group code recorded — *NEEDED_USER_INPUT*
- [ ] GitHub repo URL set; clean, meaningful git history — *NEEDED_USER_INPUT*
- [ ] Hugging Face access confirmed without storing a token — *NEEDED_USER_INPUT*
- [ ] Final push performed **only on explicit user request**

---

*Stage 0 status: Section A complete; Sections B–G open by design (work not yet started).
No item outside Section A is checked, and none is claimed as passing.*
