import nllw
import pytest
import torch

from lecturebridge.live import build_parser, build_wlk_command, force_nllb_cpu


def test_live_defaults_are_local_and_english_only() -> None:
    args = build_parser().parse_args([])
    command = build_wlk_command(
        executable="wlk",
        model=args.model,
        model_dir=None,
        port=args.port,
        translation_enabled=args.translation,
    )

    assert command[:2] == ["wlk", "serve"]
    assert command[command.index("--host") + 1] == "127.0.0.1"
    assert command[command.index("--backend") + 1] == "faster-whisper"
    assert command[command.index("--backend-policy") + 1] == "localagreement"
    assert command[command.index("--model") + 1] == "distil-large-v3.5"
    assert args.device == "auto"
    assert "--target-language" not in command
    assert "--nllb-backend" not in command
    assert "--pcm-input" in command
    assert "--beams" not in command


def test_live_english_only_omits_translation_configuration() -> None:
    command = build_wlk_command(
        executable="wlk",
        model="tiny.en",
        model_dir=None,
        port=9000,
        translation_enabled=False,
    )

    assert command[command.index("--model") + 1] == "tiny.en"
    assert command[command.index("--port") + 1] == "9000"
    assert "--target-language" not in command
    assert "--translation-backend" not in command
    assert "--nllb-backend" not in command


def test_live_translation_is_explicit_opt_in() -> None:
    args = build_parser().parse_args(["--translation"])
    command = build_wlk_command(
        executable="wlk",
        model=args.model,
        model_dir=None,
        port=args.port,
        translation_enabled=args.translation,
    )

    assert command[command.index("--target-language") + 1] == "vi"
    assert command[command.index("--nllb-backend") + 1] == "ctranslate2"


def test_live_parser_rejects_unknown_model() -> None:
    with pytest.raises(SystemExit):
        build_parser().parse_args(["--model", "unknown-model"])


def test_live_command_uses_locked_model_directory(tmp_path) -> None:
    command = build_wlk_command(
        executable="wlk",
        model="tiny.en",
        model_dir=tmp_path,
        port=8000,
        translation_enabled=False,
    )

    assert command[command.index("--model_dir") + 1] == str(tmp_path)


def test_nllb_loader_is_forced_to_cpu_and_restores_torch_probe(monkeypatch) -> None:
    original_probe = torch.cuda.is_available

    def fake_load_model(*args: object, **kwargs: object) -> str:
        return "cuda" if torch.cuda.is_available() else "cpu"

    monkeypatch.setattr(nllw, "load_model", fake_load_model)
    force_nllb_cpu()

    assert nllw.load_model(["eng_Latn"]) == "cpu"
    assert torch.cuda.is_available is original_probe
