# Analysis — Stage 6A

> Reproducible analysis generated **from already-committed data only** by
> `src/ex05_airllm/analyze_measurements.py` (+ `analysis_stats.py`, `cost_model.py`).
> Re-run with `uv run python -m ex05_airllm.analyze_measurements`.

## 1. Status

- Analysis from **existing committed data only** (Stage 5B CSV/JSON + Stage 3/4A AirLLM JSONs).
- **No model runs**, **no new downloads**, **no benchmark/final-performance claim**.
- Raw measurement files are read-only inputs (verified unmodified); outputs go to
  `results/analysis/`, `figures/`, `reports/`.

## 2. Data sources

- Stage 5B Transformers CPU measurement: `results/measurements/transformers_cpu_qwen2_0_5b/`
  (`summary.csv` + 6 per-run JSONs).
- Stage 3/4A AirLLM **failure** evidence:
  `results/stage3_smoke_airllm_qwen2_0_5b.json`,
  `results/stage3b_smoke_airllm_qwen2_0_5b_resharded.json`,
  `results/stage3c_smoke_airllm_qwen2_0_5b_torch241.json`,
  `results/stage4a_smoke_airllm_qwen2_0_5b_patched.json`.

## 3. Transformers CPU summary (computed)

`6/6` runs succeeded. `environment=wsl_cpu`. **TTFT unavailable (None)** — `generate()` was not
token-streamed in this runner.

| metric | min | mean | max |
| --- | --- | --- | --- |
| total_runtime_seconds | 5.16 | 5.68 | 6.57 |
| tokens_per_second | 4.42 | 5.07 | 5.31 |
| peak_ram_mb | 3985.4 | 4015.6 | 4029.1 |
| output_tokens | 27 | 28.7 | 30 |

| prompt_id | runs | mean_runtime_s | mean_tok/s | mean_peak_ram_mb |
| --- | --- | --- | --- | --- |
| os_definition | 2 | 6.06 | 4.83 | 4007.2 |
| ai_agent_short | 2 | 5.76 | 5.21 | 4010.5 |
| memory_management_short | 2 | 5.23 | 5.16 | 4029.1 |

Authoritative copy: `results/analysis/transformers_cpu_qwen2_0_5b_summary_stats.json`.

### 3b. Streaming TTFT run (Stage 9B — real first-token timing)

A **separate** streaming run (`results/measurements/transformers_cpu_streaming_qwen2_0_5b/`,
6/6 succeeded) measures **real TTFT** via `TextIteratorStreamer` on the same cached Qwen2-0.5B,
CPU, offline — **superseding Stage 5B for TTFT/TPOT** while Stage 5B stays valid for non-streaming
total-runtime/throughput. Numbers below are computed directly from that run's `summary.csv` (not
from the Stage 6A figures, which are unchanged):

| metric | min | mean | max |
| --- | --- | --- | --- |
| ttft_seconds | 0.2486 | 0.4122 | 1.1599 |
| tpot_seconds | 0.1892 | 0.1922 | 0.1961 |
| tokens_per_second | 4.3599 | 5.0240 | 5.2151 |
| generation_seconds | 5.1773 | 5.7321 | 6.6516 |
| peak_ram_mb | 3988.2 | 4008.15 | 4019.9 |

The **mean TTFT is skewed by the first (cold) run ≈1.16 s**; the other five are ≈0.25–0.27 s. TTFT
is measured (streamer observation), not estimated; TPOT here is the real decode-only per-token time.

### 3c. Dynamic INT8 quantization run (Stage 9C Route A — FP32 vs INT8)

A **separate** no-download run (`results/measurements/transformers_cpu_int8_quantization_qwen2_0_5b/`,
12/12) compares FP32 vs **PyTorch dynamic INT8** on the same cached Qwen2-0.5B (full detail:
`docs/MEASUREMENT_RUNS.md` §9). Per-variant means:

| variant | mean gen (s) | mean tok/s | mean peak RAM (MB) | mean out tokens |
| --- | --- | --- | --- | --- |
| fp32_reference | 6.03 | 4.83 | 7192.4 | 28.7 |
| int8_dynamic | 1.89 | 17.27 | 7086.3 | 32.0 |

