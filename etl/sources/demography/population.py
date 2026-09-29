from pathlib import Path
import pandas as pd
from etl.normalization.text import normalize_name, parse_number

SOURCE_URL = "https://stat.gov.kz/api/iblock/element/6584/csv/file/ru/"
SOURCE_PAGE = "https://stat.gov.kz/ru/industries/socialtatistics/demography/dynamic-tables/"


def _territory_key(name: str) -> str:
    lower = (name or "").casefold()
    kind = "region" if "область" in lower else "city" if lower.startswith("г.") or " г.а." in lower else "territory"
    return f"{kind}:{normalize_name(name)}"


def parse(path: Path, kato_csv: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    raw = pd.read_csv(path, sep="\t", dtype=str)
    kato = pd.read_csv(kato_csv, dtype=str).fillna("")
    regions = kato[kato.admin_level.astype(int).eq(1)].copy()
    regions["match_key"] = regions.name_ru.map(_territory_key)
    # A normalized key is safe only when it identifies exactly one current KATO.
    # For example, "г. Алматы" and "Алматинская область" must never collapse
    # into an automatic match after administrative words are removed.
    unique = regions.groupby("match_key").filter(lambda group: len(group) == 1)
    lookup = dict(zip(unique.match_key, unique.kato))
    data = raw[(raw["СПТМ (по каталогу)"].str.casefold()=="всего") & (raw["СП"].str.casefold()=="всего") & (raw["СГНЛ"].str.casefold()=="все группы")].copy()
    data["match_key"] = data["КАТО(по каталогу)"].map(_territory_key)
    data["kato"] = data.match_key.map(lookup)
    data["year"] = data.PERIOD.str[:4].astype(int)
    data["value"] = data.VAL.map(parse_number)
    data["period"] = data.year.astype(str)
    data["indicator"] = "population"
    data["unit"] = "человек"
    data["source_url"] = SOURCE_URL
    unmatched = data[data.kato.isna()][["КАТО(по каталогу)","period"]].drop_duplicates()
    return data[data.kato.notna()][["kato","indicator","period","year","value","unit","source_url"]], unmatched
