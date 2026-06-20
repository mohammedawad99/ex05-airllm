# Quantization Preflight & Decision Plan — Stage 9C-0

> **Planning/audit only.** No model download, no dependency change, no `uv add`, no
> `pyproject.toml`/`uv.lock` edit, no model generation, no quantization run happens in this stage.
> This document chooses *how* to close the quantization gap and states the exact approval needed
> before any Stage 9C execution.

## 1. Status

- **Quantization requirement (R-QUANT-01 / R-MEAS-QUAL): NOT_DONE.** No quantized inference has been
  run or measured. Nothing here changes that — this is a route decision, not an execution.
- **HEAD:** `b6a3b47` (Stage 9B streaming TTFT). Working tree clean except ignored artifacts.
- **Approved local model:** `Qwen/Qwen2-0.5B` only (already cached). **`Qwen2-7B` remains not
  downloaded / not approved.** AirLLM remains **blocked / not evidenced**.
- **Dependencies:** `torch==2.4.1` (CPU) + `transformers==4.44.2` present; **no GGUF/`llama-cpp`/
  `bitsandbytes` runtime is installed** (confirmed in `pyproject.toml`).

## 2. Current measured evidence (what already exists)

- **Stage 5B** — Transformers CPU, `Qwen2-0.5B`, non-streaming, 6/6:
  `results/measurements/transformers_cpu_qwen2_0_5b/` (runtime/throughput/peak-RAM; TTFT `None`).
- **Stage 9B** — Transformers CPU streaming, `Qwen2-0.5B`, 6/6, **real TTFT**:
  `results/measurements/transformers_cpu_streaming_qwen2_0_5b/`.
- Both at precision **`quantization=none`** (fp32). There is **no quantized run** yet — so there is
  no precision *comparison*, which is the open gap.

## 3. Open quantization requirement

The assignment asks to **apply and compare quantization levels** (e.g. FP16 / Q8 / Q4) and assess
the effect on memory/latency/quality. To satisfy it honestly we need **≥2 precisions measured
like-for-like** on the same model/prompts/harness, with a qualitative sample per level — produced by
a real run, never fabricated.

## 4. Route A — PyTorch dynamic INT8 (no-download, no new dependency)

- **Mechanism:** `torch.ao.quantization.quantize_dynamic(model, {torch.nn.Linear}, dtype=torch.qint8)`
  applied to the already-cached `Qwen2-0.5B`, CPU, offline. Uses the **existing `torch` dependency
  only**.
- **Comparison produced:** **fp32 (`none`) vs dynamic-INT8** — two precisions on the same harness
  (reuse the Stage 5B/9B runner pattern, `MeasurementResult` schema, `ResultWriter`). New results
  dir, e.g. `results/measurements/transformers_cpu_quant_qwen2_0_5b/`.
- **Pros:** no model download, **no new dependency**, no `pyproject.toml`/`uv.lock` change, low risk,
  fully offline/reproducible; gives a genuine measured 2-level comparison + per-level qualitative
  sample.
- **Cons:** dynamic INT8 quantizes **Linear layers only** (not embeddings/attention math), so memory
  savings on a 0.5B model may be modest and CPU INT8 kernels may not always speed up small models —
  this must be **reported honestly** (it may even be neutral/slower); it is **one quantized level
  (INT8)**, **not Q4**, so it only *partially* satisfies a strict "Q8 and Q4" reading.
