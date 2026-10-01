# LectureBridge test report

Copy this template for a test run. See the [testing guide](testing.md) for the
steps. Use `PASS`, `FAIL`, `BLOCKED`, or `NOT TESTED`; use `NOT MEASURED` for
missing measurements. Include only tests actually performed.

## Summary

- Date, time, and timezone:
- Release/version and commit (`BUILD_INFO.json`, or `git rev-parse --short HEAD`):
- Installation source: release archive / CI archive / Git clone
- Local code or configuration changes:
- Tested: real application / synthetic fixture / both, recorded separately
- Overall result: usable / problems found / blocked / insufficient evidence
- Most significant problem:
- Any crash, freeze, reboot, or driver reset:
- Last completed step and reason for stopping:

## Environment

| Detail | Value |
| --- | --- |
| Server OS and build/version | |
| CPU | |
| Total RAM / RAM in use before testing | |
| GPU / total VRAM in MiB | |
| NVIDIA driver | |
| Python version in the application environment | |
| Browser and version | |
| Microphone or audio input | |
| Free space on the recording-library drive | |
| Custom `--data-dir`, if used | |
| AC power or battery | |
| Ventilation and other resource-heavy apps | |

Optional read-only GPU information:

```text
nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader
```

Windows Python version: `.\.venv\Scripts\python.exe --version`.
Ubuntu Python version: `.venv/bin/python --version`.

## Installation and launch

| Check | Status | Result or error |
| --- | --- | --- |
| Correct version extracted or checked out | NOT TESTED | |
| Install completed | NOT TESTED | |
| Selected profile, model, device, and language | NOT TESTED | |
| Start opened the server and browser | NOT TESTED | |
| Actual device matches the terminal output | NOT TESTED | |
| CPU fallback, if encountered | NOT TESTED | |

- Exact Install/Start commands:
- Setup log attachment, with personal details removed:
- Developer checks, if run: lint / Python tests / Node tests / package build
- Developer test counts, if available:

## GPU check, if performed

CPU-only testers can leave this section `NOT TESTED`.

- Model and language: tiny / tiny.en; en / zh / zh-Hant / ja / ko
- How started: first Start / manual smoke command
- Model download/verification result:
- Did inference start? yes / no / unknown
- `Deep model smoke test` result:
- Did the output include `executed on cuda`?
- Other preflight warnings/errors:
- Ended normally / watchdog / Ctrl+C / crash / other:
- Exit code, if captured (`$LASTEXITCODE` in PowerShell; `$?` in Bash):
- Approximate total duration:

| Measurement | Before | Highest/lowest observed | After |
| --- | --- | --- | --- |
| GPU temperature, °C | | Highest: | |
| VRAM used, MiB | | Highest: | |
| VRAM free, MiB | | Lowest: | |
| System RAM used, GB | | Highest: | |

```text
Paste relevant smoke output, including any watchdog stop reason.
```

## Session log

Repeat this section for each session. Keep different models and translation
settings in separate entries.

### S01

- Start date/time:
- Exact launch command:
- Requested model/device and actual device from terminal output:
- Source language:
- Real application or synthetic fixture:
- Browser/device displaying the UI:
- Connection: localhost / Tailscale direct / Tailscale relay / unknown
- Display mode and time of any mode change:
- Recording on/off:
- Audio source and permission to use it:
- Accent, speaking speed, microphone distance, and background noise:
- Capture duration:
- Models already cached? Server-ready wait time, if measured:
- Ended by Stop / disconnect / closed page / Ctrl+C / error:

| Measurement | Value | Method |
| --- | --- | --- |
| First spoken sound to first text | | |
| End of sentence to committed paragraph | | |
| Largest processing delay shown in UI | | |
| Stop to session finalized | | |
| Highest observed GPU temperature | | |
| Highest VRAM used / lowest VRAM free | | |
| Highest observed system RAM use | | |

