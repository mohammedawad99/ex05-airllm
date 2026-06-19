# GPU Feasibility Diagnostics — Stage 1C-A / 1C-B / 1C-C / 1C-D

> Companion to `docs/HARDWARE.md`. This investigates **whether** the physical AMD Radeon
> 890M integrated GPU can realistically drive the project stack (PyTorch / Transformers-style
> inference / AirLLM / quantization). Stage 1C-A is **diagnostic only**; Stage 1C-B adds an
> **isolated, throwaway compatibility probe** (a real DirectML install/import test performed
> in a temporary Windows venv **outside the repo**, leaving the project environment untouched).

## 1. Status

- **Diagnostic / isolated probe only** — Stage 1C-A read-only; Stage 1C-B used a throwaway
  Windows venv in `%TEMP%` (outside Git), now deleted.
- **Project environment unchanged** — no `pip install`/`uv add`/`uv sync` into the project
  env; no `pyproject.toml`; no project dependency changes. (Stage 1C-B installed packages
  **only** into the disposable Windows venv, which was then removed.)
- **No benchmark performed** — no timing, no model run.
- **No model downloaded** — confirmed; the probe used only locally-created tensors.
- **No final execution backend selected** — CPU/AirLLM remains the dependable main path, but
  Stage 1C-D **confirms DirectML works** on the AMD iGPU with a compatible Python (see §3d/§6).
  The formal backend ADR remains deferred per ADR-0010.
- **Stage 1C-D update** — with **user authorization**, Python **3.11.9** was installed
  (user-scope, no admin) and a DirectML 64×64 matmul **succeeded** on the Radeon 890M. The
  GPU is now an evidenced **possible** baseline/extension path (AirLLM-on-DirectML still
  UNKNOWN). The throwaway venv was deleted; the project environment was never touched.
- **The machine has a GPU.** A physical AMD Radeon 890M integrated GPU is present (§2). This
  document does **not** treat the machine as GPU-less; it asks whether that GPU is *usable*
  for this specific software stack — and Stage 1C-B tested exactly that.

Collected: 2026-06-19 (host via `powershell.exe`/CIM/dxdiag; experiment env inside Ubuntu WSL2).

## 2. Physical GPU evidence (Windows host)

```
Win32_VideoController → Name: AMD Radeon(TM) 890M Graphics
                        DriverVersion: 32.0.13022.3006
                        VideoProcessor: AMD Radeon Graphics Processor (0x150E)
                        AdapterRAM: 536,870,912 (512 MB reported — unreliable for iGPUs)
Win32_PnPSignedDriver → DeviceName: AMD Radeon(TM) 890M Graphics
                        DriverVersion: 32.0.13022.3006
                        Manufacturer: Advanced Micro Devices, Inc.
dxdiag → Card name:        AMD Radeon(TM) 890M Graphics
         Display Memory:   12127 MB
         Dedicated Memory:   290 MB
         Shared Memory:    11836 MB
         Driver Version:   32.0.13022.3006
         Feature Levels:   12_2, 12_1, 12_0, 11_1, … (DirectX 12 Ultimate capable)
```

- **The machine has an AMD Radeon 890M integrated GPU** (RDNA 3.5 class), driver
  32.0.13022.3006, vendor AMD.
- **Memory profile (important):** only **290 MB dedicated**; the remaining **~11.8 GB is
  *shared* system memory**. The iGPU draws from the same RAM pool the CPU uses — so a GPU
  path would **not add memory capacity** beyond the system RAM already counted in
  `HARDWARE.md`. This is directly relevant to AirLLM's "larger-than-memory" framing.
- **DirectX 12_2** feature level → the adapter is, in principle, a valid **DirectML** target
  on Windows.
- Windows-native Python 3.13 is also present (`C:\…\Python313\python.exe`, `py` launcher).

## 3. WSL GPU visibility (experiment environment)

```
uname -a   → Linux … 6.6.87.2-microsoft-standard-WSL2 … x86_64   (WSL2)
/dev/dxg   → crw-rw-rw- 10,125   (WSL GPU paravirtualization device PRESENT)
lspci      → not available (pciutils not installed) — cannot enumerate PCI in WSL
nvidia-smi → command not found
rocminfo   → command not found
rocm-smi   → command not found
python3    → Python 3.12.3
torch      → torch_installed: False  (ModuleNotFoundError: No module named 'torch')
```

- **`/dev/dxg` is present** → the WSL GPU paravirtualization channel exists (the basis for
  WSLg / DirectML-class access), but a channel is not a working compute backend on its own.
