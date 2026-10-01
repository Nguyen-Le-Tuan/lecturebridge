import os
import platform
from pathlib import Path

import pytest

from lecturebridge.runtime import (
    CUDA_READY_ENV,
    RuntimeSelection,
    choose_runtime,
    cuda_environment,
    nvidia_library_dirs,
    windows_cuda_dll_status,
)


def test_cuda_environment_prepends_required_paths_without_duplicates() -> None:
    cublas = Path("/venv/nvidia/cublas/lib")
    cudnn = Path("/venv/nvidia/cudnn/lib")
    environment = cuda_environment(
        {"LD_LIBRARY_PATH": os.pathsep.join(("/system/lib", str(cublas)))},
        (cublas, cudnn),
    )

    assert environment["LD_LIBRARY_PATH"] == os.pathsep.join(
        (
            str(cublas),
            str(cudnn),
            "/system/lib",
        )
    )
    assert environment[CUDA_READY_ENV] == "1"


@pytest.mark.skipif(platform.system() != "Linux", reason="Linux pip CUDA packages")
def test_nvidia_library_dirs_contain_required_shared_libraries() -> None:
    cublas, cudnn = nvidia_library_dirs()

    assert (cublas / "libcublas.so.12").is_file()
    assert (cudnn / "libcudnn.so.9").is_file()


def test_auto_falls_back_to_cpu_with_safe_compute_type() -> None:
    result = choose_runtime(
        "auto", gpu_ready=False, gpu_detail="driver missing", compute_type="auto"
    )

    assert result == RuntimeSelection(
        requested_device="auto",
        device="cpu",
        compute_type="int8",
        detail="CUDA unavailable (driver missing); using CPU",
        warning="CUDA unavailable (driver missing); using CPU",
    )


def test_explicit_cuda_does_not_silently_fallback() -> None:
    with pytest.raises(RuntimeError, match="CUDA was requested"):
        choose_runtime("cuda", gpu_ready=False, gpu_detail="DLL missing")


def test_windows_cuda_dll_check_uses_path(tmp_path: Path) -> None:
    for filename in ("cublas64_12.dll", "cudnn64_9.dll", "cudnn_ops64_9.dll"):
        (tmp_path / filename).touch()

    ready, detail = windows_cuda_dll_status({"PATH": str(tmp_path)})

    assert ready
    assert "available" in detail


def test_windows_private_cuda_dirs_are_detected_without_import(monkeypatch, tmp_path):
    from lecturebridge import runtime

    monkeypatch.setattr(runtime.sysconfig, "get_path", lambda name: str(tmp_path))
    cublas = tmp_path / "nvidia/cublas/bin"
    cudnn = tmp_path / "nvidia/cudnn/bin"
    cublas.mkdir(parents=True)
    cudnn.mkdir(parents=True)
    (cublas / "cublas64_12.dll").touch()
    for name in ("cudnn64_9.dll", "cudnn_ops64_9.dll"):
        (cudnn / name).touch()
    assert runtime.windows_cuda_library_dirs() == [cublas, cudnn]
    assert runtime.windows_cuda_dll_status()[0]
    assert not runtime.windows_cuda_dll_status({"PATH": ""})[0]
