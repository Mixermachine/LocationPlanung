"""Overpass: list all settlements (place=*) within 30 km of Brackenheim.

Writes .research/places.json: [{name, place, population, lat, lon, dist_km}]
Politeness: identified UA, sequential endpoints, 30s pause on failure.
"""
import json
import math
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / ".research" / "places.json"
CENTER = (49.0786, 9.1072)
RADIUS_M = 30000

QUERY = f"""[out:json][timeout:90];
(
 node["place"~"^(city|town|village|suburb|hamlet)$"](around:{RADIUS_M},{CENTER[0]},{CENTER[1]});
 way["place"~"^(city|town|village|suburb|hamlet)$"](around:{RADIUS_M},{CENTER[0]},{CENTER[1]});
);
out center 800;"""

ENDPOINTS = [
    "https://maps.mail.ru/osm/tools/overpass/api/interpreter",
    "https://overpass-api.de/api/interpreter",
    "https://overpass.private.coffee/api/interpreter",
]
HEADERS = {
    "User-Agent": "hochzeit-location-search/0.1 (private research, single user)",
    "Referer": "https://github.com/local/hochzeit_location",
}


def hav_km(lat: float, lon: float) -> float:
    p = math.pi / 180
    x = (math.sin((lat - CENTER[0]) * p / 2) ** 2
         + math.cos(CENTER[0] * p) * math.cos(lat * p)
         * math.sin((lon - CENTER[1]) * p / 2) ** 2)
    return 6371 * 2 * math.asin(math.sqrt(x))


def main() -> None:
    data = urllib.parse.urlencode({"data": QUERY}).encode()
    payload = None
    for url in ENDPOINTS:
        try:
            req = urllib.request.Request(url, data=data, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=150) as resp:
                payload = json.load(resp)
            print("endpoint ok:", url)
            break
        except Exception as exc:  # noqa: BLE001
            print("fail:", url, repr(exc)[:80])
            time.sleep(31)
    if payload is None:
        raise SystemExit("all endpoints failed")

    seen = {}
    for e in payload.get("elements", []):
        t = e.get("tags", {})
        name = t.get("name")
        if not name:
            continue
        c = e.get("center") or {"lat": e.get("lat"), "lon": e.get("lon")}
        lat, lon = c.get("lat"), c.get("lon")
        if lat is None or lon is None:
            continue
        pop = int(t.get("place:population", 0) or 0)
        rec = {
            "name": name,
            "place": t.get("place"),
            "population": pop,
            "lat": round(lat, 5),
            "lon": round(lon, 5),
            "dist_km": round(hav_km(lat, lon), 1),
        }
        key = (name, round(lat, 2), round(lon, 2))
        if key not in seen:
            seen[key] = rec
    rows = sorted(seen.values(), key=lambda r: r["dist_km"])
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(rows)} settlements -> {OUT}")
    for r in rows:
        print(f"{r['dist_km']:5.1f} km | {r['place']:7} | pop {r['population']:>6} | {r['name']}")


if __name__ == "__main__":
    main()
