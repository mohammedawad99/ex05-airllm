"""Unit tests for the disabled-by-default API gatekeeper (no network, ever)."""

from __future__ import annotations

import json

import pytest

from ex05_airllm.api_gatekeeper import (
    ApiGatekeeper,
    ExternalApiDisabledError,
    load_rate_limits,
)


def test_disabled_by_default_refuses() -> None:
    gk = ApiGatekeeper()
    assert gk.is_enabled() is False
    with pytest.raises(ExternalApiDisabledError):
        gk.guard("example_provider")


def test_env_flag_opts_in() -> None:
    assert ApiGatekeeper(env={"EX05_ENABLE_EXTERNAL_API": "1"}).is_enabled() is True
    assert ApiGatekeeper(env={"EX05_ENABLE_EXTERNAL_API": "0"}).is_enabled() is False
    assert ApiGatekeeper(env={}).is_enabled() is False  # default off


def test_call_runs_only_when_enabled() -> None:
    calls = []

    def fake_request(x):
        calls.append(x)
        return x * 2

    disabled = ApiGatekeeper(enabled=False)
    with pytest.raises(ExternalApiDisabledError):
        disabled.call("p", fake_request, 21)
    assert calls == []  # request_fn never invoked while disabled

    enabled = ApiGatekeeper(enabled=True)
    assert enabled.call("p", fake_request, 21) == 42
    assert calls == [21]


def test_from_config_file_stays_disabled_without_env(tmp_path) -> None:
    cfg = {
        "external_api_enabled": True,
        "providers": {"example_provider": {"requests_per_minute": 60}},
    }
    path = tmp_path / "rate_limits.json"
    path.write_text(json.dumps(cfg), encoding="utf-8")
    # config says enabled, but env opt-in is required → still disabled
    gk = ApiGatekeeper.from_config_file(path, env={})
    assert gk.is_enabled() is False
    assert gk.provider_limits("example_provider")["requests_per_minute"] == 60
    assert gk.provider_limits("missing") == {}
    # both config-enabled AND env opt-in → enabled
    gk2 = ApiGatekeeper.from_config_file(path, env={"EX05_ENABLE_EXTERNAL_API": "1"})
    assert gk2.is_enabled() is True


def test_load_rate_limits_reads_committed_example() -> None:
    data = load_rate_limits("config/rate_limits.example.json")
    assert data["external_api_enabled"] is False
