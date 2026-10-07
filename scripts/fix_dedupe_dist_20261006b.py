# -*- coding: utf-8 -*-
"""Korrektur nach dedupe_20261006b: le-moulin wiederherstellen + dist an master-angleichen."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / ".research" / "candidates_master.json"
DIST = ROOT / ".research" / "candidates_dist.json"
KEEP = {"mein-forsthof": "forsthof-hotel-restaurant", "schloss-neuhaus": "cw-schlo-neuhaus-sinsheim"}

master = json.loads(MASTER.read_text(encoding="utf-8"))
mcands = master if isinstance(master, list) else master["candidates"]
dist = json.loads(DIST.read_text(encoding="utf-8"))
dcands = dist if isinstance(dist, list) else dist["candidates"]

# 1) le-moulin aus dist wieder in master aufnehmen (fehlte komplett)
have_lm = any(c.get("id") == "le-moulin-alte-muehle-sinsheim" for c in mcands)
restored = 0
if not have_lm:
    lm = next((c for c in dcands if c.get("id") == "le-moulin-alte-muehle-sinsheim"), None)
    if lm:
        lm = dict(lm)
        lm["note"] = (lm.get("note") or "") + " | dedupe 20261006b: Doppel-Eintrag bereinigt"
        mcands.append(lm)
        restored = 1

# 2) dist: Merges anwenden (fuer alle Paare)
merged = []
for keep, drop in KEEP.items():
    kd = next((c for c in dcands if c.get("id") == keep), None)
    dd = next((c for c in dcands if c.get("id") == drop), None)
    if kd and dd:
        for k in ("dance", "dance_note", "kap_note"):
            if (not kd.get(k) or kd.get(k) in ("unbekannt", "unknown")) and dd.get(k):
                kd[k] = dd[k]
        if len(dd.get("kap_note") or "") > len(kd.get("kap_note") or ""):
            kd["kap_note"] = dd["kap_note"]
        qs = list(kd.get("quellen") or [])
        qs += [q for q in (dd.get("quellen") or []) if q not in qs]
        kd["quellen"] = qs
        merged.append(drop)
dcands = [c for c in dcands if c.get("id") not in merged]

# 3) le-moulin war evtl. doppelt in dist (bereits in dedupe-Skript entfernt) - sanity
ids = [c.get("id") for c in dcands]
assert len(ids) == len(set(ids)), f"dist hat noch doppelte ids: {[i for i in ids if ids.count(i) > 1]}"

MASTER.write_text(json.dumps(mcands if isinstance(master, list) else {**master, "candidates": mcands},
                             ensure_ascii=False, indent=1), encoding="utf-8")
DIST.write_text(json.dumps(dcands if isinstance(dist, list) else {**dist, "candidates": dcands},
                           ensure_ascii=False, indent=1), encoding="utf-8")
print("master:", len(mcands), "| dist:", len(dcands), "| le-moulin restored:", restored, "| dist-merges:", merged)
