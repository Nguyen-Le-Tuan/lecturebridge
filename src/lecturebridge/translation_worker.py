"""Isolated, CPU-only NLLB worker; one bounded request at a time over stdio."""

from __future__ import annotations

import json
import os
import sys

from lecturebridge.languages import LANGUAGES


def translate_text(translator, tokenizer, text: str, source_code: str) -> str:
    """Translate one bounded request; objects are injected for CPU-only unit tests."""
    if source_code not in {profile.nllb for profile in LANGUAGES.values()}:
        raise ValueError("Unsupported translation source")
    tokens = tokenizer.encode(text, add_special_tokens=False).tokens[:256]
    result = translator.translate_batch(
        [[source_code, *tokens, "</s>"]],
        target_prefix=[["vie_Latn"]],
        beam_size=1,
        max_decoding_length=256,
    )[0].hypotheses[0]
    ids = [tokenizer.token_to_id(token) for token in result if token != "vie_Latn"]
    return tokenizer.decode(
        [token for token in ids if token is not None], skip_special_tokens=True
    )


def main() -> None:
    os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
    os.environ["OMP_NUM_THREADS"] = "2"
    os.environ["TOKENIZERS_PARALLELISM"] = "false"
    from pathlib import Path

    import ctranslate2
    from tokenizers import Tokenizer

    directory = Path(sys.argv[1])
    try:
        tokenizer = Tokenizer.from_file(str(directory / "tokenizer.json"))
        translator = ctranslate2.Translator(
            str(directory),
            device="cpu",
            compute_type="int8",
            inter_threads=1,
            intra_threads=2,
        )
        print(json.dumps({"ready": True}), flush=True)
        for line in sys.stdin:
            request = json.loads(line)
            text = translate_text(
                translator, tokenizer, request["text"], request["source_language"]
            )
            print(json.dumps({"text": text}, ensure_ascii=False), flush=True)
    except Exception:  # noqa: BLE001 - process boundary, redact third-party exception text
        # Never include request text or private paths in process logs.
        print(json.dumps({"error": "translation_failed"}), flush=True)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
