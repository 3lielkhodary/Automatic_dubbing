
import logging
import os

import numpy as np
import torch
import whisper
import imageio_ffmpeg
from scipy.io import wavfile

from config import settings

log = logging.getLogger(__name__)

# Whisper model sizes:
# tiny / base / small / medium / large
DEFAULT_MODEL = "base"


class Transcriber:
    """
    Converts a WAV audio file to text using OpenAI Whisper.
    Runs on GPU automatically when CUDA is available.
    """

    def __init__(self, model_name: str = DEFAULT_MODEL) -> None:
        self._device = "cuda" if torch.cuda.is_available() else "cpu"

        # Add bundled ffmpeg to PATH (optional fallback)
        ffmpeg_dir = os.path.dirname(imageio_ffmpeg.get_ffmpeg_exe())
        os.environ["PATH"] += os.pathsep + ffmpeg_dir

        log.info("Loading Whisper model '%s' on %s ...", model_name, self._device)
        self._model = whisper.load_model(model_name, device=self._device)
        log.info("Whisper ready.")

    def transcribe(self, wav_path: str, language: str = settings.DEFAULT_SOURCE_LANGUAGE) -> str:
        """
        Transcribe WAV file and return text.
        """

        log.info("Step 2/5 - Transcribing audio with Whisper (%s) ...", self._device.upper())

        lang_short = language.split("-")[0] if language else None

        # Read WAV directly
        sample_rate, audio = wavfile.read(wav_path)

        # Convert to float32
        audio = audio.astype(np.float32)

        # Normalize PCM int16 audio
        if np.max(np.abs(audio)) > 1.0:
            audio = audio / 32768.0

        result = self._model.transcribe(
            audio,
            language=lang_short,
            fp16=(self._device == "cuda"),
            verbose=False,
        )

        text = result["text"].strip()

        if not text:
            raise ValueError("Whisper returned an empty transcript.")

        detected_lang = result.get("language", "unknown")

        log.info("Detected language: %s", detected_lang)
        log.info("Transcription complete (%d words)", len(text.split()))

        return text