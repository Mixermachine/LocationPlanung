"""Merge wave1 + wave2 image batches into images_manifest.json (up to 7 images/location).

Wave1 (.research/image_wave/batch0..11.json)  = base, keeps its ranks 1..N
Wave2 (.research/image_wave2/batch0..40.json) = top-up, appended (rank offset +10)
Dedup by URL against existing ranked list and existing file-based image.
Top image (rank 1 of final list) becomes entry.url (hotlink fallback for card).
Empty wave2 entries only fill notes for locations that have no manifest entry yet.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MP = ROOT / ".research" / "images_manifest.json"
W1 = ROOT / ".research" / "image_wave"
W2 = ROOT / ".research" / "image_wave2"
CAP = 7

man = json.loads(MP.read_text(encoding="utf-8"))

def ranked_of(batch_dir, idx):
    p = batch_dir / f"batch{idx}.json"
    if not p.exists():
        return None
    out = []
    for e in json.loads(p.read_text(encoding="utf-8")):
        cid = e.get("id")
        if not cid:
            continue
        out.append((cid, e))
    return out

n_updates = n_append = 0
skipped = []
# --- wave2 first: collect per-location additions (wave1 already in manifest) ---
additions = {}
notes = {}
for i in range(41):
    got = ranked_of(W2, i)
    if got is None:
        skipped.append(i)
        continue
    for cid, e in got:
        imgs = [im for im in e.get("images", []) if im.get("url")]
        imgs.sort(key=lambda x: x.get("rank") if isinstance(x.get("rank"), int) else 99)
        additions.setdefault(cid, []).extend(imgs)
        if e.get("note"):
            notes.setdefault(cid, e["note"])

for cid, imgs in additions.items():
    entry = man.get(cid) or {}
    existing_urls = set()
    ranked = entry.get("ranked", [])
    for r in ranked:
        existing_urls.add(r.get("url"))
    if entry.get("url"):
        existing_urls.add(entry["url"])
    new_items = []
    for pos, im in enumerate(imgs, 1):
        if im["url"] in existing_urls:
            continue
        existing_urls.add(im["url"])
        new_items.append({"url": im["url"], "rank": 10 + pos,
                          "verdict": im.get("verdict"), "reason": (im.get("reason") or "")[:140]})
    if new_items:
        ranked = ranked + new_items
        ranked.sort(key=lambda x: x.get("rank", 99))
        entry["ranked"] = ranked[:CAP]
        if "file" not in entry:
            entry["url"] = entry["ranked"][0]["url"]
            entry["source_url"] = entry["ranked"][0]["url"]
        man[cid] = entry
        n_append += len(new_items)
        n_updates += 1
    elif cid not in man and notes.get(cid):
        man[cid] = {"note": notes[cid]}

MP.write_text(json.dumps(man, ensure_ascii=False, indent=1), encoding="utf-8")
with_img = sum(1 for v in man.values() if v.get("file") or v.get("url"))
full = sum(1 for v in man.values() if len(v.get("ranked", [])) >= CAP or (v.get("file") and not v.get("ranked")))
print(f"manifest: {len(man)} entries, {with_img} mit Bild, {full} mit {CAP}+ | +{n_append} Bilder auf {n_updates} Locations | wave2-Batches fehlend: {skipped or 'keine'}")
