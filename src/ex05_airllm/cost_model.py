"""Conservative, assumption-driven cost & energy estimate (pure functions, testable).

Every number derives from clearly-documented **assumptions**, NOT verified live market pricing.
The formulas are deliberately simple and explicit so the estimate is transparent and
reproducible. See ``docs/COSTS.md`` / ``docs/ANALYSIS.md``.
"""

from __future__ import annotations

DEFAULT_ASSUMPTIONS: dict[str, object] = {
    "local_cpu_power_watts": 45.0,  # assumed CPU package draw under inference (not metered)
    "electricity_usd_per_kwh": 0.20,  # assumed tariff
    "api_cost_per_1m_input_tokens_usd": 0.50,  # ASSUMPTION ONLY — not verified live pricing
    "api_cost_per_1m_output_tokens_usd": 1.50,  # ASSUMPTION ONLY — not verified live pricing
    "hardware_cost_usd": 0.0,  # 0 = ignore CAPEX; set a value for sensitivity only
    "pricing_status": "assumption_not_live_verified",
    "pricing_note": "assumption-based; NOT current/verified market pricing",
}


def energy_kwh(runtime_seconds: float, watts: float) -> float:
    """Energy in kWh for a run: seconds/3600 * watts/1000."""
    return runtime_seconds / 3600.0 * watts / 1000.0


def local_electricity_cost_usd(runtime_seconds: float, watts: float, price_per_kwh: float) -> float:
    """Electricity cost (USD) of one local run under the given assumptions."""
    return energy_kwh(runtime_seconds, watts) * price_per_kwh


def api_cost_usd(
    input_tokens: float, output_tokens: float, in_per_1m: float, out_per_1m: float
) -> float:
    """Assumed external-API cost (USD) for one request given token counts and per-1M prices."""
    return input_tokens / 1_000_000 * in_per_1m + output_tokens / 1_000_000 * out_per_1m


def break_even_requests(
    hardware_cost: float, api_per_request: float, local_per_request: float
) -> float | None:
    """N where hardware + N*local == N*api → hardware/(api-local); None if api <= local."""
    delta = api_per_request - local_per_request
    if delta <= 0:
        return None
    return hardware_cost / delta


def estimate(
    mean_runtime_seconds: float,
    mean_input_tokens: float,
    mean_output_tokens: float,
    assumptions: dict[str, object] | None = None,
) -> dict[str, object]:
    """Build the per-run energy/cost estimate dict from measured means + assumptions."""
    a: dict[str, object] = {**DEFAULT_ASSUMPTIONS, **(assumptions or {})}
    watts = float(a["local_cpu_power_watts"])
    price = float(a["electricity_usd_per_kwh"])
    local = local_electricity_cost_usd(mean_runtime_seconds, watts, price)
    api = api_cost_usd(
        mean_input_tokens,
        mean_output_tokens,
        float(a["api_cost_per_1m_input_tokens_usd"]),
        float(a["api_cost_per_1m_output_tokens_usd"]),
    )
    be = break_even_requests(float(a["hardware_cost_usd"]), api, local)
    return {
        "assumptions": a,
        "per_run_energy_kwh": round(energy_kwh(mean_runtime_seconds, watts), 8),
        "per_run_local_electricity_usd": round(local, 8),
        "per_run_api_cost_usd_estimate": round(api, 8),
        "break_even_requests": (None if be is None else round(be, 2)),
        "caveat": "illustrative under assumptions; not current verified market pricing",
    }
