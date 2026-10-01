# Installation reference

Install downloads uv 0.12.13, managed Python 3.12, locked application dependencies,
and verified speech-model files. It checks hardware without running a model.
The tools and Python environment stay inside the installation folder; setup
leaves system PATH and GPU drivers unchanged.

## Profiles

| Profile | Behavior |
| --- | --- |
| `auto` | Selects multilingual tiny/base/small using the hardware checks below |
| `safe` | Selects multilingual tiny; GPU is still allowed |
| `cpu` | Selects multilingual tiny on CPU |

The default is `auto`. Windows accepts `-Profile` and `-Language`; Ubuntu accepts
`--profile` and `--language`. To skip the language menu, add `-NonInteractive` on
Windows or `--non-interactive` on Ubuntu. Administrator prompts and the Windows
wrapper's closing pause can still require interaction.

## Automatic model selection

| Reported hardware | Starting choice |
| --- | --- |
| GPU 0: at least 6 GiB total VRAM and 4 GiB free; system RAM at least 16 GiB | `small` / CUDA |
| GPU 0: at least 4 GiB total VRAM and 2 GiB free; system RAM at least 8 GiB | `base` / CUDA |
| Other eligible NVIDIA GPU with at least 2 GiB free VRAM | `tiny` / CUDA |
| GPU unavailable, warm/busy, or CPU profile selected | `tiny` / CPU |

GPU selection also requires a reported temperature of 65°C or lower. These
thresholds choose a starting model; performance still depends on the device and
audio. Start performs a bounded tiny check before the first GPU launch and after
a GPU/driver change. See [Testing LectureBridge](testing.md) for the limits.

## Downloads and local files

uv archives and model files are checked against pinned SHA-256 values. Python
dependencies come from the locked versions in `uv.lock`. Windows installs private
CUDA/cuDNN libraries when GPU is selected; Linux dependencies include those
libraries even for a CPU installation.

| Location | Contents |
| --- | --- |
| `.tools/` | Installer tools and managed Python |
| `.venv/` | Application Python environment |
| `.lecturebridge/install.json` | Selected profile, language, model, and hardware report |
| `.lecturebridge/setup.log` | Output from the latest installation attempt |
| `~/.cache/huggingface` by default | Speech-model cache |

A failed installation blocks Start until Install completes. Fix the reported
problem and rerun Install; valid cached downloads can be reused. Moving or
copying an existing virtual environment between computers is unsupported.
For an update, install the new archive in a separate directory.

Recordings live separately in the user data directory described in the
[README](../README.md#recordings-and-privacy). Removing the installation folder
doesn't remove recordings or shared model caches.

## Check an installation or transcribe a file

Preflight checks the environment, model cache, and local port without loading
a model unless `--deep` is supplied. Use the same model, language, and device
as the server when checking a running instance. `--local-only` skips Tailscale.

Windows PowerShell:

```powershell
.\.venv\Scripts\python.exe -m lecturebridge.preflight --local-only --device cpu --model tiny --language en
.\.venv\Scripts\python.exe -m lecturebridge.offline path\to\permitted.wav --device cpu --model tiny --language en
```

Ubuntu:

```bash
.venv/bin/python -m lecturebridge.preflight --local-only --device cpu --model tiny --language en
.venv/bin/python -m lecturebridge.offline /path/to/permitted.wav --device cpu --model tiny --language en
```

The offline command runs transcription on the specified file. Keep private
recordings and generated transcripts outside Git. For initial GPU verification,
use the bounded tiny script in the [testing guide](testing.md) rather than an
unbounded deep check with a larger model.
