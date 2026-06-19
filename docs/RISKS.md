# Risk Register

> **STATUS: STAGE 0.** Identified risks with likelihood, impact, mitigation, contingency,
> and owner. Re-reviewed at every stage close. Likelihood/Impact scale: Low / Med / High.
> IDs are referenced from `REQUIREMENTS_AUDIT.md`.

---

| id | risk | L | I | trigger / signal | mitigation (preventive) | contingency (if it happens) | owner |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R-MODELSIZE | **Model too large** — the chosen model can't run even under AirLLM, or never finishes in a reasonable time | High | High | OOM despite layer-wise loading; disk thrash; runtime unbounded | Size the model against real hardware (after R-HW-01); start with a small proof model (Stage 3); cap max output tokens; estimate shard/disk footprint before download | Step down model size or quantization; document the failure as a finding (negative result is valid, ADR-0005) | Human |
| R-AIRLLM-COMPAT | **AirLLM compatibility** — model architecture/format unsupported, sharding fails, or API mismatch | Med | High | Class-mismatch errors; sharding step errors; unsupported architecture | Prefer well-supported families (e.g., generic `AutoModel` path); pin AirLLM version; verify support before committing to a model | Switch to a supported model; record incompatibility in DECISIONS/reports | Human/AI |
| R-PYENV | **Python / PyTorch / CUDA mismatch** — version incompatibilities break install or GPU use | Med | High | Install errors; CUDA "not available"; ABI/driver mismatches | Pin versions via `uv` + `uv.lock`; match Torch build to the documented CUDA/driver (after R-HW-01); record exact versions | Fall back to CPU path; pin a known-good matrix; document constraints | Human/AI |
| R-DISK | **Disk space** — model shards + quantized copies + caches exceed free space | Med | High | `df` low; download/sharding aborts mid-way | Check free space before download (R-HW-01 → U-DISK-FREE); estimate footprint; git-ignore weights; clean intermediate shards | Choose a smaller model/precision; relocate cache; free space | Human |
| R-IO | **I/O bottleneck** — AirLLM is disk-bound; slow disk (HDD/SATA) dominates TPOT | High | Med | Very high TPOT; low throughput; CPU/GPU idle waiting on reads | Document disk type (U-DISK-TYPE); measure and *attribute* the bottleneck (this is a core finding, not just a problem); prefer NVMe if available | Report I/O as the dominant bottleneck with evidence (Roofline argument); this is an expected, reportable result | AI |
| R-SECRETS | **Secrets exposure** — HF token / API key committed or leaked | Low | High | Token string appears in a diff/file; key in code | `.gitignore` for `.env`/keys/credentials; secrets via `os.environ` only; `.env-example` placeholders; no `git add .`; pre-push scan | Rotate/revoke the exposed key immediately; purge from history; re-issue | Human |
| R-NONREPRO | **Fake or non-reproducible measurements** — numbers that can't be regenerated, or instrumentation that distorts timings | Med | High | Numbers don't match on re-run; no recorded command/seed; metric defined ambiguously | Define every metric precisely (`PRD_measurement.md`); fix seeds; record exact commands/env; separate raw vs summary results; never hand-edit numbers | Re-run with documented method; discard un-reproducible numbers; annotate variance | AI/Human |
| R-OVERCLAIM | **Overclaim** — stating conclusions stronger than the evidence (specs, costs, energy, quality) | Med | High | Claims without an evidence path; estimates presented as measurements | Evidence-bound reporting (ADR-0005); label estimates; state assumptions; SUBMISSION_CHECKLIST honesty gate; mark unknowns `NEEDED_USER_INPUT` | Soften/retract the claim; add caveats; tie to evidence or remove | Human |

---

## Cross-cutting controls

- **Stage gates:** No stage starts until the prior stage's Definition of Done is met
  (`PLAN.md`), bounding cascade failures.
- **Audit re-check:** `REQUIREMENTS_AUDIT.md` is re-audited each stage; risk column links
  requirements to the risks above.
- **Honesty gate:** `SUBMISSION_CHECKLIST.md` includes explicit no-fabrication / evidence
  checks before submission.

## Risk review log

| date | stage | change |
| --- | --- | --- |
| 2026-06-19 | 0 | Initial register created with the eight required risks. |
