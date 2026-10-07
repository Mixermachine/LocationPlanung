"""Overpass wave 2: community halls / event venues / historic wine presses
(keltern) around Brackenheim that plain 'barn' query missed.

Writes .research/overpass2.json. Same politeness rules as wave 1.
"""
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / ".research" / "overpass2.json"
CENTER = (49.0786, 9.1072)
RADIUS_M = 30000

QUERY = f"""[out:json][timeout:60];
(
 node["amenity"~"^(community_centre|venue)$"](around:{RADIUS_M},{CENTER[0]},{CENTER[1]});
 way["amenity"~"^(community_centre|venue)$"](around:{RADIUS_M},{CENTER[0]},{CENTER[1]});
);out center 250;"""

QUERY2 = f"""[out:json][timeout:60];
(
 node["name"~"[Kk]elter$"](around:{RADIUS_M},{CENTER[0]},{CENTER[1]});
 way["name"~"[Kk]elter$"](around:{RADIUS_M},{CENTER[0]},{CENTER[1]});
 node["name"~"(Zehnt|Tabak|Frucht|Stall|Marstall|Speicher)$"](around:{RADIUS_M},{CENTER[0]},{CENTER[1]});
 way["name"~"(Zehnt|Tabak|Frucht|Stall|Marstall|Speicher)$"](around:{RADIUS_M},{CENTER[0]},{CENTER[1]});
);out center 250;"""

QUERIES = [QUERY, QUERY2]

ENDPOINTS = [
    "https://maps.mail.ru/osm/tools/overpass/api/interpreter",
    "https://overpass-api.de/api/interpreter",
    "https://overpass.private.coffee/api/interpreter",
]
HEADERS = {"User-Agent": "hochzeit-location-search/0.1 (private research, single user)"}


def main() -> None:
    all_elements = []
    for i, q in enumerate(QUERIES):
        data = urllib.parse.urlencode({"data": q}).encode()
        got = False
        for url in ENDPOINTS:
            try:
                req = urllib.request.Request(url, data=data, headers=HEADERS)
                with urllib.request.urlopen(req, timeout=120) as resp:
                    payload = json.load(resp)
                all_elements.extend(payload.get("elements", []))
                print(f"q{i} OK {url}")
                got = True
                break
            except Exception as exc:  # noqa: BLE001
                print(f"q{i} fail:", url, repr(exc)[:90])
                time.sleep(31)
        if not got:
            print(f"q{i}: skipping (all endpoints failed)")
        time.sleep(20)
    OUT.write_text(json.dumps({"elements": all_elements}, ensure_ascii=False), encoding="utf-8")
    print(f"total {len(all_elements)} elements -> {OUT}")


if __name__ == "__main__":
    main()
