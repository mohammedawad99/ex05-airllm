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

*Template for future entries:*
*Prompt NNN — <stage>: <title> — Intent / Context / Constraints / Verbatim prompt /
Actions / Outcome / Iterations / Lessons.*
