"""Build the immutable data bundle consumed by the GitHub Pages frontend."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
PUBLIC = ROOT / "apps" / "frontend" / "public" / "data"


def main() -> None:
    PUBLIC.mkdir(parents=True, exist_ok=True)
    for source, target in [
        ("territories_adm1.geojson", "territories-adm1.geojson"),
        ("territories_adm2.geojson", "territories-adm2.geojson"),
    ]:
        shutil.copyfile(PROCESSED / source, PUBLIC / target)

    catalog = json.loads((PUBLIC / "catalog.json").read_text(encoding="utf-8"))
    count = sum(len(c["indicators"]) for c in catalog["categories"])
    print(json.dumps({"territories": [20, 205], "indicators": count, "output": str(PUBLIC)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
