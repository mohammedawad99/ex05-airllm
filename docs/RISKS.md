# Risk Register

> **STATUS: STAGE 0.** Identified risks with likelihood, impact, mitigation, contingency,
> and owner. Re-reviewed at every stage close. Likelihood/Impact scale: Low / Med / High.
> IDs are referenced from `REQUIREMENTS_AUDIT.md`.

---

| id | risk | L | I | trigger / signal | mitigation (preventive) | contingency (if it happens) | owner |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R-MODELSIZE | **Model too large** — the chosen model can't run even under AirLLM, or never finishes in a reasonable time | High | High | OOM despite layer-wise loading; disk thrash; runtime unbounded | Size the model against real hardware (after R-HW-01); start with a small proof model (Stage 3); cap max output tokens; estimate shard/disk footprint before download | Step down model size or quantization; document the failure as a finding (negative result is valid, ADR-0005) | Human |
| R-AIRLLM-COMPAT | **AirLLM compatibility** — model architecture/format unsupported, sharding fails, or API mismatch | Med | High | Class-mismatch errors; sharding step errors; unsupported architecture | Prefer well-supported families (`AutoModel`, Llama2/Mistral/Mixtral/QWen2 classes seen in 1D); pin AirLLM version; verify support before committing to a model | Switch to a supported model; record incompatibility in DECISIONS/reports | Human/AI |
| R-AIRLLM-DEPS | **AirLLM dependency-matrix breakage** — AirLLM 2.11.0 imports `optimum.bettertransformer` (removed in optimum 2.x) and relies on `transformers` 4.x APIs (`is_tf_available`, removed in transformers 5.x); latest deps break import | High | High | 1D: `ModuleNotFoundError optimum.bettertransformer`; `ImportError is_tf_available`; missing `sentencepiece` | **Pin** a known-good matrix in the Stage 2 `uv` lock: `transformers==4.44.2`, `optimum==1.23.3`, `sentencepiece`, CPU `torch` wheel (`2.12.1+cpu` worked); avoid the default CUDA torch | If pins drift/break, re-resolve from the 1D working matrix in `AIRLLM_FEASIBILITY.md`; consider an alternate AirLLM version | Human/AI |
| R-PYENV | **Python / PyTorch / CUDA mismatch** — version incompatibilities break install or GPU use | Med | High | Install errors; CUDA "not available"; ABI/driver mismatches | Pin versions via `uv` + `uv.lock`; match Torch build to the documented CUDA/driver (after R-HW-01); record exact versions | Fall back to CPU path; pin a known-good matrix; document constraints | Human/AI |
| R-DISK | **Disk space** — model shards + quantized copies + caches exceed free space | Med | High | `df` low; download/sharding aborts mid-way | Check free space before download (R-HW-01 → U-DISK-FREE); estimate footprint; git-ignore weights; clean intermediate shards | Choose a smaller model/precision; relocate cache; free space | Human |
| R-IO | **I/O bottleneck** — AirLLM is disk-bound; slow disk (HDD/SATA) dominates TPOT | High | Med | Very high TPOT; low throughput; CPU/GPU idle waiting on reads | Document disk type (U-DISK-TYPE); measure and *attribute* the bottleneck (this is a core finding, not just a problem); prefer NVMe if available | Report I/O as the dominant bottleneck with evidence (Roofline argument); this is an expected, reportable result | AI |
| R-SECRETS | **Secrets exposure** — HF token / API key committed or leaked | Low | High | Token string appears in a diff/file; key in code | `.gitignore` for `.env`/keys/credentials; secrets via `os.environ` only; `.env-example` placeholders; no `git add .`; pre-push scan | Rotate/revoke the exposed key immediately; purge from history; re-issue | Human |
| R-NONREPRO | **Fake or non-reproducible measurements** — numbers that can't be regenerated, or instrumentation that distorts timings | Med | High | Numbers don't match on re-run; no recorded command/seed; metric defined ambiguously | Define every metric precisely (`PRD_measurement.md`); fix seeds; record exact commands/env; separate raw vs summary results; never hand-edit numbers | Re-run with documented method; discard un-reproducible numbers; annotate variance | AI/Human |
| R-OVERCLAIM | **Overclaim** — stating conclusions stronger than the evidence (specs, costs, energy, quality) | Med | High | Claims without an evidence path; estimates presented as measurements | Evidence-bound reporting (ADR-0005); label estimates; state assumptions; SUBMISSION_CHECKLIST honesty gate; mark unknowns `NEEDED_USER_INPUT` | Soften/retract the claim; add caveats; tie to evidence or remove | Human |

### Added in Stage 1A (revealed by measured hardware — see `HARDWARE.md`)

