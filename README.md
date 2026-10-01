# LectureBridge

Local live captions for **English, Mandarin Chinese, Japanese, and Korean**, with
optional translation into **Vietnamese**. Run it on your Windows or Ubuntu
computer and use its microphone in a browser. An iPhone or iPad can also connect
through Tailscale HTTPS.

This is an early testing build. Speech and translation can be inaccurate;
translation may lag by tens of seconds. Recordings are **off by default**.

## Install on a new computer

You do **not** need to install Git, Python, CUDA Toolkit, or Python libraries
manually. Ask the project owner for the Windows ZIP or Ubuntu archive built
from `main`. GitHub Actions also provides them under **CI → a successful run →
Artifacts → lecturebridge-installers**. This repository is private: recipients
can use a bundle shared by the owner without a GitHub account.

| Windows 10/11 x86-64 | Ubuntu 22.04/24.04 x86-64 |
| --- | --- |
| Extract the entire `*-windows-x64.zip` into a permanent folder you can write to. | Extract the entire `*-ubuntu-x64.tar.gz` into a permanent folder you can write to. |
| Double-click **Install.cmd**. | Open a terminal in the extracted folder and run **`bash Install.sh`**. |
| Choose the spoken language and wait for “Setup complete”. | Choose the spoken language and wait for “Setup complete”. |
| Double-click **Start.cmd**. | Run **`bash Start.sh`**. |

