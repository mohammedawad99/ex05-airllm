"""Verify the package version stays consistent with ``pyproject.toml`` (R-VERSION)."""

from __future__ import annotations

import tomllib
from pathlib import Path

from ex05_airllm import __version__, constants
from ex05_airllm.version import __version__ as module_version

_PYPROJECT = Path(__file__).resolve().parents[2] / "pyproject.toml"


def _pyproject_version() -> str:
    data = tomllib.loads(_PYPROJECT.read_text(encoding="utf-8"))
    return data["project"]["version"]


def test_package_and_pyproject_versions_match() -> None:
    assert __version__ == _pyproject_version()


def test_init_reexports_module_version() -> None:
    assert __version__ == module_version


def test_version_is_1_0_0() -> None:
    # Versioning starts at 1.0.0 per the submission guidelines (R-VERSION).
    assert __version__ == "1.0.0"


def test_result_schema_has_expected_keys() -> None:
    # Touches constants.py so its definitions are import-covered and stays aligned
    # with docs/MEASUREMENT_DESIGN.md §4.
    for column in ("run_id", "backend", "ttft_seconds", "peak_ram_mb", "success"):
        assert column in constants.RESULT_SCHEMA_COLUMNS
    assert constants.BACKEND_AIRLLM_CPU in constants.BACKENDS
