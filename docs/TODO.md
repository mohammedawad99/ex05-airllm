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

## Stage 1A — Hardware intake & planning calibration  *(documentation tasks complete)*

| id | task | pri | status | req | DoD |
| --- | --- | --- | --- | --- | --- |
| T1A.1 | Run read-only hardware discovery probes | P0 | DONE | R-HW-01 | Real outputs captured (OS/CPU/RAM/GPU/disk/python/uv) |
| T1A.2 | Create `docs/HARDWARE.md` from terminal evidence | P0 | DONE | R-HW-01 | Evidence doc with quoted outputs; no invented specs |
| T1A.3 | Update audit: hardware items → PARTIALLY_EVIDENCED | P0 | DONE | R-HW-01 | Legend + R-HW-01 + §C updated to evidence |
| T1A.4 | Calibrate PRD/PLAN to measured constraints | P0 | DONE | R-DOC-PRD,R-DOC-PLAN | PRD C1/PLAN §0 reflect ~11 GiB/CPU-only |
| T1A.5 | Add hardware-revealed risks | P0 | DONE | — | R-NOGPU/WSL-MEM/QUANT-CPU/WSL-DISK/EVID-GAP added |
| T1A.6 | Record evidence-backed decision (ADR) | P0 | DONE | — | ADR-0007/0008 in DECISIONS.md |
| T1A.7 | Point README to HARDWARE.md; keep status honest | P0 | DONE | R-README-01 | README links + status updated |
| T1A.8 | Log this prompt in PROMPTS.md | P0 | DONE | R-PROMPTLOG | Prompt 002 recorded |

> Note: hardware is captured but **not complete** — group code (U-GROUP), HF access
> (U-HF-ACCESS), and cost assumptions (U-ELEC/U-HWCOST) remain `NEEDED_USER_INPUT`.
> No experimental requirement is marked DONE.

## Stage 1B — Host hardware verification  *(documentation tasks complete)*

| id | task | pri | status | req | DoD |
| --- | --- | --- | --- | --- | --- |
| T1B.1 | Collect host-side Windows evidence via PowerShell/CIM | P0 | DONE | R-HW-01 | OS/CPU/RAM/GPU/disk + wsl status captured; failures recorded honestly |
| T1B.2 | Add host/WSL/experiment boundary sections to `HARDWARE.md` | P0 | DONE | R-HW-01 | §0 boundary, §A host, §B experiment availability, §7 consequences |
| T1B.3 | Resolve U-DISK-TYPE from host (NVMe SSD) | P1 | DONE | R-HW-01 | Host `Get-PhysicalDisk` evidence recorded; I/O still to be measured |
| T1B.4 | Audit: set EVIDENCED vs PARTIALLY_EVIDENCED per layer | P0 | DONE | R-HW-01 | §C host/experiment columns; GPU/VRAM stay PARTIALLY_EVIDENCED |
| T1B.5 | Update RISKS (host-vs-execution mismatch, host-GPU-unusable) | P0 | DONE | — | R-NOGPU/WSL-MEM/WSL-DISK reconciled |
| T1B.6 | Record ADR-0009 (select against execution env, not host) | P0 | DONE | — | ADR in DECISIONS.md |
| T1B.7 | Update README + log Prompt 003 | P0 | DONE | R-README-01,R-PROMPTLOG | README host/exec distinction; Prompt 003 |

> Stage 1B confirms the evidence boundary. **No model selected; no experimental requirement
> marked DONE.** U-DISK-TYPE is now host-EVIDENCED (NVMe SSD); actual I/O speed is still a
> Stage 4/5 measurement, not a claim.

## Stage 1C-A — GPU feasibility diagnostics  *(diagnostic tasks complete)*

| id | task | pri | status | req | DoD |
| --- | --- | --- | --- | --- | --- |
| T1C.1 | Run read-only GPU diagnostics (host CIM/dxdiag + WSL dxg/rocm/torch) | P1 | DONE | R-HW-01 | Evidence captured; no installs |
| T1C.2 | Create `docs/GPU_FEASIBILITY.md` (status/evidence/paths/questions) | P1 | DONE | R-HW-01 | Required 6-section structure present |
| T1C.3 | Record candidate backend paths with status | P1 | DONE | — | PLANNED/POSSIBLE/BLOCKED/NEEDS_INSTALL_CHECK assigned |
| T1C.4 | Reference feasibility from HARDWARE/RISKS/DECISIONS | P1 | DONE | — | HARDWARE §4 link; R-NOGPU re-opened; ADR-0010 |
| T1C.5 | Log Prompt 004 | P1 | DONE | R-PROMPTLOG | Prompt 004 recorded |
| T1C.6 | **Resolve §5 compatibility questions** (AirLLM CPU/DirectML; torch-directml; quant) | P1 | TODO | R-AIR-01,R-QUANT-CPU | Documented research findings before backend ADR |
| T1C.7 | Make final execution-backend decision (ADR) | P0 | TODO | — | Evidence-backed backend ADR (revisits ADR-0008) |

