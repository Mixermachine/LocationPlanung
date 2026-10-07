"""Build cluster batches: all not-yet-done clusters -> 8 batches, JSON for researcher children."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
clusters = json.loads((ROOT / ".research" / "clusters.json").read_text(encoding="utf-8"))
prog = json.loads((ROOT / ".research" / "cluster_progress.json").read_text(encoding="utf-8")) if (ROOT / ".research" / "cluster_progress.json").exists() else {}

openl = [c for c in clusters if not prog.get(c["query_label"], {}).get("done")]
print("open clusters:", len(openl))

NB = 8
batches = [[] for _ in range(NB)]
for i, c in enumerate(openl):
    batches[i % NB].append({"label": c["query_label"], "members": c["members"][:4], "lat": c["lat"], "lon": c["lon"]})

(ROOT / ".research" / "clusters_todo.json").write_text(json.dumps(batches, ensure_ascii=False, indent=1), encoding="utf-8")
for i, b in enumerate(batches):
    print(f"batch {i}: {len(b)} clusters")
