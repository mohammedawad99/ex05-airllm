# Decision Log (ADRs)

> **STATUS: STAGE 0.** Architecture Decision Records. Each ADR captures a decision, its
> context, the alternatives weighed, the consequences, and its status. Decisions that
> require hardware or experiment data are recorded as **PROPOSED/DEFERRED** until the
> evidence exists — they are not pre-decided.

**ADR statuses:** `PROPOSED` · `ACCEPTED` · `DEFERRED` · `SUPERSEDED`.

---

## ADR-0001 — Documentation-first (Stage 0 before any code)
- **Status:** ACCEPTED
- **Context:** Course methodology (guidelines §1.4) mandates full requirements before code.
  The grader inspects every file and rewards planning and traceability.
- **Decision:** Produce the complete requirements/planning/risk/quality/cost documentation
  set and repo scaffold in Stage 0; write no implementation code, download no models,
  install no dependencies.
- **Alternatives:** Start coding a quick AirLLM demo first (rejected: violates methodology,
  risks fabricated/un-audited claims).
- **Consequences:** Strong audit trail; slower start to "real" runs; everything downstream
  traces to a documented requirement.

## ADR-0002 — `uv` as the sole package manager
- **Status:** ACCEPTED
- **Context:** Guidelines §8.4 require `uv`; `pip`/`python -m`/`venv` direct use is forbidden.
- **Decision:** From Stage 2, manage all dependencies via `uv` (`uv add`/`uv sync`/`uv run`);
  commit `pyproject.toml` + `uv.lock`. No dependencies installed in Stage 0.
- **Consequences:** Reproducible, locked environment; all commands run through `uv run`.

## ADR-0003 — Secrets never in the repository
- **Status:** ACCEPTED
- **Context:** Hugging Face tokens / API keys must never be committed (assignment §6.2,
  guidelines §7.4).
- **Decision:** Secrets come only from `os.environ` or interactive login at runtime; `.env`
  and key/credential files are git-ignored; a placeholder `.env-example` is committed when
  secrets are first needed (Stage 4). `.gitignore` enforces this from Stage 0.
- **Consequences:** Safe public repo; runtime requires the user to set env vars / log in.

## ADR-0004 — Layered, SDK-fronted architecture with a central API Gatekeeper
- **Status:** ACCEPTED (design intent; realized in Stage 9A — see ADR-0020)
- **Context:** Guidelines §4–5 require all logic behind an SDK and all external API calls
  through a central gatekeeper (rate limit, retry, queue, logging).
- **Decision:** Adopt the layered design in `PLAN.md` §2; route every API call through
  `ApiGatekeeper`; keep CLI/analysis layers thin; OOP + DRY; files ≤150 lines.
- **Consequences:** Clear boundaries, testable units, no scattered API calls.

## ADR-0020 — Thin SDK facade + fail-closed API gatekeeper; gatekeeper requirement N/A today
- **Status:** ACCEPTED (Stage 9A, docs+code; no model run/download)
- **Context:** A grading audit flagged that the SDK facade and the API-gatekeeper status were not
  closed. The project makes **no live external-API calls** (On-Prem-vs-API cost is assumption-based,
  not queried), so a full gatekeeper is not exercised — but the status must be explicit.
- **Decision:**
  1. Add a **thin SDK facade** `src/ex05_airllm/sdk.py` exposing stable entry points (version,
     prompts, measurement loading, summary stats, cost/energy estimate) by **delegating** to the
     existing modules — no business logic duplicated, **no model loading, no network**. (R-ARCH-SDK
     → PARTIALLY_EVIDENCED.)
  2. Mark **R-ARCH-GATEKEEPER `N/A_WITH_RATIONALE`** (no live API), but ship a minimal **fail-closed,
     disabled-by-default** `ApiGatekeeper` (`api_gatekeeper.py`) as the single choke point a future
     live path must use; it performs **no network I/O** and is unit-tested. Config example:
     `config/rate_limits.example.json`.
  3. Commit **`.env-example`** (dummy values only; tokens optional/blank; committed results are
     inspectable without credentials). (R-CONFIG-ARCH → EVIDENCED.)
