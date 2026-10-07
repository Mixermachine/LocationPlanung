"""Add Brackenheim municipal halls found via city page (2026-10-06)."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / ".research" / "candidates_master.json"
cands = json.loads(P.read_text(encoding="utf-8"))
idx = {c["id"]: c for c in cands}

# lat/lon = Orts-Koordinaten (Stadtteil), +0.002 for OT if known
NEW = [
 ("kelter-meimsheim", "Kelter Meimsheim", "Brackenheim OT Meimsheim", 49.0836, 9.0836,
  {"kap": None, "kap_note": "Buergerhaus-Klasse; Kapazitaet auf Stadtteilseite + Rathaus erfragen", "rustic": "high"}),
 ("gemeindehalle-doerrenzimmern", "Gemeindehalle Doerrenzimmern", "Brackenheim OT Doerrenzimmern", 49.1189, 9.0739,
  {"kap": 300, "kap_note": "300 (Stadtseite), Vermietung Stadt Brackenheim", "rustic": "low"}),
 ("kelter-haberschlacht", "Buergerhaus 'Kelter' Haberschlacht", "Brackenheim OT Haberschlacht", 49.0850, 9.1800,
  {"kap": 250, "kap_note": "250 (Stadtseite) - buergerhaus in echter Kelter!", "rustic": "high"}),
 ("gemeindehalle-stockheim", "Gemeindehalle Stockheim", "Brackenheim OT Stockheim", 49.0700, 9.0300,
  {"kap": 246, "kap_note": "246 (Stadtseite)", "rustic": "low"}),
 ("gemeindehalle-neipperg", "Gemeindehalle Neipperg", "Brackenheim OT Neipperg", 49.1089, 9.1689,
  {"kap": 207, "kap_note": "207 (Stadtseite)", "rustic": "low"}),
 ("gemeindehalle-hausen", "Gemeindehalle Hausen a.d. Zaber", "Brackenheim OT Hausen", 49.0861, 9.0278,
  {"kap": None, "kap_note": "Kapazitaet Stadtseite pruefen/anfragen", "rustic": "low"}),
 ("gemeindehalle-botenheim", "Gemeindehalle Botenheim", "Brackenheim OT Botenheim", 49.0933, 9.0833,
  {"kap": None, "kap_note": "Kapazitaet anfragen", "rustic": "low"}),
]
n = 0
for nid, name, town, lat, lon, extra in NEW:
    if nid in idx: continue
    c = {"id": nid, "name": name, "town": town, "lat": lat, "lon": lon, "dance": "unknown",
         "catering": "free", "price": "Entgeltordnung Stadt Brackenheim (guenstig fuer Einheimische)",
         "site": "https://www.brackenheim.de/leben-wohnen/turn-sportanlagen/turn-und-versammlungshallen",
         "quellen": ["brackenheim.de 2026-10-06 (Staedte-Harvest)"], "status": "gelb", "stretch": False,
         "open": ["Tanzflaeche+Bankett-Kap beim Buergerbuero erfragen"], "note": "Stadt Brackenheim - eigene Schatzliste"}
    c.update(extra); cands.append(c); n += 1
    print("add:", nid, "kap", c.get("kap"))
P.write_text(json.dumps(cands, ensure_ascii=False, indent=1), encoding="utf-8")
print("master:", len(cands), "(+" + str(n) + ")")
