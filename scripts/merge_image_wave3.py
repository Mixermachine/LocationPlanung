"""Merge wave3 batches (image_wave3/batch0..3.json) into images_manifest.json (Cap 7).

Wie merge_image_wave2.py: dedup gegen existing ranked/url/file, rank-Offset +20
(nach wave2-Offsets), leere Eintraege erweitern nur Notizen bestehender Eintraege.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MP = ROOT / ".research" / "images_manifest.json"
W3 = ROOT / ".research" / "image_wave3"
CAP = 7

man = json.loads(MP.read_text(encoding="utf-8"))
n_append = n_updates = 0
missing = []
for i in range(4):
    p = W3 / f"batch{i}.json"
    if not p.exists():
        missing.append(i)
        continue
    for e in json.loads(p.read_text(encoding="utf-8")):
        cid = e.get("id")
        if not cid:
            continue
        imgs = [im for im in e.get("images", []) if im.get("url")]
        imgs.sort(key=lambda x: x.get("rank") if isinstance(x.get("rank"), int) else 99)
        entry = man.get(cid) or {}
        ranked = entry.get("ranked", [])
        seen = {r.get("url") for r in ranked} | {entry.get("url")}
        new_items = []
        for pos, im in enumerate(imgs, 1):
            if im["url"] in seen:
                continue
            seen.add(im["url"])
            new_items.append({"url": im["url"], "rank": 20 + pos,
                              "verdict": im.get("verdict"), "reason": (im.get("reason") or "")[:140]})
        if new_items:
            ranked = ranked + new_items
            ranked.sort(key=lambda x: x.get("rank") if isinstance(x.get("rank"), int) else 99)
            entry["ranked"] = ranked[:CAP]
            if "file" not in entry:
                entry["url"] = entry["ranked"][0]["url"]
                entry["source_url"] = entry["ranked"][0]["url"]
            man[cid] = entry
            n_append += len(new_items)
            n_updates += 1
        if e.get("note"):
            old = entry.get("note") or ""
            entry["note"] = (old + " | " + e["note"]).strip(" |")
            man[cid] = entry

MP.write_text(json.dumps(man, ensure_ascii=False, indent=1), encoding="utf-8")
with_img = sum(1 for v in man.values() if v.get("file") or v.get("url"))
print(f"manifest: {len(man)} entries, {with_img} mit Bild | wave3 +{n_append} auf {n_updates} Locations | fehlende Batches: {missing or 'keine'}")
