#!/usr/bin/env python3
"""Static checks on a built site (V2 or V3) against the scraped live data.

    python3 tools/verify_static.py site-v2 https://timoteoadrogue.github.io/cobalt-creation-site-v2/
Exits non-zero on any failure.
"""
import re, sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlparse, unquote
sys.path.insert(0, str(Path(__file__).parent))
import common as c

site = Path(sys.argv[1]).resolve()
staging = sys.argv[2]
PAGES = [""] + [s for s, _ in c.NAV if s] + ["politique-de-confidentialite"]
fails = []


def fail(msg):
    fails.append(msg)


class Collect(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.refs, self.meta, self.links, self.text, self.ids = [], {}, {}, [], set()
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get("id"):
            self.ids.add(a["id"])
        if tag in ("script", "style"):
            self.skip += 1
        for k in ("href", "src", "poster"):
            if a.get(k):
                self.refs.append((tag, k, a[k]))
        for k in ("srcset",):
            if a.get(k):
                for part in a[k].split(","):
                    self.refs.append((tag, k, part.strip().split(" ")[0]))
        if tag == "meta":
            key = a.get("name") or a.get("property")
            if key:
                self.meta[key] = a.get("content", "")
        if tag == "link" and a.get("rel"):
            self.links[a["rel"]] = a.get("href")
        style = a.get("style", "")
        for u in re.findall(r"url\(([^)]+)\)", style):
            self.refs.append((tag, "style", u.strip("'\"")))

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self.skip -= 1

    def handle_data(self, d):
        if not self.skip:
            self.text.append(d)


all_text = {}
for slug in PAGES:
    f = site / (f"{slug}/" if slug else "") / "index.html"
    if not f.exists():
        fail(f"missing page {slug or '/'}"); continue
    raw = f.read_text(encoding="utf-8")
    p = Collect(); p.feed(raw)
    text = " ".join(p.text)
    all_text[slug] = text
    where = slug or "/"
    if p.meta.get("robots") != "noindex, nofollow":
        fail(f"{where}: robots meta = {p.meta.get('robots')!r}")
    if p.links.get("canonical") != "https://www.cobaltcreation.com/" + slug:
        fail(f"{where}: canonical {p.links.get('canonical')}")
    if not p.meta.get("og:url", "").startswith(staging) or not p.meta.get("og:image", "").startswith(staging):
        fail(f"{where}: og not absolute to staging ({p.meta.get('og:url')}, {p.meta.get('og:image')})")
    else:
        rel = p.meta["og:image"][len(staging):]
        if not (site / rel).exists():
            fail(f"{where}: og:image file missing {rel}")
    if "—" in raw or "–" in raw:
        fail(f"{where}: em or en dash present")
    for bad in ("lorem", "todo", "undefined", "NaN", "null", "xxx"):
        if re.search(rf"\b{re.escape(bad)}\b", text, re.I):
            fail(f"{where}: forbidden string {bad!r} in visible text")
    # every local reference resolves on disk
    page_url = staging + (f"{slug}/" if slug else "")
    for tag, k, ref in p.refs:
        if ref.startswith(("mailto:", "tel:", "data:", "#")):
            continue
        absu = urljoin(page_url, ref)
        if absu.startswith(staging):
            path = unquote(urlparse(absu).path[len(urlparse(staging).path):])
            frag = urlparse(absu).fragment
            target = site / path
            if path == "" or path.endswith("/"):
                target = target / "index.html"
            if not target.exists():
                fail(f"{where}: broken local {k} {ref}")
        elif absu.startswith("http"):
            host = urlparse(absu).netloc
            if host not in ("www.cobaltcreation.com", "www.instagram.com", "www.google.com", "timoteoadrogue.github.io"):
                fail(f"{where}: unexpected external {absu}")

# rubric counts
for slug, n in c.RUBRIC_COUNTS.items():
    raw = (site / slug / "index.html").read_text(encoding="utf-8")
    got = len(set(re.findall(r'id="piece-(\d+)"', raw)))
    if got != n:
        fail(f"{slug}: {got} works, expected {n}")

# contact details identical to the live site
raw = (site / "contact-feedback/index.html").read_text(encoding="utf-8")
for g in c.team():
    for person in g["people"]:
        if person["name"] not in raw:
            fail(f"contact: missing {person['name']}")
        if f'mailto:{person["email"]}"' not in raw:
            fail(f"contact: email {person['email']}")
        if person["phone"] and (c.esc(person["phone"]) not in raw or f'tel:{c.tel(person["phone"])}"' not in raw):
            fail(f"contact: phone {person['phone']}")
for s in (c.esc(c.PHONE), c.EMAIL, c.esc(c.ADDRESS_LINE)):
    if s not in raw:
        fail(f"contact: missing {s}")

# home logos
raw = (site / "index.html").read_text(encoding="utf-8")
for l in c.LOGOS:
    if l["file"] not in raw:
        fail(f"home: logo {l['name']} missing")
if "depuis plus de 10 ans" not in raw:
    fail("home: founding claim must read « depuis plus de 10 ans »")
if "2014" in raw:
    fail("home: unsourced year 2014 present")

robots = (site / "robots.txt").read_text()
if "Disallow: /" not in robots:
    fail("robots.txt does not disallow")
if not (site / ".nojekyll").exists():
    fail(".nojekyll missing")

print(f"{site.name}: {len(fails)} failure(s)")
for f in fails:
    print("  FAIL", f)
sys.exit(1 if fails else 0)
