"""Conservative installer planning and launch orchestration; no install-time inference."""

from __future__ import annotations

import argparse
import csv
import ctypes
import json
import os
import platform
import shutil
import socket
import subprocess
import sys
import threading
import webbrowser
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

from lecturebridge.languages import LANGUAGES, validate_model_language
from lecturebridge.models import SUPPORTED_MODELS

GIB = 1024**3
MIN_FREE_GIB = 20
LANGUAGE_NAMES = {
    "en": "English",
    "zh": "Mandarin Chinese",
    "zh-Hant": "Mandarin (Traditional text)",
    "ja": "Japanese",
    "ko": "Korean",
}


def read_gpu() -> dict | None:
    """Read GPU 0 telemetry only; never call CUDA or load a model."""
    executable = shutil.which("nvidia-smi")
    if not executable:
        return None
    try:
        result = subprocess.run(
            [
                executable,
                "--id=0",
                "--query-gpu=name,memory.total,memory.free,driver_version,temperature.gpu",
                "--format=csv,noheader,nounits",
            ],
            capture_output=True,
            text=True,
            check=True,
            timeout=5,
        )
        name, total, free, driver, temperature = next(
            csv.reader(result.stdout.splitlines())
        )
        return {
            "name": name.strip(),
            "total_mib": int(total),
            "free_mib": int(free),
            "driver": driver.strip(),
            "temperature": int(temperature),
        }
    except (OSError, ValueError, StopIteration, subprocess.SubprocessError):
        return None


def physical_ram() -> int:
    try:
        if os.name == "nt":

            class MemoryStatus(ctypes.Structure):
                _fields_ = [("length", ctypes.c_ulong), ("load", ctypes.c_ulong)] + [
                    (name, ctypes.c_ulonglong)
                    for name in (
                        "total",
                        "available",
                        "page_total",
                        "page_available",
                        "virtual_total",
                        "virtual_available",
                        "extended",
                    )
                ]

            status = MemoryStatus()
            status.length = ctypes.sizeof(status)
            if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
                return status.total
            return 0
        return os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES")
    except (AttributeError, OSError, ValueError):
        return 0


def inspect_hardware(root: Path) -> dict:
    return {
        "system": platform.system(),
        "machine": platform.machine(),
        "cpu_threads": os.cpu_count() or 1,
        "ram_bytes": physical_ram(),
        "free_bytes": shutil.disk_usage(root).free,
        "gpu": read_gpu(),
    }


def recommend(hardware: dict, language: str, profile: str = "auto") -> dict:
    validate_model_language("tiny", language)
    if hardware["system"] not in {"Windows", "Linux"} or hardware[
        "machine"
    ].lower() not in {"amd64", "x86_64"}:
        raise RuntimeError(
            "This installer requires Windows or Ubuntu/Linux on an x86-64 computer."
        )
    if hardware["free_bytes"] < MIN_FREE_GIB * GIB:
        raise RuntimeError(
            f"At least {MIN_FREE_GIB} GB of free disk space is required. Free space and run Install again."
        )
    if 0 < hardware["ram_bytes"] < 4 * GIB:
        raise RuntimeError(
            "At least 4 GB of system RAM is required for this test build."
        )
    if profile not in {"auto", "safe", "cpu"}:
        raise ValueError("Unknown setup profile")
    gpu = hardware.get("gpu")
    usable = bool(
        gpu
        and gpu["free_mib"] >= 2048
        and gpu["temperature"] <= 65
        and profile != "cpu"
    )
    model = "tiny"
    if usable and profile == "auto":
        if (
            gpu["total_mib"] >= 6144
            and gpu["free_mib"] >= 4096
            and hardware["ram_bytes"] >= 16 * GIB
        ):
            model = "small"
        elif gpu["total_mib"] >= 4096 and hardware["ram_bytes"] >= 8 * GIB:
            model = "base"
    return {
        "schema": 1,
        "status": "installing",
        "language": language,
        "model": model,
        "device": "cuda" if usable else "cpu",
        "profile": profile,
        "port": 8000,
        "windows_cuda": usable and hardware["system"] == "Windows",
        "hardware": hardware,
        "verified_gpu": None,
    }


def save_state(root: Path, state: dict) -> None:
    folder = root / ".lecturebridge"
    folder.mkdir(exist_ok=True, mode=0o700)
    temporary = folder / "install.json.tmp"
    temporary.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    temporary.replace(folder / "install.json")


