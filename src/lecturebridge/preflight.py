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

from lecturebridge.languages import LANGUAGES, source_language, validate_model_language
from lecturebridge.model_store import (
    TRANSLATION_MODEL,
    load_locked_models,
    model_directory,
    verify_snapshot,
)
from lecturebridge.models import DEFAULT_MODEL, MODEL_BY_NAME, SUPPORTED_MODELS
from lecturebridge.runtime import (
    DEVICE_CHOICES,
    RuntimeSelection,
    cuda_prerequisites,
    ensure_runtime,
)

PASS = "PASS"
WARN = "WARN"
FAIL = "FAIL"


@dataclass(frozen=True)
class Check:
    name: str
    status: str
    detail: str

    @property
    def passed(self) -> bool:
        return self.status != FAIL


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def run_command(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, capture_output=True, check=False, text=True)


def python_check(root: Path) -> Check:
    expected = (root / ".venv").resolve()
    actual = Path(sys.prefix).resolve()
    status = PASS if actual == expected else FAIL
    return Check("Python environment", status, str(actual))


def package_check() -> Check:
    try:
        installed = version("whisperlivekit")
    except PackageNotFoundError:
        return Check("WhisperLiveKit", FAIL, "not installed; run `uv sync`")
    status = PASS if installed == "0.2.26" else FAIL
    return Check("WhisperLiveKit", status, installed)


def gpu_check(
    requested_device: str = "auto",
    runtime: RuntimeSelection | None = None,
) -> Check:
    if runtime is not None:
        if runtime.device == "cuda":
            return Check("NVIDIA GPU", PASS, runtime.detail)
        if requested_device == "cpu":
            return Check("NVIDIA GPU", PASS, "CPU explicitly selected")
        return Check("NVIDIA GPU", WARN, runtime.detail)

    ready, detail = cuda_prerequisites()
    if ready:
        return Check("NVIDIA GPU", PASS, detail)
    status = FAIL if requested_device == "cuda" else WARN
    return Check("NVIDIA GPU", status, detail)


def executable_check(name: str, *, required: bool = True) -> Check:
    location = shutil.which(name)
    if location:
        return Check(name, PASS, location)
    status = FAIL if required else WARN
    return Check(name, status, "not found")


def tailscale_check() -> Check:
    if shutil.which("tailscale") is None:
        return Check("Tailscale", FAIL, "not installed or not on PATH")
    result = run_command(["tailscale", "status", "--json"])
    if result.returncode != 0:
        return Check("Tailscale", FAIL, result.stderr.strip() or "status failed")
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError:
        return Check("Tailscale", FAIL, "invalid status response")
    online = payload.get("BackendState") == "Running" and bool(
        payload.get("Self", {}).get("Online")
    )
    detail = "online" if online else f"backend={payload.get('BackendState', 'unknown')}"
    return Check("Tailscale", PASS if online else FAIL, detail)


def _hub_snapshot(hub: Path, model: str) -> Path:
    spec = MODEL_BY_NAME[model]
    return hub / spec.cache_directory_name / "snapshots" / spec.revision


def cache_check(
    root: Path,
    *,
    model: str = DEFAULT_MODEL,
    translation_enabled: bool = False,
    hub: Path | None = None,
) -> Check:
    hub_root = hub or Path(HF_HUB_CACHE)
    locked = load_locked_models()
    asr_path = _hub_snapshot(hub_root, model)
    asr_failures = verify_snapshot(locked[model], asr_path)

    translation_candidates = (
        root / "nllb-200-distilled-600M-ctranslate2",
        hub_root
        / "models--entai2965--nllb-200-distilled-600M-ctranslate2"
        / "snapshots"
        / locked[TRANSLATION_MODEL].revision,
    )
    translation_path = next(
        (path for path in translation_candidates if path.is_dir()), None
    )
    translation_failures = (
        verify_snapshot(locked[TRANSLATION_MODEL], translation_path)
        if translation_path is not None
        else ["missing"]
    )

    asr_ready = not asr_failures
    translation_ready = not translation_failures
    ready = asr_ready and (translation_ready or not translation_enabled)
    nllb_detail = (
        ("ready" if translation_ready else "; ".join(translation_failures))
        if translation_enabled
        else "not required (source-only)"
    )
    asr_detail = "ready" if asr_ready else "; ".join(asr_failures)
    detail = f"ASR {model}={asr_detail}, NLLB={nllb_detail}"
    return Check("Model cache", PASS if ready else FAIL, detail)


def deep_model_check(
    model: str, runtime: RuntimeSelection, language: str = "en"
) -> Check:
    """Load and execute the model to catch dynamic CUDA library failures."""
    try:
        validate_model_language(model, language)
        import numpy as np
        from faster_whisper import WhisperModel

        path = model_directory(model, download=False)
        loaded = WhisperModel(
            str(path), device=runtime.device, compute_type=runtime.compute_type
        )
        segments, _ = loaded.transcribe(
            np.zeros(16000, dtype=np.float32),
            language=source_language(language).whisper,
            beam_size=1,
        )
        list(segments)
    except (ImportError, OSError, RuntimeError, ValueError) as exc:
        return Check("Deep model smoke test", FAIL, str(exc))
    return Check(
        "Deep model smoke test",
        PASS,
        f"{model} executed on {runtime.device} ({runtime.compute_type})",
    )


