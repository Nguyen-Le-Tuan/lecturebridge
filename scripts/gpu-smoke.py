"""Manual-only, bounded tiny.en/tiny GPU smoke check; never called by CI.

This watchdog reduces exposure; it cannot prevent driver/power/OS failures.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import time

from lecturebridge.languages import LANGUAGES, validate_model_language

MAX_SECONDS = 60
MAX_TEMPERATURE = 75
MIN_FREE_MIB = 1024


def read_gpu() -> tuple[int, int]:
    executable = shutil.which("nvidia-smi")
    if not executable:
        raise RuntimeError("nvidia-smi is unavailable")
    result = subprocess.run(
        [
            executable,
            "--id=0",
            "--query-gpu=temperature.gpu,memory.free",
            "--format=csv,noheader,nounits",
        ],
        capture_output=True,
        text=True,
        check=True,
        timeout=3,
    )
    temperature, free_memory = result.stdout.strip().split(",")
    return int(temperature), int(free_memory)


def stop_reason(temperature: int, free_memory: int, elapsed: float) -> str | None:
    if elapsed >= MAX_SECONDS:
        return "60-second time limit reached"
    if temperature >= MAX_TEMPERATURE:
        return f"GPU temperature reached {temperature} C"
    if free_memory < MIN_FREE_MIB:
        return f"only {free_memory} MiB VRAM remains free"
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", choices=("tiny.en", "tiny"))
    parser.add_argument("--language", choices=tuple(LANGUAGES), default="en")
    args = parser.parse_args()
    model = args.model or ("tiny.en" if args.language == "en" else "tiny")
    try:
        validate_model_language(model, args.language)
    except ValueError as exc:
        parser.error(str(exc))
    process = None
    try:
        temperature, free_memory = read_gpu()
        reason = stop_reason(temperature, free_memory, 0)
        if reason or temperature > 65:
            print(f"Not started: {reason or 'let the GPU cool below 66 C first'}")
            return 1
        print(
            f"Manual GPU check: {model}, language={args.language}, "
            "one second of silence, no translation.",
            flush=True,
        )
        print(
            "Watchdog: 60 seconds / 75 C / at least 1024 MiB free VRAM. Ctrl+C stops.",
            flush=True,
        )
        started = time.monotonic()
        process = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "lecturebridge.preflight",
                "--model",
                model,
                "--language",
                args.language,
                "--device",
                "cuda",
                "--deep",
            ],
            env=dict(os.environ, CUDA_VISIBLE_DEVICES="0", OMP_NUM_THREADS="2"),
        )
        while process.poll() is None:
            temperature, free_memory = read_gpu()
            reason = stop_reason(temperature, free_memory, time.monotonic() - started)
            if reason:
                print(f"Stopping test: {reason}", flush=True)
                return 1
            time.sleep(0.5)
        return process.returncode
    except KeyboardInterrupt:
        print("Stopped by user.")
        return 130
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as exc:
        print(f"Monitoring unavailable; test stopped: {exc}", file=sys.stderr)
        return 1
    finally:
        if process is not None and process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()


if __name__ == "__main__":
    raise SystemExit(main())
