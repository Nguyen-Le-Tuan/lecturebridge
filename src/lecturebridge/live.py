"""Stable LectureBridge launcher for the pinned WhisperLiveKit server."""

from __future__ import annotations

import argparse
import os
import shutil
import sys
from collections.abc import Sequence

from lecturebridge.offline import SUPPORTED_MODELS
from lecturebridge.runtime import ensure_cuda_runtime


def build_wlk_command(
    *,
    executable: str,
    model: str,
    port: int,
    translation_enabled: bool,
) -> list[str]:
    """Build the pinned, local-only WhisperLiveKit command."""
    command = [
        executable,
        "serve",
        "--host",
        "127.0.0.1",
        "--port",
        str(port),
        "--backend",
        "faster-whisper",
        "--backend-policy",
        "localagreement",
        "--model",
        model,
        "--lan",
        "en",
        "--pcm-input",
        "--beams",
        "1",
        "--pause-segmentation-seconds",
        "1.2",
        "--log-level",
        "INFO",
    ]
    if translation_enabled:
        command.extend(
            [
                "--target-language",
                "vi",
                "--translation-backend",
                "nllb",
                "--nllb-backend",
                "ctranslate2",
                "--nllb-size",
                "600M",
            ]
        )
    return command


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run local English-to-Vietnamese live captions."
    )
    parser.add_argument(
        "--model",
        choices=SUPPORTED_MODELS,
        default="base.en",
        help="ASR model (default: base.en)",
    )
    parser.add_argument(
        "--no-translation",
        action="store_true",
        help="Run English-only captions if translation is unavailable or too slow",
    )
    parser.add_argument(
        "--port", type=int, default=8000, help="Loopback port (default: 8000)"
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if not 1 <= args.port <= 65535:
        print("error: port must be between 1 and 65535", file=sys.stderr)
        return 2

    try:
        ensure_cuda_runtime()
    except RuntimeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    executable = shutil.which("wlk")
    if executable is None:
        print("error: WhisperLiveKit is unavailable; run `uv sync` first", file=sys.stderr)
        return 1

    command = build_wlk_command(
        executable=executable,
        model=args.model,
        port=args.port,
        translation_enabled=not args.no_translation,
    )
    os.execvpe(command[0], command, os.environ)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
