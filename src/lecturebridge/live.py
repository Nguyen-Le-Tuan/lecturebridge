"""Stable LectureBridge launcher for the pinned WhisperLiveKit server."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from lecturebridge.model_store import TRANSLATION_MODEL, model_directory
from lecturebridge.models import DEFAULT_MODEL, SUPPORTED_MODELS
from lecturebridge.runtime import DEVICE_CHOICES, ensure_runtime


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
    model_dir: Path | None,
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
    if model_dir is not None:
        command.extend(["--model_dir", str(model_dir)])
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
        description="Run high-accuracy local English live captions."
    )
    parser.add_argument(
        "--model",
        choices=SUPPORTED_MODELS,
        default=DEFAULT_MODEL,
        help=f"ASR model (default: {DEFAULT_MODEL})",
    )
    parser.add_argument(
        "--device",
        choices=DEVICE_CHOICES,
        default="auto",
        help="Inference device; auto prefers CUDA and falls back to CPU",
    )
    translation = parser.add_mutually_exclusive_group()
    translation.add_argument(
        "--translation",
        action="store_true",
        help="Opt in to English-to-Vietnamese translation on CPU",
    )
    translation.add_argument(
        "--no-translation",
        action="store_true",
        help="Deprecated compatibility alias; English-only is already the default",
    )
    parser.add_argument(
        "--port", type=int, default=8000, help="Loopback port (default: 8000)"
    )
    parser.add_argument(
        "--data-dir", type=Path, help="Private recording library directory"
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if not 1 <= args.port <= 65535:
        print("error: port must be between 1 and 65535", file=sys.stderr)
        return 2

    try:
        runtime = ensure_runtime(args.device)
    except RuntimeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    if runtime.warning:
        print(f"warning: {runtime.warning}", file=sys.stderr)

    try:
        asr_model_dir = model_directory(args.model, download=True)
        if args.translation:
            model_directory(TRANSLATION_MODEL, download=True)
    except RuntimeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.no_translation:
        print(
            "warning: --no-translation is deprecated; English-only is now the default",
            file=sys.stderr,
        )

    import uvicorn

    from lecturebridge.backend import WLKBackend
    from lecturebridge.server import create_app

    app = create_app(
        WLKBackend(args.model, asr_model_dir, runtime),
        data_dir=args.data_dir,
        translation_default=args.translation,
    )
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=args.port,
        log_level="info",
        access_log=False,
        ws_max_size=65536,
        ws_max_queue=8,
        timeout_graceful_shutdown=10,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
