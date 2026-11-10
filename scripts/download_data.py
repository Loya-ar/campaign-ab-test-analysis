"""Download the Hillstrom MineThatData email experiment CSV and verify its checksum.

Usage:  python scripts/download_data.py
The file lands in data/raw/hillstrom.csv (gitignored).
"""
from __future__ import annotations

import hashlib
import sys
import urllib.request
from pathlib import Path

URL = (
    "http://www.minethatdata.com/"
    "Kevin_Hillstrom_MineThatData_E-MailAnalytics_DataMiningChallenge_2008.03.20.csv"
)
EXPECTED_SHA256 = "0e5893329d8b93cefecc571777672028290ab69865718020c78c7284f291aece"
EXPECTED_BYTES = 3_964_977
DEST = Path(__file__).resolve().parents[1] / "data" / "raw" / "hillstrom.csv"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    DEST.parent.mkdir(parents=True, exist_ok=True)
    if not DEST.exists():
        print(f"Downloading {URL}")
        tmp = DEST.with_suffix(".part")
        urllib.request.urlretrieve(URL, tmp)
        tmp.replace(DEST)
    size, digest = DEST.stat().st_size, sha256(DEST)
    if size != EXPECTED_BYTES or digest != EXPECTED_SHA256:
        print(f"Checksum mismatch: {size} bytes, sha256 {digest}", file=sys.stderr)
        return 1
    print(f"OK: {DEST} ({size:,} bytes, sha256 verified)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
