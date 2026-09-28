"""
01_download.py
Download UN General Assembly ideal point estimates from Harvard Dataverse.

Source : Voeten, Erik. "United Nations General Assembly Ideal Point Estimates,
         1946-2025." Harvard Dataverse, doi:10.7910/DVN/LEJUQZ (V39, July 2025).
Usage  : python src/01_download.py
Output : data/raw/ (each file is verified against the md5 published by Dataverse)
"""
from pathlib import Path
import hashlib

import requests

DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"
API_URL = "https://dataverse.harvard.edu/api/access/datafile/{file_id}"

# md5 / size values are taken from the Dataverse dataset metadata,
# so the pipeline fails loudly if a download is truncated or corrupted.
FILES = [
    {
        "save_as": "IdealPointEstimates_1946-2025.csv",
        "dataverse_name": "IdealpointestimatesFP_2026FP.csv",
        "file_id": 14098429,
        "size": 1_419_867,
        "md5": "ba6b6c7b6d1344d68fc0dc94ecbbfd9d",
    },
    {
        "save_as": "Codebook_IdealPointEstimates1946-2025.txt",
        "dataverse_name": "Codebook_IdealPointEstimates1946-2025.txt",
        "file_id": 13642024,
        "size": 5_032,
        "md5": "09e645df9232ef0e30b4f203091520d0",
    },
]


def md5sum(path: Path) -> str:
    h = hashlib.md5()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def download(item: dict) -> None:
    out = DATA_DIR / item["save_as"]
    if out.exists() and md5sum(out) == item["md5"]:
        print(f"[skip] {out.name} already downloaded and verified")
        return

    url = API_URL.format(file_id=item["file_id"])
    print(f"[get ] {item['dataverse_name']} ({item['size'] / 1e6:.2f} MB)")
    tmp = out.with_suffix(out.suffix + ".part")
    with requests.get(url, stream=True, timeout=180) as r:
        r.raise_for_status()
        with open(tmp, "wb") as fh:
            for chunk in r.iter_content(chunk_size=1 << 15):
                fh.write(chunk)
    tmp.replace(out)

    got = md5sum(out)
    if got != item["md5"]:
        raise SystemExit(f"md5 mismatch for {out.name}: got {got}, expected {item['md5']}")
    print(f"[ok  ] {out.name} saved and md5-verified")


if __name__ == "__main__":
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    for item in FILES:
        download(item)
