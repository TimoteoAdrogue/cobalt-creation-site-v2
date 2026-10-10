#!/usr/bin/env python3
"""Build V3 « Atelier » into site-v3/ from data/*.json.

    python3 tools/build_v3.py
"""
import json, shutil
import common as c
from common import esc

ROOT = c.ROOT
SITE = ROOT / "site-v3"
STAGING = "https://timoteoadrogue.github.io/cobalt-creation-site-v3/"
A = c.Assets(SITE)

TITLES = {k: c.PAGES["pages"][k]["title"] for k in c.PAGES["pages"]}
DESCS = {k: c.PAGES["pages"][k]["description"] for k in c.PAGES["pages"]}
LABEL = dict(c.NAV)
NEXT = {"creation-d-objet-unique": "ateliers-de-personnalisation", "ateliers-de-personnalisation": "design-graphique-design-papier",
        "design-graphique-design-papier": "coffrets-packaging", "coffrets-packaging": "creation-d-objet-unique"}
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
<script>document.documentElement.classList.add('js')</script>
<script src="{b}assets/vendor/gsap.min.js" defer></script>
<script src="{b}assets/vendor/ScrollTrigger.min.js" defer></script>
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
<nav class="ov" id="ov" aria-label="Navigation principale" data-ov>
  <ul>{''.join(items)}</ul>
  <div class="ov__foot"><span>{esc(c.ADDRESS_LINE)}</span><a href="tel:{c.tel(c.PHONE)}">{esc(c.PHONE)}</a><a href="mailto:{c.EMAIL}">{c.EMAIL}</a><span>{esc(c.typo(c.HOURS))}</span></div>
</nav>"""


def footer(slug):
    b = base(slug)
    nav = "".join(f'<li><a href="{link(slug, t)}">{esc(l)}</a></li>' for t, l in c.NAV)
    return f"""<footer class="ft3">
  <div class="wrap">
    <div class="ft3__grid">
      <div>
        <img src="{b}assets/media/logo-cobalt-creme.png" width="653" height="337" alt="Cobalt Création" loading="lazy">
        <p class="ft3__name">Agence Cobalt Création</p>
        <p>{esc(c.ADDRESS_LINE)}<br><a href="tel:{c.tel(c.PHONE)}">{esc(c.PHONE)}</a><br><a href="mailto:{c.EMAIL}">{c.EMAIL}</a><br>{esc(c.typo(c.HOURS))}</p>
      </div>
      <ul aria-label="Pages">{nav}</ul>
      <ul aria-label="Liens"><li><a href="{c.INSTAGRAM}" rel="noopener" target="_blank">Instagram</a></li><li><a href="mailto:{c.EMAIL}">{c.EMAIL}</a></li></ul>
    </div>
    <div class="ft3__base"><span>Cobalt Création, Paris</span><a href="{link(slug, 'politique-de-confidentialite')}">Politique de confidentialité</a></div>
  </div>
