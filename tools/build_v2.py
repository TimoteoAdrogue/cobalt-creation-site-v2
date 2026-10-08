#!/usr/bin/env python3
"""Build V2 « Maison » into site-v2/ from data/*.json.

    python3 tools/build_v2.py
"""
import json, shutil
from pathlib import Path
import common as c
from common import esc

ROOT = c.ROOT
SITE = ROOT / "site-v2"
STAGING = "https://timoteoadrogue.github.io/cobalt-creation-site-v2/"
A = c.Assets(SITE)

TITLES = {k: c.PAGES["pages"][k]["title"] for k in c.PAGES["pages"]}
DESCS = {k: c.PAGES["pages"][k]["description"] for k in c.PAGES["pages"]}


def base(slug):
    return "../" if slug else ""


def home_href(slug):
    return "../" if slug else "./"


def link(slug, target):
    return home_href(slug) if target == "" else f"{base(slug)}{target}/"


def nav_items(slug, cls):
    out = []
    for target, label in c.NAV:
        cur = ' aria-current="page"' if target == slug else ""
        out.append(f'<li><a class="{cls}" href="{link(slug, target)}"{cur}>{esc(label)}</a></li>')
    return "\n".join(out)


def header(slug):
    b = base(slug)
    return f"""<header class="hd" data-header>
  <div class="hd__brand"><a href="{home_href(slug)}" aria-label="Cobalt Création, accueil"><img src="{b}assets/media/{A.file('logo-cobalt.png')}" width="653" height="337" alt="Cobalt Création"></a></div>
  <nav class="hd__nav" aria-label="Navigation principale">
    <a class="hd__mini" href="{home_href(slug)}" aria-label="Cobalt Création, accueil"><img src="{b}assets/media/logo-cobalt.png" width="653" height="337" alt=""></a>
    <ul class="hd__list">
{nav_items(slug, "")}
    </ul>
    <button class="hd__menu" type="button" aria-expanded="false" aria-controls="menu"><span class="hd__burger" aria-hidden="true"></span><span data-menu-label>Menu</span></button>
  </nav>
</header>
<div class="menu" id="menu" data-menu>
  <ul>
{nav_items(slug, "menu__link")}
  </ul>
  <div class="menu__foot">
    <p>{esc(c.ADDRESS_LINE)}<br><a href="tel:{c.tel(c.PHONE)}">{esc(c.PHONE)}</a><br><a href="mailto:{c.EMAIL}">{c.EMAIL}</a></p>
  </div>
</div>"""


def footer(slug):
    b = base(slug)
    return f"""<footer class="ft">
  <div class="wrap">
    <img src="{b}assets/media/logo-cobalt.png" width="653" height="337" alt="Cobalt Création" loading="lazy">
    <p class="ft__name">Agence Cobalt Création</p>
    <p class="ft__addr"><span>{esc(c.ADDRESS_LINE)}</span><span class="ft__sep"> / </span><span><a href="tel:{c.tel(c.PHONE)}">{esc(c.PHONE)}</a></span><span class="ft__sep"> / </span><span><a href="mailto:{c.EMAIL}">{c.EMAIL}</a></span></p>
    <p>{esc(c.typo(c.HOURS))}</p>
    <p class="ft__links"><a href="{c.INSTAGRAM}" rel="noopener" target="_blank">Instagram</a><a href="{link(slug, 'politique-de-confidentialite')}">Politique de confidentialité</a></p>
  </div>
</footer>"""


