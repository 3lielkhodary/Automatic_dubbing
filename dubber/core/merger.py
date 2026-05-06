"""Step 5 – Replace the video's audio track with the dubbed audio."""

import logging
import os
import subprocess
import imageio_ffmpeg

from config import settings

log = logging.getLogger(__name__)


class VideoMerger:
    """
    Swaps the original audio track in a video file for the dubbed one.
    """

    def merge(self, video_path: str, audio_path: str, output_path: str) -> None:
        """
        Combine video with dubbed audio and save final result.
        """

        video_path = os.path.abspath(video_path)
        audio_path = os.path.abspath(audio_path)
        output_path = os.path.abspath(output_path)

        log.info("Step 5/5 - Merging dubbed audio into video ...")

        cmd = [
            imageio_ffmpeg.get_ffmpeg_exe(),
            "-y",
            "-i", video_path,
            "-i", audio_path,
            "-map", "0:v:0",
            "-map", "1:a:0",
            "-c:v", "copy",
            "-c:a", "aac",
            "-shortest",
            output_path,
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            raise RuntimeError(
                f"ffmpeg failed during merge:\n{result.stderr}"
            )

        log.info("Dubbed video saved -> %s", output_path)