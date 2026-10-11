#!/usr/bin/env python3
"""Build V2 « Maison » into site-v2/ from data/*.json.

The client's live site, every feature kept, staged as a scroll-driven experience:
full-screen auto-sliding banner (live cadence, right to left), word-lit manifesto,
stacking métiers, pinned horizontal gallery, scrubbed book, velocity marquee,
wiping mosaics with parallax, next-rubric links, cross-page transitions.

    python3 tools/build_v2.py
"""
import json, shutil
import common as c
from common import esc

ROOT = c.ROOT
SITE = ROOT / "site-v2"
STAGING = "https://timoteoadrogue.github.io/cobalt-creation-site-v2/"
A = c.Assets(SITE)

TITLES = {k: c.PAGES["pages"][k]["title"] for k in c.PAGES["pages"]}
# decided before the first paint, so the opening never flashes the finished page first
PT_SNIPPET = ";try{if(sessionStorage.getItem('cc-pt')){sessionStorage.removeItem('cc-pt');if(!matchMedia('(prefers-reduced-motion: reduce)').matches)document.documentElement.classList.add('pt-in')}}catch(e){}"
INTRO_SNIPPET = ";try{if(!sessionStorage.getItem('cc-intro')&&!matchMedia('(prefers-reduced-motion: reduce)').matches)document.documentElement.classList.add('is-opening')}catch(e){}"
DESCS = {k: c.PAGES["pages"][k]["description"] for k in c.PAGES["pages"]}
LABEL = dict(c.NAV)
# Slide names as given by the client on the live home slideshow (aria-labels of its dots).
HOME_SLIDE_NAMES = ["Graphisme - gaufrage", "Édition limitée - peinture", "Artisanat feuille d’or"]
NEXT = {"creation-d-objet-unique": "ateliers-de-personnalisation", "ateliers-de-personnalisation": "design-graphique-design-papier",
        "design-graphique-design-papier": "coffrets-packaging", "coffrets-packaging": "creation-d-objet-unique"}


def base(slug):
    return "../" if slug else ""


def link(slug, target):
    if target == "":
        return "../" if slug else "./"
    return f"{base(slug)}{target}/"


def nav_items(slug, cls):
    out = []
    for target, label in c.NAV:
        cur = ' aria-current="page"' if target == slug else ""
        out.append(f'<li><a class="{cls}" href="{link(slug, target)}"{cur}>{esc(label)}</a></li>')
    return "\n".join(out)


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
<meta name="theme-color" content="#ffffff">
<meta property="og:type" content="website">
<meta property="og:locale" content="fr_FR">
<meta property="og:site_name" content="Cobalt Création">
<meta property="og:title" content="{esc(TITLES[slug])}">
<meta property="og:description" content="{esc(DESCS[slug])}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{STAGING}assets/media/{og_file}">
<link rel="icon" href="{b}assets/media/{A.file('favicon-64.png')}" type="image/png">
<link rel="apple-touch-icon" href="{b}assets/media/{A.file('apple-touch-icon.png')}">
<link rel="preload" href="{b}assets/fonts/jost.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{b}assets/site.css">
<script>document.documentElement.classList.add('js'){PT_SNIPPET}{INTRO_SNIPPET if slug == "" else ""}</script>
<script src="{b}assets/vendor/gsap.min.js" defer></script>
<script src="{b}assets/vendor/ScrollTrigger.min.js" defer></script>
<script src="{b}assets/vendor/lenis.min.js" defer></script>
<script src="{b}assets/site.js" defer></script>
</head>"""


def header(slug, over_hero):
    b = base(slug)
    cls = "hd is-over" if over_hero else "hd"
    return f"""<header class="{cls}" data-header>
  <a class="hd__logo" href="{link(slug, '')}" aria-label="Cobalt Création, accueil">
    <img class="hd__logo-ink" src="{b}assets/media/{A.file('logo-cobalt.png')}" width="653" height="337" alt="Cobalt Création">
    <img class="hd__logo-cream" src="{b}assets/media/{A.file('logo-cobalt-creme.png')}" width="653" height="337" alt="" aria-hidden="true">
  </a>
  <nav class="hd__nav" aria-label="Navigation principale">
    <ul class="hd__list">
{nav_items(slug, "")}
    </ul>
  </nav>
  <button class="hd__menu" type="button" aria-expanded="false" aria-controls="menu"><span class="hd__burger" aria-hidden="true"></span><span data-menu-label>Menu</span></button>
