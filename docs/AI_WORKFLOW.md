# AI Workflow — Using AI Agents as Engineering Collaborators

> **STATUS: STAGE 0.** Describes how AI is used on this project, the human-in-the-loop
> controls, and the guardrails that keep the work honest and reproducible. This reflects
> the course's "Vibe Coding / Agentic Software Engineering" methodology: the human acts as
> a senior architect orchestrating AI agents, not as a passive prompt-typer.

---

## 1. Operating model

- **Human role:** Architect / reviewer / decision-owner. Defines requirements, approves the
  plan, supplies real hardware data, makes irreversible decisions (model choice, commits,
  pushes), and verifies every claim before it is recorded.
- **AI role:** Collaborator that drafts documentation, proposes architecture, scaffolds and
  later writes code under TDD, runs analysis, and maintains the audit trail — always under
  human review.
- **Golden rule (from guidelines §1.4):** *Document full requirements before any line of
  code.* Stage 0 is exactly this rule applied to the whole project.

## 2. Guardrails (non-negotiable)

These are enforced on every AI-assisted step:

1. **No fabrication.** AI never invents hardware specs, benchmark numbers, graphs, or
   citations. Missing facts are marked `NEEDED_USER_INPUT`, never guessed.
2. **No premature work.** No implementation code, model downloads, or dependency installs
   until the corresponding stage's entry conditions are met.
3. **No secrets.** AI never writes tokens/keys into the repo; secrets come from `os.environ`
   or interactive login at runtime only.
4. **Evidence-bound claims.** Anything stated as a result must point to a real file under
   `results/`, `figures/`, or `reports/`. No evidence → not claimed.
5. **Honesty over success.** A documented failure or negative result is a valid, valued
   outcome and is reported as such.
6. **Reversibility gating.** Hard-to-reverse actions (git init/commit/push, deleting files,
   external API calls that cost money) require explicit human go-ahead.

## 3. Workflow loop (per task)

```
  Requirement (audit) → AI drafts → human reviews & corrects → record decision/prompt
        ↑                                                              │
        └──────────────── re-audit at stage close ◄────────────────────┘
```

1. Pick a task from `TODO.md` (traced to a requirement).
2. AI produces a draft (doc, design, or — later — test-first code).
3. Human reviews against the requirement and the guardrails.
4. On acceptance: update `TODO.md`/audit; significant prompts logged in `PROMPTS.md`;
   notable choices logged in `DECISIONS.md`.
5. At each stage boundary, re-run the requirements audit and the relevant quality gates.

## 4. AI use across stages

| Stage | How AI is used | Human checkpoint |
| --- | --- | --- |
| 0 Requirements | Draft all planning docs + audit | Verify completeness, no fabrication |
| 1 Approval | Summarize, collect hardware inputs | Approve PRD; supply real specs |
| 2 Design | Propose measurement design + model options | Approve ADRs, model choice |
| 3 Pipeline | TDD code generation (tests first) | Review tests + code; run gates |
| 4–5 Experiments | Generate runners; parse/collect metrics | Confirm runs are real; inspect raw output |
| 6 Analysis | Build figures, cost model, concept write-ups | Verify numbers regenerate; check honesty |
| 7 Submission | Assemble report; run checklist | Final audit; authorize push |

## 5. Tooling & reproducibility

- **Package management:** `uv` only (no `pip`/`python -m`) from Stage 2 onward.
- **Quality gates:** `ruff` (zero errors), pytest with coverage ≥85% — see `QUALITY.md`.
- **Prompt log:** `PROMPTS.md` records significant prompts, intent, outcome, and iterations.
- **Decision log:** `DECISIONS.md` records ADRs with rationale and alternatives.
- **Determinism:** Seeds and exact commands are documented so AI-assisted runs reproduce.

## 6. What AI is *not* allowed to decide alone

- The final model identity, the API provider/pricing baseline, the chosen extension.
- Any `git add`/commit/push, file deletion, or paid external call.
- Marking a requirement `DONE` without a human-verified evidence path.
