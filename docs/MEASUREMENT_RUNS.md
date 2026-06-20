# Measurement Runs — Stage 5B (Transformers CPU)

> Real, repeatable CPU inference measurements via the Stage 5A SDK. **This is the runnable
> measurement path (ADR-0018), not AirLLM and not a full benchmark.**

## 1. Status

- **Stage 5B measurement run** — 6 runs, all succeeded.
- **Transformers CPU only** (HF `transformers`, `device="cpu"`).
- **Qwen/Qwen2-0.5B only** (already cached; loaded offline, `local_files_only=True`).
- **No AirLLM run** (blocked, not evidenced). **No Qwen2-7B.** **No DirectML.** **No download.**

## 2. Runner configuration

| field | value |
| --- | --- |
| runner | `src/ex05_airllm/run_transformers_cpu_measurement.py` |
| model_id | `Qwen/Qwen2-0.5B` |
| backend | `transformers` |
| device | `cpu` (torch float32, `torch.manual_seed(0)`, `do_sample=False`) |
| prompts | `os_definition`, `ai_agent_short`, `memory_management_short` (registry) |
| repeats | 2 per prompt → **6 runs** |
| max_new_tokens | 32 |
| offline | `HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1`, `local_files_only=True` |

## 3. Raw outputs

- **Result directory:** `results/measurements/transformers_cpu_qwen2_0_5b/`
- **Per-run JSON:** `tfcpu-qwen2_0_5b-<prompt_id>-r<repeat>.json` (6 files, schema-valid).
- **Summary CSV:** `results/measurements/transformers_cpu_qwen2_0_5b/summary.csv` (stable header + 6 rows).

## 4. Metrics interpretation

- **Measured:** `load_seconds` (one-time model+tokenizer load), `generation_seconds`
  (the `generate()` call), `total_runtime_seconds` (tokenize→generate→decode per run),
  `output_tokens`, `tokens_per_second` (= `output_tokens / generation_seconds`), `peak_ram_mb`
  (peak RSS sampled around generation via `psutil`).
- **Approximate / unavailable:**
  - **`ttft_seconds` is `None`** — HF `generate()` is not token-streamed here, so there is no
    first-token hook to time prefill separately. Recorded honestly as `None`, never faked.
  - **`tpot_seconds` is an approximation:** `generation_seconds / output_tokens` (no TTFT to
    subtract prefill). Each record carries this caveat in its `notes` field
    (`tpot_seconds ~= generation_seconds/output_tokens (approx; no TTFT/streaming hook)`).
- These are a small repeatable measurement (6 runs), **not** a tuned benchmark; absolute numbers
  are environment-specific (CPU-only WSL2).

## 5. Results summary (actual measured values)

`environment` = `wsl_cpu`; `load_seconds` ≈ **5.43 s** (one-time). Per-run:

| run_id | prompt_id | success | output_tokens | total_runtime_s | tokens_per_second | peak_ram_mb |
| --- | --- | --- | --- | --- | --- | --- |
| tfcpu-qwen2_0_5b-os_definition-r1 | os_definition | True | 29 | 6.57 | 4.42 | 3985.4 |
| tfcpu-qwen2_0_5b-ai_agent_short-r1 | ai_agent_short | True | 30 | 5.87 | 5.11 | 3991.9 |
| tfcpu-qwen2_0_5b-memory_management_short-r1 | memory_management_short | True | 27 | 5.30 | 5.10 | 4029.1 |
| tfcpu-qwen2_0_5b-os_definition-r2 | os_definition | True | 29 | 5.54 | 5.23 | 4029.1 |
| tfcpu-qwen2_0_5b-ai_agent_short-r2 | ai_agent_short | True | 30 | 5.65 | 5.31 | 4029.1 |
| tfcpu-qwen2_0_5b-memory_management_short-r2 | memory_management_short | True | 27 | 5.16 | 5.23 | 4029.1 |

**Ranges (descriptive, not a benchmark claim):** output 27–30 tokens; total runtime 5.16–6.57 s;
throughput ≈ 4.42–5.31 tokens/s; peak RAM ≈ 3985–4029 MB; TPOT ≈ 0.19–0.23 s/token (approx).
The first run is slightly slower (cold caches). No overclaiming: this is a tiny CPU measurement
of a 0.5B model, used to validate the pipeline and provide honest reference numbers. (Timing
varies run-to-run even with a fixed seed; absolute values are environment-specific.)

## 6. Relationship to AirLLM

- This Transformers CPU path is the **runnable measurement path**; it produces real metrics.
- **AirLLM CPU remains blocked / not evidenced** (R-AIRLLM-META; `docs/AIRLLM_PATCH_FEASIBILITY.md`)
  — its failure runs are kept as structured evidence.
- These numbers are **not** an AirLLM result and must **not** be compared as if AirLLM succeeded.
  AirLLM and this baseline are different things; the report presents them as such.

## 7. Next steps

- **Analysis/plots generated (Stage 6A)** *from* `summary.csv` — see `docs/ANALYSIS.md`,
  `reports/measurement_summary.md`, `results/analysis/*.json`, and `figures/transformers_cpu_*.png`
  (plain matplotlib, no hand-drawn figures).
- **Cost/energy estimate (assumption-based)** generated in Stage 6A
  (`results/analysis/cost_energy_estimate.json`, `figures/cost_break_even_estimate.png`,
  `docs/COSTS.md` §7) — **not** verified market pricing.
- **Final-report integration (Stage 6/7):** this measurement as the honest local-inference
  baseline, alongside the AirLLM failure analysis and (optional) DirectML extension.