</header>
<div class="menu" id="menu" data-menu data-lenis-prevent>
  <ul>
{nav_items(slug, "menu__link")}
  </ul>
  <div class="menu__foot">
    <p>{esc(c.ADDRESS_LINE)}<br><a href="tel:{c.tel(c.PHONE)}">{esc(c.PHONE)}</a><br><a href="mailto:{c.EMAIL}">{c.EMAIL}</a></p>
  </div>
</div>"""


def contact_band(slug):
    return f"""<section class="callout" aria-labelledby="callout-t">
  <div class="wrap" data-end-in>
    <a class="callout__big" href="{link(slug, 'contact-feedback')}" id="callout-t"><span class="split">Nous contacter</span><span class="callout__arrow" aria-hidden="true">&rarr;</span></a>
    <p class="callout__ways"><a href="tel:{c.tel(c.PHONE)}">{esc(c.PHONE)}</a><a href="mailto:{c.EMAIL}">{c.EMAIL}</a></p>
  </div>
</section>"""


def footer(slug):
    b = base(slug)
    return f"""<footer class="ft">
  <div class="wrap ft__in">
    <img src="{b}assets/media/logo-cobalt-creme.png" width="653" height="337" alt="Cobalt Création" loading="lazy">
    <div>
      <p class="ft__name">Agence Cobalt Création</p>
      <p class="ft__addr"><span>{esc(c.ADDRESS_LINE)}</span><span class="ft__sep"> / </span><span><a href="tel:{c.tel(c.PHONE)}">{esc(c.PHONE)}</a></span><span class="ft__sep"> / </span><span><a href="mailto:{c.EMAIL}">{c.EMAIL}</a></span></p>
      <p>{esc(c.typo(c.HOURS))}</p>
    </div>
    <p class="ft__links"><a href="{c.INSTAGRAM}" rel="noopener" target="_blank">Instagram</a><a href="{link(slug, 'politique-de-confidentialite')}">Politique de confidentialité</a></p>
  </div>
</footer>"""


def hero(slug, title_html, sub_html, names=None):
    """Full-screen auto-sliding banner: the live slides, right to left, one advance every 3 s."""
    b = base(slug)
    slides, dots = [], []
    banner = c.sharp_slides(slug, 1440, 900, 3)   # live slides, unless too small for full screen
    for i, n in enumerate(banner):
        pic = A.picture_wide(n, b, "100vh", alt="", eager=i < 2, priority=i == 0, cls="sl__img")
        name = f' data-name="{esc(names[i])}"' if names else ""
        slides.append(f'<div class="sl{" is-on" if i == 0 else ""}" role="group" aria-roledescription="diapositive" aria-label="{i + 1} sur {len(banner)}"{name}>{pic}</div>')
        dots.append(f'<button class="bn__dot" type="button" aria-label="Image {i + 1} sur {len(banner)}"><span></span></button>')
    caption = f'<p class="hero__name" aria-live="off"><span data-slide-name>{esc(names[0])}</span></p>' if names else ""
    intro = ""
    if slug == "":
        A.file("c-mask.png"); A.file("c-drop.png")
        intro = ' data-intro'
    return f"""<section class="hero" data-banner{intro} tabindex="0" aria-roledescription="carrousel" aria-label="Diaporama, défilement automatique toutes les 3 secondes">
  <div class="hero__slides" data-slides>{''.join(slides)}</div>
  {'<div class="hero__drop" aria-hidden="true" data-drop></div>' if slug == "" else ""}
  <div class="hero__shade" aria-hidden="true"></div>
  <div class="hero__content wrap" data-hero-content>
    {title_html}
    {sub_html}
  </div>
  <div class="hero__foot wrap">
    {caption}
    <div class="bn__ctrl">{''.join(dots)}<button class="bn__pp" type="button" aria-label="Mettre le diaporama en pause"><span></span></button></div>
  </div>
