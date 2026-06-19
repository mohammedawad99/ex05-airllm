# PRD — Running a Massive LLM Locally with AirLLM & Quantization

> **STATUS: STAGE 0 DRAFT.** This document defines requirements only. It contains no
> results and no final model choice. It is finalized and frozen at the end of Stage 1
> (see `PLAN.md`). Changes after that are tracked as ADRs in `DECISIONS.md`.

- **Document version:** 0.1 (Stage 0 draft)
- **Source authority:** the assignment brief and the course software guidelines
- **Related docs:** `PLAN.md`, `TODO.md`, `REQUIREMENTS_AUDIT.md`, `RISKS.md`, `QUALITY.md`, `COSTS.md`

---

## 1. Context & background

Large language models are growing far faster than the memory of a single commodity
machine. The naïve approach — load the whole model into RAM/VRAM at once — fails for a
sufficiently large model. **AirLLM** sidesteps this by loading the transformer **one layer
at a time** from disk, computing it, freeing it, and moving on, so the resident memory is
bounded by a single layer rather than the whole model. The price is heavy, repeated disk
I/O. This project quantifies that trade-off on real hardware and contrasts it with running
the same workload through an external API.

This is an **engineering experiment**, not a product. The deliverable is a deep-dive
technical report (the README) backed by reproducible measurements.

## 2. Problem statement & target audience

- **Problem:** Given a fixed, memory-constrained local machine, can we run a model that is
  *larger than memory*, and what does it cost in latency, throughput, memory, energy, and
  money compared to (a) a direct local baseline and (b) an external API?
- **Primary audience:** The course grader (a strict reviewer who inspects every file) and
  engineers evaluating On-Prem vs API LLM deployment.
- **Secondary audience:** Future-us reproducing or extending the experiment.

## 3. Goals & non-goals

### Goals
- G1. Demonstrate, with evidence, that a deliberately-too-large model runs locally via AirLLM.
- G2. Measure and explain *where the time goes* (prefill vs decode; compute- vs memory-bound).
- G3. Quantify the quantization trade-off (speed/memory vs quality).
- G4. Produce a defensible On-Prem-vs-API cost analysis with a break-even point.
- G5. Deliver a reproducible, honestly-scoped, professionally-documented repository.

### Non-goals
- N1. **Not** maximizing model output quality.
- N2. **Not** achieving fast/real-time inference (slow is acceptable and expected).
- N3. **Not** building a production serving system or UI beyond a thin experiment harness.
- N4. **Not** fine-tuning for accuracy (LoRA/QLoRA only as an optional extension, if chosen).

## 4. Success metrics / KPIs

These are *targets for the experiment's completeness*, not performance promises. Numeric
performance values are produced later and are **not** asserted here.

| KPI | Definition | Acceptance target |
| --- | --- | --- |
| KPI-1 Measurement completeness | All of TTFT, TPOT/ITL, throughput, peak RAM, peak VRAM*, total runtime, energy estimate, qualitative quality captured per configuration | 100% captured (*VRAM only if GPU present) |
| KPI-2 Configurations compared | Baseline + AirLLM + ≥2 quantization levels run on the same task | ≥3 configurations |
| KPI-3 Cost analysis | API cost, On-Prem cost, and break-even all computed with explicit assumptions | Break-even graph produced |
| KPI-4 Concept coverage | Every required lecture concept explained and tied to our evidence | All concepts in R-CONCEPT-01 covered |
| KPI-5 Reproducibility | A reader can regenerate every number/figure from documented commands | Reproduction section verified |
| KPI-6 Quality gates | Lint clean, coverage ≥85%, files ≤150 lines, no secrets | All gates green (see QUALITY.md) |
| KPI-7 Honesty | No fabricated data; negative results reported; assumptions stated | Passes SUBMISSION_CHECKLIST |

## 5. Functional requirements (planned)

- FR-1 **Hardware probe (doc):** Collect and record OS/CPU/RAM/GPU/VRAM/disk/free-disk.
- FR-2 **Model selection:** Choose & justify a HF model larger than local memory.
- FR-3 **Baseline runner:** Execute the task directly (Ollama/HF) and capture behavior incl. failure.
- FR-4 **AirLLM runner:** Execute the same task via AirLLM layer-wise loading.
- FR-5 **Quantization sweep:** Run AirLLM across ≥2 precisions (e.g., FP16/Q8/Q4).
- FR-6 **Metrics collector:** Capture TTFT, TPOT/ITL, throughput, peak RAM/VRAM, runtime, energy estimate.
- FR-7 **Quality sampler:** Persist sample outputs per configuration for qualitative review.
- FR-8 **Cost model:** Compute API vs On-Prem cost and break-even; optional cloud-GPU line.
- FR-9 **API gatekeeper:** Route any external API calls through a central rate-limited/retrying/logged gateway.
- FR-10 **Reporting:** Generate tables/figures and assemble the README technical report.
- FR-11 **Extension:** Implement the chosen original extension.

