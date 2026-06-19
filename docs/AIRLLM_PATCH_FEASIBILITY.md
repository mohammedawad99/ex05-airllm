# AirLLM Qwen2 CPU Patch Feasibility — Stage 4A

> Can the AirLLM Qwen2 CPU meta-device blocker be fixed with a **minimal, local, project-owned**
> compatibility shim — without editing site-packages, downloading new models, or running the
> main experiment? **Conclusion: no.** A safe minimal shim is **not feasible**; the blocker is in
> AirLLM's *core* CPU parameter-streaming, not a peripheral buffer.

## 1. Status

- **Feasibility only** — investigation + one targeted shim + one patched smoke probe.
- **No new model downloads** (the probe reused the already-local re-sharded Qwen2-0.5B).
- **No benchmark.** **No Qwen2-7B.** No site-packages edits (AirLLM source read-only).

## 2. Failure recap

- **Stage 3A:** AirLLM rejected the single-file Qwen2-0.5B (needs `model.safetensors.index.json`).
- **Stage 3B:** local re-shard + untie fixed the format; AirLLM loaded and started the CPU
  forward, then failed: `RuntimeError: Tensor on device cpu is not on the expected device meta!`.
- **Stage 3C:** `torch==2.4.1+cpu` retest failed identically → **torch version ruled out**.
- **Stage 3D:** a direct HF `transformers` CPU smoke **succeeded** (pipeline proven), but that is
  not AirLLM.

## 3. Source inspection findings

- **AirLLM** (`airllm/airllm_base.py`): `init_model()` builds the model under accelerate's
  `init_empty_weights()` (all tensors on `meta`), then `forward()` re-inits each call and streams
  layers: `load_layer_to_cpu(name)` → `move_layer_to_device(state_dict)` (which calls
  `set_module_tensor_to_device(self.model, param, running_device, value=..., dtype=float16)`),
  runs the layer, then `layer.to("meta")` to free memory (lines ~560–599).
- **transformers 4.44.2 Qwen2** (`modeling_qwen2.py`): each `Qwen2Attention`/`Qwen2SdpaAttention`
  owns its **own** `Qwen2RotaryEmbedding` (non-persistent `inv_freq`/`cos_cached`/`sin_cached`,
  not saved in shards). `Qwen2RMSNorm.forward` is `return self.weight * hidden_states` (line 131).
- **Initial suspect:** the non-streamed rotary buffers stuck on `meta`.
- **Actual culprit (proved in §6 diagnostic):** a **decoder-layer parameter** — the running
  layer's `input_layernorm.weight` (an RMSNorm weight) is on `meta` when the layer executes. The
  meta `mul` is `self.weight * hidden_states` in `Qwen2RMSNorm.forward`, reached via
  `Qwen2DecoderLayer.forward` ← `airllm_base.forward` line 569 `layer(seq, **kwargs)`. So AirLLM's
  per-layer **parameter** streaming is not materializing the layer's weights onto CPU before the
  layer runs — a defect in AirLLM's *core* meta→CPU movement, not the rotary buffers.

## 4. Patch options considered

| option | risk | decision |
| --- | --- | --- |
| Rebuild the non-streamed Qwen2 `rotary_emb` buffers on CPU after each `init_model()` (instance-scoped wrap) | low; small/local/testable | **Implemented & probed** (§5/§6) — but **disproven** as the cause (rotary was not on meta). |
| Provide `position_embeddings` to each layer (newer-API approach) | n/a | **Rejected** — transformers 4.44.2 attention has no `position_embeddings` param; would error. |
| Patch AirLLM's `move_layer_to_device` / `set_module_tensor_to_device` CPU path so layer params actually land on CPU | **high** — reaches into AirLLM core streaming; effectively forks the library; fragile across versions | **Rejected** — outside "minimal, safe, local shim"; not pursued. |
| Disable prefetching | low | **Rejected** — source shows prefetching only affects load scheduling, not the device of the materialized params; would not address the meta param. |

## 5. Implemented shim

- **File:** `src/ex05_airllm/airllm_compat.py` (repo-local; **does not** edit site-packages).
- **Scope:** Qwen2 CPU only. `rebuild_qwen2_rotary_on_cpu(hf_model)` swaps any meta-device
  `Qwen2RotaryEmbedding` for a freshly-built CPU one; `patch_airllm_qwen2_cpu(model)` wraps the
  AirLLM instance's `init_model()` (instance-scoped, not a global monkeypatch) to rebuild rotary
  after every re-init. Applied only when the smoke is run with `EX05_AIRLLM_PATCH=1`.
- **Fail-closed:** raises `ValueError` if the model is not Qwen2, if `init_model`/`.model` are
  missing, or if no `Qwen2RotaryEmbedding` is found. Tested in
  `tests/unit/test_airllm_compat.py` (no model download).
- **Limitations:** experimental; makes **no claim of upstream correctness**; targets only the
  rotary buffers — which §6 shows are **not** the actual blocker, so the shim is **insufficient**.

## 6. Probe result

- **Probe:** `EX05_AIRLLM_PATCH=1` patched AirLLM CPU smoke on the local re-sharded Qwen2-0.5B
  (`device="cpu"`, `max_new_tokens=16`, no download).
- **Raw JSON:** `results/stage4a_smoke_airllm_qwen2_0_5b_patched.json` (`patched=true`,
  `success=false`); console `results/raw/stage4a_smoke_console.log`.
- **Result: FAILED** — same `RuntimeError: Tensor on device cpu is not on the expected device
  meta!`.
- **Interpretation (from a throwaway, no-download diagnostic):** the shim ran but rebuilt **0**
  rotary modules (`REBUILT_ROTARY=0`) and **no** rotary buffers were on `meta` — so rotary was
  never the cause. The full traceback shows the meta tensor is the running decoder layer's
  `input_layernorm.weight` (RMSNorm) → AirLLM's per-layer **parameter** streaming leaves layer
  weights on `meta` on this CPU path. Fixing that needs a patch to AirLLM's core streaming, not a
  small local shim.

## 7. Next decision

- **Do NOT pursue a large AirLLM core patch.** The only remaining fix touches AirLLM's core
  meta→CPU parameter movement — large, fragile, version-coupled, effectively forking the library.
- **Recommended path: documented limitation + Transformers CPU baseline.** AirLLM CPU is recorded
  as blocked for Qwen2 on this stack (R-AIRLLM-META); the experiment proceeds using the proven HF
  `transformers` CPU pipeline (Stage 3D) as the working measurement path. AirLLM remains
  **not evidenced**.
- **Possible future paths (not now, no downloads):** test an alternate AirLLM-supported family, or
  run AirLLM in a GPU environment where its meta→device streaming is the intended/used path.
- The experimental `airllm_compat.py` shim is **kept** (off by default, env-gated) as a documented,
  tested artifact of this investigation — not as a working fix.
