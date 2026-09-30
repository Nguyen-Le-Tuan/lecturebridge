"""Private, single-owner recording library. No audio is stored without opt-in."""

from __future__ import annotations

import json
import os
import sqlite3
import struct
import sys
import uuid
import wave
from contextlib import closing
from datetime import UTC, datetime
from pathlib import Path


def default_data_dir() -> Path:
    if sys.platform == "win32":
        return (
            Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData/Local"))
            / "LectureBridge"
        )
    return (
        Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local/share"))
        / "lecturebridge"
    )


def repair_wav(path: Path) -> int:
    """Repair the fixed PCM header after interruption, discarding an odd byte."""
    size = max(0, path.stat().st_size - 44) // 2 * 2
    with path.open("r+b") as file:
        file.truncate(44 + size)
        file.seek(0)
        file.write(
            struct.pack(
                "<4sI4s4sIHHIIHH4sI",
                b"RIFF",
                size + 36,
                b"WAVE",
                b"fmt ",
                16,
                1,
                1,
                16000,
                32000,
                2,
                16,
                b"data",
                size,
            )
        )
    return size


class Library:
    def __init__(self, root: Path):
        self.root = root.expanduser().resolve()
        self.root.mkdir(parents=True, exist_ok=True, mode=0o700)
        self.database = self.root / "library.sqlite3"
        with closing(self.connect()) as db, db:
            db.execute("""CREATE TABLE IF NOT EXISTS recordings (
                id TEXT PRIMARY KEY, title TEXT NOT NULL, created TEXT NOT NULL,
                status TEXT NOT NULL, duration REAL NOT NULL DEFAULT 0,
                bytes INTEGER NOT NULL DEFAULT 0, segments TEXT NOT NULL DEFAULT '[]'
            )""")
        if os.name != "nt":
            self.database.chmod(0o600)

    def connect(self):
        db = sqlite3.connect(self.database, timeout=5)
        db.row_factory = sqlite3.Row
        return db

    def audio_path(self, recording_id: str) -> Path:
        if str(uuid.UUID(recording_id)) != recording_id:
            raise ValueError("invalid recording ID")
        return self.root / f"{recording_id}.wav"

    def recover(self) -> None:
        for item in self.list():
            if item["status"] == "recording":
                path = self.audio_path(item["id"])
                size = repair_wav(path) if path.exists() else 0
                self.update(
                    item["id"], status="interrupted", duration=size / 32000, size=size
                )

    def create(self, title: str) -> str:
        recording_id = str(uuid.uuid4())
        with closing(self.connect()) as db, db:
            db.execute(
                "INSERT INTO recordings (id, title, created, status) VALUES (?, ?, ?, ?)",
                (
                    recording_id,
                    title.strip()[:120] or "Bài giảng mới",
                    datetime.now(UTC).isoformat(),
                    "recording",
                ),
            )
        return recording_id

    def list(self) -> list[dict]:
        with closing(self.connect()) as db:
            return [
                dict(row)
                for row in db.execute(
                    "SELECT id, title, created, status, duration, bytes FROM recordings ORDER BY created DESC"
                )
            ]

    def get(self, recording_id: str) -> dict:
        self.audio_path(recording_id)
        with closing(self.connect()) as db:
            row = db.execute(
                "SELECT * FROM recordings WHERE id = ?", (recording_id,)
            ).fetchone()
        if row is None:
            raise KeyError(recording_id)
        result = dict(row)
        result["segments"] = json.loads(result["segments"])
        return result

    def update(
        self,
        recording_id: str,
        *,
        status: str | None = None,
        duration: float | None = None,
        size: int | None = None,
        segments: list | None = None,
        title: str | None = None,
    ) -> None:
        values = {
            "status": status,
            "duration": duration,
            "bytes": size,
            "title": title,
            "segments": json.dumps(segments, ensure_ascii=False)
            if segments is not None
            else None,
        }
        fields = {key: value for key, value in values.items() if value is not None}
        if not fields:
            return
        with closing(self.connect()) as db, db:
            db.execute(
                f"UPDATE recordings SET {', '.join(f'{key} = ?' for key in fields)} WHERE id = ?",
                (*fields.values(), recording_id),
            )

    def delete(self, recording_id: str) -> None:
        item = self.get(recording_id)
        if item["status"] == "recording":
            raise RuntimeError("recording is active")
        self.audio_path(recording_id).unlink(missing_ok=True)
        with closing(self.connect()) as db, db:
            db.execute("DELETE FROM recordings WHERE id = ?", (recording_id,))


class Recorder:
    def __init__(self, library: Library, title: str):
        self.library = library
        self.id = library.create(title)
        self.size = 0
        self.failed = False
        self.closed = False
        try:
            self.file = library.audio_path(self.id).open("wb")
            if os.name != "nt":
                library.audio_path(self.id).chmod(0o600)
            self.wav = wave.open(self.file, "wb")  # noqa: SIM115 - closed by session
            self.wav.setparams((1, 2, 16000, 0, "NONE", "not compressed"))
            self.wav.writeframes(b"")
            self.file.flush()
        except OSError:
            if hasattr(self, "file"):
                self.file.close()
            library.audio_path(self.id).unlink(missing_ok=True)
            library.update(self.id, status="interrupted")
            raise

    def write(self, pcm: bytes) -> None:
        if len(pcm) % 2:
            raise ValueError("PCM16 requires whole samples")
        self.wav.writeframes(pcm)
        self.file.flush()
        self.size += len(pcm)

    def checkpoint(self, segments: list[dict]) -> None:
        self.library.update(
            self.id, duration=self.size / 32000, size=self.size, segments=segments
        )

    def close(self, segments: list[dict], *, interrupted: bool = False) -> None:
        if self.closed:
            return
        self.closed = True
        try:
            self.wav.close()
        finally:
            self.file.close()
        size = repair_wav(self.library.audio_path(self.id))
        self.library.update(
            self.id,
            segments=segments,
            duration=size / 32000,
            size=size,
            status="interrupted" if interrupted or self.failed else "complete",
        )