INT8 ≈**3.6× faster** but **output quality regressed** (committed per-variant previews) and peak RAM
dropped only ≈1.5% — a **speed/quality trade-off, not a free win**. **Dynamic INT8 only — NOT GGUF,
NOT Q4, NOT Q8** → quantization is **PARTIALLY_EVIDENCED**; a low-bit GGUF sweep remains open.

### 3d. GGUF low-bit sweep (Stage 10A — Q8_0 vs Q4_K_M)

A **separate** user-approved low-bit GGUF sweep (`results/measurements/gguf_quantization_qwen2_5_0_5b/`,
12/12) via `llama-cpp-python` on **`Qwen2.5-0.5B-Instruct-GGUF`** (different model/runtime than the
Transformers stages; full detail: `docs/MEASUREMENT_RUNS.md` §10). Per-variant means:

| variant | mean TTFT (s) | mean TPOT (s/tok) | mean tok/s | mean peak RAM (MB) | file (MB) |
| --- | --- | --- | --- | --- | --- |
| q8_0 | 0.403 | 0.0173 | 32.56 | 787.6 | 675.7 |
| q4_k_m | 0.354 | 0.0186 | 31.79 | 684.8 | 491.4 |

**Q4_K_M used ~13% less peak RAM and a 27% smaller file than Q8_0 at ~equal throughput, with coherent
output for both** — the expected low-bit memory benefit. **F16 excluded** (1266 MB > ~1.2 GB cap).
This is **not cross-comparable** with the Transformers runs (different model + runtime). With both
dynamic INT8 (3c) and GGUF Q8/Q4 (3d) measured, low-bit quantization is now genuinely evidenced.

## 4. Figures

Generated with **plain matplotlib** (no seaborn, no custom styling):
- `figures/transformers_cpu_runtime_by_prompt.png` — mean runtime (s) per prompt.
- `figures/transformers_cpu_throughput_by_prompt.png` — mean throughput (tokens/s) per prompt.
- `figures/transformers_cpu_peak_ram_by_prompt.png` — mean peak RAM (MB) per prompt.
- `figures/cost_break_even_estimate.png` — illustrative On-Prem-vs-API break-even under
  **assumed** pricing (NOT verified market prices).

## 5. AirLLM failure evidence summary (negative result)

`results/analysis/airllm_failure_summary.json` — `any_success: false`, 4 attempts all
`success=false`:
- **3A:** format issue — single-file safetensors lacked `model.safetensors.index.json`.
- **3B:** re-shard + untie **solved the format**, but the CPU forward failed (meta-device).
- **3C:** `torch==2.4.1+cpu` retest failed identically → **torch ruled out**.
- **4A:** local rotary shim didn't help — root cause is AirLLM's **core CPU parameter
  streaming** (a layer param left on `meta`); a minimal safe patch is infeasible (ADR-0017).

**This is a documented limitation, not an AirLLM success.**

## 6. Cost & energy estimate (assumption-based)

All numbers derive from documented **assumptions**, not verified live pricing
(`results/analysis/cost_energy_assumptions.json`, `cost_energy_estimate.json`):

- Assumptions: CPU power **45 W**, electricity **$0.20/kWh**, assumed API **$0.50 / $1.50** per
  1M input / output tokens, `hardware_cost_usd = 0` (sensitivity only).
- Formulas: `energy_kWh = runtime_s/3600 × W/1000`; `local_cost = energy_kWh × price`;
  `api_cost = in/1e6×in_price + out/1e6×out_price`;
  `break_even_N = hardware_cost / (api_per_req − local_per_req)`.
- Result (per run, at mean runtime ~5.68 s, ~9 input / ~29 output tokens): energy ≈
  7.1×10⁻⁵ kWh; local electricity ≈ $1.4×10⁻⁵; assumed API ≈ $4.9×10⁻⁵; with `hardware_cost=0`
  the break-even is at **0 requests** (On-Prem cheaper per request once CAPEX is excluded).
- **Caveat:** illustrative under assumptions; **not** current verified market pricing. Real
  pricing must be sourced and dated before any quantitative cost claim.

## 7. Interpretation

