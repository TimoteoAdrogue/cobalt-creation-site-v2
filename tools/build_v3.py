#!/usr/bin/env python3
"""Build V3 « Atelier » into site-v3/ from data/*.json.

    python3 tools/build_v3.py
"""
import json, shutil
import common as c
from common import esc
from PIL import Image, ImageOps

ROOT = c.ROOT
SITE = ROOT / "site-v3"
STAGING = "https://timoteoadrogue.github.io/cobalt-creation-site-v3/"
A = c.Assets(SITE)

TITLES = {k: c.PAGES["pages"][k]["title"] for k in c.PAGES["pages"]}
DESCS = {k: c.PAGES["pages"][k]["description"] for k in c.PAGES["pages"]}
LABEL = dict(c.NAV)
NEXT = {"creation-d-objet-unique": "ateliers-de-personnalisation", "ateliers-de-personnalisation": "design-graphique-design-papier",
        "design-graphique-design-papier": "coffrets-packaging", "coffrets-packaging": "creation-d-objet-unique"}
# ---------- V3-only sharp derivatives ----------
# Cut from the client's originals in src-media/ and written only to site-v3/assets/media/v3-*. Never graded: resized,
# and cropped where a slot shows only part of a panorama. Kept between builds (re-encoding takes minutes).
V3M = SITE / "assets/media"
V3_USED = set()
Image.MAX_IMAGE_PIXELS = None


def derive(name, widths, crop=None, tag="", q=64):
    """[{w, h, jpg, avif}] for `name` resized to each width (capped at the source), optionally cropped first.
    crop = (x0, y0, x1, y1) as fractions of the original."""
    src = ROOT / "src-media" / name
    im = Image.open(src)
    W, H = im.size
    if im.getexif().get(0x0112, 1) in (5, 6, 7, 8):
        W, H = H, W
    box = (round(crop[0] * W), round(crop[1] * H), round(crop[2] * W), round(crop[3] * H)) if crop else (0, 0, W, H)
    cw, ch = box[2] - box[0], box[3] - box[1]
    stem = "v3-" + name.split("~")[0].replace("53e2f6_", "")[:12] + (f"-{tag}" if tag else "")
    out, full = [], None
    for w in sorted({min(w, cw) for w in widths}):
        h = round(ch * w / cw)
        f = {"w": w, "h": h, "jpg": f"{stem}-{w}.jpg", "avif": f"{stem}-{w}.avif"}
        if not (V3M / f["jpg"]).exists() or not (V3M / f["avif"]).exists():
            if full is None:
                full = ImageOps.exif_transpose(Image.open(src)).convert("RGB").crop(box)
            V3M.mkdir(parents=True, exist_ok=True)
            r = full.resize((w, h), Image.LANCZOS)
            r.save(V3M / f["jpg"], "JPEG", quality=84, optimize=True, progressive=True)
            r.save(V3M / f["avif"], "AVIF", quality=q, speed=5)
        V3_USED.update((f["jpg"], f["avif"]))
        out.append(f)
    return out


def pic(name, b, sizes, widths=(800, 1280, 1920, 2560), crop=None, tag="", alt="", cls="", eager=False, priority=False):
    """<picture> from V3 derivatives. `sizes` must state the real rendered width (object-fit: cover included)."""
    files = derive(name, widths, crop, tag)
    av = ", ".join(f"{b}assets/media/{f['avif']} {f['w']}w" for f in files)
    jp = ", ".join(f"{b}assets/media/{f['jpg']} {f['w']}w" for f in files)
    f0 = files[-1]
    load = 'loading="eager"' if eager else 'loading="lazy"'
    pr = ' fetchpriority="high"' if priority else ""
    k = f' class="{cls}"' if cls else ""
    return (f'<picture><source type="image/avif" srcset="{av}" sizes="{sizes}"><img{k} src="{b}assets/media/{files[0]["jpg"]}" '
            f'srcset="{jp}" sizes="{sizes}" width="{f0["w"]}" height="{f0["h"]}" alt="{esc(alt)}" {load} decoding="async"{pr}></picture>')


def cover(box_w, box_h, ar):
    """The width an image renders at under object-fit: cover in a box_w x box_h box."""
    return f"max({box_w}, calc({box_h} * {ar:.3f}))"


def ratio(name):
    m = c.MEDIA_INDEX[name]
    return m["w"] / m["h"]


def mid(i12):
    """The source file in src-media/ of a photograph, by the 12 first hex digits of its id."""
    return next(p.name for p in sorted((ROOT / "src-media").iterdir()) if i12 in p.name)


def work_of(i12):
    """The client's own work (and so its verbatim title) behind a photograph, if any."""
    return next((w for w in c.WORKS if i12 in w["media"]), None)


def src_size(name):
    im = Image.open(ROOT / "src-media" / name)
    w, h = im.size
    return (h, w) if im.getexif().get(0x0112, 1) in (5, 6, 7, 8) else (w, h)


def tone(name, crop=None):
    """'light' or 'dark' for the strips of a full-bleed photograph that the top bar sits on (its left logo, its right
    links): the bar takes ink over a light photograph, cream over a dark one. Measured once on a small copy."""
    im = ImageOps.exif_transpose(Image.open(ROOT / "src-media" / name)).convert("L")
    if crop:
        W, H = im.size
        im = im.crop((round(crop[0] * W), round(crop[1] * H), round(crop[2] * W), round(crop[3] * H)))
    im.thumbnail((400, 400))
    W, H = im.size
    out = []
    lum = lambda v: ((v / 255 + .055) / 1.055) ** 2.4 if v > 10 else v / 255 / 12.92
    ratio = lambda a, b: (max(a, b) + .05) / (min(a, b) + .05)
    # where the logo and the links fall on the photograph as it is drawn full screen (cover, 110 % tall) at 1440 x 900
    vw, vh = 1440, 990
    sc = max(vw / W, vh / H)
    fx = lambda x: (x + (W * sc - vw) / 2) / (W * sc)
    fy = lambda y: (y + 45 + (H * sc - vh) / 2) / (H * sc)
    for x0, x1 in ((fx(40), fx(190)), (fx(1100), fx(1400))):
        band = im.crop((round(x0 * W), round(fy(10) * H), round(x1 * W), round(fy(66) * H)))
        L = sum(lum(v) for v in band.getdata()) / (band.width * band.height)
        out.append("light" if ratio(L, .0348) > ratio(L, .852) else "dark")   # ink #02374F against cream #F3EEE4
    return out