## Functional results

| ID | Expected behavior | Status | Session / observation / evidence |
| --- | --- | --- | --- |
| F01 | Layout and controls fit the screen | NOT TESTED | |
| F02 | Mic permission, Start, and Stop work; Stop releases the mic | NOT TESTED | |
| F03 | Source transcript appears and remains after Stop | NOT TESTED | |
| F04 | Recording off creates no library entry | NOT TESTED | |
| F05 | Temporary transcript can be exported without recording audio | NOT TESTED | |
| F06 | Recording on shows its indicator and creates a saved entry | NOT TESTED | |
| F07 | Playback contains the expected voice and content without unusual gaps/distortion | NOT TESTED | |
| F08 | Audio duration is close to capture duration; record the difference | NOT TESTED | |
| F09 | Player seeking and transcript timestamps reach the approximate passage | NOT TESTED | |
| F10 | WAV/TXT/JSON exports open and preserve source text and Vietnamese accents | NOT TESTED | |
| F11 | Renamed recording persists after page reload and server restart | NOT TESTED | |
| F12 | Deleted test recording is no longer accessible through the UI | NOT TESTED | |
| F13 | Recording resets to off for the next session | NOT TESTED | |
| F14 | Theme and text-size controls work | NOT TESTED | |
| F15 | Reading older text doesn't force scrolling down; return-to-latest works | NOT TESTED | |
| F16 | Missing translation model requires download approval | NOT TESTED | |
| F17 | Switching to bilingual keeps the transcript and microphone running | NOT TESTED | |
| F18 | New text is translated; earlier text isn't backfilled | NOT TESTED | |
| F19 | Original mode stops new translation requests and preserves existing text | NOT TESTED | |
| F20 | iPad microphone works over Tailscale HTTPS; both orientations are usable | NOT TESTED | |

## Content quality

- Session:
- Audio type: self-read sentences / lecture / conversation / other
- What was actually spoken, including any speaking errors:

```text
Two to four sentences that may be shared.
```

- Committed transcript:

```text
Corresponding source transcript.
```

- Vietnamese translation, if tested:

```text
Corresponding translation, or NOT TESTED.
```

- Incorrect words, names, or meaning:
- Missing/repeated sentences or changes after commitment:
- Did captions make the audio easier to follow? Why or why not?

## Translation measurements, if tested

- Session and ASR model:
- Translator already cached / downloaded through the UI / not downloaded:
- Time from enabling translation to ready:
- Time from committed source text to Vietnamese text:
- Source-caption delay before/after enabling translation:
- RAM use before/after; CPU use if observed:
- Queue status, untranslated markers, or error messages:

## Phone/tablet observations, if tested

- Device, OS, and browser versions:
- Server OS:
- Same Wi-Fi or separate networks:
- Tailscale direct / relay / unknown:
- HTTPS used:
- Microphone used:
- Browser kept in foreground with screen on:
- Layout, touch, or permission problems:
- Any incidental screen lock, app switch, or disconnect and what followed:

## Bug report

Repeat this block for each issue.

### B01: Short title

- Severity: crash/freeze / data loss / blocked use / incorrect content / UI issue
- Session and time:
- Model, device, display mode, and recording setting:
- Steps to reproduce:
  1.
  2.
  3.
- Expected result:
- Actual result:
- Occurrences / attempts actually made:
- Was the recording recoverable?
- Recovery steps taken:
- Screenshot or log filenames:

```text
Relevant error and traceback, with private details removed.
```

For a crash, describe the symptoms and approximate time. Include existing
Reliability Monitor/Event Viewer details if available; repeating the crash is
not required.

## Untested areas and attachments

- GPU or other models:
- Translation:
- Phone/tablet:
- Longer sessions and recovery:
- Classroom accuracy/reference transcript:
- Other:
- Attached logs/screenshots/permitted short exports:
- Issue to investigate first:
