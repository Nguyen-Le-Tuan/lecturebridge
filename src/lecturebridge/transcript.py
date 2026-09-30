"""Convert cumulative WLK committed lines into stable, translatable paragraphs."""

from __future__ import annotations

import re


def seconds(value: str | float | None) -> float:
    if value is None:
        return 0.0
    result = 0.0
    for part in str(value).split(":"):
        result = result * 60 + float(part)
    return result


class Transcript:
    def __init__(self):
        self.segments: list[dict] = []
        self.pending: dict | None = None
        self.seen: dict[str, tuple[str, float]] = {}
        self.translation_enabled = False
        self.epoch = 0
        self.last_line: str | None = None

    def flush(self) -> list[dict]:
        if not self.pending:
            return []
        segment = self.pending
        segment["text"] = segment["text"].strip()
        segment["final"] = True
        self.segments.append(segment)
        self.pending = None
        return [segment]

    def ingest(self, lines: list[dict]) -> list[dict]:
        completed = []
        for line in lines:
            text = line.get("text") or ""
            if not text.strip():
                continue
            key = str(line.get("start", 0))
            start, end = seconds(line.get("start")), seconds(line.get("end"))
            previous, previous_end = self.seen.get(key, ("", start))
            if text == previous:
                continue
            # Committed WLK lines only grow; never duplicate a revised snapshot.
            if not text.startswith(previous):
                continue
            addition = text[len(previous) :]
            self.seen[key] = (text, end)
            if self.last_line != key:
                completed.extend(self.flush())
                self.last_line = key
            if self.pending is None:
                self.pending = {
                    "id": len(self.segments) + 1,
                    "start": previous_end,
                    "end": end,
                    "text": "",
                    "translation": None,
                    "translation_status": "pending"
                    if self.translation_enabled
                    else "off",
                    "epoch": self.epoch,
                    "final": False,
                }
            self.pending["text"] += addition
            self.pending["end"] = end
            if (
                re.search(r"[.!?][\s\"\u201d]*$", self.pending["text"])
                or end - self.pending["start"] >= 8
                or len(self.pending["text"]) >= 400
            ):
                completed.extend(self.flush())
        return completed

    def snapshot(self) -> list[dict]:
        return [
            dict(item)
            for item in self.segments + ([self.pending] if self.pending else [])
        ]


def export_text(segments: list[dict]) -> str:
    return "\n\n".join(
        f"[{int(item['start']) // 60:02}:{int(item['start']) % 60:02}] {item['text']}"
        + (f"\n{item['translation']}" if item.get("translation") else "")
        for item in segments
    )