def load_state(root: Path, *, ready: bool = False) -> dict:
    try:
        state = json.loads(
            (root / ".lecturebridge/install.json").read_text(encoding="utf-8")
        )
    except (OSError, ValueError) as exc:
        raise RuntimeError("Setup has not completed. Run Install first.") from exc
    if (
        not isinstance(state, dict)
        or state.get("schema") != 1
        or state.get("model") not in SUPPORTED_MODELS
        or state.get("device") not in {"cpu", "cuda"}
    ):
        raise RuntimeError("Invalid setup configuration. Run Install again.")
    validate_model_language(state["model"], state.get("language", ""))
    if state.get("port") != 8000:
        raise RuntimeError(
            "This launcher uses port 8000. Restore the setup configuration."
        )
    if ready and (
        state.get("status") != "ready" or (root / ".lecturebridge/installing").exists()
    ):
        raise RuntimeError(
            "Setup is incomplete. Run Install again and check .lecturebridge/setup.log."
        )
    return state


def choose_language(default: str = "en") -> str:
    codes = list(LANGUAGE_NAMES)
    print("\nChoose the language spoken in your audio:")
    for i, code in enumerate(codes, 1):
        print(f"  {i}. {LANGUAGE_NAMES[code]} ({code})")
    answer = input(f"Language [Enter = {LANGUAGE_NAMES[default]}]: ").strip()
    if not answer:
        return default
    if answer in codes:
        return answer
    if answer.isdigit() and 1 <= int(answer) <= len(codes):
        return codes[int(answer) - 1]
    raise ValueError("Please run Install again and choose one of the listed languages.")


def plan_install(
    root: Path, language: str | None, profile: str, non_interactive: bool
) -> dict:
    if language is None:
        previous = root / ".lecturebridge/install.json"
        default = "en"
        if previous.exists():
            try:
                candidate = load_state(root).get("language")
                if candidate in LANGUAGES:
                    default = candidate
            except (OSError, ValueError, RuntimeError):
                pass
        language = default if non_interactive else choose_language(default)
    state = recommend(inspect_hardware(root), language, profile)
    # Account for a model cache on a different disk before downloading weights.
    cache = Path(
        os.environ.get(
            "HF_HUB_CACHE",
            Path(os.environ.get("HF_HOME", Path.home() / ".cache/huggingface")) / "hub",
        )
    )
    while not cache.exists() and cache != cache.parent:
        cache = cache.parent
    if shutil.disk_usage(cache).free < 2 * GIB:
        raise RuntimeError(
            "The model-cache drive needs at least 2 GB free. Free space and retry."
        )
    save_state(root, state)
    print(
        f"\nDetected: {state['hardware']['system']}, {state['hardware']['ram_bytes'] / GIB:.1f} GB RAM"
    )
    print(
        f"Selected: {state['model']} / {state['device']} / {LANGUAGE_NAMES[language]}"
    )
    print("The choice is a conservative starting profile, not a performance guarantee.")
    print(
        "Setup downloads files only. It will not run model inference or change GPU drivers."
    )
    if state["device"] == "cpu":
        print(
            "GPU 0 is unavailable, busy, warm, or CPU was requested. Using tiny on CPU."
        )
    return state


def finish_install(root: Path) -> dict:
    # Dependencies are installed before this stage; imports here do not load weights.
    from lecturebridge.model_store import model_directory
    from lecturebridge.runtime import cuda_prerequisites

    state = load_state(root)
    if state["device"] == "cuda":
        available, detail = cuda_prerequisites()
        if not available:
            print(
                f"GPU prerequisites are unavailable: {detail}. Selecting tiny on CPU."
            )
            state.update(device="cpu", model="tiny")
    names = list(dict.fromkeys(["tiny", state["model"]]))
    for model in names:
        print(f"Downloading/verifying {model}...", flush=True)
        model_directory(model, download=True)
    subprocess.run(
        [
            sys.executable,
            "-m",
            "lecturebridge.preflight",
            "--local-only",
            "--model",
            state["model"],
            "--device",
            state["device"],
            "--language",
            state["language"],
        ],
        cwd=root,
        check=True,
    )
    state["status"] = "ready"
    save_state(root, state)
    print("\nSetup complete. Use Start.cmd (Windows) or bash Start.sh (Ubuntu).")
    print(
        "On the first GPU launch, a bounded one-second tiny check runs before the app."
    )
    print(
        "Use the app's bilingual/Vietnamese mode to explicitly download translation later."
    )
    return state


