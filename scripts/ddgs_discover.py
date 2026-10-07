# -*- coding: utf-8 -*-
"""Stage-A Bild-Discovery via ddgs (DuckDuckGo Images) fuer alle Locations mit <7 Bildern.

Schreibt .research/ddgs_pool.json: {id: [{url, page, w, h, query, ok(200,image,bytes)}]}
- 1-2 Queries pro Location (Name+Ort, Varianten), 4-5s Sleep (ratelimit-sicher)
- Resume-faehig: Locations mit Eintraegen (auch ohne ok) werden uebersprungen
- HTTP-Validierung per curl (image content-type, >10KB)
"""
import json, subprocess, sys, time, urllib.parse
from pathlib import Path
from ddgs import DDGS

ROOT = Path(__file__).resolve().parents[1]
MAN = ROOT / ".research" / "images_manifest.json"
MASTER = ROOT / ".research" / "candidates_master.json"
POOL = ROOT / ".research" / "ddgs_pool.json"
CAP = 7
SLEEP = 4.0

man = json.loads(MAN.read_text(encoding="utf-8"))
master = json.loads(MASTER.read_text(encoding="utf-8"))
cands = master if isinstance(master, list) else master.get("candidates", master)

pool = {}
if POOL.exists():
    pool = json.loads(POOL.read_text(encoding="utf-8"))

def need(cid):
    e = man.get(cid) or {}
    return len(e.get("ranked") or []) < CAP

todo = []
for c in cands:
    if not need(c["id"]) or c["id"] in pool:
        continue
    name = (c.get("name") or "").replace("(OSM)", "").strip()
    town = (c.get("town") or "").split("(")[0].strip()
    queries = [f"{name} {town}"] if name and town else [name or town]
    if c["id"].startswith("cw-"):
        clean = c.get("name") or ""
        clean = clean.replace(" (OSM)", "").replace("(OSM)", "").strip()
        queries = [f"{clean} Festhalle" if "halle" in clean.lower() else clean]
    todo.append((c["id"], queries))

print(f"zu verarbeiten: {len(todo)} Locations", flush=True)
UA = "Mozilla/5.0"

def validate(url):
    try:
        r = subprocess.run(["curl", "-s", "-o", "NUL", "-m", "20", "-L", "-A", UA,
                            "-w", "%{http_code}|%{content_type}|%{size_download}", url],
                           capture_output=True, text=True, timeout=30)
        code, ctype, size = (r.stdout + "|||").split("|")[:3]
        ok = code == "200" and ctype.startswith("image") and int(size or 0) > 10000
        return {"ok": bool(ok), "bytes": int(size or 0), "ctype": ctype[:20]}
    except Exception:
        return {"ok": False, "bytes": 0, "ctype": "err"}

queries_total = 0
for n, (cid, queries) in enumerate(todo, 1):
    items = []
    for q in queries:
        try:
            with DDGS() as d:
                res = list(d.images(q, max_results=8))
        except Exception as e:
            print(f"  {n}. {cid} Q-ERR {type(e).__name__} {str(e)[:80]}", flush=True)
            time.sleep(20)
            try:
                with DDGS() as d:
                    res = list(d.images(q, max_results=8))
            except Exception as e2:
                print(f"  {n}. {cid} Q-ERR2 {str(e2)[:60]}", flush=True)
                res = []
        queries_total += 1
        seen = set()
        for x in res:
            u = x.get("image") or ""
            if not u or u in seen:
                continue
            seen.add(u)
            items.append({"url": u, "page": x.get("title"), "w": x.get("width"), "h": x.get("height"),
                          "query": q, "v": None})
        time.sleep(SLEEP)
    # nur beste 6 validieren (2 queries x 8 -> max 12 unique, nehme top 6 gemischt)
    best = items[:6]
    for it in best:
        v = validate(it["url"])
        it["v"] = v
    pool[cid] = best
    if n % 10 == 0 or n == len(todo):
        POOL.write_text(json.dumps(pool, ensure_ascii=False, indent=1), encoding="utf-8")
        n_ok = sum(1 for c in pool.values() for i in c if i.get("v", {}).get("ok"))
        print(f"  {n}/{len(todo)} | gueltige Kandidaten bisher: {n_ok}", flush=True)

POOL.write_text(json.dumps(pool, ensure_ascii=False, indent=1), encoding="utf-8")
n_ok = sum(1 for c in pool.values() for i in c if i.get("v", {}).get("ok"))
n_loc = sum(1 for c in pool.values() if any(i.get("v", {}).get("ok") for i in c))
print(f"FERTIG: {len(pool)} Locations im Pool, {n_ok} gueltige Kandidaten, {n_loc} Locations mit >=1 gueltigem Kandidaten")
