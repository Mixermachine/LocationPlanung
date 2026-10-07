"""Build image worklist: candidates without manifest image, split into batches for subagent wave."""
import json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
man = json.loads((ROOT / ".research" / "images_manifest.json").read_text(encoding="utf-8"))
cands = json.loads((ROOT / ".research" / "candidates_dist.json").read_text(encoding="utf-8"))
missing = [c for c in cands if c["id"] not in man]
todo = [{"id": c["id"], "name": c["name"], "town": c["town"], "site": c.get("site") or "", "quellen": c.get("quellen") or []} for c in missing]

N = 12
batches = [todo[i::N] for i in range(N)]
out = ROOT / ".research" / "image_todo.json"
out.write_text(json.dumps(batches, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"{len(missing)} ohne Bild -> {N} Batches:", [len(b) for b in batches])
