# Hardware Evidence — Stage 1A/1B Intake

> **STATUS: Stage 1A/1B hardware intake — NOT benchmark results.** This document records the
> *real* machine facts collected from the terminal so model selection (Stage 2) can proceed
> without inventing anything. No performance numbers are claimed here. Every fact below is
> backed by a quoted command output; where a tool was unavailable, that is stated plainly
> rather than guessed.

- **Stage 1A collection (WSL-side):** 2026-06-19 14:23 UTC — read-only probes inside Ubuntu.
- **Stage 1B collection (host-side):** 2026-06-19 — Windows PowerShell via `powershell.exe`.
- **Project path probed:** `/home/awad_moha/ex05-airllm`

---

## 0. Evidence boundary (read this first)

There are **three distinct layers**, and conflating them would be a measurement error:

1. **Physical Windows host** — what the laptop actually contains (§A below). Collected with
   PowerShell/CIM. Larger than what the experiment can use.
2. **Ubuntu WSL2 execution environment** — the Linux VM the experiment runs in (§1–§6).
   A *subset* of the host: RAM is capped, devices are virtualized/paravirtualized.
3. **Resources actually available to the experiment** — the intersection that the model and
   benchmarks can truly rely on (§B below). **This is what model selection is calibrated to.**

> Rule applied throughout: a capability counts as *available to the experiment* **only** if
> it is evidenced **inside Ubuntu WSL2**, not merely present on the Windows host.

---

## A. Physical Windows host evidence (Stage 1B)

Collected via `powershell.exe -NoProfile -Command "Get-CimInstance …"`. Model/part strings
are component identifiers, not serial numbers; no serial numbers are recorded.

```
Win32_OperatingSystem → Caption: Microsoft Windows 11 Pro
                        Version: 10.0.26200   BuildNumber: 26200   OSArchitecture: 64-bit
Win32_ComputerSystem  → Manufacturer: ASUSTeK COMPUTER INC.
                        Model: ASUS Vivobook S 14 M5406WA
                        TotalPhysicalMemory: 24,823,836,672 bytes  (≈ 23.12 GiB ≈ 24 GB)
Win32_Processor       → Name: AMD Ryzen AI 9 HX 370 w/ Radeon 890M
                        NumberOfCores: 12   NumberOfLogicalProcessors: 24   MaxClockSpeed: 2000 MHz
Win32_VideoController → Name: AMD Radeon(TM) 890M Graphics
                        DriverVersion: 32.0.13022.3006   VideoProcessor: AMD Radeon Graphics (0x150E)
                        AdapterRAM: 536,870,912 bytes (512 MB reported; iGPU shares system RAM)
Win32_DiskDrive       → Model: MTFDKBA1T0QFM-1BD1AABGB   InterfaceType: SCSI
                        MediaType: "Fixed hard disk media"   Size: ~1,024,203,640,320 bytes
Get-PhysicalDisk      → FriendlyName: MTFDKBA1T0QFM-1BD1AABGB
                        MediaType: SSD   BusType: NVMe   Size: ~1 TB
wsl.exe --status      → Default Distribution: Ubuntu   Default Version: 2
nvidia-smi.exe        → command not found  (no NVIDIA GPU on host)
```

**Host facts:**
- **Host OS:** Windows 11 Pro 10.0.26200 (build 26200), 64-bit.
- **Machine:** ASUS Vivobook S 14 (M5406WA), ASUSTeK.
- **Host CPU:** AMD Ryzen AI 9 HX 370 — 12 cores / 24 logical, base ~2.0 GHz.
- **Host RAM:** ≈ **24 GB** (23.12 GiB) physical.
- **Host GPU:** **AMD Radeon 890M** integrated graphics (driver 32.0.13022.3006). **No
  NVIDIA GPU** (`nvidia-smi.exe` absent). The 512 MB `AdapterRAM` is a reported allocation;
  an iGPU shares system RAM rather than having large dedicated VRAM.
- **Host disk:** Micron **NVMe SSD** (~1 TB) — `Get-PhysicalDisk` reports `MediaType: SSD`,
  `BusType: NVMe`. (`Win32_DiskDrive`'s generic "Fixed hard disk media"/"SCSI" is a WMI
  quirk; the authoritative answer is NVMe SSD.)
- **WSL:** default distro Ubuntu, **Version 2** (confirms WSL2).

> **GPU availability note (per the no-overclaim rule):** *Host GPU is detected by Windows,
> but CUDA/ROCm compute availability inside Ubuntu WSL2 is **not** evidenced.* It is an **AMD
> integrated GPU**, so there is no CUDA path by definition, and ROCm for Radeon iGPUs under
> WSL2 is not available/evidenced here (see §4). Therefore the host GPU is **not** counted as
> an experiment compute resource.

