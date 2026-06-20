# Prompt Engineering Log

> **STATUS: STAGE 0.** Per guidelines §8.3, this log records significant prompts used to
> drive the project with AI agents: the intent, the context, the outcome, and any
> iterations. It documents *how* the work was orchestrated, not just *what* was produced.
> Secrets, tokens, and personal data are never recorded here.

---

## Index

| # | Stage | Title | Outcome |
| --- | --- | --- | --- |
| 001 | 0 | Stage 0 — Requirements, planning & repository foundation | 13 documentation files + scaffold created |
| 002 | 1A | Stage 1A — Hardware intake & planning calibration | `HARDWARE.md` created; audit/PRD/PLAN/RISKS/DECISIONS/TODO/README calibrated to measured hardware |
| 003 | 1B | Stage 1B — Host hardware verification | Host-side CIM evidence added; host/WSL/experiment boundary documented; audit GPU/VRAM kept PARTIALLY_EVIDENCED; ADR-0009 added |
| 004 | 1C-A | Stage 1C-A — GPU feasibility diagnostics | `GPU_FEASIBILITY.md` created; backend paths assessed; R-NOGPU re-opened; ADR-0010 (defer backend) added |
| 005 | 1C-B | Stage 1C-B — Isolated DirectML compatibility probe | Throwaway Windows venv probe: torch-directml installs but import fails (Py3.9<3.10; no 3.13 wheel) → all GPU backends BLOCKED on current toolchain; CPU/AirLLM confirmed as practical path |
| 006 | 1C-C | Stage 1C-C — DirectML retest with compatible Python | No Python 3.10–3.12 installed; winget could add 3.11.9 but persistent host change stopped-and-reported (user-gated); DirectML stays BLOCKED; CPU/AirLLM remains main path |
| 007 | 1C-D | Stage 1C-D — DirectML retest (user-authorized Python 3.11) | Python 3.11.9 installed (user-scope); DirectML matmul SUCCEEDS on Radeon 890M; transformers imports (no model); GPU = verified optional baseline/extension; CPU/AirLLM stays main path |
| 008 | 1D | Stage 1D — AirLLM CPU feasibility check | airllm 2.11.0 installs+imports on CPU with a pinned matrix (transformers 4.44.2/optimum 1.23.3/sentencepiece/torch-cpu); `device='cpu'` first-class; CPU path EVIDENCED; `AIRLLM_FEASIBILITY.md` + R-AIRLLM-DEPS + ADR-0011 |
| 009 | 2A | Stage 2A — Project dependency skeleton & measurement design | Created `pyproject.toml`+`uv.lock` (pinned matrix, CPU torch), `src/ex05_airllm` skeleton + version test, `MEASUREMENT_DESIGN.md`, `config/experiment.example.toml`; gates green (uv sync, 4 tests @100%, ruff, ≤150 lines); ADR-0012 |
| 010 | 2B | Stage 2B — Model shortlist & selection matrix | Metadata-verified shortlist (no downloads): tiny Qwen2-0.5B, main Qwen2-7B (15.24 GB > 11 GiB), apache-2.0/ungated; `MODEL_SELECTION.md`, `PRD_measurement.md`, `PRD_airllm_pipeline.md`, candidate config; ADR-0101a; final pick deferred to approval |
| 011 | 3A | Stage 3A — Tiny AirLLM CPU smoke probe | Ran `smoke_airllm.py` on Qwen2-0.5B (approved); **FAILED honestly** — AirLLM needs sharded safetensors+index (single-file model); `SMOKE_RUN.md` + R-AIRLLM-SHARD + ADR-0014; no 7B download, no benchmark, no fake results |
| 012 | 3B | Stage 3B — Re-sharded tiny AirLLM CPU smoke | Re-shard + untie (download Qwen2-0.5B only) **fixed the format** → AirLLM loads & starts inference, but CPU forward pass **FAILED** with meta-device error (R-AIRLLM-META); ADR-0015 corrective (older torch) proposed; weights ignored; no 7B, no benchmark, no fake results |
| 013 | 3C | Stage 3C — Torch-pin retest (torch 2.4.1) | Pinned `torch==2.4.1+cpu`, reran smoke on existing re-sharded model → **identical** meta-device error → **torch ruled out**. Root cause: AirLLM leaves Qwen2 `rotary_emb` on `meta`. Kept torch 2.4.1; recommend Stage 3D HF CPU fallback (ADR-0016). No new download, no benchmark, no fake results |
| 014 | 3D | Stage 3D — Transformers CPU fallback smoke | Direct HF `transformers` CPU smoke on cached Qwen2-0.5B (offline) **SUCCEEDED** (coherent 16-token output) → measurement pipeline proven (R-REPRO partial; ADR-0016 EVIDENCED). NOT AirLLM, NOT a benchmark; AirLLM CPU stays blocked. No new download, no 7B, no fake results |
| 015 | 4A | Stage 4A — AirLLM Qwen2 CPU patch feasibility | Implemented + tested a local fail-closed rotary shim (`airllm_compat.py`, no site-packages edit); patched smoke **still FAILED**; diagnostic disproved rotary → meta culprit is a layer param (RMSNorm `weight`) in AirLLM's core CPU streaming. Minimal shim **infeasible** → ADR-0017 (documented limitation + HF baseline). No new download, no 7B, no benchmark, no fake results |
| 016 | 4B | Stage 4B — Formal experiment direction revision | `EXPERIMENT_REVISION.md` + ADR-0018: HF `transformers` CPU is the runnable measurement path; AirLLM kept as documented failure analysis; Qwen2-7B deferred (`download_approved=false`). Stage 5 = measurement SDK + repeatable Transformers CPU run. Added R-GRADE-AIRLLM. Docs-only; no model run, no download, no benchmark, no fake results |
| 017 | 5A | Stage 5A — Measurement SDK & result schema | Implemented `result_schema`/`metrics`/`result_writer`/`prompts`/`env` (TDD, ≤150 lines); 38 tests ~97% cov, ruff/format clean. Optional metrics None, success False (no fake values). No inference, no download, no benchmark, no fake results |
| 018 | 5B | Stage 5B — Repeatable Transformers CPU measurement runner | `run_transformers_cpu_measurement.py` + tests; ran **6/6** HF CPU runs on cached Qwen2-0.5B (offline) → JSON + summary.csv; runtime ~5.3–6.4 s, ~4.5–5.3 tok/s, peak RAM ~4.0 GB; TTFT None / TPOT approx documented. `MEASUREMENT_RUNS.md`; audit PARTIALLY_EVIDENCED. No AirLLM, no 7B, no benchmark, no fake results |
| 019 | 6A | Stage 6A — Analysis, figures & cost/energy estimate | `analyze_measurements.py`+`analysis_stats.py`+`cost_model.py` (TDD); computed stats/per-prompt from committed `summary.csv`, AirLLM negative-result aggregation (`any_success=false`), assumption-based cost/energy, 4 matplotlib figures; `ANALYSIS.md`. From committed data only — no model run, no download, no benchmark, no fake results; raw data unmodified |

---

## Prompt 001 — Stage 0: Requirements, planning & repository foundation

- **Stage:** 0
- **Date:** 2026-06-19
- **Intent:** Establish the project's documented foundation *before any implementation* —
  requirements, traceability, planning, risks, decisions, AI workflow, prompt log, quality
  gates, cost methodology, submission checklist, `.gitignore`, and a Stage-0 README —
  targeting a strict-grader, self-assessment-100 submission.
- **Context given to the agent:** Brand-new repo for Assignment 05 (AirLLM); course focus on
  Vibe Coding / agentic SE / professional documentation; course assignment materials
  available locally; strict constraints (no implementation code, no model downloads, no final
  model choice, no fake results/specs/graphs, no secrets, no commit/push, no `git add .`);
  missing info must be marked `NEEDED_USER_INPUT`.
- **Key constraints encoded into the work:**
  - Documentation-only; create only the allowed doc/scaffold files.
  - Requirements audit with statuses `PLANNED` / `NEEDED_USER_INPUT` / `N/A_WITH_RATIONALE`.
  - Explicit `NEEDED_USER_INPUT`: OS, CPU, RAM, GPU, VRAM, disk type & free space, group
    code, GitHub repo URL, Hugging Face access (without storing a token).
  - PLAN stages 0–7 as specified; RISKS must include the eight named risks.
  - README must state: Stage 0 only, no results yet, not submission-ready, next input =
    hardware specs.
  - No forbidden placeholder phrases ("will contain", "coming soon", "lorem", "placeholder",
    "fake result", "TODO later").

- **Verbatim prompt:**

> In this environment you have access to a set of tools you can use to answer the user's
> question. [...] **Important course requirements:** Do not write implementation code yet.
> Do not download models yet. Do not choose a final model yet. Do not claim results we do
> not have. Start with requirements, planning, traceability, risks, and documentation. The
> project must later include PRD, PLAN, TODO, AI workflow, prompts, decisions, quality,
> costs, results, figures, and a strong README. Use uv later as the package manager [...].
> No secrets. [...] No placeholders like "will contain", "TODO later", "coming soon", or
> empty skeleton reports. If information is missing, mark it explicitly as
> NEEDED_USER_INPUT, not DONE.
>
> **Your task in this Stage 0:** Create only documentation and repository planning files.
> Do not implement experiment code. *(Allowed edits: README.md; docs/REQUIREMENTS_AUDIT.md;
> docs/PRD.md (Stage 0 draft); docs/PLAN.md; docs/TODO.md; docs/AI_WORKFLOW.md;
> docs/PROMPTS.md with this prompt as Prompt 001; docs/DECISIONS.md; docs/RISKS.md;
> docs/SUBMISSION_CHECKLIST.md; docs/QUALITY.md (planned gates only); docs/COSTS.md (planned
> methodology only); directories docs/ reports/ results/ figures/ experiments/ src/ tests/
> config/; a Python/uv-oriented .gitignore.)* Forbidden: implementation code, fake
> results/graphs/specs, model downloads, dependency installs, tokens, commit, push,
> `git add .`, marking requirements DONE without evidence.
>
> *Required content:* (1) REQUIREMENTS_AUDIT.md table `requirement_id | requirement |
> source | status | evidence_path | risk | notes` using statuses PLANNED /
> NEEDED_USER_INPUT / N/A_WITH_RATIONALE. (2) Explicit missing user inputs: OS, CPU, RAM,
> GPU, VRAM, disk type & free space, group code, GitHub repo URL, HF access without storing
> a token. (3) PLAN.md stages 0–7 (0 requirements; 1 PRD/PLAN/TODO approval; 2 measurement
> architecture; 3 small pipeline proof; 4 baseline; 5 AirLLM+quantization; 6
> analysis/graphs/costs; 7 final audit/submission). (4) RISKS.md: model too large, AirLLM
> compatibility, Python/PyTorch/CUDA mismatch, disk space, I/O bottleneck, secrets
> exposure, fake/non-reproducible measurements, overclaim. (5) README.md must make clear:
> Stage 0 documentation only; no results yet; repo not submission-ready; next required
> input is hardware specs.
>
> *Validation:* `find . -maxdepth 3 -type f | sort`; `grep -RniE "will contain|coming
> soon|lorem|placeholder|fake result|TODO later" README.md docs .gitignore || true`;
> `git status --short`.
>
> *(Full prompt retained in the conversation transcript; condensed here for readability.)*

- **Agent actions taken:**
  1. Read the assignment brief and the course software guidelines to ground all docs in
     the real requirements.
  2. Created directory scaffold: `docs/ reports/ results/ figures/ experiments/ src/ tests/
     config/`.
  3. Authored `.gitignore`, `README.md`, and the eleven `docs/*.md` files with real content
     (no placeholders).
  4. Ran the validation commands.

- **Outcome:** Stage 0 deliverables produced; requirements audit lists every requirement
  and all `NEEDED_USER_INPUT`; no code, no results, no secrets, no commit/push.
- **Iterations / corrections:** *(none in Stage 0 — to be appended if the user requests
  revisions.)*
- **Lessons / notes for next prompts:** The next prompt (Stage 1) must supply the real
  hardware specs so model selection (Stage 2) can proceed; keep enforcing the evidence-bound
  and no-fabrication guardrails from `AI_WORKFLOW.md`.

---

## Prompt 002 — Stage 1A: Hardware intake & planning calibration

