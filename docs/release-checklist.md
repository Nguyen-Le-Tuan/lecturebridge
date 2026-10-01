# Release checklist

Use a pre-release for builds that still need feedback from testers. A release
tag identifies the exact source commit used to build the downloadable archives.
A GitHub Release inherits the repository's visibility; creating one does not
make a private repository public.

## Prepare an alpha release

- [ ] Merge the intended changes into `main` through the normal CI checks.
- [ ] Confirm Windows and Ubuntu jobs pass for the selected commit.
- [ ] Review setup instructions, known issues, and the testing guide.
- [ ] Run the repository guard and inspect the files included in each bundle.
- [ ] Build or download the Windows ZIP, Ubuntu TAR.GZ, and `SHA256SUMS.txt`.
- [ ] Check archive hashes and confirm `BUILD_INFO.json` names the selected commit.
- [ ] Use a version such as `v0.1.0-alpha.1` and mark the release as a pre-release.
- [ ] Attach both installer archives and the checksum file.
- [ ] Write release notes covering changes, installation, known limitations,
      and which checks have been completed.
- [ ] Give testers the matching report template and ask them to record the version.

Archive contents should include code and documentation only. Models download
during setup; recordings, transcripts, credentials, local reports, and virtual
environments stay out of release assets. GitHub's automatically generated source
archives are separate from the installer bundles.

Keep published tags and their assets tied to the original build. If a fix changes
what testers receive, publish the next version rather than silently replacing it.

## Before a stable release

- [ ] Complete fresh-machine setup on Windows and Ubuntu.
- [ ] Verify CPU fallback and a bounded tiny GPU check on each supported platform.
- [ ] Test the selected larger models separately on suitable hardware.
- [ ] Verify downloads and checksums from an empty model cache.
- [ ] Check offline operation after the required models are cached.
- [ ] Complete microphone, recording, playback, export, deletion, and restart checks.
- [ ] Record actual transcription and translation quality for supported languages.
- [ ] Test physical Safari/iPad access through Tailscale HTTPS.
- [ ] Document remaining limitations with enough detail for users to decide
      whether the release suits their needs.

Longer-session testing is a separate acceptance step after short sessions are
stable. The [test history](test-evidence.md) records earlier results; a CI pass
or tiny smoke test alone does not establish classroom reliability.

## Before making the repository public

- [ ] Review tracked files and Git history for private data and credentials.
- [ ] Review author metadata and decide whether any personal details need removal.
- [ ] Back up all branches and tags before any necessary history rewrite.
- [ ] Check source, dependency, and model licensing; keep NLLB out of commercial use.
- [ ] Confirm branch protection, required CI, and vulnerability-reporting settings.
- [ ] Review visibility and access with the repository owner before changing them.

History rewriting and visibility changes are separate maintenance operations;
ordinary alpha releases do not require them.
