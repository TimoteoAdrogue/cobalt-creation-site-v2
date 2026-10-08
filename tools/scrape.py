#!/usr/bin/env python3
"""Scrape cobaltcreation.com (Wix) into data/works.json and data/pages.json.

Source of truth for V2 and V3. Run from the project root:
    python3 tools/scrape.py            # uses data/raw/*.html if present, else downloads
    python3 tools/scrape.py --refresh  # re-download the live pages first
"""
import html, json, re, sys, urllib.request
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
SITE = "https://www.cobaltcreation.com/"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128 Safari/537.36"
PAGES = ["", "creation-d-objet-unique", "ateliers-de-personnalisation", "coffrets-packaging",
         "design-graphique-design-papier", "contact-feedback", "politique-de-confidentialite"]
RUBRICS = {"creation-d-objet-unique": 14, "ateliers-de-personnalisation": 20,
           "coffrets-packaging": 14, "design-graphique-design-papier": 22}

# Banner slides, read from the rendered slideshow on 2026-10-08 (Wix only ships slide 1 in the HTML).
# Order = live playback order starting from the slide served first.
BANNERS = {
    "": ["53e2f6_56d6a37866f5489ab2e188a6e434831e~mv2.jpg", "53e2f6_bed69cc934fb4abb8b4152db4876ca6f~mv2.jpg",
         "53e2f6_beea44379bf74660a11e63a464da50fe~mv2.jpg"],
    "creation-d-objet-unique": ["53e2f6_87c0fa6112f9428398e28798795d4435~mv2.jpg",
                                "53e2f6_beea44379bf74660a11e63a464da50fe~mv2.jpg"],
    "ateliers-de-personnalisation": ["53e2f6_572f520a8a4d41398a2cdd54bee9608d~mv2.jpg",
                                     "53e2f6_fc0048d91a964b30b9bd7db34361105c~mv2_d_10071_2146_s_2.jpg",
                                     "53e2f6_87c0fa6112f9428398e28798795d4435~mv2.jpg"],
    "coffrets-packaging": ["53e2f6_4922bf49ba42414ca20620dd4fadc25b~mv2.jpg",
                           "53e2f6_bf50eca92f9a422ab12ecdffb54ec9d1~mv2.jpg",
                           "53e2f6_3acb8531a73c4680a097802f5d4d7525~mv2.jpg"],
    "design-graphique-design-papier": ["53e2f6_0b9ff684a24841c892e024b978cb05ca~mv2.jpg",
                                       "53e2f6_56d6a37866f5489ab2e188a6e434831e~mv2.jpg",
                                       "53e2f6_ff12a3622cdb4286b2c51cdbb95ce102~mv2.jpg"],
}
HOME_COLUMNS = ["53e2f6_08cb192d62d24bceb420224c9b426c56~mv2.jpg",  # Animations retail sur-mesure
                "53e2f6_fc2e3c66345845eda03b96457d9f5f63~mv2.jpg",  # Studio Graphique
                "53e2f6_430ff5e51a034de59c0d94f9a639ec16~mv2.jpg"]  # Atelier parisien
LOGO_WALL = "53e2f6_61ffb11644664713932a2e78b41f8871~mv2.jpg"
VIDEO = "https://video.wixstatic.com/video/53e2f6_1ebc36ae7e814d1a9f0ab575045fee57/1080p/mp4/file.mp4"
YOUTUBE = "PG_bCMPUA3M"
BOOK = "https://www.cobaltcreation.com/_files/ugd/53e2f6_60c3fd2f9705410a9f57b6aa58808359.pdf"


def fetch(slug):
    req = urllib.request.Request(SITE + slug, headers={"User-Agent": UA})
    return urllib.request.urlopen(req, timeout=60).read().decode("utf-8")


def raw(slug, refresh):
    f = RAW / f"{slug or 'home'}.html"
    if refresh or not f.exists():
        RAW.mkdir(parents=True, exist_ok=True)
        f.write_text(fetch(slug), encoding="utf-8")
    return f.read_text(encoding="utf-8")  # UTF-8, never unicode_escape (breaks accents)


