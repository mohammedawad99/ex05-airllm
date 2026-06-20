# EX05 — Final Report (extended)

> Companion to the top-level [`README.md`](../README.md) technical report. This document goes deeper
> on the AirLLM root-cause analysis, the concept mapping, and the assignment's Research Questions.
> It adds **no new measurements**: every number traces to committed data under `results/`. AirLLM
> is presented as an investigated **negative result**; the Transformers CPU path is the measured,
> reproducible evidence base. Cost/energy is **assumption-based**, not market-verified.

## 1. Scope and honesty contract

- **Measured here:** Hugging Face `transformers` **CPU** inference on the locally-cached
  `Qwen/Qwen2-0.5B` — 6 runs, offline.
- **Investigated but blocked:** AirLLM CPU layer-streaming on Qwen2 — root-caused failure, no
  generation.
- **Attempted as a guarded structured negative:** a direct large-model (>RAM) memory-pressure
  baseline — `Qwen/Qwen2.5-7B-Instruct` fp16 on Transformers CPU under a capped child memory budget
  (Stage 10B, §4a). It failed to load within budget (`memory_budget_exceeded`) — a guarded
  memory-budget attempt, **not** a full benchmark, and **not** a large-model performance claim.
- **Discussed, not executed:** large-model quantization; a GPU/DirectML model run; a *successful*
  large-model generation.
- **Estimated under assumptions:** energy and On-Prem-vs-API cost — explicitly not live pricing.

## 2. Status at a glance

| Area | State | Primary evidence |
| --- | --- | --- |
| Hardware characterization | Measured (host + WSL2) | `docs/HARDWARE.md` |
| Backend feasibility | DirectML reachable (optional); AirLLM imports | `docs/GPU_FEASIBILITY.md`, `docs/AIRLLM_FEASIBILITY.md` |
| AirLLM CPU/Qwen2 | **Blocked / not evidenced** | `results/stage3*`, `results/stage4a*`, `docs/AIRLLM_PATCH_FEASIBILITY.md` |
| Transformers CPU measurement | **6/6 runs** | `results/measurements/transformers_cpu_qwen2_0_5b/`, `docs/MEASUREMENT_RUNS.md` |
| Large-model (>RAM) pressure baseline | **Attempted & evidenced — structured negative** (`memory_budget_exceeded`) | `results/measurements/large_model_pressure_qwen2_5_7b/`, `docs/LARGE_MODEL_PREFLIGHT.md` §1 |
| Analysis + figures | Generated from committed data | `results/analysis/`, `figures/`, `docs/ANALYSIS.md` |
| Cost/energy | Assumption-based estimate | `results/analysis/cost_energy_estimate.json`, `docs/COSTS.md` |

### 2a. Measured evidence summary

Three measured CPU evidence groups, all on the cached `Qwen/Qwen2-0.5B` (offline, deterministic). AirLLM
remains a structured **negative result**; none of these is AirLLM or a benchmark.

| stage | what it measures | headline numbers | evidence dir |
| --- | --- | --- | --- |
| **5B** baseline (non-streaming) | runtime / throughput / peak RAM | gen ≈5.68 s; ≈5.07 tok/s; ≈4016 MB; TTFT `None` | `transformers_cpu_qwen2_0_5b/` |
| **9B** streaming | **real TTFT** + decode-only TPOT | TTFT mean **0.412 s** (min 0.249, max 1.160); TPOT mean **0.192 s/tok**; throughput mean **5.02 tok/s** | `transformers_cpu_streaming_qwen2_0_5b/` |
| **9C** FP32 vs dynamic INT8 | quantization trade-off | fp32: **6.03 s / 4.83 tok/s / 7192 MB / 28.7 tok** · int8_dynamic: **1.89 s / 17.27 tok/s / 7086 MB / 32.0 tok** | `transformers_cpu_int8_quantization_qwen2_0_5b/` |
| **10A** GGUF Q8_0 vs Q4_K_M *(diff. model/runtime)* | low-bit sweep (`llama.cpp`, `Qwen2.5-0.5B-Instruct-GGUF`) | q8_0: **32.56 tok/s / 787.6 MB / 675.7 MB file** · q4_k_m: **31.79 tok/s / 684.8 MB / 491.4 MB file** (both coherent; F16 excluded) | `gguf_quantization_qwen2_5_0_5b/` |

