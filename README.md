# LectureBridge

LectureBridge is a local-first English live-caption prototype with optional
Vietnamese translation. An iPhone or iPad captures audio in Safari, while an
Ubuntu laptop performs ASR locally.

New to the project? Read the Vietnamese, beginner-friendly walkthrough:
[`docs/lecturebridge-explained-for-a-12-year-old.md`](docs/lecturebridge-explained-for-a-12-year-old.md).

```text
iPhone/iPad microphone -> Tailscale HTTPS -> Faster-Whisper GPU -> English captions
                                                       \-> optional NLLB CPU -> Vietnamese
```

## Current MVP

- One microphone client and one session.
- High-accuracy English transcription with `distil-large-v3.5` by default on
  NVIDIA CUDA.
- English-only by default; optional Vietnamese translation with NLLB-200
  distilled 600M on CPU.
- Browser UI supplied by pinned WhisperLiveKit `0.2.26`.
- Tailnet-only access through Tailscale Serve; Funnel is not used.
- Audio and transcripts are not saved by default.

## Requirements

- Ubuntu with an NVIDIA GPU and a working driver.
- Python 3.12 managed by [`uv`](https://docs.astral.sh/uv/).
- FFmpeg and Tailscale.
- An iPhone or iPad signed into the same tailnet.
- Permission to capture and process the audio source.

## Install and verify

```bash
uv sync
uv run lecturebridge-preflight --peer ipad153
```

Every preflight line must say `PASS`. The first sync downloads several large
CUDA dependencies. Model downloads also require Internet once; inference uses
the local cache afterward.

## Offline baseline

Place a permitted recording at `data/private/english_test_30s.m4a`. The entire
directory and common audio formats are ignored by Git.

```bash
uv run lecturebridge-transcribe data/private/english_test_30s.m4a
uv run lecturebridge-transcribe data/private/english_test_30s.m4a --model distil-large-v3.5
uv run lecturebridge-transcribe data/private/english_test_30s.m4a --model small.en --beam-size 5
```

The command prints timestamped English text, model load time, inference time,
and real-time factor (RTF). Lower RTF is faster; the initial target is `< 0.7`.

## Live captions

```bash
uv run lecturebridge-live
```

Open <http://127.0.0.1:8000> for a local check. For iPhone/iPad use, follow
[`docs/classroom-runbook.md`](docs/classroom-runbook.md).

Fallbacks:

```bash
uv run lecturebridge-live --model small.en
uv run lecturebridge-live --model base.en
uv run lecturebridge-live --model tiny.en
```

Opt in to Vietnamese translation only when needed:

```bash
uv run lecturebridge-live --translation
```

## Development checks

```bash
uv run ruff check .
uv run pytest -q
```

The live CUDA acceptance test is opt-in and requires a permitted audio file:

```bash
LECTUREBRIDGE_DEBATE_AUDIO=/path/to/permitted.wav \
  uv run pytest -q tests/test_debate_stress.py
```

Measured results and known limitations are in
[`docs/test-evidence.md`](docs/test-evidence.md). Third-party model and software
terms are summarized in [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md).

## Privacy

Do not commit classroom recordings, real transcripts, cookies, tokens, `.env`
files, or model weights. Confirm the class recording policy and obtain any
required permission before turning on the microphone.