def galleries(src):
    """Every Wix Pro Gallery on the page, in on-page order, with its items in display order."""
    dec = json.JSONDecoder()
    out = []
    for m in re.finditer(r'"(comp-[a-z0-9]+)_galleryData":', src):
        data, _ = dec.raw_decode(src, m.end())
        pos = src.find(f'id="{m.group(1)}"')
        out.append((pos if pos >= 0 else 10**12, m.group(1), data.get("items", [])))
    seen, ordered = set(), []
    for pos, comp, items in sorted(out):
        if comp in seen:
            continue
        seen.add(comp)
        ordered.append((comp, items))
    return ordered


def clean(s):
    return re.sub(r"[ \t ​]+", " ", s or "").replace(" \n", "\n").strip()


class RichText(HTMLParser):
    """Collect text blocks (h1-h6, p, li) from Wix rich-text elements, in document order."""
    BLOCK = {"h1", "h2", "h3", "h4", "h5", "h6", "p", "li"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.depth = 0          # >0 while inside a rich-text element
        self.stack = []
        self.cur = None
        self.blocks = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if self.depth:
            self.depth += 1
        elif a.get("data-testid") == "richTextElement":
            self.depth = 1
        if self.depth and tag in self.BLOCK and self.cur is None:
            self.cur = [tag, ""]
        if self.depth and tag == "br" and self.cur is not None:
            self.cur[1] += "\n"
        if self.depth and tag == "a" and self.cur is not None:
            self.cur.append(a.get("href"))

    def handle_startendtag(self, tag, attrs):
        if self.depth and tag == "br" and self.cur is not None:
            self.cur[1] += "\n"

    def handle_endtag(self, tag):
        if self.depth and tag in self.BLOCK and self.cur is not None and self.cur[0] == tag:
            text = clean(self.cur[1])
            if text:
                self.blocks.append({"tag": tag, "text": text, "links": [h for h in self.cur[2:] if h]})
            self.cur = None
        if self.depth:
            self.depth -= 1

    def handle_data(self, data):
        if self.depth and self.cur is not None:
            self.cur[1] += data


def text_blocks(src):
    p = RichText()
    p.feed(src)
    return p.blocks


def main():
    refresh = "--refresh" in sys.argv
    works, pages = [], {}
    for slug in PAGES:
        src = raw(slug, refresh)
        title = html.unescape(re.search(r"<title>(.*?)</title>", src, re.S).group(1)).strip()
        desc = re.search(r'<meta name="description" content="([^"]*)"', src)
        pages[slug] = {"slug": slug, "title": title,
                       "description": html.unescape(desc.group(1)) if desc else "",
                       "blocks": text_blocks(src), "banner": BANNERS.get(slug, [])}
        if slug in RUBRICS:
            n = 0
            for gi, (comp, items) in enumerate(galleries(src)):
                for it in items:
                    md = it.get("metaData", {})
                    n += 1
                    works.append({
                        "page": slug, "gallery": gi, "index": n, "itemId": it["itemId"],
                        "media": it["mediaUrl"], "type": md.get("type", "image"),
                        "width": md.get("width"), "height": md.get("height"),
                        "title": clean(md.get("title", "")).replace("\r", ""),
                        "description": clean(md.get("description", "")).replace("\r", ""),
                    })
            assert n == RUBRICS[slug], f"{slug}: {n} items, expected {RUBRICS[slug]}"
    assert len(works) == 70, len(works)
    data = ROOT / "data"
    (data / "works.json").write_text(json.dumps(works, ensure_ascii=False, indent=1), encoding="utf-8")
    (data / "pages.json").write_text(json.dumps({
        "pages": pages, "home_columns": HOME_COLUMNS, "logo_wall": LOGO_WALL,
        "video": VIDEO, "youtube": YOUTUBE, "book": BOOK, "scraped": "2026-10-08",
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    print("works", len(works), {k: sum(w["page"] == k for w in works) for k in RUBRICS})


if __name__ == "__main__":
    main()