- **Honesty:** This does **not** add any experimental result. Quantization/TTFT/large-model gaps stay
  open (PLAN §8 Stage 9B–9D); the repo is **not** claimed self-assessment-100-ready.
- **Consequences:** Professional-rubric gaps (SDK, gatekeeper status, `.env-example`) are closed at
  low risk; experimental completeness is unchanged and honestly reported.

## ADR-0005 — Honest, evidence-bound reporting; negative results are valid
- **Status:** ACCEPTED
- **Context:** Assignment §2 and §6.2: the goal is a correct, well-analyzed experiment, not
  a fast/high-quality model; a well-analyzed negative result outscores an unsupported claim.
- **Decision:** No result is stated without a real evidence file; estimates are labelled as
  estimates; failures (including a crashing baseline) are documented as findings.
- **Consequences:** Credibility; some sections may report "it failed, and here's why".

## ADR-0006 — Versioning starts at 1.00
- **Status:** ACCEPTED
- **Context:** Guidelines §8.1 require explicit version tracking in code and config.
- **Decision:** Code (`version.py`), `config/*.json` (`"version"`), and rate-limit config
  start at `1.00` and increment on meaningful change.

## ADR-0007 — Capture hardware evidence before selecting a model (Stage 1A)
- **Status:** ACCEPTED
- **Context:** A model can only be responsibly chosen against the *real* machine; inventing
  specs would violate the no-fabrication rule and produce an infeasible plan.
- **Decision:** Before any model selection, probe the machine with read-only commands and
  record the results in `docs/HARDWARE.md`; gate Stage 2 model selection on that evidence.
- **Evidence:** `docs/HARDWARE.md` (collected 2026-06-19).
- **Consequences:** Stage 2 selection is calibrated to ~11.24 GiB RAM, CPU-only, 933 GB disk;
  hardware audit items move to `PARTIALLY_EVIDENCED` rather than guessed.

## ADR-0008 — Target a CPU-only execution path (evidence-backed)
- **Status:** ACCEPTED (reversible if a GPU compute stack is later enabled)
- **Context:** Stage 1A probes found no usable compute GPU: `nvidia-smi`/`rocm-smi` absent,
  no NVIDIA kernel driver, OpenGL renderer is `llvmpipe` (CPU), 0 MB dedicated VRAM.
  `/dev/dxg` exists but no CUDA/ROCm libraries are installed. `lspci` is unavailable, so this
  is framed as "no *usable* compute GPU detected", not "no GPU hardware".
- **Decision:** Plan all experiments for CPU-only execution; treat the peak-VRAM metric as
  `N/A_WITH_RATIONALE`; choose models/quantization feasible on CPU within ~11 GiB resident.
- **Consequences:** AirLLM `bitsandbytes` (CUDA) quantization is likely off the table →
  CPU-compatible GGUF Q4/Q8 becomes the probable route (open question R-QUANT-CPU, ADR-0103).
  Slow, I/O-bound runs are expected and acceptable.

## ADR-0009 — Calibrate model selection to execution-environment resources, not host specs
- **Status:** ACCEPTED
- **Context:** Stage 1B host-side CIM evidence shows the physical laptop is larger than what
  the experiment can use: host ≈ **24 GB** RAM, an AMD Radeon 890M iGPU, and a ~1 TB **NVMe
  SSD** — but inside Ubuntu WSL2 the experiment sees only ≈ **11.24 GiB** RAM, **no usable
  GPU/CUDA/ROCm**, and disk via a VHDX layer. Sizing the model against host specs would
  overstate capacity and produce an infeasible plan.
- **Decision:** All model-selection and feasibility decisions are calibrated to the
  **resources actually available inside the WSL2 execution environment** (`HARDWARE.md` §B:
  ~11 GiB RAM, CPU-only, NVMe-backed disk), **not** to the larger host hardware. A host
  capability is only counted when it is evidenced *inside* WSL2.