def banner(slug):
    b = base(slug)
    names = c.PAGES["pages"][slug]["banner"]
    slides, dots = [], []
    for i, n in enumerate(names):
        pic = A.picture(n, b, "100vw", alt="", eager=i < 2, priority=i == 0)
        slides.append(f'<li class="bn__slide" aria-roledescription="diapositive" aria-label="{i + 1} sur {len(names)}">{pic}</li>')
        dots.append(f'<button class="bn__dot" type="button" aria-label="Image {i + 1} sur {len(names)}"><span></span></button>')
    return f"""<section class="bn" data-banner tabindex="0" aria-roledescription="carrousel" aria-label="Diaporama, défilement automatique toutes les 3 secondes">
  <div class="bn__viewport"><ul class="bn__track">
    {''.join(slides)}
  </ul></div>
  <div class="bn__ctrl">{''.join(dots)}<button class="bn__pp" type="button" aria-label="Mettre le diaporama en pause"><span></span></button></div>
</section>"""


def head(slug, extra=""):
    b = base(slug)
    og_name = (c.PAGES["pages"][slug]["banner"] or c.PAGES["pages"][""]["banner"])[0]
    og_file = [f for f in c.MEDIA_INDEX[og_name]["files"] if f["w"] <= 1920][-1]["jpg"]
    A.file(og_file)
    url = STAGING + (f"{slug}/" if slug else "")
    canon = "https://www.cobaltcreation.com/" + slug
    return f"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(TITLES[slug])}</title>
<meta name="description" content="{esc(DESCS[slug])}">
<meta name="robots" content="noindex, nofollow">
<link rel="canonical" href="{canon}">
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
<script>document.documentElement.classList.add('js')</script>
<script src="{b}assets/site.js" defer></script>
{extra}</head>"""


def page(slug, main, body_cls, lightbox=False):
    lb = ""
    if lightbox:
        lb = """<dialog class="lb" data-lightbox aria-label="Réalisation agrandie">
  <div class="lb__stage"><picture><source type="image/avif"><img alt=""></picture></div>
  <div class="lb__meta"><p class="lb__count" aria-live="polite"></p><h2 class="lb__t"></h2><p class="lb__s"></p><p class="lb__d"></p></div>
  <button class="lb__btn lb__prev" type="button" aria-label="Réalisation précédente">&larr;</button>
  <button class="lb__btn lb__next" type="button" aria-label="Réalisation suivante">&rarr;</button>
  <button class="lb__btn lb__close" type="button">Fermer</button>
</dialog>"""
    html = f"""{head(slug)}
<body class="{body_cls}">
<a class="skip" href="#contenu">Aller au contenu</a>
{header(slug)}
<main id="contenu">
{main}
</main>
{footer(slug)}
{lb}
</body>
</html>
"""
    c.check_no_dashes(html, slug)
    c.write(SITE, (f"{slug}/" if slug else "") + "index.html", html)


def build_home():
    h = c.home()
    slug = ""
    b = ""
    cols = []
    for col in h["columns"]:
        paras = "".join(f"<p>{esc(p)}</p>" for p in col["paras"])
        lead = f'<p class="metier__lead">{esc(col["lead"])}</p>' if col["lead"] else ""
        lis = "".join(f"<li>{esc(x)}</li>" for x in col["bullets"])
        pic = A.picture(col["image"], b, "(max-width: 900px) 92vw, 30vw", alt="")
        cols.append(f"""<article class="metier" data-reveal>
      <a class="metier__media" href="{link(slug, col['slug'])}" tabindex="-1" aria-hidden="true">{pic}</a>
      <h2 class="t-up"><a href="{link(slug, col['slug'])}">{esc(col['title'])}</a></h2>
      {paras}{lead}<ul>{lis}</ul>
      <a class="metier__more" href="{link(slug, col['slug'])}" aria-label="Voir les réalisations : {esc(col['title'])}">Voir les réalisations <span aria-hidden="true">&rarr;</span></a>
    </article>""")
    ag = h["agence"]
    logos = c.LOGOS
    half = len(logos) // 2
    def item(l):
        A.file(f"logos/{l['file']}")
        return f'<div class="mq__item"><span class="logo" style="-webkit-mask-image:url(assets/media/logos/{l["file"]});mask-image:url(assets/media/logos/{l["file"]})"></span></div>'
    row1 = "".join(item(l) for l in logos[:half])
    row2 = "".join(item(l) for l in logos[half:])
    grid = "".join(item(l) for l in logos)
    names = "".join(f"<li>{esc(l['name'])}</li>" for l in logos)
    A.file("book-cover-600.jpg"); A.file("book-cover-600.avif"); A.file("book-cover-1200.jpg"); A.file("book-cover-1200.avif")
    main = f"""{banner(slug)}
