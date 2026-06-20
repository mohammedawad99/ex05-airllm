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
- **No generalization to Qwen2-7B** — not downloaded, not run; the same AirLLM core path applies.

## 8. Next steps

- **Done (Stage 7A):** these tables/figures are integrated into the README technical report and
  `reports/final_report.md`; gaps tracked in `docs/FINAL_GAP_AUDIT.md`.
- *Optional:* a Windows-native DirectML analysis if time permits (extension, not AirLLM).
- **No Qwen2-7B** unless the AirLLM blocker is resolved on a viable backend.