</section>"""


def lines(text):
    return f'<span class="split">{esc(text)}</span>'


def page(slug, main, body_cls, lightbox=False, over_hero=True, end=""):
    lb = ""
    if lightbox:
        lb = """<dialog class="lb" data-lightbox aria-label="Réalisation agrandie" data-lenis-prevent>
  <div class="lb__stage"><picture><source type="image/avif"><img alt=""></picture></div>
  <div class="lb__meta"><p class="lb__count" aria-live="polite"></p><h2 class="lb__t"></h2><p class="lb__s"></p><p class="lb__d"></p></div>
  <button class="lb__btn lb__prev" type="button" aria-label="Réalisation précédente">&larr;</button>
  <button class="lb__btn lb__next" type="button" aria-label="Réalisation suivante">&rarr;</button>
  <button class="lb__btn lb__close" type="button">Fermer</button>
</dialog>"""
    html = f"""{head(slug)}
<body class="{body_cls}">
<a class="skip" href="#contenu">Aller au contenu</a>
{header(slug, over_hero)}
<main id="contenu">
{main}
</main>
<div class="end" data-end>
{end}{footer(slug)}
</div>
{lb}
</body>
</html>
"""
    c.check_no_dashes(html, slug)
    c.write(SITE, (f"{slug}/" if slug else "") + "index.html", html)


def build_home():
    h = c.home()
    slug, b = "", ""
    ag = h["agence"]
    mission = ag[2]  # « Notre mission : donner de l’âme et de la couleur à vos ateliers de personnalisation, ... »
    hero_title = '<h1 class="hero__title"><span class="hero__kicker">Cobalt Création, Paris</span>' \
                 '<span class="split">Donner de l’âme <em>et de la couleur</em> à vos ateliers de personnalisation</span></h1>'
    hero_sub = f'<p class="hero__sub reveal-soft">{esc(ag[0])}</p>'
    top = hero(slug, hero_title, hero_sub, HOME_SLIDE_NAMES)

    words = " ".join(f'<span class="w">{esc(w)}</span>' for w in ag[1].split())
    manifest = f"""<section class="manifest" aria-labelledby="agence-t">
  <div class="wrap manifest__in">
    <h2 id="agence-t" class="eyebrow">{esc(h['title'])}</h2>
    <p class="manifest__lit" data-lit>{words}</p>
  </div>
</section>"""

    # the frame opens: a photograph of the client's work grows from a small frame to full screen, the mission over it
    kicker, sentence = mission.split(" : ", 1)
    sentence = sentence[0].upper() + sentence[1:]
    fw = c.works("design-graphique-design-papier")[9]          # Givenchy, Carnet (4633 x 3089)
    fl = c.work_lines(fw)
    big = esc(sentence).replace("en offrant des créations sur-mesure", "<em>en offrant des créations sur-mesure</em>", 1)
    frame = f"""<section class="frame" data-frame aria-labelledby="frame-t">
  <div class="frame__pin">
    <div class="frame__media" data-frame-media>{A.picture_wide(fw["media"], b, "100vh", alt="", cls="frame__img")}<span class="frame__shade" aria-hidden="true"></span>
      <div class="frame__text wrap">
        <h2 class="frame__k" id="frame-t">{esc(kicker)}</h2>
        <p class="frame__p split">{big}</p>
      </div>
      <p class="frame__cap wrap" aria-hidden="true">{esc(" · ".join(fl))}</p>
    </div>
  </div>
