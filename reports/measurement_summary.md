# Measurement Summary (generated)

Transformers CPU on Qwen/Qwen2-0.5B — 6/6 runs succeeded. Small repeatable measurement, **not** a benchmark. TTFT unavailable (None): HF generate() was not token-streamed in this runner.

| metric | min | mean | max |
| --- | --- | --- | --- |
| total_runtime_seconds | 5.1624 | 5.6824 | 6.5699 |
| tokens_per_second | 4.4206 | 5.0672 | 5.3091 |
| peak_ram_mb | 3985.4 | 4015.6167 | 4029.1 |
| output_tokens | 27.0 | 28.6667 | 30.0 |

## Per-prompt means

| prompt_id | runs | mean_runtime_s | mean_tok/s | mean_peak_ram_mb |
| --- | --- | --- | --- | --- |
| os_definition | 2 | 6.0563 | 4.8269 | 4007.2 |
| ai_agent_short | 2 | 5.7595 | 5.2116 | 4010.5 |
| memory_management_short | 2 | 5.2314 | 5.1633 | 4029.1 |

## AirLLM (negative result)
- attempts: 4; any success: **False**. AirLLM CPU/Qwen2 is blocked in this environment; a negative result, not a success.

## Cost & energy (assumption-based, illustrative)
- per-run energy ≈ 7.103e-05 kWh; local electricity ≈ $1.421e-05; assumed API ≈ $4.85e-05. illustrative under assumptions; not current verified market pricing
