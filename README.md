# EX05 — Running a Massive LLM Locally: AirLLM, Quantization & Performance Benchmarking

> **Technical report (final draft).** This README is the submission-facing report. It documents a
> reproducible engineering experiment in running a language model on memory-constrained local
> hardware. The headline finding is an **honest negative result**: AirLLM's CPU layer-streaming
> path for Qwen2 is **blocked in this environment** by a core meta-device parameter-streaming
> defect, so a working Hugging Face `transformers` **CPU measurement path** on `Qwen2-0.5B` is used
> as the real, repeatable evidence base. Every number here regenerates from committed data; nothing
> is fabricated. A longer companion write-up lives in [`reports/final_report.md`](reports/final_report.md).

## 1. Abstract

This project investigates how to run a model on **local (On-Premises) hardware whose memory budget
is small** (~11 GiB inside WSL2), the regime that motivates disk-backed layer-wise loading tools
such as **AirLLM**. AirLLM installs and imports correctly here, and a local re-sharding step fixes
its model-format requirement — but its actual CPU forward pass **fails** with a meta-device error
that was traced to AirLLM's own parameter streaming (PyTorch version and rotary embeddings were both
ruled out). Because reproducing that same failure on a ~15 GB `Qwen2-7B` download is not justified,
the experiment pivots to a **proven, reproducible Hugging Face `transformers` CPU path** on the
already-cached `Qwen/Qwen2-0.5B`, measured over **6 runs**. The report presents those measurements
(runtime, throughput, peak RAM, output tokens), an **assumption-based** (not market-verified)
cost/energy estimate, a mapping from the evidence to the lecture concepts, and a strict limitations
section. The guiding principle, stated in the assignment, is that **a well-analyzed negative result
outscores an unsupported positive claim**.

## 2. Project status summary

| Dimension | Status |
| --- | --- |
| **What works** | HF `transformers` **CPU** inference on `Qwen2-0.5B` (6/6 runs); the measurement SDK (typed schema, metrics collector, result writer); the analysis + figure + cost pipeline; pinned `uv` env; tests/lint/coverage gates. |
| **What failed** | AirLLM's **CPU forward pass for Qwen2** — meta-device error at its core parameter streaming (3B/3C/4A); a minimal local shim was shown infeasible. |
| **What was measured** | Wall-clock runtime, throughput (tok/s), peak RAM (RSS), output-token counts — Transformers CPU, `Qwen2-0.5B`, offline. |
| **What was not attempted** | A successful AirLLM generation; any GPU/DirectML *measurement*; a quantized inference *run*; a streaming TTFT hook. |
| **Larger model** | **`Qwen2-7B` was not downloaded** and is **not approved** (`download_approved=false`). No large-model performance is claimed. |

## 3. Hardware and environment

Hardware is measured on both layers (host + WSL2) in [`docs/HARDWARE.md`](docs/HARDWARE.md); no
specs are invented. A strict **evidence boundary** separates the physical host from what the
experiment can actually use.

- **Physical host (context):** Windows 11, ASUS Vivobook S 14, Ryzen AI 9 HX 370 (12c/24t),
  **≈ 24 GB** RAM, AMD **Radeon 890M iGPU** (no NVIDIA), ~1 TB **NVMe SSD**.
- **Experiment env (binding — Ubuntu 24.04 WSL2):** 24 CPU threads (AVX-512/VNNI), **≈ 11.24 GiB**
  RAM (WSL2 cap) + 3 GiB swap, 933 GB free ext4 on an NVMe-backed VHDX. Python 3.12, `uv`.
- **GPU for compute:** **none usable inside WSL2** — the host iGPU is detected by Windows but
  CUDA/ROCm compute is not available in Ubuntu ⇒ **CPU-only**; peak VRAM is `N/A`.
- **DirectML (optional, not the main path):** a Windows-native Python 3.11 **DirectML PyTorch tensor
  smoke succeeded** on the iGPU (`docs/GPU_FEASIBILITY.md`). It proves the device is reachable for
  tensor ops, but it is **not** used for any model measurement in this report and is kept as an
  optional future lane.
- **Measurement path:** **CPU + Hugging Face `transformers`**, the runnable, reproducible lane.

## 4. Model selection

- **Measured:** `Qwen/Qwen2-0.5B` — small, openly available, already cached locally; used for all
  real measurements here.
- **Originally the main candidate:** `Qwen/Qwen2-7B` (fp16 ≈ 15.24 GB > 11.24 GiB RAM), chosen
  precisely to be *larger than memory* for the AirLLM layer-streaming demonstration. It was
  **deferred** once the AirLLM CPU path was shown blocked — downloading ~15 GB to reproduce a known
  failure is not justified (`docs/MODEL_SELECTION.md`, ADR-0101a/0018). **Qwen2-7B was not
  downloaded and not tested**; no large-model performance is claimed.
