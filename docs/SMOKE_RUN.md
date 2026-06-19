# Stage 3A/3B — Tiny AirLLM CPU Smoke Probe

> Smallest honest end-to-end AirLLM probe on CPU using **Qwen/Qwen2-0.5B** (the only model
> approved for download). **This is a smoke probe, not a benchmark** — no performance is
> measured or claimed, and the result is not generalized to larger models.
>
> **Overall status:** the tiny **AirLLM** CPU smoke did **NOT** succeed (3A format → 3B/3C
> meta-device error; torch ruled out in 3C). A **Transformers CPU fallback** smoke (Stage 3D)
> **succeeded** and **proves the measurement pipeline** — but it is **not** AirLLM and **not** a
> benchmark. Every failure and the fallback success are recorded honestly below; nothing is
> faked. See §6 (3B), §7 (3C), §8 (3D).

## 1. Status

- **Outcome: FAILED (honestly recorded)** — AirLLM aborted at the layer-sharding step.
- **Not a benchmark**; no timing/throughput claimed. **Not generalized** to Qwen2-7B.
- Probe code: `src/ex05_airllm/smoke_airllm.py`; raw evidence:
  `results/stage3_smoke_airllm_qwen2_0_5b.json` (+ console log `results/raw/stage3_smoke_console.log`).

## 2. What ran

- Script: `uv run python -m ex05_airllm.smoke_airllm` (pinned project env, CPU torch).
- Config: `model_id=Qwen/Qwen2-0.5B`, `device="cpu"`, prompt = one short sentence,
  `max_new_tokens=16`, `layer_shards_saving_path=results/raw/layer_shards_qwen2_0_5b` (git-ignored).
- Collected (real): `start/end_timestamp`, `total_runtime_seconds=6.92`, `peak_rss_mb=261.5`,
  `success=false`, `failure_reason`, full `traceback_summary`.

## 3. Failure category & evidence

**Category: AirLLM input-format incompatibility (model not pre-sharded).**

```
AssertionError: model.safetensors.index.json should exist.
  airllm/utils.py:213 in split_and_save_layers
  ← airllm_base.py:108 find_or_create_local_splitted_path
  ← airllm_qwen2.py / auto_model.py from_pretrained
```

**Root cause:** AirLLM's `split_and_save_layers` requires a model published as **multiple
safetensors shards with a `model.safetensors.index.json`** index. Qwen2-0.5B is small enough
that it ships as a **single `model.safetensors`** (no index file), so AirLLM asserts before it
can split layers. This is an AirLLM packaging assumption, not a hardware or CPU-mode problem —
the CPU instantiation path itself was reached (consistent with the Stage 1D API finding).

**Download note:** AirLLM checks the index **before** fetching weights, so only the small
metadata/tokenizer files (~12 MB: `config.json`, `tokenizer.json`, `vocab.json`, `merges.txt`,
etc.) were downloaded to the **external** HF cache (`~/.cache/huggingface`). The ~1 GB
`model.safetensors` weights were **not** downloaded, and **no weight files exist in the repo
tree**.

## 4. Corrective next steps (Stage 3B — not executed here)

In priority order:

1. **Pre-shard the tiny model locally** — load Qwen2-0.5B with `transformers` and
   `save_pretrained(..., max_shard_size="50MB")` to produce multi-shard safetensors **with**
   `model.safetensors.index.json`, then point AirLLM at that local path. Stays within the
   approved Qwen2-0.5B model; downloads only the 0.5B weights.
2. **Rely on natural sharding for the main model** — Qwen2-**7B** is published as *multiple*
   safetensors shards **with** `model.safetensors.index.json` (the 7B repo has the index that
   0.5B lacks), so AirLLM's requirement should be satisfied for the main run once its download
   is approved. The single-file issue is specific to very small models.
3. **Alternative tiny model already sharded** — only if (1)/(2) prove awkward.

> Decision direction: use approach (1) for a tiny AirLLM proof and treat (2) as the reason the
> limitation likely will not block the main `Qwen2-7B` run. Recorded as ADR-0014.

## 5. What this does and does NOT establish

- **Does:** AirLLM imports and begins instantiation on CPU in the project env (Stage 1D held);
  the failure mode is a concrete, reproducible **format requirement**, captured with evidence.
- **Does NOT:** prove an AirLLM end-to-end CPU generation (it did not run); say anything about
  performance; generalize to Qwen2-7B; justify marking the AirLLM run requirement DONE.

---

## 6. Stage 3B — Re-sharded tiny AirLLM CPU smoke (format fixed; runtime FAILED)

