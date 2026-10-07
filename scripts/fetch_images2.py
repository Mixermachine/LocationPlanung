"""Second image pass: pull og:image from specific subpages for missing top candidates."""
import json
from pathlib import Path
from fetch_images import IMG, fetch, get_og  # reuse helpers
import urllib.parse
import re
import time

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / ".research" / "images_manifest.json"

TARGETS = {
    "klosterkelter-maulbronn": "https://www.klosterkelter.de/hochzeiten/",
    "sonnenhof": "https://sonnenhof-event.de/",
    "kelter-hohenhaslach": "https://raeume-zum-feiern.de/in/sachsenheim.html",
    "wiesenscheune": "https://www.wiesenscheune.com/",
    "wedding-ranch": "https://www.wedding-ranch.de/hochzeit/",
    "kulturwerk-kelter-kleinbottwar": "https://www.kulturwerk-kelter.de/raeume_mieten",
    "schloss-massenbach": "https://schloss-massenbach.de/",
    "alte-kelter-horrheim": "https://www.vaihingen.de/leben-wohnen/staedtische-veranstaltungsraeume/alte-kelter-horrheim",
    "kelter-langenbeutingen": "https://www.langenbrettach.de/freizeit-erlebnis/veranstaltungsstaetten/kelter-langenbeutingen",
    "keltersaal-cannstatt": "https://weller-dasoriginal.de/locations/keltersaal-bad-cannstatt/",
    "burg-stettenfels": "https://burg-stettenfels.de/de/feiern-und-hochzeiten/fuggersaal.php",
    "stadthalle-alte-kelter-besigheim": "https://www.besigheim.de",
    "steng": "https://steng-lauffen.de/eventhalle/",
    "michelfeld": "https://www.landgut-schloss-michelfeld.de/hochzeiten/",
    "eichenstolz": "https://www.eichenstolz.de/",
    "schifferer": "https://www.mayer-erligheim.de/locations/weingut-tobias-schifferer",
    "sml-carlocation": "https://www.hochzeitsportal24.de/branchenbuch/hochzeitslocations/sml-carlocation-eberdingen-hochdorf/",
    "zuechterheim": "https://hochzeits-location.info/hochzeitslocation/gaststatte-zuchterheim",
    "fessler-muehle": "https://hochzeit.click/hochzeitslocation/fessler-muehle/",
    "marienhoehe": "https://www.xn--landgut-marienhhe-e0b.de/event-location/hochzeiten",
}


def main():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8")) if MANIFEST.exists() else {}
    for cid, page in TARGETS.items():
        if cid in manifest:
            continue
        try:
            hb, fu = fetch(page)
            html = hb.decode("utf-8", "ignore")
            img = get_og(html, fu)
            if not img:
                m = re.search(r'(https?://[^"\']+\.(?:jpe?g|png|webp))', html, re.I)
                img = m.group(1) if m else None
            if not img:
                print("no img", cid)
                continue
            ib, _ = fetch(img)
            if len(ib) < 8000:
                print("tiny", cid, len(ib))
                continue
            ext = img.rsplit(".", 1)[-1].split("?")[0].lower()
            ext = {"jpg": "jpg", "jpeg": "jpg", "png": "png", "webp": "webp"}.get(ext, "jpg")
            dest = IMG / f"{cid}.{ext}"
            dest.write_bytes(ib)
            manifest[cid] = {"file": f"images/{dest.name}", "source_url": img, "page_url": page}
            print("ok", cid, len(ib) // 1024, "KB")
        except Exception as e:
            print("fail", cid, repr(e)[:90])
        time.sleep(1)
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")
    print("total images:", len(manifest))


if __name__ == "__main__":
    main()
