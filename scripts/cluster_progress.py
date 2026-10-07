"""Cluster progress ledger — Regel 1. Seeded with clusters processed in discovery rounds.

Usage:
  python scripts/cluster_progress.py --report
  python scripts/cluster_progress.py --done "<label>" --query "<search queries used>"
"""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / ".research" / "cluster_progress.json"

SEED_DONE = {
    "Brackenheim, Nordheim, Leingarten, Flein": "wave1 batch A (photos+keywords+city pages)",
    "Besigheim, Freifeld a. Weinsberg, Hohenstetten, Bönnigheim": "wave1 batch B",
    "Mundelsheim, Hessigheim, Gemmrigheim, Kleinsachsenheim": "wave1 batch B2",
    "Ilsfeld, Auenstein, Schwaigern, Gueglingen": "wave1 batch B3",
    "Lauffen a.N., Neipperg, Schwaigern, Massenbach": "wave1 batch B4",
    "Sachsenheim, Oßweil, Waldhausensche Hofwiesen": "wave1 + stadt-sachsenheim page",
    "Bietigheim-Bissingen, Bissingen a. Enz, Enzweihingen": "wave1 batch C",
    "Heilbronn, Böckingen, Klingenberg, Sontheim": "wave1 batch D + portals",
    "Ludwigsburg, Stuttgart-Nord/Rand": "wave1 batch E (partly, portals only)",
    "Vaihingen an der Enz, Horrheim": "wave2 - found Steinbachhof; Horrheim Kelter via user intake",
    "Neckarwestheim, Gaimersheim, Lauffen": "wave2",
    "Oberstenfeld, Kleinochsenfeld, Erbstetten, Pleidelsheim, Steinheim, Winzerhausen": "wave2",
    "Möckmühl, Zaberfeld, Güglingen": "wave2 partial (guglingen-kelter)",
    "Löchgau, Walheim": "wave2 partial",
}


def load():
    if STATE.exists():
        return json.loads(STATE.read_text(encoding="utf-8"))
    return {}


def save(d):
    STATE.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--init", action="store_true")
    ap.add_argument("--done")
    ap.add_argument("--query")
    a = ap.parse_args()
    clusters = json.loads((ROOT / ".research" / "clusters.json").read_text(encoding="utf-8"))
    labels = [c["query_label"] if isinstance(c, dict) else c for c in clusters]
    prog = load()
    if a.init:
        for k, q in SEED_DONE.items():
            for lab in labels:
                if lab == k or any(part in lab for part in k.split(", ")[:1]):
                    prog[lab] = {"done": True, "query": q}
        save(prog)
        a.report = True
    if a.done:
        prog[a.done] = {"done": True, "query": a.query or ""}
        save(prog)
        a.report = True
    if a.report:
        openl = [l for l in labels if not prog.get(l, {}).get("done")]
        print(f"clusters offen: {len(openl)} / {len(labels)}")
        for l in openl[:50]:
            print(" -", l)


if __name__ == "__main__":
    main()