### 2b. Quantization interpretation (Stage 9C Route A)

Dynamic INT8 was **≈3.6× faster** (17.27 vs 4.83 tok/s; gen 1.89 vs 6.03 s) but **peak RAM barely
dropped (~1.5%, 7086 vs 7192 MB)** and **output quality regressed clearly** — FP32 produced a coherent
answer while INT8 produced incoherent text (per-variant `output_preview`/`output_text` are committed).
The honest summary: **INT8 provided a speed/quality trade-off, not a free win.**

**Why this is PARTIAL, not full quantization satisfaction:** it is **PyTorch dynamic INT8 only**
(quantizes Linear modules at inference), **not GGUF, not Q4, not Q8**, and not a low-bit sweep. The RAM
figure also holds both the FP32 reference and the derived INT8 model in memory at once, so it is not
comparable to the single-model Stage 5B RSS. A true **low-bit GGUF Q4/Q8** comparison remains
**NOT_DONE / approval-gated** (Route B). So R-QUANT-01 / R-MEAS-QUAL are **PARTIALLY_EVIDENCED**, never
"fully satisfied".

## 3. AirLLM forensic detail

AirLLM's premise is **layer-wise loading**: keep only the active transformer layer resident, stream
the rest from disk, so a model larger than RAM can run with a small memory footprint. That premise
fits this machine (small RAM budget, fast NVMe). The investigation went as far as a root cause:

1. **Install / import (1D)** — succeeds on CPU with the pinned matrix (`airllm==2.11.0`,
   `transformers==4.44.2`, `torch==2.4.1+cpu`). `device='cpu'` is a first-class AirLLM option.
2. **Format requirement (3A)** — AirLLM expects **sharded** safetensors with a
   `model.safetensors.index.json`; the upstream single-file `Qwen2-0.5B` lacks it →
   `AssertionError: model.safetensors.index.json should exist.`
3. **Format fix (3B)** — a local re-shard + weight-untie (`prepare_sharded_model.py`) produces the
   index. AirLLM now **loads and begins inference**, then fails in the forward pass:
   `RuntimeError: Tensor on device cpu is not on the expected device meta!`
4. **PyTorch ruled out (3C)** — re-running under `torch==2.4.1+cpu` reproduces the **identical**
   meta-device error → not a torch-version artifact.
5. **Rotary ruled out, root cause localized (4A)** — a fail-closed local rotary shim
   (`airllm_compat.py`, no site-packages edits) did **not** help; a diagnostic showed a **layer
   parameter** (e.g. an RMSNorm `weight`) still resident on the `meta` device during the CPU
   forward. The defect is in AirLLM's **core CPU parameter streaming** — moving the per-layer
   parameters off `meta` onto CPU — not in any single op we can safely shim. A minimal, safe patch is
   therefore **infeasible** (ADR-0017).

**Aggregated:** `results/analysis/airllm_failure_summary.json` → `any_success: false`, 4 attempts,
all `success=false`. **Conclusion: AirLLM CPU/Qwen2 is blocked here — a documented limitation, not a
success.** The decision not to download `Qwen2-7B` follows directly: the same core path would fail
identically, so ~15 GB to reproduce a known blocker is unjustified (ADR-0018).

## 4. Transformers CPU measurement (the measured path)

Direct HF `transformers` CPU inference on the cached `Qwen2-0.5B`, offline; **3 deterministic
prompts × 2 repeats = 6 runs**. Authoritative values:
`results/analysis/transformers_cpu_qwen2_0_5b_summary_stats.json`.

