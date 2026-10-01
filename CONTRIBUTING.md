# Contributing

Bug reports, installation feedback, and focused fixes are welcome. For a useful
bug report, include the version or commit, operating system, model, source
language, and the steps needed to reproduce it. The
[test report template](docs/acceptance-report-template.md) covers these details.

## Set up a development environment

Use Python 3.12 and uv. From a clone of `main`:

```bash
uv sync --locked
uv run ruff check .
uv run pytest -q -m "not gpu"
node --test tests/test_worklet.cjs
uv build
uv run python scripts/check_repository.py
```

On Windows, add `--extra windows-cuda` to `uv sync` if you need the private GPU
runtime libraries. Node is needed for the audio-worklet tests, not for running
the application.

Normal tests use fake speech and translation backends. GPU tests require an
explicit `--run-gpu` flag and are excluded from CI. A documentation change
usually needs a link and command review, not hardware testing. For a first
manual GPU check, follow [the testing guide](docs/testing.md).

## Submit a change

Keep each pull request focused on one problem. Describe what changes for the
user and how you checked it. For behavior changes, add tests that exercise the
failure or expected result. Call out platform-specific changes and validate
on the affected platform where possible.

Use a short commit subject, such as `fix: detect private CUDA libraries`.
Before pushing, review the staged diff and run the repository guard. Keep
recordings, transcripts, credentials, model weights, and generated output out
of Git. Use synthetic or permitted examples in tests and issue reports.

## Build installer bundles

```bash
uv run python scripts/build_installers.py --ref HEAD
```

This writes Windows/Ubuntu archives and `SHA256SUMS.txt` to `dist/installers`.
The builder reads the selected commit, so commit any intended changes first.
It includes application files and installation documentation from an allowlist;
Git history, personal reports, recordings, environments, and weights are excluded.
Each archive includes its source commit in `BUILD_INFO.json`.

CI uploads `lecturebridge-installers` after both platform jobs pass. Release
preparation is covered in the [maintainer checklist](docs/release-checklist.md).

## Documentation

Write for the person using or maintaining the project. Explain the task, give
the command or steps, and describe the result they should expect. Keep README
focused on getting started; put detailed reference material in `docs/`.

Use English for current guides. Describe existing behavior in the present tense
and label proposals separately. Avoid assistant-style replies, implementation
recaps, and claims that haven't been tested. Preserve historical measurements
and user-submitted reports when editing nearby documentation.

Project and dependency licenses are separate; see
[third-party notices](THIRD_PARTY_NOTICES.md). Report security issues according
to [SECURITY.md](SECURITY.md).
