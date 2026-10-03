import json
from pathlib import Path


LOCALES_DIR = Path(__file__).parent / "locales"
SUPPORTED_LANGUAGES = ("ru", "en", "he")


def load_locale(language: str):
    if language not in SUPPORTED_LANGUAGES:
        language = "en"

    path = LOCALES_DIR / f"{language}.json"

    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def get_text(language: str | None, key: str, **kwargs):
    language = language \
        if language in SUPPORTED_LANGUAGES \
        else "en"

    text = load_locale(language)[key]

    if isinstance(text, list):
        return [
            item.format(**kwargs)
            for item in text
        ]

    return text.format(**kwargs)