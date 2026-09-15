# Test evidence

Date: 2026-09-14

## Test machine

- Ubuntu 26.04
- Lenovo IdeaPad Gaming 3 15IAH7
- Intel Core i5-12500H, 16 GB RAM
- NVIDIA GeForce RTX 3050 Laptop GPU, 4096 MiB VRAM
- NVIDIA driver 610.57.04
- Python 3.12.14
- Faster-Whisper 1.2.1
- WhisperLiveKit 0.2.26

## Offline GPU baseline

The permitted private test recording was 83.84 seconds. Its transcript is not
stored in the repository.

| Model | Cold model load | Inference | RTF | Result |
| --- | ---: | ---: | ---: | --- |
| `tiny.en` | 25.00 s | 0.89 s | 0.011 | Pass, no OOM |
| `base.en` | 55.15 s | 1.37 s | 0.016 | Pass, no OOM |
| `small.en` | 62.73 s | 2.61 s | 0.031 | Pass, no OOM |
| `distil-large-v3.5` | 18.21 s | 2.55 s | 0.030 | Pass, ~1080 MiB VRAM; selected default |

The cold-load numbers include first-use download/cache work and are not steady
state. All results are far below the initial RTF target of 0.7.

## Historical translated live smoke test

- WLK health endpoint returned `ready: true`.
- The browser UI rendered at `http://127.0.0.1:8000`.
- Start opened `/asr` and streamed PCM audio through AudioWorklet.
- English and Vietnamese text both appeared.
- Stop completed and the UI reported it was ready to record again.
- Observed live processing lag was approximately 1-2 seconds during the short
  local sample.
- The server process used approximately 3512 MiB VRAM during this test and did
  not OOM.

## Historical translated GPU recovery test

- `small.en` initially caused an OOM when NLLB auto-selected CUDA.
- LectureBridge now forces the CTranslate2 NLLB translator onto CPU and keeps
  Faster-Whisper on CUDA.
- The health endpoint returned `ready: true` with `small.en` and translation.
- A headless WebSocket test streamed the private 83.84-second recording at 4x
  speed and received 222 responses, 213 non-empty updates, nine committed
  lines, a non-empty English transcript, Vietnamese translation, and the final
  `ready_to_stop` signal.
- The live process used approximately 440 MiB VRAM after the completed test and
  did not OOM.

This test documents the earlier translated configuration. Translation is now
opt-in rather than the default.

## Debate English-only feasibility

- `distil-large-v3.5` started successfully through WLK LocalAgreement on the
  RTX 3050 4 GB.
- A 30-second real-time stream produced first text after approximately 0.56
  seconds and completed in 30.39 seconds.
- A permitted sample accelerated to approximately 184 words per minute:
  - produced first text after 0.56 seconds;
  - reached at most 1.8 seconds of processing backlog;
  - reached at most 2.7 seconds of policy/commit backlog;
  - processed 15.01 seconds of audio in 16.59 seconds;
  - produced no translation and completed with `ready_to_stop`.
- The repeatable opt-in GPU acceptance test passed in 22.55 seconds.
- The normal suite currently reports 20 passed and one GPU test skipped unless
  `LECTUREBRIDGE_DEBATE_AUDIO` is supplied.

## Optional translation compatibility

- `distil-large-v3.5` and the CPU-pinned NLLB translator started together
  without OOM.
- A 15.01-second permitted sample streamed at 2x produced non-empty English and
  Vietnamese updates, then the WLK client received `ready_to_stop`.
- This verifies that translation remains available; it is not enabled by the
  default classroom command.

## Still requiring a physical test

- Safari microphone access through the Tailscale HTTPS URL.
- Two-to-five-minute iPad session with useful committed English text and less
  than five seconds of sustained lag.
- Twenty-minute powered soak test.
- Actual debate speech with rapid speaker changes and overlap.
- A human reference transcript for measuring WER; current tests prove
  feasibility and latency, not classroom accuracy.

The MVP is not declared classroom-ready until these checks pass.
