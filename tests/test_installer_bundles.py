import importlib.util
import json
import subprocess
import tarfile
import zipfile
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location(
    "bundles", Path(__file__).parents[1] / "scripts/build_installers.py"
)
bundles = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bundles)


def test_bundle_uses_committed_allowlist_and_preserves_launchers(tmp_path):
    root = tmp_path / "repo"
    root.mkdir()
    for name in bundles.REQUIRED | {
        "report.md",
        "recording.wav",
        ".env",
        "src/lecturebridge/live.py",
    }:
        target = root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("committed\n", encoding="utf-8")
    for args in [
        ["init"],
        ["add", "."],
        [
            "-c",
            "user.name=Test",
            "-c",
            "user.email=test@example.invalid",
            "commit",
            "-m",
            "fixture",
        ],
    ]:
        subprocess.run(["git", *args], cwd=root, check=True, capture_output=True)
    (root / "README.md").write_text("UNCOMMITTED PRIVATE DATA", encoding="utf-8")
    paths = bundles.build(root, tmp_path / "out")
    with zipfile.ZipFile(paths[0]) as archive:
        names = archive.namelist()
        prefix = names[0].split("/")[0] + "/"
        assert archive.read(prefix + "README.md") == b"committed\n"
        assert archive.read(prefix + "Install.cmd") == b"committed\r\n"
        assert not any(
            n.endswith(("report.md", ".env", "recording.wav")) for n in names
        )
        assert len(json.loads(archive.read(prefix + "BUILD_INFO.json"))["commit"]) == 40
    with tarfile.open(paths[1]) as archive:
        assert archive.getmember(prefix + "Install.sh").mode == 0o755
        assert archive.getmember(prefix + "Start.sh").mode == 0o755
    assert paths[2].read_text().count("\n") == 2


@pytest.mark.parametrize(
    "path",
    [
        "../src/lecturebridge/live.py",
        "/src/lecturebridge/live.py",
        "src/lecturebridge/__pycache__/private.py",
        "src/lecturebridge/secret.wav",
        "report.md",
        ".tools/uv",
        ".lecturebridge/install.json",
    ],
)
def test_bundle_excludes_private_and_unsafe_paths(path):
    assert not bundles.selected(path)
