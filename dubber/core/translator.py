"""Step 3 – Translate transcribed text into the target language."""

import logging
import re

from deep_translator import GoogleTranslator

from config import settings

log = logging.getLogger(__name__)


class Translator:

    _SENTENCE_RE = re.compile(r'(?<=[.!?])\s+')

    def translate(self, text: str, source_lang: str, target_lang: str) -> str:

        log.info("Step 3/5 – Translating from '%s' to '%s' …", source_lang, target_lang)

        batches = self._build_batches(text)
        log.info("  Translating %d batch(es)", len(batches))

        translated_parts = [
            GoogleTranslator(source=source_lang, target=target_lang).translate(batch)
            for batch in batches
        ]

        result = " ".join(translated_parts)
        log.info("  Translation complete (%d chars)", len(result))
        return result



    def _build_batches(self, text: str) -> list[str]:
        """Split text into batches that each stay within the API char limit."""
        sentences = self._SENTENCE_RE.split(text)
        batches: list[str] = []
        current = ""

        for sentence in sentences:
            if len(current) + len(sentence) + 1 < settings.TRANSLATION_MAX_CHARS:
                current = f"{current} {sentence}".strip()
            else:
                if current:
                    batches.append(current)
                current = sentence

        if current:
            batches.append(current)

        return batches
