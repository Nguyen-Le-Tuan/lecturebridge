import asyncio
import io
import wave

import pytest
from fakes import FakeBackend, FakeTranslator
from fastapi.testclient import TestClient

from lecturebridge.server import create_app
from lecturebridge.storage import Library, Recorder
from lecturebridge.transcript import Transcript

PCM = b"\x00\x00" * 16000


@pytest.fixture
def studio(tmp_path):
    backend, translator = FakeBackend(), FakeTranslator()
    with TestClient(
        create_app(backend, data_dir=tmp_path, translator=translator)
    ) as client:
        yield client, backend, translator


def receive(ws, kind):
    for _ in range(50):
        item = ws.receive_json()
        if item.get("type") == "error":
            pytest.fail(item["message"])
        if item.get("type") == kind:
            return item
    pytest.fail(f"no {kind} message")


def start(ws, **options):
    ws.send_json({"type": "start", **options})
    return receive(ws, "config")


def stop(ws):
    ws.send_json({"type": "stop"})
    return receive(ws, "ready_to_stop")


def test_private_origin_static_assets_and_health(studio):
    client, _, _ = studio
    assert "Theo kịp từng ý tưởng" in client.get("/").text
    assert "lecturebridge-pcm" in client.get("/assets/pcm-worklet.js").text
    assert client.get("/health").json()["ready"]
    assert client.get("/api/capabilities").json()["storage"] == "local"
    assert (
        client.get(
            "/api/recordings", headers={"Origin": "https://evil.example"}
        ).status_code
        == 403
    )
    assert client.get("/", headers={"Host": "evil.example"}).status_code == 403
    assert (
        client.get(
            "/",
            headers={
                "Host": "laptop.tailnet.ts.net",
                "Origin": "https://laptop.tailnet.ts.net",
            },
        ).status_code
        == 200
    )
    assert (
        "frame-ancestors 'none'" in client.get("/").headers["content-security-policy"]
    )


def test_transient_session_saves_nothing(studio, tmp_path):
    client, backend, _ = studio
    with client.websocket_connect("/api/live") as ws:
        assert start(ws)["recording_id"] is None
        ws.send_bytes(PCM)
        assert receive(ws, "transcript")["segments"][0]["text"] == "This is sentence 1."
        assert stop(ws)["recording_id"] is None
    assert backend.last_processor.clean
    assert client.get("/api/recordings").json() == []
    assert not list(tmp_path.glob("*.wav"))


def test_record_playback_range_export_rename_delete(studio):
    client, _, _ = studio
    with client.websocket_connect("/api/live") as ws:
        recording_id = start(ws, save=True, title="Lớp sinh học")["recording_id"]
        assert client.delete(f"/api/recordings/{recording_id}").status_code == 409
        ws.send_bytes(PCM)
        receive(ws, "transcript")
        stop(ws)
    base = f"/api/recordings/{recording_id}"
    item = client.get(base).json()
    assert item["title"] == "Lớp sinh học"
    assert item["status"] == "complete"
    assert item["duration"] == 1
    assert len(item["segments"]) == 1
    audio = client.get(base + "/audio")
    with wave.open(io.BytesIO(audio.content)) as wav:
        assert wav.getparams()[:3] == (1, 2, 16000)
        assert wav.readframes(wav.getnframes()) == PCM
    assert (
        client.get(base + "/audio", headers={"Range": "bytes=44-99"}).status_code == 206
    )
    assert (
        "attachment"
        in client.get(base + "/audio?download=true").headers["content-disposition"]
    )
    assert "sentence 1" in client.get(base + "/export").text
    assert (
        client.get(base + "/export?format=json").json()["segments"] == item["segments"]
    )
    assert client.patch(base, json={"title": "Tên mới"}).json()["title"] == "Tên mới"
    assert client.patch(base, json={"title": " "}).status_code == 400
    assert client.delete(base).status_code == 200
    assert client.get(base).status_code == 404
    assert client.get(base + "/audio").status_code == 404


