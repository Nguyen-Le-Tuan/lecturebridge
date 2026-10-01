"""Explicit source-language profiles shared by ASR, translation, and the UI."""

from dataclasses import dataclass


@dataclass(frozen=True)
class SourceLanguage:
    label: str
    whisper: str
    nllb: str


LANGUAGES = {
    "en": SourceLanguage("Tiếng Anh", "en", "eng_Latn"),
    "zh": SourceLanguage("Tiếng Trung", "zh", "zho_Hans"),
    "zh-Hant": SourceLanguage("Tiếng Trung (phồn thể)", "zh", "zho_Hant"),
    "ja": SourceLanguage("Tiếng Nhật", "ja", "jpn_Jpan"),
    "ko": SourceLanguage("Tiếng Hàn", "ko", "kor_Hang"),
}


def source_language(code: str) -> SourceLanguage:
    try:
        return LANGUAGES[code]
    except KeyError:
        raise ValueError(f"Unsupported source language: {code}") from None


def validate_model_language(model: str, language: str) -> None:
    profile = source_language(language)
    if profile.whisper != "en" and (
        model.endswith(".en") or model == "distil-large-v3.5"
    ):
        raise ValueError(
            f"{model} supports English only; for --language {language}, "
            "choose a multilingual model, e.g. --model tiny or --model small"
        )