## 6. Non-functional requirements

- NFR-1 **Reproducibility:** Documented seeds, commands, environment, assumptions.
- NFR-2 **Honesty/integrity:** No invented specs, numbers, or graphs; estimates labelled.
- NFR-3 **Architecture:** Layered, SDK-fronted, OOP, DRY, files ≤150 lines.
- NFR-4 **Quality:** `ruff` clean; tests TDD; coverage ≥85%.
- NFR-5 **Security:** No secrets in repo; env-based tokens; `.gitignore` enforced.
- NFR-6 **Tooling:** `uv` only; `pyproject.toml` + `uv.lock` committed.
- NFR-7 **Portability of analysis:** Cost/energy assumptions parameterized via config, not hardcoded.

## 7. Constraints & assumptions

- C1. Hardware is fixed and now **measured on both layers** (Stage 1A WSL + Stage 1B host,
  `docs/HARDWARE.md`). **Physical host:** Windows 11, ASUS Vivobook S 14, Ryzen AI 9 HX 370,
  ≈ 24 GB RAM, AMD Radeon 890M iGPU (no NVIDIA), ~1 TB NVMe SSD. **Experiment env (WSL2 —
  the binding constraint, ADR-0009):** AMD CPU with 24 threads (AVX-512/VNNI), **≈ 11.24 GiB
  RAM** (WSL2 cap) + 3 GiB swap, **933 GB** free ext4 on an NVMe-backed VHDX, and **no
  compute-capable GPU** usable inside WSL2 (CPU-only; no measurable VRAM).
- C1a. Because RAM is ~11 GiB, the "larger than memory" target is sized against ~11 GiB, and
  the **execution path is CPU-only** unless a GPU compute stack is deliberately enabled.
- C1b. The peak-VRAM metric is expected `N/A_WITH_RATIONALE` (no usable GPU compute in WSL2;
  the host iGPU shares system RAM — see `GPU_FEASIBILITY.md`); the physical disk
  type is hidden by WSL2, so I/O behavior must be measured, not assumed.
- C2. The model must exceed local memory (~11 GiB) — deliberately a "stress" configuration.
- C3. Slow runs and even direct-baseline failure are acceptable and expected outcomes
  (an FP16 7–8B model is expected to OOM/thrash in ~11 GiB — a documentable baseline result).
- C4. No model weights or secrets are committed.
- C5. Network access to Hugging Face / the chosen API provider is available at run time.
- A1. The user can authenticate to Hugging Face without storing a token in the repo.

## 8. Out-of-scope items

- Production deployment, autoscaling, serving infrastructure.
- Training/fine-tuning for accuracy (beyond optional LoRA/QLoRA extension).
- Cross-machine/distributed inference.

## 9. Acceptance criteria (definition of done for the project)

The project is done when: all FRs are implemented and exercised; KPI-1..7 are met;
`REQUIREMENTS_AUDIT.md` shows every requirement `DONE` (or `N/A_WITH_RATIONALE`) with real
evidence paths; the README reads as a complete technical report; and
`SUBMISSION_CHECKLIST.md` passes end-to-end.

## 10. Open questions (resolved in later stages)

- OQ-1 Which specific HF model? → Stage 2, after hardware (ADR).
- OQ-2 Which API provider/pricing baseline for cost? → Stage 6 (ADR, dated pricing).
- OQ-3 Which original extension? → Stage 6 (ADR).
- OQ-4 Baseline via Ollama or HF `transformers` (or both)? → Stage 4 (ADR).

## 11. Per-mechanism PRDs (to be authored)

Per guidelines §2.3, the central mechanisms get dedicated PRDs once their design is fixed
in Stage 2: a planned `docs/PRD_airllm_pipeline.md` (layer-wise loading + quantization
pipeline) and `docs/PRD_measurement.md` (metric definitions, timing methodology, energy
model). These are scheduled, not yet written, and are tracked as R-DOC-PRD-MECH.