- **Stage:** 1A
- **Date:** 2026-06-19
- **Intent:** Collect *real* machine hardware facts from the Ubuntu/WSL2 terminal, create a
  hardware evidence document, and calibrate the Stage 0 docs so the project can move toward
  model selection **without inventing anything**. Still before implementation.
- **Context:** Stage 0 committed & pushed (`5311838`); `main` tracks
  `origin/main`; local reference course files are kept out of the repo via a local-only git
  exclude. Real hardware evidence is required before selecting a model or writing code.
- **Key constraints encoded:** documentation-only; no implementation code, no deps, no
  `pyproject.toml` yet, no model download, **no final model selection**, no AirLLM/Ollama
  run, no fake results/specs, **measure rather than estimate** hardware, no secrets, don't
  touch the local reference course files, no commit/push, no `git add .`. Hardware audit items move to
  `PARTIALLY_EVIDENCED` only where terminal evidence exists; experimental requirements must
  **not** be marked DONE.
- **Verbatim prompt (condensed; full text retained in the conversation transcript):**

  > **Stage 1A — Hardware Intake and Planning Calibration.** Goal: collect real machine
  > hardware facts from the Ubuntu terminal, create a hardware evidence document, and update
  > Stage 0 docs so the project can move toward model selection without inventing anything.
  > *Allowed edits:* create `docs/HARDWARE.md`; update `REQUIREMENTS_AUDIT.md` (hardware
  > items `NEEDED_USER_INPUT` → `PARTIALLY_EVIDENCED` only where terminal evidence exists; do
  > not mark model-selection/benchmark/AirLLM/quantization DONE); update `PRD.md`/`PLAN.md`
  > for actual CPU/GPU/disk constraints; update `RISKS.md` for new hardware risks; update
  > `TODO.md` (mark Stage 1A docs complete after files updated); update `DECISIONS.md` for
  > evidence-backed decisions; update `README.md` to point to `HARDWARE.md` and keep status
  > honest; add this prompt to `PROMPTS.md`. *Forbidden:* implementation code, deps,
  > `pyproject.toml`, model downloads, final model choice, running AirLLM/Ollama, fake
  > results, manual hardware estimation when a command can measure it, secrets, touching the
  > local reference course files, commit, push, `git add .`. *Run discovery commands* (`uname -a`,
  > `lsb_release`/`os-release`, `lscpu`, `free -h`, `df -h .`, `lsblk`, `findmnt`, `lspci`,
  > `nvidia-smi`, `rocm-smi`, `python3 --version`, `which uv`, `uv --version`) and include
  > relevant outputs in `HARDWARE.md`. *HARDWARE.md structure & required GPU/disk honesty
  > rules specified* (don't claim "no GPU" unless `lspci` supports it; note SSD/NVMe
  > uncertainty). *Remaining user values:* group code, repo URL, HF access, electricity
  > tariff, hardware cost.

- **Agent actions taken:**
  1. Ran all read-only discovery commands; added `glxinfo`, `/dev/dxg`, `/proc/driver/nvidia`,
     and `/proc/meminfo` probes for evidence-based GPU/RAM detection.
  2. Created `docs/HARDWARE.md` with quoted outputs, an honest GPU conclusion (no compute GPU
     detected; `lspci` unavailable so no absolute "no GPU" claim), and model-selection impact.
  3. Updated `REQUIREMENTS_AUDIT.md` (added `PARTIALLY_EVIDENCED`; R-HW-01 + §C statuses),
     `PRD.md` (constraints C1/C1a/C1b/C3), `PLAN.md` (§0 calibrated constraints + trade-offs),
     `RISKS.md` (R-NOGPU/WSL-MEM/QUANT-CPU/WSL-DISK/EVID-GAP), `DECISIONS.md` (ADR-0007/0008),
     `TODO.md` (Stage 1A tasks DONE), and `README.md` (banner, status, hardware section).
- **Outcome:** Hardware evidence captured; planning calibrated to ~11.24 GiB RAM / CPU-only /
  933 GB disk; no model selected; no experimental requirement marked DONE; no code/deps/runs;
  local reference course files untouched and still ignored.
- **Iterations / corrections:** *(none.)*
- **Lessons / notes for next prompts:** Stage 2 must resolve the **CPU quantization route**
  (R-QUANT-CPU: `bitsandbytes` needs CUDA → likely GGUF Q4/Q8) and formally set the VRAM
  metric to `N/A_WITH_RATIONALE`; still awaiting group code, HF-access confirmation, and cost
  assumptions from the user.

---

## Prompt 003 — Stage 1B: Host hardware verification

- **Stage:** 1B
- **Date:** 2026-06-19
- **Intent:** Collect **host-side Windows** hardware evidence from WSL (via PowerShell/CIM)
  and update the docs to clearly distinguish (1) the **physical Windows host**, (2) the
  **Ubuntu WSL2 execution environment**, and (3) the **resources actually available to the
  experiment** — so model selection is calibrated to the real execution budget, not the
  larger host specs. Still before implementation; nothing committed.
- **Context:** Stage 1A captured WSL-side facts only; host vs execution resources needed
  disambiguation before any model decision. WSL2 RAM cap (~11 GiB) and the host's true GPU
  and disk type were the key unknowns.
- **Key constraints encoded:** documentation-only; run only the listed read-only
  PowerShell/CIM + `wsl --status` + `nvidia-smi.exe` probes; record failures honestly; **do
  not** store serial numbers; GPU/VRAM must stay `PARTIALLY_EVIDENCED` unless compute is
  evidenced *inside* WSL2; no benchmark/model/AirLLM/quantization/cost/final-report
  requirement marked DONE; no code, no `pyproject.toml`, no deps, no model download, no
  AirLLM/Ollama, no final model selection, no inventing facts, don't touch local reference
  course files, no staging/commit/push, no `git add .`.
- **Verbatim prompt (condensed; full text retained in the conversation transcript):**

  > **Stage 1B — Host Hardware Verification.** Goal: collect host-side Windows hardware
  > evidence from WSL using PowerShell, then update `docs/HARDWARE.md` and related docs to
  > distinguish physical host hardware, the Ubuntu WSL2 execution environment, and resources
  > actually available to the experiment. *Allowed commands* (run from WSL, record failures
  > honestly): `Get-CimInstance Win32_OperatingSystem|Win32_Processor|Win32_ComputerSystem|
  > Win32_VideoController|Win32_DiskDrive`, `Get-PhysicalDisk`, `wsl.exe --status`,
  > `nvidia-smi.exe || true`. *Required doc changes:* HARDWARE.md sections (Evidence
  > boundary; Physical Windows host evidence; Ubuntu WSL2 execution environment evidence;
  > Experiment resource availability; Consequences for model selection); if a host GPU
  > exists, state it exists on the host but do not claim it's available to the experiment
  > unless CUDA/ROCm/nvidia-smi works inside Ubuntu — if only Windows display evidence,
  > write "Host GPU is detected by Windows, but CUDA/ROCm compute availability inside Ubuntu
  > WSL2 is not evidenced"; if host disk type is discoverable, state it host-side and keep
  > the WSL filesystem evidence separate, without overclaiming I/O before benchmarks. Update
  > REQUIREMENTS_AUDIT (hardware may become PARTIALLY_EVIDENCED or EVIDENCED; GPU/VRAM stay
  > PARTIALLY_EVIDENCED if unavailable in WSL2; no benchmark/model/AirLLM/quant/cost/report
  > DONE), RISKS (keep host-vs-execution mismatch; add host-GPU-unavailable constraint),
  > DECISIONS (model selection based on execution-environment resources, not just host),
  > TODO (Stage 1B doc tasks only), PROMPTS (this prompt). *Forbidden:* code, pyproject,
  > deps, models, AirLLM, Ollama, final model, inventing facts, storing serial numbers,
  > touching local reference files, staging, commit, push, `git add .`.

- **Host-side facts collected (CIM):** Windows 11 Pro 26200; ASUS Vivobook S 14 (M5406WA);
  Ryzen AI 9 HX 370 (12c/24t, ~2.0 GHz base); ≈ 24 GB host RAM; AMD Radeon 890M iGPU
  (driver 32.0.13022.3006), **no NVIDIA** (`nvidia-smi.exe` absent); ~1 TB **NVMe SSD**
  (`Get-PhysicalDisk` MediaType SSD / BusType NVMe); `wsl --status` → Ubuntu, Version 2.
- **Outcome:** `HARDWARE.md` now has §0 boundary, §A host, WSL §1–§6, §B experiment
  availability, §7 consequences; audit §C uses host/experiment columns with GPU/VRAM kept
  `PARTIALLY_EVIDENCED`; RISKS reconciled; ADR-0009 added; TODO Stage 1B tasks DONE; README
  updated. **No model selected; no experimental requirement DONE; no serial numbers stored;
  no code/deps/runs/commit/push.**
- **Iterations / corrections:** *(none.)*
- **Lessons / notes for next prompts:** The binding budget for Stage 2 model selection is the
  **execution environment** (~11 GiB RAM, CPU-only, NVMe-backed disk), per ADR-0009. NVMe is
  favorable but I/O speed remains a Stage 4/5 measurement, not a claim.

---

## Prompt 004 — Stage 1C-A: GPU feasibility diagnostics

- **Stage:** 1C-A
- **Date:** 2026-06-19
- **Intent:** Investigate (diagnostically only) whether the physical AMD Radeon 890M iGPU
  can realistically drive the project stack (PyTorch / Transformers-style inference / AirLLM
  / quantization) — **without** installing anything, changing the environment, selecting a
  model, or making a final backend decision. Core principle: distinguish (1) GPU exists
  physically, (2) GPU compute backend availability in WSL/Windows, (3) backend↔library
  compatibility, and (4) if GPU isn't selected, justify it from feasibility evidence rather
  than by treating the machine as GPU-less.
- **Context:** Stage 1A/1B established the host has an AMD Radeon 890M iGPU; this stage must
  neither ignore it nor assume it is usable until feasibility is checked. No commits.
- **Key constraints encoded:** read-only diagnostics only; **no** package installs, `pip
  install`, `uv add`/`uv sync`, `pyproject.toml`, implementation code, model downloads,
  AirLLM/Ollama runs, benchmarks, final model selection, or final backend decision unless
  evidence is conclusive; don't touch local reference course files; no staging/commit/push;
  no `git add .`.
