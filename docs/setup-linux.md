# Linux setup

LectureBridge supports x86-64 Ubuntu/Linux with Python 3.12. NVIDIA GPU
inference requires a working driver; project dependencies provide the CUDA 12
cuBLAS and cuDNN 9 runtime libraries.

## 1. Install system prerequisites

Install Git, curl, Tailscale, and optionally FFmpeg. FFmpeg is not required for
the default browser PCM path, but it is useful for diagnostics and other audio
inputs. Confirm the NVIDIA driver when GPU inference is expected:

```bash
nvidia-smi
```

Do not install Python packages globally and do not copy `.venv` from another
computer.

## 2. Clone and bootstrap

```bash
git clone --branch codex/local-studio https://github.com/Nguyen-Le-Tuan/lecturebridge.git
cd lecturebridge
bash scripts/bootstrap-linux.sh
```

The script installs `uv` when missing, creates `.venv`, performs a locked
dependency sync, downloads the pinned default model, verifies its SHA-256
checksums, and runs preflight.

If Tailscale has not been authenticated yet, sign in and rerun:

```bash
uv run lecturebridge-preflight --device auto
```

For a conservative first test, follow [the bounded tiny.en check](windows-test-handoff-vi.md).
The following deep preflight uses the larger default model and should wait until
that first test passes.

## 3. Prove GPU inference

`nvidia-smi` only proves that the driver can see the GPU. Run the deep test to
load CTranslate2, cuBLAS, cuDNN, and the model:

```bash
uv run lecturebridge-preflight --device cuda --deep
```

Every required line must report `PASS`. A missing CUDA package is repaired by
rerunning `uv sync --locked`; do not manually copy `.so` files into the repo.

## 4. Start LectureBridge

```bash
uv run lecturebridge-live --device auto
```

Open <http://127.0.0.1:8000>. For a mobile microphone, continue with the
[classroom runbook](classroom-runbook.md).

## CPU-only mode

```bash
uv run lecturebridge-live --device cpu --model tiny.en
```

CPU mode uses `int8`. It is intended as a compatibility fallback and may not
meet real-time latency targets with the default large model.
