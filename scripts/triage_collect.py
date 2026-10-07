"""Apply triage results: reject -> coverage_rejected.txt (begründet), add -> master (gelb/rot, Kap unvalidiert)."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
offen = json.loads((ROOT / ".research" / "offen_rustikal.json").read_text(encoding="utf-8"))
rej_path = ROOT / ".research" / "coverage_rejected.txt"
existing_rej = rej_path.read_text(encoding="utf-8").splitlines() if rej_path.exists() else []

adds, rejects = [], []
for n in (0, 1, 2):
    f = ROOT / ".research" / "triage" / f"out_part{n}.json"
    if not f.exists():
        print("SKIP missing", f.name); continue
    for r in json.loads(f.read_text(encoding="utf-8")):
        src = offen[r["idx"]] if r["idx"] < len(offen) else {}
        r["_href"] = src.get("href", "")
        (adds if r.get("decision") == "add" else rejects).append(r)

print(f"add={len(adds)} reject={len(rejects)}")

with rej_path.open("a", encoding="utf-8") as f:
    for r in rejects:
        f.write(f"{r['name']} | {r.get('town') or '?'} | {r.get('reason','').strip()}\n")

for r in adds:
    print(" ADD:", r["name"], "|", r.get("town"), "| kap", r.get("kap"))
(ROOT / ".research" / "triage_adds.json").write_text(json.dumps(adds, ensure_ascii=False, indent=1), encoding="utf-8")
print("rejects angehängt an coverage_rejected.txt; adds vorgemerkt -> triage_apply.py")
