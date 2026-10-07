"""Generate workflows/image_wave2.js with one run per batch of image_todo2.json."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
batches = json.loads((ROOT / ".research" / "image_todo2.json").read_text(encoding="utf-8"))

spec = """const spec = (i) => [
 'DU BIST Bild-Beauftragter fuer Hochzeitslocations (WELLE 2, Ziel: bis zu 7 gute Bilder pro Location).',
 'Lies .research/image_todo2.json und bearbeite AUSSCHLIESSLICH Batch-Index ' + i + ' (Element [' + i + '], ~6 Objekte {id,name,town,site,n_existing,existing,prior_note}).',
 'Rule 1 TIMEDISZIPLIN: pro Location MAX 6 NEUE Bildkandidaten laden+einlesen, curl mit -m 15, HTML-Response > 300KB nur noch per Regex og:image/img direkt abbrechen. Wenn Batchmaan Zeit knapp wird, priorisiere Locations mit den wengsten Bildern.',
 'Rule 2 SKIPLISTE: URLs aus "existing" NICHT erneut anhaegen. Nur neue, versierte URLs.',
 'Quellen (in dieser Reihenfolge): (a) site-Galerie/Unterseiten: probiere site + /galerie /fotos /hochzeit /feiern(typeof URL, wenn base vorhanden); (b) Wikimedia Commons API mit thumb.wikimedia.org-Thumbnail-Server (upload.wikimedia.org ist rate-limit 429): https://commons.wikimedia.org/w/api.php?action=query&generator=search&gsrsearch=<name OR town>&gsrlimit=8&prop=imageinfo&iiprop=url|size&iiurlwidth=1200&format=json; (c) Openverse: https://api.openverse.org/v1/images/?q=<name+town>&license_type=all&page_size=8; (d) Wayback Machine http://archive.org/wayback/available?url=<site> wenn die Site tot/403 ist.',
 'Bildeinlesen + Bewertung (PFLICHT, jeweilig): read auf .research/tmp/<id>_<n>.jpg; Gut = zeigt Gebaeude/Saal/Fassade/Aussengelaende; Verworfen = Logo, Team, Speisekarte, OSM-Karte, Ortsansicht ohne Gebaeudebezug, Screenshot-Artefakt, Personenportraet, kleiner als 200px.',
 'Objektiv: pro Location bis zu 7 GESAMT-Guettebilder. Wenn n_existing >= 7: Location komplett ueberspringen (nur {id, images: [], note: "already complete"}). Wenn prior_note sagt "kein Bild moeglich": ein Versuch mit Openverse/Wayback, sonst note uebernehmen.',
 'OUTPUT .research/image_wave2/batch' + i + '.json als JSON-array: {id, images: [{url, rank, verdict, reason}], note}. Fuer Location ohne neuen Fund: {id, images: [], note: "grund"}.',
 'ANTWORT am Ende exakt eine Zeile: batch' + i + ' done, <n> locations, <m> new images'
].join('\\n')

const kids = [
"""
lines = []
for i in range(len(batches)):
    lines.append(f"  {{key: 'w2_{i:02d}', agent: 'delegate', model: 'opencode-go/deepseek-v4.1-flash', context: 'fresh', task: spec({i})}},")
tail = """]
const results = await runs.all(kids)
for (const r of results) emit(String(r && (r.summary || r.result || r.status || 'ok')).slice(0, 160))
"""
js = spec + "\n" + "\n".join(lines) + "\n" + tail
(ROOT / "workflows" / "image_wave2.js").write_text(js, encoding="utf-8")
print(f"workflows/image_wave2.js: {len(batches)} children")
