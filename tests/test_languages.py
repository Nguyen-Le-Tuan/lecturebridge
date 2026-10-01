"""Multilingual contracts using doubles only: no weights or GPU execution."""

import asyncio
import json
import runpy
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
from fakes import FakeBackend, FakeProcessor, FakeTranslator, Response
from fastapi.testclient import TestClient

from lecturebridge import live, offline, preflight
from lecturebridge.languages import LANGUAGES, validate_model_language
from lecturebridge.models import SUPPORTED_MODELS
from lecturebridge.server import create_app
from lecturebridge.transcript import Transcript
from lecturebridge.translation import TranslationService
from lecturebridge.translation_worker import translate_text


@pytest.mark.parametrize("language", tuple(LANGUAGES))
def test_multilingual_models_accept_each_source(language):
    for model in ("tiny", "base", "small", "medium", "large-v3-turbo", "large-v3"):
        assert model in SUPPORTED_MODELS
        validate_model_language(model, language)


@pytest.mark.parametrize("language", ["zh", "zh-Hant", "ja", "ko"])
@pytest.mark.parametrize(
    "model", ["tiny.en", "base.en", "small.en", "distil-large-v3.5"]
)
def test_english_models_reject_other_sources(model, language):
    with pytest.raises(ValueError, match="English only"):
        validate_model_language(model, language)


@pytest.mark.parametrize("module", [live, offline, preflight])
def test_bad_language_model_fails_before_runtime_or_download(module, monkeypatch):
    def forbidden(*a, **kw):
        pytest.fail("Invalid language reached runtime/model download")

    monkeypatch.setattr(module, "ensure_runtime", forbidden)
    monkeypatch.setattr(module, "model_directory", forbidden)
    args = ["--model", "tiny.en", "--language", "zh"]
    if module is offline:
        args.insert(0, "unused.wav")
    assert module.main(args) == 2


@pytest.mark.parametrize("language", tuple(LANGUAGES))
def test_translation_service_and_worker_route_source_to_vietnamese(language):
    profile = LANGUAGES[language]
    requests = []

    class Writer:
        def write(self, value):
            requests.append(json.loads(value))

        async def drain(self):
            pass

    class Reader:
        async def readline(self):
            return json.dumps({"text": "Bản dịch thử"}, ensure_ascii=False).encode()

    async def run():
        service = TranslationService(language)
        service.state = "ready"
        service.process = SimpleNamespace(stdin=Writer(), stdout=Reader())
        assert await service.translate("原文。") == "Bản dịch thử"

    asyncio.run(run())
    assert requests == [{"text": "原文。", "source_language": profile.nllb}]
    captured = {}

    class Tokenizer:
        def encode(self, text, **kwargs):
            assert text == "原文。"
            return SimpleNamespace(tokens=["source-token"])

        def token_to_id(self, token):
            return 42 if token == "output-token" else None

        def decode(self, ids, **kwargs):
            assert ids == [42]
            return "Bản dịch thử"

    class Translator:
        def translate_batch(self, inputs, **kwargs):
            captured.update(inputs=inputs, **kwargs)
            return [SimpleNamespace(hypotheses=[["vie_Latn", "output-token"]])]

    assert (
        translate_text(
            Translator(),
            Tokenizer(),
            text=requests[0]["text"],
            source_code=requests[0]["source_language"],
        )
        == "Bản dịch thử"
    )
    assert captured["inputs"] == [[profile.nllb, "source-token", "</s>"]]
    assert captured["target_prefix"] == [["vie_Latn"]]
    with pytest.raises(ValueError, match="Unsupported"):
        translate_text(Translator(), Tokenizer(), "原文。", "not-a-language")


@pytest.mark.parametrize(
    "text", ["你好。", "今日は晴れです！", "真的吗？", "「こんにちは。」"]
)
def test_cjk_punctuation_commits_short_sentences(text):
    transcript = Transcript(language="zh")
    transcript.translation_enabled = True
    segments = transcript.ingest([{"start": 0, "end": 1, "text": text}])
    assert len(segments) == 1
    assert segments[0]["final"]
    assert segments[0]["text"] == text
    assert segments[0]["language"] == "zh"
    assert segments[0]["translation_status"] == "pending"


