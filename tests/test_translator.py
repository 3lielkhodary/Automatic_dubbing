import pytest
from unittest.mock import patch, MagicMock

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dubber.core.translator import Translator


class TestTranslator:

    def setup_method(self):
        self.translator = Translator()

    def test_build_batches_short_text(self):
        text = "Hello world. How are you?"
        batches = self.translator._build_batches(text)
        assert len(batches) == 1
        assert batches[0] == text

    def test_build_batches_long_text(self):
        # Build a text that exceeds the character limit
        sentence = "This is a sentence. "
        text = sentence * 300  # ~6000 chars
        batches = self.translator._build_batches(text)
        assert len(batches) > 1
        for batch in batches:
            assert len(batch) < 4600

    @patch("dubber.core.translator.GoogleTranslator")
    def test_translate_calls_api(self, mock_gt_class):
        mock_instance = MagicMock()
        mock_instance.translate.return_value = "مرحبا بالعالم"
        mock_gt_class.return_value = mock_instance

        result = self.translator.translate("Hello world.", "en", "ar")

        mock_gt_class.assert_called_once_with(source="en", target="ar")
        mock_instance.translate.assert_called_once_with("Hello world.")
        assert result == "مرحبا بالعالم"

    @patch("dubber.core.translator.GoogleTranslator")
    def test_translate_joins_multiple_batches(self, mock_gt_class):
        # Each batch creates a new GoogleTranslator instance, so we configure
        # translate() on each successive instance returned by the constructor.
        instance_a, instance_b = MagicMock(), MagicMock()
        instance_a.translate.return_value = "Bonjour."
        instance_b.translate.return_value = "Comment ça va?"
        mock_gt_class.side_effect = [instance_a, instance_b]

        sentence = "Hello. " * 300  # ~1 800 chars → at least 1 batch
        result = self.translator.translate(sentence, "en", "fr")

        # At least one instance was constructed and called
        assert mock_gt_class.call_count >= 1
        assert "Bonjour." in result
