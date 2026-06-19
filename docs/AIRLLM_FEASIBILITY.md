# AirLLM CPU Feasibility — Stage 1D

> Companion to `docs/HARDWARE.md` and `docs/GPU_FEASIBILITY.md`. This checks whether **AirLLM**
> is practically usable for the assignment's main **CPU / RAM / disk-I/O** path in the current
> Ubuntu WSL2 environment — at the package/install/import/API level only.

## 1. Status

- **Feasibility only** — install + import + API introspection in a throwaway env.
- **No model download** — no `from_pretrained` on a real/remote model; no shards created.
- **No inference** — no forward pass, no generation.
- **No benchmark** — no timing of anything.
- **No final model selected**; no final backend committed.
- **Project environment unchanged** — all installs were in a disposable WSL venv under
  `/tmp` (outside the repo), since removed. No `pyproject.toml`, no repo dependency changes.

Collected: 2026-06-19, inside Ubuntu WSL2.

## 2. Environment

- **OS:** Ubuntu 24.04 on **WSL2** (`docs/HARDWARE.md`).
- **Python (WSL):** 3.12.3 · **uv:** 0.11.9.
- **Experiment resources (binding):** ~**11.24 GiB** RAM (WSL2 cap) + 3 GiB swap; **933 GB**
  free ext4 on an NVMe-backed VHDX; **CPU-only** (no usable GPU compute in WSL2). See
  `HARDWARE.md` §B. AirLLM exists precisely to run models **larger than ~11 GiB** by streaming
  one layer at a time from that 933 GB disk.

## 3. Package discovery & install/import probe

- **Package name:** `airllm` (PyPI). `air-llm` is **not** a package (no distribution).
- **Available versions:** latest **2.11.0** (history back to 0.9.x) — discoverable via
  `pip index versions airllm`.
- **Throwaway env:** `uv venv` (Python 3.12) under `/tmp/ex05_airllm_probe`, outside the repo.
- **Install attempt:** ✅ `airllm 2.11.0` installed. Dependencies pulled include
  `transformers`, `accelerate`, `optimum`, `safetensors`, `scipy`, `huggingface-hub`,
  `tokenizers` — **`bitsandbytes` was *not* a hard dependency**. `torch` was pinned to the
  **CPU wheel** (`2.12.1+cpu`) to keep the download light.

### Import: blocked on latest deps, then succeeded with a pinned matrix

| attempt | dependency set | import result |
| --- | --- | --- |
| 1 | airllm + **latest** optimum (2.2.0), transformers 5.12.1 | ❌ `ModuleNotFoundError: optimum.bettertransformer` (removed in optimum 2.x) |
| 2 | + `optimum==1.23.3` | ❌ `ImportError: cannot import name 'is_tf_available'` (removed in transformers 5.x) |
| 3 | + `transformers==4.44.2`, `optimum==1.23.3` | ❌ `ModuleNotFoundError: sentencepiece` (missing optional dep) |
| 4 | + `sentencepiece==0.2.1` | ✅ **`airllm 2.11.0` imported** on CPU |

**Working CPU import matrix (evidence):**
```
python 3.12 · torch 2.12.1+cpu · airllm 2.11.0
transformers 4.44.2 · optimum 1.23.3 · sentencepiece 0.2.1
(+ accelerate, safetensors, scipy, huggingface-hub 0.36.2, tokenizers 0.19.1)
torch.cuda.is_available() → False   (imported fine without CUDA)
```

> **Key dependency finding for Stage 2:** AirLLM 2.11.0 is **incompatible with the latest
> `optimum`/`transformers`**. A **pinned matrix** (`transformers` 4.4x + `optimum` 1.2x +
> `sentencepiece`) is **required** — this must be encoded in the project's `uv` lock in Stage 2.

### API surface (introspected, no model loaded)