- **Verbatim prompt (condensed; full text retained in the conversation transcript):**

  > **Stage 1C-A — GPU Feasibility Diagnostics Only.** Investigate whether the AMD Radeon
  > 890M iGPU can realistically be used for the stack (PyTorch, Transformers-style inference,
  > AirLLM if compatible, quantization). Diagnostic only — install nothing, change nothing,
  > select no model, no commit. *Allowed read-only commands* — host: `Get-CimInstance
  > Win32_VideoController`; `Get-CimInstance Win32_PnPSignedDriver` (DISPLAY); `dxdiag /t`
  > then grep Card name/Display/Dedicated/Shared Memory/Driver Version/Feature Levels;
  > `Get-Command python`/`py`. WSL: `uname -a`; os-release; `ls /dev/dxg`; `lspci | grep`
  > GPU; `nvidia-smi`; `rocminfo`; `rocm-smi`; `python3 --version`; a `torch` import probe;
  > optional `pip show torch-directml|torch|transformers|airllm`. *Allowed edits:* create
  > `docs/GPU_FEASIBILITY.md` (Status; Physical GPU evidence; WSL GPU visibility; Candidate
  > backend paths as PLANNED/POSSIBLE/BLOCKED/NEEDS_INSTALL_CHECK — WSL+DirectML, Windows
  > DirectML, ROCm-WSL, ROCm-native, CPU+AirLLM; Compatibility questions; Preliminary
  > interpretation that does not decide yet); update HARDWARE.md to reference feasibility;
  > update RISKS/DECISIONS only if evidence-backed; update TODO with Stage 1C diagnostic
  > tasks (don't close experimental tasks); add this prompt to PROMPTS. *Forbidden:* installs,
  > pip/uv, pyproject, code, models, AirLLM/Ollama, benchmarks, final model, premature
  > backend decision, staging, commit, push, touching local reference files, `git add .`.

- **Host GPU facts collected:** AMD Radeon 890M (driver 32.0.13022.3006, AMD); dxdiag →
  Display Memory 12127 MB / **Dedicated 290 MB / Shared 11836 MB**, **DirectX 12_2** feature
  level; Windows-native Python 3.13 present.
- **WSL GPU visibility:** `/dev/dxg` present; `lspci` unavailable; `nvidia-smi`/`rocminfo`/
  `rocm-smi` absent; `python3` 3.12.3; **`torch` not installed** (CUDA check couldn't run);
  `torch-directml`/`torch`/`transformers`/`airllm` all **not installed**.
- **Backend path verdicts:** WSL+DirectML `NEEDS_INSTALL_CHECK` (leaning BLOCKED); Windows
  DirectML `POSSIBLE`/`NEEDS_INSTALL_CHECK`; ROCm-WSL `BLOCKED`; ROCm-native `BLOCKED` (this
  setup); CPU+AirLLM `POSSIBLE` (strongest current evidence).
- **Outcome:** `GPU_FEASIBILITY.md` created; HARDWARE §4 links to it; R-NOGPU re-opened as
  not-yet-closed; ADR-0010 defers the backend decision pending the §5 compatibility checks;
  TODO Stage 1C-A diagnostic tasks DONE with T1C.6/T1C.7 open. **No installs, no code, no
  models, no benchmarks, no backend/model decision, no commit/push.**
- **Iterations / corrections:** dxdiag needed a longer poll for its output file; re-ran with
  a wait loop and obtained the memory/feature-level data.
- **Lessons / notes for next prompts:** Before any backend ADR, resolve §5 (AirLLM CPU mode?
  AirLLM/DirectML? torch-directml coverage? quantization route?). Remember the iGPU memory is
  **shared system RAM**, so a GPU path would not enlarge the AirLLM memory budget.

---

## Prompt 005 — Stage 1C-B: Isolated DirectML compatibility check

- **Stage:** 1C-B
- **Date:** 2026-06-19
- **Intent:** Run a minimal, **isolated** compatibility check to decide whether the AMD Radeon
  890M can realistically be used via **Windows-native DirectML** for this stack — using a
  throwaway Windows venv **outside** the repo, without modifying project code/deps and without
  committing. Feasibility test only, not the final experiment.
- **Context:** 1C-A left Windows-native DirectML as `POSSIBLE/NEEDS_INSTALL_CHECK`; this stage
  actually attempts the install + import + device + tiny matmul to resolve it with evidence.
- **Key constraints encoded:** throwaway Windows-side venv outside Git; install only minimal
  DirectML packages there; tiny smoke test (import torch / import torch_directml / make device
  / move tensor / matmul); only if DirectML imports, optionally test a `transformers` import
  with **no model download**; do **not** install AirLLM (mark its DirectML compat UNKNOWN); no
  project deps/`pyproject.toml`/code changes, no model download, no AirLLM/Ollama, no
  benchmark, no final model, no final backend decision unless conclusive; don't touch local
  course materials; no staging/commit/push; no `git add .`.
- **Verbatim prompt (condensed; full text retained in the conversation transcript):**

  > **Stage 1C-B — Isolated GPU Backend Compatibility Check.** Run a minimal isolated check to
  > decide whether the Radeon 890M can be used via Windows-native DirectML, without modifying
  > project code or committing. Prefer a throwaway Windows venv outside the repo; don't install
  > into the project env; no `pyproject.toml`; no model downloads; no AirLLM/benchmarks; don't
  > finalize the backend unless conclusive. *Actions:* check Windows Python (`py -0p`,
  > `python --version`); make a temp dir under `%TEMP%\ex05_directml_probe`; create a throwaway
  > venv on a torch-directml-compatible Python; install minimal packages (`torch-directml`,
  > `torch` if needed; **no** `transformers` unless DirectML import succeeds); run a tiny
  > DirectML smoke test (import torch, import torch_directml, create device, move a small
  > tensor, tiny matmul, print device/shape/success); if it succeeds, optionally install
  > `transformers` and do an import-level check **without** downloading a model; do **not**
  > install AirLLM (mark its DirectML compat UNKNOWN). *Edits:* update `GPU_FEASIBILITY.md`
  > (add "Stage 1C-B DirectML compatibility probe"; record Python versions, env creation,
  > packages attempted & install result, torch_directml import, device creation, tensor op,
  > transformers test, model-download avoidance; update backend statuses with
  > POSSIBLE/BLOCKED/NEEDS_FURTHER_CHECK; add interpretation; keep final decision deferred
  > unless conclusive), and `HARDWARE/RISKS/DECISIONS/TODO/PROMPTS` as needed. *Forbidden:*
  > project code, src files, `pyproject.toml`, project dep changes, installs into the repo env,
  > model downloads, AirLLM, Ollama, benchmarks, final model, staging, commit, push, touching
  > local course materials, `git add .`.

- **Results:**
  - **Windows Pythons:** 3.13.2 (default) and 3.9 (VS-shared).
  - **Throwaway venv:** created with Python 3.9 in `%TEMP%\ex05_directml_probe` (outside Git);
    removed at the end.
  - **Install:** `torch-directml 0.2.5.dev240914` + `torch 2.4.1+cpu` installed successfully.
  - **`import torch`:** OK. **`import torch_directml`:** **FAILED** —
    `TypeError: 'staticmethod' object is not callable` (root cause: package needs Python
    3.10+; 3.9 can't call a bare staticmethod used as a default arg at import). Retried with
    `torch-directml 0.2.4.dev240913` → **same failure**.
  - **Device / tensor matmul:** not reached (import failed).
  - **`transformers`:** not tested (gated on DirectML success). **Model download:** none.
  - **Cleanup:** throwaway env deleted; WSL project env re-verified to have no torch.
- **Outcome:** Windows-native DirectML → **`BLOCKED` on the available toolchain** (re-openable
  only via a Python 3.10–3.12 install); all GPU backends now blocked → **CPU + AirLLM** is the
  practical path. `GPU_FEASIBILITY.md` §3b/§4/§5/§6 updated; HARDWARE/RISKS/DECISIONS/TODO
  updated; final backend ADR still deferred pending §5 (AirLLM CPU mode). **No project deps
  changed, no project code, no model download, no AirLLM/Ollama, no benchmark, no commit/push.**
- **Iterations / corrections:** dxdiag-style waits not needed here; needed a second
  torch-directml version to confirm the import failure was version-independent on Python 3.9.
- **Lessons / notes for next prompts:** The GPU path is closed *by toolchain*, not hardware —
  state it that way. Next, resolve AirLLM CPU-mode feasibility (T1C.6) to finalize the backend
  ADR; the iGPU's shared memory means even a working GPU path wouldn't enlarge the AirLLM
  memory budget.

---

## Prompt 006 — Stage 1C-C: DirectML retest with compatible Python

- **Stage:** 1C-C
- **Date:** 2026-06-19
- **Intent:** Determine whether the Radeon 890M can run a tiny PyTorch DirectML op using a
  **compatible Windows Python (3.10–3.12)**, without modifying the project environment. Still
  a feasibility test, not implementation. No commit.
- **Context:** 1C-B failed because the only present Windows Pythons (3.9, 3.13) can't run
  `torch-directml`. This stage checks for / safely obtains a compatible interpreter, then
  retests — but only if the install route is clearly standard and user-safe.
- **Key constraints encoded:** check `py -0p` for 3.10–3.12; if absent, check `winget`
  availability + `Python.Python.3.11`; **do not install Python automatically** unless clearly
  standard and user-safe — if it needs admin rights / unclear prompts / Store ambiguity /
  unclean global changes, **stop and report**; if a compatible Python exists (or a safe,
  explicitly-confirmed install completes), make a throwaway venv outside the repo, install only
  `torch-directml`, run the tiny smoke test; install `transformers` only if DirectML succeeds;
  no model download; clean up the venv; no project deps/`pyproject.toml`/code, no AirLLM/Ollama,
  no benchmark, no final model, no final backend decision unless conclusive; don't touch local
  course materials; no staging/commit/push; no `git add .`.
- **Verbatim prompt (condensed; full text retained in the conversation transcript):**

  > **Stage 1C-C — DirectML Retest with Compatible Python.** Determine whether the Radeon 890M
  > can run a tiny PyTorch DirectML op using a compatible Windows Python, without modifying the
  > project env. (1) `py -0p` to check for 3.10–3.12. (2) If none, check `winget --version` and
  > `winget search Python.Python.3.11`. (3) Do **not** install Python automatically unless the
  > route is clearly standard and user-safe; if it needs admin/unclear prompts/Store
  > ambiguity/unclean global changes, **stop and report**. (4) If a compatible Python exists (or
  > a safe confirmed install completed): throwaway venv outside the repo, install only
  > `torch-directml` (let pip resolve torch), run the tiny smoke test (import torch / import
  > torch_directml / device() / two 64×64 tensors / matmul / print device,shape,dtype,success).
  > (5) `transformers` only if DirectML succeeds; (6) no model download; (7) clean up the venv.
  > *Edits:* `GPU_FEASIBILITY.md` add "Stage 1C-C compatible-Python DirectML retest" recording
  > Python availability/install, torch-directml install, import, device, matmul, transformers
  > test, model-download avoidance, and updated backend status; plus
  > `HARDWARE/RISKS/DECISIONS/TODO/PROMPTS` as needed. *Forbidden:* project dep changes,
  > `pyproject.toml`, installs in the repo, code, model downloads, AirLLM, Ollama, benchmarks,
  > final model, premature final backend decision, staging, commit, push, touching local course
  > materials, `git add`.

- **Results:**
  - **Compatible Python (3.10–3.12):** **not installed** (`py -0p` → only 3.13 + 3.9).
  - **Install route:** `winget` v1.28.240 present; `winget search` lists `Python.Python.3.11`
    **3.11.9** (winget source).
  - **Decision:** **Stopped and reported** — installing a Python runtime is a persistent,
    global change to the user's personal host (and may raise a UAC prompt unanswerable from
    this non-interactive flow), which the stage's rule says to defer. Python was **not**
    installed; the DirectML retest was **not** executed.
  - **transformers:** not tested. **Model download:** none.
- **Outcome:** Windows-native DirectML stays **`BLOCKED` under the current practical setup**;
  completing the retest is a **user-gated** step (install Python 3.10–3.12, e.g. `winget
  install Python.Python.3.11`). CPU + AirLLM remains the dependable main path.
  `GPU_FEASIBILITY.md` §1/§3c/§4/§6 updated; HARDWARE/RISKS/DECISIONS/TODO updated. **No
  project deps changed, no code, no model download, no AirLLM/Ollama, no benchmark, no commit.**
- **Iterations / corrections:** first `winget search` rendered only a progress spinner; re-ran
  with `--disable-interactivity`/`--accept-source-agreements` and `$ProgressPreference` to get
  clean output.
- **Lessons / notes for next prompts:** GPU/DirectML is closed *only by a missing, user-gated
  Python runtime* — not by hardware. If the user wants the GPU baseline explored, authorize a
  Python 3.10–3.12 install and re-run the 1C-C smoke test; otherwise proceed with CPU/AirLLM
  and resolve AirLLM CPU-mode feasibility (T1C.6) to finalize the backend ADR.

---

## Prompt 007 — Stage 1C-D: DirectML retest with user-authorized Python 3.11

- **Stage:** 1C-D
- **Date:** 2026-06-19
- **Intent:** With the user's explicit authorization, install Python 3.11 by the safest
  user-scope/non-invasive route and run the tiny DirectML smoke test to determine whether the
  Radeon 890M can actually run a PyTorch DirectML op — without modifying the project env.
- **Context:** 1C-C stopped-and-reported because no compatible Python was installed and a host
  install is a user decision. The user authorized the install (user-scope, no unclear admin).
- **Key constraints encoded:** don't modify the project env; no `pyproject.toml`; no installs
  in the repo; throwaway Windows venv outside the repo; install only `torch-directml` (+
  resolved deps); run only the tiny smoke test (import torch / import torch_directml / device /
  64×64 matmul); if it succeeds, optionally `import transformers` **without** downloading a
  model; delete the throwaway venv after recording; update only
  `GPU_FEASIBILITY/RISKS/DECISIONS/TODO/PROMPTS` as needed; no final model; no AirLLM/Ollama;
  no benchmark; no stage/commit/push.
- **Verbatim prompt (condensed; full text retained in the conversation transcript):**

  > **Proceed with Stage 1C-D.** I authorize installing Python 3.11 using the safest
  > user-scope/non-invasive route via winget or the official launcher flow, only if it does
  > not require unclear admin changes. Constraints: do not modify the project env; no
  > `pyproject.toml`; nothing installed inside the repo; throwaway Windows venv outside the
  > repo; install only `torch-directml` + resolved deps; run only the tiny DirectML smoke test
  > (import torch, import torch_directml, create dml device, 64×64 matmul); if DirectML
  > succeeds, optionally test `transformers` import only, without downloading a model; delete
  > the throwaway venv after recording; update only docs/GPU_FEASIBILITY, RISKS, DECISIONS,
  > TODO, PROMPTS if needed; do not select a final model; no AirLLM/Ollama; no benchmark; no
  > stage/commit/push. Final report only.

- **Results:**
  - **Python 3.11:** **installed** — `winget install Python.Python.3.11 --scope user --silent`
    → **3.11.9** (user-scope, no admin/UAC issue). Visible via `py -0p`.
  - **torch-directml:** installed in a throwaway Py3.11 venv (`torch-directml 0.2.5.dev240914`,
    `torch 2.4.1`).
  - **DirectML smoke test:** ✅ **SUCCESS** — `import torch_directml` OK; `device_count()` = 1;
    device `privateuseone:0`; 64×64 `x @ y` → shape `(64,64)`, dtype `float32`, all-finite.
  - **transformers:** ✅ imported (`5.12.1`) alongside torch_directml; **no model downloaded.**
  - **Cleanup:** throwaway venv deleted; WSL project env re-verified to have no torch/directml/
    transformers/airllm. Python 3.11.9 remains on the host (authorized persistent change).
- **Outcome:** Windows-native DirectML → **`POSSIBLE` (verified)** as an *optional* GPU
  baseline/extension; **CPU + AirLLM remains the main path** (AirLLM-on-DirectML UNKNOWN; iGPU
  shares system RAM → no extra memory budget). Updated `GPU_FEASIBILITY.md` (§1/§3d/§4/§5/§6),
  `RISKS.md` (R-NOGPU downgraded + 1C-D log), `DECISIONS.md` (ADR-0010 1C-D update), `TODO.md`
  (1C-D tasks), `PROMPTS.md`. **No project deps changed, no project code, no model download, no
  AirLLM/Ollama, no benchmark, no commit/push.**
- **Iterations / corrections:** none — install and smoke test passed first time on Python 3.11.
- **Lessons / notes for next prompts:** GPU compute via DirectML is real but Windows-native and
  outside the AirLLM memory story; the decisive open question for the backend ADR is now AirLLM
  CPU-mode feasibility (and, if anyone wants the GPU lane, AirLLM-on-DirectML), tracked as T1C.7.

---

## Prompt 008 — Stage 1D: AirLLM CPU feasibility check

- **Stage:** 1D
- **Date:** 2026-06-19
- **Intent:** Determine whether **AirLLM** is practically usable for the assignment's main
  **CPU/RAM/disk-I/O** path in the current Ubuntu WSL2 environment — **without downloading
  models** and without creating project implementation code. Feasibility work, not the
  experiment.
- **Context:** GPU feasibility resolved (1C-D: DirectML works but is an optional, Windows-native
  lane). The remaining gate before a backend milestone is AirLLM's own CPU feasibility.
- **Key constraints encoded:** inspect WSL python/uv; discover `airllm`/`air-llm` versions;
  throwaway WSL temp env outside the repo (no repo `pyproject.toml`, no repo installs); lightest
  install + import probe; inspect CPU-mode discoverability; **no model download**, no
  `from_pretrained` on a remote model, no inference, no shards; if install fails, record the
  failure category and a fallback plan without long debugging; clean up the throwaway env; no
  final model; no Ollama; no benchmark; don't touch local course materials; no stage/commit/push.
- **Verbatim prompt (condensed; full text retained in the conversation transcript):**

  > **Stage 1D — AirLLM CPU Feasibility Check.** Determine whether AirLLM is practically usable
  > for the CPU/RAM/disk-I/O path in WSL2, without downloading models or writing project code.
  > Actions: check `python3 --version`/`uv --version`; `pip index versions airllm`/`air-llm`;
  > make a throwaway temp env outside the repo (no repo `pyproject.toml`/installs); lightest
  > install/import probe (install airllm if discoverable, import it, inspect version, inspect
  > whether CPU mode is documented/discoverable from module/API/help; **no** model download, no
  > `from_pretrained` on a real model, no inference, no shards); if install fails record the
  > exact failure category + fallback plan (GGUF/llama.cpp/Ollama for baseline; pinned
  > versions for AirLLM) without long debugging; if import succeeds record Python/package
  > versions, dependencies, likely model-format requirements; clean up the env. Create
  > `docs/AIRLLM_FEASIBILITY.md` (Status / Environment / Package discovery / CPU feasibility
  > interpretation / Constraints & risks / Backend implication) and update
  > `GPU_FEASIBILITY/HARDWARE/RISKS/DECISIONS/TODO/PROMPTS/PLAN` as needed. *Forbidden:* project
  > code, repo `pyproject.toml`, project dep changes, repo installs, model download, AirLLM
  > inference, Ollama, benchmark, final model, stage/commit/push, touching local course
  > materials, `git add`.

- **Results:**
  - **Discovery:** `airllm` on PyPI, latest **2.11.0**; `air-llm` is not a package. (`uv pip
    index` unsupported in uv 0.11.9 → used `pip index`.)
  - **Throwaway env:** `uv venv` (Py 3.12) in `/tmp/ex05_airllm_probe`; CPU `torch` (`2.12.1+cpu`)
    installed first to avoid a multi-GB CUDA download.
  - **Install:** ✅ `airllm 2.11.0` (no `bitsandbytes` hard dep).
  - **Import:** ❌ on latest deps → `optimum.bettertransformer` missing (optimum 2.x removed it);
    ❌ with optimum 1.23.3 → `is_tf_available` missing (transformers 5.x removed it); ❌ then
    missing `sentencepiece`; ✅ **imported** with `transformers==4.44.2` + `optimum==1.23.3` +
    `sentencepiece` (torch CPU, `cuda.is_available()` False).
  - **CPU mode:** **evidenced at API level** — `AirLLMBaseModel(device='cuda:0', …)` exposes
    `device` as a param; source sets `self.device = torch.device(device)` (so `'cpu'` works);
    `bitsandbytes` is imported in a try/except (optional). No model was downloaded.
  - **Cleanup:** throwaway env removed; WSL project env re-verified to have no airllm/torch/etc.
- **Outcome:** **CPU + AirLLM main path EVIDENCED** (import/API). `AIRLLM_FEASIBILITY.md`
  created; added **R-AIRLLM-DEPS** + refined R-QUANT-CPU/R-AIRLLM-COMPAT; **ADR-0011** (pin the
  matrix); TODO/PLAN/PROMPTS/GPU_FEASIBILITY updated. **No model download, no inference, no
  benchmark, no project deps/code changes, no commit/push.**
- **Iterations / corrections:** three bounded dependency pins were needed to reach a clean
  import; stopped as soon as it imported (no deep debugging).
- **Lessons / notes for next prompts:** Stage 2 must pin the 1D matrix in the `uv` lock; the
  last open gate is a **Stage 3 small-model runtime check** with `device='cpu'` (T1D.8) to
  confirm no CUDA-only code path at run time before finalizing the backend ADR.

---

## Prompt 009 — Stage 2A: Project dependency skeleton & measurement design

- **Stage:** 2A
- **Date:** 2026-06-20
- **Intent:** Create the project's **reproducible Python/uv skeleton** and the **measurement
  architecture documentation** — without downloading models, running AirLLM inference, or
  benchmarking. First stage that creates `pyproject.toml`/`uv.lock` and real (skeleton) code.
- **Context:** Stage 1 (hardware + GPU/AirLLM feasibility) is committed (`6a64afe`). CPU +
  AirLLM is the main path with the 1D pinned matrix; this stage turns that into a locked env
  plus the measurement design, ahead of Stage 2B model selection.
- **Key constraints encoded:** `uv` only (no `requirements.txt`, no direct project `pip`);
  pin the 1D AirLLM matrix; CPU torch wheel; Python `>=3.12,<3.13` (stop & report if it can't
  resolve); ruff (line 100, py312, `E,F,W,I,N,UP,B,C4,SIM`), pytest, coverage `fail_under=85`;
  every file ≤150 code lines; no secrets/weights/downloads; **no runner/AirLLM/DirectML/plot/
  cost code**, no inference, no Ollama, no benchmark, no final model, no fake results; no
  commit/push.
- **Verbatim prompt (condensed; full text retained in the conversation transcript):**

  > **Stage 2A — Project Dependency Skeleton and Measurement Design.** Create the project's
  > reproducible Python/uv skeleton and measurement architecture docs without downloading
  > models, running AirLLM, or benchmarking. Create `pyproject.toml`, `uv.lock` (via uv),
  > minimal `src/ex05_airllm` (`__init__`, `version`, `constants`), `tests/unit/test_version.py`
  > (package vs pyproject version consistency), `docs/MEASUREMENT_DESIGN.md`, a
  > `config/experiment.example.{toml,json}` (example only, no real model id), and update
  > PLAN/QUALITY/TODO/DECISIONS/REQUIREMENTS_AUDIT (no experiments DONE)/PROMPTS/README. Pin the
  > AirLLM matrix (airllm==2.11.0, transformers==4.44.2, optimum==1.23.3, sentencepiece) + CPU
  > torch; add psutil/pandas/matplotlib/pydantic/typer/rich and dev pytest/pytest-cov/ruff;
  > Python >=3.12,<3.13 (stop & report if resolution fails). ruff line-length 100, target py312,
  > select E,F,W,I,N,UP,B,C4,SIM; pytest + coverage source=src fail_under=85; files ≤150 code
  > lines. MEASUREMENT_DESIGN.md must have the 9 sections (status/goals/metrics/result schema/
  > experiment matrix/tools/repro rules/risks/Stage 2B acceptance). Validation: `uv sync --extra
  > dev`, `uv run pytest`, `uv run ruff check .`, `uv run ruff format --check .`, and a ≤150
  > line-count script. Forbidden: benchmark/AirLLM/DirectML/plot/cost runners, model download,
  > inference, Ollama, fake results/figures, commit, push.

- **Results / validation:**
  - **`uv sync --extra dev`:** ✅ resolved & installed with **no version conflicts** — pins
    landed exactly: `airllm 2.11.0`, `transformers 4.44.2`, `optimum 1.23.3`, `sentencepiece
    0.2.1`, `torch 2.12.1+cpu`, plus pandas/matplotlib/pydantic/typer/rich/psutil + dev tools.
    `uv.lock` created (1343 lines). `airllm` imports in the project env (import only).
  - **`uv run pytest`:** ✅ 4 passed; **coverage 100%** (≥85).
  - **`ruff check .`:** ✅ All checks passed (after merging two imports). **`ruff format
    --check .`:** ✅ clean. **Line-count:** ✅ all Python files ≤150 code lines.
  - **Files:** created `pyproject.toml`, `uv.lock`, `src/ex05_airllm/{__init__,version,
    constants}.py`, `tests/unit/test_version.py`, `docs/MEASUREMENT_DESIGN.md`,
    `config/experiment.example.toml`; updated `config/README.md`, `docs/{PLAN,QUALITY,TODO,
    DECISIONS,REQUIREMENTS_AUDIT,PROMPTS}.md` (+ README if needed). ADR-0012 recorded.
- **Outcome:** Reproducible CPU env + measurement design in place; **no model selected, no
  download, no inference, no benchmark, no fake results, no commit/push.**
- **Iterations / corrections:** ruff flagged unsorted imports in the test → merged
  `from ex05_airllm import __version__, constants`; re-ran, clean.
- **Lessons / notes for next prompts:** Stage 2B = model shortlist + ADR-0101 selection
  (sized to ~11 GiB / 933 GB / AirLLM families), then `PRD_measurement.md`/`PRD_airllm_pipeline.md`;
  no download before the model decision is approved.

---

## Prompt 010 — Stage 2B: Model shortlist and selection matrix

- **Stage:** 2B
- **Date:** 2026-06-20
- **Intent:** Produce a justified model-selection plan and shortlist for each role (tiny smoke /
  main AirLLM CPU / direct baseline / optional DirectML GPU) **without downloading weights,
  running inference, or selecting blindly**.
- **Context:** Stage 2A locked the env (pinned AirLLM matrix, CPU torch). CPU+AirLLM is the main
  path; this stage picks *candidates* sized to ~11.24 GiB RAM / 933 GB disk and verifies them via
  HF metadata only.
- **Key constraints encoded:** HF **metadata only** (model card / file sizes / config — no
  `.safetensors`/`.bin`/`.gguf`/shards); if live metadata can't be checked, mark
  `NEEDS_ONLINE_VERIFICATION` and don't fake facts; no inference/AirLLM/Ollama/benchmark; no final
  model chosen blindly; no tokens/secrets; don't touch local course materials; no fake
  results/figures; no commit/push.
- **Verbatim prompt (condensed; full text retained in the conversation transcript):**

  > **Stage 2B — Model Shortlist and Selection Matrix.** Create a model-selection plan and
  > shortlist without downloading weights, running inference, or selecting blindly, justifying
  > candidate categories for: tiny smoke model; main AirLLM CPU candidate; baseline direct-run;
  > optional Windows DirectML GPU extension. Use repo docs; inspect installed AirLLM metadata/help/
  > source (no model loading); use HF metadata only if accessible without downloading weights
  > (lightweight API/model-card metadata/small config files; forbid downloading
  > safetensors/bin/gguf/shards). If metadata can't be checked safely, mark
  > NEEDS_ONLINE_VERIFICATION. Create `docs/MODEL_SELECTION.md` (status; constraints; roles;
  > candidate table with role/candidate_model_id/family/estimated_size/expected_format/
  > license_status/access_status/why_candidate/risk/decision_status/verification_needed; criteria;
  > strategy; preliminary recommendation with RECOMMENDED_FOR_VERIFICATION/DEFERRED/
  > REJECTED_WITH_REASON; what-to-verify-before-download), `docs/PRD_measurement.md`,
  > `docs/PRD_airllm_pipeline.md`, and `config/model_candidates.example.toml` (example groups only,
  > no fake final model, each with decision_status + verification_needed). Update
  > DECISIONS/TODO/RISKS/PLAN/REQUIREMENTS_AUDIT/PROMPTS/README (no final model unless truly
  > verified). Forbidden: download weights, inference, AirLLM/Ollama runtime, benchmark, final
  > model blindly, HF tokens/secrets, local course materials, fake results/figures, commit, push.

- **Metadata actually verified (HF `model_info`, metadata only — no weights):**
  - `Qwen/Qwen2-0.5B` — ungated, apache-2.0, safetensors, **~1.0 GB**.
  - `Qwen/Qwen2-1.5B` — ungated, apache-2.0, **~3.1 GB**.
  - `Qwen/Qwen2-7B` — ungated, apache-2.0, **~15.24 GB** (> 11.24 GiB RAM).
  - `Qwen/Qwen2.5-7B-Instruct` — ungated, apache-2.0, **~15.24 GB**.
  - `mistralai/Mistral-7B-Instruct-v0.2` — ungated, apache-2.0, ~14.5 GB fp16 (repo ~29.5 GB w/ dup).
  - `Qwen/Qwen2-72B` — ungated, license `other`, **~145.4 GB**.
  - Also verified (import only): transformers 4.44.2 natively supports qwen2/mistral/mixtral/llama
    (no `trust_remote_code`); AirLLM exposes `AirLLMQWen2`/`AirLLMMistral`/etc.
- **Outcome:** `MODEL_SELECTION.md` + `PRD_measurement.md` + `PRD_airllm_pipeline.md` +
  `config/model_candidates.example.toml` created; recommendation = tiny `Qwen2-0.5B`, main + direct
  baseline `Qwen2-7B` (RECOMMENDED_FOR_VERIFICATION), Mistral backup / Qwen2-72B stretch /
  Qwen2-1.5B optional GPU all DEFERRED; ADR-0101a recorded, ADR-0101 → SHORTLISTED; RISKS/PLAN/
  TODO/audit/README updated. **No weights downloaded, no inference, no benchmark, no final pick,
  no commit/push.**
- **Iterations / corrections:** none — live metadata was reachable, so no candidate needed the
  `NEEDS_ONLINE_VERIFICATION` fallback.
- **Lessons / notes for next prompts:** final selection (T2.6) needs **user download approval**;
  then Stage 3 runs the tiny model end-to-end on `device='cpu'` to confirm the AirLLM path before
  the 7B run. Primary picks are ungated → no token expected (keeps the no-secrets posture).

---

## Prompt 011 — Stage 3A: Tiny AirLLM CPU smoke probe

- **Stage:** 3A
- **Date:** 2026-06-20
- **Intent:** Run the smallest honest end-to-end AirLLM smoke probe using **Qwen/Qwen2-0.5B** on
  CPU, collect raw evidence, and update docs. Not a benchmark. First stage permitted to download
  a model — **only Qwen2-0.5B**.
- **Context:** Stage 2 (env + measurement design + model shortlist) committed (`1cf2036`).
  Explicit approval: only `Qwen/Qwen2-0.5B` may be downloaded for the smoke; **not** Qwen2-7B.
- **Key constraints encoded:** create `src/ex05_airllm/smoke_airllm.py`; use the pinned env;
  `Qwen/Qwen2-0.5B` only; `device="cpu"`; short prompt; `max_new_tokens<=16`; record timestamps/
  runtime/success/failure_reason/peak RSS/model/backend/device/prompt/output; write raw JSON to
  `results/stage3_smoke_airllm_qwen2_0_5b.json`; **never fake success**; on failure write a
  failure JSON with exception + traceback; no HF token; add a unit test for the result helper
  (no model load); files ≤150 lines. Forbidden: download Qwen2-7B or any other model, Ollama,
  DirectML, benchmark, graphs, fake results, edit materials, store tokens, stage/commit/push.
- **Verbatim prompt (condensed; full text retained in the conversation transcript):**

  > **Stage 3A — Tiny AirLLM CPU Smoke Probe.** Run the smallest honest end-to-end AirLLM smoke
  > using Qwen/Qwen2-0.5B on CPU; collect raw evidence; update docs. Not the final benchmark.
  > Create `src/ex05_airllm/smoke_airllm.py` (pinned env; model id Qwen/Qwen2-0.5B only; AirLLM
  > device="cpu"; short prompt; max_new_tokens<=16; measure start/end/runtime/success/
  > failure_reason/peak RSS/model/backend/device/prompt/output; write raw JSON to
  > results/stage3_smoke_airllm_qwen2_0_5b.json; never fake success; on failure write failure
  > JSON with exception class/message + traceback summary; no HF token). Add a unit test for the
  > schema writer/helper without loading a model; files ≤150 lines. Update SMOKE_RUN.md / TODO /
  > PLAN / RISKS / DECISIONS / REQUIREMENTS_AUDIT (PARTIALLY_EVIDENCED not DONE) / PROMPTS /
  > README. If success: mark Stage 3A AirLLM tiny smoke EVIDENCED, not a benchmark, don't
  > generalize to 7B. If failure: preserve failure JSON, document exact category, propose
  > corrective step. Forbidden: download Qwen2-7B / any other model, Ollama, DirectML, benchmark,
  > graphs, fake results, materials, tokens, stage/commit/push. Only Qwen/Qwen2-0.5B may be
  > downloaded.

- **Outcome:** Probe ran; **success=False** (recorded honestly). Failure category: **AirLLM
  input-format incompatibility** — `AssertionError: model.safetensors.index.json should exist`
  in `split_and_save_layers`: AirLLM requires multi-shard safetensors + index, but Qwen2-0.5B is
  a single `model.safetensors`. AirLLM checks the index **before** fetching weights, so only ~12
  MB metadata/tokenizer files reached the **external** HF cache; the ~1 GB weights were **not**
  downloaded and **no weights are in the repo**. Runtime 6.92 s, peak RSS 261.5 MB. Raw evidence:
  `results/stage3_smoke_airllm_qwen2_0_5b.json` (+ `results/raw/stage3_smoke_console.log`).
  Created `SMOKE_RUN.md`; added R-AIRLLM-SHARD + ADR-0014; updated TODO/PLAN/audit. AirLLM smoke
  is **NOT** marked EVIDENCED (it failed). Tests 8/8 @100%, ruff/format clean, ≤150 lines.
- **Iterations / corrections:** first launch's shell redirect failed (`results/raw/` didn't
  exist; `>` doesn't mkdir) so Python never ran → `mkdir -p results/raw` and re-launched.
- **Lessons / notes for next prompts:** Stage 3B applies ADR-0014: re-save Qwen2-0.5B sharded
  (`save_pretrained(max_shard_size=...)`) for the tiny AirLLM proof; pre-confirm Qwen2-7B is
  natively sharded (it has the index 0.5B lacks) so the limitation won't block the main run.

---

## Prompt 012 — Stage 3B: Re-sharded tiny AirLLM CPU smoke probe

- **Stage:** 3B
- **Date:** 2026-06-20
- **Intent:** Create a local **sharded** copy of Qwen/Qwen2-0.5B so AirLLM receives the
  `model.safetensors.index.json` format it expects (Stage 3A blocker), then rerun the tiny CPU
  smoke honestly. Not a benchmark.
- **Context:** 3A failed because the upstream tiny model is a single safetensors file. Explicit
  approval: download **only Qwen/Qwen2-0.5B** full weights to build a local sharded copy; **not**
  Qwen2-7B or any other model.
- **Key constraints encoded:** add model-artifact ignore rules (`.local_models/`, `.hf_cache/`,
  weight extensions, index files); use an **ignored** `.local_models/qwen2_0_5b_sharded/`;
  `prepare_sharded_model.py` (download+`save_pretrained(max_shard_size)`+tokenizer save+verify
  index+JSON record, honest success/failure, no HF token, no other model); smoke loads the local
  path, `device="cpu"`, short prompt, `max_new_tokens<=16`, records full result; write
  `results/stage3b_smoke_airllm_qwen2_0_5b_resharded.json`; on success say only "Tiny AirLLM CPU
  smoke succeeded on a locally re-sharded Qwen2-0.5B"; on failure preserve+categorize+propose
  (no extra downloads); files ≤150 lines. Forbidden: download 7B/other models, Ollama, DirectML,
  benchmark, graphs, fake results, secrets, materials, stage/commit/push.
- **Verbatim prompt (condensed; full text retained in the conversation transcript):**

  > **Stage 3B — Re-sharded Tiny AirLLM CPU Smoke Probe.** Approved to download only Qwen/Qwen2-
  > 0.5B full weights to create a local sharded copy and run the tiny AirLLM smoke; not approved
  > for Qwen2-7B/any other model. Add ignore rules (`.local_models/`, `.hf_cache/`,
  > `*.safetensors|bin|gguf|pt|pth`, `model.safetensors.index.json`,
  > `pytorch_model.bin.index.json`). Use an ignored `.local_models/qwen2_0_5b_sharded/`. Create
  > `src/ex05_airllm/prepare_sharded_model.py` (download/load Qwen2-0.5B via transformers;
  > `save_pretrained(max_shard_size="50MB")`; `tokenizer.save_pretrained`; verify
  > `model.safetensors.index.json`; write `results/stage3b_prepare_qwen2_0_5b_sharded.json`;
  > honest success/failure; no HF token; no other model). Update the smoke script to load the
  > local path; run AirLLM `device="cpu"`, short prompt, `max_new_tokens<=16`; record model_id/
  > local_model_path/backend/device/success/failure_reason/traceback/start+end/runtime/peak RSS/
  > prompt/output; write `results/stage3b_smoke_airllm_qwen2_0_5b_resharded.json` and console log.
  > Update SMOKE_RUN/TODO/PLAN/RISKS/DECISIONS/REQUIREMENTS_AUDIT (PARTIALLY_EVIDENCED only if
  > the smoke actually succeeds; never DONE)/PROMPTS/README. On success say only "Tiny AirLLM CPU
  > smoke succeeded on a locally re-sharded Qwen2-0.5B" (no benchmark/7B/final-perf claims). On
  > failure: preserve JSON/log, categorize (dependency/AirLLM API/CPU runtime/tokenizer/memory/
  > architecture), propose next correction without more downloads. Forbidden: 7B/other downloads,
  > Ollama, DirectML, benchmark, graphs, fake results, secrets, materials, stage/commit/push.

- **Outcome:** **Tiny AirLLM CPU smoke did NOT succeed.** Three issues surfaced, fixed in order:
  (1) re-shard produced the index; (2) **tied embeddings** → `IndexError` (no `lm_head`), fixed
  by untying (clone embed weight → `lm_head.weight`, numerically identical); (3) AirLLM then
  loaded all layers and **started** the CPU forward pass (peak RSS ≈ 2.7 GB) but failed with
  `RuntimeError: Tensor on device cpu is not on the expected device meta!` — **AirLLM CPU
  runtime issue (meta-device mismatch)**, likely aggravated by torch 2.12.1. Full weights for
  **Qwen2-0.5B only** were downloaded (~954 MB, external HF cache); shards/layers live in the
  git-ignored `.local_models/` (verified untracked). Evidence:
  `results/stage3b_prepare_qwen2_0_5b_sharded.json`,
  `results/stage3b_smoke_airllm_qwen2_0_5b_resharded.json`, `SMOKE_RUN.md` §6. Added
  R-AIRLLM-TIED (resolved) + R-AIRLLM-META (confirmed); ADR-0015 (older-torch corrective,
  proposed); R-AIR-01 stays PLANNED. Tests 11/11 @100%, ruff/format clean, ≤150 lines.
- **Iterations / corrections (this stage):** (a) created `results/raw` before redirect; (b)
  pre-create the AirLLM layers dir (AirLLM `check_space` stats it before creating); (c) untie
  embeddings; then stopped at the meta-device error (deeper fix needs a torch change → ADR-0015).
- **Lessons / notes for next prompts:** AirLLM 2.11 is GPU-oriented; its CPU path hits a
  meta-device bug on torch 2.12. Stage 3C should pin an older torch (user-gated, alters lock) or
  fall back to a direct HF CPU run to prove the pipeline. Don't attempt Qwen2-7B until the CPU
  meta-device issue is resolved (same runtime path); note Qwen2-7B is already multi-shard +
  untied, so issues #1/#2 won't recur there.

---

## Prompt 013 — Stage 3C: Torch-pin retest for the AirLLM CPU meta-device failure

- **Stage:** 3C
- **Date:** 2026-06-20
- **Intent:** Test whether the Stage 3B AirLLM CPU **meta-device** failure is caused by the torch
  version, by pinning an older CPU torch (`torch==2.4.1+cpu`) and rerunning the already-downloaded,
  already-re-sharded Qwen2-0.5B smoke. Controlled dependency-compatibility test.
- **Context:** 3B fixed the model format (re-shard + untie); AirLLM then loaded and started the CPU
  forward pass but failed with `Tensor on device cpu ... meta!` under torch 2.12.1. This stage may
  modify `pyproject.toml`/`uv.lock`. No new model download; preserve 3A/3B evidence.
- **Key constraints encoded:** try `torch==2.4.1+cpu` first; keep AirLLM pins (airllm 2.11.0,
  transformers 4.44.2, optimum 1.23.3, sentencepiece); `uv` only; Python >=3.12,<3.13; CPU index;
  rerun the smoke on `.local_models/qwen2_0_5b_sharded/`; write
  `results/stage3c_smoke_airllm_qwen2_0_5b_torch241.json` + console log; **do not overwrite 3A/3B
  artifacts**; if 2.4.1 doesn't resolve → stop & record (don't try many versions); if it resolves
  but AirLLM still fails → preserve, categorize, recommend ONE next step (AirLLM workaround or
  Stage 3D HF fallback); if it succeeds → record a smoke success only (no benchmark/7B/perf
  claims). Forbidden: 7B/other downloads, Ollama, DirectML, benchmark, graphs, fake results,
  deleting 3A/3B artifacts, secrets, materials, stage/commit/push.
- **Verbatim prompt (condensed; full text retained in the conversation transcript):**

  > **Stage 3C — Torch Pin Retest for AirLLM CPU Meta-Device Failure.** Test whether the AirLLM CPU
  > meta-device failure is caused by torch by pinning an older CPU torch and rerunning the
  > already-resharded Qwen2-0.5B smoke. May modify pyproject/uv.lock (controlled test). Try
  > `torch==2.4.1+cpu` first; keep AirLLM/transformers/optimum/sentencepiece pins; uv only; Python
  > >=3.12,<3.13; CPU index. Inspect current torch pin; modify pyproject to `torch==2.4.1+cpu`;
  > `uv sync --extra dev`; confirm torch version + cuda_available; rerun the 3B smoke on
  > `.local_models/qwen2_0_5b_sharded/`; write `results/stage3c_smoke_airllm_qwen2_0_5b_torch241.json`
  > and console log. If 2.4.1 doesn't resolve → stop & record (don't try many versions; may propose
  > next candidate, don't execute). If it resolves but AirLLM still fails → preserve, categorize,
  > don't claim AirLLM CPU works, recommend one next step (obvious AirLLM workaround from source, or
  > Stage 3D Transformers CPU fallback). If AirLLM had passed → record a smoke-pass note only
  > (re-sharded Qwen2-0.5B under torch 2.4.1+cpu), with no 7B/performance claims. [It did not pass.]
  > Update SMOKE_RUN/TODO/PLAN/RISKS/DECISIONS/REQUIREMENTS_AUDIT/PROMPTS/README/QUALITY.
  > Forbidden: 7B/other model downloads, Ollama, DirectML, benchmark, graphs, fake results, delete
  > 3A/3B artifacts, secrets, materials, stage/commit/push.