</section>"""

    cards = []
    for i, col in enumerate(h["columns"]):
        paras = "".join(f"<p>{esc(p)}</p>" for p in col["paras"])
        lead = f'<p class="card__lead">{esc(col["lead"])}</p>' if col["lead"] else ""
        lis = "".join(f"<li>{esc(x)}</li>" for x in col["bullets"])
        pic = A.picture(col["image"], b, "(max-width: 900px) 100vw, 56vw", alt="", cls="card__img")
        cards.append(f"""<article class="card" style="--i:{i}">
      <div class="card__in">
        <span class="card__veil" aria-hidden="true"></span>
        <a class="card__media" href="{link(slug, col['slug'])}" tabindex="-1" aria-hidden="true">{pic}</a>
        <div class="card__text">
          <p class="card__num" aria-hidden="true"><span>0{i + 1}</span> / 0{len(h["columns"])}</p>
          <h3 class="card__t"><a href="{link(slug, col['slug'])}">{esc(col['title'])}</a></h3>
          {paras}{lead}<ul>{lis}</ul>
          <a class="more" href="{link(slug, col['slug'])}">Voir les réalisations <span aria-hidden="true">&rarr;</span></a>
        </div>
      </div>
    </article>""")
    metiers = f"""<section class="stack" aria-label="Nos métiers">{''.join(cards)}</section>"""

    # pinned horizontal gallery: four works per rubric, in live order, linked to their page
    items = []
    for s in c.RUBRICS:
        ws = [w for w in c.works(s) if c.work_lines(w)][:3]
        for w in ws:
            n = c.works(s).index(w) + 1
            ln = c.work_lines(w)
            m = c.MEDIA_INDEX[w["media"]]
            ar = m["w"] / m["h"]
            pic = A.picture(w["media"], b, f"(max-width: 900px) 78vw, calc(62vh * {ar * 1.16:.2f})", alt=c.work_alt(w), cls="hx__img")
            items.append(f'<li class="hx__item" style="--ar:{ar:.3f}"><a href="{link(slug, s)}#piece-{n}"><span class="hx__frame">{pic}</span>'
                         f'<span class="hx__cap"><span class="hx__t">{esc(ln[0])}</span><span class="hx__s">{esc(" · ".join(ln[1:]))}</span>'
                         f'<span class="hx__r">{esc(LABEL[s])}</span></span></a></li>')
    rubric_links = "".join(f'<li><a href="{link(slug, s)}">{esc(LABEL[s])}</a></li>' for s in c.RUBRICS)
    works = f"""<section class="hx" aria-labelledby="hx-t" data-hx data-scene="cream">
  <div class="hx__pin">
    <span class="hx__ghost" aria-hidden="true" data-hx-ghost>Réalisations</span>
    <div class="hx__head wrap">
      <h2 id="hx-t" class="h-sec">Réalisations</h2>
      <ul class="hx__rubrics">{rubric_links}</ul>
    </div>
    <div class="hx__viewport"><ul class="hx__track" data-hx-track>{''.join(items)}</ul></div>
    <div class="hx__bar wrap" aria-hidden="true"><span data-hx-bar></span></div>
  </div>
