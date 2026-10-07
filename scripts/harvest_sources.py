"""Harvest venue names from known aggregator list pages (full pagination).

Sources parsed:
  hochzeitsportal24.de branchenbuch lists (ort heilbronn/ludwigsburg/eppingen, all pages)
  hochzeits-location.info region pages (href slugs + text names)
  unserehochzeitslocation.de region pages (href slugs)
  freetime-events.de/locations
  mayer-erligheim.de/locations
Output: .research/harvest/<source>.json  [{name, town, href}]
Politeness: identified UA, 1.2s sleep between requests.
"""
import json
import re
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / ".research" / "harvest"
OUT.mkdir(parents=True, exist_ok=True)
UA = "hochzeit-location-search/0.1 (private research, single user)"


def get(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "ignore")


def save(name: str, rows: list):
    (OUT / f"{name}.json").write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{name}: {len(rows)}")


def hlp24(ort: str):
    rows, page, fails = [], 1, 0
    while fails < 2 and page < 12:
        url = f"https://www.hochzeitsportal24.de/branchenbuch/hochzeitslocations/ort/{ort}/" + (f"page/{page}/" if page > 1 else "")
        try:
            html = get(url)
        except Exception as e:
            print("  page fail", page, repr(e)[:60]); fails += 1; page += 1; continue
        fails = 0
        # entry cards: <h3 ...>NAME</h3> or links with title attr
        for m in re.finditer(r'href="(/branchenbuch/hochzeitslocations/[^"#]+)"[^>]*>(?:\s*<[^>]+>)*\s*([A-Za-zÄÖÜäöüß0-9][^<]{3,60})\s*<', html):
            href, nm = m.group(1), m.group(2).strip()
            if nm.lower().startswith(("zur", "mehr", "alle", "vergleic", "start")):
                continue
            rows.append({"name": nm, "href": "https://www.hochzeitsportal24.de" + href, "town": ort})
        time.sleep(1.2)
        page += 1
    uniq = {r["href"]: r for r in rows}
    save(f"hlp24_{ort}", list(uniq.values()))


def hl_region(ort: str):
    rows = []
    for page in (1, 2, 3):
        url = f"https://hochzeits-location.info/hochzeit/{ort}" + (f"?page={page}" if page > 1 else "")
        try:
            html = get(url)
        except Exception as e:
            print("  fail", url, repr(e)[:60]); break
        for m in re.finditer(r'href="(/hochzeitslocation/[^"#]+)"[^>]*>\s*(?:<img[^>]*alt="[^"]*"\s*)?([^<]{3,70})<', html):
            href, nm = m.group(1), m.group(2).strip()
            if len(nm) < 3 or nm.isdigit():
                continue
            rows.append({"name": nm, "href": "https://hochzeits-location.info" + href, "town": ort})
        time.sleep(1.2)
    uniq = {r["href"]: r for r in rows}
    save(f"hlinfo_{ort}", list(uniq.values()))


def uhl(region: str):
    url = f"https://www.unserehochzeitslocation.de/hochzeitslocations/{region}/"
    try:
        html = get(url)
    except Exception as e:
        print("  fail", repr(e)[:60]); return
    rows = [{"name": (m.group(2).replace('-', ' ').title()),
             "href": m.group(1), "town": region}
            for m in re.finditer(r'href="(/hochzeitslocation/([^"/]+)_[0-9]+/)"', html)]
    save(f"uhl_{region}", [{**r} for r in {r['href']: r for r in rows}.values()])


def simple(name, url, pattern):
    try:
        html = get(url)
    except Exception as e:
        print("  fail", name, repr(e)[:60]); return
    rows = [{"name": m.group(1).strip(), "href": url, "town": ""} for m in re.finditer(pattern, html)]
    save(name, list({r["name"]: r for r in rows}.values()))


def main():
    hlp24("heilbronn")
    hlp24("ludwigsburg")
    hlp24("eppingen")
    hl_region("brackenheim")
    hl_region("heilbronn")
    hl_region("ludwigsburg")
    uhl("heilbronn")
    uhl("ludwigsburg")
    simple("freetime", "https://www.freetime-events.de/locations/",
           r'<h[23][^>]*>\s*(?:<[^>]+>)?\s*([^<]{4,60})\s*</h[23]>')
    simple("mayer_erligheim", "https://www.mayer-erligheim.de/locations",
           r'<h[23][^>]*>\s*(?:<[^>]+>)?\s*([^<]{4,60})\s*</h[23]>')


if __name__ == "__main__":
    main()