@pytest.mark.parametrize(
    "language,text",
    [
        ("zh", "今天学习数学。"),
        ("zh-Hant", "今天學習數學。"),
        ("ja", "今日は数学を勉強します。"),
        ("ko", "오늘은 수학을 공부합니다."),
    ],
)
def test_live_source_switch_translation_and_unicode_exports(tmp_path, language, text):
    class Processor(FakeProcessor):
        async def process_audio(self, pcm):
            if not pcm:
                await self.queue.put(None)
                return
            i = len(self.lines)
            self.lines.append({"start": i, "end": i + 1, "text": text})
            await self.queue.put(Response(self.lines))

    class Backend(FakeBackend):
        def processor(self):
            return Processor()

    backend = Backend()
    backend.language = language
    backend.model = "tiny"
    translator = FakeTranslator()

    def until(ws, kind, predicate=lambda event: True):
        for _ in range(50):
            event = ws.receive_json()
            assert event["type"] != "error", event
            if event["type"] == kind and predicate(event):
                return event
        pytest.fail("Expected event missing")

    with TestClient(
        create_app(backend, data_dir=tmp_path, translator=translator)
    ) as client:
        assert client.get("/api/capabilities").json()["language"] == language
        with client.websocket_connect("/api/live") as ws:
            ws.send_json({"type": "start", "save": True})
            config = until(ws, "config")
            assert config["language_label"] == LANGUAGES[language].label
            ws.send_bytes(b"\0\0" * 16000)
            until(ws, "partial")
            ws.send_json({"type": "translation", "enabled": True})
            until(ws, "translation_state", lambda e: e["state"] == "ready")
            ws.send_bytes(b"\0\0" * 16000)
            event = until(
                ws,
                "transcript",
                lambda e: len(e["segments"]) == 2 and e["segments"][1]["translation"],
            )
            assert event["segments"][0]["translation"] is None
            ws.send_json({"type": "stop"})
            until(ws, "ready_to_stop")
        base = f"/api/recordings/{config['recording_id']}"
        exported = client.get(base + "/export?format=json").json()
        assert all(s["language"] == language for s in exported["segments"])
        assert text in client.get(base + "/export?format=txt").text
        assert "Bản dịch:" in client.get(base + "/export?format=txt").text
        assert translator.calls == [text]


def test_watchdog_rejects_large_models_before_reading_gpu(monkeypatch):
    rules = runpy.run_path(str(Path(__file__).parents[1] / "scripts/gpu-smoke.py"))
    monkeypatch.setattr(sys, "argv", ["gpu-smoke.py", "--model", "large-v3"])
    with pytest.raises(SystemExit) as exc:
        rules["main"]()
    assert exc.value.code == 2


@pytest.mark.parametrize("language", ["zh", "zh-Hant", "ja", "ko"])
def test_offline_and_deep_preflight_pass_source_language(
    monkeypatch, tmp_path, language
):
    import faster_whisper

    from lecturebridge.runtime import RuntimeSelection

    calls = []

    class Model:
        def __init__(self, *a, **kw):
            pass

        def transcribe(self, audio, **kwargs):
            calls.append(kwargs)
            return iter(
                [SimpleNamespace(start=0, end=1, text="原文")]
            ), SimpleNamespace(duration=1, language=LANGUAGES[language].whisper)

    monkeypatch.setattr(faster_whisper, "WhisperModel", Model)
    monkeypatch.setattr(preflight, "model_directory", lambda *a, **kw: tmp_path)
    audio = tmp_path / "placeholder.wav"
    audio.touch()
    result = offline.transcribe_audio(
        audio, model_name="tiny", device="cpu", language=language
    )
    assert result.language == LANGUAGES[language].whisper
    runtime = RuntimeSelection("cpu", "cpu", "int8", "test")
    assert preflight.deep_model_check("tiny", runtime, language).passed
    assert len(calls) == 2
    assert all(c["language"] == LANGUAGES[language].whisper for c in calls)
