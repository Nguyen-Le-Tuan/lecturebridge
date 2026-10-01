# Windows setup

Download the Windows archive from
[Releases](https://github.com/Nguyen-Le-Tuan/lecturebridge/releases), or use the
archive shared with you. On Windows 10/11 x86-64, extract it completely into a
writable folder and double-click `Install.cmd`.

Install sets up Python and the required libraries. For profile options and
automatic model selection, see the [installation reference](installation.md).
For supported languages and model commands, see the [model guide](models.md).

Setup installs private uv/Python dependencies and, for eligible NVIDIA hardware,
private CUDA/cuDNN libraries. A missing Microsoft Visual C++ x64 runtime is
installed using Microsoft's signed installer; accept its UAC prompt. Setup
stops if Windows requires a restart. Restart yourself, then rerun Install.
GPU drivers are not modified. Missing/incompatible GPU support uses a CPU
starting profile or falls back to CPU after the bounded first-launch check.

Double-click `Start.cmd` after setup. Keep its terminal open while using the
app. To change language, close the server and run in PowerShell:

```powershell
.\Start.cmd --language ko
```

To select a CPU-only installation:

```powershell
.\Install.cmd -Profile cpu -Language ko
```

## Recovery

- Extract before running; do not launch from inside the ZIP viewer.
- Use a normal writable folder, not `Program Files`, a network share, or a
  synchronized folder. Keep the folder in place after installation.
- If a download fails, check connectivity and rerun `Install.cmd`.
- If policy blocks scripts, ask the computer's administrator to approve the
  specific installer. The wrapper uses a process-only execution policy; it does
  not change persistent PowerShell policy.
- On failure, read `.lecturebridge\setup.log`. Start remains blocked until
  setup completes. Do not manually remove the incomplete-install marker.
- If port 8000 is occupied, close the other server first.
- For GPU issues, rerun with `-Profile cpu`. GPU driver updates are handled separately from the application installer.
- To update, extract a new bundle into a separate directory and run Install
  there. Existing recordings in `%LOCALAPPDATA%\LectureBridge` are retained.

Tailscale is needed only for another device to reach the server over HTTPS.
