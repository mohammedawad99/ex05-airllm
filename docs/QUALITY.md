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

**Stage 3A–4A update:** gates stay green with the smoke/prepare/compat modules added and the torch
pin `torch==2.4.1+cpu` — **21 tests pass, coverage ~98%, ruff/format clean, files ≤150 lines**
(`uv run pytest` / `ruff check .`). Model-loading code paths are `# pragma: no cover` (they need
real weights/network); their behaviour is evidenced instead by the raw run JSONs under `results/`.
These are smoke probes, not benchmarks. Stage 3D's HF CPU smoke succeeded and proves the
result-writing pipeline (R-REPRO partially evidenced); Stage 4A's `airllm_compat.py` shim is unit-
tested (no model) but did **not** unblock AirLLM CPU (ADR-0017).
