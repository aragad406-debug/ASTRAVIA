"""Text helpers: Arabic-aware normalization for search, and short-language helpers."""
import re
import unicodedata

from django.conf import settings
from django.utils import translation

# Arabic diacritics (tashkeel), Quranic marks and tatweel.
_ARABIC_MARKS = re.compile("[ؐ-ًؚ-ٰٟۖ-ۭـ]")
_ARABIC_FOLD = str.maketrans({
    "أ": "ا", "إ": "ا", "آ": "ا", "ٱ": "ا",
    "ى": "ي", "ئ": "ي",
    "ؤ": "و",
    "ة": "ه",
    "گ": "ك", "ک": "ك", "ی": "ي",
})
_WS = re.compile(r"\s+")


def normalize_search_text(value: str) -> str:
    """Fold case, strip Latin accents and Arabic diacritics, unify Arabic letter variants.

    The same function is applied to stored search documents and to user queries, so
    "أسترافيا", "استرافيا" and "أَسْتْرَافِيَا" all match each other.
    """
    if not value:
        return ""
    value = unicodedata.normalize("NFKC", str(value))
    value = _ARABIC_MARKS.sub("", value)
    value = value.translate(_ARABIC_FOLD)
    # Strip Latin accents (é -> e) without touching Arabic letters.
    decomposed = unicodedata.normalize("NFD", value)
    value = "".join(ch for ch in decomposed if not (unicodedata.category(ch) == "Mn" and ord(ch) < 0x0600))
    return _WS.sub(" ", value.casefold()).strip()


def current_language() -> str:
    lang = (translation.get_language() or settings.LANGUAGE_CODE or "en").split("-")[0]
    return lang if lang in {code for code, _ in settings.LANGUAGES} else "en"


def is_rtl(lang: str | None = None) -> bool:
    return (lang or current_language()) in settings.RTL_LANGUAGES
