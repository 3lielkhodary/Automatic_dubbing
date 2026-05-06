"""Unit tests for language utility functions."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dubber.utils.language import normalise_language_code, to_bcp47


class TestNormaliseLanguageCode:

    def test_short_code_unchanged(self):
        assert normalise_language_code("fr") == "fr"

    def test_bcp47_stripped_to_short(self):
        assert normalise_language_code("en-US") == "en"
        assert normalise_language_code("fr-FR") == "fr"

    def test_chinese_simplified_kept(self):
        assert normalise_language_code("zh-CN") == "zh-CN"

    def test_chinese_traditional_kept(self):
        assert normalise_language_code("zh-TW") == "zh-TW"


class TestToBcp47:

    def test_already_bcp47_unchanged(self):
        assert to_bcp47("en-GB") == "en-GB"
        assert to_bcp47("fr-FR") == "fr-FR"

    def test_english_maps_to_en_us(self):
        assert to_bcp47("en") == "en-US"

    def test_chinese_maps_to_zh_cn(self):
        assert to_bcp47("zh") == "zh-CN"

    def test_portuguese_maps_to_pt_br(self):
        assert to_bcp47("pt") == "pt-BR"

    def test_generic_short_code(self):
        assert to_bcp47("ar") == "ar-AR"
        assert to_bcp47("de") == "de-DE"
