"""Shared content model for the V2 and V3 builds.

Everything here reads data/*.json (scraped from cobaltcreation.com on 2026-10-08).
No fact is typed by hand: copy comes from the live pages, with the documented
typo fixes in FIXES applied to running text only.
"""
import html, json, re, shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
MEDIA = ROOT / "media"

PAGES = json.loads((DATA / "pages.json").read_text())
WORKS = json.loads((DATA / "works.json").read_text())
MEDIA_INDEX = json.loads((DATA / "media.json").read_text())
LOGOS = json.loads((DATA / "logos.json").read_text())

# Unambiguous slips in the live running text (logged in DECISIONS.md). Never applied to
# names, emails, phone numbers or the privacy policy.
FIXES = [
    ("Dolce & Gabanna", "Dolce & Gabbana"),
    ("La feuille l'or", "La feuille d'or"),
    ("La feuille l’or", "La feuille d’or"),
    ("magnifie et créé des", "magnifie et crée des"),
    ("Nos créatifs vous accompagne ", "Nos créatifs vous accompagnent "),
    ("cadeaux d’exceptions", "cadeaux d’exception"),
    ("cadeaux d'exceptions", "cadeaux d'exception"),
]

# Navigation: live order, live labels, live slugs.
NAV = [
    ("", "Accueil"),
    ("creation-d-objet-unique", "Nos ateliers signatures"),
    ("ateliers-de-personnalisation", "Nos animations retail sur mesure"),
    ("design-graphique-design-papier", "Notre studio graphique & design"),
    ("coffrets-packaging", "Notre atelier parisien"),
    ("contact-feedback", "Contact"),
]
RUBRICS = ["creation-d-objet-unique", "ateliers-de-personnalisation",
           "design-graphique-design-papier", "coffrets-packaging"]
RUBRIC_COUNTS = {"creation-d-objet-unique": 14, "ateliers-de-personnalisation": 20,
                 "coffrets-packaging": 14, "design-graphique-design-papier": 22}

ADDRESS_LINE = "35, Boulevard Berthier - 75017 Paris"
PHONE = "+33 (0) 1 44 09 81 85"
EMAIL = "contact@cobaltcreation.com"
HOURS = "Horaires d'ouverture : 9h30 - 18h30"
INSTAGRAM = "https://www.instagram.com/cobaltcreation/"
BOOK_SIZE = "9,7 Mo"  # 9 748 595 bytes, measured 2026-10-08
MAPS_LINK = "https://www.google.com/maps/search/?api=1&query=35+Boulevard+Berthier+75017+Paris"
MAPS_EMBED = "https://www.google.com/maps?q=35+Boulevard+Berthier,+75017+Paris&output=embed"
YOUTUBE_ID = PAGES["youtube"]
YOUTUBE_TITLE = "Atelier Gravure by Givenchy"


def fix(s):
    for a, b in FIXES:
        s = s.replace(a, b)
    return s


def typo(s):
    """French typographic apostrophe; keeps the words untouched."""
    return s.replace("'", "’")


def esc(s):
    return html.escape(s, quote=True)


def tel(s):
    s = s.replace("(0)", "")
    return "+" + re.sub(r"\D", "", s)


def blocks(slug):
    return PAGES["pages"][slug]["blocks"]


def body_blocks(slug):
    """Page blocks without the shared footer."""
    out = []
    for b in blocks(slug):
        if b["text"].startswith("Agence Cobalt Création"):
            break
        out.append(b)
    return out


def join_fragments(texts):
    """Wix breaks paragraphs into one <p> per line. Re-join lines into paragraphs:
    a line continues the previous one when the previous ends with a comma or has no
    final punctuation and the new line starts in lowercase."""
    paras = []
    for t in texts:
        if paras and (paras[-1].endswith(",") or (t[:1].islower() and not paras[-1].endswith((".", "!", "?", ":")))):
            paras[-1] += " " + t
        else:
            paras.append(t)
    return [typo(fix(p)) for p in paras]


def heading(slug):
    h = next(b["text"] for b in blocks(slug) if b["tag"] == "h1")
    return [x.strip() for x in h.split("\n") if x.strip()]


def intro(slug):
    """Intro paragraphs of a rubric page (between the h1 and the gallery)."""
    texts, started = [], False
    for b in body_blocks(slug):
        if b["tag"] == "h1":
            if started:
                break  # design page: second h1 opens the keyword block, left out on purpose
            started = True
            continue
        if started and b["tag"] == "p":
            texts.append(b["text"])
    return join_fragments(texts)