</section>"""

    # the client's own book, leafed through with the scroll (pages rendered from their PDF)
    A.file("cobalt-creation-book.pdf")
    bk = json.loads((c.DATA / "book.json").read_text())
    def chapter(n):
        return ("Animations points de ventes" if 3 <= n < 20 else "Commandes spéciales" if 20 <= n < 28 else
                "Design graphique / Design papier" if 28 <= n < 43 else "Coffrets & packaging / GWP" if 43 <= n < 55 else "Le book")
    def page_img(pg, eager=False):
        fs = pg["files"]
        for f in fs:
            A.file(f["jpg"]); A.file(f["avif"])
        avif = ", ".join(f"assets/media/{f['avif']} {f['w']}w" for f in fs)
        jpg = ", ".join(f"assets/media/{f['jpg']} {f['w']}w" for f in fs)
        return (f'<picture><source type="image/avif" srcset="{avif}" sizes="(max-width: 900px) 78vw, 560px">'
                f'<img src="assets/media/{fs[0]["jpg"]}" srcset="{jpg}" sizes="(max-width: 900px) 78vw, 560px" width="{fs[0]["w"]}" height="{fs[0]["h"]}" '
                f'alt="Le book de Cobalt Création, page {pg["page"]}" loading="{"eager" if eager else "lazy"}" decoding="async"></picture>')
    leaves = []
    for k in range(0, len(bk), 2):
        front, back = bk[k], bk[k + 1]
        leaves.append(f'<div class="fb__leaf" data-chapter="{esc(chapter(bk[k + 2]["page"]) if k + 2 < len(bk) else "Le book")}">'
                      f'<div class="fb__face fb__front">{page_img(front, k == 0)}<span class="fb__sheen" aria-hidden="true"></span></div>'
                      f'<div class="fb__face fb__back">{page_img(back)}<span class="fb__sheen" aria-hidden="true"></span></div></div>')
    strip = "".join(f'<li>{page_img(pg)}</li>' for pg in bk)
    book = f"""<section class="fb" aria-labelledby="book-t" data-fb data-scene="ink">
  <div class="fb__pin">
    <div class="fb__head wrap">
      <h2 id="book-t" class="h-sec">{lines(h['book_title'])}</h2>
      <p class="fb__chapter" aria-live="off"><span data-fb-chapter>Le book</span></p>
      <div class="fb__dl"><a class="book__btn" href="assets/media/cobalt-creation-book.pdf" download="Cobalt-Creation-Book.pdf"><span>{esc(h['book_link'])}</span><span aria-hidden="true">&darr;</span></a><span class="book__meta">PDF, {c.BOOK_SIZE}</span></div>
    </div>
    <div class="fb__stage"><div class="fb__book" data-fb-book>{''.join(leaves)}</div></div>
    <ul class="fb__strip" aria-label="Pages du book">{strip}</ul>
  </div>
</section>"""

    logos = c.LOGOS
    half = len(logos) // 2

    def item(l):
        A.file(f"logos/{l['file']}")
        u = f"assets/media/logos/{l['file']}"
        return f'<div class="mq__item"><span class="logo" style="-webkit-mask-image:url({u});mask-image:url({u})"></span></div>'
    row1 = "".join(item(l) for l in logos[:half])
    row2 = "".join(item(l) for l in logos[half:])
    grid = "".join(item(l) for l in logos)
    names = "".join(f"<li>{esc(l['name'])}</li>" for l in logos)
    trust = f"""<section class="trust" aria-labelledby="trust-t" data-scene="paper">
  <div class="wrap"><h2 id="trust-t" class="h-sec trust__t">{lines(h['trust_title'])}</h2></div>
  <ul class="sr-only">{names}</ul>
  <div class="mq" aria-hidden="true" data-mq>
    <div class="mq__row"><div class="mq__track" data-dir="-1">{row1}{row1}</div></div>
    <div class="mq__row"><div class="mq__track" data-dir="1">{row2}{row2}</div></div>
  </div>
  <div class="wrap trust__grid" aria-hidden="true">{grid}</div>
