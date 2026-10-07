"""Final distance pass: OSRM drive distance/time from Brackenheim for every
candidate in .research/candidates_master.json; writes .research/candidates_dist.json.
"""
import json
import math
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / ".research" / "candidates_master.json"
OUT = ROOT / ".research" / "candidates_dist.json"
ORIGIN = (9.1072, 49.0786)  # lon,lat
UA = "hochzeit-location-search/0.1 (private research, single user)"


def hav(lon, lat):
    p = math.pi / 180
    x = (math.sin((lat - ORIGIN[1]) * p / 2) ** 2
         + math.cos(ORIGIN[1] * p) * math.cos(lat * p)
         * math.sin((lon - ORIGIN[0]) * p / 2) ** 2)
    return 6371 * 2 * math.asin(math.sqrt(x))


def route(lon, lat):
    url = f"https://router.project-osrm.org/route/v1/driving/{ORIGIN[0]},{ORIGIN[1]};{lon},{lat}?overview=false"
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=25) as r:
        x = json.load(r)["routes"][0]
    return round(x["distance"] / 1000, 1), round(x["duration"] / 60)


def main():
    cands = json.loads(SRC.read_text(encoding="utf-8"))
    fails = 0
    for c in cands:
        c["luft_km"] = round(hav(c["lon"], c["lat"]), 1)
        try:
            km, min = route(c["lon"], c["lat"])
            c["fahr_km"] = km
            c["fahr_min"] = min
        except Exception:
            fails += 1
            time.sleep(2)
            try:
                km, min = route(c["lon"], c["lat"])
                c["fahr_km"] = km
                c["fahr_min"] = min
            except Exception as e:
                c["fahr_km"] = None
                c["fahr_min"] = None
                print("route fail:", c["id"], repr(e)[:60])
        time.sleep(0.35)
    OUT.write_text(json.dumps(cands, ensure_ascii=False, indent=1), encoding="utf-8")
    rows = sorted(cands, key=lambda c: (c.get("fahr_km") or 999))
    print(f"{'Fahr':>6} {'min':>4} {'Luft':>5}  id")
    for c in rows:
        print(f"{str(c.get('fahr_km')):>6} {str(c.get('fahr_min')):>4} {c['luft_km']:5.1f}  {c['id']}")
    print("total:", len(cands), "route fails:", fails)


if __name__ == "__main__":
    main()
