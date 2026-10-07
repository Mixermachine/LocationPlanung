"""Fix geocode-Fails: Oberstenfeld Gronau + Schloss Liebenstein mit OSM-Naeherungswerten."""
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
P = ROOT / ".research" / "candidates_master.json"
cands = json.loads(P.read_text(encoding="utf-8"))
idx = {c["id"]: c for c in cands}
add = [
 {"id":"alte-kelter-oberstenfeld","name":"Alte Kelter Oberstenfeld (Gronau)","town":"Oberstenfeld OT Gronau","lat":48.9659,"lon":9.2916,"kap":None,"kap_note":"Rathausplatz 3 Gronau, Gemeindelisten-Hall; Kap anfragen","dance":"unknown","rustic":"high","catering":"free","price":"Entgeltordnung Gemeinde","site":"https://www.oberstenfeld.de/Gemeindeleben/Freizeit-Kultur/Hallen-und-Veranstaltungsraeume","quellen":["oberstenfeld.de 2026-10-06"],"status":"gelb","stretch":False,"open":["Kapazitaet Gemeinde anfragen"]},
 {"id":"schloss-liebenstein","name":"Schloss Liebenstein","town":"Neckarwestheim","lat":48.9590,"lon":9.2280,"kap":None,"kap_note":"Schloss ueber Event Inc; nur kleine Raeume gelistet (62qm 'Kurfuerst I'), Grossraum unklar; Catering im Haus","dance":"unknown","rustic":"medium","catering":"house","price":"unbekannt","site":"https://www.eventinc.de/eventlocation/heilbronn/schloss-liebenstein","quellen":["eventinc.de 2026-10-06"],"status":"gelb","stretch":False,"open":["Grossraum-Kap bei Event Inc erfragen"]},
]
n=0
for c in add:
    if c["id"] not in idx: cands.append(c); n+=1
P.write_text(json.dumps(cands, ensure_ascii=False, indent=1), encoding="utf-8")
print("added", n, "total", len(cands))
# Sachsenheim 404 aus Quellenliste werfen
sp = ROOT / ".research" / "staedte_sources.json"
src = [s for s in json.loads(sp.read_text(encoding="utf-8")) if s["town"] != "Sachsenheim"]
sp.write_text(json.dumps(src, ensure_ascii=False, indent=1), encoding="utf-8")
print("sources:", len(src))
