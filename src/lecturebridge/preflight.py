"""Read-only readiness checks for a LectureBridge classroom session."""

from __future__ import annotations

import argparse
import json
import shutil
import socket
import subprocess
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

from huggingface_hub.constants import HF_HUB_CACHE

from lecturebridge.models import DEFAULT_MODEL, MODEL_BY_NAME, SUPPORTED_MODELS


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


def cache_check(
    root: Path,
    *,
    model: str = DEFAULT_MODEL,
    translation_enabled: bool = False,
    hub: Path | None = None,
) -> Check:
    hub_root = hub or Path(HF_HUB_CACHE)
    asr = hub_root / MODEL_BY_NAME[model].cache_directory_name
    translation_candidates = (
        root / "nllb-200-distilled-600M-ctranslate2",
        hub_root / "models--entai2965--nllb-200-distilled-600M-ctranslate2",
    )
    translation = next((path for path in translation_candidates if path.is_dir()), None)
    asr_ready = asr.is_dir()
    translation_ready = translation is not None
    ready = asr_ready and (translation_ready or not translation_enabled)
    nllb_detail = (
        "ready" if translation_ready else "missing"
    ) if translation_enabled else "not required (EN-only)"
    detail = (
        f"ASR {model}={'ready' if asr_ready else 'missing; download before class'}, "
        f"NLLB={nllb_detail}"
    )
    return Check("Model cache", ready, detail)


def port_check(port: int = 8000, expected_model: str = DEFAULT_MODEL) -> Check:
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
    if not ready:
        return Check("Port 8000", False, "service is not ready")

    try:
        with urlopen(f"http://127.0.0.1:{port}/v1/models", timeout=1) as response:
            model_payload = json.load(response)
    except (OSError, URLError, json.JSONDecodeError):
        return Check("Port 8000", False, "could not verify the running ASR model")

    model_ids = {
        item.get("id")
        for item in model_payload.get("data", [])
        if isinstance(item, dict)
    }
    expected_id = f"faster-whisper/{expected_model}"
    model_matches = expected_id in model_ids
    return Check(
        "Port 8000",
        model_matches,
        (
            f"LectureBridge is ready with {expected_model}"
            if model_matches
            else f"running model differs; expected {expected_id}"
        ),
    )


def peer_check(peer: str) -> Check:
    result = run_command(["tailscale", "ping", "-c", "1", peer])
    detail = result.stdout.strip() or result.stderr.strip() or "no response"
    if result.returncode != 0 or "pong from" not in detail:
        return Check(f"Tailscale peer {peer}", False, detail)
    route = "relay" if "DERP(" in detail else "direct"
    return Check(f"Tailscale peer {peer}", True, f"{route}: {detail}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Check classroom readiness.")
    parser.add_argument(
        "--model",
        choices=SUPPORTED_MODELS,
        default=DEFAULT_MODEL,
        help=f"Expected ASR model (default: {DEFAULT_MODEL})",
    )
    parser.add_argument(
        "--translation",
        action="store_true",
        help="Also require the optional English-to-Vietnamese translation model",
    )
    parser.add_argument("--peer", help="Optional Tailscale device name to ping")
    parser.add_argument(
        "--port", type=int, default=8000, help="Expected local port (default: 8000)"
    )
    return parser


def collect_checks(
    root: Path | None = None,
    *,
    model: str = DEFAULT_MODEL,
    translation_enabled: bool = False,
    peer: str | None = None,
    port: int = 8000,
) -> list[Check]:
    project_root = root or repo_root()
    checks = [
        python_check(project_root),
        package_check(),
        gpu_check(),
        executable_check("ffmpeg"),
        tailscale_check(),
        cache_check(
            project_root,
            model=model,
            translation_enabled=translation_enabled,
        ),
        port_check(port, model),
    ]
    if peer:
        checks.insert(-1, peer_check(peer))
    return checks


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if not 1 <= args.port <= 65535:
        print("error: port must be between 1 and 65535", file=sys.stderr)
        return 2
    checks = collect_checks(
        model=args.model,
        translation_enabled=args.translation,
        peer=args.peer,
        port=args.port,
    )
    for check in checks:
        marker = "PASS" if check.passed else "FAIL"
        print(f"[{marker}] {check.name}: {check.detail}")
    return 0 if all(check.passed for check in checks) else 1


if __name__ == "__main__":
    raise SystemExit(main())
