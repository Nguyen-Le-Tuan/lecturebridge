# LectureBridge

LectureBridge is a local-first English live-caption prototype with optional
Vietnamese translation. An iPhone or iPad captures audio in Safari while a
Linux or Windows x86-64 computer performs inference locally.

```text
iPhone/iPad microphone -> Tailscale HTTPS -> Faster-Whisper -> English captions
                                                   \-> optional NLLB -> Vietnamese
```

The application prefers an NVIDIA GPU and safely falls back to CPU when CUDA
is unavailable. Recordings and transcripts are not saved by default.

## What is included

- High-accuracy English transcription with locked `distil-large-v3.5` weights.
- Smaller `small.en`, `base.en`, and `tiny.en` fallback models.
- Native Ubuntu/Linux and Windows 10/11 x86-64 setup.
- NVIDIA CUDA acceleration or a slower CPU `int8` fallback.
- Optional NLLB-200 distilled 600M translation on CPU.
- Tailnet-only HTTPS through Tailscale Serve; Funnel is not supported.

## Requirements

- A 64-bit Ubuntu/Linux or Windows 10/11 computer.
- Python 3.12 managed by [`uv`](https://docs.astral.sh/uv/).
- Tailscale on the computer and viewing device.
- For GPU inference: an NVIDIA driver, CUDA 12, and cuDNN 9. Linux CUDA
  runtime libraries are installed by the project; Windows libraries must be
  available on `PATH`.
- At least 10 GB free for the environment and default ASR model. Allow about
  13 GB when optional translation is also installed.
- Permission to capture and process the audio source.

## Quick start

Linux:

```bash
git clone https://github.com/Nguyen-Le-Tuan/lecturebridge.git
cd lecturebridge
bash scripts/bootstrap-linux.sh
```

Windows PowerShell:

```powershell
git clone https://github.com/Nguyen-Le-Tuan/lecturebridge.git
Set-Location lecturebridge
powershell -ExecutionPolicy Bypass -File .\scripts\bootstrap-windows.ps1
```

The bootstrap scripts create `.venv`, install the locked dependencies, download
the immutable default model, verify its SHA-256 checksums, and run readiness
checks. Model weights remain outside Git.

Detailed instructions:

- [Linux setup](docs/setup-linux.md)
- [Windows setup](docs/setup-windows.md)
- [Troubleshooting](docs/troubleshooting.md)
- [Classroom runbook](docs/classroom-runbook.md)
- [Public release checklist](docs/release-checklist.md)
- [Original Vietnamese project roadmap](docs/roadmap/lecture-translation-roadmap-vi.pdf)
- [Vietnamese beginner walkthrough](docs/lecturebridge-explained-for-a-12-year-old.md)

### Khởi động nhanh bằng tiếng Việt

Clone repo, chạy script tương ứng với hệ điều hành, rồi kiểm tra dòng
`NVIDIA GPU`. Nếu dòng này là `PASS`, LectureBridge đang dùng GPU; nếu là
`WARN`, chương trình vẫn chạy bằng CPU nhưng chậm hơn. Không copy `.venv` hoặc
model từ máy khác vì các file nhị phân phụ thuộc hệ điều hành.

## Run

Start the local server:

```bash
uv run lecturebridge-live --device auto
```

Open <http://127.0.0.1:8000> for a local check. To use an iPhone or iPad,
configure Tailscale Serve as described in the classroom runbook.

Force a device or choose a smaller model:

```bash
uv run lecturebridge-live --device cuda
uv run lecturebridge-live --device cpu --model tiny.en
```

Download and verify models explicitly:

```bash
uv run lecturebridge-models list
uv run lecturebridge-models download --model small.en
uv run lecturebridge-models verify --model small.en
uv run lecturebridge-models download --translation
```

Translation is opt-in because it downloads a large non-commercial model:

```bash
uv run lecturebridge-live --translation
```

## Offline transcription and verification

Place a permitted recording under `data/private/`; the directory and common
audio formats are ignored by Git.

```bash
uv run lecturebridge-preflight --device auto
uv run lecturebridge-preflight --device cuda --deep
uv run lecturebridge-transcribe data/private/example.m4a --device auto
```

`--deep` loads and executes the model, which catches CUDA/cuDNN problems that
`nvidia-smi` alone cannot detect.

## Development

```bash
uv sync --locked
uv run ruff check .
uv run pytest -q
uv build
uv run python scripts/check_repository.py
```

The live GPU acceptance test is opt-in and requires a permitted audio file:

```bash
LECTUREBRIDGE_DEBATE_AUDIO=/path/to/permitted.wav \
  uv run pytest -q tests/test_debate_stress.py
```

GitHub-hosted CI tests both Linux and Windows CPU-compatible code paths. GPU
acceptance must run manually on trusted NVIDIA hardware.

## Privacy, licenses, and limitations

Do not commit classroom recordings, transcripts, cookies, tokens, `.env`
files, model weights, or generated output. Confirm the recording policy and
obtain permission before enabling the microphone.

One mono microphone cannot reliably recover overlapping speech. Captions may
contain errors and must not be treated as an authoritative transcript.

LectureBridge source and project-owned documentation are licensed under the
[MIT License](LICENSE). Model weights and dependencies retain their own terms;
see [third-party notices](THIRD_PARTY_NOTICES.md). In particular, the optional
NLLB weights are CC-BY-NC-4.0 and are not licensed for commercial use.