- **No vendor compute tooling in WSL:** `nvidia-smi`, `rocminfo`, `rocm-smi` are all absent.
- **No PyTorch installed**, so there is currently no `torch.cuda`/`torch.xpu`/DirectML device
  to query. The CUDA check could not run because `torch` is not present.

### Package presence (WSL Python 3.12, read-only `pip show`)

| package | installed? |
| --- | --- |
| `torch` | **No** |
| `torch-directml` | **No** |
| `transformers` | **No** |
| `airllm` | **No** |

`pip 24.0` is available. (Per project policy, dependencies will be managed with `uv` in a
later stage — nothing is installed now.)

## 3b. Stage 1C-B — DirectML compatibility probe (isolated, throwaway)

A real DirectML install/import/device test was run in a **disposable Windows venv outside the
repo** (`%TEMP%\ex05_directml_probe`), which was deleted afterwards. The project environment
was never touched.

**Windows Python versions discovered (`py -0p`):**
```
-V:3.13 *  C:\Users\…\Python313\python.exe     (default)
-V:3.9     C:\Program Files (x86)\…\Python39_64\python.exe   (Visual Studio shared)
python --version → Python 3.13.2
```

**Probe procedure & results:**

| step | outcome |
| --- | --- |
| Throwaway venv created | ✅ Yes — Python **3.9** (the only version in torch-directml's wheel range), in `%TEMP%`, outside Git |
| `pip install torch-directml` | ✅ Install **succeeded** → `torch-directml 0.2.5.dev240914`, `torch 2.4.1+cpu`, `torchvision 0.19.1`, `numpy 2.0.2` |
| `import torch` | ✅ Succeeded (`torch 2.4.1+cpu`) |
| `import torch_directml` | ❌ **FAILED** — `TypeError: 'staticmethod' object is not callable` at `torch_directml/__init__.py:74` |
| Retried with older `torch-directml 0.2.4.dev240913` | ❌ **Same import failure** |
| Create DirectML device | ⛔ Not reached (import failed) |
| Tiny tensor `.to(dml)` + 64×64 matmul | ⛔ Not reached (import failed) |
| `import transformers` | ⛔ **Not tested** — gated on DirectML success (which failed), per the probe plan |
| Model download | ✅ **Avoided** — none attempted; tensors were locally created |
| Throwaway venv cleanup | ✅ Removed; project env re-verified to have **no** `torch`/`torch-directml` |

**Root cause (evidence-based):** `torch_directml`'s module-init calls a `staticmethod`
(`default_device()`) as a default-argument value. Bare `staticmethod` objects only became
**callable in Python 3.10+**; under **Python 3.9** this raises `TypeError` *at import time*,
before any device can be created. The two installed Windows Pythons are therefore both unusable
for this package: **3.9** imports-broken (needs 3.10+), and **3.13** has **no `cp313` wheel**
published. No Python in torch-directml's supported window (**3.10–3.12**) is installed on the host.

> This is a **toolchain / Python-version gap, not a hardware limitation** — the GPU itself is
> DirectX 12_2 capable. The path could be re-opened by installing a Python 3.10–3.12 runtime
> on the host (a user-gated action not taken here, to avoid modifying the host beyond a
> throwaway venv).

## 3c. Stage 1C-C — compatible-Python DirectML retest

Stage 1C-B failed because Windows Python 3.9 can't import `torch-directml` (needs 3.10+) and
3.13 has no wheel. Stage 1C-C checks whether a **compatible Python 3.10–3.12** is available so
the DirectML matmul can actually be exercised.

| check | result |
| --- | --- |
| Python 3.10 / 3.11 / 3.12 already installed? | ❌ **No** — `py -0p` shows only **3.13** (default) and **3.9** (VS-shared) |
| Non-invasive install route available? | ⚠️ `winget` is present (v1.28.240) and offers `Python.Python.3.11` (**3.11.9**, winget source) |
| Compatible Python installed in this stage? | ❌ **No — intentionally not installed** (see decision below) |
| Throwaway venv created | ⛔ Not reached (no compatible interpreter) |
| `torch-directml` installed | ⛔ Not reached |
| `import torch_directml` | ⛔ Not reached |
| DirectML device creation | ⛔ Not reached |
| Tiny tensor / 64×64 matmul | ⛔ Not reached |
| `transformers` import tested | ⛔ Not tested (gated on DirectML success) |
| Model download | ✅ **Avoided** — nothing downloaded |

**Decision — stopped and reported (per the stage's safety rule):** Installing a Python
3.10–3.12 runtime via `winget` is a **persistent, global change to the user's personal
Windows host**, not a disposable venv, and a package install may raise a **UAC elevation
prompt** that cannot be answered from this non-interactive terminal flow. The stage's rule is
explicit: *do not install Python automatically if it requires admin rights, unclear prompts,
or global changes that cannot be cleanly explained — stop and report.* Therefore the retest
was **not** executed; the install is offered to the user as a **gated next step** (see §6).

> **The blocker remains a toolchain gap, not the GPU.** The Radeon 890M is DX12_2 capable; the
> only missing piece for a DirectML attempt is a user-authorized Python 3.10–3.12 runtime.

## 3d. Stage 1C-D — DirectML retest on a compatible Python (user-authorized) ✅

The user explicitly authorized installing Python 3.11 via the safest user-scope route. The
DirectML smoke test was then run in a fresh throwaway venv (outside the repo), which was
deleted afterwards. **The project environment was not modified.**

| step | outcome |
| --- | --- |
| Install Python 3.11 (winget, **user scope, `--silent`, no admin**) | ✅ **Installed** — `Python.Python.3.11` → **3.11.9** at `…\Programs\Python\Python311` |
| Throwaway venv on Python 3.11 (in `%TEMP%`, outside Git) | ✅ Created |
| `pip install torch-directml` | ✅ `torch-directml 0.2.5.dev240914`, `torch 2.4.1`, `torchvision 0.19.1`, `numpy 2.4.6` |
| `import torch` | ✅ `2.4.1+cpu` |
| `import torch_directml` | ✅ **Succeeded** (the 1C-B Python-3.9 import bug is gone on 3.11) |
| `torch_directml.device_count()` | ✅ **1** |
| Create DML device `torch_directml.device()` | ✅ `privateuseone:0` |
| 64×64 tensors on DML + matmul `x @ y` | ✅ **SUCCESS** — result shape `(64, 64)`, dtype `torch.float32`, all-finite |
| `pip install transformers` + `import transformers` | ✅ `transformers 5.12.1` imported; DML device still resolves |
| Model download | ✅ **Avoided** — none attempted |
| Throwaway venv cleanup | ✅ Removed; WSL project env re-verified to have **no** torch/directml/transformers/airllm |

**Result:** the AMD Radeon 890M **can run PyTorch tensor compute via DirectML** on
Windows-native Python 3.11. This is a positive, reproducible result — the earlier blockage was
purely the Python-version/toolchain gap, now resolved by the authorized 3.11 install.

> Python 3.11.9 remains installed on the host (the authorized persistent change). Only the
> throwaway venv was deleted. The WSL project environment and repo are untouched.

## 4. Candidate backend paths

Status vocabulary: `PLANNED` · `POSSIBLE` · `BLOCKED` · `NEEDS_INSTALL_CHECK` ·
`NEEDS_FURTHER_CHECK`. Statuses updated after the Stage 1C-B probe.

| # | Backend path | Status (post 1C-B) | Evidence-based reasoning |
| --- | --- | --- | --- |
| 1 | **WSL + DirectML (`torch-directml`)** | `BLOCKED` (leaning) / `NEEDS_FURTHER_CHECK` | `torch-directml` is published for **Windows-native** Python, not Linux/WSL; it has no Linux wheel for the WSL Python. Not separately retested in 1C-B (the Windows-native test below is the more promising one and already fails). Treated as effectively blocked. |
| 2 | **Windows-native Python + DirectML (`torch-directml`)** | **`POSSIBLE`** (verified, 1C-D) | **1C-D:** with user-authorized Python **3.11.9**, `torch-directml` imports, exposes 1 DML device (`privateuseone:0`), and a 64×64 matmul on the Radeon 890M **succeeds**; `transformers` also imports. Viable as a **GPU baseline/extension** path. Caveats: lives outside the WSL project env (Windows-native), and **AirLLM-on-DirectML compatibility is still UNKNOWN**. |
| 3 | **ROCm in WSL** | `BLOCKED` | `rocminfo`/`rocm-smi` absent. ROCm-on-WSL targets specific **discrete** Radeon cards; the **890M iGPU** is not supported. No new evidence in 1C-B. |
| 4 | **ROCm on native Linux** | `BLOCKED` (for this setup) | Environment is WSL2, not bare-metal Linux; ROCm for this RDNA-3.5 **iGPU** is unofficial/limited. Out of scope without changing the OS. |
| 5 | **CPU + AirLLM** | `POSSIBLE` (**main path for the AirLLM focus**) | No special backend required; CPU fully available with AVX-512/VNNI (`HARDWARE.md`). Remains the dependable path for the assignment's AirLLM/memory-management focus. AirLLM's exact CPU behaviour still to be confirmed (§5, T1C.6). |

> **After 1C-D:** Windows-native DirectML (path 2) is **verified `POSSIBLE`** — the AMD iGPU
> runs PyTorch matmuls via DirectML on Python 3.11. ROCm paths (3–4) stay `BLOCKED`; WSL
> DirectML (1) is still effectively blocked (Windows-native package). The GPU is therefore a
> real **optional baseline/extension** lane, but **CPU + AirLLM remains the main path** for the
> assignment's core focus, and **AirLLM-on-DirectML is unproven**.

## 5. Compatibility questions to resolve before implementation

| question | current answer | action |
| --- | --- | --- |
| Can AirLLM run CPU-only? | **UNKNOWN** | AirLLM is GPU-oriented (layer-by-layer onto an accelerator); a CPU mode exists in some versions. Confirm by reading AirLLM docs/source before committing (planned research). |
| Can AirLLM use a DirectML backend? | **UNKNOWN** | AirLLM expects a PyTorch CUDA-style device; DirectML (`dml`) integration is not a documented AirLLM target. Planned research; mark UNKNOWN until shown. |
| Does the intended Transformers/PyTorch stack support `torch-directml`? | **PARTIAL — import OK (1C-D)** | On Python 3.11, `torch`, `torch_directml`, and `transformers` all import together and the DML device resolves. Basic tensor ops run on DML; **op-coverage for a full Transformers forward pass and quantization is still unverified** (no model was run). |
| Is quantization compatible with the DirectML/ROCm/CPU path? | **PATH-DEPENDENT** | `bitsandbytes` 4/8-bit needs **CUDA** (unavailable here). DirectML quantization is limited. The CPU-compatible route is **GGUF Q4/Q8** (llama.cpp/Ollama). Tracked as R-QUANT-CPU. |
| Would using the GPU distract from the assignment's AirLLM focus? | **PRELIMINARY: likely yes** | The assignment centres on **memory management / AirLLM**. The iGPU shares system RAM (290 MB dedicated), so it adds little memory headroom while adding significant toolchain complexity (DirectML/ROCm). Noted as a consideration, **not** a decision. |

## 6. Engineering interpretation (updated after Stage 1C-D)

- **The GPU exists physically** — an AMD Radeon 890M integrated GPU, DirectX 12_2 capable
  (§2). The project documents this plainly and does **not** ignore it.
- **DirectML now works on the GPU (1C-D, §3d):** on user-authorized Python 3.11, the Radeon
  890M runs a PyTorch matmul through DirectML, and `transformers` imports. This is a positive,
  reproducible result. Earlier "blocked" verdicts (1C-B/1C-C) were a Python-version gap, now
  resolved — at no point was the machine treated as GPU-less.
- **What it means:** the GPU is a genuine **optional baseline / extension** lane — e.g. a small
  GPU-vs-CPU comparison could enrich the report. It is **not** automatically the AirLLM path:
  **AirLLM-on-DirectML compatibility is UNKNOWN** (AirLLM expects CUDA-style devices), and a
  full Transformers forward pass + quantization on DirectML is unverified.
- **CPU + AirLLM is confirmed the main path** — Stage 1D (`AIRLLM_FEASIBILITY.md`) evidences
  that AirLLM installs/imports on CPU and exposes `device='cpu'`. Two reasons hold regardless
  of 1C-D: (a) the iGPU's memory is **shared system RAM**,
  so a GPU path does **not** enlarge the "larger-than-memory" budget that AirLLM exists to
  address; (b) the GPU path is Windows-native, separate from the Linux/WSL project toolchain.
- **Backend decision remains formally deferred** (ADR-0010) pending the remaining §5 checks
  (AirLLM CPU mode, AirLLM/DirectML, quantization route). Practical direction: **CPU/AirLLM as
  main path, with Windows-native DirectML available as an optional GPU baseline/extension.**
- A key memory caveat for any future GPU decision: because the iGPU's memory is **shared
  system RAM**, a GPU path would not expand the memory budget that constrains the
  "larger-than-memory" experiment — it would mainly shift *compute*, not *capacity*.

---

*This document records feasibility evidence only. No packages were installed, no model was
chosen, no backend was finalized, and no benchmark was run.*
