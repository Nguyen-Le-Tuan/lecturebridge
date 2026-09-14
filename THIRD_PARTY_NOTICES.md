# Third-party notices

LectureBridge installs and runs third-party software and model weights. This
file is a summary, not a replacement for their license texts or model cards.

## WhisperLiveKit

- Project: <https://github.com/QuentinFuxa/WhisperLiveKit>
- License: Apache License 2.0
- Role: streaming ASR server, WebSocket protocol, and bundled web UI

## Faster-Whisper and CTranslate2

- Projects: <https://github.com/SYSTRAN/faster-whisper> and
  <https://github.com/OpenNMT/CTranslate2>
- Role: local Whisper inference and optimized model execution
- Their own repositories and installed distributions contain the authoritative
  license terms.

## NLLB-200 distilled 600M

- Model: <https://huggingface.co/facebook/nllb-200-distilled-600M>
- Model weights license: CC-BY-NC-4.0
- Role: English-to-Vietnamese translation through NLLW/WhisperLiveKit

The NLLB weights are restricted to non-commercial use. Do not describe this
MVP as commercially licensed, and review the current model card and license
before any distribution or commercial deployment.
