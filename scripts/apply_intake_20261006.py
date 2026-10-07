"""Apply 2026-10-06 user intake: add 4 new candidates, update Fessler + Boennigheim Kelter."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / ".research" / "candidates_master.json"
cands = json.loads(P.read_text(encoding="utf-8"))
idx = {c["id"]: c for c in cands}

NEW = [
 {"id":"wedding-ranch","name":"Wedding RANCH (Scheunen + Blockhaus-Areal)","town":"Pforzheim","lat":48.9042,"lon":8.6483,"kap":200,"kap_note":"2 Scheunen + Blockhaus, 20-200 Pers., Mai-Sep, Trauwiesen, Catering aus einer Hand","dance":"probable","dance_note":"Aussenbereiche/Trauwiesen; Innen-Tanz klären","rustic":"high","catering":"house","price":"unbekannt","site":"https://www.wedding-ranch.de/hochzeit/","quellen":["wedding-ranch.de","User-Intake"],"status":"gelb","stretch":True,"open":["~40km Luft / Fahrzeit beachten (Reißer)","Saison Mai-Sep nur"]},
 {"id":"kelter-langenbeutingen","name":"Alte Kelter Langenbeutingen","town":"Langenbrettach","lat":49.2320,"lon":9.4950,"kap":125,"kap_note":"bis 125 Gaeste, sommers, Vermietung Gemeinde (Locaboo)","dance":"unknown","rustic":"high","catering":"free","price":"Locaboo-Tarif","site":"https://www.langenbrettach.de/freizeit-erlebnis/veranstaltungsstaetten/kelter-langenbeutingen","quellen":["langenbrettach.de","eventcatering24","User-Intake"],"status":"rot","stretch":True,"open":["Kap 125 unter Ziel; ~35km Reißer – nur wenn alles andere nicht passt"]},
 {"id":"kulturwerk-kelter-kleinbottwar","name":"KulturWerk in der Kelter Kleinbottwar","town":"Sachsenheim-Kleinbottwar","lat":48.9540,"lon":9.0380,"kap":None,"kap_note":"historische Kelter, Raumvermietung private Feiern/Hochzeiten; Kap Website prüfen","dance":"unknown","rustic":"high","catering":"free","price":"unbekannt","site":"https://www.kulturwerk-kelter.de/raeume_mieten","quellen":["kulturwerk-kelter.de","Beifund User-Intake"],"status":"gelb","stretch":False,"open":["Kap+Tanz auf Website/anfragen"]},
 {"id":"kelter-cleebronn","name":"Historische Kelter Cleebronn","town":"Cleebronn (5 km!)","lat":49.1213,"lon":9.0352,"kap":None,"kap_note":"nichts öffentlich Vermietbares gefunden (nur Gastronomie Leiterwägele 120+Terrasse 130)","dance":"unknown","rustic":"high","catering":"unknown","price":"unbekannt","site":None,"quellen":["User-Intake","leiterwaegele"],"status":"gelb","stretch":False,"open":["Gemeinde Cleebronn fragen ob Kelter vermietet wird"]},
 {"id":"keltersaal-cannstatt","name":"Keltersaal Bad Cannstatt (Weller)","town":"Stuttgart-Bad Cannstatt","lat":48.8060,"lon":9.2000,"kap":120,"kap_note":"310qm, bis 120 je nach Bestuhlung","dance":"unknown","rustic":"high","catering":"house","price":"Tagespreis 'gutes PLV'","site":"https://weller-dasoriginal.de/locations/keltersaal-bad-cannstatt/","quellen":["weller-dasoriginal.de","Beifund"],"status":"rot","stretch":True,"open":["Kap 120","~30km Luft, Fahrt pruefen"]},
]

for n in NEW:
    if n["id"] not in idx:
        cands.append(n)

# Fessler: Kap jetzt belegt
f = idx.get("fessler-muehle")
if f:
    f["kap"] = 300
    f["kap_note"] = "75-300 (eventlokale, Theater bestuhlt); Betreiber wirbt 10-600; Muehlenanwesen mit Beutelkasten/Wagenschuppen"
    f["rustic"] = "high"
    f["status"] = "gelb"
    f["quellen"].append("eventlokale.de/fessler-muehle.de User-Intake 2026-10-06")
    f["open"] = ["Tanzflaeche auf Gelaende?","Hochzeits-Kombi bei 150+ bestaetigen"]

# Kelter Boennigheim Notiz: Genossenschaftskelter Burgplatz
kb = idx.get("kelter-boennigheim")
if kb:
    kb["kap_note"] = "Genossenschaftskelter Burgplatz 1947, maechtiger Dachstuhl, laut Presse 'gepraegendes Gebaeude ohne Nutzung' – Vermietungsstand im Rathaus kl"
    kb["quellen"].append("bietigheimerzeitung.de (User-Intake-Hinweis Historische Kelter Boennigheim)")

P.write_text(json.dumps(cands, ensure_ascii=False, indent=1), encoding="utf-8")
print("master:", len(cands), "Kandidaten")
