# EX05 — Running a Massive LLM Locally: AirLLM, Quantization & Performance Benchmarking

> **⚠️ STAGE 4B — EXPERIMENT DIRECTION REVISED (honest, post-AirLLM-blocker).**
> Planning/requirements docs, measured hardware & backend-feasibility evidence, a reproducible
> `uv` project skeleton, and Stage-3 smoke probes are committed. **Key finding:** the
> **AirLLM CPU path for Qwen2 is BLOCKED in this environment** (a core meta→CPU
> parameter-streaming defect — torch-ruled-out, rotary-ruled-out, a minimal local shim proven
> insufficient; see `docs/AIRLLM_PATCH_FEASIBILITY.md`). **The runnable measurement path is the
> proven HF `transformers` CPU pipeline** on the local `Qwen2-0.5B`; AirLLM is kept as a
> documented feasibility/failure analysis, **not** a successful run. **Qwen2-7B has NOT been
> downloaded** and is **deferred** (`download_approved=false`). There are **no benchmarks/figures
> yet** and **no fake AirLLM success**. Full revision: `docs/EXPERIMENT_REVISION.md`.
> **This repository is NOT submission-ready.**

---

## What this project will be

A deep-dive engineering experiment that demonstrates, in a measured and reproducible way,
how to run a model that is **deliberately larger than this machine's memory** on local
(On-Premises) hardware. The work follows a single throughline:

1. Document the exact local hardware and justify a Hugging Face model against it.
2. Attempt a **direct baseline** (Ollama / Hugging Face `transformers`) and document what
   happens — including the expected failure or slowdown.
3. Run the same task with **AirLLM + quantization** (layer-wise loading from disk).
4. **Measure** TTFT, TPOT/ITL, throughput, peak RAM/VRAM, total runtime, estimated energy,
   and qualitative output quality.
5. **Analyze** On-Prem vs external-API cost, including the break-even point.
6. **Explain** the lecture concepts (CPU/GPU, VRAM, Prefill/Decode, KV cache, quantization,
   SafeTensors/GGUF, virtual memory, paging, mmap, AirLLM layer-wise loading).
7. Deliver an **original extension** (e.g., bottleneck-shift map / quantization Pareto
   frontier / AirLLM decision matrix / API-vs-local break-even simulator).

The final deliverable is this README evolved into a **readable technical report** with
tables, graphs, an evidence map, reproduction instructions, and honest limitations.

> The grading philosophy of this assignment is explicit: **the goal is not output quality
> of the model, nor "fastest" inference.** It is a correct, honest, well-documented
> experiment. A negative result that is well analyzed scores higher than an unsupported
> positive claim. This repository is built to that standard.

---

## Current status

