import hashlib
import json
from pathlib import Path

from lecturebridge.model_store import (
    LockedFile,
    LockedModel,
    load_locked_models,
    model_directory,
    selected_model_names,
    verify_snapshot,
)

ROOT = Path(__file__).resolve().parents[1]


def test_lock_manifest_contains_all_supported_models() -> None:
    locked = load_locked_models()

    assert {
        "distil-large-v3.5",
        "small.en",
        "base.en",
        "tiny.en",
        "nllb-200-distilled-600M",
    } == set(locked)
    assert all(len(model.revision) == 40 for model in locked.values())


def test_packaged_lock_manifest_matches_repository_manifest() -> None:
    assert (ROOT / "models.lock.json").read_bytes() == (
        ROOT / "src" / "lecturebridge" / "models.lock.json"
    ).read_bytes()


def test_load_locked_models_rejects_unknown_schema(tmp_path: Path) -> None:
    manifest = tmp_path / "models.lock.json"
    manifest.write_text(json.dumps({"schema_version": 2}), encoding="utf-8")

    try:
        load_locked_models(manifest)
    except ValueError as exc:
        assert "unsupported" in str(exc)
    else:
        raise AssertionError("unsupported lock schema was accepted")


def test_verify_snapshot_checks_size_and_sha256(tmp_path: Path) -> None:
    content = b"locked model data"
    (tmp_path / "model.bin").write_bytes(content)
    model = LockedModel(
        name="fixture",
        kind="asr",
        repository="example/model",
        revision="0" * 40,
        license="mit",
        files={
            "model.bin": LockedFile(
                size=len(content), sha256=hashlib.sha256(content).hexdigest()
            )
        },
    )

    assert verify_snapshot(model, tmp_path) == []
    (tmp_path / "model.bin").write_bytes(b"tampered")
    assert "size" in verify_snapshot(model, tmp_path)[0]


def test_model_selection_keeps_translation_opt_in() -> None:
    assert selected_model_names(
        "tiny.en", include_translation=False, include_all=False
    ) == ["tiny.en"]
    assert selected_model_names(
        "tiny.en", include_translation=True, include_all=False
    ) == ["tiny.en", "nllb-200-distilled-600M"]


def test_download_uses_verified_cache_before_network(monkeypatch, tmp_path: Path) -> None:
    content = b"cached"
    (tmp_path / "model.bin").write_bytes(content)
    locked = LockedModel(
        name="fixture",
        kind="asr",
        repository="example/model",
        revision="0" * 40,
        license="mit",
        files={
            "model.bin": LockedFile(
                size=len(content), sha256=hashlib.sha256(content).hexdigest()
            )
        },
    )
    calls: list[dict[str, object]] = []

    def fake_snapshot_download(**kwargs):
        calls.append(kwargs)
        return str(tmp_path)

    monkeypatch.setattr(
        "lecturebridge.model_store.load_locked_models", lambda: {"fixture": locked}
    )
    monkeypatch.setattr(
        "lecturebridge.model_store.snapshot_download", fake_snapshot_download
    )

    assert model_directory("fixture", download=True) == tmp_path
    assert len(calls) == 1
    assert calls[0]["local_files_only"] is True
