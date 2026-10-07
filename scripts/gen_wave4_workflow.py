# -*- coding: utf-8 -*-
"""Stage-B: .research/image_todo4.json + workflows/image_wave4.js generieren.

Kinder bekommen vorgefischte ddgs-Kandidaten (HTTP-geprueft) via image_todo4.json
und machen NUR: downloaden -> read (visuell) -> verdict -> image_wave4/batch<i>.json.
Limits: max 2 Reads/Location, max 12 Reads/Kind, 6 Locations/Kind.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
pool = json.loads((ROOT / ".research" / "ddgs_pool.json").read_text(encoding="utf-8"))

items = []
for cid, cands in pool.items():
    good = [c for c in cands if (c.get("v") or {}).get("ok")]
    if good:
        items.append({"id": cid, "cands": good[:4]})

per = 6
batches = [items[i:i + per] for i in range(0, len(items), per)]
(ROOT / ".research" / "image_todo4.json").write_text(
    json.dumps(batches, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"Locations mit gueltigen Kandidaten: {len(items)} -> {len(batches)} Batches")

spec = """const spec = (i) => [
 'DU BIST Bild-Gutachter (WELLE 4, ddgs-Pool-Verifikation).',
 'Lies .research/image_todo4.json und bearbeite AUSSCHLIESSLICH Batch-Index ' + i + ' (Element [' + i + '], ~6 Objekte {id, cands:[{url, page, w, h}]}) — Kandidaten sind vorgefischt und HTTP-geprueft.',
 'HARTES LIMIT: MAX 2 Bild-Reads PRO Location, MAX 12 gesamt (Endpoint erlaubt max 20 Bilder/Anfrage).',
 'Vorgehen pro Location (fuer bis zu 2 Kandidaten): (1) curl -s -m 20 -L -A Mozilla/5.0 -o .research/tmp/w4/<id>_<n>.jpg "<url>"; (2) pruefe Datei > 8KB und Bildformat; (3) READ die Datei und BEWerte visuell: GUT = zeigt Gebaeude/Saal/Fassade/Aussengelaende; SCHLECHT = Logo, Speisen, Personenportrait, Ortsansicht ohne Gebaeudebezug, anderes Motiv/Fremdlogo (GENAU hinschauen!), Screenshots, <400px.',
 'Ehrlichkeit: verdict "ja" nur, wenn das Bild plausibel DIESE Location zeigt. Zweifelhaft -> verdict "vielleicht" + Begruendung. Beide schlecht -> images: [] + note.',
 'OUTPUT .research/image_wave4/batch' + i + '.json als JSON-Array: [{id, images: [{url, rank, verdict, reason}], note}].',
 'mkdir -p .research/image_wave4 .research/tmp/w4 bei Bedarf zuerst. ANTWORT am Ende exakt eine Zeile: batch' + i + ' done, <n> locations, <m> new images'
].join('\\n')
"""

lines = [f"  {{key: 'w4_{i:02d}', agent: 'delegate', model: 'opencode-go/deepseek-v4.1-flash', context: 'fresh', task: spec({i})}}," for i in range(len(batches))]
tail = """
]
const results = await runs.all(kids)
for (const r of results) emit(String(r && (r.output || r.summary || r.result || r.status || 'ok')).slice(0, 160))
"""
js = spec + "\nconst kids = [\n" + "\n".join(lines) + tail
(ROOT / "workflows" / "image_wave4.js").write_text(js, encoding="utf-8")
print("workflows/image_wave4.js geschrieben")
