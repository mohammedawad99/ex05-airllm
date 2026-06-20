"""Unit tests for environment metadata (no secrets, no private paths)."""

from __future__ import annotations

import platform

from ex05_airllm.env import environment_metadata
from ex05_airllm.version import __version__


def test_metadata_has_expected_keys() -> None:
    meta = environment_metadata()
    for key in ("python_version", "platform", "torch_version", "cuda_available", "project_version"):
        assert key in meta
    assert meta["python_version"] == platform.python_version()
    assert meta["project_version"] == __version__


def test_metadata_excludes_secrets_and_private_paths() -> None:
    meta = environment_metadata()
    for key in meta:
        lowered = key.lower()
        assert "user" not in lowered
        assert "token" not in lowered
        assert "secret" not in lowered
    # no value should leak an absolute home path
    for value in meta.values():
        assert "/home/" not in str(value)