</section>"""
    page(slug, top + manifest + frame + metiers + works + book + trust, "p-home", end=contact_band(slug))


def tile(w, n, b, cls):
    lines_ = c.work_lines(w)
    desc = c.work_desc(w)
    alt = c.work_alt(w) or f"Réalisation {n}"
    sizes = "(max-width: 767px) 92vw, 64vw" if cls == "s2" else "(max-width: 767px) 92vw, 32vw"
    pic = A.picture(w["media"], b, sizes, alt=alt, cls="tile__img")
    full_jpg, full_avif = A.largest(w["media"], b)
    data = json.dumps({"t": lines_[0] if lines_ else "", "s": "\n".join(lines_[1:]), "d": desc,
                       "jpg": full_jpg, "avif": full_avif, "alt": alt}, ensure_ascii=False)
    cap = ""
    if lines_ or desc:
        cap = (f'<figcaption class="tile__cap"><span class="tile__t">{esc(lines_[0] if lines_ else "")}</span>'
               f'<span class="tile__s">{esc(" · ".join(lines_[1:]))}</span><span class="tile__d">{esc(desc)}</span></figcaption>')
    return (f'<figure class="tile {cls}" id="piece-{n}" data-wipe>'
            f'<a class="tile__link" href="#piece-{n}" data-lb="{n}" data-item=\'{esc(data)}\' aria-label="Agrandir : {esc(alt)}">{pic}</a>{cap}</figure>')


def mosaic_cells(items, start, b):
    cells = []
    for i, w in enumerate(items):
        pair, first = divmod(i, 2)
        big_first = pair % 2 == 1
        cls = ("s2" if first == 0 else "s1") if big_first else ("s1" if first == 0 else "s2")
        cells.append(tile(w, start + i, b, cls))
    return cells


def build_rubric(slug):
    b = base(slug)
    items = c.works(slug)
    assert len(items) == c.RUBRIC_COUNTS[slug]
    galleries = {}
    for w in items:
        galleries.setdefault(w["gallery"], []).append(w)
    blocks, n = [], 1
    for gi in sorted(galleries):
        g = galleries[gi]
        if slug == "ateliers-de-personnalisation" and len(g) == 1:
            A.file("atelier-video-720.mp4"); A.file("atelier-video-poster.jpg")
            video = (f'<figure class="tile s1 tile--video" data-wipe><video data-autoplay muted loop playsinline preload="none" '
                     f'poster="{b}assets/media/atelier-video-poster.jpg" aria-label="Film d’atelier : gaufrage à la main"><source src="{b}assets/media/atelier-video-720.mp4" type="video/mp4"></video>'
                     f'<button class="tile__play" type="button">Lire le film</button></figure>')
            blocks.append(f'<div class="mosaic mosaic--tall">{video}{tile(g[0], n, b, "s2")}</div>')
            n += 1
            continue
        cells = mosaic_cells(g, n, b)
        if len(g) % 2 == 1:
            lone_big = (len(g) // 2) % 2 == 1
            cta = (f'<div class="tile tile--cta {"s1" if lone_big else "s2"}" data-wipe><h2 class="t-up">Nous contacter</h2>'
                   f'<p><a href="tel:{c.tel(c.PHONE)}">{esc(c.PHONE)}</a></p><p><a href="mailto:{c.EMAIL}">{c.EMAIL}</a></p></div>')
            cells.append(cta)
        blocks.append(f'<div class="mosaic">{"".join(cells)}</div>')
        n += len(g)
    film = ""
    if slug == "ateliers-de-personnalisation":
        A.file("givenchy-film-1280.jpg"); A.file("givenchy-film-1280.avif")
        film = f"""<section class="film" aria-labelledby="film-t" data-scene="ink">
  <div class="wrap">
    <div class="film__frame" data-film="{c.YOUTUBE_ID}" data-title="{esc(c.YOUTUBE_TITLE)}">
      <button class="film__btn" type="button" aria-describedby="film-n"><picture><source type="image/avif" srcset="{b}assets/media/givenchy-film-1280.avif"><img src="{b}assets/media/givenchy-film-1280.jpg" width="1280" height="720" alt="" loading="lazy" decoding="async"></picture>
        <span class="film__label"><span class="film__icon" aria-hidden="true"></span><strong id="film-t">{esc(c.YOUTUBE_TITLE)}</strong><span class="sr-only">Lire la vidéo</span></span></button>
    </div>
    <p class="film__note" id="film-n">La vidéo est hébergée par YouTube : elle ne se charge qu’au clic.</p>
  </div>
