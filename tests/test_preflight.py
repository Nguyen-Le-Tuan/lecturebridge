import json
import subprocess
from pathlib import Path

from lecturebridge.preflight import (
    FAIL,
    PASS,
    Check,
    cache_check,
    peer_check,
    port_check,
    python_check,
)


def test_python_check_accepts_expected_virtual_environment(
    monkeypatch,
    tmp_path: Path,
) -> None:
    expected = tmp_path / ".venv"
    expected.mkdir()
    monkeypatch.setattr("lecturebridge.preflight.sys.prefix", str(expected))

    result = python_check(tmp_path)

    assert result.passed


def test_check_is_immutable_result() -> None:
    result = Check("GPU", PASS, "ready")

    assert result.name == "GPU"
    assert result.status == PASS
    assert result.passed is True
    assert result.detail == "ready"


def test_failed_check_is_not_passing() -> None:
    assert not Check("GPU", FAIL, "missing").passed


def test_model_cache_is_mode_aware(monkeypatch, tmp_path: Path) -> None:
    hub = tmp_path / "hub"
    model = (
        hub
        / "models--distil-whisper--distil-large-v3.5-ct2"
        / "snapshots"
        / "9793ccc07920e0f830e1dba0343efcdf0ef8c903"
    )
    model.mkdir(parents=True)
    monkeypatch.setattr(
        "lecturebridge.preflight.verify_snapshot",
        lambda locked, path: [] if path.is_dir() else ["missing"],
    )

    english_only = cache_check(tmp_path, hub=hub)
    translated = cache_check(tmp_path, hub=hub, translation_enabled=True)

    assert english_only.passed
    assert "NLLB=not required" in english_only.detail
    assert not translated.passed
    assert "NLLB=missing" in translated.detail

    (
        hub
        / "models--entai2965--nllb-200-distilled-600M-ctranslate2"
        / "snapshots"
        / "86876131d0a16b17ced0a5c558fdc3e4613ae545"
    ).mkdir(parents=True)
    assert cache_check(
        tmp_path,
        hub=hub,
        translation_enabled=True,
    ).passed


def test_peer_check_reports_direct_and_relay_routes(monkeypatch) -> None:
    direct = subprocess.CompletedProcess(
        [],
        0,
        stdout="pong from ipad via 10.0.0.2:41641 in 5ms\n",
        stderr="",
    )
    monkeypatch.setattr("lecturebridge.preflight.run_command", lambda command: direct)
    assert "direct:" in peer_check("ipad").detail

    relay = subprocess.CompletedProcess(
        [],
        0,
        stdout="pong from ipad via DERP(nyc) in 40ms\n",
        stderr="",
    )
    monkeypatch.setattr("lecturebridge.preflight.run_command", lambda command: relay)
    result = peer_check("ipad")
    assert result.passed
    assert "relay:" in result.detail


class _OpenSocket:
    def __enter__(self):
        return self

    def __exit__(self, *args: object) -> None:
        return None

    def settimeout(self, timeout: float) -> None:
        return None

    def connect_ex(self, address: tuple[str, int]) -> int:
        return 0


class _JsonResponse:
    def __init__(self, payload: dict[str, object], status: int = 200) -> None:
        self.payload = payload
        self.status = status

    def __enter__(self):
        return self

    def __exit__(self, *args: object) -> None:
        return None

    def read(self) -> bytes:
        return json.dumps(self.payload).encode()


def test_port_check_verifies_running_model(monkeypatch) -> None:
    monkeypatch.setattr("lecturebridge.preflight.socket.socket", lambda *args: _OpenSocket())

    def matching_urlopen(url: str, timeout: float) -> _JsonResponse:
        if url.endswith("/health"):
            return _JsonResponse({"ready": True})
        return _JsonResponse(
            {"data": [{"id": "faster-whisper/distil-large-v3.5"}]}
        )

    monkeypatch.setattr("lecturebridge.preflight.urlopen", matching_urlopen)
    assert port_check(8123).passed

    monkeypatch.setattr(
        "lecturebridge.preflight.urlopen",
        lambda url, timeout: (
            _JsonResponse({"ready": True})
            if url.endswith("/health")
            else _JsonResponse({"data": [{"id": "faster-whisper/small.en"}]})
        ),
    )
    mismatch = port_check(8123)
    assert not mismatch.passed
    assert "running model differs" in mismatch.detail