- **Evidence:** `docs/HARDWARE.md` §A (host), §1–§6 (WSL), §B (intersection).
- **Consequences:** The "larger-than-memory" target is sized against ~11 GiB; the host GPU
  is excluded from the compute plan; the NVMe finding informs but does not pre-judge I/O
  performance (still to be measured). If the user raises the WSL2 RAM cap via `.wslconfig`,
  this decision is revisited with new evidence.

## ADR-0010 — Defer the execution-backend decision pending a GPU feasibility check
- **Status:** ACCEPTED (qualifies ADR-0008)
- **Context:** Stage 1C-A diagnostics (`docs/GPU_FEASIBILITY.md`) confirm the host has a
  DirectX 12_2-capable AMD Radeon 890M iGPU, while inside WSL2 there is currently no
  CUDA/ROCm backend and no installed `torch`/`torch-directml`/`transformers`/`airllm`.
  DirectML paths (WSL and Windows-native) are **not disproven**, only unverified.
- **Decision:** Do **not** finalize the execution backend yet. The CPU+AirLLM path (ADR-0008)
  remains the working assumption, but the **final** backend choice is deferred until the §5
  compatibility questions in `GPU_FEASIBILITY.md` are resolved with evidence. Any eventual
  "GPU not used" statement must cite feasibility evidence, never assume the absence of a GPU.
- **Evidence:** `docs/GPU_FEASIBILITY.md` §2–§5.
- **Consequences:** Keeps the GPU option honestly open; prevents premature closure; the
  backend ADR (revisiting ADR-0008) is recorded once the compatibility check completes.
- **Update (Stage 1C-B):** The DirectML compatibility probe ran in an isolated throwaway
  Windows venv: `torch-directml` **installs but fails to import** on the only wheel-compatible
  Windows Python (3.9 requires 3.10+; 3.13 has no wheel), and no Python 3.10–3.12 is
  installed. **All GPU backends are therefore `BLOCKED` on the current toolchain** —
  evidence-based, not a hardware limitation. The practical direction is now firmly
  **CPU + AirLLM**; the GPU/DirectML option stays re-openable only if a Python 3.10–3.12
  runtime is installed. The **final** backend ADR is still deferred pending the last §5 checks
  (AirLLM CPU mode and the quantization route); at this 1C-B point no GPU path was viable on
  the then-current toolchain (**later superseded by the 1C-D update below**, which got DirectML
  working on Python 3.11).
- **Update (Stage 1C-C):** Confirmed no Python 3.10–3.12 is installed; `winget` could install
  `Python.Python.3.11` (3.11.9), but installing a persistent Python runtime on the user's host
  is a global change beyond a throwaway venv (and may require UAC), so per the stop-and-report
  rule it was **not** auto-performed. Completing the DirectML retest is a **user-gated**
  action. This does not change the working direction (**CPU + AirLLM**); it only keeps the GPU
  option explicitly re-openable with the user's authorization.
- **Update (Stage 1C-D):** The user **authorized** the install; Python **3.11.9** was added
  (winget, user-scope, no admin) and the DirectML smoke test **succeeded** — the Radeon 890M
  ran a 64×64 matmul on `privateuseone:0`, and `transformers` imported (no model). The throwaway
  venv was deleted; the project env/repo were untouched. **Conclusion:** the GPU is a *verified
  optional* GPU baseline/extension lane (Windows-native), but **CPU + AirLLM remains the main
  path** for the AirLLM/memory-management focus because (a) AirLLM-on-DirectML is UNKNOWN and
  (b) the iGPU shares system RAM, so it adds no "larger-than-memory" capacity. The final backend
  ADR stays deferred pending §5 (AirLLM CPU mode / AirLLM-DirectML / quantization route).

