"""Unit tests for the prompt registry (no model, no network)."""

from __future__ import annotations

import pytest

from ex05_airllm.prompts import get_prompt, prompt_ids


def test_expected_prompt_ids_present() -> None:
    ids = prompt_ids()
    for expected in ("os_definition", "ai_agent_short", "memory_management_short"):
        assert expected in ids


def test_prompts_are_short_and_deterministic() -> None:
    for prompt_id in prompt_ids():
        spec = get_prompt(prompt_id)
        assert spec.prompt_id == prompt_id
        assert 0 < len(spec.text) <= 120
        assert get_prompt(prompt_id).text == spec.text  # stable


def test_unknown_prompt_raises() -> None:
    with pytest.raises(KeyError):
        get_prompt("does_not_exist")
