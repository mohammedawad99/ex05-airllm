# Quality Gates (Planned)

> **STATUS: STAGE 0 — PLANNED GATES ONLY.** This document defines the quality bars the
> project will be held to. **No gate has been run yet and no results are reported here.**
> Each gate lists how it is checked and where its evidence will live. Gates activate from
> the stage noted; in Stage 0 there is no code to lint or test.

---

## 1. Gate summary

| gate | requirement | tool / method | threshold | activates | evidence (later) |
| --- | --- | --- | --- | --- | --- |
| Q1 Lint | R-LINT | `uv run ruff check` | 0 errors | Stage 3 | CI/run log |
| Q2 Format | R-LINT | `uv run ruff format --check` | clean | Stage 3 | run log |
| Q3 Coverage | R-COVERAGE | `uv run pytest --cov` w/ `fail_under=85` | ≥85% | Stage 3 | `htmlcov/` (git-ignored), coverage report |
| Q4 Tests pass | R-TDD | `uv run pytest` (happy + error paths) | all pass | Stage 3 | pytest output |
| Q5 File length | R-FILELEN | line count per source file | ≤150 lines (excl. blanks/comments) | Stage 3 | audit script |
| Q6 No hardcoded values | R-NOHARDCODE | review + grep for literals (URLs/limits/timeouts) | none in source | Stage 3 | review notes |
| Q7 No secrets | R-SECRETS-POLICY | secret scan + `.gitignore` review | none committed | Stage 0 (policy) / every stage | `.gitignore`, scan log |
| Q8 Architecture | R-ARCH-SDK, R-ARCH-OOP, R-ARCH-GATEKEEPER | design review | SDK-fronted, DRY, all API via gatekeeper | Stage 3 | review notes |
| Q9 Versioning | R-VERSION | check `version.py` + config `"version"` | starts `1.00` | Stage 2 | files |
| Q10 Dep management | R-UV | repo has `pyproject.toml` + `uv.lock`; no `pip` usage | present, `uv` only | Stage 2 | files |
| Q11 Reproducibility | R-REPRO | re-run documented commands → same numbers | regenerates | Stage 5 | re-run log |
| Q12 No fabrication | R-NOFAKE | manual + checklist; every claim has evidence path | 100% | every stage | SUBMISSION_CHECKLIST |
| Q13 Docs present | R-DOC-* | presence + content review of `docs/` | all mandatory docs | Stage 0 → ongoing | `docs/` |

## 2. Planned tool configuration (added in Stage 2, not yet present)

Per guidelines §6–7, `pyproject.toml` will configure:

```toml
# ruff (R-LINT)
[tool.ruff]
line-length = 100
target-version = "py310"
[tool.ruff.lint]
select = ["E","F","W","I","N","UP","B","C4","SIM"]
ignore = ["E501"]

# coverage (R-COVERAGE)
[tool.coverage.run]
source = ["src"]
omit = ["src/main.py", "*/tests/*", "src/**/gui/*"]
[tool.coverage.report]
fail_under = 85
```

> This block documents the *intended* configuration. It is **not** active in Stage 0 — no
> `pyproject.toml` exists yet and nothing has been linted or tested.

## 3. TDD policy (from Stage 3)

- Red → Green → Refactor; tests written **before** implementation.
- Every module has a matching `tests/` file mirroring `src/` structure.
- Both happy paths and error/edge cases tested; external dependencies (HF, API, filesystem)
  mocked in unit tests.
- Test files also obey the ≤150-line rule; shared fixtures in `conftest.py`.

## 4. Reproducibility policy

- Fixed random seeds; exact commands and environment recorded.
- Raw run artifacts separated from curated summaries (raw is git-ignored).
- Measurement methodology pinned in `docs/PRD_measurement.md` (Stage 2) so metrics are
  defined unambiguously before any number is produced.

## 5. Current quality status

**Stage 0:** Q7 (secrets policy via `.gitignore`) and Q13 (docs presence) active.

**Stage 2A (skeleton now exists — gates configured and passing on the skeleton):**

