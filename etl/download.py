"""Atomic downloader for the verified official BNS CSV endpoints."""
from __future__ import annotations
import gzip
import hashlib
from pathlib import Path
import requests
from etl.pipeline import RAW
from etl.sources.registry import SOURCES, csv_url


def download_all() -> dict:
    changed = 0
    session = requests.Session()
    session.headers["User-Agent"] = "kaz-data-etl/1.0 (+https://github.com/armanbostybayev-maker/kaz-Data)"
    for source in SOURCES:
        response = session.get(csv_url(source["element"]), timeout=300)
        response.raise_for_status()
        content = response.content
        if not content.startswith(b'\xef\xbb\xbf"NAM"') and not content.startswith(b'"NAM"'):
            raise ValueError(f"Unexpected BNS response for {source['indicator']}")
        target = RAW / source["file"]; target.parent.mkdir(parents=True, exist_ok=True)
        stored = gzip.compress(content, compresslevel=9, mtime=0) if target.suffix == ".gz" else content
        old = target.read_bytes() if target.exists() else b""
        if hashlib.sha256(old).digest() == hashlib.sha256(stored).digest(): continue
        temporary = target.with_suffix(target.suffix + ".tmp")
        temporary.write_bytes(stored); temporary.replace(target); changed += 1
    return {"checked":len(SOURCES), "changed":changed}