</section>"""
    h = c.heading(slug)
    title = f'<h1 class="hero__title hero__title--page">{lines(h[0])}'
    if len(h) > 1:
        title += f'<span class="hero__kicker hero__kicker--after">{esc(h[1])}</span>'
    title += "</h1>"
    intro = c.intro(slug)
    lead_words = " ".join(f'<span class="w">{esc(w)}</span>' for w in intro[0].split())
    rest = "".join(f"<p>{esc(p)}</p>" for p in intro[1:])
    nxt = NEXT[slug]
    nimg = A.picture_wide(c.sharp_slides(nxt, 1440, 900, 1)[0], b, "100vh", alt="", cls="next__img")
    main = f"""{hero(slug, title, "")}
<section class="intro">
  <div class="wrap intro__in">
    <p class="intro__lit" data-lit>{lead_words}</p>
    <div class="intro__rest" data-reveal>{rest}</div>
  </div>
</section>
<section class="works" aria-label="Réalisations" data-scene="paper">
  <div class="wrap">
    {''.join(blocks)}
  </div>
</section>
{film}
<div class="nx" data-nx data-scene="ink">
  <a class="next" href="{link(slug, nxt)}">
    <span class="next__media" aria-hidden="true" data-nx-media>{nimg}</span>
    <span class="next__k">Rubrique suivante</span>
    <span class="next__t">{esc(LABEL[nxt])}</span>
  </a>
</div>"""
    page(slug, main, "p-rubric", lightbox=True, end=contact_band(slug))


def build_contact():
    slug = "contact-feedback"
    b = base(slug)
    groups = c.team()
    gs = []
    for g in groups:
        ppl = []
        for p in g["people"]:
            ph = f'<a href="tel:{c.tel(p["phone"])}">{esc(p["phone"])}</a>' if p["phone"] else ""
            ppl.append(f'<li class="tp"><span class="tp__n">{esc(p["name"])}</span><span class="tp__r">{esc(c.typo(p["role"]))}</span>'
                       f'<span class="tp__c"><a href="mailto:{p["email"]}">{p["email"]}</a>{ph}</span></li>')
        gs.append(f'<div class="tg" data-reveal><h3 class="tg__n">{esc(g["name"])}</h3><ul class="tg__list">{"".join(ppl)}</ul></div>')
    cw = c.works("ateliers-de-personnalisation")[5]          # Guerlain, Xmas 2024, atelier retail international
    cpic = A.picture(cw["media"], b, "(max-width: 900px) 100vw, 44vw", alt=c.work_alt(cw), cls="ctx__img", eager=True, priority=True)
    street, city = c.ADDRESS_LINE.split(" - ")
    main = f"""<section class="ctx" aria-labelledby="ct-t">
  <figure class="ctx__media">{cpic}<figcaption>{esc(" · ".join(c.work_lines(cw)))}</figcaption></figure>
  <div class="ctx__body">
    <h1 id="ct-t" class="ctx__title">{lines("Nous contacter")}</h1>
    <div class="ct-grid">
      <dl class="ct-ways" data-reveal>
        <div><dt>Téléphone</dt><dd><a href="tel:{c.tel(c.PHONE)}">{esc(c.PHONE)}</a></dd></div>
        <div><dt>Email</dt><dd><a href="mailto:{c.EMAIL}">{c.EMAIL}</a></dd></div>
        <div><dt>Instagram</dt><dd><a href="{c.INSTAGRAM}" rel="noopener" target="_blank">@cobaltcreation</a></dd></div>
        <div><dt>Adresse</dt><dd>{esc(street)}<br>{esc(city)}</dd></div>
      </dl>
      <form class="form" data-mailto="{c.EMAIL}" novalidate data-reveal>
        <div class="field"><label for="f-nom">Nom</label><input id="f-nom" name="nom" autocomplete="family-name"><p class="field__err" aria-live="polite"></p></div>
        <div class="field"><label for="f-prenom">Prénom</label><input id="f-prenom" name="prenom" autocomplete="given-name"><p class="field__err" aria-live="polite"></p></div>
        <div class="field field--full"><label for="f-email">Email *</label><input id="f-email" name="email" type="email" autocomplete="email" required><p class="field__err" aria-live="polite"></p></div>
        <div class="field field--full"><label for="f-msg">Message *</label><textarea id="f-msg" name="message" required></textarea><p class="field__err" aria-live="polite"></p></div>
        <div class="form__foot"><button class="btn" type="submit">Envoyer</button><p class="form__note">En cliquant sur Envoyer, votre messagerie s’ouvre avec votre message prêt à partir vers {c.EMAIL}.</p></div>
      </form>
    </div>
  </div>
