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

## 8. Stage 9B — streaming TTFT measurement (separate run; real first-token timing)

Stage 5B used a non-streaming `generate()`, so **TTFT was `None`** there. Stage 9B adds a separate
streaming run that observes the **first generated token** via `TextIteratorStreamer` (generation on
a worker thread), measuring **real TTFT** — never estimated from total runtime.

- **Runner:** `src/ex05_airllm/run_transformers_cpu_streaming_measurement.py` (+ pure helpers in
  `src/ex05_airllm/streaming_measurement.py`). **Results:**
  `results/measurements/transformers_cpu_streaming_qwen2_0_5b/` (6 per-run JSON + `summary.csv`).
- **Config:** same model/prompts as Stage 5B — `Qwen/Qwen2-0.5B`, CPU, offline
  (`HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1`, `local_files_only=True`), `torch.manual_seed(0)`,
  `do_sample=False`, `max_new_tokens=32`, 3 prompts × 2 repeats = **6 runs, all succeeded**.
- **Definitions:** `ttft_seconds` = start → first observed token; `generation_seconds` = full
  generate window (start → end); `tpot_seconds = (generation_seconds − ttft_seconds)/(output_tokens
  − 1)`; `tokens_per_second = output_tokens / generation_seconds`.

| metric | min | mean | max |
| --- | --- | --- | --- |
| **ttft_seconds** | 0.2486 | 0.4122 | 1.1599 |
| tpot_seconds | 0.1892 | 0.1922 | 0.1961 |
| tokens_per_second | 4.3599 | 5.0240 | 5.2151 |
| generation_seconds | 5.1773 | 5.7321 | 6.6516 |
| peak_ram_mb | 3988.2 | 4008.15 | 4019.9 |
| output_tokens | 27 | 28.67 | 30 |

- *Note:* the **mean TTFT is skewed by the first run (≈1.16 s, cold)**; the other five runs are
  ≈0.25–0.27 s. Absolute values are environment-specific and vary run-to-run.
- **Supersedes / preserves:** this streaming run **supersedes Stage 5B for TTFT/TPOT
  interpretation**; **Stage 5B remains valid** for the non-streaming total-runtime/throughput
  evidence. Stage 5B raw data is **unmodified** (separate directory). Still **not** AirLLM, **not** a
  benchmark, **no** quantization, **no** download, **no** Qwen2-7B.

## 9. Stage 9C Route A — PyTorch dynamic INT8 vs FP32 (no-download quantization)

A real **no-download** quantization comparison (user-approved Route A): the cached `Qwen2-0.5B` FP32
reference vs a **PyTorch dynamic INT8** version of the *same* model
(`torch.ao.quantization.quantize_dynamic` on Linear modules), CPU, offline, deterministic. **This is
dynamic INT8 only — NOT GGUF, NOT Q4, NOT Q8.**

- **Runner:** `src/ex05_airllm/run_transformers_cpu_int8_quantization_measurement.py` (+ pure helpers
  `src/ex05_airllm/quantization_measurement.py`). **Results:**
  `results/measurements/transformers_cpu_int8_quantization_qwen2_0_5b/` (12 per-run JSON + summary).
- **Config:** `Qwen/Qwen2-0.5B`, CPU, offline, `torch.manual_seed(0)`, `do_sample=False`,
  `max_new_tokens=32`, 3 prompts × 2 repeats × 2 variants = **12 runs, all succeeded**.

| variant | runs | mean gen (s) | mean tok/s | mean peak RAM (MB) | mean out tokens |
| --- | --- | --- | --- | --- | --- |
| fp32_reference | 6 | 6.026 | 4.834 | 7192.4 | 28.7 |
| int8_dynamic | 6 | 1.892 | 17.268 | 7086.3 | 32.0 |

- **INT8 vs FP32 (descriptive ratios):** throughput **×3.57** (faster), generation time **×0.314**,
  peak RAM **×0.985** (≈1.5% lower — modest). Quantization step took ≈14 s once.
