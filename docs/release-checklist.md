# Public release checklist

Keep the GitHub repository private until every required item is complete.

## Repository safety

- [ ] Create and verify an offline `git bundle --all` backup.
- [ ] Rewrite the personal author/committer email to the GitHub noreply address
      across every branch and tag.
- [ ] Confirm the old email is absent from `git log --all`.
- [ ] Run `uv run python scripts/check_repository.py` after staging all files.
- [ ] Inspect `git diff --cached --stat` and confirm no model, audio, transcript,
      credential, local cache, or file larger than 10 MiB is present.
- [ ] Verify a fresh clone can run `uv sync --locked` without local paths.

## Quality gates

- [ ] Linux CI passes lint, tests, build, repository guard, and Bash syntax.
- [ ] Windows CI passes lint, tests, build, repository guard, and PowerShell syntax.
- [ ] Linux NVIDIA deep preflight passes on trusted hardware.
- [ ] Windows NVIDIA deep preflight passes on trusted hardware.
- [ ] Windows CPU fallback runs with `tiny.en` when CUDA is hidden or absent.
- [ ] Default model downloads and verifies from an empty Hugging Face cache.
- [ ] The application runs offline after the verified download.
- [ ] Tailscale Serve HTTPS works from an iPhone/iPad on both host platforms.

## GitHub publication

- [ ] Update rewritten `main` only with `--force-with-lease` while private.
- [ ] Push `chore/bootstrap` and open the cross-platform bootstrap pull request.
- [ ] Merge with a merge commit so the reviewed atomic commits remain visible.
- [ ] Enable branch protection: required CI and review, no deletion, no force-push.
- [ ] Enable private vulnerability reporting and public secret scanning.
- [ ] Change visibility to public only after a final owner review.
- [ ] Tag `v0.1.0` only after both physical GPU acceptance runs pass.
- [ ] Release source archives only; never attach model weights or private audio.
