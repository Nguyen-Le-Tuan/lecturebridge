# Third-party notices

LectureBridge installs and runs third-party software and model weights. This
file is a summary, not a replacement for their license texts or model cards.

## WhisperLiveKit

- Project: <https://github.com/QuentinFuxa/WhisperLiveKit>
- License: Apache License 2.0
- Role: streaming speech-recognition engine and PCM audio processing

## Faster-Whisper and CTranslate2

- Projects: <https://github.com/SYSTRAN/faster-whisper> and
  <https://github.com/OpenNMT/CTranslate2>
- License: MIT
- Role: local Whisper inference and optimized model execution
- Their own repositories and installed distributions contain the authoritative
  license terms.

## Distil-Whisper Large v3.5

- Model: <https://huggingface.co/distil-whisper/distil-large-v3.5>
- CTranslate2 weights: <https://huggingface.co/distil-whisper/distil-large-v3.5-ct2>
- License: MIT
- Role: English ASR model and advanced CLI default

## NLLB-200 distilled 600M

- Model: <https://huggingface.co/facebook/nllb-200-distilled-600M>
- CTranslate2 conversion:
  <https://huggingface.co/entai2965/nllb-200-distilled-600M-ctranslate2>
- Model weights license: CC-BY-NC-4.0
- Role: optional English/Chinese/Japanese/Korean-to-Vietnamese translation
  through the isolated CPU CTranslate2 worker

The NLLB weights are restricted to non-commercial use. LectureBridge's MIT
license does not grant commercial rights to those weights. Their model card
and license define the permitted uses.

## Multilingual Whisper models

- Original models and size/language reference: <https://github.com/openai/whisper>
- CTranslate2 tiny/base/small/medium/large-v3: <https://huggingface.co/Systran>
- CTranslate2 large-v3-turbo:
  <https://huggingface.co/dropbox-dash/faster-whisper-large-v3-turbo>
- License: MIT, as declared by these model repositories
- Role: original-language ASR; Vietnamese translation is performed separately by NLLB.
- Immutable revisions and file checksums are recorded in both model manifests.
  For the added models, large-file SHA-256 values come from Hugging Face LFS metadata;
  small config/tokenizer/vocabulary files were hashed directly. Every model download
  verifies the actual local files before use.
