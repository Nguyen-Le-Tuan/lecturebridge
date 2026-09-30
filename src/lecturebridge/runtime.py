"""Cross-platform runtime selection for LectureBridge command-line tools."""

from __future__ import annotations

import os
import platform
import shutil
import subprocess
import sys
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from importlib import import_module
from pathlib import Path

CUDA_READY_ENV = "LECTUREBRIDGE_CUDA_RUNTIME_READY"
DEVICE_CHOICES = ("auto", "cuda", "cpu")
WINDOWS_CUDA_DLLS = ("cublas64_12.dll", "cudnn64_9.dll", "cudnn_ops64_9.dll")


@dataclass(frozen=True)
class RuntimeSelection:
    requested_device: str
    device: str
    compute_type: str
    detail: str
    warning: str | None = None


def nvidia_library_dirs() -> tuple[Path, Path]:
    """Locate Linux pip-installed cuBLAS and cuDNN shared-library directories."""
    modules = (import_module("nvidia.cublas.lib"), import_module("nvidia.cudnn.lib"))
    paths: list[Path] = []
    for module in modules:
        module_file = getattr(module, "__file__", None)
        if module_file is not None:
            paths.append(Path(module_file).resolve().parent)
            continue

        namespace_paths = list(getattr(module, "__path__", ()))
        if len(namespace_paths) != 1:
            raise RuntimeError("NVIDIA runtime package has no unique library path")
        paths.append(Path(namespace_paths[0]).resolve())
    return paths[0], paths[1]


def cuda_environment(
    environ: Mapping[str, str], library_dirs: Sequence[Path]
) -> dict[str, str]:
    """Return an environment with NVIDIA runtime paths prepended once."""
    updated = dict(environ)
    current = [
        item for item in environ.get("LD_LIBRARY_PATH", "").split(os.pathsep) if item
    ]
    prefixes = [str(path) for path in library_dirs]
    updated["LD_LIBRARY_PATH"] = os.pathsep.join(
        prefixes + [item for item in current if item not in prefixes]
    )
    updated[CUDA_READY_ENV] = "1"
    return updated


def nvidia_smi_detail() -> tuple[bool, str]:
    executable = shutil.which("nvidia-smi")
    if executable is None:
        return False, "nvidia-smi not found"
    result = subprocess.run(
        [
            executable,
            "--query-gpu=name,memory.total,driver_version",
            "--format=csv,noheader",
        ],
        capture_output=True,
        check=False,
        text=True,
    )
    detail = result.stdout.strip() or result.stderr.strip() or "no GPU reported"
    return result.returncode == 0, detail


def windows_cuda_dll_status(
    environ: Mapping[str, str] | None = None,
) -> tuple[bool, str]:
    """Check that Faster-Whisper's required CUDA DLLs are visible on Windows."""
    environment = environ or os.environ
    directories = [
        Path(item)
        for item in environment.get("PATH", "").split(os.pathsep)
        if item
    ]
    missing = [
        filename
        for filename in WINDOWS_CUDA_DLLS
        if not any((directory / filename).is_file() for directory in directories)
    ]
    if missing:
        return False, "missing from PATH: " + ", ".join(missing)
    return True, "CUDA 12 and cuDNN 9 DLLs are available on PATH"


def cuda_prerequisites(
    *,
    system: str | None = None,
    environ: Mapping[str, str] | None = None,
) -> tuple[bool, str]:
    """Report whether this host has the NVIDIA runtime required by CTranslate2."""
    gpu_ready, gpu_detail = nvidia_smi_detail()
    if not gpu_ready:
        return False, gpu_detail

    host = system or platform.system()
    if host == "Linux":
        try:
            cublas, cudnn = nvidia_library_dirs()
        except (ImportError, RuntimeError) as exc:
            return False, f"Linux CUDA runtime packages unavailable: {exc}"
        required = (cublas / "libcublas.so.12", cudnn / "libcudnn.so.9")
        missing = [str(path) for path in required if not path.is_file()]
        if missing:
            return False, "missing CUDA libraries: " + ", ".join(missing)
        return True, gpu_detail
    if host == "Windows":
        dll_ready, dll_detail = windows_cuda_dll_status(environ)
        return dll_ready, f"{gpu_detail}; {dll_detail}"
    return False, f"CUDA is unsupported on {host}; NVIDIA GPU detected: {gpu_detail}"


def choose_runtime(
    requested_device: str,
    *,
    gpu_ready: bool,
    gpu_detail: str,
    compute_type: str = "auto",
) -> RuntimeSelection:
    """Choose CUDA or CPU without silently ignoring an explicit CUDA request."""
    if requested_device not in DEVICE_CHOICES:
        raise ValueError(f"unsupported device: {requested_device}")
    if requested_device == "cuda" and not gpu_ready:
        raise RuntimeError(
            "CUDA was requested but is unavailable: "
            f"{gpu_detail}. Install an NVIDIA driver, CUDA 12, and cuDNN 9."
        )

    if requested_device == "cpu":
        device = "cpu"
        warning = None
        detail = "CPU explicitly selected"
    elif gpu_ready:
        device = "cuda"
        warning = None
        detail = gpu_detail
    else:
        device = "cpu"
        warning = f"CUDA unavailable ({gpu_detail}); using CPU"
        detail = warning

    resolved_compute = compute_type
    if compute_type == "auto":
        resolved_compute = "int8_float16" if device == "cuda" else "int8"
    return RuntimeSelection(
        requested_device=requested_device,
        device=device,
        compute_type=resolved_compute,
        detail=detail,
        warning=warning,
    )


def ensure_runtime(
    requested_device: str = "auto",
    *,
    compute_type: str = "auto",
) -> RuntimeSelection:
    """Select a device and prepare its process environment."""
    ready, detail = cuda_prerequisites()
    selection = choose_runtime(
        requested_device,
        gpu_ready=ready,
        gpu_detail=detail,
        compute_type=compute_type,
    )

    if selection.device == "cpu":
        os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
        return selection

    if platform.system() == "Linux" and os.environ.get(CUDA_READY_ENV) != "1":
        environment = cuda_environment(os.environ, nvidia_library_dirs())
        os.execvpe(sys.executable, [sys.executable, *sys.argv], environment)
    return selection


def ensure_cuda_runtime() -> None:
    """Compatibility wrapper for callers that explicitly require CUDA."""
    ensure_runtime("cuda")
