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
