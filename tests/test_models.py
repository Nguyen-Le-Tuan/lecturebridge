from lecturebridge.models import DEFAULT_MODEL, MODEL_BY_NAME, MODEL_SPECS


def test_default_model_is_first_and_names_are_unique() -> None:
    names = [spec.name for spec in MODEL_SPECS]

    assert DEFAULT_MODEL == "distil-large-v3.5"
    assert names[0] == DEFAULT_MODEL
    assert len(names) == len(set(names))
    assert set(names) == set(MODEL_BY_NAME)


def test_model_cache_directory_names_match_hugging_face_layout() -> None:
    assert (
        MODEL_BY_NAME["distil-large-v3.5"].cache_directory_name
        == "models--distil-whisper--distil-large-v3.5-ct2"
    )
    assert (
        MODEL_BY_NAME["small.en"].cache_directory_name
        == "models--Systran--faster-whisper-small.en"
    )


def test_models_are_pinned_to_immutable_revisions() -> None:
    assert all(len(spec.revision) == 40 for spec in MODEL_SPECS)
    assert all(set(spec.revision) <= set("0123456789abcdef") for spec in MODEL_SPECS)
