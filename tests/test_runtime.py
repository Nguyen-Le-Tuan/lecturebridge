from pathlib import Path

from lecturebridge.runtime import (
    CUDA_READY_ENV,
    cuda_environment,
    nvidia_library_dirs,
)


def test_cuda_environment_prepends_required_paths_without_duplicates() -> None:
    cublas = Path("/venv/nvidia/cublas/lib")
    cudnn = Path("/venv/nvidia/cudnn/lib")
    environment = cuda_environment(
        {"LD_LIBRARY_PATH": f"/system/lib:{cublas}"},
        (cublas, cudnn),
    )

    assert environment["LD_LIBRARY_PATH"] == (
        "/venv/nvidia/cublas/lib:/venv/nvidia/cudnn/lib:/system/lib"
    )
    assert environment[CUDA_READY_ENV] == "1"


def test_nvidia_library_dirs_contain_required_shared_libraries() -> None:
    cublas, cudnn = nvidia_library_dirs()

    assert (cublas / "libcublas.so.12").is_file()
    assert (cudnn / "libcudnn.so.9").is_file()