| metric | min | mean | max |
| --- | --- | --- | --- |
| total runtime (s) | 5.16 | 5.68 | 6.57 |
| throughput (tokens/s) | 4.42 | 5.07 | 5.31 |
| peak RAM — RSS (MB) | 3985.4 | 4015.6 | 4029.1 |
| output tokens | 27 | 28.7 | 30 |

- **TTFT = None in this Stage 5B run** (no streaming hook) — recorded, never estimated. **Real TTFT
  is measured in the Stage 9B streaming run** (below).
- **TPOT (Stage 5B) approximate** = generation_seconds / output_tokens; the decode-only TPOT is
  measured in Stage 9B.
- **Peak VRAM = N/A** (CPU-only). RAM is process RSS.

**Stage 9B — real TTFT (streaming, same cached model, no new download).** A separate run observes the
first generated token via `TextIteratorStreamer` (`results/measurements/
transformers_cpu_streaming_qwen2_0_5b/`, 6/6). It **supersedes Stage 5B for TTFT/TPOT**; Stage 5B
stays valid for non-streaming total-runtime/throughput. **TTFT** min/mean/max = **0.249 / 0.412 /
1.160 s** (mean skewed by the cold first run ≈1.16 s; steady ≈0.25–0.27 s); **decode-only TPOT** ≈
**0.19 s/token**; throughput ≈ 4.36–5.22 tok/s; peak RAM ≈ 3988–4020 MB. Measured, not estimated.

The numbers are tight and stable across repeats, which is the point: a small, **reproducible**
measurement, not a competitive benchmark.

**Qualitative smoke sample (illustrative, from committed evidence).** The Stage 3D smoke
(`results/stage3d_smoke_transformers_qwen2_0_5b_cpu.json`) preserved one short output:

> Prompt: "Define an operating system in one short sentence." → Output (16 tokens): "An operating
> system is a software program that manages the hardware and software resources of a…" *(truncated
> at `max_new_tokens=16`)*

It is a **tiny Transformers CPU smoke sample** — **not** AirLLM output, **not** a benchmark, **not** a
full qualitative comparison, and **not** a quantization comparison. The Stage 5B JSONs store metrics
but no generated text, so no broader qualitative table is asserted; no model was rerun to produce this.

## 4a. Stage 10B — guarded large-model (>RAM) memory-pressure baseline (structured negative)

The deliberately *larger-than-memory* case, run under explicit approval as a **guarded** attempt. A
direct `Qwen/Qwen2.5-7B-Instruct` **fp16 Transformers CPU** load was attempted from the locally-cached
snapshot (found in the **ignored HF cache**; weights **git-ignored**, never committed). A child
subprocess was capped at **13312 MiB** (`RLIMIT_AS`) — below the ~15.24 GB fp16 footprint on a
~11 GiB-RAM + ~3 GiB-swap host — so the parent survives and writes a structured record instead of
being OOM-killed. The child hit **`Cannot allocate memory`** (`DefaultCPUAllocator`) **during model
load, before any generation**:

| field | value |
| --- | --- |
| attempt_type / backend / environment | `transformers_7b_direct_cpu_baseline` / `transformers` / `wsl_cpu` |
| success / structured_negative_result | `false` / `true` |
| failure_class | `memory_budget_exceeded` |
| download_completed / local_snapshot_found | `true` / `true` |
| load_completed / generation_completed | `false` / `false` |
| child_memory_limit_mb | `13312` |
| returncode / timed_out | `3` / `false` |
| elapsed_seconds / child_maxrss_mb | `4.65` / `871.8` |

*Evidence:* `results/measurements/large_model_pressure_qwen2_5_7b/`. This **demonstrates direct fp16 7B
memory pressure** on the WSL CPU environment and **closes the direct large-model pressure baseline
gap**. It is a **guarded memory-budget attempt, not a full benchmark**; it never generated, so **no
large-model performance is claimed**, and it is **not** an AirLLM result (AirLLM stays blocked, §3).