| gate | Stage 2A result |
| --- | --- |
| Q1 Lint (`ruff check .`) | ✅ All checks passed |
| Q2 Format (`ruff format --check`) | ✅ Clean (4 files formatted) |
| Q3 Coverage (`fail_under=85`) | ✅ **100%** on `src/ex05_airllm` |
| Q4 Tests (`pytest`) | ✅ 4 passed |
| Q5 File length ≤150 code lines | ✅ All Python files pass |
| Q9 Versioning starts `1.0.0` | ✅ `version.py` + `pyproject` = `1.0.0`, test-enforced |
| Q10 Dep management (`uv`) | ✅ `pyproject.toml` + `uv.lock` present; `uv sync` resolves |

> These results are for the **skeleton only** (version/constants modules + version test).
> Q8 (full SDK/gatekeeper architecture), Q11 (reproducibility of real runs), and Q12 apply
> from Stage 3+ when experiment code and measurements exist. No experiment results are claimed.

**Stage 3A–6A update:** gates stay green with the smoke/prepare/compat modules, the **measurement
SDK**, the **runner**, and the **analysis** (`analyze_measurements`, `analysis_stats`,
`cost_model`) — **54 tests pass, coverage ~97%, ruff/format clean, files ≤150 lines** (`uv run
pytest` / `ruff check .`). Stage 5B ran a real **6/6** Transformers CPU measurement on Qwen2-0.5B
(`MEASUREMENT_RUNS.md`); Stage 6A computed stats/figures + an **assumption-based** cost/energy
estimate **from committed data** (`ANALYSIS.md`). These are small measurements/estimates, **not**
benchmarks or verified pricing; TTFT `None` / TPOT approximate / cost assumptions are documented,
never faked. Figure/`matplotlib` code is `# pragma: no cover`; the pure stats/cost math is tested.
Model-loading code paths are `# pragma: no cover` (they need real weights/network); their
behaviour is evidenced by the raw run JSONs under `results/`. The SDK is **pure/testable** — its
metric math is unit-tested with a controlled clock, no model/network. These are smoke probes, not
benchmarks. Stage 3D's HF CPU smoke proved the pipeline (R-REPRO partially evidenced); Stage 4A's
`airllm_compat.py` did **not** unblock AirLLM CPU (ADR-0017).

**Stage 7A/7B update (final report draft + polish):** docs-only — no code/test changes. README
became the 13-section technical report (embedded figures, resolvable evidence links);
`reports/final_report.md` + `docs/FINAL_GAP_AUDIT.md` added; `docs/SUBMISSION_CHECKLIST.md` rewritten
to real DONE/PARTIAL/BLOCKED/TODO statuses. Gates re-verified unchanged: **54 tests pass, ~97%
coverage, ruff check + format clean, all files ≤150 code lines.** No model run/download; raw
results/analysis/figures untouched; AirLLM stays blocked; no `Qwen2-7B`.

**Stage 9A update (low-risk rubric repairs; no model run/download):** added a thin **SDK facade**
(`sdk.py`, delegates only — no logic duplicated, no model/network), a fail-closed disabled-by-default
**`ApiGatekeeper`** guard (`api_gatekeeper.py`; no live API → `N/A_WITH_RATIONALE`), `config/
rate_limits.example.json`, and committed **`.env-example`** (dummy values). New unit tests cover both
modules (tmp_path, no network). Gates: **64 tests pass, ~97% coverage, ruff check + format clean, all
files ≤150 code lines.** Raw results/analysis/figures untouched; `pyproject.toml`/`uv.lock` unchanged.
Repo is **not** claimed self-assessment-100-ready — quantization/TTFT/large-model gaps stay open.

**Stage 9B update (real TTFT streaming measurement; cached model, no download):** added
`run_transformers_cpu_streaming_measurement.py` + pure `streaming_measurement.py` helpers + tests
(fake-timing). Ran a **separate** streaming run (6/6) measuring **real TTFT** via
`TextIteratorStreamer` on the cached Qwen2-0.5B (offline) → new dir
`results/measurements/transformers_cpu_streaming_qwen2_0_5b/`; Stage 5B raw data untouched. Gates:
**71 tests pass, ~97% coverage, ruff check + format clean, all files ≤150 code lines.** No download,
no Qwen2-7B, no AirLLM, no quantization; `pyproject.toml`/`uv.lock`/figures/analysis-JSON unchanged.

