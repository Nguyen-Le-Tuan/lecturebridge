"""Installer coverage with simulated hardware and downloads; never loads models."""

import json
import subprocess
from types import SimpleNamespace

import pytest

from lecturebridge import installation as setup


def hardware(**changes):
    result = {
        "system": "Windows",
        "machine": "AMD64",
        "ram_bytes": 16 * setup.GIB,
        "free_bytes": 30 * setup.GIB,
        "cpu_threads": 8,
        "gpu": None,
    }
    result.update(changes)
    return result


def gpu(**changes):
    result = {
        "name": "test GPU",
        "total_mib": 6144,
        "free_mib": 5000,
        "temperature": 40,
        "driver": "test",
    }
    result.update(changes)
    return result


@pytest.mark.parametrize("language", ["en", "zh", "zh-Hant", "ja", "ko"])
def test_cpu_profile_is_multilingual_and_never_selects_large_model(language):
    state = setup.recommend(hardware(gpu=gpu()), language, "cpu")
    assert (state["model"], state["device"], state["windows_cuda"]) == (
        "tiny",
        "cpu",
        False,
    )


@pytest.mark.parametrize(
    "device,ram,profile,expected",
    [
        (None, 16, "auto", ("tiny", "cpu")),
        (gpu(), 16, "auto", ("small", "cuda")),
        (gpu(total_mib=4096, free_mib=3000), 8, "auto", ("base", "cuda")),
        (gpu(), 4, "auto", ("tiny", "cuda")),
        (gpu(), 32, "safe", ("tiny", "cuda")),
        (gpu(free_mib=2000), 32, "auto", ("tiny", "cpu")),
        (gpu(temperature=66), 32, "auto", ("tiny", "cpu")),
    ],
)
def test_hardware_recommendations(device, ram, profile, expected):
    state = setup.recommend(
        hardware(gpu=device, ram_bytes=ram * setup.GIB), "zh", profile
    )
    assert (state["model"], state["device"]) == expected


@pytest.mark.parametrize(
    "change",
    [
        {"system": "Darwin"},
        {"machine": "arm64"},
        {"free_bytes": 19 * setup.GIB},
        {"ram_bytes": 2 * setup.GIB},
    ],
)
def test_unsupported_hardware_stops_before_dependencies(change):
    with pytest.raises(RuntimeError):
        setup.recommend(hardware(**change), "en")


def test_gpu_probe_does_not_execute_cuda(monkeypatch):
    monkeypatch.setattr(setup.shutil, "which", lambda name: "fake-nvidia-smi")
    calls = []

    def run(command, **kwargs):
        calls.append((command, kwargs))
        return SimpleNamespace(stdout='"NVIDIA, test", 6144, 4000, 999.0, 50\n')

    monkeypatch.setattr(setup.subprocess, "run", run)
    assert setup.read_gpu()["name"] == "NVIDIA, test"
    assert calls[0][0][1] == "--id=0"
    assert calls[0][1]["timeout"] == 5
    monkeypatch.setattr(
        setup.subprocess,
        "run",
        lambda *a, **kw: (_ for _ in ()).throw(
            subprocess.TimeoutExpired("nvidia-smi", 5)
        ),
    )
    assert setup.read_gpu() is None


def test_incomplete_or_corrupt_setup_cannot_launch(tmp_path):
    state = setup.recommend(hardware(), "ja")
    setup.save_state(tmp_path, state)
    with pytest.raises(RuntimeError, match="incomplete"):
        setup.load_state(tmp_path, ready=True)
    state["status"] = "ready"
    setup.save_state(tmp_path, state)
    assert setup.load_state(tmp_path, ready=True)["language"] == "ja"
    (tmp_path / ".lecturebridge/installing").touch()
    with pytest.raises(RuntimeError, match="incomplete"):
        setup.load_state(tmp_path, ready=True)
    (tmp_path / ".lecturebridge/install.json").write_text("[]", encoding="utf-8")
    with pytest.raises(RuntimeError, match="Invalid"):
        setup.load_state(tmp_path)


