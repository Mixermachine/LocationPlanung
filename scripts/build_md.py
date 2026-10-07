"""Regenerate longlist.md from candidates_dist.json + manifest (data mirror)."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / ".research" / "candidates_dist.json").read_text(encoding="utf-8"))
MAN = json.loads((ROOT / ".research" / "images_manifest.json").read_text(encoding="utf-8")) if (ROOT / ".research" / "images_manifest.json").exists() else {}

STATUS = {"gruen": "GRÜN", "gelb": "GELB", "rot": "ROT"}
DANCE = {"confirmed": "✓", "probable": "~", "unknown": "?"}
RUST = {"high": "hoch", "mid": "mittel", "low": "niedrig"}

lines = ["# Longlist Hochzeitslocations — Daten-Spiegel zu locations.html",
         "",
         f"Stand: 2026-10-06 · {len(DATA)} Kandidaten · {len(MAN)} Bilder in `images/` · Fahrten via OSRM ab Brackenheim.",
         "GRÜN = Kernkriterien (150+ mit Tanz) belegt · GELB = Rückfrage offen · ROT = verletzter Filter (mit Grund). `⤢` = Radius-Reißer.",
         "",
         "| Status | Location | Ort | Fahrt km/min | Kapazität | Tanz | Rustikal | Catering | Preis | Bild | Offene Fragen / Quelle |",
         "|---|---|---|---|---|---|---|---|---|---|---|"]
rows = sorted(DATA, key=lambda c: (-(c["status"] == "gruen"), c.get("fahr_km") or 999))
for c in rows:
    img = "✓" if c["id"] in MAN else "—"
    openq = "; ".join(c.get("open") or []) or "—"
    src = c.get("site") or (c.get("quellen") or ["—"])[0]
    stretch = " ⤢" if c.get("stretch") else ""
    lines.append(f"| {STATUS[c['status']]} | **{c['name']}**{stretch} | {c['town']} | {c.get('fahr_km','?')} / {c.get('fahr_min','?')} | {c.get('kap') or '?'} ({c.get('kap_note','')}) | {DANCE.get(c['dance'],'?')} | {RUST.get(c['rustic'],'?')} | {c.get('catering') or '?'} | {c.get('price') or '—'} | {img} | {openq} · [{src}]({src}) |")
(ROOT / "longlist.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
print("longlist.md:", len(rows), "Zeilen")
