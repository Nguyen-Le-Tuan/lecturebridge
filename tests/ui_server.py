"""UI test fixture only: python tests/ui_server.py. No models, network downloads or GPU."""

import argparse
import tempfile
from pathlib import Path

import uvicorn
from fakes import FakeBackend, FakeProcessor, FakeTranslator, Response

from lecturebridge.languages import LANGUAGES
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
SOURCES = {
    "en": SENTENCES,
    "zh": [
        "学习不仅仅是记住信息。它还意味着建立联系。",
        "当我们把新想法与已知的知识联系起来时，就更容易理解。",
        "想一想你这周学到的一个概念。它与你的经历有什么关系？",
        "一个好问题可能比一个快速的答案更有价值。",
    ],
    "zh-Hant": [
        "學習不僅僅是記住資訊。它還意味著建立聯繫。",
        "當我們把新想法與已知的知識聯繫起來時，就更容易理解。",
        "想一想你這週學到的一個概念。它與你的經歷有什麼關係？",
        "一個好問題可能比一個快速的答案更有價值。",
    ],
    "ja": [
        "学ぶことは情報を覚えるだけではありません。つながりを作ることです。",
        "新しい考えを知っていることと結びつけると、理解しやすくなります。",
        "今週学んだ概念は、自分の経験とどのように関係していますか？",
        "良い質問は素早い答えよりも価値があるかもしれません。",
    ],
    "ko": [
        "배움은 정보를 기억하는 것만이 아닙니다. 연결을 만드는 것입니다.",
        "새로운 생각을 이미 아는 것과 연결하면 이해하기 쉬워집니다.",
        "이번 주에 배운 개념은 자신의 경험과 어떤 관련이 있나요?",
        "좋은 질문은 빠른 답변보다 더 가치가 있을 수 있습니다.",
    ],
}


class UIProcessor(FakeProcessor):
    def __init__(self, language="en"):
        super().__init__()
        self.sentences = SOURCES[language]
        self.samples = 0

    async def process_audio(self, pcm):
        if not pcm:
            await self.queue.put(None)
            return
        self.samples += len(pcm) // 2
        index = len(self.lines)
        if self.samples >= (index + 1) * 16000 and index < len(self.sentences):
            self.lines.append(
                {"start": index, "end": index + 1, "text": self.sentences[index]}
            )
            await self.queue.put(Response(self.lines))


class UIBackend(FakeBackend):
    def __init__(self, language="en"):
        self.language = language

    def processor(self):
        return UIProcessor(self.language)


class UITranslator(FakeTranslator):
    def __init__(self, language="en"):
        super().__init__()
        self.sentences = SOURCES[language]

    async def translate(self, text):
        return TRANSLATIONS[self.sentences.index(text)]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--language", choices=tuple(LANGUAGES), default="en")
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="lecturebridge-ui-") as directory:
        app = create_app(
            UIBackend(args.language),
            data_dir=Path(directory),
            translator=UITranslator(args.language),
        )
        uvicorn.run(app, host="127.0.0.1", port=args.port, log_level="warning")
