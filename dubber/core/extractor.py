"""Step 1 – Extract the audio track from a video file."""

import logging
import subprocess
import imageio_ffmpeg
from config import settings

log = logging.getLogger(__name__)


class AudioExtractor:


    def extract(self, video_path: str, output_wav: str) -> None:

        log.info("Step 1/5 – Extracting audio …")

        cmd = [
            imageio_ffmpeg.get_ffmpeg_exe(),
            "-y",
            "-i", video_path,
            "-ac", str(settings.AUDIO_CHANNELS),
            "-ar", str(settings.AUDIO_SAMPLE_RATE),
            "-vn",
            output_wav,
        ]

        result = subprocess.run(cmd, capture_output=True)
        if result.returncode != 0:
            raise RuntimeError(
                f"ffmpeg failed during audio extraction:\n{result.stderr.decode()}"
            )

        log.info("  Audio extracted → %s", output_wav)