## ADR-0011 — CPU + AirLLM is the main path (feasibility evidenced); pin the dependency matrix
- **Status:** ACCEPTED (import/API-level; runtime confirmation in Stage 3)
- **Context:** Stage 1D installed and imported AirLLM in a throwaway WSL venv. `airllm 2.11.0`
  imports on **CPU** (torch CPU wheel, `cuda.is_available()` False); `device` is a first-class
  constructor parameter resolved via `torch.device(...)` (so `device='cpu'` is supported), and
  `bitsandbytes` is optional (try/except). However, AirLLM is **incompatible with the latest
  `optimum`/`transformers`** — a pinned matrix is required.
- **Decision:**
  1. **CPU + AirLLM is the project's main execution path** for the AirLLM/memory-management
     focus; the Windows DirectML GPU lane stays an *optional* baseline/extension (ADR-0010).
  2. The Stage 2 `uv` environment **must pin** a known-good matrix (from `AIRLLM_FEASIBILITY.md`
     §3): `transformers==4.44.2`, `optimum==1.23.3`, `sentencepiece`, and a **CPU `torch`
     wheel** — never the default CUDA torch.
  3. Quantization on this CPU path uses **GGUF Q4/Q8** (llama.cpp/Ollama), not AirLLM's
     bitsandbytes compression (R-QUANT-CPU).
- **Evidence:** `docs/AIRLLM_FEASIBILITY.md` (§3 working matrix; §4 device/bitsandbytes source).
- **Consequences:** Unblocks Stage 2 model selection (sized to ~11 GiB, AirLLM families seen in
  1D: Llama2/Mistral/Mixtral/QWen2). The **final backend ADR** (revisiting ADR-0008) is taken
  after a Stage 3 small-model runtime check confirms no remaining CUDA-only code path at run time.

## ADR-0012 — Project skeleton: hatchling + src-layout, `uv`-locked, pinned AirLLM matrix, CPU torch
- **Status:** ACCEPTED
- **Context:** Stage 2A needs a reproducible Python environment before any runner code, with
  the AirLLM stack that 1D proved (and which breaks on latest optimum/transformers).
- **Decision:**
  - **Build:** `hatchling` backend, **src-layout** package `src/ex05_airllm` (`version.py` as
    the single version source, `constants.py` for the result schema / labels — no magic values).
  - **Deps:** `pyproject.toml` is the source of truth; `uv.lock` committed; **no
    `requirements.txt`**, **no direct `pip`** for the project env (R-UV). Pinned per 1D:
    `airllm==2.11.0`, `transformers==4.44.2`, `optimum==1.23.3`, `sentencepiece`.
  - **Torch:** sourced from the **`pytorch-cpu` index** (`[tool.uv.sources]`) so only CPU
    wheels are used (`torch 2.12.1+cpu`), never a multi-GB CUDA build.
  - **Quality:** `ruff` (line-length 100, py312, `E,F,W,I,N,UP,B,C4,SIM`), `pytest` +
    coverage `fail_under=85`, every Python file ≤150 code lines.
  - **Version:** starts at `1.0.0` in code + `pyproject` + config, test-enforced (R-VERSION).
- **Evidence:** `pyproject.toml`, `uv.lock`; Stage 2A validation (uv sync OK; 4 tests, 100%
  coverage; ruff/format clean; line-count OK).
- **Consequences:** Reproducible CPU env ready for Stage 2B model selection and Stage 3 code.
  Resolution succeeded with **no version conflicts**; if the pins ever drift, re-resolve from
  `docs/AIRLLM_FEASIBILITY.md` §3. No model/inference/benchmark performed.

## ADR-0014 — Handle AirLLM's pre-sharded-safetensors requirement
- **Status:** ACCEPTED (corrective plan; implemented in Stage 3B)
- **Context:** The Stage 3A smoke (`docs/SMOKE_RUN.md`) showed AirLLM's `split_and_save_layers`
  requires a model published as **multi-shard safetensors with `model.safetensors.index.json`**.
  Qwen2-0.5B ships as a **single** `model.safetensors` (no index) → `AssertionError` before any
  weights are even downloaded. CPU mode itself was not the problem.