- The **runnable measurement path** is Transformers CPU on Qwen2-0.5B — real, repeatable numbers.
- **AirLLM** is an investigated **negative result** in this environment (blocked at its core CPU
  streaming); it is presented as a limitation analysis, never as a success.
- **Direct large-model pressure (Stage 10B)** is **attempted & evidenced** as a **structured
  negative**: a guarded `Qwen/Qwen2.5-7B-Instruct` fp16 Transformers CPU load under a 13312 MiB child
  budget hit `Cannot allocate memory` during load (`memory_budget_exceeded`,
  `results/measurements/large_model_pressure_qwen2_5_7b/`). It is a guarded memory-budget attempt, not
  a full benchmark, and is excluded from the small-model analysis pipeline above. **No large-model
  performance is claimed.**
- **No large-model *performance* generalization** — the 7B never generated; the result is a
  load-time memory-pressure negative, not a throughput/latency benchmark.

## 8. Next steps

- **Done (Stage 7A):** these tables/figures are integrated into the README technical report and
  `reports/final_report.md`; gaps tracked in `docs/FINAL_GAP_AUDIT.md`.
- *Optional:* a Windows-native DirectML analysis if time permits (extension, not AirLLM).
- **No Qwen2-7B** unless the AirLLM blocker is resolved on a viable backend.

## 9. Stage 11A — final-analysis hardening (cost v2, roofline, figures; docs/code only)

A reproducible pipeline `src/ex05_airllm/analysis_pipeline.py` reads **only committed** measurement
CSV/JSON (5B/9B/9C/10A/10B) and writes new analysis artifacts — **no model run, no download, no raw
file mutated**. Run: `uv run python -m ex05_airllm.analysis_pipeline` (and `… -m ex05_airllm.cost_model`).

- **Evidence summary** — `results/analysis/final_evidence_summary.json` with all five groups (5B
  baseline, 9B streaming TTFT/TPOT, 9C dynamic INT8, 10A GGUF Q8/Q4, 10B 7B memory-pressure).
- **Cost model v2** — `src/ex05_airllm/cost_model.py` → `results/analysis/cost_model_v2.json`. Adds a
  **nonzero allocated CAPEX**: $900 laptop × 25% local-LLM usage = **$225** effective, amortized over
  4 years = **$4.6875/month**. Electricity: **0.6432 ILS/kWh ÷ 3.70 = $0.1738/kWh** (Israel
  residential tariff assumption). API: OpenAI **gpt-4o-mini $0.15/$0.60**, **gpt-4.1-mini $0.40/$1.60**
  per 1M in/out. Workload 512 in / 128 out tokens over [100 … 1,000,000] req/month. **All values are
  dated assumptions accessed 2026-06-21 — NOT guaranteed future prices.**
  - **Electricity-only** local cost is tiny (sub-cent/request) ⇒ electricity-only break-even is **0**
    (local cheaper from the first request).
  - **CAPEX dominates** local economics; the meaningful **amortized break-even** is **≈47,487
    req/month** vs gpt-4o-mini and **≈13,215 req/month** vs gpt-4.1-mini.
  - Privacy / offline capability may justify local inference even when pure cost does not.
- **Roofline-style qualitative classification** — `results/analysis/roofline_classification.json`
  (from measured evidence; **not** a formal hardware roofline benchmark): 5B memory/CPU-constrained,
  moderate throughput; 9B prefill latency (TTFT) visible, decode TPOT stable; 9C INT8 faster but
  quality regresses with small RAM savings (Linear-only + both models held); 10A GGUF Q4 lower memory
  at near-equal throughput; 10B 7B fp16 memory-capacity bound (budget exceeded before generation).
- **Figures** (plain matplotlib, default colors, no subplots): `figures/final_quantization_speed_ram.png`,
  `figures/final_ttft_tpot.png`, `figures/final_cost_break_even.png`,
  `figures/final_roofline_classification.png`.
- **Honesty:** 9C dynamic INT8 (Transformers) and 10A GGUF Q4/Q8 (`llama.cpp`) stay **separate**
  quantization experiments on different models/runtimes — **not cross-comparable**. AirLLM stays
  blocked/not evidenced; 10B stays a guarded memory-pressure **structured negative**, not a full 7B
  benchmark. The repo is **not** claimed 100-ready / 100% complete.
