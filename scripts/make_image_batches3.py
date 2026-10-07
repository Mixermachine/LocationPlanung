# -*- coding: utf-8 -*-
"""Welle 3: Batches fuer die bildlosen Locations (39) + kreuzberghof-Check."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
man = json.loads((ROOT / ".research" / "images_manifest.json").read_text(encoding="utf-8"))
master = json.loads((ROOT / ".research" / "candidates_master.json").read_text(encoding="utf-8"))
cands = master if isinstance(master, list) else master["candidates"]
idx = {c["id"]: c for c in cands}

zero = json.loads((ROOT / ".research" / "wave3_zero_ids.json").read_text(encoding="utf-8"))
zero = [z for z in zero if len((man.get(z) or {}).get("ranked") or []) == 0]

batches = []
per = 10
for i in range(0, len(zero), per):
    chunk = zero[i:i + per]
    items = []
    for z in chunk:
        c = idx[z]
        items.append({
            "id": z,
            "name": c.get("name"),
            "town": c.get("town"),
            "site": c.get("site"),
            "lat": c.get("lat"), "lon": c.get("lon"),
            "n_existing": 0,
            "existing": [],
            "prior_note": (man.get(z) or {}).get("note") or "",
        })
    batches.append(items)

todo = {"batches": batches, "target": 7, "kb": 300}
(ROOT / ".research" / "image_todo3.json").write_text(json.dumps(todo, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"wave3: {len(batches)} Batches, {len(zero)} Locations | kreuzberghof-Check separat")