def home():
    bl = [b["text"] for b in body_blocks("")]
    i = {t: n for n, t in enumerate(bl)}
    def between(a, b):
        return bl[i[a] + 1:i[b]]
    agence = join_fragments(between("NOTRE AGENCE", "Animations retail sur-mesure"))
    col1 = between("Animations retail sur-mesure", "Studio Graphique")
    col2 = between("Studio Graphique", "Atelier parisien")
    col3 = between("Atelier parisien", "NOTRE BOOK")
    lis = {b["text"] for b in body_blocks("") if b["tag"] == "li"}
    def split(col):
        paras = [t for t in col if t not in lis and not t.startswith("•")]
        bullets = [t for t in col if t in lis] + [t.lstrip("• ").strip() for t in col if t.startswith("•")]
        return paras, [typo(fix(x)) for x in bullets]
    p1, b1 = split(col1)
    p2, b2 = split(col2)
    p3, b3 = split(col3)
    lead3 = [t for t in p3 if t.endswith(":")]
    p3 = [t for t in p3 if not t.endswith(":")]
    return {
        "title": "Notre agence",
        "agence": agence,
        "columns": [
            {"title": "Animations retail sur-mesure", "slug": "ateliers-de-personnalisation",
             "image": PAGES["home_columns"][0], "paras": join_fragments(p1), "bullets": b1, "lead": None},
            {"title": "Studio Graphique", "slug": "design-graphique-design-papier",
             "image": PAGES["home_columns"][1], "paras": join_fragments(p2), "bullets": b2, "lead": None},
            {"title": "Atelier parisien", "slug": "coffrets-packaging",
             "image": PAGES["home_columns"][2], "paras": join_fragments(p3), "bullets": b3,
             "lead": typo(lead3[0]) if lead3 else None},
        ],
        "book_title": "Notre book",
        "book_link": "Télécharger notre book",
        "trust_title": "Ils nous font confiance",
    }


def team():
    """Five groups, twelve people, exactly as published on /contact-feedback."""
    groups, cur, person = [], None, None
    started = False
    for b in body_blocks("contact-feedback"):
        if b["tag"] == "h2":
            started = True
            cur = {"name": b["text"], "people": []}
            groups.append(cur)
            person = None
            continue
        if not started or b["tag"] != "p":
            continue
        for t in [x.strip() for x in b["text"].split("\n") if x.strip()]:
            if "@" in t:
                person["email"] = t
            elif t.startswith("+") or t[:1].isdigit():
                person["phone"] = t
            elif person is None or person.get("role"):
                person = {"name": t, "role": None, "email": None, "phone": None}
                cur["people"].append(person)
            else:
                person["role"] = t
    assert len(groups) == 5 and sum(len(g["people"]) for g in groups) == 12, groups
    return groups


def privacy():
    out = []
    for b in body_blocks("politique-de-confidentialite"):
        for t in [x.strip() for x in b["text"].split("\n") if x.strip()]:
            out.append({"tag": b["tag"], "text": t})
    return out


def works(slug):
    return [w for w in WORKS if w["page"] == slug]


def work_lines(w):
    """Title lines (maison, campaign, type) without blank lines, typo-fixed."""
    return [typo(fix(x.strip())) for x in w["title"].split("\n") if x.strip()]


def work_desc(w):
    return typo(fix(w["description"])) if w["description"] else ""


def work_alt(w):
    lines = work_lines(w)
    return ", ".join(lines) if lines else ""


class Assets:
    """Collects every media file a build references, then copies exactly those."""

    def __init__(self, site_dir):
        self.site = Path(site_dir)
        self.used = set()

    def media(self, name):
        return MEDIA_INDEX[name]

    def picture(self, name, base, sizes, alt="", cls="", eager=False, priority=False, attrs=""):
        m = MEDIA_INDEX[name]
        files = m["files"]
        for f in files:
            self.used.add(f["jpg"]); self.used.add(f["avif"])
        avif = ", ".join(f"{base}assets/media/{f['avif']} {f['w']}w" for f in files)
        jpg = ", ".join(f"{base}assets/media/{f['jpg']} {f['w']}w" for f in files)
        first = files[0]
        load = 'loading="eager"' if eager else 'loading="lazy"'
        pr = ' fetchpriority="high"' if priority else ""
        c = f' class="{cls}"' if cls else ""
        return (f'<picture><source type="image/avif" srcset="{avif}" sizes="{sizes}">'
                f'<img{c} src="{base}assets/media/{first["jpg"]}" srcset="{jpg}" sizes="{sizes}" '
                f'width="{first["w"]}" height="{first["h"]}" alt="{esc(alt)}" {load} decoding="async"{pr}{attrs}></picture>')

    def largest(self, name, base, cap=1600):
        files = [f for f in MEDIA_INDEX[name]["files"] if f["w"] <= cap] or MEDIA_INDEX[name]["files"][:1]
        f = files[-1]
        self.used.add(f["jpg"]); self.used.add(f["avif"])
        return f"{base}assets/media/{f['jpg']}", f"{base}assets/media/{f['avif']}"

    def file(self, rel):
        self.used.add(rel)
        return rel

    def copy(self):
        dst = self.site / "assets/media"
        dst.mkdir(parents=True, exist_ok=True)
        for rel in sorted(self.used):
            (dst / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(MEDIA / rel, dst / rel)
        return len(self.used)


def write(site, rel, text):
    p = Path(site) / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def check_no_dashes(text, where):
    bad = [c for c in ("—",) if c in text]
    assert not bad, f"em-dash in {where}"