- **No gated/private models** and **no Hugging Face token** are required; everything runs from a
  local cache, offline.

## 5. Methodology

A staged, documentation-first engineering process; each stage leaves committed evidence and is
re-audited (`docs/REQUIREMENTS_AUDIT.md`, `docs/PLAN.md`):

1. **Requirement audit** → PRD / PLAN / TODO (traceability before code).
2. **Hardware feasibility** (Stage 1A/1B) — host vs WSL2, CPU-only determination.
3. **Backend feasibility** (Stage 1C/1D) — DirectML reachable (optional); AirLLM imports on CPU.
4. **Smoke probes** (Stage 3A–3D, 4A) — AirLLM format fix + CPU failure; HF CPU smoke success.
5. **Measurement SDK** (Stage 5A) — typed `MeasurementResult` schema, injectable-clock
   `MetricsCollector`, `ResultWriter` (stable CSV header), deterministic prompts.
6. **Measurement run** (Stage 5B) — 6 repeatable Transformers CPU runs on `Qwen2-0.5B`, offline.
7. **Analysis** (Stage 6A) — stats, figures, and an assumption-based cost/energy estimate computed
   **from committed data only**.

Engineering discipline throughout: **`uv`-locked** dependencies (`pyproject.toml` + `uv.lock`),
**TDD** with `pytest`, **ruff** lint+format, **coverage ≥ 85%**, every Python file **≤ 150 code
lines**, and reproducibility (fixed prompts/seeds, raw JSON per run, regenerable analysis).

## 6. AirLLM investigation (negative result)

AirLLM is the assignment's local-memory-management mechanism. It was investigated thoroughly and
**did not succeed** on CPU/Qwen2 here. The evidence chain (raw JSONs under `results/`, analysis in
[`docs/AIRLLM_PATCH_FEASIBILITY.md`](docs/AIRLLM_PATCH_FEASIBILITY.md) /
[`docs/SMOKE_RUN.md`](docs/SMOKE_RUN.md); direction recorded in
[`docs/EXPERIMENT_REVISION.md`](docs/EXPERIMENT_REVISION.md)):

| Stage | What was tried | Outcome |
| --- | --- | --- |
| 1D | Install + import AirLLM (pinned matrix) | **OK** — imports on CPU; `device='cpu'` is first-class |
| 3A | Upstream single-file safetensors | **FAIL** — needs `model.safetensors.index.json` (sharded format) |
| 3B | Local re-shard + untie weights | Format **fixed** → AirLLM loads & starts, then **FAIL** (meta-device) |
| 3C | Re-test under `torch==2.4.1+cpu` | **FAIL** identically → **torch ruled out** |
| 4A | Local rotary shim (no site-packages edit) | **FAIL** — diagnostic disproved rotary; meta tensor is a **layer parameter** in AirLLM's core CPU streaming ⇒ minimal safe patch infeasible (ADR-0017) |

The recurring runtime error is `RuntimeError: Tensor on device cpu is not on the expected device
meta!`. Aggregated evidence: `results/analysis/airllm_failure_summary.json` →
**`any_success: false`, 4 attempts, all `success=false`**.

**Final interpretation:** AirLLM CPU/Qwen2 is **blocked in this environment** — a documented,
root-caused limitation, **not a success**. This is reported as a valid negative result, not hidden.

## 7. Transformers CPU measurement

The runnable measurement path: direct Hugging Face `transformers` **CPU** inference on the local
`Qwen/Qwen2-0.5B` (offline, cache-only). **6 runs** across **3 deterministic prompts × 2 repeats**
(`os_definition`, `ai_agent_short`, `memory_management_short`). Details:
[`docs/MEASUREMENT_RUNS.md`](docs/MEASUREMENT_RUNS.md); full analysis:
[`docs/ANALYSIS.md`](docs/ANALYSIS.md); authoritative numbers:
`results/analysis/transformers_cpu_qwen2_0_5b_summary_stats.json`. This is a small, repeatable
measurement — descriptive, **not** a competitive benchmark.

| metric | min | mean | max |
| --- | --- | --- | --- |
| total runtime (s) | 5.16 | 5.68 | 6.57 |
| throughput (tokens/s) | 4.42 | 5.07 | 5.31 |
| peak RAM — RSS (MB) | 3985.4 | 4015.6 | 4029.1 |
| output tokens | 27 | 28.7 | 30 |

