from pathlib import Path

from lecturebridge.preflight import Check, python_check


def test_python_check_accepts_expected_virtual_environment(
    monkeypatch,
    tmp_path: Path,
) -> None:
    expected = tmp_path / ".venv"
    expected.mkdir()
    monkeypatch.setattr("lecturebridge.preflight.sys.prefix", str(expected))

    result = python_check(tmp_path)

    assert result.passed


def test_check_is_immutable_result() -> None:
    result = Check("GPU", True, "ready")

    assert result.name == "GPU"
    assert result.passed is True
    assert result.detail == "ready"
