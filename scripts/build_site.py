"""Build locations.html from .research/candidates_dist.json + images_manifest.json.

Self-contained page: Leaflet via CDN, embedded data, relative images/.
Re-run after data updates:  python scripts/build_site.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / ".research" / "candidates_dist.json").read_text(encoding="utf-8"))
MANIFEST = json.loads((ROOT / ".research" / "images_manifest.json").read_text(encoding="utf-8")) if (ROOT / ".research" / "images_manifest.json").exists() else {}

TEMPLATE = """<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Hochzeitslocations · 30km um Brackenheim</title>
<link rel="stylesheet" href="assets/leaflet.css">
<style>
:root{--g:#2e7d32;--y:#f9a825;--r:#c62828;--bg:#faf7f2;--card:#fff;--ink:#2b2b2b;--sub:#6d6a64}
*{box-sizing:border-box}
body{margin:0;font-family:system-ui,Segoe UI,Roboto,sans-serif;background:var(--bg);color:var(--ink)}
header{padding:14px 18px;background:#fff;border-bottom:1px solid #e6e1d8}
h1{margin:0 0 4px;font-size:20px}
.sub{color:var(--sub);font-size:13px}
#filters{display:flex;flex-wrap:wrap;gap:8px;padding:10px 18px;background:#fff;border-bottom:1px solid #e6e1d8;align-items:center}
.chip{border:1px solid #cfc9bd;background:#f3efe7;border-radius:16px;padding:5px 12px;font-size:13px;cursor:pointer;user-select:none}
.chip.on{background:#333;color:#fff;border-color:#333}
select,input[type=range]{font-size:13px}
#map{height:330px;width:100%}
#grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:14px;padding:16px 18px}
.card{background:var(--card);border:1px solid #e6e1d8;border-radius:10px;overflow:hidden;cursor:pointer;display:flex;flex-direction:column}
.card img{width:100%;height:160px;object-fit:cover;background:#ddd}
.ph{width:100%;height:160px;display:flex;align-items:center;justify-content:center;background:linear-gradient(135deg,#d7cfc2,#b9ac97);color:#fff;font-size:13px}
.body{padding:10px 12px;display:flex;flex-direction:column;gap:6px;flex:1}
.name{font-weight:700;font-size:15px;line-height:1.2}
.town{color:var(--sub);font-size:12.5px}
.badges{display:flex;flex-wrap:wrap;gap:5px;font-size:11.5px}
.b{padding:2px 8px;border-radius:9px;background:#efece5}
.b.kap{background:#e3f0e3}.b.dance-y{background:#d8ecd8;color:var(--g)}.b.dance-u{background:#f7ecd0;color:#8a6d1b}.b.stretch{background:#e8ddF0;color:#5b2a86}.b.rot{background:#f3d8d8;color:var(--r)}
.stat{width:9px;height:9px;border-radius:50%;display:inline-block}
.sg{background:var(--g)}.sy{background:var(--y)}.sr{background:var(--r)}
.kapline{font-size:13px}
.q{font-size:12px;color:#8a6d1b}
footer{padding:14px 18px;color:var(--sub);font-size:12px}
#modal{position:fixed;inset:0;background:rgba(0,0,0,.55);display:none;align-items:center;justify-content:center;z-index:1000;padding:20px}
#modal.open{display:flex}
.mbox{background:#fff;border-radius:12px;max-width:760px;width:100%;max-height:88vh;overflow:auto}
.mbox img{width:100%;max-height:340px;object-fit:cover;border-radius:12px 12px 0 0}
.mbody{padding:16px 20px}
.gal{display:flex;gap:8px;overflow-x:auto;padding:6px 0}
.gal img{width:72px;height:54px;object-fit:cover;border-radius:4px;cursor:pointer;opacity:.65;border:2px solid transparent}
.gal img.g-on{opacity:1;border-color:#5b2a86}
#galmain{width:100%;max-height:380px;object-fit:contain;background:#111;border-radius:6px;margin-bottom:10px}
.mbody h2{margin:0 0 2px}
.mbody table{border-collapse:collapse;font-size:13.5px;width:100%;margin:10px 0}
.mbody td{padding:4px 8px;border-bottom:1px solid #eee;vertical-align:top}
.mbody td:first-child{color:var(--sub);white-space:nowrap}
.copybtn{margin-top:8px;font-size:12px;padding:6px 10px;border:1px solid #bbb;border-radius:8px;background:#f5f2ec;cursor:pointer}
a{color:#1a5fb4}
.klick{font-size:12px;color:var(--sub)}
</style>
</head>
<body>
<header>
 <h1>💒 Hochzeitslocations — 30 km um 74336 Brackenheim <span style="font-weight:400;font-size:14px;color:#6d6a64">· ~150 Gäste + Tanzfläche · rustikal bevorzugt</span></h1>
 <div class="sub" id="count"></div>
</header>
<div id="filters">
 <span class="chip on" data-f="gruen">● grün: 150+Tanz erfüllt/belegt</span>
 <span class="chip on" data-f="gelb">● gelb: Rückfrage offen</span>
 <span class="chip on" data-f="rot">● rot: Filter verletzt</span>
 <span class="chip" data-f="stretch">Radius-Reißer zeigen</span>
 <span class="chip" data-f="dance">nur Tanzfläche bestätigt</span>
 <span class="chip" data-f="rustic">nur rustikal (hoch)</span>
 <span class="chip" data-f="cap150">nur Kapazität ≥150</span>
 <label>Fahrt max <input id="dist" type="range" min="10" max="80" value="80" step="5"> <span id="distval">80</span> km</label>
 <select id="sort"><option value="score">Sortierung: Eignung</option><option value="dist">Sortierung: Fahrzeit</option><option value="kap">Sortierung: Kapazität</option></select>
</div>
<div id="map"></div>
<div id="grid"></div>
<div id="modal"><div class="mbox" id="mbox"></div></div>
<footer>Bilder: og:image der offiziellen Websites (private Nutzung, Quellen im Detailbild). Datenstand: <span id="stand"></span> · Fehler/Unbekanntes ist markiert — Zahlen ohne Quellenangabe bitte telefonisch verifizieren.</footer>
<script src="assets/leaflet.js"></script>
<script>
const DATA = __DATA__;
const IMG = __IMAGES__;
const ORIGIN = [49.0786, 9.1072];
let filters = new Set(["gruen","gelb","rot"]);
let only = new Set();

function score(c){
 let s = 0;
 if(c.dance==="confirmed") s+=3; else if(c.dance==="probable") s+=2;
 if(c.kap && c.kap>=150) s+=3; else if(c.kap && c.kap>=140) s+=1;
 if(c.rustic==="high") s+=2; else if(c.rustic==="mid") s+=1;
 if(c.status==="gruen") s+=3; if(c.status==="rot") s-=4;
 if(c.stretch) s-=2;
 if(c.fahr_km && c.fahr_km<=30) s+=1;
 return s;
}
function visible(c){
 if(!filters.has(c.status)) return false;
 if(c.stretch && !filters.has("stretch")) return false;
 if(only.has("dance") && c.dance!=="confirmed") return false;
 if(only.has("rustic") && c.rustic!=="high") return false;
 if(only.has("cap150") && !(c.kap && c.kap>=150)) return false;
 const dmax = +document.getElementById("dist").value;
 if(c.fahr_km && c.fahr_km > dmax) return false;
 return true;
}
function esc(s){return String(s??"").replace(/</g,"&lt;")}
function cardHtml(c){
 const img = IMG[c.id];
 const imgSrc = img ? (img.file || img.url) : null;
 const imgTag = imgSrc ? `<img src="${imgSrc}" loading="lazy" alt="${esc(c.name)}">` : `<div class="ph">kein Bild – Website prüfen</div>`;
 const stc = c.status==="gruen"?"sg":c.status==="gelb"?"sy":"sr";
 let badges = `<span class="b kap">👥 ${c.kap? c.kap+" Pers." : "Kap ?"}</span>`;
 badges += c.dance==="confirmed" ? `<span class="b dance-y">Tanz ✓</span>` : c.dance==="probable" ? `<span class="b dance-y">Tanz ~</span>` : `<span class="b dance-u">Tanz ?</span>`;
 if(c.rustic==="high") badges += `<span class="b">🌾 rustikal</span>`;
 if(c.catering==="free") badges += `<span class="b">Catering frei</span>`; else if(c.catering==="house") badges += `<span class="b">Catering Haus</span>`;
 if(c.stretch) badges += `<span class="b stretch">⤢ Reißer ${c.fahr_km}km</span>`;
 if(c.status==="rot") badges += `<span class="b rot">${esc(c.open.join("; ")||"Filter verletzt")}</span>`;
 return `<div class="card" onclick="openDetail('${c.id}')">${imgTag}<div class="body">
 <div class="name"><span class="stat ${stc}"></span> ${esc(c.name)}${c.note?` <span class="klick">(${esc(c.note)})</span>`:""}</div>
 <div class="town">${esc(c.town)} · ${c.fahr_km??"?"} km / ${c.fahr_min??"?"} min Fahrt · Luft ${c.luft_km} km</div>
 <div class="badges">${badges}</div>
 <div class="kapline">${esc(c.kap_note||"")}</div>
 ${c.open && c.open.length?`<div class="q">❓ ${c.open.map(esc).join("<br>❓ ")}</div>`:""}
 </div></div>`;
}
function render(){
 const rows = DATA.filter(visible);
 const sort = document.getElementById("sort").value;
 rows.sort((a,b)=> sort==="dist" ? (a.fahr_min||999)-(b.fahr_min||999) : sort==="kap" ? (b.kap||0)-(a.kap||0) : score(b)-score(a));
 document.getElementById("grid").innerHTML = rows.map(cardHtml).join("");
 document.getElementById("count").textContent = `${rows.length} von ${DATA.length} Locations sichtbar · Gesamtliste bleibt, nichts gelöscht`;
 updateMarkers(rows);
}
document.querySelectorAll("#filters .chip").forEach(ch=>{
 ch.onclick=()=>{
  const f=ch.dataset.f;
  if(["gruen","gelb","rot","stretch"].includes(f)){ filters.has(f)?filters.delete(f):filters.add(f); }
  else { only.has(f)?only.delete(f):only.add(f); }
  ch.classList.toggle("on"); render();
 };
});
document.getElementById("dist").oninput=e=>{document.getElementById("distval").textContent=e.target.value;render()};
document.getElementById("sort").onchange=render;
// initial chip states
document.querySelectorAll(".chip").forEach(ch=>{ch.classList.toggle("on", filters.has(ch.dataset.f)||only.has(ch.dataset.f))});

// map
const map = L.map("map").setView(ORIGIN, 9);
L.tileLayer("https://maps.wikimedia.org/osm-intl/{z}/{x}/{y}.png",{attribution:'&copy; <a href="https://maps.wikimedia.org/">Wikimedia maps</a> | Map data &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',maxZoom:19}).addTo(map);
L.circle(ORIGIN,{radius:30000,color:"#5b2a86",weight:1.5,fillOpacity:0.04}).addTo(map);
L.marker(ORIGIN).addTo(map).bindPopup("<b>Brackenheim (Start)</b>");
let markers=[];
function updateMarkers(rows){
 markers.forEach(m=>map.removeLayer(m)); markers=[];
 const pts = rows.filter(c=>c.lat&&c.lon).map(c=>[c.lat,c.lon]);
 rows.forEach(c=>{
  const col = c.status==="gruen"?"#2e7d32":c.status==="gelb"?"#f9a825":"#c62828";
  const m = L.circleMarker([c.lat,c.lon],{radius:c.stretch?5:7,color:col,fillColor:col,fillOpacity:.85,weight:1.5,dashArray:c.stretch?"4,4":null})
   .addTo(map).bindPopup(`<b>${esc(c.name)}</b><br>${esc(c.town)}<br>👥 ${c.kap??"?"} · Tanz ${c.dance==="confirmed"?"✓":c.dance==="probable"?"~":"?"}<br><a href="#" onclick="openDetail('${c.id}');return false">Details ▸</a>`);
  markers.push(m);
 });
 if (pts.length) map.fitBounds(L.latLngBounds(pts).pad(0.12), {maxZoom: 12});
}
function galPick(el){
 el.closest('.mbody').querySelectorAll('.gal img').forEach(i=>i.classList.remove('g-on'));
 el.classList.add('g-on');
 var m = el.closest('.mbox').querySelector('#galmain'); if(m) m.src = el.src;
}
function openDetail(id){
 const c = DATA.find(x=>x.id===id); if(!c) return;
 const img = IMG[c.id];
 const qText = c.open&&c.open.length ? c.open.map(q=>"- "+q).join("\\n") : "";
 const mail = `Hallo, wir planen eine Hochzeit mit ca. 150 Gästen inkl. Tanzfläche. Ist Ihre Location dafür geeignet, welche Bestuhlungsvarianten gibt es, wie ist die Catering-Regelung und was kostet die Raummiete an einem Samstag im\\n[MONAT/JAHR]?`
 document.getElementById("mbox").innerHTML = `
  ${(IMG[c.id] && IMG[c.id].ranked && IMG[c.id].ranked.length>1) ? `<div class="gal">${IMG[c.id].ranked.slice(0,7).map(g=>`<img src="${g.url}" loading="lazy" onclick="galPick(this)">`).join('')}</div><img id="galmain" src="${IMG[c.id].ranked[0].url}">` : (img?`<img src="${img.file||img.url}">`:`<div class="ph" style="height:120px">kein Bild</div>`) }
  <div class="mbody">
   <h2>${esc(c.name)}</h2><div class="town">${esc(c.town)} · Fahrt ${c.fahr_km ?? "?"} km (${c.fahr_min ?? "?"} min) · Luftlinie ${c.luft_km} km ${c.stretch?"· ⤢ Radius-Reißer":""}</div>
   <table>
    <tr><td>Kapazität</td><td>${esc(c.kap??"unbekannt — anfragen")} ${c.kap_note?"· "+esc(c.kap_note):""}</td></tr>
    <tr><td>Tanzfläche</td><td>${{confirmed:"bestätigt",probable:"wahrscheinlich",unknown:"unbekannt — anfragen"}[c.dance]}</td></tr>
    <tr><td>Rustikal</td><td>${{high:"hoch",mid:"mittel",low:"niedrig"}[c.rustic]}</td></tr>
    <tr><td>Catering</td><td>${{house:"Hausgastronomie",free:"Caterer frei",unknown:"unbekannt",null:"unbekannt"}[c.catering]||"unbekannt"}</td></tr>
    <tr><td>Preis</td><td>${esc(c.price||"unbekannt")}</td></tr>
    <tr><td>Status</td><td>${c.status==="gruen"?"● Kernkriterien belegt erfüllt":c.status==="gelb"?"● Rückfragen offen":"● Filter verletzt"}</td></tr>
    ${c.note?`<tr><td>Notiz</td><td>${esc(c.note)}</td></tr>`:""}
    ${c.open&&c.open.length?`<tr><td>Offene Fragen</td><td>${c.open.map(esc).join("<br>")}</td></tr>`:""}
    <tr><td>Quellen</td><td>${(c.quellen||[]).map(esc).join(" · ")}${c.site?` · <a href="${c.site}" target="_blank">Website ↗</a>`:""}</td></tr>
    ${img?`<tr><td>Bildquelle</td><td><a href="${IMG[c.id].source_url}" target="_blank">${IMG[c.id].page_url}</a></td></tr>`:""}
   </table>
   ${qText?`<div class="q">${qText.split("\\n").map(esc).join("<br>")}</div>`:""}
   <button class="copybtn" onclick="navigator.clipboard.writeText(\\`${mail.replace(/`/g,"'")}\\`).then(()=>this.textContent='Anfragetext kopiert ✓')">📋 Anfrage-E-Mail-Text kopieren</button>
   <button class="copybtn" onclick="document.getElementById('modal').classList.remove('open')">schließen</button>
  </div>`;
 document.getElementById("modal").classList.add("open");
}
document.getElementById("modal").onclick=e=>{if(e.target.id==="modal")e.target.classList.remove("open")};
document.getElementById("stand").textContent = "__STAND__";
render();
</script>
</body>
</html>
"""


def main():
    html = (TEMPLATE
            .replace("__DATA__", json.dumps(DATA, ensure_ascii=False))
            .replace("__IMAGES__", json.dumps(MANIFEST, ensure_ascii=False))
            .replace("__STAND__", "2026-10-06, 73 Kandidaten"))
    (ROOT / "locations.html").write_text(html, encoding="utf-8")
    print("locations.html geschrieben:", len(html), "Bytes,", len(DATA), "Kandidaten,", len(MANIFEST), "Bilder")


if __name__ == "__main__":
    main()
