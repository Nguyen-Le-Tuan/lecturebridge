from pathlib import Path

import pytest

from lecturebridge.offline import (
    SUPPORTED_MODELS,
    TranscriptionResult,
    TranscriptSegment,
    calculate_rtf,
    format_timestamp,
    render_human,
)


def test_distil_large_v35_is_default() -> None:
    from lecturebridge.offline import build_parser

    args = build_parser().parse_args(["audio.m4a"])

    assert args.model == "distil-large-v3.5"
    assert args.device == "auto"
    assert args.compute_type == "auto"
    assert args.beam_size == 5


def test_debate_and_fallback_models_are_supported() -> None:
    assert SUPPORTED_MODELS == (
        "distil-large-v3.5",
        "small.en",
        "base.en",
        "tiny.en",
    )


def test_calculate_rtf() -> None:
    assert calculate_rtf(3.5, 10.0) == pytest.approx(0.35)


def test_calculate_rtf_rejects_empty_audio() -> None:
    with pytest.raises(ValueError, match="greater than zero"):
        calculate_rtf(1.0, 0.0)


def test_format_timestamp() -> None:
    assert format_timestamp(65.432) == "00:01:05.432"
    assert format_timestamp(-1) == "00:00:00.000"


def test_render_human_uses_basename_without_private_path() -> None:
    result = TranscriptionResult(
        audio_name=Path("/private/class/audio.m4a").name,
        model="tiny.en",
        device="cuda",
        compute_type="int8_float16",
        language="en",
        duration_seconds=10.0,
        model_load_seconds=1.0,
        inference_seconds=2.0,
        rtf=0.2,
        segments=[TranscriptSegment(0.0, 1.0, "Hello world.")],
    )

    rendered = render_human(result)

    assert "Hello world." in rendered
    assert "audio.m4a" in rendered
    assert "/private/class" not in rendered
    assert "RTF: 0.200" in rendered