def mean_colour(name, crop=None):
    """The photograph's own average colour: the ground of its frame, so a frame never shows a foreign colour."""
    im = ImageOps.exif_transpose(Image.open(ROOT / "src-media" / name)).convert("RGB")
    if crop:
        W, H = im.size
        im = im.crop((round(crop[0] * W), round(crop[1] * H), round(crop[2] * W), round(crop[3] * H)))
    im.thumbnail((64, 64))
    n = im.width * im.height
    return "#%02x%02x%02x" % tuple(round(sum(px[k] for px in im.getdata()) / n) for k in range(3))


HOLD = ' data-hold onload="var i=this;(i.decode?i.decode():Promise.resolve()).then(function(){i.dataset.ready=1},function(){i.dataset.ready=1})" onerror="this.dataset.ready=1"'


# round 2: every rubric opens on its strongest photograph at full light, never graded nor tinted:
# (source id, wide crop ~16:10, tall crop ~4:5). The previous page's « next rubric » panel shows the same frame.
OPEN = {
    "creation-d-objet-unique": ("beea44379bf7", (0, .031, 1, .969), (.33, 0, .86, 1)),          # gold-leaf coasters (live banner)
    "ateliers-de-personnalisation": ("ed1e4c8ec7b2", (0, .19, 1, .81), (.1, 0, .9, 1)),         # Givenchy, hands engraving
    "design-graphique-design-papier": ("dd7d7397eb9f", (0, .0625, 1, .9375), (.16, 0, .73, 1)),  # Guerlain, Néroli Plein Sud
    "coffrets-packaging": ("fb314fe1673a", (0, .19, 1, .81), (.1, 0, .9, 1)),                   # Martell, sunburst case
}


def opening(slug, b, cls="", eager=False):
    """The rubric's full-screen opening frame (drift slack 110 %): a wide crop for screens, a tall crop for phones."""
    i12, wide, tall = OPEN[slug]
    name = mid(i12)
    fw = derive(name, (960, 1440, 1920, 2560, 3200), wide, "w", q=60)
    ft = derive(name, (600, 900, 1200, 1600), tall, "t", q=60)
    arw, art = fw[-1]["w"] / fw[-1]["h"], ft[-1]["w"] / ft[-1]["h"]
    srcs = lambda fs, k: ", ".join(f"{b}assets/media/{f[k]} {f['w']}w" for f in fs)
    sw, st = cover("100vw", "110vh", arw), cover("100vw", "110vh", art)
    load = ('loading="eager" fetchpriority="high"' + HOLD) if eager else 'loading="lazy"'
    k = f' class="{cls}"' if cls else ""
    return (f'<picture><source media="(max-width: 767px)" type="image/avif" srcset="{srcs(ft, "avif")}" sizes="{st}">'
            f'<source media="(max-width: 767px)" srcset="{srcs(ft, "jpg")}" sizes="{st}">'
            f'<source type="image/avif" srcset="{srcs(fw, "avif")}" sizes="{sw}">'
            f'<img{k} src="{b}assets/media/{fw[1]["jpg"]}" srcset="{srcs(fw, "jpg")}" sizes="{sw}" width="{fw[-1]["w"]}" height="{fw[-1]["h"]}" alt="" {load} decoding="async"></picture>')


def opening_tone(slug):
    i12, wide, _ = OPEN[slug]
    l, r = tone(mid(i12), wide)
    return f'data-tone-l="{l}" data-tone-r="{r}" style="background-color:{mean_colour(mid(i12), wide)}"'


FINISHES = [("foil", "Marquage à chaud"), ("gravure", "Gravure"), ("emboss", "Embossage"), ("leaf", "Feuille d’or")]


def base(slug):
    return "../" if slug else ""


def link(slug, target):
    if target == "":
        return "../" if slug else "./"
    return f"{base(slug)}{target}/"


def head(slug):
    b = base(slug)
    og_name = (c.PAGES["pages"][slug]["banner"] or c.PAGES["pages"][""]["banner"])[0]
    og_file = [f for f in c.MEDIA_INDEX[og_name]["files"] if f["w"] <= 1920][-1]["jpg"]
    A.file(og_file)
    url = STAGING + (f"{slug}/" if slug else "")
    return f"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(TITLES[slug])}</title>
