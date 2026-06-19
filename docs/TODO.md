# TODO — Staged Task Ledger

> **STATUS: STAGE 0.** Live ledger; updated as work progresses. Statuses:
> `TODO` · `IN_PROGRESS` · `BLOCKED` · `DONE` · `DEFERRED`.
> Priorities: `P0` (blocker) · `P1` (core) · `P2` (enhancement).
> Each task lists its **Definition of Done (DoD)**. Requirement IDs trace to
> `REQUIREMENTS_AUDIT.md`.

---

## Stage 0 — Requirements & foundation  *(current)*

| id | task | pri | status | req | DoD |
| --- | --- | --- | --- | --- | --- |
| T0.1 | Read assignment + guidelines; extract requirements | P0 | DONE | all | assignment brief + guidelines read; requirements enumerated |
| T0.2 | Create `.gitignore` (secrets, weights, caches, coverage) | P0 | DONE | R-SECRETS-POLICY | File present; covers `.env`/keys/weights/`.coverage`/`htmlcov` |
| T0.3 | Create requirements traceability audit | P0 | DONE | all | Table w/ status+evidence+risk; all NEEDED_USER_INPUT listed |
| T0.4 | Draft PRD (Stage 0) | P0 | DONE | R-DOC-PRD | PRD with goals/KPIs/FR/NFR/acceptance |
| T0.5 | Draft PLAN with stages 0–7 + architecture | P0 | DONE | R-DOC-PLAN | Layered architecture + staged DoDs |
| T0.6 | Create this staged TODO ledger | P0 | DONE | R-DOC-TODO | Tasks with priority/status/phase/DoD |
| T0.7 | Create AI_WORKFLOW, PROMPTS (Prompt 001), DECISIONS | P0 | DONE | R-PROMPTLOG | Files present; Prompt 001 logged |
| T0.8 | Create RISKS register | P0 | DONE | — | All required risks + mitigations |
| T0.9 | Create QUALITY (planned gates only) | P0 | DONE | R-LINT,R-COVERAGE | Gates listed; no fake results |
| T0.10 | Create COSTS (methodology only) | P0 | DONE | R-COST-* | Method only; no numbers |
| T0.11 | Create SUBMISSION_CHECKLIST | P0 | DONE | R-NOFAKE | Final-audit checklist present |
| T0.12 | Create Stage 0 README (requirements-oriented) | P0 | DONE | R-README-01 | States Stage 0/no results/not submission-ready/next input |
| T0.13 | Validate: file listing, placeholder grep, status | P0 | DONE | R-NOFAKE | Greps clean; no forbidden phrases |

## Stage 1 — Approval & hardware capture

| id | task | pri | status | req | DoD |
| --- | --- | --- | --- | --- | --- |
| T1.1 | Collect hardware specs from user/machine | P0 | BLOCKED | R-HW-01 | OS/CPU/RAM/GPU/VRAM/disk/free recorded |
| T1.2 | Capture group code, repo URL, HF-access confirmation | P0 | BLOCKED | R-GIT-HISTORY,U-HF-ACCESS | All three recorded; no token stored |
| T1.3 | Resolve hardware-independent open questions (PRD §10) | P1 | TODO | R-DOC-PRD | OQ-1..4 dispositioned |
| T1.4 | Freeze PRD v1.0 after user approval | P0 | BLOCKED | R-DOC-PRD | User sign-off; version bumped |

## Stage 2 — Measurement architecture & model selection

| id | task | pri | status | req | DoD |
| --- | --- | --- | --- | --- | --- |
| T2.1 | Write `PRD_measurement.md` (metric defs + timing method) | P0 | TODO | R-DOC-PRD-MECH,R-MEAS-* | Every metric precisely defined |
| T2.2 | Write `PRD_airllm_pipeline.md` | P0 | TODO | R-DOC-PRD-MECH | Layer-wise + quant pipeline specified |
| T2.3 | Select & justify HF model vs hardware (ADR) | P0 | TODO | R-MODEL-01 | ADR with params/format/size rationale |
| T2.4 | Define `config/*.json` schema (versioned) + `.env-example` | P0 | TODO | R-CONFIG-ARCH,R-VERSION | Config schema v1.00; placeholders only |
| T2.5 | Set up `pyproject.toml`, `uv`, `ruff`, coverage(fail_under=85) | P0 | TODO | R-UV,R-LINT,R-COVERAGE | `uv sync` works; ruff/coverage configured |

