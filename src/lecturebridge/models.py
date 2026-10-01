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
    ModelSpec(
        "tiny",
        "Systran/faster-whisper-tiny",
        "d90ca5fe260221311c53c58e660288d3deb8d356",
        "multilingual smoke and lightest fallback",
    ),
    ModelSpec(
        "base",
        "Systran/faster-whisper-base",
        "ebe41f70d5b6dfa9166e2c581c45c9c0cfc57b66",
        "small multilingual baseline",
    ),
    ModelSpec(
        "small",
        "Systran/faster-whisper-small",
        "536b0662742c02347bc0e980a01041f333bce120",
        "intermediate multilingual baseline",
    ),
    ModelSpec(
        "medium",
        "Systran/faster-whisper-medium",
        "08e178d48790749d25932bbc082711ddcfdfbc4f",
        "larger multilingual comparison",
    ),
    ModelSpec(
        "large-v3-turbo",
        "dropbox-dash/faster-whisper-large-v3-turbo",
        "0a363e9161cbc7ed1431c9597a8ceaf0c4f78fcf",
        "multilingual large model optimized for transcription speed",
    ),
    ModelSpec(
        "large-v3",
        "Systran/faster-whisper-large-v3",
        "edaa852ec7e145841d8ffdb056a99866b5f0a478",
        "largest supported multilingual model",
    ),
)

DEFAULT_MODEL = MODEL_SPECS[0].name
SUPPORTED_MODELS = tuple(spec.name for spec in MODEL_SPECS)
MODEL_BY_NAME = {spec.name: spec for spec in MODEL_SPECS}
