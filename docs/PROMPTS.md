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

*Template for future entries:*
*Prompt NNN — <stage>: <title> — Intent / Context / Constraints / Verbatim prompt /
Actions / Outcome / Iterations / Lessons.*
