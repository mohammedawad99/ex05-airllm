# config/ — Configuration files

Versioned configuration (experiment settings, cost/energy assumptions) lives here. No
hardcoded values in source; secrets come from environment variables, never from these files
(`docs/DECISIONS.md` ADR-0003, ADR-0006).

## Files

- **`experiment.example.toml`** — Stage 2A template for an experiment run. It uses a
  **placeholder model id** on purpose (model selection is Stage 2B; no download before
  approval). Copy it to a real config once a model is chosen. The schema mirrors
  `docs/MEASUREMENT_DESIGN.md` and `src/ex05_airllm/constants.py`.

Configs are versioned (`version = "1.0.0"`, R-VERSION). Never store tokens/keys here.