<meta name="description" content="{esc(DESCS[slug])}">
<meta name="robots" content="noindex, nofollow">
<link rel="canonical" href="https://www.cobaltcreation.com/{slug}">
<meta name="theme-color" content="#02374F">
<meta name="color-scheme" content="dark">
<style>html{{background:#02374F}}</style>
<meta property="og:type" content="website">
<meta property="og:locale" content="fr_FR">
<meta property="og:site_name" content="Cobalt Création">
<meta property="og:title" content="{esc(TITLES[slug])}">
<meta property="og:description" content="{esc(DESCS[slug])}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{STAGING}assets/media/{og_file}">
<link rel="icon" href="{b}assets/media/{A.file('favicon-64.png')}" type="image/png">
<link rel="apple-touch-icon" href="{b}assets/media/{A.file('apple-touch-icon.png')}">
<link rel="preload" href="{b}assets/fonts/geist.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="{b}assets/fonts/bodonimoda.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{b}assets/site.css">
<script>document.documentElement.classList.add('js');addEventListener('pagereveal',function(){{document.querySelectorAll('img[data-hold]').forEach(function(i){{if(i.complete&&i.naturalWidth)i.dataset.ready=1}})}})</script>
<script src="{b}assets/vendor/gsap.min.js" defer></script>
<script src="{b}assets/vendor/ScrollTrigger.min.js" defer></script>
<script src="{b}assets/vendor/lenis.min.js" defer></script>
{'<script src="assets/hero-gl.js" defer></script>' if slug == "" else ""}
<script src="{b}assets/site.js" defer></script>
</head>"""


def topbar(slug):
    b = base(slug)
    items = []
    for target, label in c.NAV:
        cur = ' aria-current="page"' if target == slug else ""
        items.append(f'<li><a class="ov__link" href="{link(slug, target)}"{cur}>{esc(label)}</a></li>')
    cur_ct = ' aria-current="page"' if slug == "contact-feedback" else ""
    return f"""<header class="tb" data-topbar>
  <a class="tb__logo" href="{link(slug, '')}" aria-label="Cobalt Création, accueil"><img src="{b}assets/media/{A.file('logo-cobalt-creme.png')}" width="653" height="337" alt="Cobalt Création"></a>
  <div class="tb__right">
    <a class="tb__cta" href="{link(slug, 'contact-feedback')}"{cur_ct}>Nous contacter</a>
    <button class="tb__menu" type="button" aria-expanded="false" aria-controls="ov"><span class="tb__bars" aria-hidden="true"></span><span data-menu-label>Menu</span></button>
  </div>
</header>
<nav class="ov" id="ov" aria-label="Navigation principale" data-ov data-lenis-prevent>
  <ul>{''.join(items)}</ul>
  <div class="ov__foot"><span>{esc(c.ADDRESS_LINE)}</span><a href="tel:{c.tel(c.PHONE)}">{esc(c.PHONE)}</a><a href="mailto:{c.EMAIL}">{c.EMAIL}</a><span>{esc(c.typo(c.HOURS))}</span></div>
</nav>"""


def footer(slug):
    b = base(slug)
    nav = "".join(f'<li><a href="{link(slug, t)}">{esc(l)}</a></li>' for t, l in c.NAV)
    cta = "" if slug == "contact-feedback" else f"""<div class="ft3__cta" data-end-in>
      <a class="ft3__big" href="{link(slug, 'contact-feedback')}"><span>Nous</span> <em>contacter</em></a>
      <p class="ft3__ways"><a href="tel:{c.tel(c.PHONE)}">{esc(c.PHONE)}</a><a href="mailto:{c.EMAIL}">{c.EMAIL}</a></p>
    </div>"""
    return f"""<footer class="ft3 end" data-end>
  <div class="wrap">
    {cta}
    <div class="ft3__grid">
      <div>
        <img src="{b}assets/media/logo-cobalt-creme.png" width="653" height="337" alt="Cobalt Création" loading="lazy">
        <p class="ft3__name">Agence Cobalt Création</p>
        <p>{esc(c.ADDRESS_LINE)}<br>{esc(c.typo(c.HOURS))}</p>
      </div>
      <ul aria-label="Pages">{nav}</ul>
      <ul aria-label="Liens"><li><a href="{c.INSTAGRAM}" rel="noopener" target="_blank">Instagram</a></li><li><a href="{link(slug, 'politique-de-confidentialite')}">Politique de confidentialité</a></li></ul>
    </div>
    <p class="ft3__base">Cobalt Création, Paris</p>
  </div>
</footer>"""


VIEWER = """<dialog class="vw" data-viewer aria-label="Réalisation agrandie" data-lenis-prevent>
  <div class="vw__stage"><picture><source type="image/avif"><img alt=""></picture></div>
  <div class="vw__meta"><div class="vw__nav"><button class="vw__btn vw__prev" type="button" aria-label="Réalisation précédente">&larr;</button><p class="vw__count" aria-live="polite"></p><button class="vw__btn vw__next" type="button" aria-label="Réalisation suivante">&rarr;</button></div><h2 class="vw__t"></h2><p class="vw__s"></p><p class="vw__d"></p></div>
  <button class="vw__btn vw__close" type="button">Fermer</button>
</dialog>"""


def page(slug, main, body_cls, viewer=False, pre=""):
    html = f"""{head(slug)}
<body class="{body_cls}">
<a class="skip" href="#contenu">Aller au contenu</a>
{pre}{topbar(slug)}
<main id="contenu">
{main}
</main>
{footer(slug)}
{VIEWER if viewer else ""}
</body>
</html>
"""
    c.check_no_dashes(html, slug)
    c.write(SITE, (f"{slug}/" if slug else "") + "index.html", html)


def item_data(w, b, n):
    lines = c.work_lines(w)
    full_jpg, full_avif = A.largest(w["media"], b)
    return json.dumps({"n": n, "t": lines[0] if lines else "", "s": "\n".join(lines[1:]), "d": c.work_desc(w),
                       "jpg": full_jpg, "avif": full_avif, "alt": c.work_alt(w) or f"Réalisation {n}"}, ensure_ascii=False)


def caption(w):
    lines = c.work_lines(w)
    if not lines:
        return ""
    sub = " · ".join(lines[1:])
    return f'<figcaption><span class="cap__t">{esc(lines[0])}</span>{f"<span class=cap__s>{esc(sub)}</span>" if sub else ""}</figcaption>'


MONO_SVG = """<svg class="mono__svg" viewBox="0 0 1200 420" aria-hidden="true" focusable="false">
  <defs>
    <linearGradient id="g-foil" gradientUnits="userSpaceOnUse" x1="-600" y1="0" x2="1800" y2="260">
      <stop offset="0" stop-color="#6f4f28"/><stop offset=".14" stop-color="#b88d58"/><stop offset=".24" stop-color="#e9cf9d"/>
      <stop offset=".3" stop-color="#fff3d6"/><stop offset=".38" stop-color="#d6b383"/><stop offset=".5" stop-color="#9a7442"/>
      <stop offset=".62" stop-color="#c9a26c"/><stop offset=".72" stop-color="#f3dfb6"/><stop offset=".84" stop-color="#b38a55"/><stop offset="1" stop-color="#7d5a2f"/>
    </linearGradient>
    <pattern id="g-hatch" patternUnits="userSpaceOnUse" width="7" height="7" patternTransform="rotate(38)"><rect width="7" height="7" fill="#022d42"/><rect width="3.5" height="7" fill="#011824"/></pattern>
    <linearGradient id="g-emboss" x1="0" y1="0" x2=".35" y2="1"><stop offset="0" stop-color="#12698e"/><stop offset=".36" stop-color="#075275"/><stop offset=".7" stop-color="#034360"/><stop offset="1" stop-color="#023650"/></linearGradient>
    <pattern id="g-leaf" patternUnits="userSpaceOnUse" width="560" height="560"><image href="assets/media/goldleaf.jpg" width="560" height="560" preserveAspectRatio="none"/></pattern>
    <filter id="f-soft" x="-5%" y="-10%" width="110%" height="120%"><feGaussianBlur stdDeviation="2.6"/></filter>
    <filter id="f-softer" x="-5%" y="-10%" width="110%" height="120%"><feGaussianBlur stdDeviation="4.2"/></filter>
  </defs>
  <g class="mono__g">
    <text class="mono__l mono__shadow" x="600" y="320" text-anchor="middle"></text>
    <text class="mono__l mono__hi" x="600" y="320" text-anchor="middle"></text>
    <text class="mono__l mono__face" x="600" y="320" text-anchor="middle"></text>
  </g>
</svg>"""


def build_home():
    slug, b = "", ""
    h = c.home()
    ag = h["agence"]
    # The three sentences that arrive while the hero is pinned, taken from the live « Notre agence » text.
    band_texts = [ag[0], ag[1].split(",")[0] + ".", ag[2].split(",")[0] + "."]
    bands = "".join(f'<p class="band" data-band="{i}">{esc(t)}</p>' for i, t in enumerate(band_texts))
    finish_btns = "".join(
        f'<button type="button" data-finish="{k}" aria-pressed="{"true" if k == "foil" else "false"}">{esc(label)}</button>' for k, label in FINISHES)
    A.file("goldleaf.jpg")
    hero = f"""<section class="hero-wrap" data-hero-wrap aria-labelledby="hero-t">
  <div class="hero" data-hero>
    <div class="hero__leather" aria-hidden="true"></div>
    <canvas class="hero__gl" aria-hidden="true"></canvas>
    <div class="hero__light" aria-hidden="true" data-light></div>
    <div class="hero__veil" aria-hidden="true" data-veil></div>
    <div class="hero__stage" data-stage>
      <div class="mono" data-mono data-finish="foil">
        {MONO_SVG}
        <input class="mono__input" id="initiales" name="initiales" maxlength="5" autocomplete="off" autocapitalize="characters" spellcheck="false" aria-describedby="initiales-aide">
      </div>
      <div class="hero__controls" data-controls>
        <label class="mono__field" for="initiales"><span class="mono__label">Écrivez vos initiales</span><span class="mono__slots" aria-hidden="true" data-slots><i></i><i></i><i></i></span><span class="sr-only" id="initiales-aide">Trois lettres au plus. Le monogramme se met à jour pendant la saisie.</span></label>
        <div class="finish" role="group" aria-label="Finition du monogramme">{finish_btns}</div>
      </div>
    </div>
    <div class="bands" data-bands>{bands}</div>
    <div class="hero__foot" data-hero-foot>
      <div class="hero__copy">
        <h1 id="hero-t">Ateliers de personnalisation sur-mesure</h1>
      </div>
      <a class="link" href="contact-feedback/">Nous contacter <span aria-hidden="true">&rarr;</span></a>
    </div>
  </div>
</section>"""

    h = c.home()
    page(slug, hero + techniques() + '<div class="paper" data-paper data-tone-l="light" data-tone-r="light">' + bridge(BRIDGE_IN, "bridge--in")
         + reals() + maisons() + book() + "</div>" + bridge(BRIDGE_OUT, "bridge--out") + crew(), "p-home", viewer=True)


# ---------------------------------------------------------------- round 2: photographs by strength, frames that move
# The ten techniques are the client's, in the client's order; each is illustrated by the client's strongest photograph
# OF THAT TECHNIQUE, credited with that work's own verbatim title. (id, focal point for the crop, or "mount": the card
# contained on its own white, never enlarged)
TECH_PHOTO = [
    ("7d8c4d932316", "46% 50%"),   # La Gravure            <- Guerlain, Pièce unique - Gravure et mise en couleur or
    ("396411c5f961", "40% 50%"),   # La feuille d'or       <- Glenmorangie, Pièce unique - Gravure et feuille d'or
    ("1b5254f09cf6", "62% 50%"),   # L'illustration        <- Dessines moi un jardin, Illustration sur mesure
    ("522f2b9f472d", "50% 50%"),   # L'embossage et la dorure à chaud <- Éditions Cobalt Création, Carnet 2025
    ("2334ebd14cda", "64% 56%"),   # La peinture           <- Lalique, Édition Limitée - Peinture
    ("844fbc42bf78", "50% 50%"),   # La broderie           <- La Mer, Atelier retail - Broderie
    ("667ceae7bab3", "mount"),     # L'aérographe          <- its own card (1980 px)
    ("cfab69ee828b", "58% 50%"),   # La calligraphie       <- its own card
    ("21ebdcbfb258", "50% 40%"),   # Atelier Floral        <- Guerlain, Xmas 2024, Couronne strassée
    ("74d21afe5a7d", "50% 50%"),   # Les Ateliers Participatifs <- Guerlain, Abeille Royale, Atelier Participatif
]
BRIDGE_IN = "beea44379bf7"    # gold-leaf coasters on beige, 5178 px: the screen it covers turns from ink to paper
BRIDGE_OUT = "430ff5e51a03"   # hands painting the gold « 44 » on black, 3213 px: from paper back to ink
# home works: the strongest of each rubric first, nothing the techniques already show, no campaign images, no strips
RUN = {
    "ateliers-de-personnalisation": ["63471216a14a", "ed1e4c8ec7b2", "6cf80f2f42c2", "ee0a7756216d", "0a2355af026d", "5cfc64452c58", "7369d54d1d91"],
    "coffrets-packaging": ["fb314fe1673a", "2dc7671ed236", "e81a1d324247", "d891365d6708", "e5e0e67bc490", "126ffdf4c747", "12fe601dc645"],
    "design-graphique-design-papier": ["dd7d7397eb9f", "13d0253e40a6", "bf5377469999", "40a8eebbf9c0", "bb5da38813c2", "fc2e3c663458", "bc37da75fd60"],
}
# never a lead (photo audit: weak, a brand's campaign image, or an empty room): shown in pairs only
WEAK = {"04ea566d7594", "33b50297bcb6", "43122bdde558", "7ea76c0f7e48", "8b00aacc5f59", "b490ba684c8c", "b8a227d0afb9",
        "c43d20aaf56c", "f410312b0ce8", "1727f5903b42", "afd5abd662e7"}
BOOK_PAGES = ("hi-01", "hi-07", "hi-04", "hi-31")   # cover, then three inside pages the client prizes (no repeat of a plate)
RUN_W = (800, 1280, 1920)


def border_colour(name):
    im = ImageOps.exif_transpose(Image.open(ROOT / "src-media" / name)).convert("RGB")
    im.thumbnail((300, 300)); W, H = im.size; px = im.load()
    e = [px[x, y] for x in range(W) for y in range(H) if x < W * .04 or x > W * .96 or y < H * .04 or y > H * .96]
    import statistics   # the median: the object's dark parts touching the edge must not grey the field
    return "#%02x%02x%02x" % tuple(int(statistics.median(q[k] for q in e)) for k in range(3))


def techniques():
    techs = [w for w in c.works("creation-d-objet-unique") if c.work_lines(w)]
    assert len(techs) == len(TECH_PHOTO) == 10
    items = []
    for i, (w, (i12, fp)) in enumerate(zip(techs, TECH_PHOTO)):
        name = mid(i12)
        sw, sh = src_size(name)
        own = work_of(i12)
        credit = "" if own is w or own is None or not c.work_lines(own) else " · ".join(c.work_lines(own))
        if fp == "mount":   # contained inside a field of the photograph's own white: the card at its own size
            fig = (f'<figure class="tq__f tq__f--mount" data-flat-ok style="--mount:{border_colour(name)}">'
                   f'{pic(name, "", "(max-width: 900px) 84vw, 47vw", widths=(800, 1280, 1980), alt="")}</figure>')
        else:               # the frame is (100vw - index column) x 100vh; the image is 112 % tall (drift slack)
            sizes = f"(max-width: 900px) {cover('100vw', '62vh', sw / sh)}, {cover('58vw', '112vh', sw / sh)}"
            fig = f'<figure class="tq__f" style="--fp:{fp};background-color:{mean_colour(name)}">{pic(name, "", sizes, alt="")}</figure>'
        cr = f'<p class="tq__cr">{esc(credit)}</p>' if credit else ""
        items.append(f'<li class="tq__item" style="--row:{i + 2}" data-i="{i}">{fig}'
                     f'<h3 class="tq__n"><button type="button" data-tq-go="{i}">{esc(c.work_lines(w)[0])}</button></h3>'
                     f'<div class="tq__d"><p>{esc(c.work_desc(w))}</p>{cr}</div></li>')
    return f"""<section class="tq" aria-labelledby="tq-t" data-tq data-warm data-tone-l="dark" data-tone-r="dark">
  <div class="tq__stage" data-tq-stage>
    <header class="tq__head" data-tq-head><h2 id="tq-t" class="dc">{esc(LABEL['creation-d-objet-unique'])}</h2><p class="lede">{esc(c.intro('creation-d-objet-unique')[0])}</p></header>
    <ol class="tq__list">{''.join(items)}</ol>
    <p class="tq__more"><a class="link" href="creation-d-objet-unique/">{esc(LABEL['creation-d-objet-unique'])} <span aria-hidden="true">&rarr;</span></a></p>
  </div>
</section>"""


def bridge(i12, cls):
    name = mid(i12)
    sw, sh = src_size(name)
    l, r = tone(name)
    # the bridges dissolve into their ground by design (their last fifth is that ground): the motion gates check them
    # for loading only when they paint flat ([data-flat-ok])
    return (f'<div class="bridge {cls}" data-bridge data-warm data-tone-l="{l}" data-tone-r="{r}" aria-hidden="true"><figure class="bridge__f" data-flat-ok>'
            f'{pic(name, "", cover("100vw", "116vh", sw / sh), widths=(1280, 1920, 2560, 3200), alt="")}</figure></div>')


def run_cell(w, n, slot, b, href, anchor=False):
    """One work of a spread. Its frame never draws the photograph beyond its file at DPR 2 (--cap, drift included)."""
    sw, sh = src_size(w["media"])
    ar = sw / sh
    cap = round(min(max(RUN_W), sw) / 2.16)
    if slot == "lead":
        sizes = f"(max-width: 767px) 100vw, min(58vw, {84 * ar * 1.08:.1f}vh, {round(cap * 1.08)}px)"
    elif slot == "strip":
        sizes = f"(max-width: 767px) 100vw, min(100vw, {round(cap * 1.08)}px)"
    else:
        sizes = f"(max-width: 767px) 100vw, min(50vw, {round(cap * 1.08)}px)"
    lines = c.work_lines(w)
    cap_html = (f'<figcaption><span class="cap__t">{esc(lines[0])}</span>' if lines else "<figcaption>") \
        + (f'<span class="cap__s">{esc(" · ".join(lines[1:]))}</span>' if len(lines) > 1 else "") \
        + (f'<span class="cap__d">{esc(c.work_desc(w))}</span>' if slot == "lead" and c.work_desc(w) else "") + "</figcaption>"
    label = c.work_alt(w) or f"Réalisation {n}"
    idattr = f' id="piece-{n}"' if anchor else ""
    return (f'<figure class="rl rl--{slot}"{idattr} style="--ar:{ar:.3f};--cap:{cap}px"><a class="rl__a" style="background-color:{mean_colour(w["media"])}" href="{href}" data-view=\'{esc(item_data(w, b, n))}\' aria-label="Agrandir : {esc(label)}">'
            f'{pic(w["media"], b, sizes, widths=RUN_W, alt=label)}</a>{cap_html if lines or c.work_desc(w) else ""}</figure>')


def shape_of(w):
    sw, sh = src_size(w["media"])
    ar = sw / sh
    if ar > 2.2:
        return "s"
    # a lead gives its free columns to its caption: a work the client did not caption is never one
    return "l" if c.work_lines(w) and min(sw, sh) >= 1500 and .6 <= ar <= 1.7 and not any(k in w["media"] for k in WEAK) else "p"


def spreads(ws, b, cell, attrs=""):
    """Decided rows: a lead (left, then mirrored), a pair at one height, ... Strips get a row of their own at their
    own size. Client order is kept, except that a lead slot takes the next lead-worthy work among the next three."""
    q, rows, side, last = list(ws), [], "l", None
    while q:
        if shape_of(q[0][1]) == "s":
            n, w = q.pop(0)
            rows.append(f'<div class="sp sp--s"{attrs}>{cell(w, n, "strip")}</div>')
            last = "strip"
            continue
        j = next((k for k in range(min(3, len(q))) if shape_of(q[k][1]) == "l"), None) if last != "lead" else None
        if j is not None:
            n, w = q.pop(j)
            rows.append(f'<div class="sp sp--{side}"{attrs}>{cell(w, n, "lead")}</div>')
            side, last = ("r" if side == "l" else "l"), "lead"
            continue
        two = [q.pop(0)]
        if q and shape_of(q[0][1]) != "s":
            two.append(q.pop(0))
        tot = sum(src_size(w["media"])[0] / src_size(w["media"])[1] for _, w in two)
        rows.append(f'<div class="sp sp--p"{attrs} style="--sum:{tot:.3f}">{"".join(cell(w, n, "pair") for n, w in two)}</div>')
        last = "pair"
    return "".join(rows)


def reals():
    order = list(RUN)
    default = order[0]
    tabs = "".join(f'<button type="button" data-f="{s}" aria-pressed="{"true" if s == default else "false"}">{esc(LABEL[s])}</button>' for s in order)
    rows, n = [], 0
    for s in order:
        ws = [next(w for w in c.works(s) if k in w["media"]) for k in RUN[s]]
        hid = "" if s == default else " hidden"
        cell = lambda w, k, slot, s=s: run_cell(w, k, slot, "", f'{s}/#piece-{c.works(s).index(w) + 1}')
        nws = [(n + i + 1, w) for i, w in enumerate(ws)]
        n += len(ws)
        rows.append(spreads(nws, "", cell, f' data-p="{s}" data-warm{hid}'))
    return f"""<section class="reals" aria-labelledby="reals-t">
  <div class="wrap">
    <div class="reals__head">
      <h2 id="reals-t" class="dc split">Réalisations</h2>
      <div class="reals__tabs" role="group" aria-label="Choisir une rubrique">{tabs}</div>
      <p class="reals__more"><a class="link" data-reals-link href="{default}/">Voir la page <span data-reals-label>{esc(LABEL[default])}</span> <span aria-hidden="true">&rarr;</span></a></p>
    </div>
  </div>
  <div class="run run--sp" data-reals>{''.join(rows)}</div>
</section>"""


def maisons():
    """The 56 marks in ink at one optical weight on the paper lit to a gold field (ink area measured once on the
    client's own logo cut-outs). No texture, no vignette, no filter."""
    import statistics
    weights = []
    for l in c.LOGOS:
        im = Image.open(c.MEDIA / "logos" / l["file"]).convert("RGBA")
        w0, h0 = im.size
        sc = min(16 / w0, 9 / h0)                       # mask-size: contain in a 16:9 cell
        weights.append((sum(im.getchannel("A").getdata()) / 255 * sc * sc, min(16 / (w0 * sc), 9 / (h0 * sc))))
    med = statistics.median(x[0] for x in weights)
    items = []
    for i, l in enumerate(c.LOGOS):
        A.file("logos/" + l["file"])
        url = "assets/media/logos/" + l["file"]
        ink, room = weights[i]
        k = max(0.6, min((med / ink) ** 0.5, 1.18 * room))
        items.append(f'<li><span class="logo" role="img" aria-label="{esc(l["name"])}" style="--k:{k:.2f};-webkit-mask-image:url({url});mask-image:url({url})"></span></li>')
    return f"""<section class="sec maisons" aria-labelledby="maisons-t" data-maisons data-warm>
  <div class="wrap">
    <div class="sec__head"><h2 id="maisons-t" class="dc split">{esc(c.home()['trust_title'])}</h2></div>
    <div class="board" data-board><ul class="wall" data-wall>{''.join(items)}</ul></div>
  </div>
</section>"""


def book():
    """The cover and three pages of the client's book, dealt from a stack as the section rises, then still."""
    pages = []
    for k in BOOK_PAGES:
        im = None
        for w in (600, 1182):
            f = f"v3-bk-{k}-{w}"
            if not (V3M / f"{f}.avif").exists() or not (V3M / f"{f}.jpg").exists():
                im = im or Image.open(ROOT / "src-media/book" / f"{k}.jpg").convert("RGB")
                r = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
                r.save(V3M / f"{f}.jpg", "JPEG", quality=84, optimize=True, progressive=True); r.save(V3M / f"{f}.avif", "AVIF", quality=64, speed=6)
            V3_USED.update((f"{f}.jpg", f"{f}.avif"))
        alt = "Couverture du book de Cobalt Création" if k == "hi-01" else ""
        pages.append(f'<figure class="bk__p" data-bk-p><picture><source type="image/avif" srcset="assets/media/v3-bk-{k}-600.avif 600w, assets/media/v3-bk-{k}-1182.avif 1182w" sizes="(max-width: 767px) 44vw, 21vw">'
                     f'<img src="assets/media/v3-bk-{k}-600.jpg" srcset="assets/media/v3-bk-{k}-600.jpg 600w, assets/media/v3-bk-{k}-1182.jpg 1182w" sizes="(max-width: 767px) 44vw, 21vw" width="1182" height="1182" alt="{alt}" loading="lazy" decoding="async"></picture></figure>')
    A.file("cobalt-creation-book.pdf")
    h = c.home()
    return f"""<section class="bk" aria-labelledby="book-t" data-bk data-warm>
  <div class="wrap">
    <div class="bk__deal" data-bk-deal>{''.join(pages)}</div>
    <div class="bk__t"><h2 id="book-t" class="d1 split">{esc(h['book_title'])}</h2>
      <p><a class="link" href="assets/media/cobalt-creation-book.pdf" download="Cobalt-Creation-Book.pdf">{esc(h['book_link'])} <span aria-hidden="true">&darr;</span></a><span class="bk__meta">PDF, {c.BOOK_SIZE}</span></p></div>
  </div>
</section>"""


def crew():
    cols = []
    for g in c.team():
        lis = "".join('<li><span class="crew__n">' + esc(p["name"]) + '</span><span class="crew__r">' + esc(c.typo(p["role"])) + "</span></li>" for p in g["people"])
        cols.append(f'<div class="crew__g"><h3>{esc(g["name"])}</h3><ul>{lis}</ul></div>')
    return f"""<section class="sec crew-sec" aria-labelledby="crew-t" data-tone-l="dark" data-tone-r="dark">
  <div class="wrap">
    <div class="sec__head"><h2 id="crew-t" class="d1 split">L’équipe</h2></div>
    <div class="crew" data-crew>{''.join(cols)}</div>
    <p class="crew__more"><a class="link" href="contact-feedback/">Nous contacter <span aria-hidden="true">&rarr;</span></a></p>
  </div>
</section>"""


def build_rubric(slug):
    b = base(slug)
    items = c.works(slug)
    assert len(items) == c.RUBRIC_COUNTS[slug]
    h = c.heading(slug)
    title = f'<span class="split">{esc(h[0].capitalize())}</span>'
    if len(h) > 1:
        title += f"<em>{esc(h[1].capitalize())}</em>"
    ip = c.intro(slug)
    paras = f'<p class="lightp" data-lightp>{esc(ip[0])}</p>' + "".join(f"<p>{esc(p)}</p>" for p in ip[1:])
    film_cell = ""
    if slug == "ateliers-de-personnalisation":
        # the live page shows its autoplay film beside its gallery: here, the only footage of a hand at work, in a tall
        # frame beside the intro (720 px file drawn at most 360 css px: never enlarged at DPR 2)
        A.file("atelier-video-720.mp4"); A.file("atelier-video-poster.jpg")
        film_cell = (f'<figure class="rh__film"><video data-autoplay muted loop playsinline preload="none" poster="{b}assets/media/atelier-video-poster.jpg" aria-label="Film d’atelier : gaufrage à la main">'
                     f'<source src="{b}assets/media/atelier-video-720.mp4" type="video/mp4"></video><button class="cs__play" type="button">Lire le film</button><figcaption>Film d’atelier</figcaption></figure>')
    cell = lambda w, n, slot: run_cell(w, n, slot, b, f"#piece-{n}", anchor=True)
    rows = spreads([(i + 1, w) for i, w in enumerate(items)], b, cell, " data-warm")
    film = ""
    if slug == "ateliers-de-personnalisation":
        A.file("givenchy-film-1280.jpg"); A.file("givenchy-film-1280.avif")
        film = f"""<div class="film3 wrap">
    <div class="film3__frame" data-film="{c.YOUTUBE_ID}" data-title="{esc(c.YOUTUBE_TITLE)}">
      <button class="film3__btn" type="button" aria-describedby="film-n"><picture><source type="image/avif" srcset="{b}assets/media/givenchy-film-1280.avif"><img src="{b}assets/media/givenchy-film-1280.jpg" width="1280" height="720" alt="" loading="lazy" decoding="async"></picture>
        <span class="film3__label"><span class="film3__icon" aria-hidden="true"></span><strong>{esc(c.YOUTUBE_TITLE)}</strong><span class="sr-only">Lire la vidéo</span></span></button>
    </div>
    <p class="note" id="film-n">La vidéo est hébergée par YouTube : elle ne se charge qu’au clic.</p>
  </div>"""
    nxt = NEXT[slug]
    nh = c.heading(nxt)
    main = f"""<section class="rh" data-rh-wrap>
  <figure class="rh__fig" data-rh {opening_tone(slug)}><span class="rh__ph" data-drift-hold>{opening(slug, b, eager=True)}</span></figure>
  <div class="rh__sheet" data-sheet data-tone-l="dark" data-tone-r="dark">
    <div class="wrap rh__in{' rh__in--film' if film_cell else ''}">
      <h1 class="dc rh__t">{title}</h1>
      <div class="rh__intro">{paras}</div>{film_cell}
    </div>
  </div>
</section>
<section class="cat paper" aria-label="Réalisations" data-tone-l="light" data-tone-r="light">
  <div class="run run--sp run--page">{rows}</div>
  {film}
</section>
<div class="nx3" data-nx data-warm>
  <a class="next3" href="{link(slug, nxt)}" data-next>
    <span class="next3__media" aria-hidden="true" {opening_tone(nxt)}>{opening(nxt, b, cls="next3__img")}</span>
    <span class="next3__band" data-tone-l="dark" data-tone-r="dark"><span class="wrap"><span class="next3__k">Rubrique suivante</span><span class="next3__t dc"><span>{esc(nh[0].capitalize())}</span>{f"<em>{esc(nh[1].capitalize())}</em>" if len(nh) > 1 else ""}</span></span></span>
  </a>
</div>"""
    page(slug, main, "p-rubric", viewer=True)


def build_contact():
    slug = "contact-feedback"
    b = base(slug)
    gs = []
    for g in c.team():
        ppl = "".join(
            f'<li class="p3"><span class="p3__n">{esc(p["name"])}</span><span class="p3__r">{esc(c.typo(p["role"]))}</span><span class="p3__c"><a href="mailto:{p["email"]}">{p["email"]}</a>'
            + (f'<a href="tel:{c.tel(p["phone"])}">{esc(p["phone"])}</a>' if p["phone"] else "") + "</span></li>" for p in g["people"])
        gs.append(f'<div class="team3__g" data-settle><h3>{esc(g["name"])}</h3><ul class="team3__ppl">{ppl}</ul></div>')
    # an artisan engraving bottles under a loupe lamp (the live home's « Animations retail sur-mesure » image), at full
    # light: drawn at most 1485 device px from 2954
    name = mid("08cb192d62d2")
    sw, sh = src_size(name)
    cpic = pic(name, b, f"(max-width: 900px) 100vw, {cover('44vw', '110vh', sw / sh)}", widths=(800, 1280, 1920), alt="", cls="ctx3__img", eager=True, priority=True).replace(' decoding="async"', ' decoding="async"' + HOLD)
    l, r = tone(name)
    street, city = c.ADDRESS_LINE.split(" - ")
    main = f"""<section class="ctx3" aria-labelledby="ct-t">
  <figure class="ctx3__media" data-tone-l="{l}" data-tone-r="{l}" style="background-color:{mean_colour(name)}"><span class="ctx3__ph" data-drift-hold>{cpic}</span></figure>
  <div class="ctx3__body" data-tone-l="dark" data-tone-r="dark">
    <h1 id="ct-t" class="d1 split">Nous contacter</h1>
    <div class="ct3__grid">
      <dl class="ways" data-settle>
        <div><dt>Téléphone</dt><dd><a href="tel:{c.tel(c.PHONE)}">{esc(c.PHONE)}</a></dd></div>
        <div><dt>Email</dt><dd><a href="mailto:{c.EMAIL}">{c.EMAIL}</a></dd></div>
        <div><dt>Instagram</dt><dd><a href="{c.INSTAGRAM}" rel="noopener" target="_blank">@cobaltcreation</a></dd></div>
        <div><dt>Adresse</dt><dd>{esc(street)}<br>{esc(city)}</dd></div>
        <div><dt>Horaires</dt><dd>9h30 - 18h30</dd></div>
      </dl>
      <form class="f3" data-mailto="{c.EMAIL}" novalidate data-settle>
        <div class="f3__field"><label for="f-nom">Nom</label><input id="f-nom" name="nom" autocomplete="family-name"><p class="f3__err" aria-live="polite"></p></div>
        <div class="f3__field"><label for="f-prenom">Prénom</label><input id="f-prenom" name="prenom" autocomplete="given-name"><p class="f3__err" aria-live="polite"></p></div>
        <div class="f3__field f3__field--full"><label for="f-email">Email *</label><input id="f-email" name="email" type="email" autocomplete="email" required><p class="f3__err" aria-live="polite"></p></div>
        <div class="f3__field f3__field--full"><label for="f-msg">Message *</label><textarea id="f-msg" name="message" required></textarea><p class="f3__err" aria-live="polite"></p></div>
        <div class="f3__foot"><button class="btn3" type="submit">Envoyer</button><p class="f3__note">En cliquant sur Envoyer, votre messagerie s’ouvre avec votre message prêt à partir vers {c.EMAIL}.</p></div>
      </form>
    </div>
    <section class="team3-sec" aria-labelledby="team-t">
      <h2 id="team-t" class="d2 split">L’équipe</h2>
      <div class="team3">{''.join(gs)}</div>
    </section>
  </div>
</section>
<section class="map3" aria-labelledby="map-t" data-map="{c.MAPS_EMBED}" data-tone-l="dark" data-tone-r="dark">
  <div class="wrap">
    <h2 class="kicker" id="map-t">Plan d’accès</h2>
    <p class="map3__addr"><span class="split">Agence Cobalt Création</span><br><span class="split">{esc(street)}</span><br><em class="split">{esc(city)}</em></p>
    <p class="map3__actions"><button class="link" type="button" data-map-load>Afficher la carte <span aria-hidden="true">&darr;</span></button><a class="link" href="{c.MAPS_LINK}" rel="noopener" target="_blank">Ouvrir dans Google Maps <span aria-hidden="true">&nearr;</span></a></p>
    <p class="note">La carte Google ne se charge qu’au clic.</p>
  </div>
</section>"""
    page(slug, main, "p-contact")


def build_privacy():
    slug = "politique-de-confidentialite"
    out, in_list = [], False
    for bl in c.privacy():
        tag = bl["tag"]
        if tag == "li":
            if not in_list:
                out.append("<ul>"); in_list = True
            out.append(f"<li>{esc(bl['text'])}</li>")
            continue
        if in_list:
            out.append("</ul>"); in_list = False
        if tag == "h1":
            out.append(f'<h1 class="d1">{esc(bl["text"].capitalize())}</h1>')
        elif tag in ("h2", "h3"):
            out.append(f"<{tag}>{esc(bl['text'])}</{tag}>")
        else:
            out.append(f"<p>{esc(bl['text'])}</p>")
    if in_list:
        out.append("</ul>")
    page(slug, f'<section class="legal3"><div class="wrap"><div class="legal3__in">{"".join(out)}</div></div></section>', "p-legal")


def main():
    med = SITE / "assets/media"
    if med.exists():   # V3 derivatives (v3-*) are kept: re-encoding them takes minutes
        for f in med.iterdir():
            if not f.name.startswith("v3-"):
                shutil.rmtree(f) if f.is_dir() else f.unlink()
    build_home()
    for s in c.RUBRICS:
        build_rubric(s)
    build_contact()
    build_privacy()
    for f in ("leather.jpg", "leather-soft.jpg", "leather-height.png", "goldleaf.jpg", "logo-cobalt-creme.png", "logo-cobalt.png"):
        A.file(f)
    n = A.copy()
    for f in med.glob("v3-*"):
        if f.name not in V3_USED:
            f.unlink()
    n += len(V3_USED)
    fonts = SITE / "assets/fonts"
    fonts.mkdir(parents=True, exist_ok=True)
    for src, dst in (("geist-normal.woff2", "geist.woff2"), ("bodonimoda-normal.woff2", "bodonimoda.woff2"),
                     ("bodonimoda-italic.woff2", "bodonimoda-italic.woff2"), ("OFL-geist.txt", "OFL-geist.txt"),
                     ("OFL-bodonimoda.txt", "OFL-bodonimoda.txt")):
        shutil.copy2(c.MEDIA / "fonts" / src, fonts / dst)
    vendor = SITE / "assets/vendor"
    vendor.mkdir(parents=True, exist_ok=True)
    for f in ("gsap.min.js", "ScrollTrigger.min.js", "lenis.min.js", "LICENSE-lenis.txt"):
        shutil.copy2(c.MEDIA / "vendor" / f, vendor / f)
    c.write(SITE, "robots.txt", "User-agent: *\nDisallow: /\n")
    (SITE / ".nojekyll").write_text("")
    print("v3 built,", n, "media files")


if __name__ == "__main__":
    main()