- **⚠️ Quality regression (honest, important):** the dynamic-INT8 outputs **degraded clearly**. FP32
  produced a coherent answer ("An operating system is a software program that manages the hardware
  and software resources…"); INT8 produced **incoherent** text (e.g. "____. A. 1 B. 2 C. 3 D. 4 答案…").
  So INT8 here is **much faster but lower quality** — a real measured trade-off, not a free win.
- **Caveats:** peak RAM in this run (~7 GB) is **higher than Stage 5B (~4 GB)** because both the FP32
  reference *and* the derived INT8 model are held in memory together — so these RAM numbers are
  **not** directly comparable to the single-model Stage 5B run. Dynamic INT8 quantizes **Linear
  modules only** (not embeddings/attention math), which is why the resident-memory reduction is
  small. `param_mb_estimate` ≈ 2521 MB for FP32 state-dict; the INT8 packed estimate was unavailable
  and is recorded as empty (**not fabricated**).
- **Status:** this moves quantization **NOT_DONE → PARTIALLY_EVIDENCED** (dynamic INT8 only). A
  **low-bit GGUF Q4/Q8 sweep remains NOT_DONE / approval-gated** (Route B). Stage 5B/9B raw data
  unmodified. No download, no new dependency, no AirLLM, no Qwen2-7B.

## 10. Stage 10A — GGUF CPU low-bit quantization sweep (Q8_0 vs Q4_K_M)

User-approved Route B: a controlled **low-bit GGUF** sweep via **`llama-cpp-python`** on
**`Qwen/Qwen2.5-0.5B-Instruct-GGUF`**, CPU, deterministic (`temperature=0`, `top_p=1`, `seed=0`,
`max_tokens=32`), with **real streaming TTFT**. 2 variants × 3 prompts × 2 repeats = **12 runs, all
succeeded**.

- **Runner:** `src/ex05_airllm/run_gguf_quantization_measurement.py` (+ pure
  `src/ex05_airllm/gguf_measurement.py`). **Results:**
  `results/measurements/gguf_quantization_qwen2_5_0_5b/` (12 per-run JSON + summary).
- **Files used (git-ignored under `.local_models/`, never committed):**
  `qwen2.5-0.5b-instruct-q8_0.gguf` (675.7 MB), `qwen2.5-0.5b-instruct-q4_k_m.gguf` (491.4 MB).
- **F16 excluded honestly:** `qwen2.5-0.5b-instruct-fp16.gguf` is **1266.4 MB > the ~1.2 GB approval
  cap**, so no F16 reference was downloaded or run (not substituted). Sweep is **Q8_0 vs Q4_K_M**.

| variant | runs | mean TTFT (s) | mean TPOT (s/tok) | mean tok/s | mean gen (s) | mean peak RAM (MB) | file (MB) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| q8_0 | 6 | 0.403 | 0.0173 | 32.56 | 0.889 | 787.6 | 675.7 |
| q4_k_m | 6 | 0.354 | 0.0186 | 31.79 | 0.819 | 684.8 | 491.4 |

- **Finding (honest):** **Q4_K_M used ~13% less peak RAM** (685 vs 788 MB) and a **27% smaller file**
  (491 vs 676 MB) than Q8_0, at **essentially the same throughput** (~32 tok/s) and **coherent
  output** for both (per-variant previews committed). So low-bit Q4 buys a real memory/disk saving
  here with no visible quality loss on these short prompts — the expected low-bit benefit.
- **⚠️ Not cross-comparable with Stages 5B/9B/9C.** This is a **different model**
  (`Qwen2.5-0.5B-Instruct`, not `Qwen2-0.5B`), a **different runtime** (`llama.cpp`, not HF
  `transformers`), and an **instruct/chat** format. The much higher throughput (~32 vs ~5 tok/s) and
  lower RAM (~0.7 vs ~4 GB) reflect the optimized C++ runtime + low-bit weights, **not** a like-for-
  like quantization delta against the Transformers runs. Treat this as its **own** low-bit sweep.
- **Scope:** separate small-model low-bit sweep — **not AirLLM**, **not a large-model baseline**, no
  Qwen2-7B. Prior measurement dirs unmodified; GGUF weights remain git-ignored.

## 11. Stage 10B — guarded large-model (>RAM) memory-pressure baseline (structured negative)

The deliberately *larger-than-memory* case, executed under explicit approval as a **guarded** attempt
(method scoped in `docs/LARGE_MODEL_PREFLIGHT.md`). It **attempts and evidences** the direct
large-model pressure baseline — **not** a full benchmark and **not** an AirLLM run.

- **What ran:** a direct `Qwen/Qwen2.5-7B-Instruct` **fp16 Transformers CPU** load + one tiny
  generation attempt (`max_new_tokens=8`, deterministic). The model snapshot was found in the
  **ignored HF cache** (`download_completed=true`, `local_snapshot_found=true`); weights are
  **git-ignored** (`.hf_cache/`) and **never committed**.
- **Guard design:** the parent stays light and resolves the cached snapshot offline (no re-download);
  a **child subprocess** applies an address-space cap of **13312 MiB** (`RLIMIT_AS`) **before**
  importing torch/transformers, so allocations count against the budget and the parent survives to
  write a structured record instead of being OOM-killed. 13312 MiB sits **below** the ~15.24 GB fp16
  footprint on this ~11 GiB-RAM + ~3 GiB-swap host — so hitting the cap is the expected, in-spec
  outcome.
- **Outcome (structured negative):** the child raised **`Cannot allocate memory`**
  (`DefaultCPUAllocator`) **during model load, before any generation**.

| field | value |
| --- | --- |
| model_id | `Qwen/Qwen2.5-7B-Instruct` |
| attempt_type / backend / environment | `transformers_7b_direct_cpu_baseline` / `transformers` / `wsl_cpu` |
| success / structured_negative_result | `false` / `true` |
| failure_class | `memory_budget_exceeded` |
| download_completed / local_snapshot_found | `true` / `true` |
| load_completed / generation_completed | `false` / `false` |
| child_memory_limit_mb | `13312` |
| returncode / timed_out | `3` / `false` |
| elapsed_seconds / child_elapsed_seconds | `4.65` / `1.68` |
| child_maxrss_mb / max_new_tokens | `871.8` / `8` |

- **Evidence:** `results/measurements/large_model_pressure_qwen2_5_7b/` (`summary.csv` + result JSON).
  Runner `src/ex05_airllm/run_large_model_pressure_baseline.py`, pure helpers
  `src/ex05_airllm/large_model_pressure.py`, tests `tests/unit/test_large_model_pressure.py`.
- **Interpretation:** this **demonstrates direct fp16 7B memory pressure** on the WSL CPU environment
  and **closes the direct large-model pressure baseline gap**. It is a **guarded memory-budget
  attempt, not a full benchmark**; it never generated, so **no large-model performance is claimed**.
  AirLLM remains **blocked / not evidenced** (a separate path). Prior measurement dirs unmodified; no
  model artifacts committed. The run was **not** rerun for this write-up.

## 12. Stage 11A — final-analysis pipeline over the committed evidence (no new runs)

Stage 11A adds a reproducible analysis layer that **reads only committed measurement artifacts** and
emits new analysis JSON + figures — **no model run, no download, and no raw measurement file is
edited**. Entry points: `uv run python -m ex05_airllm.analysis_pipeline` and
`uv run python -m ex05_airllm.cost_model`.

- **Inputs (read-only):** the Stage 5B/9B/9C/10A `summary.csv` files and the Stage 10B `summary.csv`
  + result JSON.
- **Outputs (new only):** `results/analysis/final_evidence_summary.json` (all five evidence groups),
  `results/analysis/roofline_classification.json`, `results/analysis/cost_model_v2.json`, and four
  figures under `figures/final_*.png` (quantization speed/RAM, streaming TTFT, cost break-even,
  Roofline-style throughput by stage).
- **Cost model v2** introduces a **nonzero allocated CAPEX** ($225 effective → $4.6875/month) so the
  break-even is meaningful (≈47k req/month vs gpt-4o-mini; ≈13k vs gpt-4.1-mini); electricity-only
  break-even is 0. **All prices/tariffs are dated assumptions (2026-06-21), not guaranteed pricing.**
- **Scope/honesty:** 9C dynamic INT8 and 10A GGUF Q4/Q8 stay **separate** quantization experiments
  (different model/runtime, not cross-comparable); 10B stays a guarded memory-pressure structured
  negative (not a full benchmark); AirLLM stays blocked/not evidenced. Prior raw dirs and
  `reports/measurement_summary.md` are untouched.
