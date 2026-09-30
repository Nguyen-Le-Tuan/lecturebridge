# Windows setup

LectureBridge supports native 64-bit Windows 10 and Windows 11. WSL2 is not
required. NVIDIA GPU inference uses the Windows CTranslate2 wheel with CUDA 12
and cuDNN 9; AMD and Intel GPUs use the CPU fallback in this release.

## 1. Install prerequisites

Install:

1. Git for Windows.
2. The latest compatible NVIDIA display driver.
3. NVIDIA CUDA Toolkit 12.x.
4. NVIDIA cuDNN 9 for CUDA 12.
5. Microsoft Visual C++ 2015-2022 Redistributable (x64).
6. Tailscale for Windows.

After installing CUDA/cuDNN, open a new PowerShell window and confirm:

```powershell
nvidia-smi
where.exe cublas64_12.dll
where.exe cudnn64_9.dll
where.exe cudnn_ops64_9.dll
```

The three DLLs must be in a directory listed in the system or user `PATH`.
Do not download individual DLLs from unknown sites and do not commit them to
this repository.

## 2. Clone and bootstrap

```powershell
git clone --branch codex/local-studio https://github.com/Nguyen-Le-Tuan/lecturebridge.git
Set-Location lecturebridge
powershell -ExecutionPolicy Bypass -File .\scripts\bootstrap-windows.ps1
```

The script installs `uv` for the current user when necessary, creates `.venv`,
syncs the locked Windows dependencies, downloads the pinned default model,
verifies its SHA-256 checksums, and runs preflight. It does not install or
modify GPU drivers, CUDA, cuDNN, Visual C++, or Tailscale.

If PowerShell cannot find a newly installed program, close the terminal, open
a new one, and rerun the script.

For a conservative first test, follow [the bounded tiny.en check](windows-test-handoff-vi.md).
The following deep preflight uses the larger default model and should wait until
that first test passes.

## 3. Prove GPU inference

```powershell
uv run lecturebridge-preflight --device cuda --deep
```

This must report `PASS` for the NVIDIA GPU and deep model smoke test. If CUDA
was explicitly requested, LectureBridge will never silently fall back to CPU.

## 4. Start locally

```powershell
uv run lecturebridge-live --device auto
```

Open <http://127.0.0.1:8000> on the Windows computer.

For CPU fallback:

```powershell
uv run lecturebridge-live --device cpu --model tiny.en
```

## 5. Enable private mobile access

Open **Windows Terminal (Administrator)** and run:

```powershell
tailscale serve --bg --yes http://127.0.0.1:8000
tailscale serve status
```

Open the resulting `https://...ts.net` URL on an iPhone or iPad signed in to
the same tailnet. Never use Tailscale Funnel for classroom audio.
