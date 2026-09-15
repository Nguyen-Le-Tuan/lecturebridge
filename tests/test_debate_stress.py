"""Opt-in live GPU acceptance test for a permitted debate-like recording."""

from __future__ import annotations

import asyncio
import logging
import os
import signal
import socket
import subprocess
import sys
import time
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

import pytest
from whisperlivekit.test_client import transcribe_audio

AUDIO_ENV = "LECTUREBRIDGE_DEBATE_AUDIO"


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.bind(("127.0.0.1", 0))
        return int(probe.getsockname()[1])


def _wait_until_ready(port: int, timeout: float = 90.0) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            with urlopen(f"http://127.0.0.1:{port}/health", timeout=1) as response:
                if response.status == 200:
                    return
        except (OSError, URLError):
            time.sleep(0.25)
    raise AssertionError("live debate server did not become ready")


@pytest.mark.gpu
@pytest.mark.skipif(not os.environ.get(AUDIO_ENV), reason=f"set {AUDIO_ENV}")
def test_live_debate_latency_and_english_only() -> None:
    audio = Path(os.environ[AUDIO_ENV])
    assert audio.is_file(), "debate audio file is missing"
    port = _free_port()
    server = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "lecturebridge.live",
            "--port",
            str(port),
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        text=True,
    )

    try:
        _wait_until_ready(port)
        logging.getLogger("whisperlivekit.test_client").setLevel(logging.WARNING)
        started = time.perf_counter()
        first_text: float | None = None
        max_processing = 0.0
        max_policy = 0.0
        translation_seen = False

        def observe(message: dict[str, object]) -> None:
            nonlocal first_text, max_processing, max_policy, translation_seen
            lines = message.get("lines") or []
            buffer = message.get("buffer_transcription") or ""
            if first_text is None and (lines or buffer):
                first_text = time.perf_counter() - started
            max_processing = max(
                max_processing,
                float(message.get("remaining_time_transcription_processing") or 0),
            )
            max_policy = max(
                max_policy,
                float(message.get("remaining_time_transcription_policy") or 0),
            )
            translation_seen = translation_seen or bool(
                message.get("buffer_translation")
            ) or any(bool(line.get("translation")) for line in lines)

        result = asyncio.run(
            transcribe_audio(
                str(audio),
                url=f"ws://127.0.0.1:{port}/asr",
                speed=1.0,
                timeout=30.0,
                on_response=observe,
            )
        )
        elapsed = time.perf_counter() - started

        assert result.text.strip()
        assert first_text is not None and first_text < 2.0
        assert max_processing < 3.0
        assert max_policy < 5.0
        assert elapsed < result.audio_duration + 5.0
        assert not translation_seen
    finally:
        server.send_signal(signal.SIGINT)
        try:
            server.wait(timeout=15)
        except subprocess.TimeoutExpired:
            server.terminate()
            server.wait(timeout=5)