- **Outcome:** `torch==2.4.1` **resolved and synced** → installed **`torch 2.4.1+cpu`**
  (`cuda_available=False`). Reran the smoke on the existing re-sharded model (no new download) →
  **FAILED with the identical** `RuntimeError: Tensor on device cpu is not on the expected device
  meta!` (runtime 9.55 s, peak RSS ≈ 3.4 GB). **Conclusion: torch version is NOT the cause** (3B
  torch 2.12.1 and 3C torch 2.4.1 fail identically). **Root cause (source inspection):** AirLLM
  builds the model on `meta` and streams only decoder layers; Qwen2's **top-level `rotary_emb`
  (`inv_freq`)** stays on `meta` (AirLLM relocates a rotary buffer only for GLM) → meta/cpu
  mismatch in the forward pass. **Kept `torch==2.4.1`** as the project pin (closer to AirLLM's era;
  clean with transformers 4.44; fine for HF CPU). Recommended next step: **Stage 3D — direct HF
  `transformers` CPU smoke** to prove the measurement pipeline (ADR-0016). Evidence:
  `results/stage3c_smoke_airllm_qwen2_0_5b_torch241.json`, `SMOKE_RUN.md` §7. 3A/3B artifacts
  preserved. Tests 11/11 @100%, ruff/format clean.
