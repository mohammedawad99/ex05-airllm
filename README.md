# EX05 — Running a Massive LLM Locally: AirLLM, Quantization & Performance Benchmarking

> **⚠️ STAGE 0 — DOCUMENTATION ONLY.**
> This repository currently contains **planning and requirements documentation only**.
> There are **no experimental results, no benchmarks, no figures, and no implementation
> code yet**. **This repository is NOT submission-ready.** It is the audited foundation
> on which the experiment will later be built.

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
| Hardware specification | ❌ `NEEDED_USER_INPUT` |
| Final model choice | ⛔ Intentionally deferred (post-hardware) |
| Baseline experiment | ⛔ Not started (Stage 4) |
| AirLLM + quantization experiment | ⛔ Not started (Stage 5) |
| Measurements / figures / cost analysis | ⛔ Not started (Stages 5–6) |
| Implementation code & tests | ⛔ Not started (Stage 3+) |

There are **no results to report yet**, and none are claimed.

---

## Repository layout (Stage 0)

```
ex05-airllm/
├── README.md                     # This file (Stage 0 requirements README)
├── .gitignore                    # Excludes secrets, model weights, caches, large artifacts
├── docs/                         # Mandatory documentation (audited)
│   ├── REQUIREMENTS_AUDIT.md     # Traceability: requirement → status → evidence
│   ├── PRD.md                    # Product Requirements Document (Stage 0 draft)
│   ├── PLAN.md                   # Architecture & staged plan (Stage 0..7)
│   ├── TODO.md                   # Staged task ledger with definition-of-done
│   ├── AI_WORKFLOW.md            # How AI agents are used as collaborators
│   ├── PROMPTS.md                # Prompt engineering log (Prompt 001 = this kickoff)
│   ├── DECISIONS.md              # Architecture Decision Records (ADRs)
│   ├── RISKS.md                  # Risk register with mitigations
│   ├── QUALITY.md                # Planned quality gates (no results yet)
│   ├── COSTS.md                  # Cost-analysis methodology (no numbers yet)
│   └── SUBMISSION_CHECKLIST.md   # Final-audit checklist
├── config/                       # Configuration files (populated from Stage 2)
├── src/                          # Implementation (populated from Stage 3) — empty in Stage 0
├── tests/                        # Tests (populated from Stage 3) — empty in Stage 0
├── experiments/                  # Experiment runners/scripts (Stage 4+)
├── results/                      # Measured data: CSV/JSON (Stage 5+)
├── figures/                      # Generated graphs (Stage 6)
└── reports/                      # Long-form reports linked from README (Stage 6)
```

> `src/`, `tests/`, `experiments/`, `results/`, `figures/`, and `reports/` exist as
> scaffolding for later stages and are intentionally empty of project artifacts in Stage 0.

---

## ⛔ Next required input: hardware specifications

The very next step (Stage 1 → Stage 2) is **blocked** until the local hardware is
documented. Please provide the following (see `docs/REQUIREMENTS_AUDIT.md` for the full
`NEEDED_USER_INPUT` list):

- **OS** — distribution and version (e.g., `cat /etc/os-release`, `uname -a`).
- **CPU** — model and core/thread count (`lscpu`).
- **RAM** — total physical memory (`free -h`).
- **GPU** — model, if any (`nvidia-smi` / `lspci | grep -i vga`).
- **VRAM** — total GPU memory, if a GPU exists (`nvidia-smi`).
- **Disk** — type (NVMe / SSD / HDD) and **free space** (`df -h .`, `lsblk -d -o name,rota`).
- **Group code** — your course group identifier.
- **GitHub repo URL** — the destination remote (no push happens until you ask).
- **Hugging Face access** — confirm you can authenticate **without** storing any token in
  this repo (token via environment variable / interactive login only).

A documentation-only helper to *collect* these specs may be added in Stage 2; until then,
the fields are tracked explicitly as `NEEDED_USER_INPUT` and **not** invented.

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
