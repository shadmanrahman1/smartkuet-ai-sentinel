# Local CUDA Setup (Optional Acceleration)

This document describes how to enable GPU acceleration for SmartKUET Sentinel on a local Windows machine with an NVIDIA GPU.

> **This step is optional and not required for submission or judging.**
> CPU mode works correctly and all tests pass without CUDA. Only do this if you want faster inference on a local NVIDIA GPU.

---

## Verified Local Setup

The following was verified working on this project's development machine:

```
torch: 2.11.0+cu128
cuda_available: True
GPU: NVIDIA GeForce RTX 3050 Laptop GPU (4 GB VRAM)
CUDA: 12.8
Driver: 581.80 (supports up to CUDA 13.0)
Python: 3.13.5
```

Benchmark result after CUDA install:
```
Approximate FPS: 62.17
Average inference: 11.69 ms
```

---

## CPU Mode (Default — Always Works)

If CUDA is not installed, the project runs with CPU-only PyTorch. No code changes are needed.

```
torch: 2.x.x+cpu
cuda_available: False
FPS: lower (~10–20 FPS typical)
```

To verify CPU mode:
```powershell
.venv\Scripts\python -c "import torch; print(torch.__version__, torch.cuda.is_available())"
```

Expected: `2.x.x+cpu False`

---

## CUDA Install Steps

> ⚠️ Only proceed if you have an NVIDIA GPU with drivers installed.
> Check your driver supports CUDA 12.8: `nvidia-smi` should show CUDA Version >= 12.8.

**Step 1 — Check GPU and driver:**
```powershell
nvidia-smi
```

**Step 2 — Uninstall CPU-only torch:**
```powershell
.venv\Scripts\python -m pip uninstall torch torchvision torchaudio -y
```

**Step 3 — Install CUDA 12.8 torch (keep pip cache on project drive):**
```powershell
.venv\Scripts\python -m pip install torch torchvision torchaudio `
    --index-url https://download.pytorch.org/whl/cu128 `
    --cache-dir .cache\pip
```

> Download size is ~2.75 GB. This will take 10–30 minutes depending on internet speed.

**Step 4 — Verify:**
```powershell
.venv\Scripts\python -c "import torch; print('torch:', torch.__version__); print('cuda:', torch.cuda.is_available()); print('gpu:', torch.cuda.get_device_name(0))"
```

Expected:
```
torch: 2.11.0+cu128
cuda: True
gpu: NVIDIA GeForce RTX 3050 Laptop GPU
```

---

## Rollback to CPU Torch

If CUDA causes issues, roll back to CPU-only torch:

```powershell
.venv\Scripts\python -m pip uninstall torch torchvision torchaudio -y
.venv\Scripts\python -m pip install torch torchvision torchaudio `
    --index-url https://download.pytorch.org/whl/cpu `
    --cache-dir .cache\pip
```

After rollback, run `pytest` to confirm all 46 tests still pass:

```powershell
.venv\Scripts\python -m pytest
```

---

## Important Rules

- **Do NOT commit `.venv/`** — it is in `.gitignore` and must stay local.
- **Do NOT commit `.cache/pip/`** — pip wheels are large binary files.
- **Keep `--cache-dir .cache\pip`** pointed to the project drive, not `C:\Users\...`.
- The `YOLO_DEVICE=auto` setting in `.env` will automatically use the GPU when CUDA is available.
- No code changes are needed to switch between CPU and GPU — the device is selected automatically at startup.
