"""Add 7 Brackenheim municipal venues (from eval_brackenheim, stadtseite belegt)."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / ".research" / "candidates_master.json"
cands = json.loads(P.read_text(encoding="utf-8"))
idx = {c["id"]: c for c in cands}

NEW = [
 {"id":"gemeindehaus-kelter-haberschlacht","name":"Bürgerhaus Kelter Haberschlacht","town":"Brackenheim OT Haberschlacht","lat":49.0868,"lon":9.1695,"kap":250,"kap_note":"250 Plaetze laut Stadtseite; echte Kelter als Buergerhaus","dance":"unknown","rustic":"high","catering":"free","price":"Entgeltordnung Stadt Brackenheim (guenstig)","site":"https://www.brackenheim.de/leben-wohnen/turn-sportanlagen/turn-und-versammlungshallen","quellen":["brackenheim.de 2026-10-06"],"status":"gruen","stretch":False,"open":["Tanz moeglich? Bankett-Bestuhlung 150+ bestaetigen","Vermietung Buergerbuero Brackenheim"]},
 {"id":"kelter-meimsheim","name":"Kelter Meimsheim","town":"Brackenheim OT Meimsheim","lat":49.0795,"lon":9.0826,"kap":None,"kap_note":"Stadtseite nennt Kelter Meimsheim ohne Kap; nachfragen","dance":"unknown","rustic":"high","catering":"free","price":"Entgeltordnung Stadt","site":"https://www.brackenheim.de/leben-wohnen/turn-sportanlagen/turn-und-versammlungshallen","quellen":["brackenheim.de 2026-10-06"],"status":"gelb","stretch":False,"open":["Kapazitaet Buergerbuero erfragen"]},
 {"id":"gemeindehalle-neipperg","name":"Gemeindehalle Neipperg","town":"Brackenheim OT Neipperg","lat":49.1064,"lon":9.1654,"kap":207,"kap_note":"207 Plaetze laut Stadtseite","dance":"unknown","rustic":"low","catering":"free","price":"Entgeltordnung Stadt","site":"https://www.brackenheim.de/leben-wohnen/turn-sportanlagen/turn-und-versammlungshallen","quellen":["brackenheim.de 2026-10-06"],"status":"gelb","stretch":False,"open":["Tanzflaeche/Bankett bestaetigen"]},
 {"id":"gemeindehalle-stockheim","name":"Gemeindehalle Stockheim","town":"Brackenheim OT Stockheim","lat":49.0694,"lon":9.0447,"kap":246,"kap_note":"246 Plaetze laut Stadtseite","dance":"unknown","rustic":"low","catering":"free","price":"Entgeltordnung Stadt","site":"https://www.brackenheim.de/leben-wohnen/turn-sportanlagen/turn-und-versammlungshallen","quellen":["brackenheim.de 2026-10-06"],"status":"gelb","stretch":False,"open":["Tanzflaeche/Bankett bestaetigen"]},
 {"id":"gemeindehalle-doerrenzimmern","name":"Gemeindehalle Dürrenzimmern","town":"Brackenheim OT Dürrenzimmern","lat":49.1163,"lon":9.0734,"kap":300,"kap_note":"300 Plaetze laut Stadtseite","dance":"unknown","rustic":"low","catering":"free","price":"Entgeltordnung Stadt","site":"https://www.brackenheim.de/leben-wohnen/turn-sportanlagen/turn-und-versammlungshallen","quellen":["brackenheim.de 2026-10-06"],"status":"gelb","stretch":False,"open":["Tanzflaeche/Bankett bestaetigen"]},
 {"id":"gemeindehalle-hausen-zaber","name":"Gemeindehalle Hausen a.d. Zaber","town":"Brackenheim OT Hausen","lat":49.0888,"lon":9.0287,"kap":None,"kap_note":"Kap Stadtseite nicht ausgewiesen; Buergerbuero fragen","dance":"unknown","rustic":"low","catering":"free","price":"Entgeltordnung Stadt","site":"https://www.brackenheim.de/leben-wohnen/turn-sportanlagen/turn-und-versammlungshallen","quellen":["brackenheim.de 2026-10-06"],"status":"gelb","stretch":False,"open":["Kapazitaet erfragen"]},
 {"id":"gemeindehalle-botenheim","name":"Gemeindehalle Botenheim","town":"Brackenheim OT Botenheim","lat":49.0903,"lon":9.0905,"kap":None,"kap_note":"Kap Stadtseite nicht ausgewiesen","dance":"unknown","rustic":"low","catering":"free","price":"Entgeltordnung Stadt","site":"https://www.brackenheim.de/leben-wohnen/turn-sportanlagen/turn-und-versammlungshallen","quellen":["brackenheim.de 2026-10-06"],"status":"gelb","stretch":False,"open":["Kapazitaet erfragen"]},
]
n = 0
for c in NEW:
    if c["id"] not in idx:
        cands.append(c); n += 1
P.write_text(json.dumps(cands, ensure_ascii=False, indent=1), encoding="utf-8")
print("added", n, "| master:", len(cands))