> Diagnostics only — **no installs, no benchmarks, no backend decision, no model selected, no
> experimental requirement DONE.** T1C.6/T1C.7 remain open and gate the backend choice.

## Stage 1C-B — Isolated DirectML compatibility probe  *(probe complete)*

| id | task | pri | status | req | DoD |
| --- | --- | --- | --- | --- | --- |
| T1CB.1 | Enumerate Windows Python versions for torch-directml | P1 | DONE | — | `py -0p` recorded (3.13, 3.9) |
| T1CB.2 | Build throwaway Windows venv **outside repo** (Py 3.9) | P1 | DONE | — | venv in `%TEMP%`, project env untouched |
| T1CB.3 | Install + smoke-test torch-directml (device + matmul) | P1 | DONE | — | Install OK; **import fails** (3.9<3.10); 0.2.4 retried, same |
| T1CB.4 | Avoid model download; gate transformers on DirectML success | P1 | DONE | — | transformers not tested (DirectML failed); no model fetched |
| T1CB.5 | Tear down throwaway env | P1 | DONE | — | venv removed; WSL env re-verified torch-free |
| T1CB.6 | Record results + update backend statuses | P1 | DONE | — | GPU_FEASIBILITY §3b; Windows DirectML → BLOCKED |
| T1CB.7 | Update RISKS/DECISIONS; log Prompt 005 | P1 | DONE | — | R-NOGPU/ADR-0010 updated; Prompt 005 |

> Isolated probe only — **no project deps changed, no project code, no model download, no
> AirLLM/Ollama, no benchmark, no commit.** Practical backend direction = CPU/AirLLM; final
> backend ADR still gated on T1C.6 (AirLLM CPU mode / quantization route). No experimental
> requirement marked DONE.

## Stage 1C-C — DirectML retest with compatible Python  *(check complete; retest user-gated)*

| id | task | pri | status | req | DoD |
| --- | --- | --- | --- | --- | --- |
| T1CC.1 | Check for installed Python 3.10–3.12 | P1 | DONE | — | `py -0p`: none (only 3.13, 3.9) |
| T1CC.2 | Check non-invasive install route | P1 | DONE | — | `winget` present; `Python.Python.3.11` 3.11.9 available |
| T1CC.3 | Decide install vs stop-and-report | P0 | DONE | — | **Stopped & reported** — persistent host change is user-gated |
| T1CC.4 | Record 1C-C results + backend status | P1 | DONE | — | GPU_FEASIBILITY §3c; statuses updated |
| T1CC.5 | Log Prompt 006 | P1 | DONE | R-PROMPTLOG | Prompt 006 recorded |
| T1CC.6 | **(User-gated)** Install Python 3.10–3.12 → run DirectML smoke test | P2 | DONE | — | Authorized in 1C-D; see below |

> No compatible Python installed; DirectML retest deferred to a user-authorized install.
> **No project deps changed, no code, no model download, no AirLLM/Ollama, no benchmark, no
> commit.** Windows-native DirectML stays BLOCKED under current setup; CPU/AirLLM main path.

## Stage 1C-D — DirectML retest on compatible Python  *(user-authorized; SUCCESS)*

| id | task | pri | status | req | DoD |
| --- | --- | --- | --- | --- | --- |
| T1CD.1 | Install Python 3.11 (winget, user-scope, no admin) | P1 | DONE | — | Python **3.11.9** installed; no admin/UAC issues |
| T1CD.2 | Throwaway Py3.11 venv outside repo + `torch-directml` | P1 | DONE | — | venv in `%TEMP%`; torch-directml 0.2.5 + torch 2.4.1 |
| T1CD.3 | DirectML smoke test (import/device/64×64 matmul) | P1 | DONE | — | **SUCCESS** — `privateuseone:0`, shape (64,64), finite |
| T1CD.4 | transformers import (no model download) | P1 | DONE | — | transformers 5.12.1 imported; no model fetched |
| T1CD.5 | Tear down throwaway venv | P1 | DONE | — | venv removed; WSL project env re-verified clean |
| T1CD.6 | Update GPU_FEASIBILITY/RISKS/DECISIONS; log Prompt 007 | P1 | DONE | — | §3d added; Windows DirectML → POSSIBLE; Prompt 007 |
| T1C.7 | Final execution-backend ADR | P0 | TODO | — | Gated on §5: AirLLM CPU mode / AirLLM-DirectML / quant route |

