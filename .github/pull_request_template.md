## Summary

Describe the user-visible change and why it is needed.

## Verification

- [ ] `uv run ruff check .`
- [ ] `uv run pytest -q`
- [ ] `uv build`
- [ ] `uv run python scripts/check_repository.py`
- [ ] Platform-specific behavior was tested or clearly marked as unverified.

## Privacy and release safety

- [ ] No model weights, recordings, transcripts, credentials, `.env` files, or
      machine-specific paths are included.
- [ ] New third-party code, data, or models have documented license terms.
