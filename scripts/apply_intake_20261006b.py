"""Intake Welle 3 (2026-10-06): Kelter Horrheim + Schloss Massenbach add, Herzogskelter rename."""
import json
import re
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / ".research" / "candidates_master.json"
UA = "hochzeit-location-search/0.1 (private research, single user)"


def geocode(q):
    url = "https://nominatim.openstreetmap.org/search?format=json&limit=1&q=" + urllib.parse.quote(q)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=25) as r:
        d = json.loads(r.read())
    time.sleep(1.1)
    return (float(d[0]["lat"]), float(d[0]["lon"])) if d else None


import urllib.parse

cands = json.loads(P.read_text(encoding="utf-8"))
idx = {c["id"]: c for c in cands}

co = geocode("Klosterbergstrasse, 71665 Vaihingen an der Enz-Horrheim") or (48.9630, 8.9215)
print("horrheim coords:", co)

NEW = [
 {"id":"alte-kelter-horrheim","name":"Alte Kelter Horrheim","town":"Vaihingen a.d.Enz - Horrheim","lat":co[0],"lon":co[1],"kap":199,"kap_note":"EG max 199 Pers (Stadtseite belegt), OG-Stube 30, Empoere=Buehne; 2020 saniert, Kelterbaum original drin","dance":"unknown","dance_note":"Freitragende Halle 1788 - Tanz moeglich, klaren","rustic":"high","catering":"free","price":" Entgeltordnung Sport-/Mehrzweckhalle Vaihingen (guenstig)","site":"https://www.vaihingen.de/leben-wohnen/staedtische-veranstaltungsraeume/alte-kelter-horrheim","quellen":["vaihingen.de 2026-10-06","User-Intake Welle3"],"status":"gruen","stretch":False,"open":["Tanz/Bestuhlung anfragen","Kontakt: Hausmeister Jens Link 0174 1803742 / Verwaltungsstelle Horrheim"]},
 {"id":"schloss-massenbach","name":"Schloss Massenbach","town":"Schwaigern - Massenbach","lat":49.1663,"lon":9.0595,"kap":130,"kap_note":"Portale: Saal bis 130 Gaeste; barockes Schloss, Standesamt+freie Trauung, Appartements","dance":"unknown","rustic":"medium","catering":"external","price":"unbekannt","site":"https://schloss-massenbach.de/","quellen":["hochzeitsportal24","hochzeits-location.info","User-Intake Welle3"],"status":"rot","stretch":False,"open":["Kapazitaet direkt beim Schloss verifizieren (130 nur Portalwert)","~10km Luft - top Lage, falls Kap reicht"]},
]
for n in NEW:
    if n["id"] not in idx:
        cands.append(n)

g = idx.get("guglingen-kelter")
if g:
    g["name"] = "Herzogskelter Gueglingen"
    g["kap_note"] = "Kelter + Kelterplatz, anna-johannes: 160; historische Herzogskelter"
    g["quellen"].append("User-Intake Welle3 (Namenscheck)")

P.write_text(json.dumps(cands, ensure_ascii=False, indent=1), encoding="utf-8")
print("master:", len(cands))

it = ROOT / "intakes.txt"
add = [
 "Kelter Horrheim | Vaihingen-Horrheim | User-Intake Welle3 | DRIN (199, Stadtseite, gelb->gruen)",
 "Schloss Massenbach | Schwaigern-Massenbach | User-Intake Welle3 | DRIN (rot kap130, Pruefung offen)",
 "Herzogskelter Gueglingen | Gueglingen | User-Intake Welle3 | DRIN (umbenannt, kap160 gelb)",
 "Burg Guttenberg Marstall+Eventscheune | Hassmersheim | User-Intake Welle3 | DRIN (rot, Reisshausen-Strasse ~48km)",
]
existing = it.read_text(encoding="utf-8")
it.write_text(existing + "\n".join(add) + "\n", encoding="utf-8")
print("intakes appended")
