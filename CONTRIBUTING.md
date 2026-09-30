# Contributing to LectureBridge

Thank you for helping improve LectureBridge. Keep contributions focused,
reproducible, and safe for classroom use.

## Development setup

Install Python 3.12 through `uv`, then run:

```bash
uv sync --locked
uv run ruff check .
uv run pytest -q
```

On Windows, use PowerShell and follow [`docs/setup-windows.md`](docs/setup-windows.md).
GPU tests are opt-in and are never required on GitHub-hosted runners.

## Pull requests

- Use a short Conventional Commit subject such as `fix: explain missing cuDNN`.
- Add or update tests for behavior changes.
- Keep model weights, recordings, transcripts, credentials, and generated
  output out of Git.
- Explain platform-specific behavior and test it on the affected platform.
- Confirm `uv run python scripts/check_repository.py` passes before opening a
  pull request.

## Privacy and licensing

Only submit audio or text that you are authorized to share. Do not attach real
classroom recordings or transcripts to issues. Third-party model licenses are
independent from LectureBridge's MIT license; see `THIRD_PARTY_NOTICES.md`.
