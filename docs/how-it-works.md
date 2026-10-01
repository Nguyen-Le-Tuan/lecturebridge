# How LectureBridge works

LectureBridge turns microphone audio into captions on a web page. The browser
captures sound; a Windows or Ubuntu computer runs the speech model and sends
text back. If you enable translation, a second model translates that text into
Vietnamese.

```text
Browser microphone → LectureBridge server → Whisper → source transcript
                                               └──→ NLLB → Vietnamese
```

The browser and server can run on the same computer. A phone or tablet can also
connect to the computer through Tailscale HTTPS. In that setup, the computer
still does the recognition and translation work.

## From sound to text

After you allow microphone access, the browser sends small chunks of audio
through a WebSocket connection. An AudioWorklet converts the audio to mono,
16-bit PCM at 16,000 samples per second. Sending chunks lets captions appear
while you're still speaking.

The server uses WhisperLiveKit's streaming processor and Faster-Whisper for
speech recognition. The model considers incoming speech in context, so an
unfinished caption may change as more audio arrives. Once text is committed,
the app adds it to the transcript. This delay between a provisional caption and
a committed paragraph is part of how streaming recognition works.

## Models and hardware

A model is the downloaded data the recognizer uses to turn speech into text.
Larger models generally need more memory and processing time. Whether they
produce better captions depends on the recording, language, accent, and noise.
The [model guide](models.md) lists the supported options.

An NVIDIA GPU can accelerate speech recognition. CPU mode uses the computer's
main processor and may fall behind live speech. Install starts with a small
model so you can check the application before comparing larger ones.

Python and the application libraries live in `.venv`; the installer keeps its
own tools under `.tools`. `uv.lock` fixes dependency versions. `models.lock.json`
fixes model revisions and file checksums, which are checked after download.
These files keep installations reproducible across computers.

## Translation

Translation is a separate step after speech recognition. An incorrectly
recognized word can therefore also affect the Vietnamese result. When reporting
an error, include the spoken sentence, source transcript, and translation so
it's possible to identify which step went wrong.

NLLB runs in a separate CPU process using two threads. Turning on translation
submits new committed paragraphs. It does not translate the entire earlier
session. Turning it off stops new translation work while keeping the text
already displayed. Preparation and translation may take noticeably longer than
speech recognition.

## Saving a session

Listening and saving are separate controls. With recording off, the session
can display and export text without creating a recording in the library.
With recording on, the server writes audio to a WAV file and stores transcript
metadata in SQLite. The library supports playback, export, rename, and delete.

Recordings live in your user data directory, outside the application folder.
You can find the platform paths in the [README](../README.md#recordings-and-privacy).
A disconnected recording contains only audio that reached the server; it cannot
recover speech captured after the connection was lost.

## Phone and tablet connections

The server listens on `127.0.0.1:8000`, which refers to the computer running it.
Opening that address on an iPad would refer to the iPad itself. Tailscale Serve
provides an HTTPS address that routes the iPad's browser to the computer.
HTTPS also allows the browser to request microphone access.

Follow the [phone/tablet runbook](classroom-runbook.md) for setup. Keep access
restricted: the current app has a shared recording library and no separate
user accounts. The computer must remain on while the phone or tablet uses it.

For protocol, storage, and worker details, see the
[architecture notes](local-studio-architecture.md).
