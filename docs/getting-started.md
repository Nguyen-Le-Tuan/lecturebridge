# LectureBridge — Getting started

**Language:** [English](getting-started.md) | [Tiếng Việt](i18n/getting-started.vi.md) | [简体中文](i18n/getting-started.zh-Hans.md) | [繁體中文](i18n/getting-started.zh-Hant.md) | [日本語](i18n/getting-started.ja.md) | [한국어](i18n/getting-started.ko.md)

LectureBridge displays live captions in your browser and can translate them into Vietnamese. This guide gets you from a fresh Windows or Ubuntu computer to a short first session. You don't need to install Git, Python, or CUDA Toolkit yourself.

**Guide language, spoken language, and translation are separate choices.** Reading a translated guide doesn't change the app. Speech recognition supports English, Mandarin Chinese, Japanese, and Korean; translation outputs Vietnamese. Vietnamese speech recognition is not currently a selectable source. The studio UI is Vietnamese and installer messages are English.

## 1. Before you start

- Windows 10/11 x86-64 or Ubuntu 22.04/24.04 x86-64.
- At least 4 GB RAM and 20 GB free on the installation drive.
- Internet for setup and model downloads. Setup may download several GB; keep at least 2 GB free on the model-cache drive and another approximately 2.5 GB if you enable translation.
- A microphone and permission to capture the audio. An NVIDIA GPU is optional; CPU mode may be slower.

## 2. Download and extract

Open [Releases](https://github.com/Nguyen-Le-Tuan/lecturebridge/releases) and expand **Assets**. Download `*-windows-x64.zip` for Windows or `*-ubuntu-x64.tar.gz` for Ubuntu. Choose the installer archive rather than GitHub's automatically generated **Source code** download. If you received the installer directly, use that file. Private repository downloads require access to the repository.

Extract the whole archive into a writable folder you intend to keep. Open the inner folder containing `Install.cmd` and `Install.sh`. Run the installer from there, not from inside the archive viewer.

## 3. Install and open the app

### Windows

1. Double-click `Install.cmd`.
2. Choose the language spoken in your audio. Wait for **Setup complete**.
3. If Windows asks to install Microsoft Visual C++, approve it to continue. If setup reports a required restart, restart Windows yourself, then run Install again.
4. Double-click `Start.cmd`.

### Ubuntu

Open a terminal in the extracted folder. Run the first command and wait for **Setup complete** before running the second:

```bash
bash Install.sh
bash Start.sh
```

Choose your spoken language when prompted. Enter your `sudo` password if needed for missing system packages. Characters won't appear while typing the password; press Enter when finished.

Install downloads the application dependencies and chooses a small starting model. It checks hardware without running inference and leaves GPU drivers unchanged. On the first eligible GPU launch, Start runs a bounded `tiny` check; a failure starts that session on CPU. The browser opens at [http://127.0.0.1:8000](http://127.0.0.1:8000). Keep the terminal open while using the app.

## 4. Try a short session

Allow microphone access. Leave recording and translation off for your first 15–30 seconds of speech. **Bắt đầu nghe** starts listening; **Dừng phiên** stops it. Stop in the app first, then press Ctrl+C in the terminal to close the server.

To try translation in a separate session, select **Tiếng Việt** or **Song ngữ** and approve the model download. Translation runs on CPU and only applies to newly committed text; it can lag by tens of seconds.

Turn on **Lưu bản ghi** before a session if you want to save audio and text. Afterwards, open **Thư viện** for playback and TXT/JSON/WAV export. Audio is saved as WAV; committed text and available translations are stored in `library.sqlite3`. Export TXT or JSON to create a separate text file. The library is at `%LOCALAPPDATA%\LectureBridge` on Windows or `${XDG_DATA_HOME:-~/.local/share}/lecturebridge` on Ubuntu. Browser exports use your browser's download location.

## 5. Choose a spoken language

| Audio language | Code |
| --- | --- |
| English | `en` |
| Mandarin Chinese | `zh` |
| Mandarin with Traditional Chinese translation-source setting | `zh-Hant` |
| Japanese | `ja` |
| Korean | `ko` |

Close the server before changing the language. For example, to switch to Mandarin:

```powershell
.\Start.cmd --language zh
```

```bash
bash Start.sh --language zh
```

Choose the command for your OS. Start remembers the selection. `zh-Hant` uses the same speech recognizer as `zh` and doesn't guarantee Traditional characters in the transcript. Chinese, Japanese, and Korean require multilingual models such as `tiny`, `base`, or `small`; `.en` models and `distil-large-v3.5` support English only.

## 6. If something goes wrong

- Setup fails: read `.lecturebridge/setup.log`, fix the reported problem, and rerun Install. A failed setup blocks Start until it completes.
- Browser doesn't open: wait for server startup, then open `http://127.0.0.1:8000` yourself.
- Port 8000 is occupied: close the previous server first.
- Prefer CPU-only use: close the server and run one of the following from the installation folder. Here `en` means English audio; substitute the source code you need.

```powershell
.\Install.cmd -Profile cpu -Language en
```

```bash
bash Install.sh --profile cpu --language en
```

Keep initial sessions short. **The live server has no thermal watchdog.** Stop if the computer gets hot or responds poorly. The bounded GPU check reduces test exposure but cannot prevent every system or driver crash.

Local computer use needs no Tailscale. For a phone/tablet, use the Tailscale HTTPS setup below. Install updates in a new folder; don't move a configured `.venv` between computers or operating systems. Saved recordings remain in your user data directory.

## More help

The reference pages below are in English.

- [Windows setup](setup-windows.md)
- [Ubuntu setup](setup-linux.md)
- [Installation profiles and hardware selection](installation.md)
- [Languages, models, and commands](models.md)
- [Phone/tablet over Tailscale HTTPS](classroom-runbook.md)
- [Troubleshooting](troubleshooting.md)
- [Feature testing](testing.md)
- [Test report template](acceptance-report-template.md)
- [Project overview](../README.md)