**Stage 9C Route A update (no-download dynamic INT8 quantization):** added
`quantization_measurement.py` (pure helpers) + `run_transformers_cpu_int8_quantization_measurement.py`
+ tests (fake data). Ran FP32 vs **PyTorch dynamic INT8** (12/12) on the cached Qwen2-0.5B (offline)
→ new dir `results/measurements/transformers_cpu_int8_quantization_qwen2_0_5b/`. Honest result: INT8
≈3.6× faster but **output quality degraded** (per-variant previews committed). Gates: **77 tests
pass, ~92% coverage, ruff check + format clean, all files ≤150 code lines.** No download, no new
dependency, no GGUF/Q4/Q8, no Qwen2-7B, no AirLLM; Stage 5B/9B raw + `pyproject.toml`/`uv.lock`/
figures/analysis-JSON unchanged. Quantization → PARTIALLY_EVIDENCED (dynamic INT8 only).

**Stage 10A update (user-approved GGUF low-bit sweep):** added `gguf_measurement.py` (pure helpers)
+ `run_gguf_quantization_measurement.py` + tests (fake data). Added the **only approved dependency**
`llama-cpp-python` via `uv add` (CPU build) and downloaded **only** the approved
`Qwen2.5-0.5B-Instruct-GGUF` Q8_0 + Q4_K_M files (git-ignored under `.local_models/`; F16 excluded by
the ~1.2 GB size cap). Ran **Q8_0 vs Q4_K_M** (12/12) →
`results/measurements/gguf_quantization_qwen2_5_0_5b/`. Gates: **84 tests pass, ~88% coverage, ruff
check + format clean, all files ≤150 code lines.** Only `pyproject.toml`/`uv.lock` changed (the
dependency); prior measurement dirs/analysis/figures unchanged; **no GGUF artifact tracked**. Low-bit
quantization now evidenced (small model); no large-model quant, no Qwen2-7B; AirLLM still blocked.

**Stage 10B update (guarded large-model memory-pressure baseline; user-approved):** added pure helpers
`large_model_pressure.py` + runner `run_large_model_pressure_baseline.py` + tests (fake data only, no
model/network). The real load path is `# pragma: no cover` (it needs the 7B weights). Ran a **guarded**
`Qwen/Qwen2.5-7B-Instruct` fp16 Transformers CPU attempt under a **13312 MiB** `RLIMIT_AS` child budget
→ **structured negative** `memory_budget_exceeded` (child hit `Cannot allocate memory` during load; no
generation) → new dir `results/measurements/large_model_pressure_qwen2_5_7b/`. Gates: **103 tests pass,
~88% coverage, ruff check + format clean, all files ≤150 code lines.** `pyproject.toml`/`uv.lock`/
figures/analysis-JSON unchanged; prior measurement dirs untouched; **no model artifacts tracked**
(7B weights git-ignored under `.hf_cache/`, never committed). The run was **not** rerun for docs.
**Guarded memory-budget attempt, not a full benchmark; no large-model performance claimed; AirLLM
stays blocked.** Repo still **not** claimed self-assessment-100-ready / 100% complete.

**Stage 11A update (final-analysis hardening; docs/code only, no model run/download):** added
`analysis_pipeline.py` (reads committed CSV/JSON → `final_evidence_summary.json` +
`roofline_classification.json` + 3 figures) and a **cost model v2** in `cost_model.py`
(`cost_model_v2.json` + `final_cost_break_even.png`) with **nonzero allocated CAPEX** and a meaningful
break-even, plus tests for both and for the two previously under-tested runners
(`run_gguf_quantization_measurement.py`, `run_transformers_cpu_int8_quantization_measurement.py`).
Gates: **123 tests pass, ~96% coverage (up from ~88%), ruff check + format clean, all files ≤150 code
lines.** Both runners now 100% line-covered. Raw measurement dirs, `reports/measurement_summary.md`,
`pyproject.toml`/`uv.lock`/`.env-example`/`config/` unchanged; **no model artifacts tracked**. Pricing/
tariff/FX are **dated assumptions (2026-06-21)**, not guaranteed pricing. AirLLM stays blocked; 10B
stays a guarded structured negative; repo still **not** 100-ready / 100% complete.
