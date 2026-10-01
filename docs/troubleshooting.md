# Troubleshooting

## Setup stopped or a download failed

Read the final error and `.lecturebridge/setup.log`, check internet access/free
space, then run Install again. Downloads are verified; never skip a checksum
failure or manually mark an incomplete setup ready. Use a permanent writable
local folder. Do not copy `.venv` from another computer or OS.

## Windows requests administrator permission or a restart

The Microsoft Visual C++ runtime requires administrator approval when missing.
Its installer signature is verified before execution. If it requests a restart,
LectureBridge stops setup; restart yourself and rerun Install. No automatic
reboot or GPU driver installation is performed.

## No NVIDIA GPU or missing CUDA DLLs

CPU-only computers are supported. Select `-Profile cpu` in Windows Install or
`--profile cpu` in Ubuntu Install to use multilingual `tiny` on CPU.

For GPU use, rerun the installer while the GPU is idle and cool. Eligible
Windows installations receive private cuBLAS/cuDNN wheels; the app locates their
DLLs without system PATH changes. A manually managed developer environment
needs `uv sync --locked --extra windows-cuda` on Windows. A working NVIDIA
display driver is still required. `nvidia-smi` alone does not prove CUDA
execution works; the Start launcher uses a bounded tiny check before its first
GPU launch. A failed check falls back to CPU for that session.

Linux runtime packages are part of the locked dependencies. The app adds their
library paths to the child process before using CUDA. Rerun Install to restore missing application libraries.

## Model verification fails

Rerun Install to download and verify the selected ASR model. Advanced users can
use the installed Python with `-m lecturebridge.model_store download --model tiny`
(or the affected model name). Repository revisions, file sizes, and SHA-256
checksums are pinned in `models.lock.json`. Do not edit cached model files.

## GPU memory pressure or slow CPU

Stop the server first. Try multilingual `small`, then `base`, then `tiny`; for
a CPU baseline rerun Install with the CPU profile. Start with 15–30 seconds of
speech and translation disabled. Do not run a large-model stress test as a
recovery step. The live server has no thermal watchdog.

CPU mode may fall behind live speech, particularly with larger models.
NLLB translation runs on CPU independently of the ASR device, so a faster GPU
will not directly fix translation latency. Measure captions and translation
separately.

## Preflight fails only on Tailscale

For use on the same computer, pass `--local-only`. The Install/Start workflow
already does this. For a phone/tablet, sign in to Tailscale on both devices and
follow the [classroom runbook](classroom-runbook.md). Do not expose port 8000
publicly.

## Browser does not open or port 8000 is occupied

Keep the terminal open and read its error. After it reports server startup,
open `http://127.0.0.1:8000` yourself if browser auto-open was unavailable. Close
any previous server before starting a new one. Allow browser microphone access.
For a remote phone/tablet, microphone capture requires the HTTPS tailnet URL.

## Language or translation is wrong

Close the server and rerun Start with `--language en`, `zh`, `zh-Hant`, `ja`, or
`ko`. English-only `.en` and `distil-large-v3.5` models are rejected for other
languages. Use multilingual models for Chinese/Japanese/Korean. Translation
only receives newly committed text after it is enabled; it does not backfill
the entire earlier transcript. The app's UI language remains Vietnamese.