def port_check(port: int = 8000, expected_model: str = DEFAULT_MODEL) -> Check:
    check_name = f"Port {port}"
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.settimeout(0.5)
        open_port = probe.connect_ex(("127.0.0.1", port)) == 0
    if not open_port:
        return Check(check_name, PASS, "available")

    try:
        with urlopen(f"http://127.0.0.1:{port}/health", timeout=1) as response:
            payload = json.load(response)
    except (OSError, URLError, json.JSONDecodeError):
        return Check(check_name, FAIL, "occupied by another service")
    ready = response.status == 200 and payload.get("ready") is True
    if not ready:
        return Check(check_name, FAIL, "service is not ready")

    try:
        with urlopen(
            f"http://127.0.0.1:{port}/api/capabilities", timeout=1
        ) as response:
            model_payload = json.load(response)
    except (OSError, URLError, json.JSONDecodeError):
        return Check(check_name, FAIL, "could not verify the running ASR model")

    model_matches = model_payload.get("model") == expected_model
    return Check(
        check_name,
        PASS if model_matches else FAIL,
        (
            f"LectureBridge is ready with {expected_model}"
            if model_matches
            else f"running model differs; expected {expected_model}"
        ),
    )


def peer_check(peer: str) -> Check:
    result = run_command(["tailscale", "ping", "-c", "1", peer])
    detail = result.stdout.strip() or result.stderr.strip() or "no response"
    if result.returncode != 0 or "pong from" not in detail:
        return Check(f"Tailscale peer {peer}", FAIL, detail)
    route = "relay" if "DERP(" in detail else "direct"
    return Check(f"Tailscale peer {peer}", PASS, f"{route}: {detail}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Check classroom readiness.")
    parser.add_argument(
        "--model",
        choices=SUPPORTED_MODELS,
        default=DEFAULT_MODEL,
        help=f"Expected ASR model (default: {DEFAULT_MODEL})",
    )
    parser.add_argument(
        "--language", choices=tuple(LANGUAGES), default="en", help="Spoken language"
    )
    parser.add_argument(
        "--device",
        choices=DEVICE_CHOICES,
        default="auto",
        help="Inference device; auto prefers CUDA and falls back to CPU",
    )
    parser.add_argument(
        "--translation",
        action="store_true",
        help="Also require the optional source-to-Vietnamese translation model",
    )
    parser.add_argument(
        "--deep",
        action="store_true",
        help="Load and execute the model to validate the selected runtime",
    )
    parser.add_argument("--peer", help="Optional Tailscale device name to ping")
    parser.add_argument(
        "--local-only",
        action="store_true",
        help="Skip Tailscale checks for use on this computer",
    )
    parser.add_argument(
        "--port", type=int, default=8000, help="Expected local port (default: 8000)"
    )
    return parser


def collect_checks(
    root: Path | None = None,
    *,
    model: str = DEFAULT_MODEL,
    requested_device: str = "auto",
    runtime: RuntimeSelection | None = None,
    translation_enabled: bool = False,
    deep: bool = False,
    peer: str | None = None,
    port: int = 8000,
    language: str = "en",
    local_only: bool = False,
) -> list[Check]:
    project_root = root or repo_root()
    checks = [
        python_check(project_root),
        package_check(),
        gpu_check(requested_device, runtime),
        executable_check("ffmpeg", required=False),
        cache_check(
            project_root,
            model=model,
            translation_enabled=translation_enabled,
        ),
        port_check(port, model),
    ]
    if not local_only:
        checks.insert(-1, tailscale_check())
    if peer:
        checks.insert(-1, peer_check(peer))
    if deep and runtime is not None:
        checks.insert(-1, deep_model_check(model, runtime, language))
    return checks


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.local_only and args.peer:
        print("error: --peer cannot be used with --local-only", file=sys.stderr)
        return 2
    if not 1 <= args.port <= 65535:
        print("error: port must be between 1 and 65535", file=sys.stderr)
        return 2
    try:
        validate_model_language(args.model, args.language)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    try:
        runtime = ensure_runtime(args.device)
    except RuntimeError as exc:
        print(f"[FAIL] NVIDIA GPU: {exc}", file=sys.stderr)
        return 1

    checks = collect_checks(
        model=args.model,
        requested_device=args.device,
        runtime=runtime,
        translation_enabled=args.translation,
        deep=args.deep,
        peer=args.peer,
        port=args.port,
        language=args.language,
        local_only=args.local_only,
    )
    for check in checks:
        print(f"[{check.status}] {check.name}: {check.detail}")
    return 0 if all(check.passed for check in checks) else 1


if __name__ == "__main__":
    raise SystemExit(main())
