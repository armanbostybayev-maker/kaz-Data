import re
import unicodedata

REPLACEMENTS = {
    "г.": " ", "область": " ", "облысы": " ", "район": " ",
    "городская администрация": " ", "г.а.": " ", "қ.ә.": " ",
}


def normalize_name(value: str | None) -> str:
    text = unicodedata.normalize("NFKC", value or "").casefold().replace("ё", "е")
    for old, new in REPLACEMENTS.items():
        text = text.replace(old, new)
    text = re.sub(r"[^0-9a-zа-яәіңғүұқөһ]+", " ", text)
    return " ".join(text.split())


def parse_number(value: object) -> float | None:
    if value is None: return None
    text = str(value).strip().replace("\u00a0", "").replace(" ", "").replace(",", ".")
    if text in {"", "-", "…", "...", "x", "X"}: return None
    try: return float(text)
    except ValueError: return None

