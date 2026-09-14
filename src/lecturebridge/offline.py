"""Offline Faster-Whisper baseline used before enabling live streaming."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from dataclasses import asdict, dataclass
from pathlib import Path
from time import perf_counter

from faster_whisper import WhisperModel

SUPPORTED_MODELS = ("tiny.en", "base.en")


@dataclass(frozen=True)
class TranscriptSegment:
    start_seconds: float
    end_seconds: float
    text: str


@dataclass(frozen=True)
class TranscriptionResult:
    audio_name: str
    model: str
    device: str
    compute_type: str
    language: str
    duration_seconds: float
    model_load_seconds: float
    inference_seconds: float
    rtf: float
    segments: list[TranscriptSegment]


def calculate_rtf(inference_seconds: float, audio_duration_seconds: float) -> float:
    """Return the real-time factor for one transcription run."""
    if audio_duration_seconds <= 0:
        raise ValueError("Audio duration must be greater than zero")
    return inference_seconds / audio_duration_seconds


def format_timestamp(seconds: float) -> str:
    """Format seconds as a subtitle-friendly HH:MM:SS.mmm timestamp."""
    milliseconds = max(0, round(seconds * 1000))
    hours, remainder = divmod(milliseconds, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    secs, millis = divmod(remainder, 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"


def transcribe_audio(
    audio_path: Path,
    *,
    model_name: str = "tiny.en",
    device: str = "cuda",
    compute_type: str = "int8_float16",
) -> TranscriptionResult:
    """Transcribe an English audio file and collect baseline timings."""
    if not audio_path.is_file():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    load_started = perf_counter()
    model = WhisperModel(model_name, device=device, compute_type=compute_type)
    model_load_seconds = perf_counter() - load_started

    inference_started = perf_counter()
    segment_stream, info = model.transcribe(
        str(audio_path),
        language="en",
        beam_size=1,
        vad_filter=True,
    )
    segments = [
        TranscriptSegment(
            start_seconds=segment.start,
            end_seconds=segment.end,
            text=segment.text.strip(),
        )
        for segment in segment_stream
        if segment.text.strip()
    ]
    inference_seconds = perf_counter() - inference_started
    duration_seconds = float(info.duration)

    return TranscriptionResult(
        audio_name=audio_path.name,
        model=model_name,
        device=device,
        compute_type=compute_type,
        language=info.language,
        duration_seconds=duration_seconds,
        model_load_seconds=model_load_seconds,
        inference_seconds=inference_seconds,
        rtf=calculate_rtf(inference_seconds, duration_seconds),
        segments=segments,
    )


def render_human(result: TranscriptionResult) -> str:
    """Render a readable transcript followed by timing metrics."""
    lines = [
        f"[{format_timestamp(segment.start_seconds)} --> "
        f"{format_timestamp(segment.end_seconds)}] {segment.text}"
        for segment in result.segments
    ]
    lines.extend(
        [
            "",
            f"Audio: {result.audio_name}",
            f"Model: {result.model} ({result.device}, {result.compute_type})",
            f"Language: {result.language}",
            f"Duration: {result.duration_seconds:.2f}s",
            f"Model load: {result.model_load_seconds:.2f}s",
            f"Inference: {result.inference_seconds:.2f}s",
            f"RTF: {result.rtf:.3f}",
        ]
    )
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Transcribe a private English audio file on the local GPU."
    )
    parser.add_argument("audio", type=Path, help="Path to a permitted audio file")
    parser.add_argument(
        "--model",
        choices=SUPPORTED_MODELS,
        default="tiny.en",
        help="Whisper model to benchmark (default: tiny.en)",
    )
    parser.add_argument(
        "--device", default="cuda", help="Inference device (default: cuda)"
    )
    parser.add_argument(
        "--compute-type",
        default="int8_float16",
        help="CTranslate2 compute type (default: int8_float16)",
    )
    parser.add_argument(
        "--json", action="store_true", help="Print machine-readable JSON"
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = transcribe_audio(
            args.audio,
            model_name=args.model,
            device=args.device,
            compute_type=args.compute_type,
        )
    except (FileNotFoundError, RuntimeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(asdict(result), ensure_ascii=False, indent=2))
    else:
        print(render_human(result))

    if not result.segments:
        print("error: transcription produced no speech segments", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