</section>
<section class="team" aria-labelledby="team-t">
  <div class="wrap">
    <h2 class="team__t" id="team-t">{lines("L’équipe")}</h2>
    {''.join(gs)}
  </div>
</section>
<section class="mapx" aria-labelledby="map-t" data-map="{c.MAPS_EMBED}">
  <div class="wrap mapx__in">
    <h2 class="mapx__k" id="map-t">Plan d’accès</h2>
    <p class="mapx__addr"><span class="split">Agence Cobalt Création</span><br><span class="split">{esc(street)}</span><br><span class="split">{esc(city)}</span></p>
    <p class="mapx__actions"><button class="lnk" type="button" data-map-load>Afficher la carte <span aria-hidden="true">&darr;</span></button><a class="lnk" href="{c.MAPS_LINK}" rel="noopener" target="_blank">Ouvrir dans Google Maps <span aria-hidden="true">&nearr;</span></a></p>
    <p class="mapx__note">La carte Google ne se charge qu’au clic.</p>
  </div>
</section>"""
    page(slug, main, "p-contact", over_hero=False)


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
            out.append(f'<h1 class="ct-title">{lines(bl["text"])}</h1>')
        elif tag in ("h2", "h3"):
            out.append(f"<{tag}>{esc(bl['text'])}</{tag}>")
        else:
            out.append(f"<p>{esc(bl['text'])}</p>")
    if in_list:
        out.append("</ul>")
    page(slug, f'<section class="legal"><div class="wrap legal__in">{"".join(out)}</div></section>', "p-legal", over_hero=False)


def main():
    if (SITE / "assets/media").exists():
        shutil.rmtree(SITE / "assets/media")
    build_home()
    for s in c.RUBRICS:
        build_rubric(s)
    build_contact()
    build_privacy()
    A.file("logo-cobalt.png"); A.file("logo-cobalt-creme.png"); A.file("cobalt-creation-book.pdf")
    n = A.copy()
    fonts = SITE / "assets/fonts"
    fonts.mkdir(parents=True, exist_ok=True)
    shutil.copy2(c.MEDIA / "fonts/jost-normal.woff2", fonts / "jost.woff2")
    shutil.copy2(c.MEDIA / "fonts/jost-italic.woff2", fonts / "jost-italic.woff2")
    shutil.copy2(c.MEDIA / "fonts/OFL-jost.txt", fonts / "OFL-jost.txt")
    vendor = SITE / "assets/vendor"
    vendor.mkdir(parents=True, exist_ok=True)
    for f in ("gsap.min.js", "ScrollTrigger.min.js", "lenis.min.js", "LICENSE-lenis.txt"):
        shutil.copy2(c.MEDIA / "vendor" / f, vendor / f)
    c.write(SITE, "robots.txt", "User-agent: *\nDisallow: /\n")
    (SITE / ".nojekyll").write_text("")
    print("v2 built,", n, "media files")


if __name__ == "__main__":
    main()
