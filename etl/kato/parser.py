from dataclasses import asdict, dataclass
from pathlib import Path
import csv
import openpyxl


@dataclass(frozen=True)
class KatoRow:
    kato: str
    parent_kato: str | None
    name_ru: str
    name_kk: str
    admin_level: int
    admin_type: str
    is_active: bool
    kato_version: str


def _level(code: str) -> int:
    if code[2:] == "0000000": return 1
    if code[4:] == "00000": return 2
    if code[6:] == "000": return 3
    return 4


def _type(name: str) -> str:
    lower = name.casefold()
    if "область" in lower: return "region"
    if "район" in lower: return "district"
    if "г.а." in lower or lower.startswith("г."): return "city"
    if "с.о." in lower: return "rural_district"
    if lower.startswith("с."): return "village"
    return "territory"


def _parent(code: str, codes: set[str]) -> str | None:
    candidates = [code[:6]+"000", code[:4]+"00000", code[:2]+"0000000"]
    for candidate in candidates:
        if candidate != code and candidate in codes: return candidate
    return None


def parse_kato(path: Path, version: str = "КАТО НК РК 11-2025 / 18.09.2026") -> list[KatoRow]:
    sheet = openpyxl.load_workbook(path, read_only=True, data_only=True).active
    raw = [r for r in sheet.iter_rows(min_row=2, values_only=True) if r[0]]
    codes = {str(r[0]).split(".")[0].zfill(9) for r in raw}
    return [KatoRow(code, _parent(code, codes), str(r[7] or "").strip(), str(r[6] or "").strip(),
                    _level(code), _type(str(r[7] or "")), True, version)
            for r in raw for code in [str(r[0]).split(".")[0].zfill(9)]]


def write_csv(rows: list[KatoRow], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=asdict(rows[0]).keys())
        writer.writeheader(); writer.writerows(asdict(row) for row in rows)

