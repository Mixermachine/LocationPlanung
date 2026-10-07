"""Build search clusters from .research/places.json.

Rules:
- keep place in {city, town, village} only (drop hamlets/suburbs: they belong to parents)
- dedupe identical names
- greedy geographic clustering: a cluster spans <= ~7 km diameter, max 4 names
- cluster name string used directly in web-search templates

Writes .research/clusters.json and prints the list.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLACES = ROOT / ".research" / "places.json"
OUT = ROOT / ".research" / "clusters.json"
MAX_DIAM_KM = 7.5
MAX_PER_CLUSTER = 4


def hav(a, b):
    import math
    p = math.pi / 180
    lat1, lon1 = a
    lat2, lon2 = b
    x = (math.sin((lat2 - lat1) * p / 2) ** 2
         + math.cos(lat1 * p) * math.cos(lat2 * p)
         * math.sin((lon2 - lon1) * p / 2) ** 2)
    return 6371 * 2 * math.asin(math.sqrt(x))


def main():
    rows = [r for r in json.loads(PLACES.read_text(encoding="utf-8"))
            if r["place"] in ("city", "town", "village")]
    rows.sort(key=lambda r: r["dist_km"])
    seen_names = set()
    uniq = []
    for r in rows:
        if r["name"] in seen_names:
            continue
        seen_names.add(r["name"])
        uniq.append(r)

    clusters = []
    for r in uniq:
        placed = False
        for c in clusters:
            if len(c["members"]) >= MAX_PER_CLUSTER:
                continue
            if all(hav((m["lat"], m["lon"]), (r["lat"], r["lon"])) <= MAX_DIAM_KM
                   for m in c["members"]):
                c["members"].append(r)
                placed = True
                break
        if not placed:
            clusters.append({"members": [r]})

    out = []
    for c in clusters:
        names = [m["name"] for m in c["members"]]
        out.append({
            "names": names,
            "query_label": " ".join(names[:2]) if len(names) > 1 else names[0],
            "lat": round(sum(m["lat"] for m in c["members"]) / len(c["members"]), 4),
            "lon": round(sum(m["lon"] for m in c["members"]) / len(c["members"]), 4),
            "members": [m["name"] for m in c["members"]],
        })
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(uniq)} unique towns -> {len(out)} clusters")
    for i, c in enumerate(out):
        print(f"{i:2} | {c['query_label']}")


if __name__ == "__main__":
    main()