The browser opens at [localhost:8000](http://127.0.0.1:8000) when the server is
ready. Allow microphone access, then start a short session. Keep the terminal
window open. Stop the session in the app and press **Ctrl+C** in the terminal
to shut down the server. Run only one instance at a time.

**Requirements:** internet during setup and first translation download, at least
4 GB RAM and 20 GB free space on the installation drive. Keep at least 2 GB free
on the model-cache drive for initial ASR downloads; translation needs another
approximately 2.5 GB. Recordings and extra models need additional space. Setup
may download several GB of Python dependencies and runtime libraries.

The installer:

- Checks OS, CPU architecture, RAM, disk space, and GPU 0's reported memory,
  driver, and temperature. It does not benchmark or load models during installation.
- Downloads checksum-verified **uv 0.12.13**, managed **Python 3.12**, locked
  application dependencies, and checksum-verified ASR weights.
- Installs the Microsoft Visual C++ x64 runtime when needed on Windows (a UAC
  prompt may appear), or missing `curl`, CA certificates, and `libgomp1` on Ubuntu
  (`sudo` may ask for your password).
- Installs private CUDA/cuDNN runtime libraries for an eligible NVIDIA GPU on
  Windows. Linux dependencies already include these runtime libraries.
- Uses CPU if the NVIDIA driver/runtime is unavailable. It does **not** install
  or update GPU drivers, change system PATH, or automatically restart the computer.
- Saves its choices in `.lecturebridge/install.json` and setup output in
  `.lecturebridge/setup.log`. A failed installation cannot be launched as ready;
  rerun Install after resolving the reported problem.

Keep the extracted folder in place. Do not copy `.venv` or `.tools` between
computers or operating systems. An update is a new bundle in a separate folder,
followed by Install; the recording library remains in your user data directory.
The bundles are online bootstrap installers, not offline or signed `.exe` packages.

### Automatic starting model

All automatic choices use multilingual models, so any supported source language
can be selected. These are conservative heuristics, not speed or stability guarantees.

| Detected configuration | Starting choice |
| --- | --- |
| GPU 0 has at least 6 GiB total VRAM, 4 GiB free, and system RAM is at least 16 GiB | `small` / CUDA |
| GPU 0 has at least 4 GiB total VRAM, 2 GiB free, and system RAM is at least 8 GiB | `base` / CUDA |
| Other eligible NVIDIA GPU with at least 2 GiB free VRAM | `tiny` / CUDA |
| Missing driver, unsupported GPU, warm/busy GPU, or explicitly selected CPU | `tiny` / CPU |

GPU selection also requires a reported temperature no higher than 65°C. On the
first Start, and after a GPU/driver change, the launcher runs a **tiny-only**
check on one second of silence. It stops at 60 seconds, 75°C, or less than
1024 MiB free VRAM. A failed check selects `tiny` on CPU for that session.
This reduces exposure but cannot prevent driver, power, or OS crashes. The
live server itself has **no thermal watchdog**; keep the first session short.

To force the smallest model or CPU, run one of these from the extracted folder:

```powershell
# Windows PowerShell: choose ONE installation profile.
.\Install.cmd -Profile safe -Language zh
.\Install.cmd -Profile cpu -Language zh
```

```bash
# Ubuntu: choose ONE installation profile.
bash Install.sh --profile safe --language zh
bash Install.sh --profile cpu --language zh
```

`safe` selects `tiny` and still allows GPU; `cpu` avoids GPU inference entirely.
To skip the language menu, add `-NonInteractive` on Windows or `--non-interactive`
on Ubuntu. System administrator prompts and the Windows wrapper's closing
pause may still require interaction.

## Use the studio

The app's interface is currently Vietnamese; this README and installer messages
are English. The main controls provide:

- Original, Vietnamese, or bilingual display while the microphone keeps running.
- Light/dark themes and adjustable text size.
- An optional **Save recording** switch before each session. It saves WAV audio
  and committed text locally, and resets to off after the session.
- A recording library with playback, approximate segment seeking, rename,
  TXT/JSON export, WAV download, and delete.
- Temporary transcript export even when recording is off.

Select Vietnamese or bilingual mode and approve the in-app download to prepare
translation. NLLB downloads approximately **2.5 GB**, runs on CPU with two
threads, and translates new committed text only. A faster GPU does not directly
accelerate this translation worker. Its weights are **non-commercial**.

There is one active microphone session per server and a two-hour session limit.
Keep Safari in the foreground. Automatic reconnect/resume is not included.
If recording was enabled, received audio is retained after a disconnect.

Recordings are stored in `%LOCALAPPDATA%\LectureBridge` on Windows and
`${XDG_DATA_HOME:-~/.local/share}/lecturebridge` on Linux. They remain until you
delete them. Dual-boot systems do not automatically share libraries. Removing
an installation folder does not delete recordings or the Hugging Face model
cache (`~/.cache/huggingface` by default).

### Spoken languages

| Language | Launch option | Suitable ASR models |
| --- | --- | --- |
| English | `--language en` | All models below |
| Mandarin Chinese, Simplified translation source | `--language zh` | Multilingual models only |
| Mandarin Chinese, Traditional translation source | `--language zh-Hant` | Multilingual models only |
| Japanese | `--language ja` | Multilingual models only |
| Korean | `--language ko` | Multilingual models only |

`zh-Hant` uses Whisper's same Mandarin recognizer with the Traditional Chinese
NLLB source token; it does not guarantee Traditional characters in ASR output.
Source-language changes require a server restart. Close the running server,
then start with a language option; the launcher remembers it:

```powershell
.\Start.cmd --language zh
# Other choices: en, zh-Hant, ja, ko
```

```bash
bash Start.sh --language ja
# Other choices: en, zh, zh-Hant, ko
```

Multilingual ASR and translation routing have automated coverage. Actual
Chinese/Japanese/Korean transcription and translation quality still require
human acceptance testing.

## Model guide: lightest to largest

Download sizes below are rounded decimal sizes for the pinned model files,
not RAM/VRAM requirements. Faster or larger does not always mean more accurate
for your audio. Start small and change one variable at a time.

| Multilingual model | Parameters | Approx. download | Suggested use |
| --- | ---: | ---: | --- |
| `tiny` | 39 M | 78 MB | First hardware and language-path check |
| `base` | 74 M | 148 MB | Next lightweight comparison |
| `small` | 244 M | 488 MB | Intermediate starting point on stronger GPUs |
| `medium` | 769 M | 1.53 GB | Larger, slower comparison |
| `large-v3-turbo` | 809 M | 1.62 GB | Large model optimized for transcription speed |
| `large-v3` | 1.55 B | 3.09 GB | Largest supported model; highest resource cost |

| English-only model | Approx. download | Suggested use |
| --- | ---: | --- |
| `tiny.en` | 78 MB | Lightest English check |
| `base.en` | 148 MB | Lightweight English baseline |
| `small.en` | 488 MB | Intermediate English option |
| `distil-large-v3.5` | 1.51 GB | Larger English model; advanced CLI default |

The installer deliberately overrides the advanced CLI default with a smaller
multilingual model. `.en` models and `distil-large-v3.5` cannot transcribe Chinese,
Japanese, or Korean in this application.

### Run a different model

Use the installed Python directly; no global `uv` or Python command is needed.
Close Start first. These commands download missing pinned ASR weights, then run
on the selected device. **Each line starts a server: choose one, do not run them
all.** Manual commands do not perform the launcher's bounded GPU check.

Windows PowerShell:

```powershell
.\.venv\Scripts\python.exe -m lecturebridge.live --device cuda --model tiny --language zh
.\.venv\Scripts\python.exe -m lecturebridge.live --device cuda --model base --language zh
.\.venv\Scripts\python.exe -m lecturebridge.live --device cuda --model small --language zh
.\.venv\Scripts\python.exe -m lecturebridge.live --device cuda --model medium --language zh
.\.venv\Scripts\python.exe -m lecturebridge.live --device cuda --model large-v3-turbo --language zh
.\.venv\Scripts\python.exe -m lecturebridge.live --device cuda --model large-v3 --language zh
```

Ubuntu:

```bash
.venv/bin/python -m lecturebridge.live --device cuda --model tiny --language zh
.venv/bin/python -m lecturebridge.live --device cuda --model base --language zh
.venv/bin/python -m lecturebridge.live --device cuda --model small --language zh
.venv/bin/python -m lecturebridge.live --device cuda --model medium --language zh
.venv/bin/python -m lecturebridge.live --device cuda --model large-v3-turbo --language zh
.venv/bin/python -m lecturebridge.live --device cuda --model large-v3 --language zh
```

Replace `zh` with `ja`, `ko`, `zh-Hant`, or `en` as needed. For English-only
models, use these combinations with the same command prefix:

```text
-m lecturebridge.live --device cuda --model tiny.en --language en
-m lecturebridge.live --device cuda --model base.en --language en
-m lecturebridge.live --device cuda --model small.en --language en
-m lecturebridge.live --device cuda --model distil-large-v3.5 --language en
```

`--device cuda` requires a working CUDA runtime. Use `--device cpu --model tiny`
for a CPU baseline. `--device auto` falls back to CPU when runtime prerequisites
are missing; it cannot guarantee recovery from a later CUDA execution error.
Do not use `download --all` for a first installation.

## Short acceptance check

1. Run Install and save `.lecturebridge/setup.log`. Confirm the selected model,
   device, source language, and “Setup complete”.
2. Run Start. If GPU was selected, record whether its tiny check passed or CPU
   fallback was used. Confirm the browser and microphone work.
3. Speak for 15–30 seconds in the selected language, without translation first.
   Compare the transcript with what you said and note caption latency.
4. Enable translation in a separate short session. Note translation quality,
   delay, missing text, or repeated text independently of ASR performance.
5. Enable recording for a short session, stop, replay it, seek, export TXT/JSON
   and WAV, rename, and delete. Repeat with recording off to check privacy.
6. Restart and confirm the library persists. Record OS, CPU/GPU/RAM, driver,
   model, language, and the commit from `BUILD_INFO.json` with your results.

To rerun only the bounded GPU check manually (after Install):

```powershell
.\.venv\Scripts\python.exe scripts/gpu-smoke.py --model tiny --language zh
```

```bash
.venv/bin/python scripts/gpu-smoke.py --model tiny --language zh
```

The script accepts only `tiny` or `tiny.en`, never a larger model. Passing this
check does not validate sustained use or another model. While testing live GPU
inference, you can monitor in another terminal:

```text
nvidia-smi --id=0 --query-gpu=temperature.gpu,memory.used,memory.free,utilization.gpu --format=csv -l 1
```

Stop the session and press Ctrl+C if temperature reaches 75°C, free VRAM drops
below 1024 MiB, or the computer becomes unresponsive. These conservative test
thresholds are not a guarantee against crashes.

## Phone or tablet access

Local computer use requires no Tailscale account. For an iPhone/iPad, install
and sign in to Tailscale on both devices, then follow the
[classroom runbook](docs/classroom-runbook.md) to enable tailnet-only HTTPS.
Tailscale sign-in and access policy remain explicit owner actions. Do not use
Funnel or expose port 8000 publicly. Anyone allowed to reach this trusted
instance can access its recording library; there are no separate user accounts.

## Troubleshooting and advanced setup

- [Windows setup and recovery](docs/setup-windows.md)
- [Ubuntu setup and recovery](docs/setup-linux.md)
- [Runtime troubleshooting](docs/troubleshooting.md)

If setup fails, read its final error and `.lecturebridge/setup.log`; rerunning
Install reuses valid downloads. Proxy restrictions, antivirus policy, a denied
administrator prompt, or an incompatible driver can still require intervention.
Review logs before sharing them because they can contain local paths.

Read-only local checks and offline transcription, using the installed Python:

```powershell
.\.venv\Scripts\python.exe -m lecturebridge.preflight --local-only --device cpu --model tiny --language en
.\.venv\Scripts\python.exe -m lecturebridge.offline path\to\permitted.wav --device cpu --model tiny --language en
```

```bash
.venv/bin/python -m lecturebridge.preflight --local-only --device cpu --model tiny --language en
.venv/bin/python -m lecturebridge.offline /path/to/permitted.wav --device cpu --model tiny --language en
```

Use the same model/language/device as your current launch when checking an
already-running server. Preflight is shallow unless `--deep` is explicitly
supplied; `--deep` loads and executes the model. Prefer the bounded tiny script
for initial GPU verification.

## Development and packaging

Developers with Git and uv can clone `main` and run:

```bash
uv sync --locked
uv run ruff check .
uv run pytest -q -m "not gpu"
node --test tests/test_worklet.cjs
uv build
uv run python scripts/check_repository.py
uv run python scripts/build_installers.py --ref HEAD
```

On Windows, use `uv sync --locked --extra windows-cuda` if GPU runtime libraries
are needed. The compatibility scripts under `scripts/bootstrap-*` delegate to
the new installer.

The packaging command creates Windows/Ubuntu archives and `SHA256SUMS.txt` under
`dist/installers`. It reads an allowlist from the specified **committed Git tree**,
not uncommitted work. It excludes Git history, local reports, recordings,
secrets, environments, and model weights. CI publishes the bundles only after
Windows and Ubuntu tests pass. Each archive contains `BUILD_INFO.json`.

GPU tests are opt-in and excluded from normal CI. Automated installer tests use
mocked hardware/downloads; a successful CI run does not replace a fresh-machine
installation and human audio-quality check. Do not run stress tests for initial
acceptance.

## Privacy and licenses

Obtain permission to record the audio source. Do not commit recordings,
transcripts, tokens, cookies, `.env` files, or model weights. Audio and saved
transcripts are processed locally; setup/model downloads contact external
package and model hosts. One microphone cannot reliably separate overlapping
speech, and captions are not an authoritative transcript.

Project source and documentation use the [MIT License](LICENSE). Dependencies
and model weights retain their own terms; see [third-party notices](THIRD_PARTY_NOTICES.md).
Optional NLLB weights use **CC-BY-NC-4.0** and are not licensed for commercial use.