- **Iterations / corrections:** added an `EX05_SMOKE_OUTPUT` env override to the smoke script so the
  3C result writes to a new path **without overwriting** the 3B failure JSON.
- **Lessons / notes for next prompts:** the AirLLM CPU blocker is a library-internal meta-device
  bug (Qwen2 rotary), not a torch/version/model-format issue — a torch downgrade won't fix it.
  Stage 3D (HF CPU) is the clean way to prove the pipeline; Qwen2-7B would hit the **same** rotary
  path, so don't download 7B until AirLLM CPU is patched or the plan explicitly switches approach.

---

## Prompt 014 — Stage 3D: Transformers CPU fallback smoke

- **Stage:** 3D
- **Date:** 2026-06-20
- **Intent:** Prove the measurement / result-writing pipeline end-to-end using **direct HF
  `transformers` on CPU** with the already-downloaded Qwen2-0.5B, while keeping the AirLLM CPU
  blocker documented honestly. A fallback smoke — **not** an AirLLM success and **not** a benchmark.
- **Context:** AirLLM CPU is blocked by R-AIRLLM-META (Qwen2 rotary buffer on `meta`); 3C ruled out
  the torch version. Per ADR-0016, prove the pipeline with plain transformers on CPU.
- **Key constraints encoded:** `Qwen/Qwen2-0.5B` only; `AutoTokenizer`+`AutoModelForCausalLM`;
  CPU only; `local_files_only=True`; short prompt; `max_new_tokens<=16`; `do_sample=False`; record
  timestamps/runtime/load/gen seconds/success/failure/traceback/peak RSS/model/backend=
  "transformers"/device="cpu"/prompt/output/output_tokens_est; write
  `results/stage3d_smoke_transformers_qwen2_0_5b_cpu.json` + console log; run offline
  (`HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1`); if cache missing → record failure honestly, do not
  re-download; add a helper unit test (no model); files ≤150 lines; never fake success. Forbidden:
  7B/any new download, AirLLM rerun, Ollama, DirectML, benchmark, graphs, fake results, delete
  3A/3B/3C artifacts, secrets, materials, stage/commit/push.