def test_translation_switch_keeps_session_and_does_not_backfill(studio):
    client, _, translator = studio
    with client.websocket_connect("/api/live") as ws:
        start(ws, save=True)
        ws.send_bytes(PCM)
        receive(ws, "partial")
        ws.send_json({"type": "translation", "enabled": True})
        receive(ws, "translation_state")
        ws.send_bytes(PCM)
        while True:
            snapshot = receive(ws, "transcript")["segments"]
            if len(snapshot) == 2 and snapshot[-1]["translation"]:
                break
        assert snapshot[0]["translation"] is None
        assert snapshot[1]["translation"] == "Bản dịch: This is sentence 2."
        ws.send_json({"type": "translation", "enabled": False})
        receive(ws, "translation_state")
        ws.send_bytes(PCM)
        receive(ws, "partial")
        stop(ws)
    assert translator.calls == ["This is sentence 2."]
    recording_id = client.get("/api/recordings").json()[0]["id"]
    snapshot = client.get(f"/api/recordings/{recording_id}").json()["segments"]
    assert len(snapshot) == 3
    assert snapshot[2]["translation"] is None


@pytest.mark.parametrize("fail,missing", [(True, False), (False, True)])
def test_translation_failure_does_not_stop_english(tmp_path, fail, missing):
    translator = FakeTranslator(fail=fail, missing=missing)
    with TestClient(
        create_app(FakeBackend(), data_dir=tmp_path, translator=translator)
    ) as client:
        with client.websocket_connect("/api/live") as ws:
            start(ws, translation=True)
            ws.send_bytes(PCM)
            receive(ws, "partial")
            stop(ws)
        assert client.get("/health").status_code == 200


def test_explicit_download_consent_and_bad_ids(studio):
    client, _, _ = studio
    assert client.post("/api/translation/prepare", json={}).status_code == 400
    assert (
        client.post("/api/translation/prepare", json={"download": True}).status_code
        == 202
    )
    assert client.get("/api/recordings/not-a-uuid").status_code == 404


def test_disconnect_recovers_saved_audio(studio):
    client, _, _ = studio
    with client.websocket_connect("/api/live") as ws:
        recording_id = start(ws, save=True)["recording_id"]
        ws.send_bytes(PCM)
        receive(ws, "partial")
    item = client.get(f"/api/recordings/{recording_id}").json()
    assert item["status"] == "interrupted"
    assert item["duration"] == 1
    assert len(item["segments"]) == 1


def test_disk_write_failure_keeps_transcript(studio, monkeypatch):
    client, _, _ = studio

    def full_disk(*_args):
        raise OSError("disk full")

    monkeypatch.setattr(Recorder, "write", full_disk)
    with client.websocket_connect("/api/live") as ws:
        recording_id = start(ws, save=True)["recording_id"]
        ws.send_bytes(PCM)
        receive(ws, "recording_error")
        assert receive(ws, "transcript")["segments"]
        stop(ws)
    assert (
        client.get(f"/api/recordings/{recording_id}").json()["status"] == "interrupted"
    )


def test_second_live_session_is_rejected(studio):
    client, _, _ = studio
    with client.websocket_connect("/api/live") as first:
        start(first)
        with client.websocket_connect("/api/live") as second:
            assert second.receive_json()["type"] == "error"
        stop(first)


def test_legacy_asr_protocol(studio):
    client, _, _ = studio
    with client.websocket_connect("/asr") as ws:
        receive(ws, "config")
        ws.send_bytes(PCM)
        assert ws.receive_json()["lines"][0]["text"]
        ws.send_bytes(b"")
        receive(ws, "ready_to_stop")


def test_wav_crash_recovery(tmp_path):
    library = Library(tmp_path)
    recorder = Recorder(library, "Recovery")
    recorder.write(PCM)
    recorder.wav.close()
    recorder.file.close()
    # Simulate data flushed immediately before the header checkpoint.
    with library.audio_path(recorder.id).open("ab") as file:
        file.write(PCM + b"\0")
    library.recover()
    item = library.get(recorder.id)
    assert item["status"] == "interrupted"
    assert item["duration"] == 2
    with wave.open(str(library.audio_path(recorder.id))) as wav:
        assert wav.getnframes() == 32000


def test_cumulative_lines_are_not_duplicated_and_toggle_splits_tail():
    transcript = Transcript()
    first = {"start": "0:00:00", "end": "0:00:01", "text": "Hello"}
    assert transcript.ingest([first]) == []
    assert transcript.ingest([first]) == []
    transcript.flush()
    transcript.translation_enabled = True
    transcript.epoch += 1
    transcript.ingest([{**first, "end": "0:00:02", "text": "Hello world."}])
    segments = transcript.snapshot()
    assert [item["text"] for item in segments] == ["Hello", "world."]
    assert [item["translation_status"] for item in segments] == ["off", "pending"]
    assert [item["id"] for item in segments] == [1, 2]