> **GPU verified usable via DirectML** (optional baseline/extension), but **CPU + AirLLM is
> the main path** (AirLLM-on-DirectML UNKNOWN; iGPU shares RAM). Python 3.11.9 remains on the
> host (authorized). **No project deps changed, no project code, no model download, no
> AirLLM/Ollama, no benchmark, no commit/push.** No experimental requirement marked DONE.

## Stage 1D — AirLLM CPU feasibility check  *(feasibility complete; runtime check deferred)*

| id | task | pri | status | req | DoD |
| --- | --- | --- | --- | --- | --- |
| T1D.1 | Confirm WSL python/uv; discover `airllm` on PyPI | P1 | DONE | R-AIR-01 | `airllm` 2.11.0 discoverable; `air-llm` n/a |
| T1D.2 | Throwaway uv venv in `/tmp` (outside repo) | P1 | DONE | — | venv created; repo untouched |
| T1D.3 | Install airllm (CPU torch) + import probe | P1 | DONE | R-AIR-01 | Install OK; **import OK** with pinned matrix |
| T1D.4 | Resolve dependency-matrix breakage | P0 | DONE | R-AIRLLM-DEPS | Pinned transformers 4.44.2 + optimum 1.23.3 + sentencepiece |
| T1D.5 | Introspect CPU-mode support (no model download) | P1 | DONE | R-AIR-01 | `device='cpu'` is first-class; bitsandbytes optional |
| T1D.6 | Create `AIRLLM_FEASIBILITY.md` + update RISKS/DECISIONS | P1 | DONE | — | Doc + R-AIRLLM-DEPS + ADR-0011 |
| T1D.7 | Tear down throwaway env; log Prompt 008 | P1 | DONE | R-PROMPTLOG | env removed; Prompt 008 |
| T1D.8 | **Stage 3 runtime check** — small model on `device='cpu'` (one forward pass) | P0 | TODO | R-AIR-01 | Confirms no CUDA-only code path at run time |

> CPU + AirLLM feasibility **EVIDENCED at install+import+API level** (ADR-0011); runtime
> confirmation is a Stage 3 small-model check (T1D.8). **No model download, no inference, no
> benchmark, no project deps/code changes, no commit.** No experimental requirement marked DONE.

## Stage 1 — Approval & remaining intake

| id | task | pri | status | req | DoD |
| --- | --- | --- | --- | --- | --- |
| T1.1 | Collect hardware specs from machine | P0 | DONE | R-HW-01 | Captured in `HARDWARE.md` (GPU/disk-type partial; CPU-only WSL2) |
| T1.2a | Capture GitHub repo URL | P1 | DONE | R-GIT-HISTORY | `github.com/mohammedawad99/ex05-airllm` recorded; `origin` set |
| T1.2b | Capture group code + HF-access confirmation | P0 | BLOCKED | U-GROUP,U-HF-ACCESS | Both recorded; no token stored |
| T1.2c | Capture cost assumptions (electricity tariff, hardware cost) | P1 | BLOCKED | U-ELEC,U-HWCOST | Recorded for Stage 6 cost model |
| T1.3 | Resolve hardware-independent open questions (PRD §10) | P1 | TODO | R-DOC-PRD | OQ-1..4 dispositioned |
| T1.4 | Freeze PRD v1.0 after user approval | P0 | BLOCKED | R-DOC-PRD | User sign-off; version bumped |

## Stage 2A — Dependency skeleton & measurement design  *(complete)*

