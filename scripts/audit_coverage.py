"""Coverage audit: every harvested/mentioned venue name must be either in the
master (done), or appear as OPEN in .research/coverage_report.md.

Matching: normalized-name token overlap + difflib ratio.
Sources: .research/harvest/*.json, intakes.txt, longlist.md.
"""
import json
import re
from difflib import SequenceMatcher
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

NOISE = re.compile(r"^(zur|mehr|alle|start|vergleich|impressum|kontakt|blog|hochzeits|location$|seite)", re.I)


def norm(s: str) -> str:
    s = s.lower().replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")
    return re.sub(r"[^a-z0-9 ]", " ", s).strip()


def tokens(s):
    return {t for t in norm(s).split() if len(t) > 2 and t not in ("der", "die", "das", "und", "mit", "von", "bei", "dem", "den")}


def master_index():
    cands = json.loads((ROOT / ".research" / "candidates_master.json").read_text(encoding="utf-8"))
    return [(c, tokens(c["name"]) | tokens(c.get("town", ""))) for c in cands]


def match(name, idx):
    tn = tokens(name)
    if not tn:
        return None
    best, bestscore = None, 0.0
    for c, ct in idx:
        inter = len(tn & ct)
        ratio = SequenceMatcher(None, norm(name), norm(c["name"])).ratio()
        score = inter / max(1, min(len(tn), len(ct))) * 0.7 + ratio * 0.3
        if score > bestscore:
            bestscore, best = score, c
    return (best, round(bestscore, 2)) if bestscore >= 0.45 else None


def main():
    idx = master_index()
    names = {}
    for f in (ROOT / ".research" / "harvest").glob("*.json"):
        for r in json.loads(f.read_text(encoding="utf-8")):
            n = r["name"].strip()
            if len(n) < 4 or NOISE.match(n):
                continue
            names.setdefault(n, set()).add(f.stem)
    for line in (ROOT / "intakes.txt").read_text(encoding="utf-8").splitlines():
        if line.startswith("#") or line.strip().count("|") < 2:
            continue
        names.setdefault(line.split("|")[0].strip(), set()).add("intake")
    rejected = set()
    rj = ROOT / ".research" / "coverage_rejected.txt"
    if rj.exists():
        for l in rj.read_text(encoding="utf-8").splitlines():
            if l and not l.startswith("#"):
                rejected.add(norm(l.split("|")[0]))

    done, offen, verworfen = [], [], []
    RUSTIC = re.compile(r"kelter|scheune|scheuer|zehnt|m[üu]hle|muehle|hof|gut|stall|speicher|tenne|dresch|tagung|gasthof|landhaus", re.I)
    REGION = re.compile(r"heilbronn|ludwigsburg|eppingen|brackenheim", re.I)
    for n, srcs in sorted(names.items()):
        if len(n) < 4 or norm(n) in rejected:
            verworfen.append((n, srcs)); continue
        m = match(n, idx)
        if m:
            done.append((n, m[0]["name"], m[1], sorted(srcs)))
        else:
            offen.append((n, sorted(srcs)))

    rustig = [(n, s) for n, s in offen if RUSTIC.search(n) and any(REGION.search(x) for x in s)]
    # machine-readable export for triage (with best href from harvest)
    hrefs = {}
    for f in (ROOT / ".research" / "harvest").glob("*.json"):
        for r in json.loads(f.read_text(encoding="utf-8")):
            hrefs.setdefault(r["name"].strip(), r.get("href", ""))
    (ROOT / ".research" / "offen_rustikal.json").write_text(json.dumps(
        [{"name": n, "srcs": s, "href": hrefs.get(n, "")} for n, s in rustig], ensure_ascii=False, indent=1), encoding="utf-8")

    rep = ["# Coverage-Report — Soll (alle jemals gefundenen Namen) vs. Ist (Master)",
           "",
           f"Gefundene Namen gesamt: {len(names)} | **erledigt:** {len(done)} | **offen: {len(offen)}** (davon rustikal+Region: {len(rustig)}). Verworfen-Logik: .research/coverage_rejected.txt",
           "",
           "## ⭐ OFFEN-RUSTIKAL (zuerst abzuarbeiten: Scheune/Kelter/Mühle/Hof in unseren Portal-Quellen)",
           ""]
    rep += [f"- {n}  ·  {', '.join(s)}" for n, s in rustig]
    rep += ["", "## OFFEN (Rest)", ""]
    for n, srcs in offen:
        if (n, srcs) in rustig:
            continue
        rep.append(f"- {n}  ·  Quellen: {', '.join(srcs)}")
    rep += ["", "## ERLEDIGT (Zuordnung)", ""]
    for n, mn, sc, srcs in done:
        rep.append(f"- {n} → {mn} ({sc})")
    (ROOT / ".research" / "coverage_report.md").write_text("\n".join(rep) + "\n", encoding="utf-8")
    print(f"namen={len(names)} erledigt={len(done)} offen={len(offen)} davon_rustikal={len(rustig)}")
    print("report: .research/coverage_report.md")


if __name__ == "__main__":
    main()
