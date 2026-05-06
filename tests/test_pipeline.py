"""Integration-style tests for the Pipeline using mocked components."""

import pytest
from unittest.mock import MagicMock
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dubber.pipeline import Pipeline
from dubber.models import DubbingResult


@pytest.fixture
def pipeline():
    p = Pipeline.__new__(Pipeline)
    p._extractor   = MagicMock()
    p._transcriber = MagicMock()
    p._translator  = MagicMock()
    p._synthesiser = MagicMock()
    p._merger      = MagicMock()

    p._transcriber.transcribe.return_value = "Hello, this is a test."
    p._translator.translate.return_value   = "مرحباً، هذا اختبار."
    p._synthesiser.synthesise.return_value = {
        "original_duration_s": 5.0,
        "dubbed_duration_s": 4.8,
        "tempo_factor": 0.96,
    }
    return p


def test_pipeline_returns_dubbing_result(pipeline, tmp_path):
    input_video = tmp_path / "sample.mp4"
    input_video.touch()
    output_video = tmp_path / "sample_dubbed_ar.mp4"

    result = pipeline.run(
        video_path=str(input_video),
        target_lang="ar",
        output_path=str(output_video),
        source_lang="en-US",
    )

    assert isinstance(result, DubbingResult)
    assert result.target_language == "ar"
    assert result.original_text == "Hello, this is a test."
    assert result.translated_text == "مرحباً، هذا اختبار."
    assert result.tempo_factor == 0.96


def test_pipeline_calls_all_five_steps(pipeline, tmp_path):
    input_video = tmp_path / "video.mp4"
    input_video.touch()

    pipeline.run(str(input_video), target_lang="fr", source_lang="en-US")

    pipeline._extractor.extract.assert_called_once()
    pipeline._transcriber.transcribe.assert_called_once()
    pipeline._translator.translate.assert_called_once()
    pipeline._synthesiser.synthesise.assert_called_once()
    pipeline._merger.merge.assert_called_once()


def test_pipeline_default_output_path():
    path = Pipeline._default_output_path("/videos/lecture.mp4", "es")
    assert path.endswith("lecture_dubbed_es.mp4")


def test_pipeline_raises_on_empty_transcription(pipeline, tmp_path):
    input_video = tmp_path / "silent.mp4"
    input_video.touch()

    pipeline._transcriber.transcribe.side_effect = ValueError("No speech detected.")

    with pytest.raises(ValueError, match="No speech detected"):
        pipeline.run(str(input_video), target_lang="ar")
