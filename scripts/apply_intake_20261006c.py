"""Intake Welle 3b: Herzogskelter-Upgrade + staedte-erforsste Kommunalsaele in den Master."""
import json, time, urllib.parse, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / ".research" / "candidates_master.json"
UA = "hochzeit-location-search/0.1 (private research, single user)"

def geocode(q):
    url = "https://nominatim.openstreetmap.org/search?format=json&limit=1&q=" + urllib.parse.quote(q)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=25) as r:
            d = json.loads(r.read())
        time.sleep(1.1)
        if d: return float(d[0]["lat"]), float(d[0]["lon"])
    except Exception as e:
        print("geo fail", q, repr(e)[:50])
    return None

cands = json.loads(P.read_text(encoding="utf-8"))
idx = {c["id"]: c for c in cands}

g = idx.get("guglingen-kelter")
if g:
    g["kap"] = 350
    g["kap_note"] = "Saal bis 350 Pers. (cvent-Listing), 59 Betten im Haus; Hotel-Restaurant mit Bewirtung"
    g["catering"] = "house"
    g["site"] = "https://www.herzogskelter.de/"
    g["status"] = "gelb"
    g["open"] = ["Tanzflaeche/Bestuhlung bei Herzogskelter erfragen"]
    g["quellen"].append("cvent.com + herzogskelter.de (Stadtseiten-Runde 2026-10-06)")

NEW = [
 ("alte-kelter-stetten", "Alte Kelter Stetten", "Schwaigern OT Stetten", "Alte Kelter Stetten Schwaigern",
  {"kap": None, "kap_note": "Sommerhalle des Foerdervereins, Gebaeude von 1576 freitragend; Belegung ueber Geschaeftsstelle (Gabi Klein)", "rustic": "high", "catering": "free",
   "site": "https://www.schwaigern.de/freizeiteinrichtungen/alte-kelter-stetten-id_719/", "status": "gelb", "open": ["Kapazitaet+Termine beim Foerderverein erfragen"]}),
 ("klosterhof-lauffen", "Klosterhof Lauffen a.N.", "Lauffen am Neckar", "Klosterhof Lauffen am Neckar",
  {"kap": 180, "kap_note": "bis 180 Besucher (Stadtseite), Buchung ueber Buergerbüro", "rustic": "medium", "catering": "free",
   "site": "https://www.lauffen.de/website/de/freizeit/staedtische-veranstaltungsraeume", "status": "gelb", "open": ["Kernkriterien bei Stadt anfragen"]}),
 ("stadthalle-lauffen", "Stadthalle Lauffen a.N.", "Lauffen am Neckar", "Stadthalle Lauffen am Neckar",
  {"kap": 550, "kap_note": "Grosser Saal bis 550 (Stadtseite), flexible Bestuhlung", "rustic": "low", "catering": "external",
   "site": "https://www.lauffen.de/website/de/freizeit/staedtische-veranstaltungsraeume/stadthalle", "status": "gelb", "open": ["Bestuhlung 150+Bankett+Tanz klären"]}),
 ("gemeindehalle-loechgau", "Gemeindehalle Löchgau", "Löchgau", "Gemeindehalle Loechgau",
  {"kap": 500, "kap_note": "Grosser Saal 500 bei Konzertbestuhlung (Gemeindeseite); Bankett-Kap unbekannt", "rustic": "low", "catering": "external",
   "site": "https://www.loechgau.de/start/Leben/Gemeindehalle.html", "status": "gelb", "open": ["Bankett-Kapazitaet + Tanzflaeche anfragen"]}),
 ("festhalle-leingarten", "Festhalle Leingarten", "Leingarten", "Festhalle Leingarten",
  {"kap": None, "kap_note": "'Gute Stube der Stadt', 1938er Turn-/Festhalle, saniert; Kapazitaet Gemeindeseite prüfen", "rustic": "low", "catering": "external",
   "site": "https://www.leingarten.de/leben-und-wohnen/stadteinrichtungen/festhalle", "status": "gelb", "open": ["Kapazitaet anfragen"]}),
 ("alte-kelter-oberstenfeld", "Alte Kelter Oberstenfeld (Gronau)", "Oberstenfeld", "Alte Kelter Gronau Oberstenfeld",
  {"kap": None, "kap_note": "Rathausplatz 3 Gronau, Teil der Hallen-/Veranstaltungsraum-Liste der Gemeinde", "rustic": "high", "catering": "free",
   "site": "https://www.oberstenfeld.de/Gemeindeleben/Freizeit-Kultur/Hallen-und-Veranstaltungsraeume", "status": "gelb", "open": ["Kapazitaet+Vermietung Gemeinde anfragen"]}),
 ("schloss-liebenstein", "Schloss Liebenstein", "Neckarwestheim", "Schloss Liebenstein Neckarwestheim",
  {"kap": None, "kap_note": "Schloss über Event Inc vermietbar, hauseigenes Catering, Trauung im Park moeglich; Saalkap unklar (nur kleine Raeume gelistet)", "rustic": "medium", "catering": "house",
   "site": "https://www.eventinc.de/eventlocation/heilbronn/schloss-liebenstein", "status": "gelb", "open": ["Grossraum-Kapazitaet bei Event Inc erfragen"]}),
]

for nid, name, town, geoq, extra in NEW:
    if nid in idx: continue
    co = geocode(geoq)
    if not co:
        print("SKIP no geo:", name); continue
    c = {"id": nid, "name": name, "town": town, "lat": co[0], "lon": co[1],
         "dance": "unknown", "price": "staedtische Entgeltordnung" if "halle" in name.lower() else "unbekannt",
         "quellen": ["stadtseite/portal 2026-10-06"], "stretch": False, "note": ""}
    c.update(extra)
    c.setdefault("kap_note", "")
    c.setdefault("open", [])
    cands.append(c)
    print("add", nid)

P.write_text(json.dumps(cands, ensure_ascii=False, indent=1), encoding="utf-8")
print("master:", len(cands))