<section class="agence" aria-labelledby="agence-t">
  <div class="wrap agence__in" data-reveal>
    <h1 id="agence-t" class="t-up h-page">{esc(h['title'])}</h1>
    <div class="agence__rule" aria-hidden="true"></div>
    <p class="agence__lead">{esc(ag[0])}</p>
    <p>{esc(ag[1])}</p>
    <p class="agence__mission">{esc(ag[2])}</p>
  </div>
</section>
<section class="metiers" aria-label="Nos métiers">
  <div class="wrap metiers__grid">
    {''.join(cols)}
  </div>
</section>
<section class="book" aria-labelledby="book-t">
  <div class="wrap book__in">
    <div class="book__cover" data-reveal><picture><source type="image/avif" srcset="assets/media/book-cover-600.avif 600w, assets/media/book-cover-1200.avif 1200w" sizes="(max-width: 900px) 78vw, 420px"><img src="assets/media/book-cover-600.jpg" srcset="assets/media/book-cover-600.jpg 600w, assets/media/book-cover-1200.jpg 1200w" sizes="(max-width: 900px) 78vw, 420px" width="600" height="600" alt="Couverture du book de Cobalt Création" loading="lazy" decoding="async"></picture></div>
    <div data-reveal>
      <h2 id="book-t" class="t-up h-sec">{esc(h['book_title'])}</h2>
      <a class="book__btn" href="assets/media/{A.file('cobalt-creation-book.pdf')}" download="Cobalt-Creation-Book.pdf">{esc(h['book_link'])}</a>
      <span class="book__meta">PDF, {c.BOOK_SIZE}</span>
    </div>
  </div>
</section>
<section class="trust" aria-labelledby="trust-t">
  <h2 id="trust-t" class="t-up h-sec">{esc(h['trust_title'])}</h2>
  <ul class="sr-only">{names}</ul>
  <div class="mq" aria-hidden="true">
    <div class="mq__row"><div class="mq__track">{row1}{row1}</div></div>
    <div class="mq__row"><div class="mq__track">{row2}{row2}</div></div>
  </div>
  <div class="wrap trust__grid" aria-hidden="true">{grid}</div>
