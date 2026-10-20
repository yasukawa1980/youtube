"""Download Met Open Access catalog data and verified public-domain images only."""
import json
import time
import hashlib
import urllib.request
from pathlib import Path
import os

ROOT = Path(os.environ['WOM_EPISODE_ROOT']).expanduser().resolve()
IDS = [544075, 590939, 557830, 548344, 557657, 544206, 547871, 552247, 570223, 545547]

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "WorldsOfMysteryResearch/1.0"})
    with urllib.request.urlopen(req, timeout=60) as response:
        return response.read(32_000_000)

records = []
for oid in IDS:
    p = ROOT / "records" / f"met_{oid}.json"
    try:
        if p.exists():
            data = json.loads(p.read_text())
        else:
            data = json.loads(fetch(f"https://collectionapi.metmuseum.org/public/collection/v1/objects/{oid}"))
            p.write_text(json.dumps(data, ensure_ascii=False, indent=2))
        if not data.get("isPublicDomain"):
            raise ValueError("Catalog isPublicDomain is not true")
        url = data.get("primaryImage") or data.get("primaryImageSmall")
        if not url:
            raise ValueError("No official image URL")
        image = ROOT / "assets" / "museum" / f"met_{oid}.jpg"
        if not image.exists():
            image.write_bytes(fetch(url))
        records.append({
            "asset_id": f"MET-{oid}", "file": str(image.relative_to(ROOT)),
            "object_id": oid, "title": data["title"],
            "object_number": data["accessionNumber"], "object_date": data["objectDate"],
            "medium": data["medium"], "credit_line": data["creditLine"],
            "url": data["objectURL"], "download_url": url,
            "is_public_domain": True, "license": "Met Open Access / CC0",
            "license_url": "https://www.metmuseum.org/hubs/open-access",
            "downloaded_at_jst": "2026-10-15",
            "sha256": hashlib.sha256(image.read_bytes()).hexdigest()
        })
        print(oid, data["title"], image.stat().st_size, flush=True)
    except Exception as e:
        print("FAILED", oid, type(e).__name__, str(e), flush=True)
    time.sleep(0.35)
(ROOT / "records" / "museum_assets.json").write_text(json.dumps(records, ensure_ascii=False, indent=2))
print("Downloaded", len(records), "of", len(IDS), flush=True)