- Public classes: `AutoModel`, `AirLLMBaseModel`, `AirLLMLlama2`, `AirLLMMistral`,
  `AirLLMMixtral`, `AirLLMQWen2`, `AirLLMChatGLM`, `AirLLMInternLM`, `AirLLMBaichuan`,
  plus helpers `split_and_save_layers`, `is_on_mac_os`, `persist`, `profiler`.
- `AirLLMBaseModel.__init__` signature:
  ```
  (model_local_path_or_repo_id, device='cuda:0', dtype=torch.float16, max_seq_len=512,
   layer_shards_saving_path=None, profiling_mode=False, compression=None,
   hf_token=None, prefetching=True, delete_original=False)
  ```

## 4. CPU feasibility interpretation

- **Is AirLLM install/import feasible?** ✅ **Yes**, with the pinned matrix above. Install and
  import both succeed; `torch` is the CPU wheel and `cuda.is_available()` is `False`.
- **Is CPU mode evidenced, inferred, unknown, or blocked?** → **EVIDENCED at the API/import
  level (not yet at runtime):**
  - `device` is a **first-class constructor parameter**; source does
    `self.device = torch.device(self.running_device)` (airllm_base.py ~L114–115), so
    `device='cpu'` is accepted and turned into a valid CPU torch device — there is no
    CUDA-only hard assumption in device setup.
  - `bitsandbytes` is imported inside a `try/except` (`bitsandbytes_installed` flag), so its
    absence is handled gracefully → the **uncompressed** CPU path does not require it.
- **What remains to test in the real experiment stage (Stage 3+):**
  - Actually instantiate a model with `device='cpu'` on a **small** model and run one
    forward pass (layer-wise from disk) to confirm no code path still assumes CUDA at runtime.
  - Confirm `split_and_save_layers` / `layer_shards_saving_path` sharding works on the WSL
    ext4 disk and measure the resulting I/O behaviour.
  - Decide model input format handling (HF repo id vs local path; safetensors sharding).

## 5. Constraints & risks

- **Python/package version compatibility (high):** requires a **pinned** `transformers` 4.4x +
  `optimum` 1.2x + `sentencepiece`; latest deps break import (see §3). Tracked as R-AIRLLM-DEPS.
- **Dependency weight:** torch + transformers + accelerate + optimum + scipy. Kept light here
  via the CPU torch wheel; the project lock must do the same to avoid a multi-GB CUDA torch.
- **Compression / quantization on CPU:** `compression='4bit'/'8bit'` is **bitsandbytes-based**
  (CUDA) → likely unavailable on this CPU path (R-QUANT-CPU). The uncompressed FP16/FP32 CPU
  path is the dependable route; GGUF Q4/Q8 via llama.cpp/Ollama remains the CPU-quant option.
- **Model format / disk:** AirLLM consumes HF (safetensors) models and writes **per-layer
  shards** to `layer_shards_saving_path`; needs ample disk (have 933 GB) — but this also means
  heavy, repeated disk reads (R-IO / R-WSL-DISK).
- **Expected high latency:** CPU-only, layer-streamed-from-disk inference is expected to be
  **slow** — acceptable and the very thing the experiment measures.
- **No model downloaded yet** — all of the above is import/API-level evidence only.

## 6. Backend implication

- **CPU + AirLLM remains the main path** — package/import feasibility is now **acceptable and
  evidenced** (with the pinned matrix), and `device='cpu'` is a supported API path. Final
  confirmation is a small-model runtime check in Stage 3.
- **Windows-native DirectML (GPU)** stays an **optional baseline/extension only**
  (`GPU_FEASIBILITY.md` §3d) — it is **not** assumed to be an AirLLM backend (AirLLM expects
  CUDA-style devices; AirLLM-on-DirectML is UNKNOWN, and the iGPU shares system RAM so it adds
  no "larger-than-memory" capacity).
- **Final model selection remains deferred** to Stage 2, sized against the ~11 GiB experiment
  budget and the AirLLM model families above.

---

*Feasibility evidence only — no model downloaded, no inference, no benchmark, no model
selected, and the project environment/repo were not modified.*