- **Decision:**
  1. For the **tiny AirLLM proof**, re-save Qwen2-0.5B locally as sharded safetensors via
     `transformers` `save_pretrained(max_shard_size="50MB")` (produces the index), then point
     AirLLM at that local path — staying within the approved tiny model.
  2. For the **main run**, use `Qwen2-7B`, which is **already** published as multiple safetensors
     shards **with** the index → AirLLM's requirement is satisfied natively (the single-file
     issue is specific to very small models). No 7B download until separately approved.
- **Evidence:** `results/stage3_smoke_airllm_qwen2_0_5b.json`, `docs/SMOKE_RUN.md`.
- **Consequences:** The tiny smoke is unblocked in Stage 3B without new model approvals; the
  finding de-risks the main run rather than blocking it. No fabrication — the failure stands as
  recorded.

## ADR-0015 — Corrective for the AirLLM CPU meta-device runtime failure (proposed)
- **Status:** PROPOSED → needs user approval (changes the pinned env)
- **Context:** Stage 3B (`SMOKE_RUN.md` §6) fixed the model-format issues (re-shard + untie), and
  AirLLM then loaded and began the forward pass on CPU but failed with
  `RuntimeError: Tensor on device cpu is not on the expected device meta!` (R-AIRLLM-META). Root
  cause: AirLLM's `meta`-device lazy loading leaves a non-streamed buffer on `meta` during CPU
  compute, likely aggravated by **torch 2.12.1** (AirLLM 2.11 predates it).
- **Decision (proposed, not yet executed):**
  1. **Pin an older AirLLM-compatible torch** (e.g. 2.3.x–2.4.x CPU) and re-test the tiny smoke.
     This re-fetches *torch* (a dependency, not a model) and alters `uv.lock`, so it needs
     explicit approval before execution.
  2. If still failing, try AirLLM load options (`prefetching=False`, explicit buffer
     materialization to CPU) and/or a documented AirLLM CPU recipe.
  3. **Fallback:** prove the measurement pipeline with a **direct HF `transformers` CPU** run on
     the tiny model (no AirLLM) so Stage 3 is not fully blocked, while AirLLM CPU is resolved.
- **Evidence:** `results/stage3b_smoke_airllm_qwen2_0_5b_resharded.json`, `SMOKE_RUN.md` §6.
- **Consequences:** Until resolved, the AirLLM-run requirement (R-AIR-01) stays **PLANNED** (not
  evidenced). No 7B download should be attempted until the CPU meta-device issue is fixed (the
  same runtime path would be used).
- **Update (Stage 3C — torch ruled out):** Pinned `torch==2.4.1+cpu` and reran the smoke on the
  existing re-sharded model → **identical** `meta`-device error (`SMOKE_RUN.md` §7). So the torch
  version is **not** the cause; R-AIRLLM-META is an AirLLM 2.11 CPU-path limitation (it leaves
  Qwen2's top-level `rotary_emb` on `meta`). **Torch 2.4.1 is kept** as the project pin (closer to
  AirLLM's era, clean with transformers 4.44, fine for HF CPU). Corrective option #1 (torch pin)
  is now **closed as ineffective**; the path forward is ADR-0016.

## ADR-0016 — Stage 3D Transformers CPU fallback to prove the measurement pipeline
- **Status:** ACCEPTED — **EVIDENCED** (executed in Stage 3D)
- **Context:** AirLLM CPU is blocked by R-AIRLLM-META (rotary buffer on `meta`), and the torch
  pin did not help (ADR-0015). The measurement pipeline (timers, RSS, result schema) should not
  stay blocked on an AirLLM-internal bug.
- **Decision:** add a **direct HF `transformers` CPU** smoke on the already-downloaded tiny
  Qwen2-0.5B (no AirLLM, no meta-device streaming) to produce a real, schema-valid measurement
  record and prove the pipeline end-to-end. AirLLM CPU remains a documented limitation.
- **Evidence:** `results/stage3d_smoke_transformers_qwen2_0_5b_cpu.json` — `success=true`, coherent
  16-token output, with load/generation/runtime/RSS/token metrics; `SMOKE_RUN.md` §8.
- **Consequences:** Stage 3 pipeline proof is **done via the HF fallback** (R-REPRO partially
  evidenced) **without claiming AirLLM works** — R-AIR-01 stays PLANNED until AirLLM itself runs.
  No 7B until R-AIRLLM-META is resolved (same rotary path). Not a benchmark.

## ADR-0017 — AirLLM CPU for Qwen2 is a documented limitation; use the HF CPU baseline
- **Status:** ACCEPTED — **EVIDENCED** (Stage 4A)
- **Context:** Stage 4A tested whether a **minimal, local, project-owned** shim could fix the
  AirLLM Qwen2 CPU meta-device error. A scoped, tested rotary shim (`airllm_compat.py`) was
  implemented and probed; the patched smoke still failed, and a no-download diagnostic showed the
  rotary was **not** the cause (0 rebuilt, no meta buffers) — the meta tensor is a running decoder
  layer's **parameter** (`input_layernorm.weight`), i.e. AirLLM's core per-layer meta→CPU
  parameter streaming. Fixing that would require patching AirLLM's core (large, fragile, version-
  coupled) — outside a minimal safe shim, and forbidden (no site-packages edits).