- **Verbatim prompt (condensed; full text retained in the conversation transcript):**

  > **Stage 3D — Transformers CPU Fallback Smoke.** Prove the measurement/result-writing pipeline
  > end-to-end using direct HF transformers on CPU with the already-downloaded Qwen/Qwen2-0.5B,
  > keeping the AirLLM blocker documented. Create `src/ex05_airllm/smoke_transformers_cpu.py`
  > (Qwen2-0.5B only; AutoTokenizer+AutoModelForCausalLM; CPU; `local_files_only=True`; short
  > prompt; `max_new_tokens<=16`; `do_sample=False`; record start/end/runtime/load_seconds/
  > generation_seconds/success/failure_reason/traceback/peak RSS/model_id/backend="transformers"/
  > device="cpu"/prompt/output_text/output_tokens_est; write
  > `results/stage3d_smoke_transformers_qwen2_0_5b_cpu.json` + console log; never fake success).
  > Run `HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 uv run python -m ex05_airllm.smoke_transformers_cpu`.
  > If the model isn't cached, don't re-download — record failure honestly. Add a helper unit test
  > (no model load); files ≤150 lines. Fix doc path wording to `.local_models/qwen2_0_5b_sharded/`
  > (no misleading absolute paths). Update SMOKE_RUN/TODO/PLAN/RISKS/DECISIONS/REQUIREMENTS_AUDIT
  > (transformers fallback may be PARTIALLY_EVIDENCED only as a measurement-pipeline smoke; AirLLM
  > stays not-evidenced; no experimental requirement DONE)/QUALITY/PROMPTS/README. On success say
  > only "Transformers CPU fallback smoke succeeded on Qwen2-0.5B" (not AirLLM, not benchmark, no
  > 7B, no final perf). On failure: preserve, categorize (cache missing/transformers load/
  > tokenizer/CPU memory/generation/dependency), recommend next step without new downloads.
  > Forbidden: 7B/new downloads, AirLLM rerun, Ollama, DirectML, benchmark, graphs, fake results,
  > delete 3A/3B/3C artifacts, secrets, materials, stage/commit/push.

- **Outcome: SUCCEEDED.** `smoke_transformers_cpu.py` ran **offline** (`local_files_only=True`,
  `HF_HUB_OFFLINE=1`) → loaded Qwen2-0.5B from **cache only** (no download) and generated coherent
  16-token output (*"An operating system is a software program that manages the hardware and
  software resources of a"*). Schema-valid record written:
  `results/stage3d_smoke_transformers_qwen2_0_5b_cpu.json` (`success=true`; `load_seconds≈4.6`,
  `generation_seconds≈6.2`, `total≈14.9 s`, `peak_rss_mb≈4664`, `output_tokens_est=16`). **This is
  not AirLLM and not a benchmark.** The **measurement pipeline is proven** (ADR-0016 EVIDENCED;
  R-REPRO PARTIALLY_EVIDENCED). AirLLM CPU stays blocked (R-AIRLLM-META, R-AIR-01 PLANNED). 3A/3B/3C
  artifacts preserved. Tests 15/15 @100%, ruff/format clean.
- **Iterations / corrections:** one ruff E501 (a 101-char docstring line) → reflowed.
- **Lessons / notes for next prompts:** the pipeline (timers/RSS/schema/writer) is validated, so
  Stage 3 proper (SDK/MetricsCollector/gatekeeper, TDD) can build on it. AirLLM CPU remains a
  separate, documented limitation; don't download Qwen2-7B until R-AIRLLM-META is resolved (same
  rotary path) or the plan explicitly switches the AirLLM approach.

---

## Prompt 015 — Stage 4A: AirLLM Qwen2 CPU patch feasibility

- **Stage:** 4A
- **Date:** 2026-06-20
- **Intent:** Determine whether the AirLLM Qwen2 CPU meta-device blocker can be fixed with a
  minimal, local, project-owned compatibility shim — **without** editing site-packages,
  downloading new models, or running the main experiment. Patch feasibility only.
- **Context:** 3B/3C established the meta-device error; torch was ruled out; 3D's HF CPU fallback
  proved the pipeline. This stage investigates a targeted AirLLM patch.