| id | task | pri | status | req | DoD |
| --- | --- | --- | --- | --- | --- |
| T2A.1 | Create `pyproject.toml` + `uv.lock` (pinned AirLLM matrix, CPU torch) | P0 | DONE | R-UV,R-AIRLLM-DEPS | `uv sync --extra dev` resolves; pins match 1D |
| T2A.2 | Minimal `src/ex05_airllm` (`__init__`, `version`, `constants`) | P0 | DONE | R-ARCH-SDK,R-VERSION | Package imports; version `1.0.0` |
| T2A.3 | `tests/unit/test_version.py` (version consistency) | P0 | DONE | R-TDD,R-VERSION | 4 tests pass; coverage 100% |
| T2A.4 | Configure `ruff` + `pytest` + coverage (fail_under=85) | P0 | DONE | R-LINT,R-COVERAGE,R-FILELEN | ruff clean; format clean; ≤150 lines |
| T2A.5 | `docs/MEASUREMENT_DESIGN.md` (metrics + result schema + repro rules) | P0 | DONE | R-MEAS-* | 9-section design; no data |
| T2A.6 | `config/experiment.example.toml` (placeholder model id) | P0 | DONE | R-CONFIG-ARCH,R-VERSION | Versioned template; no real model id |
| T2A.7 | Update PLAN/QUALITY/DECISIONS/audit; log Prompt 009 | P0 | DONE | R-PROMPTLOG | ADR-0012; gates table; Prompt 009 |

> Stage 2A is skeleton + design only — **no model selected, no download, no inference, no
> benchmark.** No experimental requirement marked DONE.

## Stage 2B — Model shortlist & selection plan  *(planning complete)*

| id | task | pri | status | req | DoD |
| --- | --- | --- | --- | --- | --- |
| T2.1 | Write `PRD_measurement.md` (metric defs + timing method) | P0 | DONE | R-DOC-PRD-MECH,R-MEAS-* | Schema + metrics + no-manual-metrics rule |
| T2.2 | Write `PRD_airllm_pipeline.md` | P0 | DONE | R-DOC-PRD-MECH | CPU device, shard path, Stage 3 acceptance |
| T2.3 | Model shortlist matrix (metadata-verified, no download) | P0 | DONE | R-MODEL-01 | `MODEL_SELECTION.md` + `config/model_candidates.example.toml` |
| T2.4 | Record model-selection strategy (ADR-0101a) | P0 | DONE | R-MODEL-01 | ADR with criteria; ADR-0101 → SHORTLISTED |
| T2.5 | Update RISKS/PLAN/audit; log Prompt 010 | P0 | DONE | R-PROMPTLOG | Model risks; Prompt 010 |
| T2.6 | **Final model pick + download approval** | P0 | BLOCKED | R-MODEL-01 | User approves a candidate; download only then |
| T2.7 | Add `.env-example` when a token is first needed | P1 | TODO | R-CONFIG-ARCH | Placeholders only (primary picks are ungated → may not be needed) |
| T2.8 | Finalize CPU quantization route (GGUF Q4/Q8 vs none) | P1 | TODO | R-QUANT-CPU | Route decided in an ADR |

> Shortlist is **metadata-verified only** (no weights downloaded). **No final model selected,
> no download, no inference, no benchmark.** T2.6 is user-gated. No experimental requirement DONE.

## Stage 3A — Tiny AirLLM CPU smoke probe  *(attempted; failed honestly)*

| id | task | pri | status | req | DoD |
| --- | --- | --- | --- | --- | --- |
| T3A.1 | Write `smoke_airllm.py` + helper unit tests | P0 | DONE | R-TDD | 8 tests pass, 100% cov, ruff clean, ≤150 lines |
| T3A.2 | Run tiny AirLLM CPU probe on Qwen2-0.5B (approved) | P0 | DONE | R-AIR-01 | Ran; raw JSON written |
| T3A.3 | Outcome | P0 | **FAILED (recorded)** | R-AIRLLM-SHARD | `AssertionError: model.safetensors.index.json should exist` — AirLLM needs pre-sharded safetensors |
| T3A.4 | Document failure + corrective plan | P0 | DONE | — | `SMOKE_RUN.md`; R-AIRLLM-SHARD; ADR-0014 |
| T3A.5 | Log Prompt 011 | P0 | DONE | R-PROMPTLOG | Prompt 011 |

> Smoke **did not** succeed → AirLLM tiny smoke is **NOT** marked EVIDENCED. Only metadata/
> tokenizer files (~12 MB) hit the external HF cache; **no weights in the repo**; **no Qwen2-7B
> download**, no benchmark, no fake results.

## Stage 3B — Re-sharded tiny AirLLM CPU smoke  *(format fixed; runtime FAILED)*

