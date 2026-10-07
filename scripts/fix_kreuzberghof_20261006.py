# -*- coding: utf-8 -*-
"""kreuzberghof-Koordinatenkorrektur (belegt: Site + Nominatim, 2026-10-06)."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIX = {
    "lat": 49.1793720,
    "lon": 8.8124910,
    "town": "Oestringen-Tiefenbach (76684)",
    "note_add": "Koordinaten 2026-10-06 korrigiert: Am Kreuzbergsee 1, 76684 Oestringen-Tiefenbach (Site-Beleg + Nominatim); Luftlinie 24.19 km",
}

for name in ("candidates_master.json", "candidates_dist.json"):
    p = ROOT / ".research" / name
    d = json.loads(p.read_text(encoding="utf-8"))
    cands = d if isinstance(d, list) else d.get("candidates", d)
    for c in cands:
        if c.get("id") == "kreuzberghof":
            c["lat"] = FIX["lat"]
            c["lon"] = FIX["lon"]
            if "Oestringen-Tiefenbach" not in (c.get("town") or ""):
                c["town"] = FIX["town"]
            n = c.get("note") or ""
            if "Nominatim" not in n:
                c["note"] = (n + " | " + FIX["note_add"]).strip(" |")
    p.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
print("kreuzberghof fix angewendet (master+dist)")