Per-prompt means:

| prompt_id | runs | mean runtime (s) | mean tok/s | mean peak RAM (MB) |
| --- | --- | --- | --- | --- |
| os_definition | 2 | 6.06 | 4.83 | 4007.2 |
| ai_agent_short | 2 | 5.76 | 5.21 | 4010.5 |
| memory_management_short | 2 | 5.23 | 5.16 | 4029.1 |

**Caveats (honest):**
- **TTFT = None.** `generate()` was not token-streamed in this runner, so there is no first-token
  hook; TTFT is recorded as `None`, never estimated (R-MEAS-TTFT).
- **TPOT is approximate** = `generation_seconds / output_tokens` (no TTFT to subtract prefill);
  consistent with the measured mean throughput (~5.07 tok/s ⇒ ≈ 0.20 s/token). Labelled approximate.
- **Peak RAM is process RSS**; **peak VRAM is `N/A`** (no usable GPU compute).

Figures (plain matplotlib, generated from the committed data):

![Mean runtime by prompt](figures/transformers_cpu_runtime_by_prompt.png)
![Mean throughput by prompt](figures/transformers_cpu_throughput_by_prompt.png)
![Mean peak RAM by prompt](figures/transformers_cpu_peak_ram_by_prompt.png)

**Qualitative smoke sample (illustrative).** The Stage 3D smoke run preserved one short output
(`results/stage3d_smoke_transformers_qwen2_0_5b_cpu.json`), shown here as a coherence sanity-check:

> **Prompt:** "Define an operating system in one short sentence."
> **Output (16 tokens):** "An operating system is a software program that manages the hardware and
> software resources of a…" *(truncated at `max_new_tokens=16`)*

This is a **tiny Transformers CPU smoke sample** — **not** AirLLM output, **not** a benchmark, **not**
a full qualitative comparison, and **not** a quantization comparison. The Stage 5B measurement JSONs
record metrics and token counts but not generated text, so no broader qualitative table is claimed.

## 8. Cost and energy estimate

An **assumption-based, illustrative** estimate (`src/ex05_airllm/cost_model.py`;
`results/analysis/cost_energy_estimate.json`; method in [`docs/COSTS.md`](docs/COSTS.md)). It is
**not** market-verified pricing.

- **Assumptions:** CPU power **45 W** (assumed, not metered), electricity **$0.20/kWh**, assumed
  external API **$0.50 / $1.50** per 1M input / output tokens, `hardware_cost_usd = 0` (CAPEX
  excluded — sensitivity only). Marked `pricing_status = assumption_not_live_verified`.
- **Formulas:** `energy_kWh = runtime_s/3600 × W/1000`; `local_cost = energy_kWh × price`;
  `api_cost = in/1e6×in_price + out/1e6×out_price`;
  `break_even_N = hardware_cost / (api_per_req − local_per_req)`.
- **Result (per run, mean runtime ~5.68 s, ~9 input / ~29 output tokens):** energy ≈ **7.1×10⁻⁵
  kWh**; local electricity ≈ **$1.4×10⁻⁵**; assumed API ≈ **$4.9×10⁻⁵**.
- **Break-even caveat:** with `hardware_cost = 0` the break-even is **0 requests** — On-Prem looks
  cheaper *per request* only because CAPEX is excluded. This is the dominant sensitivity: any
  realistic hardware cost pushes break-even far to the right. The figure
  (`figures/cost_break_even_estimate.png`) is illustrative under the assumptions above.

![Illustrative break-even under assumed pricing](figures/cost_break_even_estimate.png)

> **Firm caveat:** real provider prices and a metered wattage must be sourced and dated before any
> quantitative cost claim. No live/market pricing is asserted here.

## 9. Course concept mapping

Each concept is tied to *this* evidence, with an explicit measured-vs-discussed marker:

- **Prefill vs Decode** — *Discussed + partially measured.* Prefill processes the prompt in one
  compute-heavy pass; decode emits tokens autoregressively. Our runner times the whole
  `generate()`, so prefill and decode are not separated; the measured throughput (~5 tok/s) is
  dominated by the decode loop on CPU.
- **TTFT vs TPOT / ITL** — *Discussed; TTFT not measured, TPOT approximate.* TTFT needs a first-token
  hook we did not implement (recorded `None`); TPOT/ITL is approximated as time-per-output-token.
- **Decode is memory-sensitive / memory-bound locally** — *Discussed, consistent with evidence.* On
  CPU, per-token decode is throughput-limited by moving weights + KV cache through memory, not by
  raw FLOPs — matching the modest, stable ~5 tok/s and ~4 GB RSS we observe for a 0.5B model.
