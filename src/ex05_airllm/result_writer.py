"""ResultWriter — persist :class:`MeasurementResult` records as JSON and CSV.

Stable column order (from the schema field order), parent dirs created on demand, and **no
fake defaults**: a record is serialized exactly as given (unavailable metrics stay ``None``;
``success`` is whatever was set). No model, network, or inference here.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

from ex05_airllm.result_schema import MeasurementResult, schema_field_names


def write_json(result: MeasurementResult, path: str | Path) -> Path:
    """Write one result as pretty JSON (overwrites)."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(result.ordered_dict(), indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )
    return target


def append_csv(result: MeasurementResult, path: str | Path) -> Path:
    """Append one result row to a CSV, writing the stable header if the file is new."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    columns = list(schema_field_names())
    is_new = not target.exists() or target.stat().st_size == 0
    row = result.ordered_dict()
    with target.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore")
        if is_new:
            writer.writeheader()
        writer.writerow({key: _csv_value(row.get(key)) for key in columns})
    return target


def _csv_value(value: object) -> object:
    """Render ``None`` as an empty cell (not a fake 0/False) for CSV."""
    return "" if value is None else value