</section>"""
    page(slug, main, "p-home")


def tile(w, n, b, cls):
    lines = c.work_lines(w)
    desc = c.work_desc(w)
    alt = c.work_alt(w) or f"Réalisation {n}"
    sizes = "(max-width: 767px) 92vw, 64vw" if cls == "s2" else "(max-width: 767px) 92vw, 32vw"
    pic = A.picture(w["media"], b, sizes, alt=alt)
    full_jpg, full_avif = A.largest(w["media"], b)
    data = json.dumps({"t": lines[0] if lines else "", "s": "\n".join(lines[1:]), "d": desc,
                       "jpg": full_jpg, "avif": full_avif, "alt": alt}, ensure_ascii=False)
    cap = ""
    if lines or desc:
        cap = (f'<figcaption class="tile__cap"><span class="tile__t">{esc(lines[0] if lines else "")}</span>'
               f'<span class="tile__s">{esc(" · ".join(lines[1:]))}</span><span class="tile__d">{esc(desc)}</span></figcaption>')
    return (f'<figure class="tile {cls}" id="piece-{n}" data-reveal>'
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
            # live layout: the autoplay film sits left of this single image, in a taller row
            A.file("atelier-video-720.mp4"); A.file("atelier-video-poster.jpg")
            video = (f'<figure class="tile s1 tile--video" data-reveal><video data-autoplay muted loop playsinline preload="none" '
                     f'poster="{b}assets/media/atelier-video-poster.jpg" aria-label="Film d\'atelier : gaufrage à la main"><source src="{b}assets/media/atelier-video-720.mp4" type="video/mp4"></video>'
                     f'<button class="tile__play" type="button">Lire le film</button></figure>')
            blocks.append(f'<div class="mosaic mosaic--tall">{video}{tile(g[0], n, b, "s2")}</div>')
            n += 1
            continue
        cells = mosaic_cells(g, n, b)
        if len(g) % 2 == 1:
            # a lone last image gets a contact cell beside it, so the row stays whole
            lone_big = (len(g) // 2) % 2 == 1
            cta = (f'<div class="tile tile--cta {"s1" if lone_big else "s2"}" data-reveal><h2 class="t-up">Nous contacter</h2>'
                   f'<p><a href="tel:{c.tel(c.PHONE)}">{esc(c.PHONE)}</a></p><p><a href="mailto:{c.EMAIL}">{c.EMAIL}</a></p></div>')
            cells.append(cta)
        blocks.append(f'<div class="mosaic">{"".join(cells)}</div>')
        n += len(g)
    film = ""
    if slug == "ateliers-de-personnalisation":
        A.file("givenchy-film-1280.jpg"); A.file("givenchy-film-1280.avif")
        film = f"""<section class="film" aria-labelledby="film-t">
  <div class="wrap">
    <div class="film__frame" data-film="{c.YOUTUBE_ID}" data-title="{esc(c.YOUTUBE_TITLE)}">
      <button class="film__btn" type="button" aria-describedby="film-n"><picture><source type="image/avif" srcset="{b}assets/media/givenchy-film-1280.avif"><img src="{b}assets/media/givenchy-film-1280.jpg" width="1280" height="720" alt="" loading="lazy" decoding="async"></picture>
        <span class="film__label"><span class="film__icon" aria-hidden="true"></span><strong id="film-t">{esc(c.YOUTUBE_TITLE)}</strong><span class="sr-only">Lire la vidéo</span></span></button>
    </div>
    <p class="film__note" id="film-n">La vidéo est hébergée par YouTube : elle ne se charge qu’au clic.</p>
  </div>
</section>"""
    h = c.heading(slug)
    title = "".join(f"<span>{esc(x)}</span>" for x in h)
    paras = "".join(f"<p>{esc(p)}</p>" for p in c.intro(slug))
    main = f"""{banner(slug)}
<section class="intro">
  <div class="wrap intro__in" data-reveal>
    <h1 class="t-up h-page">{title}</h1>
    {paras}
  </div>
</section>
<section class="works" aria-label="Réalisations">
  <div class="wrap">
    {''.join(blocks)}
  </div>
