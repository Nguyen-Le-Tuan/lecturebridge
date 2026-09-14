"""Stable LectureBridge launcher for the pinned WhisperLiveKit server."""

from __future__ import annotations

import argparse
import shutil
import sys
from collections.abc import Sequence

from lecturebridge.offline import SUPPORTED_MODELS
from lecturebridge.runtime import ensure_cuda_runtime


def force_nllb_cpu() -> None:
    """Keep NLLB off the small GPU while Faster-Whisper uses CUDA."""
    import nllw
    import torch

    original_load_model = nllw.load_model

    def load_model_on_cpu(*args: object, **kwargs: object) -> object:
        original_is_available = torch.cuda.is_available
        torch.cuda.is_available = lambda: False
        try:
            return original_load_model(*args, **kwargs)
        finally:
            torch.cuda.is_available = original_is_available

    nllw.load_model = load_model_on_cpu


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
        default="small.en",
        help="ASR model (default: small.en)",
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
    if not args.no_translation:
        force_nllb_cpu()

    from whisperlivekit.cli import main as wlk_main

    sys.argv = command
    wlk_main()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