- **Decision:** Do **not** pursue a large AirLLM core patch. **Record AirLLM CPU (Qwen2) as a
  documented limitation** and proceed with the **HF `transformers` CPU pipeline** (proven in
  Stage 3D, ADR-0016) as the working measurement path. Keep `airllm_compat.py` as a tested,
  env-gated, off-by-default artifact of the investigation (not a working fix).
- **Evidence:** `docs/AIRLLM_PATCH_FEASIBILITY.md`,
  `results/stage4a_smoke_airllm_qwen2_0_5b_patched.json` (`patched=true`, `success=false`).
- **Consequences:** R-AIR-01 (AirLLM run) stays **PLANNED / not evidenced**. No Qwen2-7B download
  (the same AirLLM core CPU path would fail). Future AirLLM use would need a GPU environment or an
  alternate supported family — not attempted now.

## ADR-0018 — Revised experiment direction: Transformers CPU is the measurement path; AirLLM is a documented analysis
- **Status:** ACCEPTED (Stage 4B revision)
- **Context:** Stages 3–4A proved AirLLM CPU for Qwen2 is blocked by a core meta→CPU
  parameter-streaming defect (torch-ruled-out, rotary-ruled-out, minimal shim infeasible —
  ADR-0017). The project needs a coherent, honest path that still satisfies the assignment.
- **Decision (see `docs/EXPERIMENT_REVISION.md`):**
  1. **Do NOT download Qwen2-7B** under the current AirLLM CPU path (same defect would fail
     identically); `download_approved=false` retained.
  2. **Do NOT** patch AirLLM core / edit site-packages.
  3. **The Transformers CPU pipeline is the runnable measurement path** (Stage 3D proven) — real,
     repeatable CPU inference on the local Qwen2-0.5B, feeding the metrics schema/writer.
  4. **AirLLM is retained as an investigated local-memory-management method** with feasibility +
     failure analysis and structured evidence — a valid negative result, never claimed as success.
  5. **Optional future paths (documented only):** GPU/CUDA AirLLM env; an alternate AirLLM-supported
     family; an upstream AirLLM core streaming fix; Windows DirectML as a non-AirLLM extension.
- **Evidence:** `docs/EXPERIMENT_REVISION.md`, `docs/SMOKE_RUN.md`, `docs/AIRLLM_PATCH_FEASIBILITY.md`,
  the `results/stage3*`/`stage4a*` JSONs.
- **Consequences:** Stage 5 = measurement SDK (MetricsCollector/ResultWriter) + repeatable
  Transformers CPU measurement on Qwen2-0.5B, **not** a Qwen2-7B download. R-AIR-01 stays
  PLANNED/blocked. Supersedes the AirLLM-centric framing of ADR-0101a's main run; the model
  shortlist's 7B remains a *deferred* candidate (only if the AirLLM blocker is resolved).

