"""UI test fixture only: python tests/ui_server.py. No models, network downloads or GPU."""

import argparse
import tempfile
from pathlib import Path

import uvicorn
from fakes import FakeBackend, FakeProcessor, FakeTranslator, Response

from lecturebridge.server import create_app

SENTENCES = [
    "Learning is not just about remembering information. It is about making connections.",
    "When we connect a new idea to something we already know, it becomes easier to understand.",
    "Think of a concept you learned this week. How does it relate to your own experience?",
    "A good question can be more valuable than a quick answer.",
]
TRANSLATIONS = [
    "Học không chỉ là ghi nhớ thông tin. Đó còn là việc tạo ra những kết nối.",
    "Khi kết nối một ý tưởng mới với điều đã biết, chúng ta sẽ dễ hiểu hơn.",
    "Hãy nghĩ về một khái niệm bạn đã học tuần này. Nó liên quan thế nào đến trải nghiệm của bạn?",
    "Một câu hỏi hay có thể giá trị hơn một câu trả lời vội vàng.",
]


class UIProcessor(FakeProcessor):
    def __init__(self):
        super().__init__()
        self.samples = 0

    async def process_audio(self, pcm):
        if not pcm:
            await self.queue.put(None)
            return
        self.samples += len(pcm) // 2
        index = len(self.lines)
        if self.samples >= (index + 1) * 16000 and index < len(SENTENCES):
            self.lines.append(
                {"start": index, "end": index + 1, "text": SENTENCES[index]}
            )
            await self.queue.put(Response(self.lines))


class UIBackend(FakeBackend):
    def processor(self):
        return UIProcessor()


class UITranslator(FakeTranslator):
    async def translate(self, text):
        return TRANSLATIONS[SENTENCES.index(text)]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="lecturebridge-ui-") as directory:
        app = create_app(
            UIBackend(), data_dir=Path(directory), translator=UITranslator()
        )
        uvicorn.run(app, host="127.0.0.1", port=args.port, log_level="warning")
