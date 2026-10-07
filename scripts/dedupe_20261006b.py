# -*- coding: utf-8 -*-
"""Dedupe-Sweep 2026-10-06b: echte Doppel-Eintraege aus candidates_master entfernen.

1. le-moulin-alte-muehle-sinsheim  (id doppelt, gleiche Koords/Site)  -> 1 Eintrag
2. forsthof-hotel-restaurant + mein-forsthof (gleiche Venue, mein-forsthof.de) -> mein-forsthof
3. schloss-neuhaus + cw-schlo-neuhaus-sinsheim (gleiche Venue, schlossneuhaus.com) -> schloss-neuhaus

Regeln: reichere Felder behalten, quellen/kap_note vereinigen, Bilder (ranked) aus
beiden Manifest-Eintraegen dedupiziert vereinen (Cap 7). Keine Datenfabrikation.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / ".research" / "candidates_master.json"
DIST = ROOT / ".research" / "candidates_dist.json"
MAN = ROOT / ".research" / "images_manifest.json"
CAP = 7

man = json.loads(MAN.read_text(encoding="utf-8"))

# le-moulin: gleiche id 2x in master -> erstes behalten, reichere kap_note des
# zweiten uebernehmen, zweites entfernen
def fix_lm_master(cands):
    idxs = [i for i, c in enumerate(cands) if c.get("id") == "le-moulin-alte-muehle-sinsheim"]
    if len(idxs) < 2:
        return 0
    first, second = cands[idxs[0]], cands[idxs[1]]
    if len(second.get("kap_note") or "") > len(first.get("kap_note") or ""):
        first["kap_note"] = second["kap_note"]
    qs = list(first.get("quellen") or [])
    qs += [q for q in (second.get("quellen") or []) if q not in qs]
    first["quellen"] = qs
    return 1

MERGES = [
    # (keep_id, drop_id)
    ("mein-forsthof", "forsthof-hotel-restaurant"),
    ("schloss-neuhaus", "cw-schlo-neuhaus-sinsheim"),
]

def merge_candidates(cands, keep, drop):
    a = next(c for c in cands if c.get("id") == keep)
    b = next(c for c in cands if c.get("id") == drop)
    for k in ("dance", "dance_note", "kap_note", "note"):
        if (not a.get(k) or a.get(k) in ("unbekannt", "unknown")) and b.get(k):
            a[k] = b[k]
    # laengere kap_note gewinnt (mehr Beleg)
    if len(b.get("kap_note") or "") > len(a.get("kap_note") or ""):
        a["kap_note"] = b["kap_note"]
    qs = list(a.get("quellen") or [])
    qs += [q for q in (b.get("quellen") or []) if q not in qs]
    a["quellen"] = qs
    extras = {k: b[k] for k in b.keys() - a.keys() if k not in ("id",)}
    if extras:
        a.setdefault("note_dup", {})["merged_from"] = drop
        for k, v in extras.items():
            a["note_dup"].setdefault(k, v)
    return a

def merge_manifest(keep, drop):
    ka, kb = man.get(keep) or {}, man.get(drop) or {}
    if not kb:
        return 0
    ranked = list(ka.get("ranked") or [])
    seen = {r.get("url") for r in ranked} | {ka.get("url")} | {kb.get("url")}
    add = 0
    for r in (kb.get("ranked") or []):
        if r.get("url") and r["url"] not in seen:
            seen.add(r["url"])
            ranked.append(r)
            add += 1
    if ranked:
        ranked.sort(key=lambda x: x.get("rank") if isinstance(x.get("rank"), int) else 99)
        ka["ranked"] = ranked[:CAP]
        if "file" not in ka:
            ka["url"] = ka["ranked"][0]["url"]
            ka["source_url"] = ka["ranked"][0]["url"]
    elif "file" not in ka and "file" in kb:
        ka["file"] = kb["file"]
    if kb.get("file") and "file" not in ka:
        ka["file"] = kb["file"]
    note = (ka.get("note") or "")
    if kb.get("note"):
        ka["note"] = (note + " | " + kb["note"]).strip(" |")
    man[keep] = ka
    man.pop(drop, None)
    return add

master = json.loads(MASTER.read_text(encoding="utf-8"))
mcands = master if isinstance(master, list) else master.get("candidates", master)
lm_fixed = fix_lm_master(mcands)
mcands = [c for i, c in enumerate(mcands) if not (c.get("id") == "le-moulin-alte-muehle-sinsheim" and i > 0 and lm_fixed)]
removed = []
for keep, drop in MERGES:
    if not any(c.get("id") == drop for c in mcands):
        continue
    merge_candidates(mcands, keep, drop)
    mcands = [c for c in mcands if c.get("id") != drop]
    removed.append((keep, drop, merge_manifest(keep, drop)))

if isinstance(master, list):
    out = mcands
else:
    master["candidates"] = mcands
    out = master
MASTER.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")

# le-moulin exakte Doppel (gleiche id, zweiter Eintrag verworfen; reichere kap_note behalten)
dist = json.loads(DIST.read_text(encoding="utf-8"))
dcands = dist if isinstance(dist, list) else dist.get("candidates", dist)
seen_lm = 0
kept = []
drop_dist = 0
for c in dcands:
    if c.get("id") == "le-moulin-alte-muehle-sinsheim":
        seen_lm += 1
        if seen_lm > 1:
            drop_dist += 1
            continue
    kept.append(c)
if drop_dist:
    if isinstance(dist, list):
        djson = kept
    else:
        dist["candidates"] = kept
        djson = dist
    DIST.write_text(json.dumps(djson, ensure_ascii=False, indent=1), encoding="utf-8")

MAN.write_text(json.dumps(man, ensure_ascii=False, indent=1), encoding="utf-8")
print("master:", len(mcands), "| dist:", len(kept), "| merges:", [f"{k}<-{d}(+{n} img)" for k, d, n in removed], "| le-moulin-master-fixed:", lm_fixed, "| dist-doppelt entfernt:", drop_dist)
