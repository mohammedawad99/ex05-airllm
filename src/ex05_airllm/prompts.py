"""Small registry of short, deterministic prompts for repeatable Stage 5B runs.

No external data; each prompt is fixed text so runs are reproducible. ``prompt_id`` values
feed the measurement record's ``prompt_id`` field (``docs/MEASUREMENT_DESIGN.md``).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PromptSpec:
    """A named, fixed prompt."""

    prompt_id: str
    text: str


PROMPTS: tuple[PromptSpec, ...] = (
    PromptSpec("os_definition", "Define an operating system in one short sentence."),
    PromptSpec("ai_agent_short", "In one sentence, what is an AI agent?"),
    PromptSpec(
        "memory_management_short",
        "In one sentence, what does an operating system's memory manager do?",
    ),
)

_BY_ID: dict[str, PromptSpec] = {spec.prompt_id: spec for spec in PROMPTS}


def get_prompt(prompt_id: str) -> PromptSpec:
    """Return the :class:`PromptSpec` for ``prompt_id`` (raises ``KeyError`` if unknown)."""
    return _BY_ID[prompt_id]


def prompt_ids() -> tuple[str, ...]:
    """All registered prompt ids, in registry order."""
    return tuple(spec.prompt_id for spec in PROMPTS)
