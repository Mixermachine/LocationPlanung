"""Print Overpass result JSON as a readable candidate list."""
import json
import math
import sys
from pathlib import Path

CENTER = (49.0786, 9.1072)  # Brackenheim


def haversine_km(a, b):
    (lat1, lon1), (lat2, lon2) = a, b
    p = math.pi / 180
    x = math.sin((lat2 - lat1) * p / 2) ** 2 + math.cos(lat1 * p) * math.cos(lat2 * p) * math.sin((lon2 - lon1) * p / 2) ** 2
    return 6371 * 2 * math.asin(math.sqrt(x))


def main(path: Path):
    d = json.loads(path.read_text(encoding="utf-8"))
    rows = []
    for e in d.get("elements", []):
        t = e.get("tags", {})
        c = e.get("center") or {"lat": e.get("lat"), "lon": e.get("lon")}
        kind = t.get("amenity") or t.get("leisure") or t.get("building") or "?"
        dist = haversine_km(CENTER, (c["lat"], c["lon"]))
        rows.append((dist, t.get("name", "?"), t.get("addr:city") or t.get("addr:place") or "", kind, c["lat"], c["lon"]))
    rows.sort()
    print(f"{'km':>5} | name | city | tag | lat,lon")
    for dist, name, city, kind, lat, lon in rows:
        print(f"{dist:5.1f} | {name} | {city} | {kind} | {lat:.5f},{lon:.5f}")


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else root / ".research" / "overpass1.json")
