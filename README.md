# Video Dubber — GPU-Accelerated

Automatically dub a video into another language.
Uses **Whisper** for transcription and **Coqui XTTS-v2** for voice cloning — both run on GPU.

---

## Project structure

```
video-dubber/
│
├── dubber/                   # Main package
│   ├── __init__.py           # Public API: Pipeline, DubbingResult
│   ├── pipeline.py           # Orchestrates all five steps
│   ├── models.py             # DubbingResult dataclass
│   ├── cli.py                # CLI entry point (video-dubber command)
│   │
│   ├── core/
│   │   ├── extractor.py      # Step 1 – Extract audio (ffmpeg)
│   │   ├── transcriber.py    # Step 2 – Speech to text (Whisper, GPU)
│   │   ├── translator.py     # Step 3 – Translate text (Google Translate)
│   │   ├── synthesiser.py    # Step 4 – Voice cloning TTS (Coqui XTTS-v2, GPU)
│   │   └── merger.py         # Step 5 – Merge audio into video (ffmpeg)
│   │
│   └── utils/
│       └── language.py       # Language code helpers
│
├── config/
│   └── settings.py           # All tuneable values + env-var overrides
│
├── tests/
│   ├── test_pipeline.py
│   ├── test_translator.py
│   └── test_language_utils.py
│
├── scripts/
│   └── dub_video.py          # Run without pip install
│
├── setup.py
├── requirements.txt
└── README.md
```

---

## Pipeline

```
Video
 │
 ▼  AudioExtractor   ffmpeg → 16 kHz mono WAV
 │
 ▼  Transcriber      Whisper (GPU) → original text
 │
 ▼  Translator       Google Translate → translated text
 │
 ▼  Synthesiser      Coqui XTTS-v2 (GPU) → cloned voice speaking translated text
 │                   + ffmpeg atempo (pace matching)
 │                   + pydub gain (loudness matching)
 │
 ▼  VideoMerger      ffmpeg stream copy → dubbed video
 │
Dubbed video
```

---

## Installation

### 1. System dependency

```bash
# Ubuntu / Debian
sudo apt install ffmpeg

# macOS
brew install ffmpeg
```

### 2. PyTorch (pick your CUDA version)

```bash
# CUDA 12.1 — RTX 30/40 series
pip install torch==2.3.0+cu121 torchaudio==2.3.0+cu121 \
    --index-url https://download.pytorch.org/whl/cu121

# CUDA 11.8 — RTX 20 series / older cards
pip install torch==2.3.0+cu118 torchaudio==2.3.0+cu118 \
    --index-url https://download.pytorch.org/whl/cu118

# CPU only (slower, no GPU required)
pip install torch==2.3.0 torchaudio==2.3.0 \
    --index-url https://download.pytorch.org/whl/cpu
```

> Check your CUDA version: `nvidia-smi` → look at "CUDA Version" top-right.

### 3. Python dependencies

```bash
pip install -r requirements.txt
```

### 4. (Optional) Install as a command

```bash
pip install -e .
```

---

## Usage

### Command line

```bash
# Dub an English video to Arabic
python scripts/dub_video.py my_video.mp4 --target ar

# Dub a French video to Spanish
python scripts/dub_video.py lecture.mp4 --source fr --target es

# Use a larger Whisper model for better transcription accuracy
python scripts/dub_video.py interview.mp4 --target zh-CN --whisper-model medium

# If installed with pip install -e .
video-dubber my_video.mp4 --target ar

# List all supported languages
video-dubber --list-languages
```

### Python API

```python
from dubber import Pipeline

result = Pipeline(whisper_model="base").run(
    video_path="interview.mp4",
    target_lang="ar",
    output_path="interview_ar.mp4",   # optional
    source_lang="en-US",              # optional
)

print(result.original_text)      # transcribed speech
print(result.translated_text)    # translated text
print(result.output_path)        # path to dubbed video
print(result.tempo_factor)       # how much TTS was sped up or slowed
```

---

## Configuration

All defaults live in `config/settings.py` and can be overridden with environment variables:

| Variable | Default | Description |
|---|---|---|
| `DUBBER_WHISPER_MODEL` | `base` | Whisper model size (tiny/base/small/medium/large) |
| `DUBBER_SOURCE_LANG` | `en-US` | Default source language |
| `DUBBER_TARGET_LANG` | `ar` | Default target language |
| `DUBBER_SAMPLE_RATE` | `16000` | Audio sample rate |
| `DUBBER_TEMPO_MIN` | `0.6` | Minimum tempo multiplier |
| `DUBBER_TEMPO_MAX` | `2.0` | Maximum tempo multiplier |

---

## Whisper model sizes

| Model | VRAM | Speed | Accuracy |
|---|---|---|---|
| tiny | ~1 GB | fastest | lowest |
| base | ~1 GB | fast | good ← default |
| small | ~2 GB | medium | better |
| medium | ~5 GB | slow | high |
| large | ~10 GB | slowest | best |

---

## XTTS-v2 supported languages

`en es fr de it pt pl tr ru nl cs ar zh-cn hu ko ja hi`

For other languages, the synthesiser falls back to the closest supported language.

---

## Running tests

```bash
pytest tests/ -v
```
