"""Supported ASR models and their local cache identities."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ModelSpec:
    """One supported Faster-Whisper model."""

    name: str
    repository: str
    revision: str
    role: str

    @property
    def cache_directory_name(self) -> str:
        return f"models--{self.repository.replace('/', '--')}"


MODEL_SPECS = (
    ModelSpec(
        "distil-large-v3.5",
        "distil-whisper/distil-large-v3.5-ct2",
        "9793ccc07920e0f830e1dba0343efcdf0ef8c903",
        "high-accuracy debate default",
    ),
    ModelSpec(
        "small.en",
        "Systran/faster-whisper-small.en",
        "d1d751a5f8271d482d14ca55d9e2deeebbae577f",
        "fallback level 1",
    ),
    ModelSpec(
        "base.en",
        "Systran/faster-whisper-base.en",
        "3d3d5dee26484f91867d81cb899cfcf72b96be6c",
        "fallback level 2",
    ),
    ModelSpec(
        "tiny.en",
        "Systran/faster-whisper-tiny.en",
        "0d3d19a32d3338f10357c0889762bd8d64bbdeba",
        "emergency fallback",
    ),
)

DEFAULT_MODEL = MODEL_SPECS[0].name
SUPPORTED_MODELS = tuple(spec.name for spec in MODEL_SPECS)
MODEL_BY_NAME = {spec.name: spec for spec in MODEL_SPECS}
