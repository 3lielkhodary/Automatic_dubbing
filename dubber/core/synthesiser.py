"""
Step 4 – Synthesise dubbed speech using Coqui XTTS-v2 (GPU voice cloning).
"""

import logging
import os
import subprocess
import tempfile

import imageio_ffmpeg
import torch
from pydub import AudioSegment
import os

os.environ["TTS_HOME"] = r"D:\Automatic_dubbing\models"
os.environ["HF_HOME"] = r"D:\Automatic_dubbing\models"
os.environ["TORCH_HOME"] = r"D:\Automatic_dubbing\models"

from TTS.api import TTS

from config import settings

# force pydub to use bundled ffmpeg
AudioSegment.converter = imageio_ffmpeg.get_ffmpeg_exe()

log = logging.getLogger(__name__)

XTTS_MODEL = "tts_models/multilingual/multi-dataset/xtts_v2"

XTTS_SUPPORTED_LANGUAGES = {
    "en", "es", "fr", "de", "it", "pt", "pl", "tr", "ru",
    "nl", "cs", "ar", "zh-cn", "hu", "ko", "ja", "hi",
}


class Synthesiser:
    def __init__(self) -> None:
        self._device = "cuda" if torch.cuda.is_available() else "cpu"
        log.info("Loading XTTS-v2 model on %s ...", self._device)
        self._tts = TTS(XTTS_MODEL, progress_bar=False).to(self._device)
        log.info("XTTS-v2 ready.")

    def synthesise(
        self,
        text: str,
        language: str,
        output_mp3: str,
        reference_wav: str,
    ) -> dict:

        if not text.strip():
            raise ValueError("Cannot synthesise empty text.")

        log.info(
            "Step 4/5 - Cloning voice and synthesising speech (XTTS-v2, %s) ...",
            self._device.upper()
        )

        metrics = self._extract_metrics(reference_wav)
        lang = self._normalise_lang(language)

        with tempfile.TemporaryDirectory() as tmp:
            raw_wav = os.path.join(tmp, "raw_tts.wav")

            self._synthesise_raw(
                text=text,
                language=lang,
                output_wav=raw_wav,
                reference_wav=reference_wav,
            )

            adjusted_wav = self._adjust_tempo(
                raw_wav,
                metrics["duration_s"],
                tmp
            )

            adjusted_audio = AudioSegment.from_wav(adjusted_wav)
            dubbed_duration = len(adjusted_audio) / 1000.0

            self._normalise_loudness(
                adjusted_wav,
                metrics["dbfs"],
                output_mp3
            )

        tempo_factor = (
            dubbed_duration / metrics["duration_s"]
            if metrics["duration_s"] > 0 else 1.0
        )

        return {
            "original_duration_s": metrics["duration_s"],
            "dubbed_duration_s": dubbed_duration,
            "tempo_factor": tempo_factor,
        }

    def _synthesise_raw(
        self,
        text: str,
        language: str,
        output_wav: str,
        reference_wav: str,
    ) -> None:

        self._tts.tts_to_file(
            text=text,
            speaker_wav=reference_wav,
            language=language,
            file_path=output_wav,
        )

    def _extract_metrics(self, wav_path: str) -> dict:
        audio = AudioSegment.from_wav(wav_path)
        return {
            "duration_s": len(audio) / 1000.0,
            "dbfs": audio.dBFS,
        }

    def _adjust_tempo(self, wav_path: str, target_duration_s: float, tmp_dir: str) -> str:
        audio = AudioSegment.from_wav(wav_path)
        tts_duration_s = len(audio) / 1000.0

        if target_duration_s <= 0:
            return wav_path

        raw_tempo = tts_duration_s / target_duration_s
        tempo = self._clamp_tempo(raw_tempo)

        filter_chain = self._build_atempo_filter(tempo)
        output_path = os.path.join(tmp_dir, "tempo_adjusted.wav")

        cmd = [
            imageio_ffmpeg.get_ffmpeg_exe(),
            "-y",
            "-i", wav_path,
            "-filter:a", filter_chain,
            output_path,
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            return wav_path

        return output_path

    def _normalise_loudness(self, wav_path: str, target_dbfs: float, output_path: str) -> None:
        audio = AudioSegment.from_wav(wav_path)

        if target_dbfs > settings.SILENCE_THRESHOLD_DBFS:
            gain_db = target_dbfs - audio.dBFS
            audio = audio.apply_gain(gain_db)

        audio.export(output_path, format="mp3")

    def _clamp_tempo(self, tempo: float) -> float:
        return max(settings.TEMPO_MIN, min(tempo, settings.TEMPO_MAX))

    @staticmethod
    def _normalise_lang(lang: str) -> str:
        mapping = {"zh": "zh-cn", "zh-CN": "zh-cn", "zh-TW": "zh-cn"}
        return mapping.get(lang, lang.split("-")[0])

    @staticmethod
    def _build_atempo_filter(tempo: float) -> str:
        steps = []
        remaining = tempo

        while remaining > 2.0:
            steps.append("atempo=2.0")
            remaining /= 2.0

        while remaining < 0.5:
            steps.append("atempo=0.5")
            remaining /= 0.5

        steps.append(f"atempo={remaining:.4f}")
        return ",".join(steps)