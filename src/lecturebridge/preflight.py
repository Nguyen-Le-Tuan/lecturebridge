"""Read-only readiness checks for a LectureBridge classroom session."""

from __future__ import annotations

import json
import shutil
import socket
import subprocess
import sys
from dataclasses import dataclass
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

from huggingface_hub.constants import HF_HUB_CACHE


@dataclass(frozen=True)
class Check:
    name: str
    passed: bool
    detail: str


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def run_command(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, capture_output=True, check=False, text=True)


def python_check(root: Path) -> Check:
    expected = (root / ".venv").resolve()
    actual = Path(sys.prefix).resolve()
    return Check("Python environment", actual == expected, str(actual))


def package_check() -> Check:
    try:
        installed = version("whisperlivekit")
    except PackageNotFoundError:
        return Check("WhisperLiveKit", False, "not installed; run `uv sync`")
    return Check("WhisperLiveKit", installed == "0.2.26", installed)


def gpu_check() -> Check:
    result = run_command(
        [
            "nvidia-smi",
            "--query-gpu=name,memory.total,driver_version",
            "--format=csv,noheader",
        ]
    )
    detail = result.stdout.strip() or result.stderr.strip() or "not available"
    return Check("NVIDIA GPU", result.returncode == 0, detail)


def executable_check(name: str) -> Check:
    location = shutil.which(name)
    return Check(name, location is not None, location or "not found")


def tailscale_check() -> Check:
    result = run_command(["tailscale", "status", "--json"])
    if result.returncode != 0:
        return Check("Tailscale", False, result.stderr.strip() or "status failed")
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError:
        return Check("Tailscale", False, "invalid status response")
    online = payload.get("BackendState") == "Running" and bool(
        payload.get("Self", {}).get("Online")
    )
    detail = "online" if online else f"backend={payload.get('BackendState', 'unknown')}"
    return Check("Tailscale", online, detail)


def cache_check(root: Path) -> Check:
    hub = Path(HF_HUB_CACHE)
    asr = hub / "models--Systran--faster-whisper-small.en"
    translation_candidates = (
        root / "nllb-200-distilled-600M-ctranslate2",
        hub / "models--entai2965--nllb-200-distilled-600M-ctranslate2",
    )
    translation = next((path for path in translation_candidates if path.is_dir()), None)
    ready = asr.is_dir() and translation is not None
    detail = f"ASR={'ready' if asr.is_dir() else 'missing'}, NLLB={'ready' if translation else 'missing'}"
    return Check("Model cache", ready, detail)


def port_check(port: int = 8000) -> Check:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.settimeout(0.5)
        open_port = probe.connect_ex(("127.0.0.1", port)) == 0
    if not open_port:
        return Check("Port 8000", True, "available")

    try:
        with urlopen(f"http://127.0.0.1:{port}/health", timeout=1) as response:
            payload = json.load(response)
    except (OSError, URLError, json.JSONDecodeError):
        return Check("Port 8000", False, "occupied by another service")
    ready = response.status == 200 and payload.get("ready") is True
    return Check(
        "Port 8000",
        ready,
        "LectureBridge is already ready" if ready else "service is not ready",
    )


def collect_checks(root: Path | None = None) -> list[Check]:
    project_root = root or repo_root()
    return [
        python_check(project_root),
        package_check(),
        gpu_check(),
        executable_check("ffmpeg"),
        tailscale_check(),
        cache_check(project_root),
        port_check(),
    ]


def main() -> int:
    checks = collect_checks()
    for check in checks:
        marker = "PASS" if check.passed else "FAIL"
        print(f"[{marker}] {check.name}: {check.detail}")
    return 0 if all(check.passed for check in checks) else 1


if __name__ == "__main__":
    raise SystemExit(main())