## ADR-0019 — README is the final technical report; companion report + gap audit added (Stage 7A)
- **Status:** ACCEPTED (Stage 7A, docs only — no model run/download/benchmark)
- **Context:** The prior README was a Stage-4B planning placeholder ("not submission-ready"). The
  assignment requires the README to *be* the technical report, with tables, figures, reproduction,
  concept↔evidence links, and honest limitations. The measured evidence (Stage 5B/6A) and the
  AirLLM negative result are now committed and stable.
- **Decision:**
  1. Rewrite `README.md` as the **13-section submission-facing technical report**, embedding the
     committed measurement tables and the four generated figures, and linking all evidence.
  2. Add `reports/final_report.md` as an **extended companion** (AirLLM forensics, concept mapping,
     Research-Question answers) — **no new measurements**, cites committed data only.
  3. Add `docs/FINAL_GAP_AUDIT.md` — a satisfied/partial/blocked/missing requirement audit.
  4. Keep framing honest: **AirLLM blocked (not a success)**; Transformers CPU is the measured path;
     cost/energy is **assumption-based, not verified**; `Qwen2-7B` not downloaded/approved.
- **Evidence:** `README.md`, `reports/final_report.md`, `docs/FINAL_GAP_AUDIT.md`,
  `results/analysis/*`, `figures/*`.
- **Consequences:** R-README-01 / R-CONCEPT-01 / R-RQ-01 move to `PARTIALLY_EVIDENCED`. No
  experimental requirement is marked DONE; AirLLM (R-AIR-01) stays PLANNED/blocked. Final polish +
  end-to-end `SUBMISSION_CHECKLIST` run remain (Stage 7B).

---

## Deferred decisions (evidence required first)

These are intentionally **not** decided in Stage 0; deciding them now would mean guessing.

## ADR-0101 — Final Hugging Face model selection
- **Status:** SHORTLISTED (Stage 2B) → final pick still DEFERRED to download approval + Stage 3
- **Stage 2B update:** hardware is known and candidates are **metadata-verified** (no weights
  downloaded). The shortlist (`docs/MODEL_SELECTION.md`) recommends, for verification:
  tiny = `Qwen/Qwen2-0.5B` (~1.0 GB), main + direct baseline = `Qwen/Qwen2-7B` (~15.24 GB fp16,
  exceeds ~11.24 GiB RAM), all apache-2.0 and **ungated** (no token). Mistral-7B-Instruct-v0.2 is
  a deferred backup; Qwen2-72B a deferred stretch.
- **Not finalized because:** per ADR-0101a, the final pick needs download approval and a Stage 3
  runtime smoke check (no model is chosen blindly, no download yet).
- **Decision criteria (pre-committed):** parameter count vs RAM/VRAM, file format
  (SafeTensors/GGUF), on-disk size vs free space, AirLLM/quantization support, license/access.

## ADR-0101a — Model-selection strategy (Stage 2B)
- **Status:** ACCEPTED
- **Context:** A model must be chosen against the measured ~11.24 GiB / CPU-only / 933 GB profile
  without downloading weights blindly or storing tokens.
- **Decision:**
  1. Shortlist per role (tiny smoke / main AirLLM / direct baseline / optional DirectML / stretch)
     and verify each via **HF metadata only** (size, format, license, gated) — no weight download.
  2. Prefer **apache-2.0 + ungated** models (no token; honours the no-secrets policy); reject
     gated repos when an ungated equivalent exists.
  3. Main candidate must have fp16 weights **> ~11 GiB** (forces AirLLM) yet be CPU-feasible in
     budget → 7B class; 72B is a deferred stretch.
  4. The **direct baseline uses the same model** as the main AirLLM run for a fair comparison.
  5. **No download** until the pick is approved; finalize only after the Stage 3 smoke run.
- **Evidence:** `docs/MODEL_SELECTION.md`, `config/model_candidates.example.toml`; metadata probe
  (Qwen2 family + Mistral verified ungated/apache-2.0; native in transformers 4.44.2).
