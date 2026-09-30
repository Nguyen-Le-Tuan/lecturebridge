# LectureBridge classroom runbook

This is the shortest supported procedure for the current one-device MVP.

## Before leaving for class

1. Boot the Linux or Windows computer, connect power, provide ventilation, and
   prevent suspend.
2. Connect the laptop and iPhone/iPad to Tailscale.
3. From the repository, run:

   ```bash
   uv run lecturebridge-preflight --device auto --peer ipad153
   ```

4. Require every check to report `PASS`. The peer line should say `direct`;
   `relay` can work but may add latency.
5. Start the server at least five minutes before it is needed:

   ```bash
   uv run lecturebridge-live --device auto
   ```

6. Wait for `Application startup complete`. Do not close this terminal.

The default is high-accuracy English-only transcription with
`distil-large-v3.5`. Translation is intentionally off for debate classes.

## Enable private HTTPS

Run this once on the laptop:

```bash
tailscale serve --bg --yes http://127.0.0.1:8000
tailscale serve status
```

On Windows, run these commands in Windows Terminal (Administrator), without
`sudo`. See [`setup-windows.md`](setup-windows.md) for the complete native
Windows setup.

If Tailscale prints an activation link, open it and enable Serve for this
tailnet. Use the resulting `https://...ts.net` URL only. Never enable Funnel.

## Start on iPhone or iPad

1. Open the HTTPS tailnet URL in Safari.
2. Allow microphone access for that site.
3. Keep Safari in the foreground. Choose **Lưu bản ghi** only if you want to
   retain audio on the laptop and have permission, then tap **Bắt đầu nghe**.
4. Speak for 20-30 seconds before relying on the captions.
5. Confirm an English line appears in under five seconds.

The pale/current text may change. Judge the completed lines that remain below
it, not the partial text that is still changing.

For the built-in iPad microphone:

- place the iPad near the center of the debate area;
- keep its microphone openings uncovered;
- avoid placing it beside fans, projectors, keyboards, or loudspeakers;
- keep Safari in the foreground and prevent the screen from locking.

One mono microphone cannot reliably recover two sentences spoken at exactly
the same time. Speaker diarization labels voices but does not separate mixed
speech, so it remains disabled.

## Stop safely

Tap **Dừng phiên** and wait for **Phiên học đã hoàn tất**. If recording was
enabled, open **Thư viện** to play, download or delete it.

Then stop the laptop process with `Ctrl+C`. Do not close Safari or the terminal
while the button still indicates recording.

## Fast recovery

- ASR backlog above five seconds or GPU pressure: restart with
  `uv run lecturebridge-live --model small.en`.
- If `small.en` is still behind: use `base.en`, then `tiny.en` only as the last
  fallback.
- Page disconnected: tap Stop if possible, reload the page, then tap Start.
- Server unavailable: verify Tailscale on both devices, then rerun preflight.
- Port occupied by another service: stop that service; do not bind WLK publicly.

Choose **Tiếng Việt** or **Song ngữ** above the transcript to start translating
new committed text without restarting. Missing translation weights require an
explicit download. Select **Tiếng Anh** to stop submitting translation work.
`--translation` remains available to download/prewarm the CPU worker at launch.

## After class

Stop capture and wait for finalization before stopping the server. Saving is
off by default and resets after each session. Saved audio, committed transcript
and available translations remain on the laptop until explicitly deleted.
Without saving, export any needed transcript before closing the page. Treat
exports as private. See the local studio section of README for storage paths.