| id | task | pri | status | req | DoD |
| --- | --- | --- | --- | --- | --- |
| T3B.1 | `prepare_sharded_model.py` — download Qwen2-0.5B, re-shard locally | P0 | DONE | R-AIRLLM-SHARD | 37 shards + `model.safetensors.index.json` (git-ignored) |
| T3B.2 | Untie tied embeddings so index has `lm_head.weight` | P0 | DONE | R-AIRLLM-TIED | `untied_embeddings=true`, `lm_head_in_index=true` |
| T3B.3 | Make smoke load local sharded path; pre-create layers dir | P0 | DONE | — | AirLLM accepts format, splits layers, loads |
| T3B.4 | Run AirLLM CPU smoke on re-sharded model | P0 | **FAILED (recorded)** | R-AIRLLM-META | Forward pass → `Tensor on device cpu ... meta!` |
| T3B.5 | Document outcome + correctives; tests/gates; log Prompt 012 | P0 | DONE | R-PROMPTLOG | `SMOKE_RUN.md` §6; R-AIRLLM-META; ADR-0015 |

> Re-shard/untie **resolved** the format blockers; the AirLLM **CPU runtime** failed with a
> meta-device error → AirLLM smoke **NOT** EVIDENCED. No 7B download; no benchmark; no fake
> results; weights ignored & untracked.

## Stage 3C — Torch-pin retest for the AirLLM meta-device failure  *(done; torch ruled out)*

| id | task | pri | status | req | DoD |
| --- | --- | --- | --- | --- | --- |
| T3C.1 | Pin `torch==2.4.1` + `uv sync` | P0 | DONE | R-AIRLLM-META | Installed `torch 2.4.1+cpu`; resolves cleanly |
| T3C.2 | Rerun smoke on existing re-sharded model (no new download) | P0 | DONE | R-AIRLLM-META | `results/stage3c_..._torch241.json` |
| T3C.3 | Outcome | P0 | **FAILED (same error)** | R-AIRLLM-META | Identical meta-device error → **torch not the cause** |
| T3C.4 | Root-cause via source; document; keep torch 2.4.1; log Prompt 013 | P0 | DONE | — | Qwen2 `rotary_emb` left on `meta`; `SMOKE_RUN.md` §7; ADR-0015/0016 |

> Torch version **ruled out** (2.4.1 and 2.12.1 fail identically). AirLLM CPU smoke still **NOT**
> EVIDENCED. `torch==2.4.1` kept as the project pin. No new download; no benchmark; no fake results.

## Stage 3D — Transformers CPU fallback smoke  *(SUCCEEDED — pipeline proven)*

| id | task | pri | status | req | DoD |
| --- | --- | --- | --- | --- | --- |
| T3D.1 | `smoke_transformers_cpu.py` (offline, cache-only) + helper tests | P0 | DONE | R-TDD | 15 tests, 100% cov, ruff clean, ≤150 lines |
| T3D.2 | Run direct HF `transformers` CPU `generate` on Qwen2-0.5B | P0 | DONE | R-REPRO | **success=true**; coherent 16-token output |
| T3D.3 | Schema-valid measurement record written | P0 | DONE | R-REPRO | `results/stage3d_..._cpu.json` (load/gen/runtime/RSS/tokens) |
| T3D.4 | Document; tests/gates; log Prompt 014 | P0 | DONE | R-PROMPTLOG | `SMOKE_RUN.md` §8; ADR-0016 EVIDENCED; Prompt 014 |
| T3D.5 | (Optional) AirLLM rotary-buffer materialization patch | P2 | TODO | R-AIRLLM-META | Only if AirLLM CPU is pursued; fragile |
| T3D.6 | Confirm Qwen2-7B native sharding + untied (pre-7B-download) | P1 | TODO | R-AIRLLM-SHARD | Before any 7B request (note: same rotary/meta risk) |

> **Pipeline PROVEN** via a direct HF CPU smoke — **not AirLLM, not a benchmark.** AirLLM CPU
> stays **blocked/not evidenced** (R-AIRLLM-META). No new download, no 7B, no fake results.

## Stage 4A — AirLLM Qwen2 CPU patch feasibility  *(patch attempted; infeasible)*

| id | task | pri | status | req | DoD |
| --- | --- | --- | --- | --- | --- |
| T4A.1 | Read-only inspection of AirLLM + transformers Qwen2 source | P0 | DONE | R-AIRLLM-META | Root-cause traced (`AIRLLM_PATCH_FEASIBILITY.md` §3) |
| T4A.2 | Implement local, fail-closed Qwen2 rotary shim + tests | P0 | DONE | R-AIRLLM-META | `airllm_compat.py` + `test_airllm_compat.py` (no site-packages edit) |
| T4A.3 | Run patched AirLLM CPU smoke (local model, no download) | P0 | DONE | R-AIRLLM-META | `results/stage4a_*` (`patched=true`) |
| T4A.4 | Outcome | P0 | **FAILED (recorded)** | R-AIRLLM-META | Same meta error; diagnostic shows layer-param (RMSNorm) on meta, not rotary |
| T4A.5 | Decide path; document; log Prompt 015 | P0 | DONE | — | ADR-0017 (limitation + HF baseline); Prompt 015 |

