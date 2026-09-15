"""Supported ASR models and their local cache identities."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ModelSpec:
    """One supported Faster-Whisper model."""

    name: str
    repository: str
    role: str

    @property
    def cache_directory_name(self) -> str:
        return f"models--{self.repository.replace('/', '--')}"


MODEL_SPECS = (
    ModelSpec(
        "distil-large-v3.5",
        "distil-whisper/distil-large-v3.5-ct2",
        "high-accuracy debate default",
    ),
    ModelSpec("small.en", "Systran/faster-whisper-small.en", "fallback level 1"),
    ModelSpec("base.en", "Systran/faster-whisper-base.en", "fallback level 2"),
    ModelSpec("tiny.en", "Systran/faster-whisper-tiny.en", "emergency fallback"),
)

DEFAULT_MODEL = MODEL_SPECS[0].name
SUPPORTED_MODELS = tuple(spec.name for spec in MODEL_SPECS)
MODEL_BY_NAME = {spec.name: spec for spec in MODEL_SPECS}