---

# Ubuntu WSL2 execution environment evidence (Stage 1A)

> Sections §1–§6 below describe the **Linux VM the experiment runs in** — a subset of the
> host above. These are the resources the code actually sees.

## 1. Operating system & kernel

```
$ uname -a
Linux mohamed-awad 6.6.87.2-microsoft-standard-WSL2 #1 SMP PREEMPT_DYNAMIC ... x86_64 GNU/Linux

$ lsb_release -a
Distributor ID: Ubuntu
Description:    Ubuntu 24.04.4 LTS
Release:       24.04
Codename:      noble
```

- **OS:** Ubuntu 24.04.4 LTS ("noble").
- **Kernel:** `6.6.87.2-microsoft-standard-WSL2` → this is **WSL2** (a Linux VM under a
  Windows host), not bare-metal Linux. `/etc/wsl.conf` confirms `systemd=true`.
- **Architecture:** `x86_64`.

> **Why this matters:** WSL2 runs as a lightweight VM. Memory is capped below the physical
> host total (see §3), and devices (GPU, disk) are virtualized/paravirtualized. This shapes
> every downstream constraint.

## 2. CPU

```
$ lscpu  (key lines)
Model name:          AMD Ryzen AI 9 HX 370 w/ Radeon 890M
Vendor ID:           AuthenticAMD
CPU(s):              24
Thread(s) per core:  2
Core(s) per socket:  12
Socket(s):           1
Virtualization:      AMD-V   Hypervisor vendor: Microsoft   Virtualization type: full
Flags (selected):    avx2 avx512f avx512bw avx512vl avx512_bf16 avx_vnni avx512_vnni fma
                     f16c aes sha_ni bmi2 ...
$ nproc → 24
```

- **CPU:** AMD Ryzen AI 9 HX 370 (Zen 5 generation) with integrated **Radeon 890M** iGPU.
- **Topology:** 12 physical cores × 2 threads = **24 logical CPUs**, single socket.
- **Instruction sets relevant to CPU inference:** AVX2, **AVX-512** (incl. `avx512_bf16`,
  `avx512_vnni`), **AVX-VNNI**, FMA, F16C, AES, SHA-NI. These accelerate quantized/bf16 CPU
  matmuls (e.g., llama.cpp / GGUF kernels can exploit AVX-512 + VNNI).

## 3. Memory (RAM & swap)

```
$ free -h
               total   used    free   shared  buff/cache  available
Mem:            11Gi   1.5Gi   9.2Gi  5.5Mi   705Mi       9.7Gi
Swap:          3.0Gi     0B    3.0Gi

$ grep -E "MemTotal|MemAvailable|SwapTotal" /proc/meminfo
MemTotal:     11788444 kB   (≈ 11.24 GiB)
MemAvailable: 10190180 kB   (≈  9.72 GiB)
SwapTotal:     3145728 kB   (=  3.0 GiB)
```

- **Total RAM (as seen by Linux):** ≈ **11.24 GiB** — this is the **WSL2 VM cap**. The
  physical host has **≈ 24 GB** (§A), so WSL2 currently exposes **less than half** of host
  RAM to the experiment.
- **Available at collection time:** ≈ 9.72 GiB.
- **Swap:** 3.0 GiB.

> **This is the single most important constraint.** The "deliberately larger than memory"
> target model must be sized against the **~11 GiB available to the experiment**, not the
> ~24 GB on the host. (The cap can be raised via a Windows-side `.wslconfig` — a user action,
> not assumed here; tracked under R-WSL-MEM.)

## 4. GPU detection (evidence-based)

Multiple probes were used; results are reported exactly, and **no unsupported "no GPU"
claim is made** because `lspci` (PCI enumeration) is not installed.

```
$ nvidia-smi              → command not found
$ ls /proc/driver/nvidia  → no such file or directory   (no NVIDIA kernel driver)
$ rocm-smi                → command not found            (no ROCm tooling)
$ which lspci             → lspci NOT installed          (cannot enumerate PCI devices)
$ ls -l /dev/dxg          → crw-rw-rw- 10,125            (WSL GPU paravirt device PRESENT)
$ glxinfo -B  (renderer)
    OpenGL renderer string: llvmpipe (LLVM 20.1.2, 256 bits)   ← CPU software rasterizer
    OpenGL vendor string:   Mesa
    Dedicated video memory: 0 MB
    Total available memory: 11512 MB (unified = system RAM)
```

**Findings:**
- **No NVIDIA GPU usable:** `nvidia-smi` absent and no `/proc/driver/nvidia` → no CUDA path.
- **No ROCm path:** `rocm-smi` absent.
- **`/dev/dxg` exists:** WSL2's GPU paravirtualization device is present, so the host's
  integrated **Radeon 890M** is *theoretically* reachable via WSL — but no compute stack
  (CUDA/ROCm/HIP) is installed to use it.
