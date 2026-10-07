"""Apply cluster-wave adds (batch0..7 minus missing batch4) to master + dist + ledger.

Rules (user GO 2026-10-06):
  kap>=150 & dance=yes      -> gruen
  kap>=150 (ohne dance)     -> gelb
  kap<150                   -> rot (bleibt dokumentiert)
  kap null                  -> gelb + open "Kapazitaet anfragen"
  30.5 < fahr_km <= 35.5    -> stretch=true
  fahr_km > 35.5            -> rot + stretch note
In-cluster dedupe (Bonfeld-Doppel etc.), kein Silent-Removal.
"""
import json, re, unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
M = ROOT / ".research" / "candidates_master.json"
A = ROOT / ".research" / "cluster_adds.json"
D = ROOT / ".research" / "cluster_adds_dist.json"
DIST = ROOT / ".research" / "candidates_dist.json"
LEDGER = ROOT / ".research" / "cluster_progress.json"
FD = ROOT / ".research" / "cluster_findings"

def norm(s):
    s = unicodedata.normalize("NFKD", (s or "").lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"(?u)[^a-z0-9]+", "", s)

master = json.loads(M.read_text(encoding="utf-8"))
adds = json.loads(A.read_text(encoding="utf-8"))
dists = {c["id"]: c for c in json.loads(D.read_text(encoding="utf-8"))}

existing = {norm(c["name"] + "|" + (c.get("town") or "")) for c in master}
# in-adds dedupe: same key appearing twice (Bonfeld) -> keep first (higher kap wins)
seen = {}
unique = []
for o in adds:
    k = norm(o["name"] + "|" + (o.get("town") or ""))
    if k in seen:
        old = seen[k]
        if (o.get("kap") or 0) > (old.get("kap") or 0):
            unique[unique.index(old)] = o
            seen[k] = o
        print("dedupe in-adds:", o["name"])
        continue
    seen[k] = o
    unique.append(o)

n_add = n_skip = 0
for o in unique:
    k = norm(o["name"] + "|" + (o.get("town") or ""))
    if k in existing:
        n_skip += 1
        continue
    km = o.get("fahr_km")
    status, stretch, open_ = "gelb", False, []
    if o.get("kap") is None:
        open_.append("Kapazitaet anfragen (Beleg fehlt)")
    elif o["kap"] < 150:
        status = "rot"
    if km is not None and 30.5 < km <= 35.5:
        stretch = True
    elif km is not None and km > 35.5:
        status = "rot"
        open_.append("ausserhalb 35km - nur dokumentiert")
    if o.get("dance") == "yes" and status == "gelb" and o.get("kap") is not None:
        status = "gruen"
    quellen = [o.get("evidence") or o.get("site") or "cluster-wave batch" + str(o.get("batch"))]
    c = {
        "id": o["id"], "name": o["name"], "town": o.get("town") or "", "lat": o.get("lat"),
        "lon": o.get("lon"), "kap": o.get("kap"),
        "kap_note": (o.get("kap_note") or "") + (f" [batch{o.get('batch')}, conf {o.get('confidence')}]"),
        "dance": o.get("dance") or "unknown", "dance_note": o.get("kap_note") or "",
        "rustic": o.get("rustic") or "unknown", "catering": o.get("catering") or "unknown",
        "price": "", "site": o.get("site") or "", "quellen": quellen,
        "status": status, "stretch": stretch, "open": open_,
        "note": "Cluster-Welle batch" + str(o.get("batch")),
    }
    master.append(c)
    existing.add(k)
    n_add += 1

# dist merge: dist file = full candidate dicts incl. old ones
dmap = {c["id"]: c for c in json.loads(DIST.read_text(encoding="utf-8"))} if DIST.exists() else {}
out_dist = []
for c in master:
    base = dists.get(c["id"]) or dmap.get(c["id"]) or {}
    merged = dict(base)
    merged.update({k: c[k] for k in c if c[k] is not None or k not in merged})
    for k in ("luft_km", "fahr_km", "fahr_min"):
        if k not in merged:
            merged[k] = None
    out_dist.append(merged)
DIST.write_text(json.dumps(out_dist, ensure_ascii=False, indent=1), encoding="utf-8")
M.write_text(json.dumps(master, ensure_ascii=False, indent=1), encoding="utf-8")

# ledger: tick all __CLUSTER_DONE__ labels across batches
led = json.loads(LEDGER.read_text(encoding="utf-8"))
ticked = 0
for i in range(8):
    p = FD / f"batch{i}.json"
    if not p.exists():
        continue
    for o in json.loads(p.read_text(encoding="utf-8")):
        if o.get("name") == "__CLUSTER_DONE__":
            lab = o.get("cluster_label")
            if lab and lab not in led:
                led[lab] = {"done": True, "query": f"cluster-wave batch{i} (cluster-researcher/deepseek)"}
                ticked += 1
LEDGER.write_text(json.dumps(led, ensure_ascii=False, indent=1), encoding="utf-8")

print(f"master: {len(master)} (+{n_add}, skip_dupe {n_skip}) | dist: {len(out_dist)} | ledger ticked: {ticked}")
