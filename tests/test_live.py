import pytest

from lecturebridge.live import build_parser, build_wlk_command


def test_live_defaults_are_local_and_translated() -> None:
    args = build_parser().parse_args([])
    command = build_wlk_command(
        executable="wlk",
        model=args.model,
        port=args.port,
        translation_enabled=not args.no_translation,
    )

    assert command[:2] == ["wlk", "serve"]
    assert command[command.index("--host") + 1] == "127.0.0.1"
    assert command[command.index("--backend") + 1] == "faster-whisper"
    assert command[command.index("--backend-policy") + 1] == "localagreement"
    assert command[command.index("--model") + 1] == "base.en"
    assert command[command.index("--target-language") + 1] == "vi"
    assert command[command.index("--nllb-backend") + 1] == "ctranslate2"
    assert "--pcm-input" in command


def test_live_english_only_omits_translation_configuration() -> None:
    command = build_wlk_command(
        executable="wlk",
        model="tiny.en",
        port=9000,
        translation_enabled=False,
    )

    assert command[command.index("--model") + 1] == "tiny.en"
    assert command[command.index("--port") + 1] == "9000"
    assert "--target-language" not in command
    assert "--translation-backend" not in command
    assert "--nllb-backend" not in command


def test_live_parser_rejects_unknown_model() -> None:
    with pytest.raises(SystemExit):
        build_parser().parse_args(["--model", "large-v3"])
