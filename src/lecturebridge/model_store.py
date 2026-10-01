"""Download and verify immutable model snapshots declared in models.lock.json."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

from huggingface_hub import snapshot_download

from lecturebridge.models import DEFAULT_MODEL, SUPPORTED_MODELS

TRANSLATION_MODEL = "nllb-200-distilled-600M"


@dataclass(frozen=True)
class LockedFile:
    size: int
    sha256: str


@dataclass(frozen=True)
class LockedModel:
    name: str
    kind: str
    repository: str
    revision: str
    license: str
    files: Mapping[str, LockedFile]
    local_directory: str | None = None


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def lock_path() -> Path:
    checkout_manifest = repo_root() / "models.lock.json"
    if checkout_manifest.is_file():
        return checkout_manifest
    return Path(__file__).with_name("models.lock.json")


def load_locked_models(path: Path | None = None) -> dict[str, LockedModel]:
    payload = json.loads((path or lock_path()).read_text(encoding="utf-8"))
    if payload.get("schema_version") != 1:
        raise ValueError("unsupported models.lock.json schema")

    locked: dict[str, LockedModel] = {}
    for name, raw in payload["models"].items():
        files = {
            filename: LockedFile(size=item["size"], sha256=item["sha256"])
            for filename, item in raw["files"].items()
        }
        locked[name] = LockedModel(
            name=name,
            kind=raw["kind"],
            repository=raw["repository"],
            revision=raw["revision"],
            license=raw["license"],
            local_directory=raw.get("local_directory"),
            files=files,
        )
    return locked


def verify_snapshot(model: LockedModel, directory: Path) -> list[str]:
    """Return human-readable integrity failures for one downloaded snapshot."""
    failures: list[str] = []
    for filename, expected in model.files.items():
        target = directory / filename
        if not target.is_file():
            failures.append(f"missing {filename}")
            continue
        size = target.stat().st_size
        if size != expected.size:
            failures.append(f"{filename}: size {size}, expected {expected.size}")
            continue
        digest = hashlib.sha256()
        with target.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
        actual = digest.hexdigest()
        if actual != expected.sha256:
            failures.append(f"{filename}: sha256 {actual}, expected {expected.sha256}")
    return failures


def model_directory(
    name: str,
    *,
    cache_dir: Path | None = None,
    download: bool = False,
) -> Path:
    """Resolve a locked model to a verified local directory."""
    model = load_locked_models()[name]
    kwargs: dict[str, object] = {
        "repo_id": model.repository,
        "revision": model.revision,
        "allow_patterns": list(model.files),
    }
    if cache_dir is not None:
        kwargs["cache_dir"] = str(cache_dir)
    if model.local_directory:
        local_target = repo_root() / model.local_directory
        kwargs["local_dir"] = str(local_target)
        if local_target.is_dir():
            failures = verify_snapshot(model, local_target)
            if not failures:
                return local_target
            if not download:
                joined = "; ".join(failures)
                raise RuntimeError(f"model integrity check failed for {name}: {joined}")

    try:
        directory = Path(snapshot_download(**kwargs, local_files_only=True))
    except (OSError, RuntimeError, ValueError) as local_error:
        if not download:
            raise RuntimeError(
                f"could not find locked model {name}; run "
                f"`lecturebridge-models download --model {name}`"
            ) from local_error
    else:
        failures = verify_snapshot(model, directory)
        if not failures:
            return directory
        if not download:
            joined = "; ".join(failures)
            raise RuntimeError(f"model integrity check failed for {name}: {joined}")

    try:
        directory = Path(
            snapshot_download(**kwargs, local_files_only=False, force_download=True)
        )
    except (OSError, RuntimeError, ValueError) as exc:
        raise RuntimeError(
            f"could not download locked model {name}; run "
            f"`lecturebridge-models download --model {name}`"
        ) from exc

    failures = verify_snapshot(model, directory)
    if failures:
        joined = "; ".join(failures)
        raise RuntimeError(f"model integrity check failed for {name}: {joined}")
    return directory


def selected_model_names(
    model: str,
    *,
    include_translation: bool,
    include_all: bool,
) -> list[str]:
    names = list(SUPPORTED_MODELS) if include_all else [model]
    if include_translation:
        names.append(TRANSLATION_MODEL)
    return names


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manage locked LectureBridge models.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    for command in ("download", "verify"):
        child = subparsers.add_parser(command)
        child.add_argument("--model", choices=SUPPORTED_MODELS, default=DEFAULT_MODEL)
        child.add_argument("--translation", action="store_true")
        child.add_argument("--all", action="store_true")
        child.add_argument("--cache-dir", type=Path)
    subparsers.add_parser("list")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    locked = load_locked_models()
    if args.command == "list":
        for model in sorted(
            locked.values(),
            key=lambda item: (
                item.kind != "asr",
                sum(f.size for f in item.files.values()),
            ),
        ):
            print(
                f"{model.name}\t{model.kind}\t{model.repository}@{model.revision}"
                f"\tlicense={model.license}"
            )
        return 0

    names = selected_model_names(
        args.model,
        include_translation=args.translation,
        include_all=args.all,
    )
    failed = False
    for name in names:
        try:
            directory = model_directory(
                name,
                cache_dir=args.cache_dir,
                download=args.command == "download",
            )
        except RuntimeError as exc:
            failed = True
            print(f"[FAIL] {name}: {exc}", file=sys.stderr)
        else:
            print(f"[PASS] {name}: {directory}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
