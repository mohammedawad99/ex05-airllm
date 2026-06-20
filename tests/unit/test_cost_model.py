"""Unit tests for the assumption-based cost/energy model (pure math, no network)."""

from __future__ import annotations

from ex05_airllm.cost_model import (
    DEFAULT_ASSUMPTIONS,
    api_cost_usd,
    break_even_requests,
    energy_kwh,
    estimate,
    local_electricity_cost_usd,
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
