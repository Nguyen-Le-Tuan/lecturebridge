# LectureBridge classroom runbook

This is the shortest supported procedure for the current one-iPhone MVP.

## Before leaving for class

1. Boot Ubuntu, connect power, provide ventilation, and prevent suspend.
2. Connect the laptop and iPhone to Tailscale.
3. From the repository, run:

   ```bash
   uv run lecturebridge-preflight
   ```

4. Require every check to report `PASS`.
5. Start the server at least five minutes before it is needed:

   ```bash
   uv run lecturebridge-live
   ```

6. Wait for `Application startup complete`. Do not close this terminal.

## Enable private HTTPS

Run this once on the laptop:

```bash
tailscale serve --bg --yes http://127.0.0.1:8000
tailscale serve status
```

If Tailscale prints an activation link, open it and enable Serve for this
tailnet. Use the resulting `https://...ts.net` URL only. Never enable Funnel.

## Start on iPhone

1. Open the HTTPS tailnet URL in Safari.
2. Allow microphone access for that site.
3. Keep Safari in the foreground and tap the red record button.
4. Speak for 20-30 seconds before relying on the captions.
5. Confirm both an English line and a Vietnamese line appear.

The pale/current text may change. Completed lines remain below it. Translation
can lag behind English.

## Stop safely

Tap the record button again and wait for:

```text
Finished processing audio! Ready to record again.
```

Then stop the laptop process with `Ctrl+C`. Do not close Safari or the terminal
while the button still indicates recording.

## Fast recovery

- Translation slow or failing: restart with
  `uv run lecturebridge-live --no-translation`.
- ASR backlog or GPU pressure: restart with
  `uv run lecturebridge-live --model tiny.en`.
- Page disconnected: tap Stop if possible, reload the page, then tap Start.
- Server unavailable: verify Tailscale on both devices, then rerun preflight.
- Port occupied by another service: stop that service; do not bind WLK publicly.

English-only mode is the preferred classroom fallback. It keeps speech
recognition local and avoids silently accumulating translation delay.

## After class

Stop capture and the server. The MVP does not save audio or transcript by
default. If a future version adds export, treat the exported file as private.
