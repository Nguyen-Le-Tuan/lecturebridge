# Choosing a model

Download sizes below are rounded decimal sizes for the pinned model files,
not RAM/VRAM requirements. Faster or larger does not always mean more accurate
for your audio. Start small and change one variable at a time.

| Multilingual model | Parameters | Approx. download | Suggested use |
| --- | ---: | ---: | --- |
| `tiny` | 39 M | 78 MB | Short first test |
| `base` | 74 M | 148 MB | Lightweight everyday option |
| `small` | 244 M | 488 MB | More detail on a stronger GPU |
| `medium` | 769 M | 1.53 GB | Higher resource use; compare on your own audio |
| `large-v3-turbo` | 809 M | 1.62 GB | Large model optimized for transcription speed |
| `large-v3` | 1.55 B | 3.09 GB | Largest supported model; highest resource cost |

| English-only model | Approx. download | Suggested use |
| --- | ---: | --- |
| `tiny.en` | 78 MB | Lightest English check |
| `base.en` | 148 MB | Lightweight English baseline |
| `small.en` | 488 MB | Intermediate English option |
| `distil-large-v3.5` | 1.51 GB | Larger English model; advanced CLI default |

Install chooses a small multilingual model for the first session. The advanced
CLI defaults to `distil-large-v3.5` when `--model` is omitted. `.en` models and `distil-large-v3.5` cannot transcribe Chinese,
Japanese, or Korean in this application.

### Run a different model

Use the installed Python directly; no global `uv` or Python command is needed.
Close Start first. These commands download missing pinned ASR weights, then run
on the selected device. Choose one command for the model you want to try; each starts its own server. Manual commands do not perform the launcher's bounded GPU check.

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
Each command downloads only the selected model. Downloading every model with
`--all` takes considerably more disk space.

## Before trying a larger model

Start with 15–30 seconds of speech and translation off. Compare the committed
transcript against what you actually said, then stop the server before changing
models. A larger model is worth keeping only if the improvement on your audio
outweighs its delay and resource use.

Use the [testing guide](testing.md) for the bounded tiny GPU check and monitoring
commands. Manual `lecturebridge.live` commands have no thermal watchdog. A tiny
smoke test does not establish that a larger model will run reliably.

Translation uses a separate NLLB model on CPU. Changing the Whisper model changes
speech recognition; it does not directly make the translation worker faster.
