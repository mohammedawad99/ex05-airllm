"""Unit tests for the assumption-based cost/energy model (pure math, no network)."""

from __future__ import annotations

from ex05_airllm.cost_model import (
    DEFAULT_ASSUMPTIONS,
    V2_ASSUMPTIONS,
    api_cost_usd,
    break_even_requests,
    break_even_requests_monthly,
    build_cost_model_v2,
    effective_capex_usd,
    energy_kwh,
    estimate,
    ils_to_usd_per_kwh,
    local_electricity_cost_usd,
    monthly_allocated_capex_usd,
)


def test_energy_kwh() -> None:
    # 3600 s at 1000 W = 1 kWh
    assert energy_kwh(3600, 1000) == 1.0


def test_local_electricity_cost() -> None:
    assert local_electricity_cost_usd(3600, 1000, 0.20) == 0.20


def test_api_cost() -> None:
    # 1M input + 1M output at 0.5 / 1.5 per 1M = 2.0
    assert api_cost_usd(1_000_000, 1_000_000, 0.5, 1.5) == 2.0


def test_break_even_requests() -> None:
    assert break_even_requests(100.0, 2.0, 1.0) == 100.0  # 100 / (2-1)
    assert break_even_requests(100.0, 1.0, 2.0) is None  # api <= local → never
    assert break_even_requests(100.0, 1.0, 1.0) is None  # equal → never


def test_assumptions_flag_not_real_pricing() -> None:
    assert "NOT current/verified market pricing" in str(DEFAULT_ASSUMPTIONS["pricing_note"])
    assert DEFAULT_ASSUMPTIONS["pricing_status"] == "assumption_not_live_verified"


def test_estimate_structure_and_caveat() -> None:
    out = estimate(6.0, 9.0, 30.0)
    for key in (
        "assumptions",
        "per_run_energy_kwh",
        "per_run_local_electricity_usd",
        "per_run_api_cost_usd_estimate",
        "break_even_requests",
        "caveat",
    ):
        assert key in out
    assert out["per_run_energy_kwh"] > 0
    assert "not current verified market pricing" in out["caveat"]
    # overriding assumptions is honoured
    custom = estimate(6.0, 9.0, 30.0, {"electricity_usd_per_kwh": 0.0})
    assert custom["per_run_local_electricity_usd"] == 0.0


# --- Stage 11A cost model v2 ----------------------------------------------------------------


def test_v2_capex_matches_documented_assumptions() -> None:
    assert effective_capex_usd(900.0, 0.25) == 225.0
    assert monthly_allocated_capex_usd(900.0, 0.25, 4) == 4.6875  # 225 / 48


def test_v2_ils_to_usd_per_kwh() -> None:
    assert round(ils_to_usd_per_kwh(0.6432, 3.70), 6) == 0.173838


def test_v2_break_even_monthly_none_when_api_not_costlier() -> None:
    assert break_even_requests_monthly(4.6875, 0.00005, 0.0001) is None
    val = break_even_requests_monthly(4.6875, 0.0002, 0.00005)
    assert val is not None and val > 0


def test_v2_model_nonzero_capex_and_meaningful_break_even() -> None:
    model = build_cost_model_v2(5.0673)
    derived = model["derived"]
    assert derived["effective_local_llm_capex_usd"] == 225.0
    assert derived["monthly_allocated_capex_usd"] == 4.6875
    assert derived["electricity_only_local_cost_per_request_usd_45w"] < 0.01
    assert (
        derived["electricity_only_local_cost_per_request_usd_65w"]
        > derived["electricity_only_local_cost_per_request_usd_45w"]
    )
    be = model["break_even_requests_per_month_amortized"]
    assert set(be) == {"gpt_4o_mini", "gpt_4_1_mini"}
    for name, n in be.items():
        assert n is not None and n > 0, name
    assert model["electricity_only_break_even_requests"] == 0


def test_v2_scenarios_show_capex_dominance() -> None:
    model = build_cost_model_v2(5.0673)
    scenarios = model["scenarios"]
    assert [s["requests_per_month"] for s in scenarios] == [100, 1000, 10000, 100000, 1000000]
    low = scenarios[0]
    assert low["amortized_local_usd"] > low["electricity_only_local_usd"] * 5
    assert low["amortized_local_usd"] >= model["derived"]["monthly_allocated_capex_usd"]


def test_v2_assumptions_are_dated_and_marked() -> None:
    assert V2_ASSUMPTIONS["access_date"] == "2026-06-21"
    assert V2_ASSUMPTIONS["pricing_status"] == "dated_assumption_not_guaranteed_future_pricing"
    assert "2026-06-21" in build_cost_model_v2(5.0)["caveat"]
