# Final Gap Audit — EX05 (AirLLM)

> Requirement-by-requirement audit for the final-report stage. It maps each assignment area to a
> status and the committed evidence, and states the open blockers honestly. It is paired with
> `docs/REQUIREMENTS_AUDIT.md` (the granular traceability table) and `docs/SUBMISSION_CHECKLIST.md`.

## 1. Status

- **Stage:** final report **polished** (Stage 7B) — README is the submission-facing technical report
  with resolvable evidence links; `reports/final_report.md` is the extended companion; this audit is
  aligned with `docs/SUBMISSION_CHECKLIST.md`.
- **No new model runs, no downloads, no benchmark reruns, no fake results.** All evidence is
  already committed; the analysis pipeline regenerates from it.
- **Headline:** AirLLM CPU/Qwen2 is **blocked** (root-caused negative result); HF `transformers`
  **CPU** on `Qwen2-0.5B` is the measured, reproducible path. `Qwen2-7B` not downloaded/approved.

## 2. Requirement coverage

Status legend: **SATISFIED** · **PARTIALLY_SATISFIED** · **BLOCKED** · **NOT_DONE**.

| # | Requirement area | Status | Evidence files | Notes |
| --- | --- | --- | --- | --- |
| 1 | GitHub repo & reproducibility | SATISFIED | `README.md`, `pyproject.toml`, `uv.lock`, `src/`, `tests/`, `results/`, git history | Repo pushed (`origin/main`); the measured path + analysis regenerate via documented `uv` commands. Residual user inputs (group code, license) tracked separately. |
| 2 | Hardware characterization | SATISFIED | `docs/HARDWARE.md`, `README.md` §3 | Host + WSL2 measured; CPU-only determination; VRAM `N/A_WITH_RATIONALE`. |
| 3 | Model selection rationale | PARTIALLY_SATISFIED | `docs/MODEL_SELECTION.md`, `DECISIONS.md` ADR-0101a/0018 | Rationale documented; `Qwen2-0.5B` measured; `Qwen2-7B` deferred (not downloaded/approved); final large pick not finalized. |
| 4 | Direct baseline / local inference | PARTIALLY_SATISFIED | `results/measurements/transformers_cpu_qwen2_0_5b/`, `docs/MEASUREMENT_RUNS.md` | HF `transformers` CPU baseline on `Qwen2-0.5B` ran **6/6**; baseline on a larger/selected model not done. |
| 5 | AirLLM integration | BLOCKED | `results/stage3*`, `results/stage4a*`, `results/analysis/airllm_failure_summary.json`, `docs/AIRLLM_PATCH_FEASIBILITY.md` | Installs/imports; format fixed by re-shard; **CPU forward fails** (meta-device) — root-caused to AirLLM core param streaming. `any_success=false`. Not a success. |
| 6 | Quantization | NOT_DONE | `docs/TODO.md`, `docs/REQUIREMENTS_AUDIT.md` R-QUANT-01 | Discussed only; CUDA `bitsandbytes` unavailable, CPU GGUF route not executed. **No quantized run/measurement.** |
| 7 | Metrics (runtime, throughput, TPOT, TTFT, RAM, VRAM, energy) | PARTIALLY_SATISFIED | `results/measurements/...`, `results/analysis/...`, `docs/ANALYSIS.md` | runtime **SATISFIED**; throughput **SATISFIED**; RAM (RSS) **SATISFIED**; TPOT **PARTIALLY** (approx = gen_s/out_tokens); TTFT **NOT_DONE** (no streaming hook → `None`); VRAM **N/A** (no GPU compute); energy **PARTIALLY** (assumption-based estimate). |
| 8 | Cost analysis (API / On-Prem / break-even) | PARTIALLY_SATISFIED | `results/analysis/cost_energy_estimate.json`, `figures/cost_break_even_estimate.png`, `docs/COSTS.md` | Computed under explicit assumptions; `pricing_status=assumption_not_live_verified`. CAPEX=0 sensitivity stated. Not market-verified. |
| 9 | Graphs / figures | SATISFIED | `figures/*.png`, `docs/ANALYSIS.md` §4 | 4 plain-matplotlib figures generated from committed data (runtime, throughput, peak RAM, break-even). |
| 10 | Lecture concept linkage | PARTIALLY_SATISFIED | `README.md` §9, `reports/final_report.md` §5–6 | Concepts tied to *our* evidence with measured-vs-discussed markers; some (quantization, prefill/decode split) discussed, not measured. |
| 11 | AI workflow documentation | SATISFIED | `docs/AI_WORKFLOW.md`, `docs/PROMPTS.md` | Prompt-engineering log maintained per stage. |
| 12 | Quality gates / tests | SATISFIED | `tests/`, `pyproject.toml`, `docs/QUALITY.md` | 64 tests, ~97% coverage (≥85), ruff check + format clean, every file ≤150 code lines. |
| 13 | Secrets / model-weight hygiene | SATISFIED | `.gitignore`, `.env-example`, repo audit | No secrets/tokens committed; `.env-example` has dummy values only; **no model weights/shards tracked**; weights/caches/raw logs git-ignored. |
| 14 | SDK facade & config hygiene | SATISFIED | `src/ex05_airllm/sdk.py`, `.env-example`, `tests/unit/test_sdk.py` | Stage 9A: thin SDK facade delegating to existing modules (no logic duplicated, no model/network); `.env-example` committed. |
| 15 | API gatekeeper | N/A_WITH_RATIONALE | `src/ex05_airllm/api_gatekeeper.py`, `config/rate_limits.example.json`, `tests/unit/test_api_gatekeeper.py` | No live external API is called anywhere (cost is assumption-based); a fail-closed, disabled-by-default guard is implemented + tested for any future path. |
| 16 | Quantization measured run | NOT_DONE | `docs/PLAN.md` Stage 9C | No quantized inference executed; planned GGUF/CPU, **requires explicit user approval before any download**. |
| 17 | TTFT measurement | NOT_DONE | `docs/PLAN.md` Stage 9B | No streaming hook (`None`); Stage 9B can measure on the already-cached `Qwen2-0.5B`, **no new download**. |
| 18 | Large-model memory-pressure case | NOT_DONE | `docs/PLAN.md` | No >RAM model run; **requires explicit user approval before any `Qwen2-7B` download**. |