- **OpenGL falls back to `llvmpipe`** (a CPU software renderer) with **0 MB dedicated
  VRAM** → there is currently **no hardware-accelerated GPU compute available** in this
  environment.

> **Honest conclusion (reconciled with host evidence §A):** The host **does** have a GPU —
> an **AMD Radeon 890M integrated** adapter, confirmed by Windows (`Win32_VideoController`)
> — and there is **no NVIDIA GPU** anywhere (`nvidia-smi.exe` absent on the host too). But
> *Host GPU is detected by Windows, while CUDA/ROCm compute availability inside Ubuntu WSL2
> is **not** evidenced*: `nvidia-smi`/`rocm-smi` are absent in Ubuntu, OpenGL falls back to
> the `llvmpipe` CPU renderer, and (being an AMD iGPU) there is no CUDA path by definition.
> Therefore the actionable fact for planning is **CPU-only execution** unless a GPU compute
> stack is deliberately installed and evidenced inside WSL2. **No dedicated VRAM is available
> to measure**, so the "peak VRAM" metric is `N/A_WITH_RATIONALE` unless a GPU path is later
> enabled. (`lspci` is absent in Ubuntu, but host-side CIM already enumerates the adapter, so
> the GPU's existence is no longer in doubt — only its *usability for compute inside WSL2*.)

> **GPU usability assessed separately:** see `docs/GPU_FEASIBILITY.md` (Stages 1C-A/1C-B).
> dxdiag confirms the iGPU is DirectX 12_2 capable with ~11.8 GB **shared** (290 MB dedicated)
> memory — it draws from system RAM rather than adding capacity. A Stage 1C-B isolated probe
> **tested Windows-native DirectML** in a throwaway venv: `torch-directml` installs but fails
> to import on the only compatible Windows Python (3.9 needs 3.10+; 3.13 has no wheel), so all
> GPU backends are currently `BLOCKED` on the available toolchain — an evidence-based finding,
> not a hardware limitation. The practical path is **CPU + AirLLM**; the GPU option is
> re-openable if a Python 3.10–3.12 runtime is installed.

## 5. Disk & filesystem

```
$ df -h .
Filesystem  Size  Used  Avail  Use%  Mounted on
/dev/sdd   1007G   24G   933G    3%   /

$ findmnt -T .
TARGET  SOURCE     FSTYPE  OPTIONS
/       /dev/sdd   ext4    rw,relatime,discard,errors=remount-ro,data=ordered

$ lsblk (relevant)
sdd  1T  disk  ext4  /mnt/wslg/distro   MODEL: Virtual Disk
sdc  3G  disk  swap  [SWAP]             MODEL: Virtual Disk
```

- **Filesystem for project path (`/`):** `ext4` on `/dev/sdd`.
- **Free space:** **933 GB free** of 1007 GB (3% used) — ample for large model shards and
  multiple quantized copies.
- **Disk model/type (WSL-side):** reported as **"Virtual Disk"** — a WSL2 virtual disk
  (VHDX) abstraction. The underlying physical media type is not discoverable *from inside
  WSL2*.
- **Disk model/type (host-side, now evidenced §A):** the WSL VHDX is backed by a Micron
  **NVMe SSD** (`Get-PhysicalDisk` → `MediaType: SSD`, `BusType: NVMe`, ~1 TB). This is good
  news for AirLLM's layer-streaming pattern.

> **Risk note (I/O) — no overclaim:** Knowing the host disk is an NVMe SSD does **not** let
> us claim a particular per-token I/O speed. AirLLM streams each transformer layer from disk
> on every forward pass, and the WSL2 VHDX / 9p translation layer adds overhead between the
> ext4 view and the physical NVMe. **Actual I/O throughput/latency must still be measured**
> during the experiment and attributed from data, not assumed from the media type (see
> `RISKS.md` R-IO, R-WSL-DISK).

## 6. Python & uv availability

```
$ python3 --version → Python 3.12.3
$ which uv          → /home/awad_moha/.local/bin/uv
$ uv --version      → uv 0.11.9 (x86_64-unknown-linux-gnu)
```

- **Python 3.12.3** present (system).
- **`uv` 0.11.9** installed and on PATH → the required package manager is available for
  Stage 2 (no dependencies installed yet in this stage).

---

## B. Experiment resource availability (the intersection that actually matters)

This is the reconciliation of §A (host) and §1–§6 (WSL): **what the experiment can rely on.**

| Resource | Physical host (§A) | Available to experiment (WSL2) | Verdict for the experiment |
| --- | --- | --- | --- |
| **CPU** | Ryzen AI 9 HX 370, 24 threads | 24 threads exposed, AVX-512/VNNI | ✅ Full CPU usable — primary compute |
| **RAM** | ≈ 24 GB | ≈ **11.24 GiB** (WSL2 cap) + 3 GiB swap | ⚠️ **~11 GiB is the working budget** |
| **GPU compute** | AMD Radeon 890M iGPU (no NVIDIA) | none (no CUDA/ROCm; `llvmpipe`) | ❌ **CPU-only**; host GPU not usable for compute in WSL2 |
| **VRAM** | iGPU shares system RAM | 0 MB dedicated, none measurable | ❌ peak-VRAM metric `N/A_WITH_RATIONALE` |
| **Disk capacity** | ~1 TB NVMe SSD | 933 GB free ext4 on WSL VHDX | ✅ Ample for shards/quantized copies |
| **Disk speed** | NVMe SSD (fast media) | ext4-over-VHDX (overhead unknown) | ⚠️ Fast media, but **must be benchmarked** |
| **Tooling** | — | Python 3.12.3, `uv` 0.11.9 | ✅ Ready for Stage 2 |

**One-line summary:** the experiment runs **CPU-only within ~11 GiB RAM**, backed by an
NVMe-SSD-hosted disk of ~933 GB free; the host iGPU exists but **no GPU-compute backend is
usable inside WSL2** (feasibility under review — `GPU_FEASIBILITY.md`).

## 7. Consequences for model selection (constraints, not choices)

> No model is selected here. These are the boundaries the Stage 2 selection must respect,
> derived from §B (experiment-available resources), **not** from the larger host specs.

- **Baseline constraints:** With ~11 GiB RAM and CPU-only execution, a full-precision
  (FP16) 7–8B model (~14–16 GB weights) will **not** fit in RAM and is expected to OOM or
  thrash into swap — which is exactly the kind of *direct-baseline failure/slowdown* the
  assignment asks us to document. A small quantized model (e.g., a 3–4 GB GGUF Q4 via
  Ollama) is the realistic CPU baseline that actually runs.
- **AirLLM constraints:** AirLLM's layer-wise loading is the mechanism that lets a model
  **larger than 11 GiB** run by keeping only one layer resident. The 933 GB free disk
  easily holds even a 70B-class model's shards. Expect **slow, I/O-bound** execution on
  CPU — acceptable and reportable.
- **Quantization constraints:** AirLLM's built-in 4-bit/8-bit *compression* path uses
  `bitsandbytes`, which typically **requires CUDA** — likely unavailable here. On a
  CPU-only path the practical quantization route is **GGUF (Q4/Q8) via llama.cpp/Ollama**.
  Reconciling "AirLLM + quantization" on CPU is an **open design question for Stage 2**
  (tracked as R-QUANT-CPU), not something to assume now.
- **Disk / I-O concerns:** Host media is now known to be an **NVMe SSD** (§A) — favorable —
  but it is reached through the WSL2 VHDX/9p layer, so per-token latency under AirLLM is
  still uncertain until measured; treat I/O as a primary suspected bottleneck.
- **Compute character (preview, to be proven):** CPU-only inference with AVX-512/VNNI; the
  Prefill phase is expected compute-bound while AirLLM Decode is expected I/O/memory-bound —
  to be **demonstrated with measurements**, not asserted.

## 8. Remaining user-provided values (still required)

These cannot be measured from the terminal and must be supplied by the user. They do **not**
block Stage 2 model *selection* (which depends only on the hardware above), but several are
needed for the Stage 6 cost model.

| value | status | note |
| --- | --- | --- |
| Group code | **NEEDED_USER_INPUT** | required submission metadata |
| GitHub repo URL | **PROVIDED** | `https://github.com/mohammedawad99/ex05-airllm` (remote `origin`, `main` tracked) |
| Hugging Face account / access confirmation | **NEEDED_USER_INPUT** | confirm access **without storing any token in the repo** (env var / interactive login only) |
| Electricity tariff (cost model) | **NEEDED_USER_INPUT** | price per kWh for OPEX in `COSTS.md`; region-dependent |
| Hardware cost / depreciation assumption | **NEEDED_USER_INPUT** | for CAPEX amortization in the break-even analysis |

---

## Provenance

All facts above come from read-only probes run on 2026-06-19: Stage 1A inside Ubuntu WSL2,
Stage 1B from Windows via `powershell.exe`/CIM. Tools that were **not** available
(`nvidia-smi`, `rocm-smi`, `lspci`, `vulkaninfo` in Ubuntu; `nvidia-smi.exe` on the host) are
reported as absent rather than substituted with assumptions. Only component model/part
identifiers are recorded — **no serial numbers** are stored even where command output may
have exposed them. This document is hardware *evidence*; it contains no experiment results
and selects no model.
