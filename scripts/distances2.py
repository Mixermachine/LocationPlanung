"""Compute driving distance/time from Brackenheim for every candidate that has geo
coords (either 'geo' dict or explicit 'lat'/'lon'), then print sorted table.

Sequential OSRM calls, identified User-Agent, small sleep for politeness.
Candidates without any coords get straight-line estimate from 'latlon' if present.
"""
import json
import math
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANDIDATES = ROOT / ".research" / "candidates2.json"
ORIGIN = (9.1072, 49.0786)  # lon,lat Brackenheim
UA = "hochzeit-location-search/0.1 (private research, single user)"


def route(lon, lat):
    url = (f"https://router.project-osrm.org/route/v1/driving/{ORIGIN[0]},{ORIGIN[1]};{lon},{lat}?overview=false")
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        res = json.load(r)
    x = res["routes"][0]
    return x["distance"] / 1000.0, x["duration"] / 60.0


def hav(lon, lat):
    p = math.pi / 180
    x = math.sin((lat - ORIGIN[1]) * p / 2) ** 2 + math.cos(ORIGIN[1] * p) * math.cos(lat * p) * math.sin((lon - ORIGIN[0]) * p / 2) ** 2
    return 6371 * 2 * math.asin(math.sqrt(x))


def main():
    cands = json.loads(CANDIDATES.read_text(encoding="utf-8"))
    for c in cands:
        lon = lat = None
        if c.get("geo"):
            lon, lat = c["geo"]["lon"], c["geo"]["lat"]
        elif c.get("latlon"):
            lat, lon = c["latlon"]
        if lon is None:
            continue
        try:
            time.sleep(0.4)
            km, mn = route(lon, lat)
            c["drive"] = {"km": round(km, 1), "min": round(mn), "luft": round(hav(lon, lat), 1)}
        except Exception as e:
            c["drive"] = {"km": round(hav(lon, lat), 1), "min": None, "luft": round(hav(lon, lat), 1)}
            print("route fallback (Luftlinie)", c["id"], repr(e)[:60])
    CANDIDATES.write_text(json.dumps(cands, ensure_ascii=False, indent=2), encoding="utf-8")

    rows = [c for c in cands if c.get("drive")]
    rows.sort(key=lambda c: c["drive"]["km"])
    print(f"\n{'Fahrt':>6} {'min':>4} {'Luft':>5}  Status  name | ort | Kapazität")
    for c in rows:
        d = c["drive"]
        lim = round((d["km"] or d["luft"]) / 30 * 40)  # rough: road > air
        status = "OK" if (d["km"] <= 32) else ("GRENZE" if d["km"] <= 38 else "RAUS")
        mn = d["min"] if d["min"] else "-"
        print(f"{d['km']:6.1f} {str(mn):>4} {d['luft']:5.1f}  {status:6} {c['name']} | {c['town']} | {c['kap']}")


if __name__ == "__main__":
    main()
