"""Harvest municipal venue pages (Städte im Radius). Input: .research/staedte_sources.json
[{town,url}]. Extract hall/Kelter-like venue names from headings+links of each page.
Output: .research/harvest/staedte.json -> feeds audit_coverage.
"""
import json
import re
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
UA = "hochzeit-location-search/0.1 (private research, single user)"
VENUE = re.compile(r"(kelter|scheune|scheuer|zehnt|halle|\bsaal|b[üu]rger|gemeindehaus|verwaltungs|turm|m[üu]hle|schloss|gutshof|fest)", re.I)
NOISE = re.compile(r"impressum|kontakt|anfahrt|navigation|login|cookie|startseite|footer|anmelden|verzeichnis|所有的", re.I)


def clean(s):
    s = re.sub(r"<[^>]+>", " ", s)
    s = re.sub(r"\s+", " ", s).strip(" -–—|·:")
    return s


def main():
    src = json.loads((ROOT / ".research" / "staedte_sources.json").read_text(encoding="utf-8"))
    rows = []
    for s in src:
        try:
            req = urllib.request.Request(s["url"], headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=30) as r:
                html = r.read().decode("utf-8", "ignore")
        except Exception as e:
            print("fail", s["town"], repr(e)[:60]); continue
        names = set()
        for m in re.finditer(r"<(?:h[1-6]|a|strong|dt)[^>]*>(.*?)</(?:h[1-6]|a|strong|dt)>", html, re.S | re.I):
            t = clean(m.group(1))
            if 4 < len(t) < 70 and VENUE.search(t) and not NOISE.search(t):
                names.add(t)
        for n in names:
            rows.append({"name": n, "town": s["town"], "href": s["url"], "source": "stadtseite"})
        print(f'{s["town"]}: {len(names)}')
        time.sleep(1.0)
    uniq = {}
    for r in rows:
        uniq.setdefault((r["town"], r["name"]), r)
    out = ROOT / ".research" / "harvest"
    out.mkdir(exist_ok=True)
    (out / "staedte.json").write_text(json.dumps(list(uniq.values()), ensure_ascii=False, indent=1), encoding="utf-8")
    print("total rows:", len(uniq))


if __name__ == "__main__":
    main()
