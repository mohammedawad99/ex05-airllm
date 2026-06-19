# config/ — Configuration files

Versioned JSON configuration (app settings, API rate limits, cost/energy assumptions) lives
here from **Stage 2**. No hardcoded values in source; secrets come from environment
variables, never from these files (`docs/DECISIONS.md` ADR-0003, ADR-0006).