</section>
{film}"""
    page(slug, main, "p-rubric", lightbox=True)


def build_contact():
    slug = "contact-feedback"
    groups = c.team()
    gs = []
    for g in groups:
        ppl = []
        for p in g["people"]:
            ph = f'<a href="tel:{c.tel(p["phone"])}">{esc(p["phone"])}</a>' if p["phone"] else ""
            ppl.append(f'<div class="person"><p class="person__n">{esc(p["name"])}</p><p class="person__r">{esc(c.typo(p["role"]))}</p>'
                       f'<a href="mailto:{p["email"]}">{p["email"]}</a>{ph}</div>')
        gs.append(f'<div class="team__group" data-reveal><h2 class="t-up">{esc(g["name"])}</h2><div class="team__people">{"".join(ppl)}</div></div>')
    main = f"""<section class="ct-top" aria-labelledby="ct-t">
  <div class="wrap">
    <h1 id="ct-t" class="t-up h-page">Nous contacter</h1>
    <div class="ct-grid">
      <dl class="ct-ways">
        <div><dt>Téléphone</dt><dd><a href="tel:{c.tel(c.PHONE)}">{esc(c.PHONE)}</a></dd></div>
        <div><dt>Email</dt><dd><a href="mailto:{c.EMAIL}">{c.EMAIL}</a></dd></div>
        <div><dt>Instagram</dt><dd><a href="{c.INSTAGRAM}" rel="noopener" target="_blank">@cobaltcreation</a></dd></div>
        <div><dt>Adresse</dt><dd>{esc(c.ADDRESS_LINE)}</dd></div>
      </dl>
      <form class="form" data-mailto="{c.EMAIL}" novalidate>
        <div class="field"><label for="f-nom">Nom</label><input id="f-nom" name="nom" autocomplete="family-name"><p class="field__err" id="e-nom" aria-live="polite"></p></div>
        <div class="field"><label for="f-prenom">Prénom</label><input id="f-prenom" name="prenom" autocomplete="given-name"><p class="field__err" id="e-prenom" aria-live="polite"></p></div>
        <div class="field field--full"><label for="f-email">Email *</label><input id="f-email" name="email" type="email" autocomplete="email" required aria-describedby="e-email"><p class="field__err" id="e-email" aria-live="polite"></p></div>
        <div class="field field--full"><label for="f-msg">Message *</label><textarea id="f-msg" name="message" required aria-describedby="e-msg"></textarea><p class="field__err" id="e-msg" aria-live="polite"></p></div>
        <div class="form__foot"><button class="btn" type="submit">Envoyer</button><p class="form__note">En cliquant sur Envoyer, votre messagerie s’ouvre avec votre message prêt à partir vers {c.EMAIL}.</p></div>
      </form>
    </div>
  </div>
</section>
<section class="team" aria-label="L’équipe">
  <div class="wrap">{''.join(gs)}</div>
</section>
<section class="map" aria-label="Plan d’accès">
  <div class="wrap">
    <div class="map__frame" data-map="{c.MAPS_EMBED}">
      <div class="map__inner">
        <p class="map__addr">Agence Cobalt Création<br>{esc(c.ADDRESS_LINE)}</p>
        <div class="map__actions"><button class="btn btn--ghost" type="button" data-map-load>Afficher la carte</button><a class="btn btn--ghost" href="{c.MAPS_LINK}" rel="noopener" target="_blank">Ouvrir dans Google Maps</a></div>
        <p class="map__note">La carte Google ne se charge qu’au clic.</p>
      </div>
    </div>
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
            out.append(f'<h1 class="t-up h-page">{esc(bl["text"])}</h1>')
        elif tag in ("h2", "h3"):
            out.append(f"<{tag}>{esc(bl['text'])}</{tag}>")
        else:
            out.append(f"<p>{esc(bl['text'])}</p>")
    if in_list:
        out.append("</ul>")
    main = f'<section class="legal"><div class="wrap legal__in">{"".join(out)}</div></section>'
    page(slug, main, "p-legal")


def main():
    if (SITE / "assets/media").exists():
        shutil.rmtree(SITE / "assets/media")
    for d in ["creation-d-objet-unique", "ateliers-de-personnalisation", "coffrets-packaging",
              "design-graphique-design-papier", "contact-feedback", "politique-de-confidentialite"]:
        (SITE / d).mkdir(parents=True, exist_ok=True)
    build_home()
    for s in c.RUBRICS:
        build_rubric(s)
    build_contact()
    build_privacy()
    A.file("logo-cobalt.png"); A.file("cobalt-creation-book.pdf")
    n = A.copy()
    fonts = SITE / "assets/fonts"
    fonts.mkdir(parents=True, exist_ok=True)
    shutil.copy2(c.MEDIA / "fonts/jost-normal.woff2", fonts / "jost.woff2")
    shutil.copy2(c.MEDIA / "fonts/OFL-jost.txt", fonts / "OFL-jost.txt")
    c.write(SITE, "robots.txt", "User-agent: *\nDisallow: /\n")
    (SITE / ".nojekyll").write_text("")
    print("v2 built,", n, "media files")


if __name__ == "__main__":
    main()
