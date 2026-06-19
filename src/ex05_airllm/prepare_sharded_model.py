"""Stage 3B — prepare a locally re-sharded copy of Qwen/Qwen2-0.5B for AirLLM.

AirLLM requires a multi-shard safetensors checkpoint with ``model.safetensors.index.json``;
the upstream tiny model ships as a single file (see docs/SMOKE_RUN.md). This script downloads
**only Qwen/Qwen2-0.5B**, re-saves it with a small ``max_shard_size`` (which creates the index),
and records a JSON preparation result. No other model is fetched; no HF token is used/stored.

Run: ``uv run python -m ex05_airllm.prepare_sharded_model``.
"""

from __future__ import annotations

import json
import sys
import traceback
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

MODEL_ID = "Qwen/Qwen2-0.5B"  # the ONLY model approved for download
MAX_SHARD_SIZE = "50MB"  # forces multiple shards + model.safetensors.index.json

_REPO_ROOT = Path(__file__).resolve().parents[2]
SHARDED_DIR = _REPO_ROOT / ".local_models" / "qwen2_0_5b_sharded"  # git-ignored
PREPARE_RECORD = _REPO_ROOT / "results" / "stage3b_prepare_qwen2_0_5b_sharded.json"
_INDEX_NAME = "model.safetensors.index.json"


def build_prepare_record(**fields: Any) -> dict[str, Any]:
    """Assemble the preparation record (testable, no model load)."""
    base: dict[str, Any] = {
        "stage": "3B-prepare",
        "model_id": MODEL_ID,
        "max_shard_size": MAX_SHARD_SIZE,
        "sharded_dir": str(SHARDED_DIR),
        "untied_embeddings": False,
        "lm_head_in_index": False,
        "index_present": False,
        "timestamp": None,
        "success": False,
        "failure_reason": "",
    }
    base.update(fields)
    return base


def write_json(path: Path, record: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8")


def _prepare() -> dict[str, Any]:  # pragma: no cover - downloads + saves the real model
    try:
        import shutil

        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer

        if SHARDED_DIR.exists():
            shutil.rmtree(SHARDED_DIR)  # clean any stale shards/index
        SHARDED_DIR.mkdir(parents=True, exist_ok=True)
        model = AutoModelForCausalLM.from_pretrained(MODEL_ID)
        # AirLLM's layer splitter expects a separate lm_head weight, but Qwen2-0.5B ties word
        # embeddings (no lm_head in the index). Untie by cloning the embedding weight so the
        # saved index includes lm_head.weight. Numerically identical to the tied model.
        untied = bool(getattr(model.config, "tie_word_embeddings", False))
        if untied:
            model.config.tie_word_embeddings = False
            model.lm_head.weight = torch.nn.Parameter(
                model.get_input_embeddings().weight.detach().clone()
            )
        model.save_pretrained(SHARDED_DIR, max_shard_size=MAX_SHARD_SIZE, safe_serialization=True)
        AutoTokenizer.from_pretrained(MODEL_ID).save_pretrained(SHARDED_DIR)
        index_present = (SHARDED_DIR / _INDEX_NAME).exists()
        lm_head_in_index = index_present and "lm_head.weight" in json.loads(
            (SHARDED_DIR / _INDEX_NAME).read_text(encoding="utf-8")
        ).get("weight_map", {})
        ok = index_present and lm_head_in_index
        return build_prepare_record(
            timestamp=datetime.now(UTC).isoformat(),
            untied_embeddings=untied,
            lm_head_in_index=lm_head_in_index,
            index_present=index_present,
            success=ok,
            failure_reason="" if ok else "index or lm_head.weight missing after save",
        )
    except Exception as exc:
        return build_prepare_record(
            timestamp=datetime.now(UTC).isoformat(),
            success=False,
            failure_reason=f"{type(exc).__name__}: {exc}",
            traceback_summary=traceback.format_exc()[-1800:],
        )


def main() -> int:  # pragma: no cover - orchestration around the real download/save
    record = _prepare()
    write_json(PREPARE_RECORD, record)
    print(f"prepare success={record['success']} index={record['index_present']} -> {SHARDED_DIR}")
    return 0 if record["success"] else 1


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
