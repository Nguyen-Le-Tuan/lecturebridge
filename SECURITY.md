# Security policy

## Supported version

Security fixes currently target the latest commit on `main`.

## Reporting a vulnerability

Do not open a public issue for a suspected vulnerability, credential exposure,
or privacy incident. Use GitHub's private vulnerability reporting feature for
this repository. Include the affected version, reproduction steps, impact, and
any suggested mitigation.

Never include classroom audio, transcripts, Tailscale credentials, Hugging
Face tokens, or other personal data in a report. Revoke exposed credentials
before reporting them.

## Security boundaries

LectureBridge binds its application server to `127.0.0.1`. Tailscale Serve is
the supported way to provide HTTPS access inside a tailnet. Tailscale Funnel
and direct public binding are outside the supported configuration.
