# Testing LectureBridge

Start with a short session on the computer running the app. Test translation
and phone/tablet access separately so a problem in one part is easier to trace.
Use the [report template](acceptance-report-template.md) to record what happened.
Leave untested items marked `NOT TESTED`; a partial report is useful.

## 1. Install and record the version

Follow the [Windows](setup-windows.md) or [Ubuntu](setup-linux.md) setup guide.
For the lightest GPU starting point, use the `safe` profile. For CPU-only testing,
use `cpu` instead. Run one installation command for the profile you want.

```powershell
.\Install.cmd -Profile safe -Language en
```

```bash
bash Install.sh --profile safe --language en
```

Choose `zh`, `zh-Hant`, `ja`, or `ko` for another source language. Install uses
multilingual models for all five choices. Save the selected model/device,
`.lecturebridge/setup.log`, and the commit in `BUILD_INFO.json`. In a Git clone,
use `git rev-parse --short HEAD` instead.

A successful install confirms that files and prerequisites are present. It does
not measure speech accuracy or sustained performance.

## 2. Start the app

Run `Start.cmd` on Windows or `bash Start.sh` on Ubuntu. Record the actual device
shown in the terminal, including any CPU fallback. The browser should open at
`http://127.0.0.1:8000`; you can open that address yourself if needed.

For a GPU profile, Start checks GPU 0 before the first launch and again after a
GPU/driver change. The check uses `tiny` and one second of silence, with a
60-second limit, a 75°C cutoff, and a minimum of 1024 MiB free VRAM. It won't
start when the reported temperature is above 65°C. A failure selects CPU for
that session. CPU-only testing can skip GPU acceptance entirely.

To rerun just the GPU check after installation, close the server first:

```powershell
.\.venv\Scripts\python.exe scripts/gpu-smoke.py --model tiny --language en
```

```bash
.venv/bin/python scripts/gpu-smoke.py --model tiny --language en
```

Use your chosen language code in place of `en`. The script accepts only `tiny`
or `tiny.en`. For English-only `tiny.en`, download that model separately first;
the guided installer caches multilingual `tiny`.

Look for a passing `Deep model smoke test` line with `executed on cuda`. If it
fails, save the output and use CPU or stop testing until the cause is understood.
There's no need to repeat a crash to produce a report.

The watchdog limits this small check only. **The live server has no thermal
watchdog**, and passing the check doesn't establish that a larger model or long
session will run reliably. You can monitor GPU 0 from another terminal:

```text
nvidia-smi --id=0 --query-gpu=temperature.gpu,memory.used,memory.free,utilization.gpu --format=csv -l 1
```

Stop the session, then press Ctrl+C in the server terminal if temperature reaches
75°C, free VRAM drops below 1024 MiB, or the computer responds poorly. Monitoring
cannot prevent every driver, power, or OS failure.

## 3. Try captions without recording

Allow microphone access. Keep recording and translation off, speak for 15–30
seconds, and stop the session in the browser. Use a few sentences you can compare
against the result. Note first-text delay, missing or repeated words, and whether
the committed transcript remains after stopping.

Check that the recording library has no new entry. Export the temporary transcript
before leaving the page. Verify that Stop releases the microphone.

## 4. Try a saved session

Start a separate short session with recording enabled. After stopping:

1. Find the new entry in the library and play it back.
2. Compare its duration with the captured session and listen for missing or
   distorted audio.
3. Seek in the player and select transcript timestamps. Seeking is approximate
   at paragraph level, not aligned word by word.
4. Download WAV, TXT, and JSON. Check source-language characters and Vietnamese
   accents where applicable.
5. Rename the recording and reload the page. Restart the server and confirm the
   saved recording still appears.
6. Delete the test recording and confirm it is no longer accessible in the library.
7. Check that recording has reset to off for the next session.

Also try the theme, font-size controls, scrolling through older text, and the
button that returns to the newest captions.

## 5. Try translation

Keep the same speech model for this comparison. Select bilingual mode and, if
prompted, approve the translation-model download. Note download/preparation time
separately from translation latency.

After the translator is ready, speak a few more sentences. Check that the
original transcript continues, new committed paragraphs receive Vietnamese
translations, and switching display modes keeps the microphone and transcript
intact. Earlier text shouldn't be translated retroactively. Returning to the
original-language mode stops new translation requests.

Record the time from a committed source sentence to its Vietnamese translation.
NLLB runs on CPU and uses additional RAM; GPU performance alone won't explain
its delay. Include a short permitted example of what you said, the committed
transcript, and its translation when reporting content errors.

## 6. Try a phone or tablet

This step is optional for an initial desktop report. Follow the
[Tailscale runbook](classroom-runbook.md), use the HTTPS address, and keep Safari
in the foreground. Check microphone permission, portrait/landscape layout, and
touch controls. Record the host OS, mobile device/browser version, and whether
the Tailscale connection is direct or relayed, if known.

If a disconnect happens, describe it. The app doesn't automatically reconnect
and join the audio into the previous session. Avoid forced failures on a device
that is already unstable.

## Send the report

Copy the [report template](acceptance-report-template.md) and fill in the parts
you tested. Keep separate entries for different sessions or models. Include
error messages and a short reproduction sequence, with private details removed.
Don't include private classroom audio, tokens, or a full environment-variable dump.

The UI's processing-delay label is not an end-to-end latency measurement.
Manual peak readings are estimates, and a short session is not enough to derive
p95 latency, long-session reliability, or classroom accuracy. Record the
measurement method alongside each number.