> Minimal safe shim **infeasible** (blocker is AirLLM's core CPU param streaming). AirLLM CPU
> **not evidenced**; proceed with the HF CPU pipeline (3D). No site-packages edits, no new
> download, no 7B, no benchmark, no fake results.

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

## Stage 5A — Measurement SDK & result schema  *(done; no inference)*

| id | task | pri | status | req | DoD |
| --- | --- | --- | --- | --- | --- |
| T5A.1 | `result_schema.py` (typed `MeasurementResult`, optional None, success=False) | P0 | DONE | R-MEAS-* | Schema + tests; no fake defaults |
| T5A.2 | `metrics.py` (`MetricsCollector`: TTFT/TPOT/throughput/runtime/peak-RAM) | P0 | DONE | R-MEAS-* | Injectable clock/RSS; math unit-tested |
| T5A.3 | `result_writer.py` (`write_json`/`append_csv`, stable header) | P0 | DONE | R-REPRO | tmp_path tests; None→empty cell |
| T5A.4 | `prompts.py` (deterministic registry) + `env.py` (safe metadata) | P0 | DONE | R-REPRO | No secrets/private paths; tested |
| T5A.5 | Docs + tests; log Prompt 017 | P0 | DONE | R-PROMPTLOG | 38 tests, ~97% cov, ruff clean, ≤150 lines |

> **No model run, no inference, no download** in 5A. All metric math is tested with a
> controlled clock; failure records never look successful.

## Stage 5B — Repeatable Transformers CPU measurement  *(done; 6/6 runs)*

| id | task | pri | status | req | DoD |
| --- | --- | --- | --- | --- | --- |
| T5B.1 | Runner: SDK around real HF `transformers` CPU `generate` (Qwen2-0.5B, local) | P0 | DONE | R-BASE-01,R-MEAS-* | `run_transformers_cpu_measurement.py` + tests |
| T5B.2 | Run the 6-run matrix (3 prompts × 2), write JSON + summary.csv | P0 | DONE | R-BASE-01,R-MEAS-* | **6/6 success**; `results/measurements/.../summary.csv` |
| T5B.3 | Document runs + metrics caveats (TTFT None, TPOT approx) | P0 | DONE | R-MEAS-* | `MEASUREMENT_RUNS.md`; audit PARTIALLY_EVIDENCED |
| T5B.4 | Fold AirLLM failure JSONs in as structured evidence | P1 | TODO | R-AIR-01 | Stage 6 report (negative result, not success) |
| T5B.5 | (Optional) DirectML tiny GPU-vs-CPU baseline | P2 | TODO | R-EXT-01 | Optional extension; Windows-native |
| T5B.6 | Qualitative output samples (Transformers CPU) | P1 | TODO | R-MEAS-QUAL | Samples stored |

> **No AirLLM run** (blocked, ADR-0017/0018), **no Qwen2-7B download** (`download_approved=false`).
> A small repeatable CPU measurement (6 runs), **not** a tuned benchmark; no fake values.

## Stage 6A — Analysis, figures & cost/energy estimate  *(done; from committed data)*

| id | task | pri | status | req | DoD |
| --- | --- | --- | --- | --- | --- |
| T6A.1 | `analyze_measurements.py` + `analysis_stats.py` + `cost_model.py` (TDD) | P0 | DONE | R-MEAS-*,R-COST-* | Tests; ≤150 lines; no model runs |
| T6A.2 | Compute stats/per-prompt from `summary.csv`; AirLLM negative-result aggregation | P0 | DONE | R-MEAS-*,R-AIR-01 | `results/analysis/*.json`; AirLLM `any_success=false` |
| T6A.3 | Plain-matplotlib figures (runtime/throughput/RAM/break-even) | P0 | DONE | R-README-01 | `figures/*.png` generated from data (no seaborn) |
| T6A.4 | Assumption-based cost/energy estimate (not verified pricing) | P0 | DONE | R-COST-*,R-MEAS-ENERGY | `cost_energy_*.json`; caveats explicit |
| T6A.5 | `ANALYSIS.md` + update COSTS/MEASUREMENT docs/audit; log Prompt 019 | P0 | DONE | R-PROMPTLOG | Audit cost/energy → PARTIALLY_EVIDENCED |

> Analysis from **committed data only** — no model run, no download, no benchmark, no fake results;
> raw measurement files unmodified. AirLLM stays **not evidenced**; Qwen2-7B not downloaded.

## Stage 7A — Final report draft & gap audit (done)

> Drafted in Stage 7A (docs only; **no model run/download/benchmark**): README rewritten as the
> 13-section technical report with embedded tables/figures; `reports/final_report.md` companion
> added; `docs/FINAL_GAP_AUDIT.md` created. AirLLM stays **blocked/not evidenced**; `Qwen2-7B` not
> downloaded/approved. Cost/energy assumption-based, not verified.

| id | task | pri | status | req | DoD |
| --- | --- | --- | --- | --- | --- |
| T6.5 | Integrate tables/figures into README technical report | P0 | IN_PROGRESS | R-README-01 | Stage 7A: README is the report (tables, embedded figures, repro, limitations). Polish + final audit pending |
| T6.6 | Concept explanations tied to evidence; answer Research Questions | P0 | IN_PROGRESS | R-CONCEPT-01,R-RQ-01 | Stage 7A: README §9 + `reports/final_report.md` §5–6 (measured-vs-discussed markers) |
| T6.7 | (Optional) original extension; DirectML analysis | P1 | TODO | R-EXT-01 | ADR for the chosen extension |
| T7A.1 | Final gap audit (satisfied/partial/blocked/missing) | P0 | DONE | all | `docs/FINAL_GAP_AUDIT.md` |

> **No AirLLM run** (blocked, ADR-0017/0018) and **no Qwen2-7B download** (`download_approved=false`).
> AirLLM compression/quantization is GPU/bitsandbytes-bound → out of scope on CPU; any quantization
> shown uses GGUF via the baseline. AirLLM appears as failure evidence, not a successful run.

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
| T7.1 | Assemble README technical report | P0 | IN_PROGRESS | R-README-01 | Stage 7A/7B: README is the report w/ tables, embedded figures, evidence map, repro, limits. Final assembly pending experiment gaps |
| T7.2 | Run SUBMISSION_CHECKLIST end-to-end | P0 | IN_PROGRESS | R-NOFAKE | Stage 7B: checklist updated to real DONE/PARTIAL/BLOCKED/TODO. Overall = PARTIAL by design (not 100% green; AirLLM blocked, quant/7B not done) |
| T7.3 | Final requirements re-audit | P0 | IN_PROGRESS | all | Stage 7B: gap audit aligned w/ README + checklist; no experimental req DONE; AirLLM BLOCKED |
| T7.4 | Clean git history; user-initiated push | P0 | IN_PROGRESS | R-GIT-HISTORY | Stages 0–7B pushed (`e3d8537`); final submission push only on explicit user request |
| T8.1 | Stage 8A final submission-readiness audit | P0 | DONE | R-NOFAKE | Verdict READY_AFTER_USER_INPUT; doc fixes (README License & credits; stale checklist push line) |
| T8.2 | Stage 8B close for manual submission | P0 | DONE | R-NOFAKE,R-LICENSE,R-EXT-01 | Readiness → **READY_FOR_MANUAL_SUBMISSION** (not submitted/100%); group code handled manually (not in repo); license undecided (ADR-0106, none invented); Stage 3D qualitative smoke sample surfaced (README §7, final_report §4); original analytical extensions designated (ADR-0105). No model run; committed + pushed |
| T9.1 | Stage 9A low-risk rubric repairs | P0 | DONE | R-CONFIG-ARCH,R-ARCH-SDK,R-ARCH-GATEKEEPER | `.env-example` (dummy); thin `sdk.py` facade; fail-closed `ApiGatekeeper` guard (N/A_WITH_RATIONALE, no live API) + `config/rate_limits.example.json`; tests (64 pass, ~97%). Docs reframed **not** self-assessment-100-ready (ADR-0020). No model run/download |
| T9.2 | Stage 9B TTFT streaming measurement (NO new download) | P0 | DONE | R-MEAS-TTFT,R-MEAS-TPOT | **Real TTFT measured** via `TextIteratorStreamer` (6/6, cached Qwen2-0.5B, offline). New dir `results/measurements/transformers_cpu_streaming_qwen2_0_5b/`; Stage 5B untouched. TTFT mean ≈0.41 s (steady ≈0.25–0.27 s), TPOT decode-only ≈0.19 s/tok. No download; 71 tests pass |
| T9.3a | Stage 9C-0 quantization preflight & route decision | P0 | DONE | R-QUANT-01 | `docs/QUANTIZATION_PREFLIGHT.md` — Route A (torch dynamic INT8, no download) recommended; Route B (GGUF Q8/Q4) approval-gated; Route C stop. Planning only; no run/download/dep change |
| T9.3 | Stage 9C Route A quantization (FP32 vs dynamic INT8) | P0 | DONE | R-QUANT-01,R-MEAS-QUAL | **Route A executed** (user-approved): FP32 vs PyTorch dynamic INT8, 12/12, no download/dep → `results/measurements/transformers_cpu_int8_quantization_qwen2_0_5b/`. INT8 ≈3.6× faster but **quality degraded**, RAM ≈1.5% lower (honest). R-QUANT-01/R-MEAS-QUAL → PARTIALLY_EVIDENCED. 77 tests pass |
| T9.3r | Stage 9C-R final TTFT/quant report integration (docs only) | P0 | DONE | R-README-01,R-RQ-01 | README §2 + final_report §2a/§2b evidence summary + quant interpretation; ANALYSIS §3c; fixed stale gap-audit blocker lines. No new data; no model run/download |
| T9.3b | Stage 10A GGUF Q8/Q4 sweep (Route B) | P0 | DONE | R-QUANT-01,R-MEAS-QUAL | **Executed** (user-approved): `llama-cpp-python` + `Qwen2.5-0.5B-Instruct-GGUF` **Q8_0 vs Q4_K_M**, 12/12 → `results/measurements/gguf_quantization_qwen2_5_0_5b/`. Q4 ~13% less RAM / 27% smaller file, ~equal throughput, coherent. F16 excluded (>~1.2 GB cap). GGUF weights git-ignored. 84 tests pass |
| T10B.0 | Stage 10B-0 large-model memory-pressure preflight (docs only) | P0 | DONE | R-BASE-01,R-HW-01 | `docs/LARGE_MODEL_PREFLIGHT.md` — hw/storage snapshot (11 GiB RAM + 3 GiB swap, 924 GB disk); 7B fp16 (~15 GB) > RAM → pressure test, OOM expected/acceptable; guardrails + exact approval text. No download/run/dep change |
| T9.4 | Stage 10B large-model memory-pressure baseline (guarded, structured negative) | P1 | DONE | R-BASE-01 | **Executed (user-approved):** guarded `Qwen/Qwen2.5-7B-Instruct` fp16 Transformers CPU attempt under a **13312 MiB** `RLIMIT_AS` child budget → child hit `Cannot allocate memory` **during load** → **structured negative** `memory_budget_exceeded` (`success=false`, returncode 3, not timed out; local snapshot found; no generation). `results/measurements/large_model_pressure_qwen2_5_7b/`. **Guarded memory-budget attempt, not a full benchmark; no large-model performance claimed; weights git-ignored/never committed.** AirLLM stays blocked |
| T11A.1 | Stage 11A final-analysis hardening (cost v2 + roofline + figures + runner tests) | P1 | DONE | R-COST-ONPREM,R-COST-BREAKEVEN,R-CONCEPT-ROOFLINE,R-EXT-01,R-MEAS-QUAL | **Docs/code only; no model run/download.** Added `analysis_pipeline.py` (reads committed CSV/JSON → `final_evidence_summary.json` + `roofline_classification.json` + 3 figures) and **cost model v2** in `cost_model.py` (nonzero allocated CAPEX $225→$4.6875/mo; amortized break-even ~47k/~13k req-month; elec-only 0) → `cost_model_v2.json` + `final_cost_break_even.png`. Added tests for both + the two under-tested runners. **123 tests, ~96% cov** (both quant runners now 100%), ruff clean, ≤150 lines. Prices/tariff/FX = **dated assumptions (2026-06-21)**. Raw dirs/`measurement_summary.md`/`pyproject`/`uv.lock` unchanged; no artifacts tracked. AirLLM blocked; 10B stays a structured negative; **not** 100-ready |

---

### Blocked / waiting on user
- **T1.1, T1.2** — need hardware specs + group code + repo URL + HF-access confirmation
  (the `NEEDED_USER_INPUT` items in `REQUIREMENTS_AUDIT.md` §C).
- **T7.4** — no commit/push until explicitly requested.