- **RAM / VRAM constraints** — *Measured (RAM) / N-A (VRAM).* Peak RSS ~4 GB on an ~11 GiB budget
  for 0.5B shows why a 7B fp16 model (~15 GB) cannot fit in memory — the core motivation for
  layer streaming. No VRAM (CPU-only).
- **Virtual memory / paging / layer streaming** — *Discussed; this is AirLLM's premise.* AirLLM
  streams layers from disk to keep resident memory small (an explicit alternative to OS paging of a
  too-large model). Our NVMe disk is favorable for this, but the path is blocked at AirLLM's CPU
  parameter streaming (§6).
- **Quantization as a memory-reduction route** — *Discussed, not a completed run.* Lower precision
  (Q8/Q4) would shrink the resident footprint, but AirLLM's `bitsandbytes` path is CUDA-oriented
  (unavailable) and a CPU GGUF route was not executed. **No quantized inference result is claimed.**
- **On-Prem vs API trade-off** — *Discussed + illustrative estimate.* §8 sketches the trade-off
  under explicit assumptions; the honest takeaway is methodological (CAPEX dominates break-even),
  not a verified price comparison.

## 10. Reproducibility

Everything regenerates from committed data; **no model weights are committed**.

```bash
# Set up the locked environment (uv only; no pip)
uv sync --extra dev

# Run the test suite and quality gates
uv run pytest
uv run ruff check .

# Regenerate the analysis tables, figures, and cost estimate from committed measurement data
uv run python -m ex05_airllm.analyze_measurements
```

- **Inspect committed measurement data:** `results/measurements/transformers_cpu_qwen2_0_5b/`
  (`summary.csv` + 6 per-run JSONs) and the AirLLM failure JSONs `results/stage3*`, `results/stage4a*`.
- **Generated analysis** lands in `results/analysis/`, `figures/`, and
  [`reports/measurement_summary.md`](reports/measurement_summary.md) — the analysis step above reads
  only committed data, so **no model is needed** to regenerate tables/figures.
- **Re-running the measurement itself is optional.** The runner
  `ex05_airllm.run_transformers_cpu_measurement` expects a **local/cached `Qwen2-0.5B`** and is
  **not** required to inspect the committed results; the report stands on the data already in
  `results/`.
- **Do not download `Qwen2-7B`** to reproduce this report — none of the committed results depend on
  it. The measured path uses the already-cached `Qwen2-0.5B`, offline.

## 11. Limitations

- **AirLLM did not generate** on CPU/Qwen2 — blocked at its core parameter streaming (§6).
- **No `Qwen2-7B` experiment** — not downloaded, not approved; no large-model performance claimed.
- **No quantized inference result** — quantization is discussed, not executed/measured here.
- **No DirectML measurement** — only a tensor smoke succeeded (Windows-native); no model was run on
  the iGPU.
- **Cost/API pricing is assumption-based**, not live/market-verified; the energy figure uses an
  assumed wattage, not a meter.
- **TTFT is unavailable** — the non-streaming `generate()` path exposes no first-token hook; TPOT is
  therefore approximate.

## 12. Repository structure

```
ex05-airllm/
├── README.md                  # This technical report
├── pyproject.toml  uv.lock    # uv-locked, pinned dependency matrix (CPU torch)
├── src/ex05_airllm/           # Measurement SDK + runners (schema, metrics, writer, prompts,
│                              #   cost_model, analysis, smoke/prepare/compat) — all ≤150 lines
├── tests/unit/                # pytest suite (TDD; mirrors src/)
├── docs/                      # Audited documentation (requirements, ADRs, analysis, gap audit)
├── results/
│   ├── measurements/transformers_cpu_qwen2_0_5b/  # Raw Stage 5B data (CSV + 6 JSONs)
│   ├── analysis/              # Generated stats / cost JSON (from committed data)
│   └── stage3*/stage4a*.json  # AirLLM failure evidence (negative result)
├── figures/                   # Generated plots (runtime/throughput/RAM/break-even)
├── reports/                   # final_report.md + generated measurement_summary.md
└── config/                    # Versioned config templates (no secrets)
```

**Ignored local artifacts (never committed):** model weights/caches (`.local_models/`, `.hf_cache/`),
raw run logs (`results/raw/`), the virtual env (`.venv/`), tool caches, and local reference
material. `.gitignore` enforces this; the audits below confirm no model weights are tracked.

## 13. Conclusion

