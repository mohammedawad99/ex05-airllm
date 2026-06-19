# Model Selection & Shortlist — Stage 2B

> A justified shortlist of candidate models for each experiment role. Candidate facts below
> were checked via **Hugging Face metadata only** (no weights downloaded). Final selection and
> any download happen only after explicit approval and the Stage 3 smoke run (ADR-0101).

## 1. Status

> **⚠️ Stage 4B revision (ADR-0018):** AirLLM CPU/Qwen2 is **blocked** in this environment
> (`docs/EXPERIMENT_REVISION.md`). Therefore **`Qwen/Qwen2-7B` remains the main candidate ONLY if
> the AirLLM blocker is resolved** (GPU/CUDA env or upstream fix); under the current CPU path it is
> **deferred** and **not downloaded/not approved** (`download_approved=false`). The runnable
> measurement path is now **HF `transformers` CPU on Qwen2-0.5B** (Stage 3D proven). The shortlist
> below is retained as the original plan; statuses are superseded by this revision where noted.

- **Stage 2B planning only** — a shortlist + recommendation, not a completed experiment.
- **Planning-level choices lead-approved** (tiny = `Qwen/Qwen2-0.5B`; main + direct baseline =
  `Qwen/Qwen2-7B`; optional DirectML = `Qwen/Qwen2-1.5B`; backup = Mistral-7B-Instruct-v0.2;
  stretch = Qwen2-72B). **This is approval for planning/verification only — NOT approval to
  download weights.** Weight download remains a separate, explicit gate (T2.6 / ADR-0101).
- **No model weights downloaded** — only HF API metadata (file sizes, license, gated flag).
- **No inference**, **no AirLLM/Ollama runtime**, **no benchmark.** `Qwen/Qwen2-7B` is the *main
  candidate*, not a completed run; `Qwen/Qwen2-0.5B` is the *Stage 3 smoke candidate*; DirectML
  is an *optional* GPU baseline/extension, **not** the main AirLLM backend.
- Metadata collected 2026-06-20 via `huggingface_hub` 0.36.2 `HfApi.model_info(files_metadata=True)`.

## 2. Hardware / backend constraints (from evidence)

- **WSL RAM ~11.24 GiB** (+3 GiB swap) → any model whose fp16 weights exceed ~11 GiB cannot be
  fully resident; that is exactly the "larger-than-memory" regime AirLLM targets.
- **CPU + AirLLM is the main path** (ADR-0011); `device='cpu'`, uncompressed; layer shards stream
  from the 933 GB NVMe-backed WSL disk.
- **Host AMD Radeon 890M + DirectML** works for PyTorch tensors on Windows-native Python 3.11
  (`GPU_FEASIBILITY.md` §3d) → an *optional* GPU baseline only.
- **AirLLM-on-DirectML is UNKNOWN** → the GPU path is not assumed for AirLLM.
- **Quantization on CPU** = GGUF Q4/Q8 route (bitsandbytes/4-8bit needs CUDA; R-QUANT-CPU).

## 3. Model roles

1. **Tiny smoke model** — prove the pipeline end-to-end (Stage 3) with no memory stress.
2. **Baseline direct-run model** — loaded the naïve way (HF `transformers`) to expose the
   direct-load limitation/latency on ~11 GiB (expected OOM/swap). Same model as the main
   candidate where possible, for a fair comparison.
3. **Main AirLLM candidate** — large enough to exceed ~11 GiB RAM (so direct load fails) yet
   feasible for AirLLM layer-streaming on CPU within the time budget.
4. **Optional DirectML model** — small enough for a Windows DirectML GPU baseline if used later.

## 4. Candidate table

All sizes/licenses/gated flags below are **metadata-verified** (✅) unless marked otherwise.
"Size" = sum of repo weight files (note: Mistral lists both `.bin` and `.safetensors`, so its
total double-counts; the fp16 safetensors set is ~half).

