# Test evidence

Date: 2026-09-13

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
| `small.en` | 62.73 s | 2.61 s | 0.031 | Pass, no OOM; selected default |

The cold-load numbers include first-use download/cache work and are not steady
state. Both results are far below the initial RTF target of 0.7.

## Local live smoke test

- WLK health endpoint returned `ready: true`.
- The browser UI rendered at `http://127.0.0.1:8000`.
- Start opened `/asr` and streamed PCM audio through AudioWorklet.
- English and Vietnamese text both appeared.
- Stop completed and the UI reported it was ready to record again.
- Observed live processing lag was approximately 1-2 seconds during the short
  local sample.
- The server process used approximately 3512 MiB VRAM during this test and did
  not OOM.

## Upgraded live smoke test

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

## Still requiring a physical test

- Safari microphone access through the Tailscale HTTPS URL.
- Two-minute iPhone/iPad session with understandable EN and VI.
- Twenty-minute powered soak test.
- Wi-Fi/cellular path representative of the classroom.

The MVP is not declared classroom-ready until these checks pass.
