"""Deterministic ASR/translation doubles. Never import or load ML models."""

import asyncio


class Response:
    def __init__(self, lines):
        self.lines = lines

    def to_dict(self):
        return {
            "lines": list(self.lines),
            "buffer_transcription": "",
            "remaining_time_transcription_processing": 0,
        }


class FakeProcessor:
    def __init__(self):
        self.queue = asyncio.Queue()
        self.lines = []
        self.clean = False

    async def process_audio(self, pcm):
        if pcm:
            index = len(self.lines)
            self.lines.append(
                {
                    "start": index,
                    "end": index + 1,
                    "text": f"This is sentence {index + 1}.",
                }
            )
            await self.queue.put(Response(self.lines))
        else:
            await self.queue.put(None)

    async def create_tasks(self):
        async def results():
            while (response := await self.queue.get()) is not None:
                yield response

        return results()

    async def cleanup(self):
        self.clean = True


class FakeBackend:
    model = "test-double-no-model"

    async def start(self):
        pass

    def processor(self):
        self.last_processor = FakeProcessor()
        return self.last_processor

    async def close(self):
        pass


class FakeTranslator:
    def __init__(self, *, missing=False, fail=False):
        self.state = "idle"
        self.missing = missing
        self.fail = fail
        self.calls = []
        self.prepare_task = None

    def capabilities(self):
        return {
            "state": self.state,
            "download_bytes": 2500000000,
            "license": "cc-by-nc-4.0",
            "device": "cpu",
        }

    def begin_prepare(self, download=False):
        async def prepare():
            if download:
                self.missing = False
            self.state = "missing" if self.missing else "ready"
            return not self.missing

        self.prepare_task = asyncio.create_task(prepare())
        return self.prepare_task

    async def translate(self, text):
        self.calls.append(text)
        if self.fail:
            self.state = "error"
            raise RuntimeError("test failure")
        return f"Bản dịch: {text}"

    async def close(self):
        pass
