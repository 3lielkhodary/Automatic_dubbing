"""
Central configuration for the video dubbing pipeline.

All tuneable values live here. Override any setting with an environment variable.
"""

import os

# ---------------------------------------------------------------------------
# Audio extraction
# ---------------------------------------------------------------------------

# Sample rate for the extracted WAV fed to Whisper.
# Whisper internally resamples to 16 kHz regardless, but 16 kHz keeps the
# intermediate file small.
AUDIO_SAMPLE_RATE = int(os.getenv("DUBBER_SAMPLE_RATE", 16_000))

# Mono audio is sufficient for speech recognition and voice cloning.
AUDIO_CHANNELS = 1

# ---------------------------------------------------------------------------
# Transcription (Whisper)
# ---------------------------------------------------------------------------

# Whisper model size: tiny | base | small | medium | large
# Larger = more accurate, slower, more VRAM.
#   tiny  ~1 GB VRAM   base  ~1 GB   small ~2 GB   medium ~5 GB   large ~10 GB
WHISPER_MODEL = os.getenv("DUBBER_WHISPER_MODEL", "base")

# Default source language passed to Whisper (ISO 639-1, e.g. "en").
# Set to None or "" to let Whisper auto-detect.
DEFAULT_SOURCE_LANGUAGE = os.getenv("DUBBER_SOURCE_LANG", "en-US")

# ---------------------------------------------------------------------------
# Translation
# ---------------------------------------------------------------------------

# Maximum characters per translation API request.
TRANSLATION_MAX_CHARS = int(os.getenv("DUBBER_TRANSLATE_MAX_CHARS", 4_500))

# Default target language (ISO 639-1 short code).
DEFAULT_TARGET_LANGUAGE = os.getenv("DUBBER_TARGET_LANG", "ar")

# ---------------------------------------------------------------------------
# Voice cloning (Coqui XTTS-v2)
# ---------------------------------------------------------------------------

# Minimum length (seconds) of the reference audio clip fed to XTTS-v2.
# XTTS-v2 needs at least 3 seconds of clean speech to clone reliably.
XTTS_MIN_REFERENCE_S = 3.0

# ---------------------------------------------------------------------------
# Tempo & loudness matching
# ---------------------------------------------------------------------------

# Tempo multiplier clamp — values outside [0.6, 2.0] produce unintelligible speech.
TEMPO_MIN = float(os.getenv("DUBBER_TEMPO_MIN", 0.6))
TEMPO_MAX = float(os.getenv("DUBBER_TEMPO_MAX", 2.0))

# Average loudness (dBFS) below which loudness normalisation is skipped
# (treats the source clip as silent).
SILENCE_THRESHOLD_DBFS = float(os.getenv("DUBBER_SILENCE_THRESHOLD", -60.0))

# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

# "copy" avoids re-encoding the video stream — fast and lossless.
VIDEO_CODEC = "copy"

# AAC is universally compatible for the dubbed audio track.
AUDIO_CODEC = "aac"
