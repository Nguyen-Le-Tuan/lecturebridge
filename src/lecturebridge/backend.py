"""Small adapter around the pinned WLK package; imports/models stay lazy."""

from __future__ import annotations

import asyncio

from lecturebridge.languages import source_language, validate_model_language


class WLKBackend:
    def __init__(self, model: str, model_dir, runtime, language: str = "en"):
        validate_model_language(model, language)
        self.model = model
        self.language = language
        self.model_dir = model_dir
        self.runtime = runtime
        self.engine = None

    async def start(self):
        await asyncio.to_thread(self._load)

    def _load(self):
        from whisperlivekit import TranscriptionEngine
        from whisperlivekit.local_agreement.backends import FasterWhisperASR

        runtime = self.runtime

        def load_locked_model(_self, model_size=None, cache_dir=None, model_dir=None):
            from faster_whisper import WhisperModel

            return WhisperModel(
                str(self.model_dir),
                device=runtime.device,
                compute_type=runtime.compute_type,
                cpu_threads=2,
                num_workers=1,
                local_files_only=True,
            )

        # WLK 0.2.26 has no faster-whisper device/compute_type constructor options.
        # Scope this compatibility hook to engine construction, then restore it.
        original = FasterWhisperASR.load_model
        FasterWhisperASR.load_model = load_locked_model
        try:
            self.engine = TranscriptionEngine(
                backend="faster-whisper",
                backend_policy="localagreement",
                model_size=self.model,
                model_dir=str(self.model_dir),
                lan=source_language(self.language).whisper,
                pcm_input=True,
                pause_segmentation_seconds=1.2,
                diarization=False,
                target_language="",
            )
        finally:
            FasterWhisperASR.load_model = original

    def processor(self):
        from whisperlivekit import AudioProcessor

        return AudioProcessor(transcription_engine=self.engine)

    async def close(self):
        pass
