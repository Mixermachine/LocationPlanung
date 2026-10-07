# -*- coding: utf-8 -*-
"""HP-Check aller ranked-URLs im Manifest: tote URLs (404/410/5xx/timeout) entfernen.
file-Eintraege (lokal) und Placeholders uebersprungen. Resume via verify_state.json optional.
"""
import json, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MP = ROOT / ".research" / "images_manifest.json"

man = json.loads(MP.read_text(encoding="utf-8"))

def check(url):
    try:
        r = subprocess.run(["curl", "-s", "-o", "NUL", "-m", "12", "-L", "-A", "Mozilla/5.0",
                            "-w", "%{http_code}|%{content_type}", url],
                           capture_output=True, text=True, timeout=25)
        code, ctype = (r.stdout + "|").split("|")[:2]
        ok = code in ("200", "301", "302", "303")
        return ok, f"{code} {ctype[:20]}"
    except Exception as e:
        return False, "timeout"

dead = {}
tasks = []
for cid, e in man.items():
    for idx, r in enumerate(e.get("ranked") or []):
        u = r.get("url") or ""
        if u and not u.startswith(("web.archive", "http")):
            continue
        if u.startswith("web.archive"):
            tasks.append((cid, idx, u))
        elif u:
            tasks.append((cid, idx, u))

# serialize local deads dictionary for concurrent curl via python
print("zu pruefen:", len(tasks))
for n, (cid, idx, u) in enumerate(tasks, 1):
    ok, info = check(u)
    if not ok:
        dead.setdefault(cid, []).append((idx, u, info))
    if n % 200 == 0:
        print(f"  {n}/{len(tasks)} | tot bisher: {sum(len(v) for v in dead.values())}")

removed = 0
for cid, lst in dead.items():
    e = man.get(cid) or {}
    ranked = e.get("ranked") or []
    bad_idx = {i for i, _, _ in lst}
    e["ranked"] = [r for i, r in enumerate(ranked) if i not in bad_idx]
    dead_notes = "; ".join(u[:60] for i, u, _ in lst)
    e["note"] = ((e.get("note") or "") + f" | URL-Check 2026-10-06: {len(lst)} tote URL(s) entfernt ({dead_notes})").strip(" |")
    if e["ranked"] and "file" not in e:
        e["url"] = e["ranked"][0]["url"]
        e["source_url"] = e["ranked"][0]["url"]
    elif not e["ranked"]:
        e.pop("url", None)
        e.pop("source_url", None)
    man[cid] = e
    removed += len(lst)

MP.write_text(json.dumps(man, ensure_ascii=False, indent=1), encoding="utf-8")
with_img = sum(1 for v in man.values() if v.get("file") or v.get("url"))
print(f"entfernt: {removed} tote URLs | manifest: {len(man)} entries, {with_img} mit Bild")
