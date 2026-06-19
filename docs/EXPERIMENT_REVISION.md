# Experiment Direction Revision — Stage 4B

> A formal, honest revision of the experiment plan after AirLLM CPU for Qwen2 was proven
> blocked (Stages 3–4A). The goal: a coherent path that satisfies as much of the assignment
> as possible **without any fake AirLLM success**.

## 1. Status

- **Post Stage 4A revision** — planning/documentation only.
- **No new model downloads** (Qwen2-7B remains not downloaded and not approved).
- **No benchmark yet**; no model code run in this stage.

## 2. Original plan

Tiny smoke (`Qwen2-0.5B`) → **main AirLLM run on `Qwen2-7B`** (larger-than-RAM, layer-streamed
on CPU) → direct HF/Ollama baseline on the same model → quantization comparison + an original
extension (e.g. break-even / DirectML). The AirLLM run was to be the centrepiece demonstrating
local memory management.

## 3. Evidence collected (what actually happened)

| stage | evidence | outcome |
| --- | --- | --- |
| 1A/1B | hardware (host vs WSL2), `HARDWARE.md` | ~11 GiB WSL RAM, CPU-only, 933 GB NVMe disk |
| 1C | GPU/DirectML feasibility, `GPU_FEASIBILITY.md` | DirectML works on the iGPU (Windows-native Py3.11); optional only |
| 1D | AirLLM install/import, `AIRLLM_FEASIBILITY.md` | imports on CPU with a pinned matrix; `device='cpu'` is first-class |
| 3A | upstream Qwen2-0.5B single-file safetensors | **FAIL** — AirLLM needs `model.safetensors.index.json` (R-AIRLLM-SHARD) |
| 3B | local re-shard + untie | shard/format **fixed**; AirLLM loads/starts, then **FAIL** meta-device (R-AIRLLM-META, R-AIRLLM-TIED) |
| 3C | `torch==2.4.1+cpu` retest | **FAIL** identical → **torch ruled out** |
| 3D | Transformers CPU fallback smoke | **SUCCESS** — coherent output; measurement pipeline proven (not AirLLM, not a benchmark) |
| 4A | local rotary shim + patched smoke | **FAIL** — diagnostic disproved rotary; meta tensor is a layer parameter (RMSNorm `weight`) → AirLLM **core** CPU param streaming; minimal safe shim **infeasible** |

Every failure is recorded as raw JSON under `results/` and analysed in `docs/SMOKE_RUN.md` /
`docs/AIRLLM_PATCH_FEASIBILITY.md`. Nothing is faked.

## 4. Decision

- **Qwen2-7B download is blocked/deferred** under the current AirLLM CPU path — the same core
  meta→CPU streaming defect would fail identically, so downloading ~15 GB to reproduce a known
  failure is not justified (`download_approved=false`).
- **AirLLM CPU/Qwen2 is NOT used for the main benchmark.** It is retained as an **investigated
  local-memory-management method** with detailed feasibility + failure analysis and structured
  evidence — a legitimate, assignment-relevant negative result.
- **The Transformers CPU pipeline becomes the runnable measurement path** (proven in Stage 3D):
  real, repeatable CPU inference on the already-downloaded `Qwen2-0.5B`, feeding the metrics
  schema and result writer.
- **No site-packages edits, no fragile AirLLM core patch** (ADR-0017).

## 5. Assignment impact analysis

**Still satisfiable (with real evidence):**
- Hardware characterization (CPU/GPU/VRAM/disk, host-vs-WSL boundary) — `HARDWARE.md`.
- **Baseline local inference** — direct HF `transformers` CPU runs on Qwen2-0.5B (Stage 3D proven).
- **Measurement metrics** — TTFT/TPOT/throughput/runtime/peak-RAM via the MetricsCollector
  (Stage 5); the result schema + writer are already proven.
- **Reproducibility** — pinned `uv` env, fixed commands/seeds, raw JSON per run.
- **Cost analysis** (On-Prem vs API, break-even) — methodology in `COSTS.md`; computable from
  measured runtimes + documented assumptions.
- **DirectML optional extension** — a GPU-vs-CPU mini-baseline (Windows-native), clearly optional.
- **AirLLM technical analysis** — concepts (meta device, layer streaming, paging/mmap, KV cache)
  explained and tied to *our* concrete evidence, including why CPU streaming failed here.

**Partially unmet (stated honestly):**
- A **successful AirLLM generation in this environment** — not achieved. We have a thorough,
  reproducible failure analysis instead (root cause localized to AirLLM's core CPU param
  streaming), which is itself a valid engineering deliverable per the assignment's "a
  well-analyzed negative result outscores an unsupported positive claim".

**How to be honest in the final report:**
- Present AirLLM as *attempted and analysed*, never as *succeeded*. Show the failure JSONs and
  the root-cause trace. Label the Transformers CPU runs as the baseline/measurement path, not as
  AirLLM. Mark every estimate as an estimate; no fabricated graphs or numbers.

## 6. Revised Stage 5 plan

1. Implement **MetricsCollector** + **ResultWriter** (TDD; SDK-fronted; files ≤150 lines) writing
   the `RESULT_SCHEMA_COLUMNS` records.
2. Run a **repeatable Transformers CPU** smoke/measurement on **Qwen2-0.5B** (already local) →
   real metrics (TTFT, TPOT, throughput, peak RAM, runtime) with fixed seeds.
3. *Optionally*, a **DirectML tiny baseline** (Windows-native) for a GPU-vs-CPU comparison, if
   time permits — clearly an optional extension, not AirLLM.
4. Include the **AirLLM failure results as structured evidence** (not success): the raw JSONs +
   the root-cause analysis become a first-class section of the report.
5. **Defer any larger-model download** until the measurement runner is solid *and* the AirLLM
   limitation is clearly framed; a 7B attempt only after an explicit, separate approval and only
   on a path where AirLLM (or the chosen backend) can actually run.

## 7. Risks

- **Grading risk** — AirLLM did not generate, so the "headline" run is a negative result.
  **Mitigation:** deep, reproducible root-cause analysis; structured failure evidence; a working
  fallback measurement pipeline (real numbers); DirectML feasibility as an extra; honest framing
  with **no fake results** (tracked as R-GRADE-AIRLLM in `RISKS.md`). The assignment explicitly
  values a well-analysed negative result over an unsupported positive claim.
- **Scope risk** — over-investing in AirLLM workarounds. **Mitigation:** AirLLM core patching is
  closed (ADR-0017); effort goes to the measurement SDK + analysis.

## 8. Exit criteria

- This revised plan is **approved** by the user.
- **No fake AirLLM claims** anywhere (AirLLM run stays PLANNED/blocked, not DONE).
- **No unapproved Qwen2-7B download** (`download_approved=false` retained).
- The next stage can implement the **measurement SDK** + repeatable Transformers CPU measurement.
