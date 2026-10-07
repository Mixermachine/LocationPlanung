"""Fetch one representative image (og:image / twitter:image) per candidate website.

Saves images/<id>.<ext> under repo root and writes .research/images_manifest.json
with {id: {file, source_url, page_url}}. Placeholder if nothing found.
"""
import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / ".research" / "candidates_dist.json"
IMG = ROOT / "images"
MANIFEST = ROOT / ".research" / "images_manifest.json"
UA = "Mozilla/5.0 (compatible; hochzeit-location-research/1.0; private use)"

OG_RE = re.compile(
    r"<meta[^>]+property=[\"']og:image[\"'][^>]+content=[\"']([^\"']+)[\"']"
    r"|<meta[^>]+content=[\"']([^\"']+)[\"'][^>]+property=[\"']og:image[\"']",
    re.I,
)


def fetch(url, timeout=20):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read(), r.geturl()


def get_og(html: str, base: str):
    m = OG_RE.search(html)
    if not m:
        return None
    u = m.group(1) or m.group(2)
    return urllib.parse.urljoin(base, u)


def main():
    IMG.mkdir(exist_ok=True)
    cands = json.loads(DATA.read_text(encoding="utf-8"))
    manifest = {}
    for c in cands:
        cid, site = c["id"], c.get("site")
        if not site:
            continue
        try:
            html_bytes, final_url = fetch(site)
            html = html_bytes.decode("utf-8", "ignore")
            img = get_og(html, final_url)
            if not img:
                m = re.search(r'(https?://[^"\']+\.(?:jpe?g|png|webp))', html, re.I)
                img = m.group(1) if m else None
            if not img:
                print("no image:", cid)
                continue
            ib, _ = fetch(img)
            if len(ib) < 8000:
                print("tiny/skip:", cid, len(ib))
                continue
            ext = img.rsplit(".", 1)[-1].split("?")[0].lower()
            ext = {"jpg": "jpg", "jpeg": "jpg", "png": "png", "webp": "webp"}.get(ext, "jpg")
            dest = IMG / f"{cid}.{ext}"
            dest.write_bytes(ib)
            manifest[cid] = {"file": f"images/{dest.name}", "source_url": img, "page_url": site}
            print(f"ok {cid}: {len(ib)//1024}KB")
        except Exception as e:
            print(f"fail {cid}: {e!r}"[:100])
        time.sleep(1)
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")
    print("manifest:", len(manifest), "images")


if __name__ == "__main__":
    main()