**Approval:** download full weights for **Qwen/Qwen2-0.5B only** (to create a local sharded
copy). No other model downloaded.

### 6.1 Preparation (succeeded)

`src/ex05_airllm/prepare_sharded_model.py` downloaded Qwen2-0.5B (~954 MB to the external HF
cache) and re-saved it to the **git-ignored** `.local_models/qwen2_0_5b_sharded/` with
`save_pretrained(max_shard_size="50MB")` → **37 shards + `model.safetensors.index.json`**.
A second issue surfaced: Qwen2-0.5B uses **tied word embeddings** (`tie_word_embeddings=true`),
so the index had **no `lm_head.weight`** and AirLLM raised `IndexError: list index out of range`
(`utils.py:302`). Fix: the prep now **unties** embeddings (clones the embedding weight into a
separate `lm_head.weight`, numerically identical) so the index includes it. Record:
`results/stage3b_prepare_qwen2_0_5b_sharded.json` → `untied_embeddings=true`,
`lm_head_in_index=true`, `success=true`.

### 6.2 AirLLM CPU smoke on the re-sharded model (FAILED at runtime)

With the local sharded path, AirLLM **accepted the format**, split all layers (including
`lm_head`) into per-layer shards, loaded them, and **started the forward pass** (peak RSS
≈ 2.7 GB, runtime 13.7 s) — then failed:

```
RuntimeError: Tensor on device cpu is not on the expected device meta!
  torch/_prims_common/check_same_device  ← _refs.mul  (during the forward pass)
```

Raw evidence: `results/stage3b_smoke_airllm_qwen2_0_5b_resharded.json` (+
`results/raw/stage3b_smoke_console.log`).

**Failure category: AirLLM CPU runtime issue (meta-device mismatch).** AirLLM is built around
GPU lazy-loading: it instantiates the model on the `meta` device and streams per-layer weights.
On the CPU path, a non-streamed tensor/buffer (e.g. a rotary/attention buffer) remains on
`meta` while activations are on `cpu`, so an elementwise op fails the same-device check. This is
an AirLLM internal CPU limitation, likely aggravated by the new **torch 2.12.1** (AirLLM 2.11
predates it). It is **not** caused by our model copy (format/lm_head are now correct).

### 6.3 Proposed corrections (Stage 3C — no further model downloads)

1. **Pin an older torch** known-good with AirLLM 2.11's meta-device CPU path (e.g. 2.3.x–2.4.x)
   and re-test — a dependency-matrix change (re-fetches *torch*, not a model); needs approval as
   it alters the pinned env (proposed as ADR-0015).
2. **AirLLM load options** — try `prefetching=False` and/or an explicit post-load `.to("cpu")`
   / buffer materialization workaround; or a documented AirLLM CPU recipe.
3. **Baseline-first fallback** — prove the *measurement pipeline* with a direct HF `transformers`
   CPU run on the tiny model (no AirLLM), while the AirLLM CPU runtime is resolved separately.
4. The main **Qwen2-7B** is natively multi-shard and **untied** (`tie_word_embeddings=false`), so
   issues #1 (index) and #2 (lm_head) won't recur — but the **meta-device** runtime issue (#6.2)
   would likely persist until corrective #1, so fix torch before any 7B attempt.

### 6.4 What Stage 3B does / does NOT establish

- **Does:** the local re-shard + untie makes AirLLM **accept and load** the model on CPU and
  begin inference — clearing the Stage 3A format blocker (R-AIRLLM-SHARD).
- **Does NOT:** complete an AirLLM CPU generation (no output produced); it is **not** a success
  and **not** a benchmark; the AirLLM-run requirement stays **PLANNED** (not EVIDENCED).

---

## 7. Stage 3C — Torch-pin retest (torch 2.4.1+cpu): meta-device error PERSISTS

**Hypothesis tested:** the Stage 3B meta-device failure was caused by the new **torch 2.12.1**.

