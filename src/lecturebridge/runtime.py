"""Runtime helpers shared by LectureBridge command-line tools."""

from __future__ import annotations

import os
import sys
from collections.abc import Mapping, Sequence
from importlib import import_module
from pathlib import Path

CUDA_READY_ENV = "LECTUREBRIDGE_CUDA_RUNTIME_READY"


def nvidia_library_dirs() -> tuple[Path, Path]:
    """Locate pip-installed cuBLAS and cuDNN shared-library directories."""
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
    current = [item for item in environ.get("LD_LIBRARY_PATH", "").split(":") if item]
    prefixes = [str(path) for path in library_dirs]
    updated["LD_LIBRARY_PATH"] = ":".join(
        prefixes + [item for item in current if item not in prefixes]
    )
    updated[CUDA_READY_ENV] = "1"
    return updated


def ensure_cuda_runtime() -> None:
    """Re-exec the current CLI once so the dynamic linker sees CUDA 12 libs."""
    if os.environ.get(CUDA_READY_ENV) == "1":
        return

    try:
        library_dirs = nvidia_library_dirs()
    except (ImportError, RuntimeError) as exc:
        raise RuntimeError(
            "CUDA runtime packages are unavailable; run `uv sync` first"
        ) from exc

    environment = cuda_environment(os.environ, library_dirs)
    os.execvpe(sys.executable, [sys.executable, *sys.argv], environment)
