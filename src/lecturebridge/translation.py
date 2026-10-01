"""Lazy model preparation and a single isolated translation worker."""

from __future__ import annotations

import asyncio
import json
import os
import sys
from pathlib import Path

from lecturebridge.languages import source_language
from lecturebridge.model_store import (
    TRANSLATION_MODEL,
    load_locked_models,
    model_directory,
)


class TranslationService:
    def __init__(self, language: str = "en"):
        self.source_code = source_language(language).nllb
        self.state = "idle"
        self.process = None
        self.lock = asyncio.Lock()
        self.prepare_task = None
        self.directory: Path | None = None

    def capabilities(self) -> dict:
        model = load_locked_models()[TRANSLATION_MODEL]
        return {
            "state": self.state,
            "download_bytes": sum(file.size for file in model.files.values()),
            "license": model.license,
            "device": "cpu",
        }

    async def prepare(self, download: bool = False) -> bool:
        async with self.lock:
            if self.process is not None and self.process.returncode is None:
                return True
            self.state = "downloading" if download else "loading"
            try:
                self.directory = await asyncio.to_thread(
                    model_directory, TRANSLATION_MODEL, download=download
                )
            except (OSError, RuntimeError, ValueError):
                self.state = "missing" if not download else "error"
                return False
            self.state = "loading"
            env = dict(
                os.environ,
                CUDA_VISIBLE_DEVICES="-1",
                OMP_NUM_THREADS="2",
                TOKENIZERS_PARALLELISM="false",
                PYTHONIOENCODING="utf-8",
            )
            try:
                self.process = await asyncio.create_subprocess_exec(
                    sys.executable,
                    "-m",
                    "lecturebridge.translation_worker",
                    str(self.directory),
                    stdin=asyncio.subprocess.PIPE,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.DEVNULL,
                    env=env,
                )
                line = await asyncio.wait_for(
                    self.process.stdout.readline(), timeout=90
                )
                if not json.loads(line).get("ready"):
                    raise RuntimeError("worker failed")
            except asyncio.CancelledError:
                await self.stop_worker()
                self.state = "idle"
                raise
            except (TimeoutError, OSError, ValueError, RuntimeError):
                await self.stop_worker()
                self.state = "error"
                return False
            self.state = "ready"
            return True

    async def translate(self, text: str) -> str:
        async with self.lock:
            if self.state != "ready" or self.process is None:
                raise RuntimeError("translation unavailable")
            try:
                request = {"text": text, "source_language": self.source_code}
                self.process.stdin.write((json.dumps(request) + "\n").encode())
                await self.process.stdin.drain()
                line = await asyncio.wait_for(
                    self.process.stdout.readline(), timeout=30
                )
                result = json.loads(line)
                if not result.get("text"):
                    raise RuntimeError("translation failed")
                return result["text"]
            except asyncio.CancelledError:
                # A cancelled read must not leave a stale reply for the next request.
                await self.stop_worker()
                self.state = "idle"
                raise
            except (TimeoutError, OSError, ValueError, RuntimeError) as exc:
                self.state = "error"
                await self.stop_worker()
                raise RuntimeError("translation unavailable") from exc

    def begin_prepare(self, download: bool = False):
        if self.prepare_task is None or self.prepare_task.done():
            self.prepare_task = asyncio.create_task(self.prepare(download))
        return self.prepare_task

    async def stop_worker(self):
        if self.process and self.process.returncode is None:
            try:
                self.process.terminate()
            except ProcessLookupError:
                pass
            try:
                await asyncio.wait_for(self.process.wait(), 5)
            except TimeoutError:
                self.process.kill()
                await self.process.wait()
        self.process = None

    async def close(self):
        if self.prepare_task and not self.prepare_task.done():
            self.prepare_task.cancel()
            await asyncio.gather(self.prepare_task, return_exceptions=True)
        await self.stop_worker()
