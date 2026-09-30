# Local Studio architecture

`lecturebridge-live` retains runtime/model verification and now starts a
LectureBridge-owned FastAPI app on loopback. `WLKBackend` uses the pinned WLK
engine and its PCM processor. A scoped constructor hook supplies the selected
CUDA/CPU device and compute type because WLK 0.2.26 otherwise uses `auto` for both.
The hook is restored immediately after construction. No site-packages are edited.

The packaged HTML/CSS/JS UI uses one microphone stream and an AudioWorklet to
resample to mono PCM16 at 16 kHz. A 4,000-sample buffer bounds client memory.
`/api/live` accepts a JSON start message, binary PCM frames, translation control
messages and stop. It returns config, transcript snapshots with stable paragraph
IDs, partial text, translation state and completion/error events. `/asr` retains
the existing WLK binary-input/cumulative-output compatibility for external clients.

Audio follows two paths only after explicit recording opt-in: ASR processing and
incremental WAV writes. With saving disabled, no session row or audio file is
created. Committed transcript checkpoints are saved at most once per second;
finalization writes a final checkpoint and status. A crash may lose text since
the last checkpoint or unflushed OS buffers. Startup repairs PCM WAV headers and
marks unfinished recordings interrupted. It cannot recover audio that never
reached the laptop. The recording writer is closed even when the socket is cancelled. Disk operations
finish before their file can be closed, and a process-level lock prevents a second
server from recovering or writing the same library while it is active.

`Library` stores UUID-named WAVs and SQLite metadata outside the repo. List,
playback (HTTP Range), download, export, rename and delete APIs operate only on
validated recording IDs. Playback/delete of an active recording is rejected.
Recording ends at two hours. Disconnects do not resume automatically.

Translation runs in a separate CPU-only Python process, using CTranslate2 int8,
two CPU threads, one worker and bounded decoding. The tokenizer and weights come
from the same verified immutable snapshot; it does not fetch an extra unpinned
Facebook tokenizer. Model preparation is lazy and disk/network work stays off
the event loop. Missing models require explicit download via UI (or the existing
`--translation` startup opt-in). English transcription continues during preparation.

Cumulative committed WLK lines become paragraphs, finalized at punctuation,
line boundaries or a bounded length/time interval. A mode change flushes the
current paragraph and advances the translation epoch: earlier text is never
backfilled. There is a 16-paragraph queue. Overflow or unavailable translation is
shown per paragraph; it never creates an unbounded work backlog. A stop drains
translation for at most five seconds, then marks remaining work untranslated.
A cancelled translation request terminates its worker so a stale reply cannot
be attached to the next paragraph. The CPU model may stay resident between
sessions until server exit; changing to English stops new translation work.

This is a single-owner trusted tailnet app, not an authenticated public service.
Host/origin checks reject cross-site access; there is no CORS wildcard, and CSP,
no-store and no-referrer headers apply. It must not be exposed through Funnel or
an internet-facing reverse proxy. Logs do not intentionally include transcript
content. Model loading/inference is never part of the UI/API test fixtures.

## Lightweight validation

- Python tests inject fake ASR/translation, including recovery and disk failure.
- `node --test tests/test_worklet.cjs` checks 16/44.1/48 kHz conversion and tail flush.
- `tests/ui_server.py` serves a temporary synthetic-only library for browser tests.
- `tests/browser_smoke.py` uses a separately installed Playwright and Chromium,
  disables browser GPU acceleration and supplies a fake microphone. It checks
  desktop/tablet/mobile, translation switching, playback, exports, rename/delete,
  opt-out and denied microphone access. Screenshots stay under ignored `artifacts/`.
- All marked GPU tests require `--run-gpu`. CI explicitly excludes them.
