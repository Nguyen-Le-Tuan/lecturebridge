"""Build source bootstrap bundles from an immutable commit, never local data."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import subprocess
import tarfile
import zipfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
FILES = {
    "Install.cmd",
    "Start.cmd",
    "Install.sh",
    "Start.sh",
    ".python-version",
    "pyproject.toml",
    "uv.lock",
    "models.lock.json",
    "README.md",
    "LICENSE",
    "THIRD_PARTY_NOTICES.md",
    "scripts/gpu-smoke.py",
    "docs/setup-linux.md",
    "docs/setup-windows.md",
    "docs/classroom-runbook.md",
    "docs/troubleshooting.md",
}
PREFIXES = ("src/lecturebridge/", "installers/")
REQUIRED = FILES | {
    "installers/setup.py",
    "installers/setup-linux.sh",
    "installers/setup-windows.ps1",
    "installers/windows-common.ps1",
}


def selected(path: str) -> bool:
    name = PurePosixPath(path)
    if name.is_absolute() or ".." in name.parts or "__pycache__" in name.parts:
        return False
    return path in FILES or (
        path.startswith(PREFIXES)
        and name.suffix
        in {".py", ".json", ".js", ".html", ".css", ".svg", ".ps1", ".sh"}
    )


def git(root: Path, *args: str) -> bytes:
    return subprocess.check_output(["git", *args], cwd=root)


def build(root: Path, output: Path, ref: str = "HEAD") -> list[Path]:
    commit = git(root, "rev-parse", "--verify", f"{ref}^{{commit}}").decode().strip()
    epoch = int(git(root, "show", "-s", "--format=%ct", commit))
    contents: dict[str, bytes] = {}
    for entry in git(root, "ls-tree", "-rz", commit).split(b"\0"):
        if not entry:
            continue
        metadata, path_bytes = entry.split(b"\t", 1)
        mode, kind, object_id = metadata.decode().split()
        path = path_bytes.decode("utf-8")
        if selected(path):
            if kind != "blob" or mode not in {"100644", "100755"}:
                raise RuntimeError(f"Refusing non-regular bundle file: {path}")
            contents[path] = git(root, "cat-file", "blob", object_id)
    missing = REQUIRED - contents.keys()
    if missing:
        raise RuntimeError(f"Bundle is missing required files: {sorted(missing)}")
    contents["BUILD_INFO.json"] = (
        json.dumps(
            {"commit": commit, "kind": "online-bootstrap", "weights_included": False},
            indent=2,
        )
        + "\n"
    ).encode()
    output.mkdir(parents=True, exist_ok=True)
    base = f"LectureBridge-{commit[:12]}"
    windows = output / f"{base}-windows-x64.zip"
    ubuntu = output / f"{base}-ubuntu-x64.tar.gz"
    with zipfile.ZipFile(windows, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, data in sorted(contents.items()):
            if name.endswith((".cmd", ".ps1")):
                data = data.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")
            item = zipfile.ZipInfo(f"{base}/{name}")
            item.compress_type = zipfile.ZIP_DEFLATED
            item.external_attr = 0o100644 << 16
            archive.writestr(item, data)
    with tarfile.open(ubuntu, "w:gz") as archive:
        for name, data in sorted(contents.items()):
            item = tarfile.TarInfo(f"{base}/{name}")
            item.size = len(data)
            item.mode = 0o755 if name.endswith(".sh") else 0o644
            item.mtime = epoch
            archive.addfile(item, io.BytesIO(data))
    paths = [windows, ubuntu]
    checksums = output / "SHA256SUMS.txt"
    checksums.write_text(
        "".join(
            f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.name}\n"
            for path in paths
        ),
        encoding="ascii",
    )
    return [*paths, checksums]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ref", default="HEAD")
    parser.add_argument("--output", type=Path, default=ROOT / "dist/installers")
    args = parser.parse_args()
    for path in build(ROOT, args.output, args.ref):
        print(path)


if __name__ == "__main__":
    main()
