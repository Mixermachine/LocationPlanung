"""Wave-2 worklist: ALL candidates, per-venue existing image URLs (skip-list), batches of 6."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
man = json.loads((ROOT / ".research" / "images_manifest.json").read_text(encoding="utf-8"))
cands = json.loads((ROOT / ".research" / "candidates_dist.json").read_text(encoding="utf-8"))
todo = []
for c in cands:
    e = man.get(c["id"]) or {}
    existing = sorted({im["url"] for im in e.get("ranked", []) if im.get("url")} | {e.get("url") or e.get("source_url") or ""} - {""})
    todo.append({
        "id": c["id"], "name": c["name"], "town": c["town"], "site": c.get("site") or "",
        "n_existing": len(existing), "existing": existing[:7],
        "prior_note": e.get("note") or ""
    })

SZ = 6
batches = [todo[i:i+SZ] for i in range(0, len(todo), SZ)]
(ROOT / ".research" / "image_todo2.json").write_text(json.dumps(batches, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"{len(todo)} locations -> {len(batches)} Batches:", [len(b) for b in batches])
