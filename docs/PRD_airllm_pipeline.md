# PRD — AirLLM Pipeline

> Per-mechanism PRD (guidelines §2.3) for the AirLLM layer-streaming inference pipeline.
>
> **⚠️ Stage 4B revision (ADR-0017/0018):** AirLLM CPU for Qwen2 is **blocked** in this
> environment (core meta→CPU parameter-streaming defect; see `docs/AIRLLM_PATCH_FEASIBILITY.md`,
> `docs/EXPERIMENT_REVISION.md`). This PRD now documents the **intended** pipeline + the
> investigated **failure analysis** — AirLLM is **not** the runnable main path here (that is the
> HF `transformers` CPU pipeline, `PRD_measurement.md`). It would apply on a GPU/CUDA env or after
> an upstream fix. No AirLLM run is claimed; no Qwen2-7B download.

## 1. Purpose

Run a model that is **larger than the ~11.24 GiB WSL RAM** on CPU by loading transformer layers
one at a time from disk (AirLLM), so resident memory is bounded by a single layer rather than the
whole model — and feed each run through the measurement subsystem (`PRD_measurement.md`).

## 2. Inputs / outputs

- **Inputs:** the experiment config (`config/experiment.example.toml` schema) — `model_id`
  (chosen in Stage 2B, e.g. `Qwen/Qwen2-7B`), `device='cpu'`, `dtype`, `quantization`,
  `layer_shards_saving_path`, `max_new_tokens`, `max_seq_len`, prompt set, seed.
- **Outputs:** generated text (persisted for qualitative review) + a measurement record
  (TTFT, TPOT, throughput, peak RAM, disk I/O, runtime, success/failure).

## 3. CPU device mode

- Uses AirLLM with `device='cpu'` (evidenced first-class in 1D: `self.device = torch.device(...)`).
- Uncompressed FP16/FP32 path (AirLLM `compression` 4/8-bit is bitsandbytes/CUDA → not used on
  CPU; quantization comparison uses the GGUF route — R-QUANT-CPU).
- `torch` is the CPU wheel (pinned via the `pytorch-cpu` index; ADR-0012).

## 4. Layer shard path strategy

- AirLLM splits the model into per-layer safetensors shards and streams them at inference.
- Shards are written under `layer_shards_saving_path` on the **933 GB NVMe-backed WSL disk**
  (e.g. `results/raw/layer_shards/`), which is **git-ignored** (never committed).
- Sufficient free space must be confirmed before sharding (R-DISK); shard/disk read volume is
  recorded as the `disk_read_mb`/`disk_write_mb` metrics (heavy, expected — R-IO/R-WSL-DISK).

## 5. No secrets / token handling

- All primary candidate models are **public/ungated** → no Hugging Face token required.
- If a token were ever needed, it comes from an environment variable at runtime only — **never**
  stored in the repo, config, or shards (ADR-0003). No token handling code is added pre-need.

## 6. No model download before approved selection

- This pipeline performs **no download** until a model is selected and approved (ADR-0101).
- The Stage 3 proof uses the tiny smoke model (`Qwen/Qwen2-0.5B`) only after approval.

## 7. Acceptance criteria for the Stage 3 smoke run

- With the **tiny** model on `device='cpu'`, the pipeline: loads/shards without error, generates a
  short output, and emits a schema-valid measurement record — confirming **no CUDA-only code path
  at runtime**.
- Peak RAM stays well under ~11 GiB for the tiny model; the run completes within minutes.
- The same code path is then reused (unchanged) for the main `Qwen2-7B` run in Stage 5.

## 8. Risks & constraints

- **AirLLM streaming/token hooks** may not expose clean per-token timing → fall back to coarse
  TTFT + average TPOT, documented (see `MEASUREMENT_DESIGN.md` §8).
- **Runtime latency** on CPU is high (expected/acceptable); cap `max_new_tokens` during proofs.
- **Disk I/O** dominates AirLLM time and is WSL-VHDX-relative (R-WSL-DISK) → attribute from data.
- **Architecture compatibility** at runtime (the chosen AirLLM class vs the model) is verified in
  Stage 3 before the large run (R-AIRLLM-COMPAT).
- **Dependency matrix** must stay pinned (R-AIRLLM-DEPS); latest optimum/transformers break import.
