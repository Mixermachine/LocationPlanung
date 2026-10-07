"""Run an Overpass API query for event venues/halls/barns around Brackenheim (30 km).

Writes JSON to .research/overpass1.json. Honors rate-limit etiquette:
identified User-Agent, sequential endpoints, 30s pause between failures.
"""
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

CENTER = (49.0786, 9.1072)  # 74336 Brackenheim
RADIUS_M = 30000

QUERY = f"""[out:json][timeout:90];
(node["amenity"="event_venue"](around:{RADIUS_M},{CENTER[0]},{CENTER[1]});
 way["amenity"="event_venue"](around:{RADIUS_M},{CENTER[0]},{CENTER[1]});
 node["leisure"="hall"](around:{RADIUS_M},{CENTER[0]},{CENTER[1]});
 way["leisure"="hall"](around:{RADIUS_M},{CENTER[0]},{CENTER[1]});
 node["building"="barn"][name](around:{RADIUS_M},{CENTER[0]},{CENTER[1]});
 way["building"="barn"][name](around:{RADIUS_M},{CENTER[0]},{CENTER[1]}););
out center 300;"""

ENDPOINTS = [
    "https://maps.mail.ru/osm/tools/overpass/api/interpreter",
    "https://overpass-api.de/api/interpreter",
    "https://overpass.private.coffee/api/interpreter",
]
HEADERS = {
    "User-Agent": "hochzeit-location-search/0.1 (private research, single user)",
    "Referer": "https://github.com/local/hochzeit_location",
}


def run(out_path: Path) -> int:
    data = urllib.parse.urlencode({"data": QUERY}).encode()
    for url in ENDPOINTS:
        try:
            req = urllib.request.Request(url, data=data, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=120) as resp:
                payload = json.load(resp)
        except Exception as exc:  # noqa: BLE001
            print(f"FAIL {url}: {exc!r}")
            time.sleep(31)
            continue
        elements = payload.get("elements", [])
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(payload), encoding="utf-8")
        print(f"OK {url}: {len(elements)} elements -> {out_path}")
        return len(elements)
    print("All endpoints failed.")
    return 0


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    n = run(root / ".research" / "overpass1.json")
    print(f"elements={n}")