| Aspect | Status |
| --- | --- |
| Requirements captured & audited | ✅ Done (`docs/REQUIREMENTS_AUDIT.md`) |
| Planning (PRD / PLAN / TODO) | ✅ Stage 0 drafts in `docs/` |
| Risks, decisions, AI workflow, prompts logged | ✅ Done in `docs/` |
| Hardware specification | 🟡 Captured & verified (Stage 1A/1B) — `docs/HARDWARE.md` (host ≈24 GB/iGPU/NVMe vs experiment ~11 GiB CPU-only; GPU/VRAM partial) |
| Backend feasibility | 🟡 GPU DirectML works (optional, `docs/GPU_FEASIBILITY.md`); AirLLM imports on CPU (`docs/AIRLLM_FEASIBILITY.md`) but its **CPU run is blocked** (see below) |
| Dependency skeleton & measurement design | ✅ Stage 2A — `pyproject.toml` + `uv.lock` (pinned matrix, CPU torch), `src/ex05_airllm` + version test, `docs/MEASUREMENT_DESIGN.md` |
| Model shortlist | 🟡 Stage 2B — metadata-verified shortlist (`docs/MODEL_SELECTION.md`): tiny `Qwen2-0.5B`, main `Qwen2-7B`; **no download** |
| Final model choice | ⛔ Shortlisted, not finalized — final pick + download await approval & Stage 3 smoke run |
| Stage 3A–4A AirLLM smoke (Qwen2-0.5B) | 🟥 **Not succeeded / blocked** — format fixed (3B); CPU run hits an AirLLM meta-device error. 3C ruled out torch; **4A** ruled out rotary (a tested local shim didn't help) — root cause is AirLLM's core CPU param streaming (`docs/AIRLLM_PATCH_FEASIBILITY.md`). Documented limitation; not evidenced |
| Experiment direction (Stage 4B) | 🟦 **Revised honestly** (`docs/EXPERIMENT_REVISION.md`, ADR-0018) — **HF `transformers` CPU is the runnable measurement path**; AirLLM kept as documented failure analysis; **Qwen2-7B deferred / not downloaded** |
| Stage 3D Transformers CPU fallback (Qwen2-0.5B) | 🟩 **Succeeded** — direct HF CPU smoke proves the **measurement pipeline** (schema-valid result JSON; `docs/SMOKE_RUN.md` §8). Not AirLLM, not a benchmark |
| Baseline experiment | ⛔ Not started (Stage 4) |
| AirLLM + quantization experiment | ⛔ Not started (Stage 5) |
| Measurements / figures / cost analysis | ⛔ Not started (Stages 5–6) |
| Implementation code & tests | 🟡 Skeleton only (`version`/`constants` + version test); runners not started (Stage 3+) |

There are **no results to report yet**, and none are claimed.

---

## Repository layout (Stage 4B)

```
ex05-airllm/
├── README.md                     # This file (the evolving technical report)
├── .gitignore                    # Excludes secrets, model weights, caches, large artifacts
├── pyproject.toml                # uv project: pinned AirLLM matrix + CPU torch, ruff/pytest/coverage
├── uv.lock                       # Locked, reproducible dependency set
├── docs/                         # Mandatory documentation (audited)
│   ├── REQUIREMENTS_AUDIT.md     # Traceability: requirement → status → evidence
│   ├── HARDWARE.md               # Stage 1A/1B hardware evidence (host vs WSL2)
│   ├── GPU_FEASIBILITY.md        # Stage 1C GPU/DirectML feasibility
│   ├── AIRLLM_FEASIBILITY.md     # Stage 1D AirLLM CPU feasibility (pinned matrix)
│   ├── MEASUREMENT_DESIGN.md     # Metrics + result schema + repro rules
│   ├── MODEL_SELECTION.md        # Stage 2B metadata-verified shortlist
│   ├── PRD_measurement.md  PRD_airllm_pipeline.md   # Per-mechanism PRDs
│   ├── SMOKE_RUN.md              # Stage 3A–4A smoke probes (AirLLM fail, HF CPU success)
│   ├── AIRLLM_PATCH_FEASIBILITY.md  # Stage 4A patch infeasibility analysis
│   ├── EXPERIMENT_REVISION.md    # Stage 4B revised direction (honest)
│   ├── PRD.md  PLAN.md  TODO.md  # Requirements / architecture / task ledger
│   ├── AI_WORKFLOW.md  PROMPTS.md  DECISIONS.md  RISKS.md
│   ├── QUALITY.md  COSTS.md  SUBMISSION_CHECKLIST.md
├── config/
│   └── experiment.example.toml   # Versioned config template (placeholder model id)
├── src/ex05_airllm/              # Package skeleton: version.py, constants.py (no runners yet)
├── tests/unit/                   # test_version.py (version/schema consistency)
├── experiments/                  # Experiment runners (Stage 4+) — not started
├── results/                      # Measured data: CSV/JSON (Stage 5+) — none yet
├── figures/                      # Generated graphs (Stage 6) — none yet
└── reports/                      # Long-form reports linked from README (Stage 6)
```

> `experiments/`, `results/`, `figures/`, and `reports/` are scaffolding for later stages and
> hold no project artifacts yet. `src/`/`tests/` contain only the Stage 2A skeleton + version
> test — no runner, AirLLM, DirectML, plotting, or cost code exists yet.

---

## Hardware: captured & verified (Stage 1A WSL + Stage 1B host)

Hardware is **measured on both layers** and documented in
[`docs/HARDWARE.md`](docs/HARDWARE.md) — no specs are invented. We keep a strict **evidence
boundary** between the physical host and what the experiment can actually use (per ADR-0009,
model selection is calibrated to the *execution environment*):

- **Physical host (context):** Windows 11, ASUS Vivobook S 14, Ryzen AI 9 HX 370, **≈ 24 GB**
  RAM, AMD Radeon 890M iGPU (no NVIDIA), ~1 TB **NVMe SSD**.
- **Experiment env (binding — Ubuntu WSL2):** 24 CPU threads (AVX-512/VNNI), **≈ 11.24 GiB**
  RAM (WSL2 cap) + 3 GiB swap, **933 GB** free ext4 on an NVMe-backed VHDX.
- **GPU for compute:** **none usable in WSL2** — the host iGPU is detected by Windows, but
  CUDA/ROCm compute inside Ubuntu is **not** evidenced → **CPU-only**; peak-VRAM `N/A`.
- **Tooling:** Python 3.12.3, `uv` 0.11.9.

> NVMe media is favorable for AirLLM's layer streaming, but **I/O speed is not claimed** —
> it is reached through the WSL VHDX/9p layer and must be benchmarked (see `docs/HARDWARE.md`
> §A/§B, `docs/RISKS.md` R-WSL-DISK).

## ⛔ Still required from the user (not measurable)

These do **not** block Stage 2 model selection but are tracked as `NEEDED_USER_INPUT` (see
`docs/REQUIREMENTS_AUDIT.md` §C) and are **not** invented:

- **Group code** — your course group identifier.
- **Hugging Face access** — confirm you can authenticate **without** storing any token in
  this repo (environment variable / interactive login only).
- **Electricity tariff** (per kWh) and **hardware cost / depreciation** — for the Stage 6
  cost model only.

> GitHub repo URL is set: `https://github.com/mohammedawad99/ex05-airllm` (`origin`, `main`).

---

## Reproduction (current stage)

There is nothing to *run* yet. To validate the Stage 0 deliverables:

```bash
# 1. List all tracked files
find . -maxdepth 3 -type f | sort

# 2. Confirm there are no forbidden placeholder phrases
grep -RniE "will contain|coming soon|lorem|placeholder|fake result|TODO later" \
    README.md docs .gitignore || echo "clean"
```

Package management for later stages will use **`uv`** exclusively (no `pip`,
no `python -m`). No dependencies are installed in Stage 0.

---

## Honest limitations (Stage 0)

- No hardware profile yet → no model can be responsibly selected → no experiment can run.
- All performance, cost, and quality sections are **planned methodology only**; they
  contain **no numbers** and make **no claims**.
- Time estimates in `docs/PLAN.md` are estimates, not measured durations.

## Security & data handling

- **No secrets are stored in this repository.** Hugging Face tokens and API keys are
  provided only via environment variables or interactive login at runtime.
- `.gitignore` excludes `.env`, key/credential files, model weights, and large artifacts.
- A committed `.env-example` (placeholders only) will be added when secrets are first
  needed (Stage 4).

## License & credits

- Course-provided materials (assignment brief, lecture 08 guidance, course software
  guidelines) are kept **local only** for reference and are not part of this repository or
  redistributed.
- This project is coursework for Assignment 05 (L08). A project license will be declared in
  `docs/DECISIONS.md` before the repository is made public.

---

*Stage 0 generated as a requirements-and-planning baseline. See `docs/` for the full
audit trail. Nothing in this repository should be read as a result.*
