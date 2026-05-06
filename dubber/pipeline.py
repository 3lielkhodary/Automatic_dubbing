import logging
import os
import tempfile
from pathlib import Path

from config import settings
from .core import AudioExtractor, Transcriber, Translator, Synthesiser, VideoMerger
from .models import DubbingResult
from .utils.language import normalise_language_code, to_bcp47

log = logging.getLogger(__name__)


class Pipeline:
    def __init__(self, whisper_model: str = settings.WHISPER_MODEL) -> None:
        self._extractor = AudioExtractor()
        self._transcriber = Transcriber(model_name=whisper_model)
        self._translator = Translator()
        self._synthesiser = Synthesiser()
        self._merger = VideoMerger()

    def run(
        self,
        video_path: str,
        target_lang: str = settings.DEFAULT_TARGET_LANGUAGE,
        output_path: str | None = None,
        source_lang: str = settings.DEFAULT_SOURCE_LANGUAGE,
    ) -> DubbingResult:

        video_path = str(Path(video_path).resolve())
        output_path = output_path or self._default_output_path(video_path, target_lang)
        output_path = str(Path(output_path).resolve())

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        src_short = normalise_language_code(source_lang)
        src_bcp47 = to_bcp47(source_lang)

        log.info("=" * 60)
        log.info("Video Dubbing Pipeline")
        log.info("Input   : %s", video_path)
        log.info("Source  : %s", src_bcp47)
        log.info("Target  : %s", target_lang)
        log.info("Output  : %s", output_path)
        log.info("=" * 60)

        # temporary mp3 outside temp folder
        mp3_path = str(Path("dubbed_temp.mp3").resolve())

        with tempfile.TemporaryDirectory() as tmp:
            wav_path = os.path.join(tmp, "audio.wav")

            # Step 1
            self._extractor.extract(video_path, wav_path)

            # Step 2
            original_text = self._transcriber.transcribe(
                wav_path,
                language=src_bcp47
            )
            log.info("Original : %s...", original_text[:100])

            # Step 3
            translated_text = self._translator.translate(
                original_text,
                src_short,
                target_lang
            )
            log.info("Translated: %s...", translated_text[:100])

            # Step 4
            metrics = self._synthesiser.synthesise(
                text=translated_text,
                language=target_lang,
                output_mp3=mp3_path,
                reference_wav=wav_path,
            )

        self._merger.merge(video_path, mp3_path, output_path)

        # cleanup temp mp3
        if os.path.exists(mp3_path):
            try:
                os.remove(mp3_path)
            except Exception:
                pass

        return DubbingResult(
            output_path=output_path,
            source_language=src_bcp47,
            target_language=target_lang,
            original_text=original_text,
            translated_text=translated_text,
            original_duration_s=metrics["original_duration_s"],
            dubbed_duration_s=metrics["dubbed_duration_s"],
            tempo_factor=metrics["tempo_factor"],
        )

    @staticmethod
    def _default_output_path(video_path: str, target_lang: str) -> str:
        p = Path(video_path)
        return str(p.with_stem(f"{p.stem}_dubbed_{target_lang}"))