</footer>"""


VIEWER = """<dialog class="vw" data-viewer aria-label="Réalisation agrandie">
  <div class="vw__stage"><picture><source type="image/avif"><img alt=""></picture></div>
  <div class="vw__meta"><p class="vw__count" aria-live="polite"></p><h2 class="vw__t"></h2><p class="vw__s"></p><p class="vw__d"></p></div>
  <button class="vw__btn vw__prev" type="button" aria-label="Réalisation précédente">&larr;</button>
  <button class="vw__btn vw__next" type="button" aria-label="Réalisation suivante">&rarr;</button>
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
    <div class="hero__light" aria-hidden="true" data-light></div>
    <div class="hero__veil" aria-hidden="true" data-veil></div>
    <div class="hero__stage" data-stage>
      <div class="mono" data-mono data-finish="foil">
        {MONO_SVG}
        <input class="mono__input" id="initiales" name="initiales" maxlength="5" autocomplete="off" autocapitalize="characters" spellcheck="false" aria-describedby="initiales-aide">
      </div>
      <div class="hero__controls" data-controls>
        <label class="mono__field" for="initiales"><span class="mono__label">Écrivez vos initiales</span><span class="mono__rule" aria-hidden="true"></span><span class="sr-only" id="initiales-aide">Trois lettres au plus. Le monogramme se met à jour pendant la saisie.</span></label>
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

    # gestes: the signature techniques, from « Nos ateliers signatures »
    techs = [w for w in c.works("creation-d-objet-unique") if c.work_lines(w)]
    media, items = [], []
    for i, w in enumerate(techs):
        alt = c.work_alt(w)
        on = ' class="is-on"' if i == 0 else ""
        media.append(f'<figure data-g="{i}"{on}>{A.picture(w["media"], b, "50vw", alt="")}</figure>')
        items.append(f"""<li class="geste{' is-on' if i == 0 else ''}" data-g="{i}">
        <div class="geste__img">{A.picture(w['media'], b, '92vw', alt=alt)}</div>
        <h3>{esc(c.work_lines(w)[0])}</h3>
        <p>{esc(c.work_desc(w))}</p>
      </li>""")
    intro_sig = c.intro("creation-d-objet-unique")[0]
    gestes = f"""<section class="sec gestes" aria-labelledby="gestes-t">
  <div class="wrap">
    <div class="sec__head" data-settle>
      <h2 id="gestes-t" class="d2 split">{esc(LABEL['creation-d-objet-unique'])}</h2>
      <p class="lede">{esc(intro_sig)}</p>
    </div>
    <div class="gestes__body">
      <div class="gestes__media" aria-hidden="true">{''.join(media)}</div>
      <div class="gestes__listwrap"><span class="gestes__line" aria-hidden="true"><span data-g-line></span></span><ul class="gestes__list">{''.join(items)}</ul></div>
    </div>
    <p class="reals__more"><a class="link" href="creation-d-objet-unique/">{esc(LABEL['creation-d-objet-unique'])} <span aria-hidden="true">&rarr;</span></a></p>
  </div>
</section>"""

    # réalisations, filter folded into the heading
    order = ["ateliers-de-personnalisation", "coffrets-packaging", "design-graphique-design-papier", "creation-d-objet-unique"]
    default = "ateliers-de-personnalisation"
    tabs = "".join(f'<button type="button" data-f="{s}" aria-pressed="{"true" if s == default else "false"}">{esc(LABEL[s])}</button>' for s in order)
    cells, n = [], 0
    for s in order:
        for w in c.works(s):
            n += 1
            hidden = "" if s == default else " hidden"
            pic = A.picture(w["media"], b, "(max-width: 767px) 46vw, 30vw", alt=c.work_alt(w) or f"Réalisation {n}")
            cells.append(f'<figure class="rl" data-p="{s}"{hidden}><a href="{link(slug, s)}#piece-{c.works(s).index(w) + 1}" data-view=\'{esc(item_data(w, b, n))}\'>{pic}</a>{caption(w)}</figure>')
    reals = f"""<section class="sec sec--deep reals" data-open aria-labelledby="reals-t">
  <div class="wrap">
    <div class="reals__head" data-settle>
      <h2 id="reals-t" class="split">Réalisations</h2>
      <div class="reals__tabs" role="group" aria-label="Choisir une rubrique">{tabs}</div>
    </div>
    <div class="reals__grid" data-reals>{''.join(cells)}</div>
    <p class="reals__more"><a class="link" data-reals-link href="{link(slug, default)}">Voir la page <span data-reals-label>{esc(LABEL[default])}</span> <span aria-hidden="true">&rarr;</span></a></p>
  </div>
</section>"""

    # maisons
    logo_items = []
    for i, l in enumerate(c.LOGOS):
        A.file("logos/" + l["file"])
        url = "assets/media/logos/" + l["file"]
        delay = (i % 7 + i // 7) * 0.32
        logo_items.append(f'<li><span class="logo" role="img" aria-label="{esc(l["name"])}" style="--d:{delay:.2f};-webkit-mask-image:url({url});mask-image:url({url})"></span></li>')
    logos = "".join(logo_items)
    maisons = f"""<section class="sec" aria-labelledby="maisons-t">
  <div class="wrap">
    <div class="sec__head"><h2 id="maisons-t" class="d2 split">{esc(h['trust_title'])}</h2></div>
    <ul class="wall" data-wall>{logos}</ul>
  </div>
</section>"""

    for f in ("book-cover-600.jpg", "book-cover-600.avif", "book-cover-1200.jpg", "book-cover-1200.avif", "cobalt-creation-book.pdf"):
        A.file(f)
    book = f"""<section class="sec sec--deep" aria-labelledby="book-t" data-open data-book3-sec>
  <div class="wrap book3">
    <div class="book3__cover" data-tilt><div class="book3__obj" data-book3><picture><source type="image/avif" srcset="assets/media/book-cover-600.avif 600w, assets/media/book-cover-1200.avif 1200w" sizes="(max-width: 900px) 80vw, 460px"><img src="assets/media/book-cover-600.jpg" srcset="assets/media/book-cover-600.jpg 600w, assets/media/book-cover-1200.jpg 1200w" sizes="(max-width: 900px) 80vw, 460px" width="600" height="600" alt="Couverture du book de Cobalt Création" loading="lazy" decoding="async"></picture><span class="book3__edge" aria-hidden="true"></span></div></div>
    <div data-settle>
      <h2 id="book-t" class="d2 split" style="margin-bottom:32px">{esc(h['book_title'])}</h2>
      <a class="btn3" href="assets/media/cobalt-creation-book.pdf" download="Cobalt-Creation-Book.pdf">{esc(h['book_link'])}</a>
      <span class="book3__meta">PDF, {c.BOOK_SIZE}</span>
    </div>
  </div>
</section>"""

    groups = c.team()
    cols = []
    for g in groups:
        lis = "".join('<li><span class="crew__n">' + esc(p["name"]) + '</span><span class="crew__r">' + esc(c.typo(p["role"])) + "</span></li>" for p in g["people"])
        cols.append(f'<div><h3>{esc(g["name"])}</h3><ul>{lis}</ul></div>')
    crew_cols = "".join(cols)
    crew = f"""<section class="sec" aria-labelledby="crew-t">
  <div class="wrap">
    <div class="sec__head"><h2 id="crew-t" class="d2 split">L’équipe</h2></div>
    <div class="crew" data-crew>{crew_cols}</div>
    <p class="reals__more"><a class="link" href="contact-feedback/">Nous contacter <span aria-hidden="true">&rarr;</span></a></p>
  </div>
</section>"""

    page(slug, hero + gestes + reals + maisons + book + crew, "p-home", viewer=True)


def build_rubric(slug):
    b = base(slug)
    items = c.works(slug)
    assert len(items) == c.RUBRIC_COUNTS[slug]
    h = c.heading(slug)
    title = f'<span class="split">{esc(h[0].capitalize())}</span>'
    if len(h) > 1:
        title += f"<em>{esc(h[1].capitalize())}</em>"
    banner = c.PAGES["pages"][slug]["banner"][0]
    fig = A.picture(banner, b, "100vw", alt="", eager=True, priority=True)
    paras = "".join(f"<p>{esc(p)}</p>" for p in c.intro(slug))
    cells = []
    for i, w in enumerate(items):
        n = i + 1
        if slug == "ateliers-de-personnalisation" and w["gallery"] == 1:
            # the live page shows its autoplay film beside this image
            A.file("atelier-video-720.mp4"); A.file("atelier-video-poster.jpg")
            cells.append(f'<figure class="cs cs--video"><div class="cs__a"><video data-autoplay muted loop playsinline preload="none" poster="{b}assets/media/atelier-video-poster.jpg" aria-label="Film d’atelier : gaufrage à la main"><source src="{b}assets/media/atelier-video-720.mp4" type="video/mp4"></video><button class="cs__play" type="button">Lire le film</button></div><figcaption><span class="cap__t">Film d’atelier</span></figcaption></figure>')
        pic = A.picture(w["media"], b, "(max-width: 767px) 46vw, 16vw", alt=c.work_alt(w) or f"Réalisation {n}")
        label = c.work_alt(w) or f"Réalisation {n}"
        cells.append(f'<figure class="cs" id="piece-{n}"><a class="cs__a" href="#piece-{n}" data-view=\'{esc(item_data(w, b, n))}\' aria-label="Agrandir : {esc(label)}">{pic}</a>{caption(w)}</figure>')
    film = ""
    if slug == "ateliers-de-personnalisation":
        A.file("givenchy-film-1280.jpg"); A.file("givenchy-film-1280.avif")
        film = f"""<section class="film3">
  <div class="wrap">
    <div class="film3__frame" data-film="{c.YOUTUBE_ID}" data-title="{esc(c.YOUTUBE_TITLE)}">
      <button class="film3__btn" type="button" aria-describedby="film-n"><picture><source type="image/avif" srcset="{b}assets/media/givenchy-film-1280.avif"><img src="{b}assets/media/givenchy-film-1280.jpg" width="1280" height="720" alt="" loading="lazy" decoding="async"></picture>
        <span class="film3__label"><span class="film3__icon" aria-hidden="true"></span><strong>{esc(c.YOUTUBE_TITLE)}</strong><span class="sr-only">Lire la vidéo</span></span></button>
    </div>
    <p class="note" id="film-n">La vidéo est hébergée par YouTube : elle ne se charge qu’au clic.</p>
  </div>
</section>"""
    main = f"""<section class="rh">
  <figure class="rh__fig" data-rh>{fig}
    <figcaption class="rh__title"><div class="wrap"><h1 class="d1">{title}</h1></div></figcaption>
  </figure>
  <div class="wrap"><div class="rh__intro" data-settle>{paras}</div></div>
</section>
<section class="sheet" aria-label="Réalisations">
  <div class="wrap"><div class="sheet__grid">{''.join(cells)}</div></div>
</section>
{film}
<a class="next3" href="{link(slug, NEXT[slug])}" data-open>
  <span class="next3__media" aria-hidden="true">{A.picture(c.PAGES["pages"][NEXT[slug]]["banner"][0], b, "100vw", alt="", cls="next3__img")}</span>
  <span class="next3__k">Rubrique suivante</span>
  <span class="next3__t">{esc(LABEL[NEXT[slug]])}</span>
</a>
<section class="sec sec--deep cta3">
  <div class="wrap" data-settle>
    <h2 class="d2 split">Nous contacter</h2>
    <div class="cta3__ways"><a href="tel:{c.tel(c.PHONE)}">{esc(c.PHONE)}</a><a href="mailto:{c.EMAIL}">{c.EMAIL}</a></div>
    <a class="link" href="{link(slug, 'contact-feedback')}">Formulaire de contact <span aria-hidden="true">&rarr;</span></a>
  </div>
</section>"""
    page(slug, main, "p-rubric", viewer=True)


def build_contact():
    slug = "contact-feedback"
    gs = []
    for g in c.team():
        ppl = "".join(
            f'<div class="p3"><p class="p3__n">{esc(p["name"])}</p><p class="p3__r">{esc(c.typo(p["role"]))}</p><a href="mailto:{p["email"]}">{p["email"]}</a>'
            + (f'<a href="tel:{c.tel(p["phone"])}">{esc(p["phone"])}</a>' if p["phone"] else "") + "</div>" for p in g["people"])
        gs.append(f'<div class="team3__g" data-settle><h2>{esc(g["name"])}</h2><div class="team3__ppl">{ppl}</div></div>')
    main = f"""<section class="ct3" aria-labelledby="ct-t">
  <div class="wrap">
    <h1 id="ct-t" class="d1 split">Nous contacter</h1>
    <div class="ct3__grid">
      <dl class="ways" data-settle>
        <div><dt>Téléphone</dt><dd><a href="tel:{c.tel(c.PHONE)}">{esc(c.PHONE)}</a></dd></div>
        <div><dt>Email</dt><dd><a href="mailto:{c.EMAIL}">{c.EMAIL}</a></dd></div>
        <div><dt>Instagram</dt><dd><a href="{c.INSTAGRAM}" rel="noopener" target="_blank">@cobaltcreation</a></dd></div>
        <div><dt>Adresse</dt><dd>{esc(c.ADDRESS_LINE)}</dd></div>
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
  </div>
</section>
<section class="sec" aria-label="L’équipe">
  <div class="wrap team3">{''.join(gs)}</div>
</section>
<section aria-label="Plan d’accès" style="padding-bottom:clamp(72px,9vw,128px)">
  <div class="wrap">
    <div class="map3" data-map="{c.MAPS_EMBED}">
      <div>
        <p class="map3__addr">Agence Cobalt Création<br>{esc(c.ADDRESS_LINE)}</p>
        <div class="map3__actions"><button class="btn3" type="button" data-map-load>Afficher la carte</button><a class="btn3" href="{c.MAPS_LINK}" rel="noopener" target="_blank">Ouvrir dans Google Maps</a></div>
        <p class="note">La carte Google ne se charge qu’au clic.</p>
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
            out.append(f'<h1 class="d1">{esc(bl["text"].capitalize())}</h1>')
        elif tag in ("h2", "h3"):
            out.append(f"<{tag}>{esc(bl['text'])}</{tag}>")
        else:
            out.append(f"<p>{esc(bl['text'])}</p>")
    if in_list:
        out.append("</ul>")
    page(slug, f'<section class="legal3"><div class="wrap"><div class="legal3__in">{"".join(out)}</div></div></section>', "p-legal")


def main():
    if (SITE / "assets/media").exists():
        shutil.rmtree(SITE / "assets/media")
    build_home()
    for s in c.RUBRICS:
        build_rubric(s)
    build_contact()
    build_privacy()
    for f in ("leather.jpg", "goldleaf.jpg", "logo-cobalt-creme.png"):
        A.file(f)
    n = A.copy()
    fonts = SITE / "assets/fonts"
    fonts.mkdir(parents=True, exist_ok=True)
    for src, dst in (("geist-normal.woff2", "geist.woff2"), ("bodonimoda-normal.woff2", "bodonimoda.woff2"),
                     ("bodonimoda-italic.woff2", "bodonimoda-italic.woff2"), ("OFL-geist.txt", "OFL-geist.txt"),
                     ("OFL-bodonimoda.txt", "OFL-bodonimoda.txt")):
        shutil.copy2(c.MEDIA / "fonts" / src, fonts / dst)
    vendor = SITE / "assets/vendor"
    vendor.mkdir(parents=True, exist_ok=True)
    for f in ("gsap.min.js", "ScrollTrigger.min.js"):
        shutil.copy2(c.MEDIA / "vendor" / f, vendor / f)
    c.write(SITE, "robots.txt", "User-agent: *\nDisallow: /\n")
    (SITE / ".nojekyll").write_text("")
    print("v3 built,", n, "media files")


if __name__ == "__main__":
    main()
