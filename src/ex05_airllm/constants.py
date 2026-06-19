"""Immutable project constants (no logic, no I/O).

Centralizing these names avoids magic strings/values in later code (requirement
R-NOHARDCODE) and keeps the measurement result schema in one authoritative place,
matching ``docs/MEASUREMENT_DESIGN.md`` §4.
"""

from __future__ import annotations

PACKAGE_NAME = "ex05-airllm"

# --- Execution environments (see docs/HARDWARE.md evidence boundary) ---
ENV_WSL2 = "wsl2-ubuntu"
ENV_WINDOWS_NATIVE = "windows-native"
ENVIRONMENTS = (ENV_WSL2, ENV_WINDOWS_NATIVE)

# --- Backends (see docs/GPU_FEASIBILITY.md / docs/AIRLLM_FEASIBILITY.md) ---
BACKEND_BASELINE_HF = "baseline-hf"
BACKEND_BASELINE_OLLAMA = "baseline-ollama"
BACKEND_AIRLLM_CPU = "airllm-cpu"
BACKEND_DIRECTML_GPU = "directml-gpu"
BACKENDS = (
    BACKEND_BASELINE_HF,
    BACKEND_BASELINE_OLLAMA,
    BACKEND_AIRLLM_CPU,
    BACKEND_DIRECTML_GPU,
)

# --- Quantization labels (CPU route favours GGUF; bitsandbytes needs CUDA) ---
QUANT_NONE = "none"
QUANT_FP16 = "fp16"
QUANT_Q8 = "q8"
QUANT_Q4 = "q4"
QUANT_LABELS = (QUANT_NONE, QUANT_FP16, QUANT_Q8, QUANT_Q4)

# --- Canonical measurement result schema (docs/MEASUREMENT_DESIGN.md §4) ---
# Order is significant: it defines the column order for results CSV/JSON output.
RESULT_SCHEMA_COLUMNS = (
    "run_id",
    "timestamp",
    "environment",
    "backend",
    "model_id",
    "model_size_label",
    "quantization",
    "prompt_id",
    "input_tokens_est",
    "output_tokens",
    "ttft_seconds",
    "tpot_seconds",
    "tokens_per_second",
    "total_runtime_seconds",
    "peak_ram_mb",
    "peak_vram_mb",
    "disk_read_mb",
    "disk_write_mb",
    "success",
    "failure_reason",
    "notes",
)

# --- Default project-relative output locations (created by later stages) ---
CONFIG_DIRNAME = "config"
RESULTS_DIRNAME = "results"
FIGURES_DIRNAME = "figures"
REPORTS_DIRNAME = "reports"
