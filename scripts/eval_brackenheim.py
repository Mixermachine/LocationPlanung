"""Evaluate Brackenheim municipal hall page: extract each hall + capacity claims."""
import json
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
UA = "hochzeit-location-search/0.1 (private research, single user)"
URL = "https://www.brackenheim.de/leben-wohnen/turn-sportanlagen/turn-und-versammlungshallen"

req = urllib.request.Request(URL, headers={"User-Agent": UA})
html = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "ignore")
text = re.sub(r"<script.*?</script>|<style.*?</style>", " ", html, flags=re.S | re.I)
text = re.sub(r"<[^>]+>", "\n", text)
text = re.sub(r"\n{2,}", "\n", text)

lines = [l.strip() for l in text.split("\n") if l.strip()]
HALL = re.compile(r"(halle|saal|kelter|zentrum|burg|scheune|buerger|b[üu]rger)", re.I)
out, cur = [], None
for i, l in enumerate(lines):
    if 4 < len(l) < 60 and HALL.search(l) and not re.search(r"impressum|navigation|men[üu]|startseite|kontakt", l, re.I):
        blob = " ".join(lines[i:i + 12])
        kps = re.findall(r"(\d{2,4})\s*(?:Personen|Besucher|Gaeste|Pl[äa]tze|St[üu]hle|m[²2]\b)", blob)
        cur = {"name": l, "context": blob[:400], "caps": kps}
        out.append(cur)
seen, uniq = set(), []
for o in out:
    if o["name"] not in seen:
        seen.add(o["name"]); uniq.append(o)
(ROOT / ".research" / "brackenheim_halls.json").write_text(json.dumps(uniq, ensure_ascii=False, indent=1), encoding="utf-8")
for o in uniq:
    print(f'- {o["name"]} | caps: {o["caps"]}')
print("total:", len(uniq))
