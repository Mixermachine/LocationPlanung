"""Collect cluster-wave findings (batch0..7, batch4 optional) -> reviewable adds + matched report.

No master mutation here. Output:
  .research/cluster_adds.json   - new candidate findings (not yet in master)
  .research/cluster_matches.txt - findings that match existing master entries (for ledger ticks)
"""
import json, re, unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MP = ROOT / ".research" / "candidates_master.json"
FD = ROOT / ".research" / "cluster_findings"

def norm(s):
    if not s:
        return ""
    s = unicodedata.normalize("NFKD", s.lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r"^(alte|hist|historische|historisch|burg|schloss|gut|hof|kelter|scheune|zehnt|zehntscheuer|gemeindehalle|stadthalle|biurgerhaus|buergerhaus|festhalle|mehrzweckhalle|mzh|eventlocation|eventhalle)\s+", "", s)
    s = re.sub(r"(?u)[^a-z0-9]+", " ", s).strip()
    # drop town suffixes for fuzzy core
    return s

def core(s):
    n = norm(s)
    return n.split()[0] if n else n

master = json.loads(MP.read_text(encoding="utf-8"))
m_norm = {c["id"]: (norm(c["name"]), core(c["name"]), (c.get("town") or "").lower()) for c in master}

adds, matches = [], []
for i in range(8):
    p = FD / f"batch{i}.json"
    if not p.exists():
        print(f"batch{i}: MISSING (expected: batch4)")
        continue
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"batch{i}: BROKEN {e}")
        continue
    b_adds = b_matches = 0
    for o in data:
        name = (o.get("name") or "").strip()
        if not name or name == "__CLUSTER_DONE__":
            continue
        if o.get("note"):
            continue  # keine-Treffer markers
        town = (o.get("town") or "").strip()
        nn, nc = norm(name), core(name)
        hit = None
        for cid, (mn, mc, mtown) in m_norm.items():
            if nn == mn or nc == mc and (town.lower()[:4] == mtown[:4] or nc in mn or mn in nn):
                hit = cid
                break
        if hit:
            matches.append({"batch": i, "cluster": o.get("cluster_label"), "name": name, "master_id": hit,
                            "kap_finding": o.get("kap"), "evidence": (o.get("evidence") or "")[:120]})
            b_matches += 1
        else:
            o["batch"] = i
            o.setdefault("status", None)
            o["id"] = "cw-" + re.sub(r"(?u)[^a-z0-9]+", "-", name.lower()).strip("-")[:40]
            adds.append(o)
            b_adds += 1
    done = sum(1 for o in data if o.get("name") == "__CLUSTER_DONE__")
    print(f"batch{i}: {b_adds} new, {b_matches} matched, {done} clusters done")

(RT := ROOT / ".research" / "cluster_adds.json").write_text(json.dumps(adds, ensure_ascii=False, indent=1), encoding="utf-8")
(ROOT / ".research" / "cluster_matches.txt").write_text(
    "\n".join(f"b{m['batch']} {m['name']} -> {m['master_id']} (kap={m['kap_finding']})" for m in matches), encoding="utf-8")
print(f"\nTOTAL: {len(adds)} neue Kandidaten, {len(matches)} Master-Matches -> .research/cluster_adds.json")
