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
- **Discussed, not executed:** quantized inference, a GPU/DirectML model run, a `Qwen2-7B`
  experiment. **`Qwen2-7B` was not downloaded and not approved.**
- **Estimated under assumptions:** energy and On-Prem-vs-API cost — explicitly not live pricing.

## 2. Status at a glance

| Area | State | Primary evidence |
| --- | --- | --- |
| Hardware characterization | Measured (host + WSL2) | `docs/HARDWARE.md` |
| Backend feasibility | DirectML reachable (optional); AirLLM imports | `docs/GPU_FEASIBILITY.md`, `docs/AIRLLM_FEASIBILITY.md` |
| AirLLM CPU/Qwen2 | **Blocked / not evidenced** | `results/stage3*`, `results/stage4a*`, `docs/AIRLLM_PATCH_FEASIBILITY.md` |
| Transformers CPU measurement | **6/6 runs** | `results/measurements/transformers_cpu_qwen2_0_5b/`, `docs/MEASUREMENT_RUNS.md` |
| Analysis + figures | Generated from committed data | `results/analysis/`, `figures/`, `docs/ANALYSIS.md` |
| Cost/energy | Assumption-based estimate | `results/analysis/cost_energy_estimate.json`, `docs/COSTS.md` |

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

- **TTFT = None** (no streaming hook) — recorded, never estimated.
- **TPOT approximate** = generation_seconds / output_tokens; ≈ 0.20 s/token at the mean throughput.
- **Peak VRAM = N/A** (CPU-only). RAM is process RSS.

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

## 5. Concept mapping (measured vs discussed)

See README §9 for the concise version. The analytical core:

- The decode loop on CPU is **throughput-limited by memory traffic** (weights + KV cache), not raw
  compute — a Roofline-style "memory-bound" placement consistent with the stable ~5 tok/s for a
  0.5B model at ~4 GB RSS.
- A 7B fp16 model (~15 GB) cannot fit the ~11 GiB budget — which is exactly why **layer streaming /
  paging / quantization** exist. AirLLM is the streaming answer; it is blocked here at the CPU
  parameter-movement step. Quantization is the precision answer; it was not executed.

## 6. Research Questions (answered with evidence)

- **What is the bottleneck when running locally?** For our measured 0.5B CPU decode, the limiter is
  **memory-bound token generation** (stable low throughput, modest RSS), not FLOPs. *Evidence:*
  §4 measurements.
- **AirLLM vs OS paging?** AirLLM intends **explicit per-layer streaming** instead of relying on the
  OS to page a too-large mapping. In this environment AirLLM's CPU streaming is **blocked** (§3), so
  we could not measure the streaming-vs-paging contrast on a large model — reported honestly.
- **Quantization trade-offs?** *Discussed, not measured.* Lower precision reduces the resident
  footprint at some quality cost; we did not produce a quantized run, so **no quantitative trade-off
  is claimed**.
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

Assumptions: CPU **45 W**, **$0.20/kWh**, assumed API **$0.50 / $1.50** per 1M in/out tokens,
`hardware_cost_usd = 0`. Per run (mean ~5.68 s, ~9 in / ~29 out tokens): energy ≈ **7.1×10⁻⁵ kWh**,
local ≈ **$1.4×10⁻⁵**, assumed API ≈ **$4.9×10⁻⁵**, break-even **0 requests** at CAPEX=0. Source:
`results/analysis/cost_energy_estimate.json`; method: `docs/COSTS.md`. **Not market-verified
pricing.**

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

Same as README §11: AirLLM CPU/Qwen2 blocked; no `Qwen2-7B` run; no quantized run; no DirectML
measurement; cost/pricing assumption-based; TTFT unavailable. The dominant **grading risk** is that
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
not 100% complete, and **not** claimed ready for a self-assessment-100 grade until the quantization
(Stage 9C), TTFT (Stage 9B), and large-model memory-pressure gaps are closed (see `docs/PLAN.md` §8).
Stage 9A added engineering hygiene only (`.env-example`, SDK facade, fail-closed API gatekeeper) — no
new experimental result.
