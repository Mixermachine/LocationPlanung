"""Filter .research/overpass2.json to hall/barn-like names worth checking."""
import json
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CENTER = (49.0786, 9.1072)
PATTERN = re.compile(r"(kelter|zehnt|tabak|frucht|stall|speicher|scheune|scheuer|festsaal|festhalle|event|halle|saal)", re.I)


def hav(lat, lon):
    p = math.pi / 180
    x = (math.sin((lat - CENTER[0]) * p / 2) ** 2
         + math.cos(CENTER[0] * p) * math.cos(lat * p)
         * math.sin((lon - CENTER[1]) * p / 2) ** 2)
    return 6371 * 2 * math.asin(math.sqrt(x))


def main():
    d = json.loads((ROOT / ".research" / "overpass2.json").read_text(encoding="utf-8"))
    rows = []
    for e in d.get("elements", []):
        t = e.get("tags", {})
        name = t.get("name", "")
        if not name:
            continue
        c = e.get("center") or {"lat": e.get("lat"), "lon": e.get("lon")}
        lat, lon = c.get("lat"), c.get("lon")
        if lat is None:
            continue
        if PATTERN.search(name):
            rows.append((hav(lat, lon), name, t.get("addr:city") or t.get("addr:place") or "",
                         t.get("amenity") or t.get("historic") or "", round(lat, 4), round(lon, 4)))
    rows.sort()
    seen = set()
    for dist, name, city, kind, lat, lon in rows:
        key = (name, lat, lon)
        if key in seen:
            continue
        seen.add(key)
        print(f"{dist:5.1f} | {name} | {city} | {kind} | {lat},{lon}")


if __name__ == "__main__":
    main()
