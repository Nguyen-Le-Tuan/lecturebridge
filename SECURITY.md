# Security

Security fixes target the current `main` branch.

## Report a vulnerability

Use the repository's private vulnerability reporting channel for security or
privacy issues. Include the affected version, reproduction steps, and expected
impact. Avoid public issues for exposed credentials or a vulnerability that
could affect other users. Revoke any exposed credentials promptly.

Reports should contain only the details needed to reproduce the issue. Leave
out private audio, transcripts, Tailscale credentials, and access tokens.

## Deployment scope

LectureBridge listens on `127.0.0.1`. Tailscale Serve provides HTTPS access for
trusted devices in a tailnet. Public internet hosting and Tailscale Funnel are
unsupported.

The application has one shared recording library and no separate user accounts.
Anyone who can reach the instance can access that library. Restrict tailnet
access accordingly and keep the host computer's user account secure.