## 5. Concept mapping (measured vs discussed)

See README §9 for the concise version. The analytical core:

- The decode loop on CPU is **throughput-limited by memory traffic** (weights + KV cache), not raw
  compute — a Roofline-style "memory-bound" placement consistent with the stable ~5 tok/s for a
  0.5B model at ~4 GB RSS.
- A 7B fp16 model (~15 GB) cannot fit the ~11 GiB budget — **directly evidenced** by Stage 10B (§4a),
  where the guarded `Qwen2.5-7B` fp16 load failed under a 13 GiB child budget (`memory_budget_exceeded`)
  — which is exactly why **layer streaming / paging / quantization** exist. AirLLM is the streaming
  answer; it is blocked here at the CPU parameter-movement step. Quantization is the precision answer;
  it was measured on a small model only.

## 6. Research Questions (answered with evidence)

- **What is the bottleneck when running locally?** For our measured 0.5B CPU decode, the limiter is
  **memory-bound token generation** (stable low throughput, modest RSS), not FLOPs. *Evidence:*
  §4 measurements.
- **AirLLM vs OS paging?** AirLLM intends **explicit per-layer streaming** instead of relying on the
  OS to page a too-large mapping. In this environment AirLLM's CPU streaming is **blocked** (§3), so
  we could not measure the streaming-vs-paging contrast on a large model — reported honestly.
- **Quantization trade-offs?** *Measured two ways (small model).* (1) **PyTorch dynamic INT8 vs FP32**
  (Stage 9C, Transformers, cached Qwen2-0.5B): INT8 **≈3.6× faster** but **degraded output quality**
  and only ≈1.5% lower peak RAM. (2) **GGUF Q8_0 vs Q4_K_M** (Stage 10A, `llama.cpp`,
  `Qwen2.5-0.5B-Instruct-GGUF`, user-approved): **Q4 used ~13% less peak RAM and a 27% smaller file at
  ~equal throughput, both coherent** — the expected low-bit memory benefit. **F16 GGUF excluded**
  (>~1.2 GB cap). The two are on **different models/runtimes** and are **not** cross-comparable; no
  large-model quantization. Evidence: `results/measurements/transformers_cpu_int8_quantization_qwen2_0_5b/`,
  `results/measurements/gguf_quantization_qwen2_5_0_5b/`.
- **How do prefill/decode map to TTFT/TPOT?** Prefill → first-token latency (TTFT); decode →
  per-token latency (TPOT/ITL). Here TTFT is **unmeasured** (no streaming hook) and TPOT is
  **approximate**; we do not over-claim a prefill/decode split from a single whole-`generate()` timer.
- **What does it cost to run a big model locally?** Under explicit assumptions (§7), per-run local
  electricity is ≈ $1.4×10⁻⁵; the honest finding is **methodological** — break-even is dominated by
  CAPEX, which we set to 0, so the comparison is illustrative only.
- **When is an API better?** When request volume is low and/or hardware CAPEX and idle time dominate,
  an API avoids amortizing fixed hardware cost; On-Prem wins at sustained high volume once CAPEX is
  amortized. We state the shape of the trade-off, not a verified price verdict.

## 7. Cost & energy (assumption-based)

**v1 estimate (CAPEX=0 — superseded by the CAPEX-aware v2 below).** Assumptions: CPU **45 W**,
**$0.20/kWh**, assumed API **$0.50 / $1.50** per 1M in/out tokens, `hardware_cost_usd = 0`. Per run
(mean ~5.68 s, ~9 in / ~29 out tokens): energy ≈ **7.1×10⁻⁵ kWh**, local ≈ **$1.4×10⁻⁵**, assumed API
≈ **$4.9×10⁻⁵**, break-even **0 requests** at CAPEX=0 (this zero is exactly *why* v2 adds a nonzero
allocated CAPEX). Source: `results/analysis/cost_energy_estimate.json`; method: `docs/COSTS.md`. **Not
market-verified pricing.**