- **Key constraints encoded:** read-only inspection of `.venv` AirLLM/transformers; optional
  repo-local `airllm_compat.py` (no site-packages edits; Qwen2 CPU-scoped; **fail closed**;
  documented experimental; no upstream-correctness claim); focused unit tests (not model-heavy);
  allowed runtime probe = rerun the existing tiny **local** re-sharded Qwen2-0.5B AirLLM smoke
  only (`device=cpu`, `max_new_tokens<=16`, no download) → write
  `results/stage4a_smoke_airllm_qwen2_0_5b_patched.json` + console log; if no safe patch, don't run
  model code — document + recommend next path. Forbidden: 7B/any new download, edit
  site-packages/AirLLM files, Ollama, DirectML, benchmark, graphs, fake results, delete Stage 3
  artifacts, secrets, materials, stage/commit/push.
- **Verbatim prompt (condensed; full text retained in the conversation transcript):**

  > **Stage 4A — AirLLM Qwen2 CPU Patch Feasibility.** Determine whether the AirLLM Qwen2 CPU
  > meta-device blocker can be fixed with a minimal local project-owned shim, without modifying
  > site-packages, without new model downloads, without the main experiment. Inspect installed
  > AirLLM + transformers Qwen2 source read-only; create `src/ex05_airllm/airllm_compat.py` only if
  > needed (local, Qwen2-CPU-scoped, fail-closed, documented experimental, no upstream claim); add
  > focused unit tests. Patch options to evaluate: materialize/move non-streamed Qwen2 rotary
  > buffers to CPU after init; instance-scope monkeypatch; disable prefetching only if source
  > confirms; smallest explainable+tested patch. If small/local, rerun the existing tiny local
  > re-sharded Qwen2-0.5B AirLLM smoke (`device=cpu`, `max_new_tokens<=16`, local
  > `.local_models/qwen2_0_5b_sharded/`, no download) → write
  > `results/stage4a_smoke_airllm_qwen2_0_5b_patched.json` + `results/raw/stage4a_smoke_console.log`.
  > If no safe patch → don't run model code; document why; recommend next path (alternate family,
  > or documented limitation + Transformers baseline). Create `docs/AIRLLM_PATCH_FEASIBILITY.md`
  > (status/failure recap/source findings/options/shim/probe/next decision) and update
  > SMOKE_RUN/RISKS/DECISIONS/TODO/PLAN/REQUIREMENTS_AUDIT/QUALITY/PROMPTS/README. Forbidden: 7B/new
  > downloads, modify site-packages/AirLLM, Ollama, DirectML, benchmark, graphs, fake results,
  > delete Stage 3 artifacts, stage/commit/push, secrets, materials.

- **Outcome:** A minimal local shim was implemented (`src/ex05_airllm/airllm_compat.py`:
  `rebuild_qwen2_rotary_on_cpu` + instance-scoped `patch_airllm_qwen2_cpu`, fail-closed, unit-
  tested with no download) and the patched smoke was **attempted** on the local model
  (`EX05_AIRLLM_PATCH=1`). It **FAILED** with the same meta error
  (`results/stage4a_smoke_airllm_qwen2_0_5b_patched.json`, `patched=true`, `success=false`). A
  **throwaway no-download diagnostic** (outside the repo; removed afterwards) reported
  `REBUILT_ROTARY=0` and no meta buffers — **disproving the rotary hypothesis** — and the full
  traceback showed the meta tensor is a running decoder layer's **`input_layernorm.weight`**
  (RMSNorm) reached from `airllm_base.forward` → `Qwen2DecoderLayer.forward`. So the blocker is
  AirLLM's **core** per-layer meta→CPU parameter streaming, **not** rotary. A minimal safe shim is
  therefore **infeasible** → **ADR-0017**: document the AirLLM CPU limitation and use the proven HF
  `transformers` CPU pipeline (3D). `airllm_compat.py` is kept (env-gated off) as a tested artifact.
  Created `docs/AIRLLM_PATCH_FEASIBILITY.md`; updated SMOKE_RUN/RISKS/DECISIONS/TODO/PLAN/QUALITY/
  README. **No site-packages edits, no new download, no 7B, no benchmark, no fake results.** Tests
  21/21 (~98% cov), ruff/format clean.
- **Iterations / corrections:** one ruff E501/format on the new test (reflowed). The targeted
  rotary shim was the natural first hypothesis; the diagnostic redirected the root cause to layer-
  param streaming, leading to the infeasibility decision.
- **Lessons / notes for next prompts:** AirLLM's CPU path leaves *layer parameters* on `meta` for
  Qwen2 on this stack — a core-library issue, not a peripheral buffer; a safe minimal patch can't
  fix it. Proceed on the HF CPU pipeline; AirLLM CPU stays not evidenced; no Qwen2-7B (same core
  path). Future AirLLM use would need a GPU env or an alternate supported family.

---

## Prompt 016 — Stage 4B: Formal experiment direction revision

- **Stage:** 4B
- **Date:** 2026-06-20
- **Intent:** Revise the experiment plan formally and honestly after AirLLM CPU/Qwen2 was proven
  blocked (Stages 3–4A), so the project keeps a coherent path that still satisfies the assignment
  **without any fake AirLLM success**. Documentation-only.
- **Context:** AirLLM CPU is blocked by a core meta→CPU param-streaming defect (ADR-0017); the HF
  `transformers` CPU smoke (3D) succeeded and proves the measurement pipeline.
- **Core decision to document:** do NOT download Qwen2-7B under the current AirLLM CPU path; do NOT
  patch AirLLM core / edit site-packages; continue with the proven Transformers CPU measurement
  pipeline; treat AirLLM as an investigated local-memory-management method whose CPU feasibility
  failed here (with detailed evidence); keep optional future paths documented only (GPU/CUDA AirLLM,
  alternate family, upstream fix, DirectML extension).
- **Key constraints encoded:** docs-only (no new code unless a doc-reference fix needs it); no model
  run, no Transformers generation, no AirLLM, no Ollama, no DirectML, no benchmark, no graphs, no
  downloads, no fake results; keep AirLLM-run requirement PLANNED/BLOCKED/PARTIAL (not DONE); keep
  `download_approved=false`; don't delete prior evidence; no stage/commit/push; no course materials, no secrets.
- **Verbatim prompt (condensed; full text retained in the conversation transcript):**

  > **Stage 4B — Formal Experiment Direction Revision.** Revise the plan honestly after AirLLM
  > CPU/Qwen2 was proven blocked. Decision: do NOT download Qwen2-7B under the current AirLLM CPU
  > path; do NOT modify site-packages / fragile core patch; continue with the proven Transformers
  > CPU measurement pipeline; treat AirLLM as an investigated method whose CPU feasibility failed,
  > with evidence; keep optional future paths documented (GPU AirLLM/CUDA; alternate family;
  > upstream fix; DirectML non-AirLLM extension). Create `docs/EXPERIMENT_REVISION.md`
  > (status/original plan/evidence/decision/assignment-impact/revised Stage 5/risks/exit criteria)
  > and update PLAN/DECISIONS/RISKS/TODO/REQUIREMENTS_AUDIT/MEASUREMENT_DESIGN/MODEL_SELECTION/
  > PRD_measurement/PRD_airllm_pipeline/README/PROMPTS and config (keep `download_approved=false`).
  > README must say AirLLM CPU/Qwen2 is blocked; Transformers CPU is the runnable measurement path.
  > Keep AirLLM generation PLANNED/BLOCKED/PARTIAL not DONE; mark only reproducibility/tooling/
  > pipeline smoke as PARTIALLY_EVIDENCED where justified; Qwen2-7B main only if blocker resolved
  > else deferred; Stage 5 = measurement SDK + repeatable Transformers CPU run (not 7B download);
  > add ADR for revised direction; include grading-risk mitigation. Forbidden: download 7B/any
  > model, run AirLLM/Transformers/Ollama/DirectML, benchmark, graphs, fake results, delete prior
  > evidence, stage/commit/push, materials, secrets.

- **Outcome:** Created `docs/EXPERIMENT_REVISION.md` (8-section structure). Added **ADR-0018**
  (Transformers CPU = measurement path; AirLLM = documented analysis; Qwen2-7B deferred). Revised
  **PLAN/TODO Stage 5** to measurement SDK + repeatable Transformers CPU on Qwen2-0.5B (no 7B
  download). Added **R-GRADE-AIRLLM** + R-SCOPE-AIRLLM with mitigation. Updated MODEL_SELECTION
  (7B deferred unless blocker resolved), MEASUREMENT_DESIGN, both PRDs (revision banners),
  REQUIREMENTS_AUDIT (R-AIR-01 PLANNED/BLOCKED), README (banner + status + tree), config
  (`download_approved=false` reaffirmed). **No model run, no download, no benchmark, no fake
  results, no commit/push.** Tests 21/21, ruff/format clean (no code changed).
- **Iterations / corrections:** none.
- **Lessons / notes for next prompts:** Stage 5 implements the measurement SDK
  (MetricsCollector/ResultWriter, TDD) and a repeatable Transformers CPU measurement; AirLLM stays
  failure evidence; no Qwen2-7B until the AirLLM blocker is resolved on a viable backend.

---

## Prompt 017 — Stage 5A: Measurement SDK & result schema

- **Stage:** 5A
- **Date:** 2026-06-20
- **Intent:** Implement a tested **measurement SDK** that can support repeatable CPU inference
  measurements in Stage 5B — **without running any model inference** in this stage.
- **Context:** Stage 4B set the runnable path to HF `transformers` CPU; this stage builds the
  reusable measurement components (schema, collector, writer, prompts, env) the runner will use.
- **Key constraints encoded:** small modular files under `src/ex05_airllm/`, each ≤150 code
  lines (`metrics.py`, `result_schema.py`, `result_writer.py`, `prompts.py`, `env.py`); typed
  result model aligned to `MEASUREMENT_DESIGN.md` (optional/None where unavailable);
  MetricsCollector with start/mark_first_token/finish + psutil memory + TTFT/TPOT/throughput/
  runtime math, **no model inference for tests**; ResultWriter `write_json`/`append_csv` with
  parent-dir creation, stable column order, **no fake defaults**; deterministic prompt registry;
  privacy-safe env metadata (no usernames/private paths/tokens); tests under `tests/unit` using
  `tmp_path`, failure record must not look successful, CSV stable headers, controlled-clock metric
  math. Forbidden: run Transformers/AirLLM/Ollama/DirectML, benchmark, download any model/Qwen2-7B,
  graphs, fake results, edit site-packages, stage/commit/push, materials, secrets.
- **Verbatim prompt (condensed; full text retained in the conversation transcript):**

  > **Stage 5A — Measurement SDK and Result Schema.** Implement a tested measurement SDK to
  > support repeatable CPU inference measurements in Stage 5B, without running model inference.
  > Create small modular files under `src/ex05_airllm/` (≤150 lines each): `metrics.py`,
  > `result_schema.py`, `result_writer.py`, `prompts.py`, maybe `env.py`. (1) Typed result
  > model/dataclass/Pydantic aligned to MEASUREMENT_DESIGN.md fields (run_id…notes), optional/None
  > allowed. (2) MetricsCollector: start()/mark_first_token()/finish(output_tokens)/psutil memory;
  > compute total_runtime/ttft/generation/tpot/tokens_per_second; simple+testable; no inference for
  > tests. (3) ResultWriter: write_json/append_csv, ensure parent dirs, stable column order, no
  > fake defaults implying success. (4) Prompt registry (os_definition, ai_agent_short,
  > memory_management_short) short+deterministic, no external data. (5) Env metadata: python/
  > platform/torch+cuda if importable/project version; no usernames/private paths/tokens/secrets.
  > Tests under tests/unit (test_result_schema/test_metrics/test_result_writer/test_prompts/
  > test_env): no model/network/HF/AirLLM, tmp_path for writer, failure result not successful, CSV
  > stable headers, controlled-clock metric math, all files ≤150 lines. Update MEASUREMENT_DESIGN/
  > PRD_measurement/TODO/PLAN/QUALITY/REQUIREMENTS_AUDIT(PARTIALLY_EVIDENCED not DONE)/PROMPTS/
  > README. Forbidden: run Transformers/AirLLM/Ollama/DirectML, benchmark, download any model/7B,
  > graphs, fake results, edit site-packages, stage/commit/push, materials, secrets.