- **Risk:** low. Worst case is a small but **honest** result ("dynamic INT8 reduced/much the same
  footprint and latency was X") — still a valid measured comparison.

## 5. Route B — GGUF CPU quantization sweep (Q8 + Q4) — APPROVAL-GATED

- **Mechanism:** a CPU GGUF runtime (e.g. `llama-cpp-python`) running **Q8_0** and **Q4_K_M** GGUF
  weights of a small model; measure runtime/throughput/peak-RAM + a qualitative sample per level.
- **Comparison produced:** a direct **Q8 vs Q4** sweep (optionally vs the fp32 baseline) — the
  cleanest match to the assignment's wording.
- **Pros:** directly addresses the Q8/Q4 requirement; GGUF is the standard CPU quantization route.
- **Cons / why gated:** requires **(a)** a new dependency (`uv add llama-cpp-python` → builds a
  native wheel; may need a compiler/toolchain) and **(b)** a **GGUF weight download** (new model
  artifact). Both need an explicit go-ahead and a model-selection/license/access audit. Weights must
  stay git-ignored.
- **Risk:** medium — native build may fail in WSL2; download size/time; license check needed.

## 6. Route C — Stop at the current state (no further quantization)

- Leave quantization **NOT_DONE**, documented honestly as a known limitation.
- **Pros:** zero risk, fully honest. **Cons:** lower score on the quantization requirement; the
  precision-comparison gap stays open.

## 7. Risk comparison

| route | new download | new dependency | edits pyproject/lock | satisfies requirement | risk |
| --- | --- | --- | --- | --- | --- |
| **A — torch dynamic INT8** | No | No | No | Partial (fp32 vs INT8; not Q4) | **Low** |
| **B — GGUF Q8/Q4** | **Yes (GGUF)** | **Yes (`llama-cpp-python`)** | **Yes** | Yes (Q8 vs Q4) | Medium |
| **C — stop** | No | No | No | No (stays NOT_DONE) | None |

## 8. Recommended path

1. **Recommended now: Route A** — a low-risk improvement that produces a **real, measured 2-level
   precision comparison (fp32 vs dynamic INT8)** with **no new download and no dependency change**.
   Report the effect honestly (including if INT8 is neutral/slower on this small CPU model).
2. **Route B only with explicit user approval** for a new dependency **and** a GGUF model download
   (for a true Q8/Q4 sweep). Without that approval, do not add `llama-cpp-python` or download GGUF.
3. **Do not recommend `Qwen2-7B`** at this point — it remains deferred/approval-gated and is a
   separate concern from quantization (Stage 9D).

## 9. Exact user approval needed before Stage 9C

- **To run Route A (default, no download):** approve, e.g. —
  > "Approved: run Stage 9C Route A — PyTorch dynamic INT8 on the cached Qwen2-0.5B, no download, no
  > new dependency."
- **To run Route B instead (download + dependency):** explicit approval of **both**, e.g. —
  > "Approved: Stage 9C Route B — add the `llama-cpp-python` dependency AND download a specified
  > small GGUF model (Q8 + Q4) for a CPU quantization sweep."
  Route B also requires naming/approving the specific GGUF model (license/access checked first).

## 10. Guardrails for the future quantization run (either route)

- Offline by default (`HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1`) for Route A; Route B's download is a
  one-time, explicitly-approved, audited step.
- Deterministic (`torch.manual_seed(0)`, `do_sample=False`, fixed prompts/`max_new_tokens`).
- **New results directory only** — never overwrite Stage 5B / Stage 9B raw data.
- Reuse the existing `MeasurementResult` schema + `ResultWriter`; record `quantization` per run.
- **No fabrication:** if a precision fails to run, record `success=false` with a clear reason;
  report neutral/negative effects honestly. Model **weights stay git-ignored**; only metrics +
  summaries are committed.
- Files must stay ≤150 code lines; tests use fake data (no model/network).

## 11. Files that *would* be allowed in Stage 9C (when approved)

- `src/ex05_airllm/run_transformers_cpu_quant_measurement.py` (Route A runner) and/or a GGUF runner
  (Route B), plus a small pure-helper module if needed to stay ≤150 lines.
- `tests/unit/test_*` for the new helpers (fake data only).
- New results under `results/measurements/transformers_cpu_quant_qwen2_0_5b/` (or a GGUF dir).
- Docs: `MEASUREMENT_RUNS.md`, `ANALYSIS.md`, `FINAL_GAP_AUDIT.md`, `SUBMISSION_CHECKLIST.md`,
  `REQUIREMENTS_AUDIT.md`, `TODO.md`, `PLAN.md`, `QUALITY.md`, `PROMPTS.md`, `README.md`,
  `reports/final_report.md`.
- **Route B only, with approval:** `pyproject.toml` + `uv.lock` (single dependency add via `uv add`).

## 12. Files that must remain protected (in any quantization stage)

- `results/measurements/transformers_cpu_qwen2_0_5b/**` (Stage 5B raw) — never edited.
- `results/measurements/transformers_cpu_streaming_qwen2_0_5b/**` (Stage 9B raw) — never edited.
- `results/analysis/*.json`, `figures/*.png`, `reports/measurement_summary.md` — not hand-edited.
- `pyproject.toml` / `uv.lock` — unchanged for Route A; for Route B changed **only** by an approved
  `uv add`, never hand-edited.
- No model weights/shards committed; no secrets/tokens.
