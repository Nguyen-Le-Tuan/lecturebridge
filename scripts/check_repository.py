"""Fail CI when local-only, oversized, or obviously secret files are tracked."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAX_TRACKED_SIZE = 10 * 1024 * 1024
FORBIDDEN_PREFIXES = (
    ".venv/",
    ".tools/",
    ".lecturebridge/",
    "data/private/",
    "models/",
    "nllb-200-distilled-600M-ctranslate2/",
    "outputs/",
    "benchmark-results/private/",
)
FORBIDDEN_SUFFIXES = (
    ".wav",
    ".mp3",
    ".m4a",
    ".webm",
    ".mp4",
    ".srt",
    ".vtt",
    ".sqlite3",
    ".sqlite3-journal",
    ".sqlite3-wal",
    ".sqlite3-shm",
)
SECRET_PATTERNS = (
    re.compile(rb"AKIA[0-9A-Z]{16}"),
    re.compile(rb"gh[pousr]_[A-Za-z0-9_]{20,}"),
    re.compile(rb"-----BEGIN (?:RSA|OPENSSH|EC|DSA) PRIVATE KEY-----"),
)


def tracked_files() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=ROOT,
        capture_output=True,
        check=True,
    )
    return [ROOT / item.decode() for item in result.stdout.split(b"\0") if item]


def main() -> int:
    failures: list[str] = []
    for path in tracked_files():
        relative = path.relative_to(ROOT).as_posix()
        if relative == ".env" or relative.startswith(".env."):
            failures.append(f"environment file is tracked: {relative}")
        if relative.startswith(FORBIDDEN_PREFIXES):
            failures.append(f"local-only path is tracked: {relative}")
        if relative.lower().endswith(FORBIDDEN_SUFFIXES):
            failures.append(f"private media/subtitle is tracked: {relative}")
        size = path.stat().st_size
        if size > MAX_TRACKED_SIZE:
            failures.append(f"tracked file exceeds 10 MiB: {relative} ({size} bytes)")
        if size <= 1024 * 1024:
            content = path.read_bytes()
            for pattern in SECRET_PATTERNS:
                if pattern.search(content):
                    failures.append(f"possible secret in tracked file: {relative}")
                    break

    if failures:
        for failure in failures:
            print(f"FAIL: {failure}", file=sys.stderr)
        return 1
    print("Repository guard passed: no private, oversized, or obvious secret files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
