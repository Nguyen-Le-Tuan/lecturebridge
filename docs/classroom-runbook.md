# Phone/tablet classroom runbook

Complete Install and a short local microphone test first. For initial
acceptance, use the [README checklist](../README.md#short-acceptance-check).

## Prepare the connection

1. Keep the Windows/Ubuntu computer powered, ventilated, and awake.
2. Install Tailscale on the computer and iPhone/iPad, sign in, and explicitly
   authorize access between the devices in your tailnet.
3. Start LectureBridge using `Start.cmd` or `bash Start.sh`. Its saved model,
   source language, and runtime are shown in the terminal.
4. On the computer, enable private HTTPS using Tailscale Serve:

   ```text
   tailscale serve --bg --yes http://127.0.0.1:8000
   tailscale serve status
   ```

   Initial configuration can require administrator permission (an Administrator
   terminal on Windows, or sudo on Ubuntu). If Tailscale prints an activation
   link, open it to enable Serve. Use the resulting `https://...ts.net` URL.
   Never enable Funnel or expose the app publicly.

Local computer use does not require Tailscale. Phone/tablet use needs HTTPS for
microphone permission. The computer must stay on for captions and library access.
Anyone allowed to reach this instance can access its library; this is a trusted
single-instance tool, not a service with separate user accounts.

## Start and verify

1. Open the tailnet HTTPS URL in Safari and allow microphone access.
2. Keep Safari in the foreground and prevent screen lock.
3. Enable the recording switch only with permission and if you want to retain
   audio. Then start listening.
4. Speak for 15–30 seconds in the configured source language. Judge committed
   lines, not the provisional text that may change. Record the observed delay.
5. Test Vietnamese/bilingual mode separately. Download approval is explicit;
   translation starts on new committed text and may lag noticeably.

Place the microphone near the speakers, uncovered, away from fans and keyboards.
One mono microphone cannot reliably recover overlapping speech. Speaker
separation is not included. Do not rely on captions as an authoritative record.

## Stop and recover

Stop the session in the app and wait for finalization. If saving was enabled,
check the library, playback, and export. If saving was off, export any temporary
transcript you need before leaving the page. Then press Ctrl+C in the computer's
terminal to stop the server.

- If captions fall behind, stop and try a smaller model or a CPU baseline as
  described in the README. Measure with translation disabled first.
- If the page disconnects, reload and start a new session; automatic reconnect
  and resume are not available. Previously received audio is retained when
  recording was enabled.
- If the server is unreachable, check Tailscale on both devices and Serve status.
- If port 8000 is occupied, close the old server; do not bind the app publicly.
- Recording resets to off after each session. Saved data persists locally until
  you delete it; review exports before sharing them.