def test_setup_downloads_only_selected_and_fallback_and_marks_ready_last(
    monkeypatch, tmp_path
):
    state = setup.recommend(hardware(gpu=gpu()), "ko")
    setup.save_state(tmp_path, state)
    downloads, checks = [], []
    monkeypatch.setattr(
        "lecturebridge.runtime.cuda_prerequisites", lambda: (True, "fake")
    )
    monkeypatch.setattr(
        "lecturebridge.model_store.model_directory",
        lambda name, **kw: downloads.append((name, kw)),
    )

    def preflight(command, **kwargs):
        checks.append(command)
        assert setup.load_state(tmp_path)["status"] == "installing"
        assert "--deep" not in command
        assert "--local-only" in command

    monkeypatch.setattr(setup.subprocess, "run", preflight)
    result = setup.finish_install(tmp_path)
    assert downloads == [("tiny", {"download": True}), ("small", {"download": True})]
    assert checks and result["status"] == "ready"
    assert setup.load_state(tmp_path, ready=True)["language"] == "ko"


def test_download_failure_never_marks_setup_ready(monkeypatch, tmp_path):
    setup.save_state(tmp_path, setup.recommend(hardware(), "en"))

    def fail(*args, **kwargs):
        raise RuntimeError("network offline")

    monkeypatch.setattr("lecturebridge.model_store.model_directory", fail)
    monkeypatch.setattr(
        setup.subprocess, "run", lambda *a, **kw: pytest.fail("must not run preflight")
    )
    with pytest.raises(RuntimeError, match="network offline"):
        setup.finish_install(tmp_path)
    assert setup.load_state(tmp_path)["status"] == "installing"


def test_missing_cuda_runtime_selects_cpu_before_download(monkeypatch, tmp_path):
    setup.save_state(tmp_path, setup.recommend(hardware(gpu=gpu()), "en"))
    downloads = []
    monkeypatch.setattr(
        "lecturebridge.runtime.cuda_prerequisites", lambda: (False, "missing")
    )
    monkeypatch.setattr(
        "lecturebridge.model_store.model_directory",
        lambda name, **kw: downloads.append(name),
    )
    monkeypatch.setattr(setup.subprocess, "run", lambda *a, **kw: None)
    result = setup.finish_install(tmp_path)
    assert (result["device"], result["model"], downloads) == ("cpu", "tiny", ["tiny"])


@pytest.mark.parametrize("returncode", [0, 1])
def test_first_gpu_launch_only_runs_tiny_watchdog(monkeypatch, tmp_path, returncode):
    state = setup.recommend(hardware(gpu=gpu()), "zh")
    calls = []
    monkeypatch.setattr(setup, "read_gpu", lambda: gpu())

    def smoke(command, **kwargs):
        calls.append(command)
        return SimpleNamespace(returncode=returncode)

    monkeypatch.setattr(setup.subprocess, "run", smoke)
    result = setup.ensure_launch_profile(tmp_path, state)
    assert calls[0][-4:] == ["--model", "tiny", "--language", "zh"]
    if returncode:
        assert (result["device"], result["model"]) == ("cpu", "tiny")
        assert state["verified_gpu"] is None
    else:
        assert result["verified_gpu"] == setup.gpu_fingerprint(gpu())
        setup.ensure_launch_profile(tmp_path, result)
        assert len(calls) == 1
        monkeypatch.setattr(setup, "read_gpu", lambda: gpu(driver="new"))
        setup.ensure_launch_profile(tmp_path, result)
        assert len(calls) == 2


def test_hot_gpu_skips_even_the_smoke(monkeypatch, tmp_path):
    state = setup.recommend(hardware(gpu=gpu()), "en")
    monkeypatch.setattr(setup, "read_gpu", lambda: gpu(temperature=70))
    monkeypatch.setattr(
        setup.subprocess, "run", lambda *a, **kw: pytest.fail("GPU must not run")
    )
    assert setup.ensure_launch_profile(tmp_path, state)["device"] == "cpu"


def test_language_change_and_failed_setup_report_actionable_errors(tmp_path, capsys):
    assert setup.main(["launch", "--root", str(tmp_path)]) == 1
    assert "Run Install first" in capsys.readouterr().err
    state = setup.recommend(hardware(), "ko")
    setup.save_state(tmp_path, state)
    assert (
        json.loads((tmp_path / ".lecturebridge/install.json").read_text())["language"]
        == "ko"
    )


def test_language_choice_keeps_source_code(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda prompt: "4")
    assert setup.choose_language() == "ja"
    monkeypatch.setattr("builtins.input", lambda prompt: "")
    assert setup.choose_language("ko") == "ko"