- **Outcome:** Implemented `result_schema.py` (typed `MeasurementResult`; optional metrics default
  `None`, `success`=`False`, `extra='forbid'`, `ordered_dict()`), `metrics.py` (`MetricsCollector`
  with injectable clock + RSS, TTFT/TPOT/throughput/runtime/peak-RAM, raises if marked before
  start), `result_writer.py` (`write_json`/`append_csv`, parent dirs, stable header, `None`→empty
  cell — no fake defaults), `prompts.py` (3 deterministic prompts), `env.py` (safe metadata, no
  user/token/`/home/`). Tests: `test_result_schema/test_metrics/test_result_writer/test_prompts/
  test_env` (no model/network; `tmp_path`; failure record not successful; CSV stable header;
  controlled-clock math). Validation: **38 tests pass, ~97% coverage, ruff/format clean, all files
  ≤150 lines.** Docs updated. **No model run, no download, no benchmark, no fake results, no
  commit/push.**
- **Iterations / corrections:** ruff merged two imports + dropped an unused `Field`; fixed a test
  that duplicated the `run_id` kwarg (used a `{**_BASE, "run_id": ...}` merge).
- **Lessons / notes for next prompts:** Stage 5B is a thin runner that wires this SDK around a real
  HF `transformers` CPU `generate` on the **local** Qwen2-0.5B (fixed seeds), writing schema-valid
  records and folding the AirLLM failure JSONs in as structured evidence — no AirLLM run, no 7B.

---

## Prompt 018 — Stage 5B: Repeatable Transformers CPU measurement runner

- **Stage:** 5B
- **Date:** 2026-06-20
- **Intent:** Implement and run a thin repeatable measurement runner over the Transformers CPU
  path using the Stage 5A SDK, producing schema-valid JSON + CSV records for the local
  Qwen/Qwen2-0.5B. No AirLLM, no new model download.
- **Context:** Stage 5A built the SDK; AirLLM CPU is blocked (ADR-0018) so Transformers CPU is the
  runnable measurement path. Qwen2-0.5B is already cached from earlier approved stages.
- **Key constraints encoded:** `run_transformers_cpu_measurement.py`; Qwen2-0.5B only;
  `AutoTokenizer`/`AutoModelForCausalLM`; CPU; `local_files_only=True`; offline; deterministic
  (`manual_seed(0)`, `do_sample=False`, `max_new_tokens<=32`); prompt registry; matrix = 3 prompts
  × 2 repeats = **6 runs**; load model once; use MetricsCollector + ResultWriter; per-run JSON +
  `summary.csv` under `results/measurements/transformers_cpu_qwen2_0_5b/`; stable run ids; record
  load/generation/total seconds, peak RAM, output tokens, tokens/sec; **TTFT may be None**; **TPOT
  may be generation_seconds/output_tokens with a documented caveat**; capture failures honestly;
  never fake success; tests must not load a model (helpers only); files ≤150 lines. Forbidden:
  download 7B/any model, AirLLM, Ollama, DirectML, benchmark beyond the 6 runs, graphs, fake
  results, edit site-packages, stage/commit/push, materials, secrets.
- **Verbatim prompt (condensed; full text retained in the conversation transcript):**

  > **Stage 5B — Repeatable Transformers CPU Measurement Runner.** Implement and run a thin
  > repeatable runner around the Transformers CPU path using the Stage 5A SDK, producing
  > schema-valid JSON+CSV for Qwen/Qwen2-0.5B. No AirLLM, no new download. Create
  > `src/ex05_airllm/run_transformers_cpu_measurement.py`: Qwen2-0.5B only; AutoTokenizer/
  > AutoModelForCausalLM; CPU; `local_files_only=True`; offline; deterministic (`manual_seed(0)`,
  > `do_sample=False`, `max_new_tokens<=32`); prompt registry; matrix 3 prompts × 2 repeats = 6;
  > load once; MetricsCollector+ResultWriter; per-run JSON under
  > `results/measurements/transformers_cpu_qwen2_0_5b/`; append `summary.csv`; stable run ids;
  > record load/generation/total seconds, peak RAM, output tokens, tokens/sec; TTFT may be None;
  > TPOT may be generation_seconds/output_tokens with documented caveat; capture failures honestly;
  > never fake success. Optional typer CLI if small/testable; defaults run the approved Qwen2-0.5B
  > only. Tests (`test_run_transformers_cpu_measurement.py`): no model load/network; unit-test run
  > id/result construction/output token estimation/config defaults; ≤150 lines. Update
  > MEASUREMENT_RUNS/MEASUREMENT_DESIGN/PRD_measurement/TODO/PLAN/QUALITY/REQUIREMENTS_AUDIT
  > (PARTIALLY_EVIDENCED, AirLLM PLANNED/BLOCKED not DONE)/PROMPTS/README. Run
  > `HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 uv run python -m
  > ex05_airllm.run_transformers_cpu_measurement`. Forbidden: download 7B/any model, AirLLM,
  > Ollama, DirectML, benchmark beyond the 6 runs, graphs, fake results, site-packages, stage/
  > commit/push, materials, secrets.

- **Outcome:** Implemented the runner (testable helpers `make_run_id`/`output_tokens_from_ids`/
  `approx_tpot`/`build_result`; model parts `# pragma: no cover`) + `test_run_transformers_cpu_
  measurement.py`. Ran offline → **6/6 runs succeeded** on cached Qwen2-0.5B; wrote 6 JSONs +
  `summary.csv` to `results/measurements/transformers_cpu_qwen2_0_5b/`. Measured: output 27–30
  tokens, total runtime 5.25–6.42 s, throughput ~4.5–5.3 tok/s, peak RAM ~3987–4031 MB, load
  ~4.50 s; **TTFT = None** (no streaming hook), **TPOT approximate** (`generation_seconds/
  output_tokens`, caveat in each record's `notes`). Created `MEASUREMENT_RUNS.md`; set
  R-BASE-01/R-MEAS-TPOT/THRU/MEM/TIME → PARTIALLY_EVIDENCED (R-MEAS-TTFT noted None; AirLLM stays
  PLANNED/BLOCKED). 44 tests ~97% cov, ruff/format clean, ≤150 lines. **No AirLLM, no Qwen2-7B, no
  new download, no DirectML/Ollama, no graphs, no fake results, no commit/push.**
- **Iterations / corrections:** ruff reformatted the runner (wrapped long signatures); fixed two
  E501s via the formatter.
- **Lessons / notes for next prompts:** Stage 6 builds analysis/plots *from* `summary.csv`, the
  cost/energy estimate, and folds the AirLLM failure JSONs in as structured evidence. To evidence
  real TTFT/TPOT later, add a token-streaming hook; current TPOT is explicitly an approximation.

---

## Prompt 019 — Stage 6A: Measurement analysis, figures, and cost/energy estimate

- **Stage:** 6A
- **Date:** 2026-06-20
- **Intent:** Generate reproducible analysis artifacts **from existing committed measurement data
  only** (Stage 5B Transformers CPU CSV/JSON + Stage 3/4A AirLLM failure JSONs): analysis tables,
  JSON stats, plain-matplotlib figures, and an assumption-driven cost/energy estimate. No model
  execution, no downloads, no fake results.
- **Context:** Stage 5B produced 6 successful Transformers CPU records; AirLLM is a documented
  blocker. This stage analyses that committed evidence and folds AirLLM in as a negative result.
- **Key constraints encoded:** create `analyze_measurements.py` + `cost_model.py` (≤150 lines
  each); read `summary.csv` (+ optional AirLLM JSONs); produce `reports/measurement_summary.md`,
  `results/analysis/*.json`, and `figures/*.png` (matplotlib only, no seaborn, plain style);
  compute success count + min/mean/max for runtime/throughput/peak-RAM/output-tokens + per-prompt
  means; note TTFT unavailable/None; AirLLM summary lists each attempt with `success=false` +
  failure category (never imply success); assumption-driven cost/energy with configurable
  assumptions (CPU watts, $/kWh, assumed API per-1M prices, optional hardware cost) and explicit
  formulas + caveats; tests use synthetic tmp data, no models/network, verify stats + cost formulas
  + AirLLM aggregation never marks success; ≤150 lines. Forbidden: download any model/Qwen2-7B,
  run Transformers/AirLLM/Ollama/DirectML, benchmark, fake results, hand-edit committed result
  JSON/CSV, edit site-packages, stage/commit/push, materials, secrets.
- **Verbatim prompt (condensed; full text retained in the conversation transcript):**

  > **Stage 6A — Measurement Analysis, Figures, and Cost/Energy Estimate.** Generate reproducible
  > analysis from existing committed data only (Stage 5B CSV/JSON + Stage 3/4A AirLLM failure
  > JSONs); no model execution, no downloads, no fake results. Create
  > `src/ex05_airllm/analyze_measurements.py` and `cost_model.py`. Analysis reads
  > `results/measurements/transformers_cpu_qwen2_0_5b/summary.csv` (+ optional AirLLM JSONs) and
  > produces `reports/measurement_summary.md`,
  > `results/analysis/transformers_cpu_qwen2_0_5b_summary_stats.json`,
  > `results/analysis/airllm_failure_summary.json`, and matplotlib figures
  > (`figures/transformers_cpu_{runtime,throughput,peak_ram}_by_prompt.png`,
  > `figures/cost_break_even_estimate.png`); no seaborn, plain matplotlib. Compute success count;
  > runtime/throughput/peak-RAM/output-token min/mean/max; per-prompt means; note TTFT None. AirLLM
  > summary lists each attempt success=false + failure category/reason, never implying success,
  > used as a negative result. Cost/energy: conservative assumption-driven model (local CPU watts,
  > $/kWh, API per-1M in/out assumptions, optional hardware cost; energy_kwh = runtime/3600 ×
  > watts/1000; local cost = energy×price; API cost from measured tokens; illustrative break-even,
  > not verified pricing); save `results/analysis/cost_energy_assumptions.json` +
  > `cost_energy_estimate.json`. Tests (`test_analyze_measurements.py`, `test_cost_model.py`):
  > synthetic tmp data, no models/network, test summary stats + cost formulas + AirLLM aggregation
  > not marking success; ≤150 lines. Update ANALYSIS/COSTS/MEASUREMENT_RUNS/MEASUREMENT_DESIGN/TODO/
  > PLAN/QUALITY/REQUIREMENTS_AUDIT (PARTIALLY_EVIDENCED; not final-report DONE; AirLLM PLANNED/
  > BLOCKED)/PROMPTS/README. Run `uv run python -m ex05_airllm.analyze_measurements`. Forbidden:
  > download any model/Qwen2-7B, run Transformers/AirLLM/Ollama/DirectML, benchmark, fake results,
  > hand-edit committed result JSON/CSV, site-packages, stage/commit/push, materials, secrets.

- **Outcome:** Implemented `cost_model.py` (pure energy/cost/break-even formulas + assumptions),
  `analysis_stats.py` (pure stats/per-prompt/AirLLM-aggregation/markdown — split out to keep files
  ≤150 lines), and `analyze_measurements.py` (figures + orchestration, matplotlib Agg, pragma no
  cover) + tests. Ran the analysis on committed data → **6/6** stats: runtime 5.16/5.68/6.57 s,
  throughput 4.42/5.07/5.31 tok/s, peak RAM 3985/4016/4029 MB, output 27/28.7/30 tokens; AirLLM
  `any_success=false` (4 attempts); assumption-based cost/energy (45 W, $0.20/kWh, $0.50/$1.50 per
  1M; per-run energy ≈7.1e-5 kWh, local ≈$1.4e-5, assumed API ≈$4.9e-5). Generated 4 figures, 4
  analysis JSONs, `reports/measurement_summary.md`; created `docs/ANALYSIS.md`; cost/energy audit
  rows → PARTIALLY_EVIDENCED (AirLLM stays PLANNED/BLOCKED). 54 tests ~97% cov, ruff/format clean,
  ≤150 lines. **Raw measurement data unmodified (git diff empty). No model run, no download, no
  benchmark, no fake results, no commit/push.**
- **Iterations / corrections:** analyze_measurements first exceeded 150 lines → split pure logic
  into `analysis_stats.py`; fixed a few E501 long markdown/docstring lines (helper rows + wrapped
  strings).
- **Lessons / notes for next prompts:** cost/energy is **assumption-based, not verified pricing** —
  source/date real prices before any quantitative claim. Stage 6B/7 integrates these tables/figures
  into the README technical report + concept/RQ write-ups; AirLLM stays a negative result; no
  Qwen2-7B.

---

*Template for future entries:*
*Prompt NNN — <stage>: <title> — Intent / Context / Constraints / Verbatim prompt /
Actions / Outcome / Iterations / Lessons.*
