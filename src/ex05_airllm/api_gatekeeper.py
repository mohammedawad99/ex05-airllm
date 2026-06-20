"""Disabled-by-default guard for any future external-API access.

**This project makes no live external-API calls** — the On-Prem-vs-API cost analysis is
assumption-based (``docs/COSTS.md``), not queried from a provider. So R-ARCH-GATEKEEPER is
effectively ``N/A_WITH_RATIONALE`` *today*. This module exists as the single, fail-closed choke
point a future live path would have to go through: it is **off unless explicitly enabled**, it
**never performs any network I/O**, and it refuses calls by raising rather than reaching out.

It can read ``config/rate_limits.example.json`` and the ``EX05_ENABLE_EXTERNAL_API`` env var, but
only to decide whether to *refuse*; it has no provider clients. See ``docs/DECISIONS.md`` ADR-0004.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

ENABLE_ENV_VAR = "EX05_ENABLE_EXTERNAL_API"


class ExternalApiDisabledError(RuntimeError):
    """Raised when an external-API call is attempted while the gatekeeper is disabled."""


def _env_enabled(env: dict[str, str] | None = None) -> bool:
    raw = (env if env is not None else os.environ).get(ENABLE_ENV_VAR, "0")
    return str(raw).strip().lower() in {"1", "true", "yes", "on"}


def load_rate_limits(path: str | Path) -> dict[str, Any]:
    """Load a rate-limit config file (pure file read; no network)."""
    return json.loads(Path(path).read_text(encoding="utf-8"))


class ApiGatekeeper:
    """Fail-closed guard for external-API access. Disabled by default; never calls the network."""

    def __init__(
        self,
        enabled: bool | None = None,
        config: dict[str, Any] | None = None,
        env: dict[str, str] | None = None,
    ) -> None:
        # Explicit ``enabled`` wins; otherwise read the env flag (default off).
        self._enabled = _env_enabled(env) if enabled is None else bool(enabled)
        self._config = config or {}

    @classmethod
    def from_config_file(cls, path: str | Path, env: dict[str, str] | None = None) -> ApiGatekeeper:
        """Build a gatekeeper from a config file; stays disabled unless the env opts in."""
        config = load_rate_limits(path)
        enabled = _env_enabled(env) and bool(config.get("external_api_enabled", False))
        return cls(enabled=enabled, config=config, env=env)

    def is_enabled(self) -> bool:
        """Whether external API access is permitted (default: ``False``)."""
        return self._enabled

    def provider_limits(self, provider: str) -> dict[str, Any]:
        """Return the configured limits for ``provider`` (empty dict if none)."""
        return dict(self._config.get("providers", {}).get(provider, {}))

    def guard(self, provider: str = "external") -> None:
        """Raise :class:`ExternalApiDisabledError` unless explicitly enabled. No network."""
        if not self._enabled:
            raise ExternalApiDisabledError(
                f"External API access to '{provider}' is disabled. This project makes no live "
                f"API calls; set {ENABLE_ENV_VAR}=1 and supply credentials to opt in (future work)."
            )

    def call(self, provider: str, request_fn: Any, *args: Any, **kwargs: Any) -> Any:
        """Run ``request_fn`` only if enabled; otherwise refuse. The gatekeeper itself never
        performs I/O — any network access lives entirely in the caller-supplied ``request_fn``."""
        self.guard(provider)
        return request_fn(*args, **kwargs)


__all__ = ["ApiGatekeeper", "ExternalApiDisabledError", "load_rate_limits", "ENABLE_ENV_VAR"]
