"""Precompute OSRM distances for .research/cluster_adds.json (no master mutation)."""
import json, math, time, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / ".research" / "cluster_adds.json"
OUT = ROOT / ".research" / "cluster_adds_dist.json"
ORIGIN = (9.1072, 49.0786)
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

adds = json.loads(SRC.read_text(encoding="utf-8"))
fails = 0
for c in adds:
    if c.get("lat") is None or c.get("lon") is None:
        c["luft_km"] = None; continue
    c["luft_km"] = round(hav(c["lon"], c["lat"]), 1)
    try:
        km, mn = route(c["lon"], c["lat"])
        c["fahr_km"], c["fahr_min"] = km, mn
    except Exception:
        fails += 1
        time.sleep(1.5)
        try:
            km, mn = route(c["lon"], c["lat"])
            c["fahr_km"], c["fahr_min"] = km, mn
        except Exception:
            c["fahr_km"] = c["fahr_min"] = None

OUT.write_text(json.dumps(adds, ensure_ascii=False, indent=1), encoding="utf-8")
inside = [c for c in adds if (c.get("fahr_km") or 99) <= 30.5]
stretch = [c for c in adds if 30.5 < (c.get("fahr_km") or 999) <= 35.5]
outside = [c for c in adds if (c.get("fahr_km") or 999) > 35.5 or c.get("fahr_km") is None]
print(f"adds={len(adds)} osrm_fails={fails}")
print(f"<=30km: {len(inside)} | 30-35km stretch: {len(stretch)} | >35km/no-route: {len(outside)}")
print()
print("== KERN (<=30km) & kap>=150 ==")
for c in sorted(inside, key=lambda x: (-(x.get('kap') or 0))):
    if (c.get('kap') or 0) >= 150:
        print(f"  {c['fahr_min']}min/{c['fahr_km']}km {c['kap']:>4} {c['name']} | {c.get('town')} | tanz={c.get('dance')} rustic={c.get('rustic')}")
print()
print("== KERN (<=30km) rustic high, kap unbekannt ==")
for c in inside:
    if c.get('kap') is None and c.get('rustic') == 'high':
        print(f"  {c['fahr_min']}min/{c['fahr_km']}km ? {c['name']} | {c.get('town')} | conf={c.get('confidence')}")
