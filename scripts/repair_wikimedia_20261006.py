# -*- coding: utf-8 -*-
"""Reparatur nach URL-Check: wikimedia-URLs, die wegen 429 als 'tot' entfernt wurden,
aus den Wave-Batch-Quelldateien zurueckholen — konvertiert auf Special:FilePath-Thumb
(keyless, umgeht upload.wikimedia.org-Ratelimits) und curl-verifiziert.
"""
import json, subprocess, urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MP = ROOT / ".research" / "images_manifest.json"
CP = 7

man = json.loads(MP.read_text(encoding="utf-8"))

DIRS = [(".research/image_wave", 0, "all"),
        (".research/image_wave2", 10, "all"),
        (".research/image_wave3", 20, "all"),
        (".research/image_wave4", 30, "ja")]


def collect():
    out = {}
    for base, off, filt in DIRS:
        files = sorted((ROOT / base).glob("batch*.json"))
        for p in files:
            for e in json.loads(p.read_text(encoding="utf-8")):
                cid = e.get("id")
                for im in e.get("images", []):
                    if filt == "ja" and im.get("verdict") != "ja":
                        continue
                    if im.get("url"):
                        rk = im.get("rank") if isinstance(im.get("rank"), int) else 1
                        out.setdefault(cid, []).append((off + rk, im["url"],
                                                        (im.get("reason") or "")[:120]))
    return out


def to_thumb(url):
    if "upload.wikimedia.org/wikipedia/commons" not in url:
        return None
    name = url.rsplit("/", 1)[-1]
    return "https://commons.wikimedia.org/wiki/Special:FilePath/" + urllib.parse.quote(name) + "?width=1200"


def check(url):
    try:
        r = subprocess.run(["curl", "-s", "-o", "NUL", "-m", "20", "-L", "-A", "Mozilla/5.0",
                            "-w", "%{http_code}|%{content_type}|%{size_download}", url],
                           capture_output=True, text=True, timeout=35)
        code, ctype, size = (r.stdout + "||").split("|")[:3]
        return code == "200" and ctype.startswith("image") and int(size or 0) > 8000
    except Exception:
        return False


allsrc = collect()
added = 0
for cid, e in man.items():
    ranked = e.get("ranked") or []
    current = {r.get("url") for r in ranked} | {e.get("url")}
    for rank, url, reason in allsrc.get(cid, []):
        if url in current:
            continue
        t = to_thumb(url)
        if not t:
            continue  # nur wikimedia reparieren
        if not check(t):
            continue
        ranked.append({"url": t, "rank": 90 + len(ranked), "verdict": "ja",
                       "reason": (reason or "")[:120] + " [thumb-2chance]"})
        ranked.sort(key=lambda x: x.get("rank") if isinstance(x.get("rank"), int) else 99)
        e["ranked"] = ranked[:CP]
        current.add(t)
        added += 1

MP.write_text(json.dumps(man, ensure_ascii=False, indent=1), encoding="utf-8")
with_img = sum(1 for v in man.values() if v.get("file") or v.get("url"))
print(f"wiederhergestellt: {added} wikimedia-URLs via thumb | {with_img}/{len(man)} mit Bild")