**Cost model v2 (Stage 11A — CAPEX-aware).** To make the break-even meaningful, a v2 model
(`src/ex05_airllm/cost_model.py` → `results/analysis/cost_model_v2.json`,
`figures/final_cost_break_even.png`) adds a **nonzero allocated CAPEX**: $900 laptop × 25% usage =
**$225** effective, amortized over 4 years = **$4.6875/month**; electricity **0.6432 ILS/kWh ÷ 3.70 =
$0.1738/kWh**; assumed OpenAI **gpt-4o-mini $0.15/$0.60** and **gpt-4.1-mini $0.40/$1.60** per 1M; 512
in / 128 out tokens. **All values are dated assumptions accessed 2026-06-21, not guaranteed future
pricing.** Result: electricity-only local cost is **tiny** (break-even 0), but the **amortized
break-even** is **≈47,487 req/month** (gpt-4o-mini) / **≈13,215 req/month** (gpt-4.1-mini) — **CAPEX
dominates** local economics; privacy/offline may justify local even when pure cost does not. A
**Roofline-style qualitative classification** (`results/analysis/roofline_classification.json`) and
four `figures/final_*.png` summarize quantization, TTFT, cost, and the per-stage memory/compute regime
— all from committed evidence, no new runs (`docs/ANALYSIS.md` §9).

## 8. Reproducibility

```bash
uv sync --extra dev
uv run pytest
uv run ruff check .
uv run python -m ex05_airllm.analyze_measurements   # regenerates tables/figures/cost from committed data
```

Inspect `results/measurements/transformers_cpu_qwen2_0_5b/` and the AirLLM failure JSONs directly.
**No model weights are committed; do not download `Qwen2-7B` to reproduce.**

## 9. Limitations and risks

Same as README §11: AirLLM CPU/Qwen2 blocked; the `Qwen2.5-7B` Stage 10B run was a **guarded
memory-pressure attempt** (structured negative, §4a) and **not a full benchmark** — no large-model
performance is claimed; quantization measured on a small model only; no DirectML measurement;
cost/pricing assumption-based. The dominant **grading risk** is that
AirLLM did not generate; the mitigation is this report's depth — a reproducible root-cause analysis,
a working measured fallback, and zero fabricated claims. The assignment explicitly rewards a
well-analyzed negative result over an unsupported positive claim.

## 10. Original analytical extensions

The project's original contributions are **analytical**, not a claimed AirLLM success:
(1) the **AirLLM forensic failure analysis** with structured negative-result evidence (§3), and
(2) the **assumption-based local-vs-API energy/cost break-even analysis** (§7). Both are built on
committed evidence and clearly labelled; neither presents AirLLM as having generated.

## 11. Conclusion

An honest negative AirLLM result plus a working, reproducible Transformers CPU measurement pipeline,
analyzed transparently with assumption-marked cost/energy. Engineering evidence over fabricated
success. Repository status: **READY_FOR_HONEST_SUBMISSION (with known limitations)** — not submitted,
not 100% complete, and **not** claimed ready for a self-assessment-100 grade. The **direct large-model
(>RAM) memory-pressure baseline** is now **attempted & evidenced** as a guarded **structured negative**
(Stage 10B, §4a: 7B fp16 ~15 GB > the 13 GiB child budget → `memory_budget_exceeded` during load) —
a memory-budget attempt, not a full benchmark, with no model artifacts committed.
**TTFT is measured** (Stage 9B) and **quantization is measured two ways** — dynamic INT8 vs FP32
(Stage 9C) and GGUF Q8_0 vs Q4_K_M (Stage 10A, user-approved download; F16 excluded by size cap).
Stage 9A added engineering hygiene only (`.env-example`, SDK facade, fail-closed API gatekeeper) — no
new experimental result.
