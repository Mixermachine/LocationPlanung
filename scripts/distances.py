"""Geocode wedding venue candidates (Nominatim) and compute driving distance/time
from Brackenheim via public OSRM. Writes results into .research/candidates.json
and prints a sorted table.

Politeness: identified User-Agent, 1.1s sleep between Nominatim requests,
sequential OSRM calls.
"""
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANDIDATES = ROOT / ".research" / "candidates.json"
ORIGIN = (9.1072, 49.0786)  # lon,lat Brackenheim
UA = "hochzeit-location-search/0.1 (private research, single user)"


def get(url: str, params: dict | None = None) -> dict:
    q = urllib.parse.urlencode(params or {})
    full = f"{url}?{q}" if q else url
    req = urllib.request.Request(full, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def geocode(query: str):
    if not query:
        return None
    res = get(
        "https://nominatim.openstreetmap.org/search",
        {"q": query, "format": "jsonv2", "limit": 1, "countrycodes": "de"},
    )
    if not res:
        return None
    return float(res[0]["lon"]), float(res[0]["lat"]), res[0]["display_name"]


def route(lon: float, lat: float):
    res = get(
        "https://router.project-osrm.org/route/v1/driving/"
        f"{ORIGIN[0]},{ORIGIN[1]};{lon},{lat}",
        {"overview": "false"},
    )
    r = res["routes"][0]
    return r["distance"] / 1000.0, r["duration"] / 60.0


def main():
    cands = json.loads(CANDIDATES.read_text(encoding="utf-8"))
    for c in cands:
        if "geo" not in c and c.get("q"):
            try:
                time.sleep(1.1)
                g = geocode(c["q"])
                if g:
                    c["geo"] = {"lon": g[0], "lat": g[1], "hit": g[2][:80]}
                    try:
                        km, min_ = route(g[0], g[1])
                        c["drive"] = {"km": round(km, 1), "min": round(min_)}
                    except Exception as exc:
                        print(f"route fail {c['id']}: {exc}")
                else:
                    c["geo"] = None
            except Exception as exc:
                print(f"geocode fail {c['id']}: {exc}")
    CANDIDATES.write_text(json.dumps(cands, ensure_ascii=False, indent=2), encoding="utf-8")

    rows = [c for c in cands if c.get("drive")]
    rows.sort(key=lambda c: c["drive"]["km"])
    print(f"{'km':>6} {'min':>4}  name / town")
    for c in rows:
        d = c["drive"]
        inr = "<=30km" if d["km"] <= 30 else "RAUS"
        print(f"{d['km']:6.1f} {d['min']:4}  {inr}  {c['name']} | {c['town']}")
    missing = [c["id"] for c in cands if not c.get("drive")]
    if missing:
        print("ohne Distanz:", ", ".join(missing))


if __name__ == "__main__":
    main()
