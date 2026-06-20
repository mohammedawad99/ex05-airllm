"""Stage 9C Route A — PyTorch dynamic INT8 vs FP32 measurement (cached Qwen/Qwen2-0.5B, CPU).

Compares the FP32 reference against a **dynamic INT8** version (``quantize_dynamic`` on Linear
modules) of the **same already-cached** model, offline (`local_files_only`), deterministic. Writes a
*separate* result set under ``results/measurements/transformers_cpu_int8_quantization_qwen2_0_5b/``
— it does **not** touch Stage 5B/9B data. **Dynamic INT8 only — NOT GGUF, NOT Q4, NOT Q8.** No
download, no new dependency, no AirLLM, no Qwen2-7B.

Run: ``HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 uv run python -m
ex05_airllm.run_transformers_cpu_int8_quantization_measurement``.
"""

from __future__ import annotations

import csv
import json
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

from ex05_airllm.prompts import get_prompt
from ex05_airllm.quantization_measurement import (
    RECORD_COLUMNS,
    VARIANT_FP32,
    VARIANT_INT8,
    build_record,
    output_preview,
)

MAX_NEW_TOKENS = 32
REPEATS = 2
PROMPT_IDS = ("os_definition", "ai_agent_short", "memory_management_short")
_REPO_ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = _REPO_ROOT / "results" / "measurements" / "transformers_cpu_int8_quantization_qwen2_0_5b"
SUMMARY_CSV = OUT_DIR / "summary.csv"


def _rss_mb() -> float:
    import psutil

    return round(psutil.Process().memory_info().rss / 1_000_000, 1)


def _param_mb(model) -> float | None:  # pragma: no cover - needs a real model
    try:
        total = sum(t.numel() * t.element_size() for t in model.state_dict().values())
        return round(total / 1_000_000, 1)
    except Exception:
        return None


def _write(record: dict, output_text: str) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / f"{record['run_id']}.json").write_text(
        json.dumps(
            {**record, "output_text": output_text}, indent=2, ensure_ascii=False, default=str
        ),
        encoding="utf-8",
    )
    is_new = not SUMMARY_CSV.exists() or SUMMARY_CSV.stat().st_size == 0
    with SUMMARY_CSV.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(RECORD_COLUMNS), extrasaction="ignore")
        if is_new:
            writer.writeheader()
        writer.writerow(
            {k: ("" if record.get(k) is None else record.get(k)) for k in RECORD_COLUMNS}
        )


def _load():  # pragma: no cover - loads the cached model
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    start = time.perf_counter()
    tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2-0.5B", local_files_only=True)
    model = AutoModelForCausalLM.from_pretrained(
        "Qwen/Qwen2-0.5B", local_files_only=True, torch_dtype=torch.float32
    )
    model.eval()
    return tokenizer, model, round(time.perf_counter() - start, 4)


def _quantize(model):  # pragma: no cover - real dynamic quantization
    import torch

    start = time.perf_counter()
    quantized = torch.ao.quantization.quantize_dynamic(model, {torch.nn.Linear}, dtype=torch.qint8)
    quantized.eval()
    return quantized, round(time.perf_counter() - start, 4)


def _run_one(
    model, tokenizer, variant, prompt_id, repeat, load_s, quant_s, param_mb
):  # pragma: no cover
    import torch

    spec = get_prompt(prompt_id)
    peak = _rss_mb()
    try:
        torch.manual_seed(0)
        inputs = tokenizer(spec.text, return_tensors="pt")
        input_len = int(inputs["input_ids"].shape[1])
        wall = time.perf_counter()
        gen0 = time.perf_counter()
        with torch.no_grad():
            out = model.generate(**inputs, max_new_tokens=MAX_NEW_TOKENS, do_sample=False)
        gen_s = round(time.perf_counter() - gen0, 4)
        total_s = round(time.perf_counter() - wall, 4)
        new_ids = out[0][input_len:]
        out_tokens = int(new_ids.shape[0])
        text = tokenizer.decode(new_ids, skip_special_tokens=True)
        peak = max(peak, _rss_mb())
        tps = round(out_tokens / gen_s, 4) if gen_s > 0 and out_tokens else None
        tpot = round(gen_s / out_tokens, 6) if out_tokens else None
        return build_record(
            variant,
            prompt_id,
            repeat,
            success=True,
            prompt=spec.text,
            timestamp=datetime.now(UTC).isoformat(),
            load_seconds=load_s,
            quantization_seconds=quant_s,
            generation_seconds=gen_s,
            total_runtime_seconds=total_s,
            output_tokens=out_tokens,
            tokens_per_second=tps,
            approximate_tpot_seconds=tpot,
            peak_ram_mb=peak,
            param_mb_estimate=param_mb,
            output_preview=output_preview(text),
        ), text
    except Exception as exc:
        rec = build_record(
            variant,
            prompt_id,
            repeat,
            success=False,
            prompt=spec.text,
            timestamp=datetime.now(UTC).isoformat(),
            failure_reason=f"{type(exc).__name__}: {exc}",
            load_seconds=load_s,
            quantization_seconds=quant_s,
            param_mb_estimate=param_mb,
        )
        return rec, ""


def main() -> int:  # pragma: no cover - orchestrates the real measurement
    import torch

    torch.manual_seed(0)
    tokenizer, fp32, load_s = _load()
    int8, quant_s = _quantize(fp32)
    variants = ((VARIANT_FP32, fp32, None), (VARIANT_INT8, int8, quant_s))
    total = ok = 0
    for variant, model, qs in variants:
        param_mb = _param_mb(model)
        for repeat in range(1, REPEATS + 1):
            for prompt_id in PROMPT_IDS:
                record, text = _run_one(
                    model, tokenizer, variant, prompt_id, repeat, load_s, qs, param_mb
                )
                _write(record, text)
                total += 1
                ok += int(bool(record["success"]))
                print(f"{record['run_id']} success={record['success']}")
    print(f"done: {ok}/{total} ok -> {SUMMARY_CSV}")
    return 0 if ok == total else 1


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