def gpu_fingerprint(gpu: dict | None) -> str | None:
    if not gpu:
        return None
    return json.dumps([gpu["name"], gpu["total_mib"], gpu["driver"]])


def ensure_launch_profile(root: Path, state: dict) -> dict:
    if state["device"] != "cuda":
        return state
    gpu = read_gpu()
    if not gpu or gpu["temperature"] > 65 or gpu["free_mib"] < 2048:
        print(
            "GPU is not ready for a short check. Starting tiny on CPU for this session."
        )
        return dict(state, device="cpu", model="tiny")
    fingerprint = gpu_fingerprint(gpu)
    if state.get("verified_gpu") != fingerprint:
        print(
            "Checking GPU with tiny: one second of silence, no translation, bounded watchdog.",
            flush=True,
        )
        result = subprocess.run(
            [
                sys.executable,
                str(root / "scripts/gpu-smoke.py"),
                "--model",
                "tiny",
                "--language",
                state["language"],
            ],
            cwd=root,
            check=False,
        )
        if result.returncode != 0:
            print(
                "GPU check did not pass. Starting tiny on CPU; no larger GPU model will load."
            )
            return dict(state, device="cpu", model="tiny")
        state["verified_gpu"] = fingerprint
        save_state(root, state)
    return state


def port_available(port: int) -> bool:
    with socket.socket() as probe:
        probe.settimeout(1)
        return probe.connect_ex(("127.0.0.1", port)) != 0


def open_when_ready(port: int, stopped: threading.Event) -> None:
    for _ in range(180):
        if stopped.wait(1):
            return
        try:
            with urlopen(f"http://127.0.0.1:{port}/health", timeout=1) as response:
                if json.load(response).get("ready"):
                    webbrowser.open(f"http://127.0.0.1:{port}")
                    return
        except (OSError, ValueError, URLError):
            pass
    print(f"If the server is ready, open http://127.0.0.1:{port} in your browser.")


def launch(root: Path, language: str | None = None) -> int:
    state = load_state(root, ready=True)
    if language:
        validate_model_language(state["model"], language)
        state["language"] = language
        save_state(root, state)
    if not port_available(state["port"]):
        raise RuntimeError(
            "Port 8000 is already in use. Close the existing LectureBridge server first."
        )
    state = ensure_launch_profile(root, state)
    print(
        f"Starting {state['model']} on {state['device']} ({LANGUAGE_NAMES[state['language']]}).",
        flush=True,
    )
    print(
        "Keep this window open. Stop the session in the app, then press Ctrl+C here to quit."
    )
    print("The live server has no thermal watchdog. Keep the first session short.")
    stopped = threading.Event()
    env = dict(os.environ, PYTHONIOENCODING="utf-8", OMP_NUM_THREADS="2")
    if state["device"] == "cuda":
        env["CUDA_VISIBLE_DEVICES"] = "0"
    process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "lecturebridge.live",
            "--model",
            state["model"],
            "--language",
            state["language"],
            "--device",
            state["device"],
        ],
        cwd=root,
        env=env,
    )
    threading.Thread(
        target=open_when_ready, args=(state["port"], stopped), daemon=True
    ).start()
    try:
        return process.wait()
    except KeyboardInterrupt:
        try:
            return process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.terminate()
            try:
                return process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
                return 130
    finally:
        stopped.set()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("plan", "complete", "launch"))
    parser.add_argument(
        "--root", type=Path, default=Path(__file__).resolve().parents[2]
    )
    parser.add_argument("--language", choices=tuple(LANGUAGES))
    parser.add_argument("--profile", choices=("auto", "safe", "cpu"), default="auto")
    parser.add_argument("--non-interactive", action="store_true")
    args = parser.parse_args(argv)
    root = args.root.resolve()
    try:
        if args.action == "plan":
            plan_install(root, args.language, args.profile, args.non_interactive)
        elif args.action == "complete":
            finish_install(root)
        else:
            return launch(root, args.language)
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as exc:
        print(
            f"ERROR: {exc}\nSee .lecturebridge/setup.log, then rerun Install after fixing the reported problem.",
            file=sys.stderr,
        )
        return 1
    except KeyboardInterrupt:
        print("Stopped. Run Install again to resume setup.")
        return 130
    return 0