This project delivers an **honest negative AirLLM result** alongside a **working, reproducible
measurement pipeline**. AirLLM was installed, format-corrected, and driven to the point of a
root-caused CPU failure; rather than fabricate a success or burn a ~15 GB download to reproduce a
known blocker, the experiment measured a real, repeatable Transformers CPU path on `Qwen2-0.5B` and
analyzed it transparently — with cost/energy clearly marked as assumption-based. The work
deliberately prioritizes **reproducible engineering evidence over fabricated success**, in line with
the assignment's stated grading philosophy.

---

## Security & data handling

- **No secrets in the repository.** Any Hugging Face token / API key is provided via environment
  variable or interactive login only; none is committed.
- `.gitignore` excludes `.env`, credentials, model weights, caches, and large artifacts.
- **No model weights or shards are tracked** (verified by audit).

## Original analytical extensions

This project's original contributions are **analytical**, built honestly on the available evidence
(neither is a measured AirLLM success):

1. **AirLLM forensic failure analysis** — a reproducible, root-caused investigation of why AirLLM's
   CPU layer-streaming is blocked for Qwen2 here, with structured negative-result evidence (the raw
   `results/stage3*` / `results/stage4a*` JSONs aggregated to `any_success=false`). See §6.
2. **Assumption-based local-vs-API energy/cost break-even analysis** — a transparent, parameterized
   model turning measured runtimes into per-request energy/cost and an illustrative break-even, with
   every input marked as an assumption (not market-verified pricing). See §8.

## License & credits

- **Project license not explicitly declared;** the course submission repository includes
  attribution/credits and no model weights. No license is invented here (ADR-0106 left undecided); a
  license file would be added only on an explicit choice.
- **Credits:** coursework for Assignment 05 (Lecture 08). Course-provided reference material is kept
  **local only** and is **not** part of this repository or redistributed. Model:
  `Qwen/Qwen2-0.5B` (Qwen2, openly available; used from a local cache, no token).
- **Honesty:** every number traces to committed data; AirLLM is reported as a structured negative
  result, never as a success; cost/energy is assumption-based, not market-verified.

## Submission status

- **READY_FOR_MANUAL_SUBMISSION** — the repository is internally consistent, honest, and
  reproducible for the measured path. It is **not** submitted and is **not** claimed 100% complete;
  remaining experiment gaps (AirLLM generation, quantization, larger-model run) are documented
  acceptable limitations.
- **Repo:** `https://github.com/mohammedawad99/ex05-airllm` (`origin`, `main`).
- **Non-repo submission metadata** (the course **group code**) is **handled manually by the student
  in the course submission system** — deliberately **not** stored in this repository, and it does
  **not** block repository readiness.
- Optional, non-blocking (see `docs/REQUIREMENTS_AUDIT.md` §C): the student's own token-free **HF
  access** confirmation, and a real **electricity tariff** / **hardware cost** if the cost estimate
  is to move beyond assumptions.

## Evidence map & key documents

Every claim above is backed by a committed document; the primary links:

- **Extended report:** [`reports/final_report.md`](reports/final_report.md) ·
  generated summary [`reports/measurement_summary.md`](reports/measurement_summary.md)
- **Requirement audits:** [`docs/FINAL_GAP_AUDIT.md`](docs/FINAL_GAP_AUDIT.md) ·
  [`docs/REQUIREMENTS_AUDIT.md`](docs/REQUIREMENTS_AUDIT.md) ·
  [`docs/SUBMISSION_CHECKLIST.md`](docs/SUBMISSION_CHECKLIST.md)
- **Measurement & analysis:** [`docs/MEASUREMENT_RUNS.md`](docs/MEASUREMENT_RUNS.md) ·
  [`docs/ANALYSIS.md`](docs/ANALYSIS.md) · [`docs/COSTS.md`](docs/COSTS.md)
- **AirLLM negative result:** [`docs/SMOKE_RUN.md`](docs/SMOKE_RUN.md) ·
  [`docs/AIRLLM_PATCH_FEASIBILITY.md`](docs/AIRLLM_PATCH_FEASIBILITY.md) ·
  [`docs/EXPERIMENT_REVISION.md`](docs/EXPERIMENT_REVISION.md)
- **Hardware & selection:** [`docs/HARDWARE.md`](docs/HARDWARE.md) ·
  [`docs/GPU_FEASIBILITY.md`](docs/GPU_FEASIBILITY.md) ·
  [`docs/MODEL_SELECTION.md`](docs/MODEL_SELECTION.md)
- **Decisions & risks:** [`docs/DECISIONS.md`](docs/DECISIONS.md) ·
  [`docs/RISKS.md`](docs/RISKS.md) · [`docs/PLAN.md`](docs/PLAN.md)