| role | candidate_model_id | family | estimated_size | expected_format | license_status | access_status | why_candidate | risk | decision_status | verification_needed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Tiny smoke | `Qwen/Qwen2-0.5B` | Qwen2 (`AirLLMQWen2`) | **~1.0 GB** ✅ | safetensors ✅ | apache-2.0 ✅ | public, ungated, no token ✅ | tiny, fits easily in 11 GiB; same family as main candidate → proves the AirLLM path cheaply | minimal | **RECOMMENDED_FOR_VERIFICATION** | confirm download size on disk; Stage 3 CPU run |
| Main AirLLM | `Qwen/Qwen2-7B` | Qwen2 (`AirLLMQWen2`) | **~15.24 GB** ✅ | safetensors ✅ | apache-2.0 ✅ | public, ungated ✅ | fp16 (~15 GB) **> 11.24 GiB RAM** → direct load OOMs (great baseline) while AirLLM streams per-layer; native in transformers 4.44.2 (no `trust_remote_code`) | CPU latency (slow, expected); shard disk I/O | **RECOMMENDED_FOR_VERIFICATION** | download size/time budget; Stage 3 then Stage 5 CPU run |
| Main (instruct alt) | `Qwen/Qwen2.5-7B-Instruct` | Qwen2 arch | **~15.24 GB** ✅ | safetensors ✅ | apache-2.0 ✅ | public ✅ | same size, better instruction outputs (nicer qualitative samples) | Qwen2.5≈Qwen2 arch — confirm `AirLLMQWen2` handles it | RECOMMENDED_FOR_VERIFICATION | confirm AirLLM class compatibility |
| Main (backup family) | `mistralai/Mistral-7B-Instruct-v0.2` | Mistral (`AirLLMMistral`) | **~14.5 GB** fp16 (repo lists ~29.5 GB incl. dup `.bin`+`.safetensors`) ✅ | safetensors + bin ✅ | apache-2.0 ✅ | public, **ungated** ✅ | independent family backup if Qwen2 hits an AirLLM issue; native in transformers 4.44.2 | larger total repo; pick safetensors only | DEFERRED (backup) | confirm safetensors-only pull; size/time |
| Baseline direct-run | *same as main* (`Qwen/Qwen2-7B`) | Qwen2 | ~15.24 GB ✅ | safetensors ✅ | apache-2.0 ✅ | public ✅ | naïve HF load on 11 GiB → expected **OOM/swap**: documents the direct-load wall the assignment asks for | may hard-crash WSL (acceptable, documented) | **RECOMMENDED_FOR_VERIFICATION** | run on the chosen main model |
| Optional DirectML | `Qwen/Qwen2-1.5B` (or `Qwen2-0.5B`) | Qwen2 | **~3.10 GB** ✅ (0.5B ~1.0 GB) | safetensors ✅ | apache-2.0 ✅ | public ✅ | small enough for a Windows-native DirectML GPU-vs-CPU baseline on the 890M | optional; must not distract from AirLLM | DEFERRED (optional) | only if GPU extension pursued |
| Stretch "massive" | `Qwen/Qwen2-72B` | Qwen2 | **~145.4 GB** ✅ | safetensors ✅ | **other** (Qwen license) ⚠️ | public, ungated ✅ | dramatically exceeds RAM; fits 933 GB disk → a striking AirLLM demo | **CPU time budget**: 72B layer-streaming likely impractically slow; non-permissive license | DEFERRED (stretch) | feasibility of runtime within budget; license terms |

## 5. Evaluation criteria

- **AirLLM compatibility / family support** — Qwen2/Mistral/Mixtral/Llama are AirLLM families
  *and* native in transformers 4.44.2 (verified, no `trust_remote_code`).
- **Model size vs RAM/disk** — main candidate must exceed ~11.24 GiB RAM (force AirLLM) yet its
  shards fit in 933 GB disk.
- **License / access** — prefer permissive (apache-2.0) and **ungated** (no token, supports the
  no-secrets policy). All primary picks are apache-2.0 + ungated.
- **Tokenizer availability** — Qwen2/Mistral ship fast tokenizers (`tokenizers` 0.19.1 present).
- **Expected direct baseline behaviour** — 7B fp16 should OOM/swap on 11 GiB (the documented wall).
- **Expected AirLLM feasibility** — per-layer streaming keeps resident memory ~one layer.
- **Quantization route** — CPU → GGUF Q4/Q8; bitsandbytes compression deferred (no CUDA).
- **Reproducibility** — fixed model id + revision pin at selection time; sizes recorded.
- **Runtime budget** — favour 7B for the main run; 72B only as a deferred stretch.

## 6. Selection strategy

1. **Start with the tiny smoke model** (`Qwen2-0.5B`) to prove the AirLLM CPU pipeline in Stage 3.
2. **Then run the main AirLLM model** (`Qwen2-7B`) — the "larger-than-memory" case.
3. **Direct baseline uses the same model** (`Qwen2-7B`) for a fair AirLLM-vs-direct comparison.
4. **Optional DirectML extension** uses a small model (`Qwen2-1.5B`/`0.5B`) and must not displace
   the AirLLM focus.

## 7. Preliminary recommendation (categories, evidence-backed — not a blind final pick)

- **Tiny smoke:** `Qwen/Qwen2-0.5B` — **RECOMMENDED_FOR_VERIFICATION** (metadata verified).
- **Main AirLLM + direct baseline:** `Qwen/Qwen2-7B` — **RECOMMENDED_FOR_VERIFICATION** (verified
  size 15.24 GB > 11.24 GiB RAM; apache-2.0; ungated; native arch).
- **Instruct alternative:** `Qwen/Qwen2.5-7B-Instruct` — RECOMMENDED_FOR_VERIFICATION (confirm AirLLM class).
- **Backup family:** `mistralai/Mistral-7B-Instruct-v0.2` — DEFERRED backup.
- **Optional GPU:** `Qwen/Qwen2-1.5B` — DEFERRED (optional extension).
- **Stretch:** `Qwen/Qwen2-72B` — DEFERRED (runtime-budget + license risk).
- **REJECTED_WITH_REASON:** gated Llama/Mistral-v0.1-style repos requiring a token — avoided to
  honour the no-secrets policy while ungated apache-2.0 equivalents exist.

> No model is *finally selected* here. These are verified candidates pending download approval
> and the Stage 3 smoke runtime check.

## 8. What must be verified before any download

- **License** terms (esp. Qwen2-72B `other`) acceptable for coursework use.
- **Disk size** of the actual download vs 933 GB free (and shard expansion headroom).
- **Model architecture compatibility** with the chosen AirLLM class at *runtime* (Stage 3).
- **`trust_remote_code`** requirement — expected **False** for Qwen2/Mistral on transformers 4.44.2.
- **Access token need** — expected **none** (all primary picks ungated); never store a token.
- **Expected download size** and whether it fits the **time budget** (esp. >7B).
- **User approval to download** — required before fetching any weights (ADR-0101).
