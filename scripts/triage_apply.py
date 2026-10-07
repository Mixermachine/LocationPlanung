"""Add triage-approved venues to master. Run after triage_collect.py."""
import json, time, urllib.parse, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / ".research" / "candidates_master.json"
UA = "hochzeit-location-search/0.1 (private research, single user)"

def geocode(q):
    url = "https://nominatim.openstreetmap.org/search?format=json&limit=1&q=" + urllib.parse.quote(q)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=25) as r:
            d = json.loads(r.read())
        time.sleep(1.1)
        if d: return float(d[0]["lat"]), float(d[0]["lon"])
    except Exception:
        pass
    return None

def slug(name):
    keep = "".join(ch if ch.isalnum() else "-" for ch in name.lower().replace("ä","ae").replace("ö","oe").replace("ü","ue").replace("ß","ss"))
    return "-".join(t for t in keep.split("-") if t and not t.isnumeric())[:40]

adds = json.loads((ROOT / ".research" / "triage_adds.json").read_text(encoding="utf-8"))
cands = json.loads(P.read_text(encoding="utf-8"))
idx = {c["id"]: c for c in cands}
n = 0
for r in adds:
    sid = slug(r["name"])
    if sid in idx or any(c["name"].lower().strip() == r["name"].lower().strip() for c in cands):
        print("dup, skip:", r["name"]); continue
    co = geocode(f'{r.get("town") or r["name"]}') or geocode(r["name"])
    if not co:
        print("NO GEO:", r["name"], "| stays OFFEN for manual intake"); continue
    kap = r.get("kap")
    status = "rot" if (kap and kap < 150) else "gelb"
    c = {"id": sid, "name": r["name"], "town": r.get("town") or "?", "lat": co[0], "lon": co[1],
         "kap": kap, "kap_note": (r.get("reason") or "")[:180],
         "dance": r.get("dance") if r.get("dance") in ("yes","no","unknown") else "unknown",
         "rustic": r.get("rustic") if r.get("rustic") in ("high","medium","low") else "medium",
         "catering": r.get("catering") if r.get("catering") in ("house","external","free","unknown") else "unknown",
         "price": "unbekannt", "site": r.get("site") or None,
         "quellen": ["triage " + (r.get("_href") or "offenliste")], "status": status,
         "stretch": False, "open": ["Triage-Uebernahme: Kapazita/Tanz direkt verifizieren"], "note": "AUTO-TRIAGE"}
    cands.append(c); n += 1
    print("add:", sid, "| kap", kap, "|", status)
P.write_text(json.dumps(cands, ensure_ascii=False, indent=1), encoding="utf-8")
print("master:", len(cands), "(+" + str(n) + ")")
