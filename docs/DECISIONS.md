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
- **Status:** ACCEPTED (design intent; implemented Stage 3+)
- **Context:** Guidelines §4–5 require all logic behind an SDK and all external API calls
  through a central gatekeeper (rate limit, retry, queue, logging).
- **Decision:** Adopt the layered design in `PLAN.md` §2; route every API call through
  `ApiGatekeeper`; keep CLI/analysis layers thin; OOP + DRY; files ≤150 lines.
- **Consequences:** Clear boundaries, testable units, no scattered API calls.

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

---

## Deferred decisions (evidence required first)

These are intentionally **not** decided in Stage 0; deciding them now would mean guessing.

## ADR-0101 — Final Hugging Face model selection
- **Status:** DEFERRED → Stage 2
- **Why deferred:** Requires the real hardware profile (`NEEDED_USER_INPUT`). The model must
  be deliberately larger than local memory yet feasible to finish via AirLLM.
- **Decision criteria (pre-committed):** parameter count vs RAM/VRAM, file format
  (SafeTensors/GGUF), on-disk size vs free space, AirLLM/quantization support, license/access.

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
- **Status:** DEFERRED → Stage 6
- **Candidates:** bottleneck-shift map · quantization Pareto frontier · AirLLM decision
  matrix · API-vs-local break-even simulator · LoRA/QLoRA mini-study · multi-model compare.

## ADR-0106 — Project license
- **Status:** DEFERRED → before any public push (Stage 7)
- **Why deferred:** Coursework; license declared once the user confirms distribution intent.