- **Consequences:** Stage 3 can proceed on the tiny model once approved; the final-model ADR is
  closed after that runtime check.

## ADR-0102 — Baseline path: Ollama vs Hugging Face `transformers`
- **Status:** DEFERRED → Stage 4
- **Why deferred:** Depends on hardware, model availability, and which path best exposes the
  out-of-memory behavior to document.

## ADR-0103 — Quantization levels to compare
- **Status:** DEFERRED → Stage 2/5
- **Why deferred:** Depends on the selected model's supported precisions and AirLLM support;
  intent is ≥2 levels (e.g., among FP16/Q8/Q4).

## ADR-0104 — External API provider & pricing baseline for cost analysis
- **Status:** DEFERRED → Stage 6
- **Why deferred:** Pricing must be current and dated at analysis time; provider chosen then
  and cited.

## ADR-0105 — Original extension (which one)
- **Status:** ACCEPTED (Stage 8B) — the delivered original extensions are **analytical**.
- **Decision:** The project's two original contributions are (1) the **AirLLM forensic failure
  analysis** with structured negative-result evidence (root-caused CPU meta-device blocker; the raw
  `results/stage3*`/`stage4a*` JSONs aggregated to `any_success=false`), and (2) the
  **assumption-based local-vs-API energy/cost break-even analysis** (`cost_model.py` + the break-even
  figure). Both are evidence-backed and clearly labelled; **neither is a measured AirLLM success.**
- **Candidates not pursued (would need a model run/quant/GPU):** quantization Pareto frontier ·
  LoRA/QLoRA mini-study · multi-model compare — out of scope under the AirLLM CPU blocker.

## ADR-0106 — Project license
- **Status:** SUPERSEDED by ADR-0107 (Stage 12A). *(Originally UNDECIDED at Stage 8B — no license
  invented, pending the author's explicit choice.)*
- **Decision (original):** The project license was **not explicitly declared**; a `LICENSE` file would
  be added only on an explicit choice by the author.
- **Why:** Coursework; declaring/choosing a license is the author's call. This has now been made — see
  ADR-0107.

## ADR-0107 — Stage 12A: license (MIT) + cost-v2/roofline methodology + 7B status
- **Status:** ACCEPTED (Stage 12A; docs/repo polish only — no model run, no download).
- **License — MIT.** A standard permissive **MIT `LICENSE`** (© 2026 Mohamed Awad) is added, covering
  the project's **own** source/tests/docs only — **not** model weights, datasets, or third-party
  dependencies (their own licenses; nothing redistributed). Supersedes ADR-0106's "undecided" stance.
  MIT chosen as the simplest, course-appropriate permissive default.
- **Cost model v2 (Stage 11A) — dated assumptions + allocated CAPEX.** `build_cost_model_v2` uses a
  **nonzero allocated CAPEX** ($900 × 25% usage = $225 → $4.6875/month) so the break-even is meaningful
  (≈47k req/month vs gpt-4o-mini, ≈13k vs gpt-4.1-mini); electricity-only break-even is 0. All
  prices/tariff/FX are **documented assumptions dated 2026-06-21**, recorded with `pricing_status`,
  **not guaranteed future pricing**. The v1 (`hardware_cost_usd=0`) estimate is retained for history.
- **Roofline output is qualitative.** `roofline_classification.json` / `final_roofline_classification.png`
  are a **Roofline-style qualitative classification anchored to measured evidence** — explicitly **not**
  a formal hardware roofline benchmark (no measured FLOP/byte arithmetic intensity).
- **7B remains a structured negative.** The large-model story stays the Stage 10B guarded
  memory-pressure **structured negative** (`memory_budget_exceeded`). A successful **GGUF-Q4 7B**
  generation is **out of scope** unless a future **Stage 12B** is explicitly approved (incl. model
  download) — preflight scoped in `docs/LARGE_MODEL_PREFLIGHT.md` §15. No 100-ready / 100%-complete
  claim is made.
