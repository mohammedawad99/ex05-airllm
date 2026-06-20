"""Typed result schema for experiment measurement records.

Fields are aligned with ``docs/MEASUREMENT_DESIGN.md`` §4 and
``constants.RESULT_SCHEMA_COLUMNS``. Optional metrics default to ``None`` (not to fake
zeros) so an unavailable measurement never reads as a real value, and ``success`` defaults
to ``False`` so a record never looks successful unless explicitly set.
"""

from __future__ import annotations

from pydantic import BaseModel


class MeasurementResult(BaseModel):
    """One measurement record (one run of one configuration)."""

    run_id: str
    timestamp: str
    environment: str
    backend: str
    model_id: str
    model_size_label: str = "unknown"
    quantization: str = "none"
    prompt_id: str
    prompt: str
    input_tokens_est: int | None = None
    output_tokens: int | None = None
    ttft_seconds: float | None = None
    tpot_seconds: float | None = None
    tokens_per_second: float | None = None
    total_runtime_seconds: float | None = None
    load_seconds: float | None = None
    generation_seconds: float | None = None
    peak_ram_mb: float | None = None
    peak_vram_mb: float | None = None
    disk_read_mb: float | None = None
    disk_write_mb: float | None = None
    success: bool = False
    failure_reason: str = ""
    notes: str = ""

    model_config = {"extra": "forbid"}

    def ordered_dict(self) -> dict[str, object]:
        """Return the record as a dict in the canonical column order."""
        from ex05_airllm.constants import RESULT_SCHEMA_COLUMNS

        data = self.model_dump()
        # RESULT_SCHEMA_COLUMNS is the stable subset used for CSV/JSON columns; this schema
        # adds prompt/load_seconds/generation_seconds, appended after the canonical columns.
        ordered = {key: data[key] for key in RESULT_SCHEMA_COLUMNS if key in data}
        for key in data:  # keep any extra fields (e.g. prompt, *_seconds) in a stable order
            ordered.setdefault(key, data[key])
        return ordered


def schema_field_names() -> tuple[str, ...]:
    """All field names of :class:`MeasurementResult` in declaration order."""
    return tuple(MeasurementResult.model_fields.keys())