## 3. Explicit blockers

- **AirLLM CPU/Qwen2 — BLOCKED.** Core meta→CPU parameter-streaming defect; torch and rotary ruled
  out; minimal local shim infeasible (ADR-0017). Documented negative result, not a success.
- **`Qwen2-7B` — DEFERRED.** Not downloaded, not approved (`download_approved=false`); the same
  AirLLM core path would fail identically, so a ~15 GB download to reproduce a known blocker is
  unjustified.
- **Quantization — NOT_DONE as a measured run.** No quantized inference executed; only discussed.
- **TTFT — MISSING.** The non-streaming `generate()` path exposes no first-token hook; recorded
  `None`, never estimated. TPOT is therefore approximate.

## 4. Risk assessment for grading

- **Biggest risk:** AirLLM did **not** successfully generate, so the assignment's "headline" AirLLM
  run is a negative result; a grader expecting a working AirLLM demo may see that as a gap.
- **Mitigation:** a deep, reproducible **root-cause analysis** of the AirLLM CPU failure; structured
  raw-JSON failure evidence; a **working measured fallback** (Transformers CPU, real repeatable
  numbers); an assumption-marked cost/energy estimate; and **zero fabricated claims**. The
  assignment explicitly values a well-analyzed negative result over an unsupported positive claim,
  which is exactly the posture taken here. Tracked as R-GRADE-AIRLLM in `docs/RISKS.md`.

## 5. Before-submission action list

1. **Final requirement re-audit** — reconcile this gap audit with `REQUIREMENTS_AUDIT.md` and
   `docs/SUBMISSION_CHECKLIST.md` (done in Stage 7B; re-run at the very end before push).
2. **README polish** — *done (Stage 7B):* evidence links resolve, figures embed with correct
   relative paths, numbers match the committed analysis JSON, tone is honest-not-self-defeating.
3. **Optional screenshot check** — verify the 4 figures render and are legible.
4. **No new heavy downloads** — do **not** pull `Qwen2-7B` or other weights; the report stands on
   the committed `Qwen2-0.5B` evidence.
5. **Provide residual user inputs** — group code, token-free HF access confirmation, and (if a
   verified cost claim is wanted) a real electricity tariff + hardware cost to replace the
   assumptions.

> This audit asserts **no** AirLLM success, **no** market-verified pricing, and **no** large-model
> performance. It records what is satisfied, what is partial, what is blocked, and what is not done.

## 6. Readiness verdict (Stage 9A)

**READY_FOR_HONEST_SUBMISSION (with known limitations)** — *not submitted, not 100% complete, and
explicitly **not** claimed ready for a self-assessment-100 grade.* The report is complete and
token-free-inspectable; the course **group code** is handled manually by the student outside the repo
(does not block readiness).

**Stage 9A closures (low-risk, no model run):** `.env-example` committed (dummy only); thin **SDK
facade** (`sdk.py`); **API gatekeeper** `N/A_WITH_RATIONALE` with a fail-closed disabled-by-default
guard implemented + tested.

**Still open before any self-assessment-100 claim** (rows 16–18 above):
- **Quantization measured run — NOT_DONE** → Stage 9C (GGUF/CPU), **requires user approval before any
  download**.
- **TTFT — NOT_DONE/PARTIAL** → Stage 9B, measurable on the **already-cached** `Qwen2-0.5B`, no new
  download.
- **Large-model memory-pressure baseline — NOT_DONE** → requires user approval before any `Qwen2-7B`
  download.

AirLLM remains **BLOCKED** (structured negative result, not a success); the original analytical
extensions are the AirLLM forensic analysis + the assumption-based break-even analysis; license not
explicitly declared (ADR-0106; none invented). See `docs/SUBMISSION_CHECKLIST.md` for the full
per-item classification.
