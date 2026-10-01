"""Exercise the shell install sequence with fake executables, not packages/models."""

import os
import platform
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[1]
SUPPORTED_HOST = (
    platform.system() == "Linux"
    and Path("/etc/os-release").exists()
    and "ubuntu" in Path("/etc/os-release").read_text()
)


@pytest.mark.skipif(not SUPPORTED_HOST, reason="Ubuntu shell installer")
@pytest.mark.parametrize("failure", ["", "sync", "complete"])
def test_shell_setup_stops_on_failure_and_keeps_incomplete_marker(tmp_path, failure):
    root = tmp_path / "folder with spaces"
    (root / "installers").mkdir(parents=True)
    shutil.copy(ROOT / "installers/setup-linux.sh", root / "installers/setup-linux.sh")
    fake_bin = root / "fake-bin"
    fake_bin.mkdir()
    dpkg = fake_bin / "dpkg-query"
    dpkg.write_text("#!/bin/sh\necho 'install ok installed'\n")
    dpkg.chmod(0o755)
    uv = root / ".tools/uv-0.12.13/uv"
    uv.parent.mkdir(parents=True)
    uv.write_text("""#!/bin/sh
echo "uv $*" >> .lecturebridge/commands
if [ "$1" = "$FAIL_STEP" ]; then exit 7; fi
""")
    uv.chmod(0o755)
    python = root / ".venv/bin/python"
    python.parent.mkdir(parents=True)
    python.write_text("""#!/bin/sh
echo "python $*" >> .lecturebridge/commands
if [ "$2" = "$FAIL_STEP" ]; then exit 8; fi
""")
    python.chmod(0o755)
    result = subprocess.run(
        ["bash", str(root / "installers/setup-linux.sh"), "--language", "ko"],
        env=dict(
            os.environ,
            PATH=str(fake_bin) + os.pathsep + os.environ["PATH"],
            FAIL_STEP=failure,
        ),
        capture_output=True,
        text=True,
        timeout=15,
        check=False,
    )
    commands = (root / ".lecturebridge/commands").read_text()
    assert "plan --language ko" in commands
    assert (root / ".lecturebridge/installing").exists() == bool(failure)
    assert (result.returncode != 0) == bool(failure)
    if failure == "sync":
        assert "setup.py complete" not in commands
    if not failure:
        assert "setup.py complete" in commands