## Stage 3 — Small pipeline proof (TDD)

| id | task | pri | status | req | DoD |
| --- | --- | --- | --- | --- | --- |
| T3.1 | SDK skeleton + thin CLI | P0 | TODO | R-ARCH-SDK | Single entry point; CLI thin |
| T3.2 | HardwareProbe (lscpu/free/nvidia-smi/df wrappers) | P0 | TODO | R-HW-01 | Emits hardware.md/json |
| T3.3 | MetricsCollector + FileStore (JSON) | P0 | TODO | R-MEAS-* | Valid metrics schema written |
| T3.4 | ApiGatekeeper (rate-limit/retry/queue/log) | P1 | TODO | R-ARCH-GATEKEEPER | All API calls routed; unit-tested |
| T3.5 | End-to-end run on a tiny model | P0 | TODO | R-REPRO | Produces metrics JSON for small model |
| T3.6 | Tests (happy+error), coverage ≥85%, ruff clean | P0 | TODO | R-TDD,R-COVERAGE,R-LINT | Gates green on implemented code |

## Stage 4 — Baseline experiment

| id | task | pri | status | req | DoD |
| --- | --- | --- | --- | --- | --- |
| T4.1 | Choose baseline path (Ollama vs HF) (ADR) | P1 | TODO | R-BASE-01 | ADR recorded |
| T4.2 | Run direct baseline; capture behavior incl. failure | P0 | TODO | R-BASE-01 | results/baseline/*.json + reports/baseline.md |
| T4.3 | Persist sample outputs for quality | P1 | TODO | R-MEAS-QUAL | Samples stored |

## Stage 5 — AirLLM + quantization

| id | task | pri | status | req | DoD |
| --- | --- | --- | --- | --- | --- |
| T5.1 | Run task via AirLLM (layer-wise) | P0 | TODO | R-AIR-01 | results/airllm/*.json |
| T5.2 | Quantization sweep (≥2 precisions) | P0 | TODO | R-QUANT-01 | results/quant/*.json per precision |
| T5.3 | Capture peak RAM/VRAM, TTFT, TPOT, throughput, runtime | P0 | TODO | R-MEAS-* | All metrics per config |
| T5.4 | Qualitative samples per precision | P1 | TODO | R-MEAS-QUAL | Samples stored |

## Stage 6 — Analysis, graphs, costs, extension

| id | task | pri | status | req | DoD |
| --- | --- | --- | --- | --- | --- |
| T6.1 | Tables + figures (latency/memory/throughput) | P0 | TODO | R-README-01 | figures/ populated from real data |
| T6.2 | Energy estimate with assumptions | P1 | TODO | R-MEAS-ENERGY | Method + numbers reproducible |
| T6.3 | Cost model + break-even graph (+optional cloud GPU) | P0 | TODO | R-COST-* | figures/breakeven.* + reports/costs.md |
| T6.4 | Bottleneck/Roofline classification | P1 | TODO | R-CONCEPT-ROOFLINE | compute- vs memory-bound argued w/ evidence |
| T6.5 | Concept explanations tied to evidence | P0 | TODO | R-CONCEPT-01 | reports/concepts.md |
| T6.6 | Original extension (ADR for which) | P1 | TODO | R-EXT-01 | Extension delivered + documented |
| T6.7 | Answer Research Questions | P0 | TODO | R-RQ-01 | Each RQ answered w/ evidence refs |

## Stage 7 — Final audit & submission

| id | task | pri | status | req | DoD |
| --- | --- | --- | --- | --- | --- |
| T7.1 | Assemble README technical report | P0 | TODO | R-README-01 | Tables/graphs/evidence map/repro/limits/links |
| T7.2 | Run SUBMISSION_CHECKLIST end-to-end | P0 | TODO | R-NOFAKE | 100% green |
| T7.3 | Final requirements re-audit | P0 | TODO | all | All DONE/N-A with evidence |
| T7.4 | Clean git history; user-initiated push | P0 | BLOCKED | R-GIT-HISTORY | Pushed only on explicit user request |

---

### Blocked / waiting on user
- **T1.1, T1.2** — need hardware specs + group code + repo URL + HF-access confirmation
  (the `NEEDED_USER_INPUT` items in `REQUIREMENTS_AUDIT.md` §C).
- **T7.4** — no commit/push until explicitly requested.
