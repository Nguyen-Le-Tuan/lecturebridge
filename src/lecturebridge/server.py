"""LectureBridge local studio, recording API and PCM WebSocket gateway."""

from __future__ import annotations

import asyncio
import json
import sqlite3
import time
from contextlib import asynccontextmanager
from pathlib import Path
from urllib.parse import urlsplit

from anyio import CancelScope
from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, JSONResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from filelock import FileLock

from lecturebridge.languages import source_language
from lecturebridge.storage import Library, Recorder, default_data_dir
from lecturebridge.transcript import Transcript, export_text
from lecturebridge.translation import TranslationService

MAX_SESSION_SECONDS = 7200
STORAGE_ERRORS = (OSError, sqlite3.Error)


def same_origin(origin: str | None, host: str) -> bool:
    if origin is None:
        return True  # CLI clients do not send Origin.
    parsed = urlsplit(origin)
    return parsed.scheme in {"http", "https"} and parsed.netloc == host


def trusted_host(host: str) -> bool:
    name = host.split(":")[0].lower()
    return name in {"localhost", "127.0.0.1", "testserver"} or name.endswith(".ts.net")


def create_app(
    backend,
    *,
    data_dir: Path | None = None,
    translator=None,
    translation_default: bool = False,
) -> FastAPI:
    language = getattr(backend, "language", "en")
    language_profile = source_language(language)
    service = translator or TranslationService(language)

    @asynccontextmanager
    async def lifespan(app):
        app.state.library = Library(data_dir or default_data_dir())
        with FileLock(str(app.state.library.root / "library.lock"), timeout=0):
            await asyncio.to_thread(app.state.library.recover)
            app.state.busy = False
            app.state.active_recording = None
            try:
                await backend.start()
                if translation_default:
                    service.begin_prepare()
                yield
            finally:
                await service.close()
                await backend.close()

    app = FastAPI(lifespan=lifespan)
    web = Path(__file__).with_name("web")

    @app.middleware("http")
    async def private_origin(request: Request, call_next):
        if (
            not trusted_host(request.headers.get("host", ""))
            or not same_origin(
                request.headers.get("origin"), request.headers.get("host", "")
            )
            or request.headers.get("sec-fetch-site") == "cross-site"
        ):
            return JSONResponse(
                {"detail": "Access requires the local or private Tailscale origin"}, 403
            )
        response = await call_next(request)
        response.headers["Cache-Control"] = "no-store"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; script-src 'self'; style-src 'self'; "
            "connect-src 'self'; media-src 'self' blob:; img-src 'self' data:; "
            "object-src 'none'; frame-ancestors 'none'; base-uri 'self'"
        )
        return response

    @app.get("/")
    async def index():
        return FileResponse(web / "index.html")

    @app.get("/health")
    async def health():
        return {"status": "ok", "backend": "faster-whisper", "ready": True}

    @app.get("/api/capabilities")
    async def capabilities():
        return {
            "translation": service.capabilities(),
            "translation_default": translation_default,
            "busy": app.state.busy,
            "max_session_seconds": MAX_SESSION_SECONDS,
            "model": getattr(backend, "model", "test"),
            "language": language,
            "language_label": language_profile.label,
            "storage": "local",
        }

    @app.post("/api/translation/prepare", status_code=202)
    async def prepare_translation(request: Request):
        body = await request.json()
        if body != {"download": True}:
            raise HTTPException(400, "Explicit download consent required")
        service.begin_prepare(download=True)
        return {"status": "preparing"}

    def recording(recording_id):
        try:
            return app.state.library.get(recording_id)
        except (KeyError, ValueError):
            raise HTTPException(404, "Recording not found") from None

    @app.get("/api/recordings")
    async def recordings():
        return await asyncio.to_thread(app.state.library.list)

    @app.get("/api/recordings/{recording_id}")
    async def recording_detail(recording_id: str):
        return recording(recording_id)

    @app.patch("/api/recordings/{recording_id}")
    async def rename(recording_id: str, request: Request):
        recording(recording_id)
        body = await request.json()
        title = body.get("title") if isinstance(body, dict) else None
        if not isinstance(title, str) or not 1 <= len(title.strip()) <= 120:
            raise HTTPException(400, "Title must contain 1-120 characters")
        await asyncio.to_thread(
            app.state.library.update, recording_id, title=title.strip()
        )
        return recording(recording_id)

    @app.delete("/api/recordings/{recording_id}")
    async def delete(recording_id: str):
        item = recording(recording_id)
        if item["status"] == "recording" or app.state.active_recording == recording_id:
            raise HTTPException(409, "Stop recording before deleting it")
        await asyncio.to_thread(app.state.library.delete, recording_id)
        return {"deleted": True}

    @app.get("/api/recordings/{recording_id}/audio")
    async def audio(recording_id: str, download: bool = False):
        item = recording(recording_id)
        if item["status"] == "recording":
            raise HTTPException(409, "Recording is still active")
        path = app.state.library.audio_path(recording_id)
        if not path.is_file():
            raise HTTPException(404, "Audio unavailable")
        return FileResponse(
            path,
            media_type="audio/wav",
            filename=f"lecturebridge-{recording_id}.wav" if download else None,
        )

    @app.get("/api/recordings/{recording_id}/export")
    async def export(recording_id: str, format: str = "txt"):
        item = recording(recording_id)
        if format not in {"txt", "json"}:
            raise HTTPException(400, "Use txt or json")
        headers = {
            "Content-Disposition": f'attachment; filename="lecturebridge-{recording_id}.{format}"'
        }
        if format == "json":
            return JSONResponse(item, headers=headers)
        return PlainTextResponse(export_text(item["segments"]), headers=headers)

    @app.websocket("/asr")
    @app.websocket("/api/live")
    async def live(socket: WebSocket):
        if not trusted_host(socket.headers.get("host", "")) or not same_origin(
            socket.headers.get("origin"), socket.headers.get("host", "")
        ):
            await socket.close(code=4403)
            return
        if app.state.busy:
            await socket.accept()
            await socket.send_json(
                {"type": "error", "message": "Một phiên khác đang hoạt động."}
            )
            await socket.close(code=4429)
            return
        app.state.busy = True
        await socket.accept()
        legacy = socket.url.path == "/asr"
        processor = None
        recorder = None
        transcript = Transcript(language=language)
        send_lock = asyncio.Lock()
        updates_lock = asyncio.Lock()
        recording_lock = asyncio.Lock()
        translation_queue = asyncio.Queue(maxsize=16)
        tasks = []
        receive_task = None
        translation_task = None
        completed = False
        bytes_received = 0
        last_checkpoint = 0.0

        async def send(payload):
            async with send_lock:
                await socket.send_json(payload)

        async def recording_io(callback, *args, **kwargs):
            # Finish an in-flight disk operation before cancellation can close its file.
            async with recording_lock:
                operation = asyncio.create_task(
                    asyncio.to_thread(callback, *args, **kwargs)
                )
                try:
                    return await asyncio.shield(operation)
                except asyncio.CancelledError:
                    await operation
                    raise

        async def publish():
            nonlocal last_checkpoint
            if not legacy:
                await send({"type": "transcript", "segments": transcript.snapshot()})
            if (
                recorder
                and not recorder.failed
                and time.monotonic() - last_checkpoint >= 1
            ):
                try:
                    await recording_io(recorder.checkpoint, transcript.snapshot())
                    last_checkpoint = time.monotonic()
                except STORAGE_ERRORS:
                    recorder.failed = True
                    await send(
                        {
                            "type": "recording_error",
                            "message": "Không thể lưu thêm dữ liệu. Transcript vẫn tiếp tục.",
                        }
                    )

        def enqueue(segments):
            for segment in segments:
                if segment["translation_status"] != "pending":
                    continue
                try:
                    translation_queue.put_nowait(segment)
                except asyncio.QueueFull:
                    segment["translation_status"] = "skipped"

        async def translation_loop():
            while True:
                segment = await translation_queue.get()
                try:
                    if (
                        not transcript.translation_enabled
                        or segment["epoch"] != transcript.epoch
                    ):
                        segment["translation_status"] = "off"
                        continue
                    ready = (
                        await asyncio.shield(service.prepare_task)
                        if service.prepare_task
                        else False
                    )
                    if not ready:
                        segment["translation_status"] = "unavailable"
                        await send(
                            {"type": "translation_state", **service.capabilities()}
                        )
                    else:
                        result = await service.translate(segment["text"])
                        async with updates_lock:
                            if (
                                transcript.translation_enabled
                                and segment["epoch"] == transcript.epoch
                            ):
                                segment["translation"] = result
                                segment["translation_status"] = "ready"
                            else:
                                segment["translation_status"] = "off"
                except RuntimeError:
                    segment["translation_status"] = "error"
                    await send({"type": "translation_state", **service.capabilities()})
                finally:
                    translation_queue.task_done()
                await publish()

        async def translation_ready():
            await asyncio.shield(service.begin_prepare())
            await send({"type": "translation_state", **service.capabilities()})

        async def set_translation(enabled):
            async with updates_lock:
                enqueue(transcript.flush())
                transcript.translation_enabled = enabled
                transcript.epoch += 1
                for segment in transcript.segments:
                    if segment["translation_status"] == "pending":
                        segment["translation_status"] = "off"
                await publish()
            if enabled:
                tasks.append(asyncio.create_task(translation_ready()))
                await send({"type": "translation_state", "state": "loading"})
            else:
                await send({"type": "translation_state", "state": "off"})

        async def results():
            generator = await processor.create_tasks()
            async for response in generator:
                raw = response.to_dict()
                if raw.get("error"):
                    raise RuntimeError("ASR failed")
                async with updates_lock:
                    enqueue(transcript.ingest(raw.get("lines", [])))
                    await publish()
                if legacy:
                    await send(raw)
                else:
                    await send(
                        {
                            "type": "partial",
                            "text": raw.get("buffer_transcription", ""),
                            "lag": raw.get(
                                "remaining_time_transcription_processing", 0
                            ),
                        }
                    )
            enqueue(transcript.flush())
            try:
                await asyncio.wait_for(translation_queue.join(), timeout=5)
            except TimeoutError:
                pass
            translation_task.cancel()
            await asyncio.gather(translation_task, return_exceptions=True)
            for segment in transcript.segments:
                if segment["translation_status"] == "pending":
                    segment["translation_status"] = "skipped"
            await publish()

        try:
            options = (
                {} if legacy else await asyncio.wait_for(socket.receive_json(), 30)
            )
            if not legacy and (
                not isinstance(options, dict)
                or options.get("type") != "start"
                or not isinstance(options.get("save", False), bool)
                or not isinstance(options.get("translation", False), bool)
            ):
                raise ValueError("Invalid start message")
            title = options.get("title", "Bài giảng mới")
            if not isinstance(title, str) or len(title) > 120:
                raise ValueError("Invalid title")
            if options.get("save"):
                recorder = Recorder(app.state.library, title)
                app.state.active_recording = recorder.id
            processor = backend.processor()
            started = time.monotonic()
            await send(
                {
                    "type": "config",
                    "useAudioWorklet": True,
                    "sample_rate": 16000,
                    "recording_id": recorder.id if recorder else None,
                    "language": language,
                    "language_label": language_profile.label,
                }
            )
            translation_task = asyncio.create_task(translation_loop())
            tasks.append(translation_task)
            result_task = asyncio.create_task(results())
            tasks.append(result_task)
            if options.get("translation", translation_default):
                await set_translation(True)
            stopping = False
            while not stopping:
                receive_task = asyncio.create_task(socket.receive())
                done, _ = await asyncio.wait(
                    [receive_task, result_task], return_when=asyncio.FIRST_COMPLETED
                )
                if result_task in done:
                    receive_task.cancel()
                    await asyncio.gather(receive_task, return_exceptions=True)
                    await result_task
                    raise RuntimeError("ASR ended before stop")
                message = receive_task.result()
                if message["type"] == "websocket.disconnect":
                    raise WebSocketDisconnect()
                if message.get("bytes") is not None:
                    pcm = message["bytes"]
                    if len(pcm) > 64000 or len(pcm) % 2:
                        raise ValueError("Invalid PCM frame")
                    if not pcm:
                        stopping = True
                    else:
                        bytes_received += len(pcm)
                        duration = bytes_received / 32000
                        if (
                            duration > MAX_SESSION_SECONDS
                            or duration > time.monotonic() - started + 8
                        ):
                            raise ValueError("Audio limit exceeded")
                        if recorder and not recorder.failed:
                            try:
                                await recording_io(recorder.write, pcm)
                            except STORAGE_ERRORS:
                                recorder.failed = True
                                await send(
                                    {
                                        "type": "recording_error",
                                        "message": "Lưu audio bị gián đoạn. Transcript vẫn tiếp tục.",
                                    }
                                )
                        await processor.process_audio(pcm)
                elif message.get("text"):
                    if len(message["text"]) > 4096:
                        raise ValueError("Control message too large")
                    control = json.loads(message["text"])
                    if not isinstance(control, dict):
                        raise ValueError("Invalid control")
                    if control.get("type") == "translation" and isinstance(
                        control.get("enabled"), bool
                    ):
                        await set_translation(control["enabled"])
                    elif control.get("type") == "stop":
                        stopping = True
                    else:
                        raise ValueError("Unknown control")
                if stopping:
                    await processor.process_audio(b"")
                    await asyncio.wait_for(asyncio.shield(result_task), 30)
            if recorder:
                await recording_io(recorder.close, transcript.snapshot())
            completed = True
            await send(
                {
                    "type": "ready_to_stop",
                    "recording_id": recorder.id if recorder else None,
                    "recording_interrupted": bool(recorder and recorder.failed),
                }
            )
        except WebSocketDisconnect:
            pass
        except (TimeoutError, ValueError, RuntimeError, *STORAGE_ERRORS):
            try:
                await send(
                    {
                        "type": "error",
                        "message": "Phiên đã gián đoạn. Kiểm tra kết nối, dung lượng hoặc khởi động lại phiên.",
                    }
                )
            except (RuntimeError, WebSocketDisconnect):
                pass
        finally:
            # ASGI test clients and server shutdown may cancel the handler here.
            # Complete disk finalization before releasing the one-session lock.
            with CancelScope(shield=True):
                if receive_task and not receive_task.done():
                    receive_task.cancel()
                    await asyncio.gather(receive_task, return_exceptions=True)
                for task in tasks:
                    task.cancel()
                await asyncio.gather(*tasks, return_exceptions=True)
                try:
                    if processor:
                        await processor.cleanup()
                finally:
                    if recorder and not recorder.closed:
                        try:
                            await recording_io(
                                recorder.close,
                                transcript.snapshot(),
                                interrupted=not completed,
                            )
                        except STORAGE_ERRORS:
                            pass  # Next launch repairs the flushed PCM header.
                    app.state.active_recording = None
                    app.state.busy = False
                try:
                    await socket.close()
                except (RuntimeError, WebSocketDisconnect):
                    pass

    app.mount("/assets", StaticFiles(directory=web), name="assets")
    return app
