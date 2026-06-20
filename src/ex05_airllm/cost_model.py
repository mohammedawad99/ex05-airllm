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


# --- Stage 11A cost model v2 (CAPEX allocation + meaningful break-even) -----------------------
# All values are DOCUMENTED ASSUMPTIONS accessed 2026-06-21 — NOT guaranteed future prices.
V2_ASSUMPTIONS: dict[str, object] = {
    "access_date": "2026-06-21",
    "hardware_purchase_usd": 900.0,  # ASSUMPTION: general-purpose laptop, not a dedicated server
    "amortization_years": 4,
    "annual_local_llm_usage_fraction": 0.25,  # fraction of CAPEX allocated to local LLM use
    "electricity_price_ils_per_kwh": 0.6432,  # ASSUMPTION: Israel residential tariff, 2026-06-21
    "usd_ils": 3.70,  # ASSUMPTION: FX rate, accessed 2026-06-21
    "api_prices_usd_per_1m": {  # ASSUMPTION: official OpenAI pricing, accessed 2026-06-21
        "gpt_4o_mini": {"input": 0.15, "output": 0.60},
        "gpt_4_1_mini": {"input": 0.40, "output": 1.60},
    },
    "input_tokens_per_request": 512,
    "output_tokens_per_request": 128,
    "local_energy_watts": 45.0,  # small-model CPU assumption (also 65W sensitivity)
    "local_energy_watts_sensitivity": 65.0,
    "requests_per_month": [100, 1000, 10000, 100000, 1000000],
    "pricing_status": "dated_assumption_not_guaranteed_future_pricing",
}


def effective_capex_usd(purchase: float, fraction: float) -> float:
    return round(purchase * fraction, 4)


def monthly_allocated_capex_usd(purchase: float, fraction: float, years: float) -> float:
    return round(effective_capex_usd(purchase, fraction) / (years * 12.0), 6)


def ils_to_usd_per_kwh(ils_per_kwh: float, usd_ils: float) -> float:
    return ils_per_kwh / usd_ils


def break_even_requests_monthly(
    monthly_capex: float, api_per_request: float, local_per_request: float
) -> float | None:
    delta = api_per_request - local_per_request
    return None if delta <= 0 else monthly_capex / delta


def build_cost_model_v2(
    measured_tokens_per_second: float, assumptions: dict[str, object] | None = None
) -> dict[str, object]:
    """Pure cost model: CAPEX allocation, electricity, API token cost, scenarios, break-even."""
    a: dict[str, object] = {**V2_ASSUMPTIONS, **(assumptions or {})}
    purchase, frac = float(a["hardware_purchase_usd"]), float(a["annual_local_llm_usage_fraction"])
    capex_month = monthly_allocated_capex_usd(purchase, frac, float(a["amortization_years"]))
    price_kwh = ils_to_usd_per_kwh(float(a["electricity_price_ils_per_kwh"]), float(a["usd_ils"]))
    in_tok, out_tok = float(a["input_tokens_per_request"]), float(a["output_tokens_per_request"])
    runtime = out_tok / measured_tokens_per_second  # local generation time per request (seconds)
    elec_req = local_electricity_cost_usd(runtime, float(a["local_energy_watts"]), price_kwh)
    elec_hi = local_electricity_cost_usd(
        runtime, float(a["local_energy_watts_sensitivity"]), price_kwh
    )
    api_prices: dict[str, dict] = a["api_prices_usd_per_1m"]  # type: ignore[assignment]
    api_req = {
        m: api_cost_usd(in_tok, out_tok, float(p["input"]), float(p["output"]))
        for m, p in api_prices.items()
    }
    be = {m: break_even_requests_monthly(capex_month, api_req[m], elec_req) for m in api_req}
    scenarios = [
        {
            "requests_per_month": n,
            "electricity_only_local_usd": round(n * elec_req, 4),
            "amortized_local_usd": round(capex_month + n * elec_req, 4),
            "api_usd": {m: round(n * api_req[m], 4) for m in api_req},
        }
        for n in a["requests_per_month"]  # type: ignore[union-attr]
    ]
    return {
        "assumptions": a,
        "derived": {
            "effective_local_llm_capex_usd": effective_capex_usd(purchase, frac),
            "monthly_allocated_capex_usd": capex_month,
            "electricity_price_usd_per_kwh": round(price_kwh, 6),
            "per_request_runtime_seconds": round(runtime, 4),
            "electricity_only_local_cost_per_request_usd_45w": round(elec_req, 8),
            "electricity_only_local_cost_per_request_usd_65w": round(elec_hi, 8),
            "api_cost_per_request_usd": {m: round(v, 8) for m, v in api_req.items()},
        },
        "scenarios": scenarios,
        "break_even_requests_per_month_amortized": {
            m: (None if v is None else round(v, 1)) for m, v in be.items()
        },
        "electricity_only_break_even_requests": 0,
        "conclusions": [
            "Electricity-only local inference cost is tiny (sub-cent per request).",
            f"Allocated CAPEX dominates local economics (fixed ${capex_month}/month).",
            "API cost scales with tokens and request volume.",
            "Break-even is meaningful only with nonzero allocated CAPEX (electricity-only is 0).",
            "Privacy / offline capability may justify local inference even when cost does not.",
        ],
        "caveat": "dated assumptions (2026-06-21); not guaranteed future market pricing",
    }


def main() -> int:  # pragma: no cover - delegates artifact writing to the analysis pipeline
    from ex05_airllm.analysis_pipeline import write_cost_artifacts

    return write_cost_artifacts()


if __name__ == "__main__":  # pragma: no cover
    import sys

    sys.exit(main())
