from deep_translator import GoogleTranslator


def normalise_language_code(lang: str) -> str:
    """
    Return the ISO 639-1 short code from a BCP-47 or short code.

    Examples
    --------
    >>> normalise_language_code("en-US")
    'en'
    >>> normalise_language_code("zh-CN")
    'zh-CN'   # kept intact — Google Translate uses zh-CN / zh-TW
    >>> normalise_language_code("fr")
    'fr'
    """
    # Special cases where the full tag is meaningful to Google Translate
    keep_full = {"zh-CN", "zh-TW"}
    if lang in keep_full:
        return lang
    return lang.split("-")[0]


def to_bcp47(lang: str) -> str:
    """
    Ensure the language code is in BCP-47 format for the STT API.

    Examples
    --------
    >>> to_bcp47("en")
    'en-US'
    >>> to_bcp47("fr")
    'fr-FR'
    >>> to_bcp47("en-GB")
    'en-GB'
    """
    if "-" in lang:
        return lang   # already BCP-47
    # Simple heuristic: duplicate the code as the region tag
    upper = lang.upper()
    overrides = {
        "EN": "en-US",
        "ZH": "zh-CN",
        "PT": "pt-BR",
    }
    return overrides.get(upper, f"{lang}-{upper}")


def get_supported_languages() -> dict[str, str]:
    """Return a mapping of {language name → ISO code} supported by Google Translate."""
    return GoogleTranslator(source="en", target="en").get_supported_languages(as_dict=True)