| id | risk | L | I | trigger / signal | mitigation (preventive) | contingency (if it happens) | owner |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R-NOGPU | **GPU usable via DirectML, but not the AirLLM compute path** — the AMD Radeon 890M now runs PyTorch via Windows-native DirectML on Python 3.11 (1C-D), so the GPU is a *verified optional* baseline/extension. However, no CUDA/ROCm exists in WSL, **AirLLM-on-DirectML is UNKNOWN**, and the iGPU shares system RAM (no extra capacity) → AirLLM core stays **CPU**. | Med | Med | 1C-D DirectML matmul OK on Windows-native Py3.11; Ubuntu still has no CUDA/ROCm; AirLLM/DirectML unproven | Use CPU for the AirLLM core (AVX-512/VNNI, GGUF); treat DirectML as an *optional* GPU baseline/extension run on Windows-native Py3.11; resolve §5 (AirLLM CPU mode, AirLLM/DirectML) before the backend ADR. Never frame this as "no GPU". | Report CPU AirLLM as the main result; optionally add a GPU-vs-CPU baseline; mark peak-VRAM for the WSL/CPU runs `N/A_WITH_RATIONALE`; revisit ADR-0008/0010 with the new evidence | Human/AI |
| R-WSL-MEM | **WSL2 memory cap (~11 GiB of ~24 GB host)** — Linux sees <half of host RAM; baseline OOMs earlier than the host specs suggest | High | Med | `free -h` ≈ 11 GiB vs host CIM ≈ 24 GB; OOM/swap thrash | Size targets against the ~11 GiB experiment budget; note the cap is raisable via host `.wslconfig` (user action, not assumed) | Document OOM as the intended baseline failure; or request a higher cap from user | Human |
| R-QUANT-CPU | **CPU quantization route** — AirLLM's `compression='4bit'/'8bit'` is `bitsandbytes`-based (CUDA); 1D confirmed `bitsandbytes` is *optional* (try/except) so the **uncompressed** CPU path works, but on-CPU compression likely won't | Med | High | 1D: `bitsandbytes` not a hard dep; compression docstring is bnb-based | Use the uncompressed FP16/FP32 AirLLM CPU path; for quantization use CPU-compatible **GGUF Q4/Q8** (llama.cpp/Ollama); decide route in Stage 2 ADR | Use GGUF-based quantization; document the constraint and chosen route in an ADR | Human/AI |
| R-WSL-DISK | **Virtualized disk I/O uncertainty** — host media is now known to be an **NVMe SSD**, but it is reached via the WSL2 VHDX/9p layer, so AirLLM's per-token I/O cost is still unpredictable until measured | Med | Med | Host `Get-PhysicalDisk` = NVMe SSD; WSL `lsblk` = "Virtual Disk" (overhead opaque) | **Measure** disk throughput/latency during runs; attribute the bottleneck from data, not from the media type | Report measured I/O behavior; do not claim a speed from "NVMe" alone | AI |
| R-EVID-GAP | **Incomplete in-WSL enumeration** — `lspci` unavailable in Ubuntu; partly mitigated by host-side CIM (Stage 1B) which enumerates CPU/GPU/disk | Low | Low | `which lspci` empty in Ubuntu | Use host CIM as the authoritative enumeration; avoid absolute claims that rely only on the missing tool | Re-probe with `lspci` after a user-approved `pciutils` install if needed | Human |

---

## Cross-cutting controls

- **Stage gates:** No stage starts until the prior stage's Definition of Done is met
  (`PLAN.md`), bounding cascade failures.
- **Audit re-check:** `REQUIREMENTS_AUDIT.md` is re-audited each stage; risk column links
  requirements to the risks above.
- **Honesty gate:** `SUBMISSION_CHECKLIST.md` includes explicit no-fabrication / evidence
  checks before submission.

## Risk review log

| date | stage | change |
| --- | --- | --- |
| 2026-06-19 | 0 | Initial register created with the eight required risks. |
| 2026-06-19 | 1A | Added R-NOGPU, R-WSL-MEM, R-QUANT-CPU, R-WSL-DISK, R-EVID-GAP after measuring hardware (`HARDWARE.md`). |
| 2026-06-19 | 1B | Reconciled with host-side CIM evidence: R-NOGPU now a confirmed design constraint (host iGPU exists but unusable in WSL2); R-WSL-MEM quantified (~11 GiB of ~24 GB); R-WSL-DISK media known (NVMe SSD) but I/O still to be measured; R-EVID-GAP partly mitigated by host CIM. |
| 2026-06-19 | 1C-A | Re-opened R-NOGPU as not-yet-closed: GPU feasibility diagnostics (`GPU_FEASIBILITY.md`) show the iGPU is DX12_2 capable; DirectML paths queued for a compatibility check before any backend decision (links to ADR-0008). |
| 2026-06-19 | 1C-B | Isolated DirectML probe (throwaway Windows venv): `torch-directml` installs but **fails to import** on the only compatible Windows Python (3.9 needs 3.10+; 3.13 has no wheel). All GPU backends now `BLOCKED` on the current toolchain (evidence-based, not hardware). R-NOGPU mitigation direction confirmed → CPU/AirLLM; re-openable via a Python 3.10–3.12 install. |
| 2026-06-19 | 1C-C | Compatible-Python retest: no Python 3.10–3.12 installed; `winget` could install one but that persistent host change was **not** auto-performed (stop-and-report). DirectML retest deferred to a user-gated Python install; Windows-native DirectML stays `BLOCKED` under current setup; CPU/AirLLM remains main path. |
| 2026-06-19 | 1C-D | **User-authorized** Python 3.11.9 install (user-scope, no admin); DirectML smoke test **succeeded** on the Radeon 890M (matmul on `privateuseone:0`); `transformers` imports. R-NOGPU downgraded: GPU is now a *verified optional* baseline/extension lane, but AirLLM-on-DirectML is UNKNOWN and CPU/AirLLM stays the main path (iGPU shares RAM → no extra memory budget). |
| 2026-06-19 | 1D | AirLLM CPU feasibility: `airllm 2.11.0` installs+imports on CPU with a **pinned matrix** (transformers 4.44.2 + optimum 1.23.3 + sentencepiece + torch cpu); latest deps break import → added **R-AIRLLM-DEPS**. `device='cpu'` is a first-class API param and `bitsandbytes` is optional → CPU path EVIDENCED at API level (runtime check deferred to Stage 3). R-QUANT-CPU refined. |