def test_cpu_only_translation_process_contract(monkeypatch):
    from lecturebridge.translation import TranslationService

    async def run():
        service = TranslationService()
        called = {}

        class Reader:
            async def readline(self):
                return b'{"ready": true}\n'

        class Process:
            returncode = None
            stdout = Reader()

            def terminate(self):
                self.returncode = 0

            async def wait(self):
                return 0

        async def spawn(*args, **kwargs):
            called.update(kwargs)
            return Process()

        monkeypatch.setattr(
            "lecturebridge.translation.model_directory", lambda *a, **k: "/fake/model"
        )
        monkeypatch.setattr(asyncio, "create_subprocess_exec", spawn)
        assert await service.prepare()
        assert called["env"]["CUDA_VISIBLE_DEVICES"] == "-1"
        assert called["env"]["OMP_NUM_THREADS"] == "2"
        assert called["env"]["PYTHONIOENCODING"] == "utf-8"
        await service.close()

    asyncio.run(run())


@pytest.mark.parametrize(
    "model,language,whisper_code",
    [
        ("tiny.en", "en", "en"),
        ("tiny", "zh", "zh"),
        ("tiny", "zh-Hant", "zh"),
        ("tiny", "ja", "ja"),
        ("tiny", "ko", "ko"),
    ],
)
def test_backend_passes_selected_runtime_without_loading_weights(
    monkeypatch, tmp_path, model, language, whisper_code
):
    import faster_whisper
    import whisperlivekit
    from whisperlivekit.local_agreement.backends import FasterWhisperASR

    from lecturebridge.backend import WLKBackend
    from lecturebridge.runtime import RuntimeSelection

    captured = {}
    original = FasterWhisperASR.load_model

    def fake_model(path, **kwargs):
        captured.update(kwargs)
        captured["path"] = path
        return object()

    def fake_engine(**kwargs):
        assert kwargs["backend_policy"] == "localagreement"
        assert not kwargs["target_language"]
        assert kwargs["lan"] == whisper_code
        FasterWhisperASR.load_model(None)
        return object()

    monkeypatch.setattr(faster_whisper, "WhisperModel", fake_model)
    monkeypatch.setattr(whisperlivekit, "TranscriptionEngine", fake_engine)
    runtime = RuntimeSelection("cpu", "cpu", "int8", "test")
    backend = WLKBackend(model, tmp_path, runtime, language=language)
    asyncio.run(backend.start())
    assert captured["device"] == "cpu"
    assert captured["compute_type"] == "int8"
    assert captured["local_files_only"] is True
    assert captured["cpu_threads"] == 2
    assert FasterWhisperASR.load_model is original


def test_second_server_cannot_recover_an_active_library(studio, tmp_path):
    from filelock import Timeout

    with (
        pytest.raises(Timeout),
        TestClient(
            create_app(FakeBackend(), data_dir=tmp_path, translator=FakeTranslator())
        ),
    ):
        pytest.fail("a second server acquired the same library")


def test_cancelled_translation_cannot_reuse_stale_output(monkeypatch):
    from lecturebridge.translation import TranslationService

    async def run():
        service = TranslationService()
        began = asyncio.Event()
        stopped = []

        class Input:
            def write(self, data):
                pass

            async def drain(self):
                pass

        class Output:
            async def readline(self):
                began.set()
                await asyncio.Event().wait()

        class Process:
            stdin = Input()
            stdout = Output()

        async def stop_worker():
            stopped.append(True)
            service.process = None

        service.process = Process()
        service.state = "ready"
        monkeypatch.setattr(service, "stop_worker", stop_worker)
        task = asyncio.create_task(service.translate("private text"))
        await began.wait()
        task.cancel()
        await asyncio.gather(task, return_exceptions=True)
        assert stopped == [True]
        assert service.process is None
        assert service.state == "idle"

    asyncio.run(run())


def test_invalid_pcm_and_origin_are_rejected(studio):
    client, _, _ = studio
    from starlette.websockets import WebSocketDisconnect

    with (
        pytest.raises(WebSocketDisconnect),
        client.websocket_connect(
            "/api/live", headers={"Origin": "https://evil.example"}
        ),
    ):
        pytest.fail("cross-site socket accepted")
    with client.websocket_connect("/api/live") as ws:
        start(ws)
        ws.send_bytes(b"odd")
        assert ws.receive_json()["type"] == "error"