**Action:** pinned `torch==2.4.1` (closer to AirLLM 2.11's era), `uv sync --extra dev` →
installed **`torch 2.4.1+cpu`** (`cuda_available=False`); reran the smoke on the **existing**
ignored re-sharded model (`.local_models/qwen2_0_5b_sharded/`, layers already split). No new
model downloaded.

**Result: FAILED — identical error.**
```
RuntimeError: Tensor on device cpu is not on the expected device meta!   (runtime 9.55 s, peak RSS ≈ 3.4 GB)
```
Raw evidence: `results/stage3c_smoke_airllm_qwen2_0_5b_torch241.json` (+
`results/raw/stage3c_smoke_console.log`). The 3B failure JSON is preserved unchanged.

**Conclusion: the torch version is NOT the cause.** Both `torch 2.12.1+cpu` (3B) and
`torch 2.4.1+cpu` (3C) fail identically → R-AIRLLM-META is an **AirLLM 2.11 CPU-path limitation**,
not a torch regression.

**Root cause (source inspection, `airllm/airllm_base.py`):** AirLLM builds the whole model on
the `meta` device via `init_empty_weights()`, then streams each **decoder layer** to CPU for
compute and back to `meta` (lines ~595–599). Components that are **not** in its per-layer
streaming list stay on `meta`. AirLLM only relocates a rotary buffer for **GLM**
(`if 'rotary_pos_emb' in self.layer_names_dict`, line 236); for **Qwen2** under transformers
4.44, rotary embeddings are computed by a **top-level** `model.model.rotary_emb` (`inv_freq`)
that AirLLM never moves off `meta`. During the forward pass, that `meta` rotary buffer multiplies
a `cpu` activation → the device mismatch.

**Decision on the pin:** `torch==2.4.1` is **kept** as the project pin (it is closer to AirLLM
2.11's supported range and pairs cleanly with transformers 4.44; HF CPU inference works on it),
even though it does not fix R-AIRLLM-META.

**Recommended next step — Stage 3D (Transformers CPU fallback smoke):** prove the *measurement
pipeline* with a direct HF `transformers` CPU `generate` on the tiny model (fits easily in
~11 GiB, no meta-device streaming), so Stage 3 is unblocked while AirLLM CPU stays a documented
limitation. (A secondary, fragile option — materialize `model.model.rotary_emb` / non-streamed
buffers to CPU by patching around AirLLM — is **not** recommended as the primary path.) The main
**Qwen2-7B** would hit the **same** rotary/meta issue, so AirLLM CPU must be resolved before any
7B attempt.

---

## 8. Stage 3D — Transformers CPU fallback smoke (SUCCEEDED — pipeline proven)

**Goal:** prove the measurement / result-writing pipeline end-to-end with **plain HF
`transformers` on CPU** (no AirLLM, no meta-device streaming), using the already-downloaded
Qwen2-0.5B. **This is a fallback smoke — not an AirLLM success and not a benchmark.**

**Action:** `src/ex05_airllm/smoke_transformers_cpu.py`, run **offline**
(`HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1`, `local_files_only=True`) → loaded Qwen2-0.5B from
the **cache only** (no download), `device="cpu"`, `do_sample=False`, `max_new_tokens=16`.

**Result: SUCCESS.** Evidence:
`results/stage3d_smoke_transformers_qwen2_0_5b_cpu.json` (+
`results/raw/stage3d_smoke_console.log`).
- `success=true`; coherent 16-token output:
  *"An operating system is a software program that manages the hardware and software resources of a"*.
- Pipeline-proof measurements (single smoke run, **not** a benchmark): `load_seconds≈4.6`,
  `generation_seconds≈6.2`, `total_runtime_seconds≈14.9`, `peak_rss_mb≈4664`, `output_tokens_est=16`.

**What this establishes:** the result schema, timers, RSS sampling, and JSON writer all work
end-to-end on a real CPU generation → the **measurement pipeline is proven** (Stage 3 DoD for the
writer/runner mechanism; R-REPRO PARTIALLY_EVIDENCED).

**What this does NOT establish:** it is **not** an AirLLM success (AirLLM CPU stays blocked by
R-AIRLLM-META); **not** a benchmark; **not** generalized to Qwen2-7B; **no** final performance is
claimed. The numbers above are incidental to one smoke run, recorded to demonstrate the pipeline
captures metrics — not as performance results.

---

## 9. Stage 4A — patched AirLLM smoke (still FAILED; see patch-feasibility doc)

A Stage 4A attempt applied an experimental, local Qwen2 rotary shim (`EX05_AIRLLM_PATCH=1`) to the
AirLLM CPU smoke on the local re-sharded model (no download). It **still failed** with the same
meta-device error: `results/stage4a_smoke_airllm_qwen2_0_5b_patched.json` (`patched=true`,
`success=false`). A no-download diagnostic showed the rotary was **not** the cause — the meta
tensor is a running decoder layer's `input_layernorm.weight` (AirLLM's core CPU param streaming).
**A minimal safe shim is infeasible**; full analysis and the decision (documented limitation + HF
baseline) are in **`docs/AIRLLM_PATCH_FEASIBILITY.md`** (ADR-0017). AirLLM CPU remains not evidenced.
