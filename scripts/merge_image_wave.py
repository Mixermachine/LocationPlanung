"""Merge image_wave batch results into images_manifest.json (URL mode).

Manifest v2: {id: {file|url, source_url, page_url, verdict, ranked:[{url,rank,verdict,reason}]}}
Existing downloaded-image entries keep file; new entries get url (hotlink) + ranked list.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MP = ROOT / ".research" / "images_manifest.json"
WF = ROOT / ".research" / "image_wave"

man = json.loads(MP.read_text(encoding="utf-8"))
n_new = n_rank = 0
for i in range(12):
    p = WF / f"batch{i}.json"
    if not p.exists():
        print(f"batch{i}: missing (retry pending?)")
        continue
    for e in json.loads(p.read_text(encoding="utf-8")):
        cid = e.get("id")
        if not cid:
            continue
        imgs = sorted(e.get("images", []), key=lambda x: x.get("rank", 99))
        if not imgs:
            man.setdefault(cid, {"note": e.get("note", "keine Bilder")})
            continue
        ranked = [{"url": im.get("url"), "rank": im.get("rank"), "verdict": im.get("verdict"), "reason": (im.get("reason") or "")[:140]} for im in imgs if im.get("url")]
        entry = man.get(cid) or {}
        if "file" not in entry and ranked:
            entry["url"] = ranked[0]["url"]
            entry["source_url"] = ranked[0]["url"]
        entry["ranked"] = ranked
        man[cid] = entry
        n_new += 1
MP.write_text(json.dumps(man, ensure_ascii=False, indent=1), encoding="utf-8")
with_img = sum(1 for v in man.values() if v.get("file") or v.get("url"))
print(f"manifest: {len(man)} entries, {with_img} mit Bild | updates: {n_new}")
