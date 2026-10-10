# Decisions log (V2 « Maison » and V3 « Atelier »)

Built 2026-10-08. Every fact comes from the client's live site, https://www.cobaltcreation.com,
scraped the same day (`tools/scrape.py` -> `data/works.json`, `data/pages.json`).
Nothing was taken from V1 or invented.

## Source and inventory (re-verified 2026-10-08)
- Live inventory matched the brief: nav order and labels, 14 / 20 / 14 / 22 works (70),
  56 client logos (7 x 8), book PDF 9.7 MB, autoplay retail film, YouTube film `PG_bCMPUA3M`,
  12 people in 5 groups, footer address, phone, email and hours.
- Banner slides per page were read from the rendered slideshow (Wix only ships slide 1 in the HTML).
  Home: 3, Ateliers signatures: 2, Animations retail: 3, Atelier parisien: 3, Studio graphique: 3.
- The banner sources are wide panoramic crops (up to 10071 x 2146); some are only 1711 x 462.
  V2's taller banner (about 61 vh at 1440 x 900) therefore upscales those two by about 12 %.

## Copy
- Live text is used verbatim. Wix splits paragraphs into one line per `<p>`; lines were re-joined
  into paragraphs. Straight apostrophes became typographic ones (’). No words changed except:
  - « Dolce & Gabanna » -> « Dolce & Gabbana » (retail caption)
  - « La feuille l'or » -> « La feuille d'or » (Ateliers signatures)
  - « magnifie et créé des objets » -> « crée »
  - « Nos créatifs vous accompagne » -> « accompagnent »
  - « des cadeaux d'exceptions » -> « d'exception »
- Not changed, flagged for the client:
  - Juliette Leroux's address is published as `jderoux@cobaltcreation.com` (probably a typo for
    `jleroux@`, but unverifiable). Published exactly as live.
  - The privacy policy (copied verbatim, legal text) lists « 82, Avenue Niel - 75017 Paris »
    while every footer says « 35, Boulevard Berthier ». It also describes analytics data and cookies
    that the new static sites do not collect or set.
  - On the live contact page, the text « contact@cobaltcreation.com » links to `info@mysite.com`
    (a Wix placeholder). The new sites link it to contact@cobaltcreation.com, the address shown.
- Left out on purpose: the long keyword list under the Studio graphique gallery (Pégase, Ciel étoilé,
  GWP...). It is SEO filler with no sentence structure; showing it would hurt the page.
- The founding claim is the live one, « depuis plus de 10 ans ». V1 says « depuis 2014 » in its
  sharing description; that year appears nowhere on the live site.
- New interface words only (no facts): « Voir les réalisations », « Fermer », « Écrivez vos initiales »,
  « Afficher la carte », « Formulaire de contact », « L’équipe », « Réalisations », form messages.

## Media
- All photography is the client's own, downloaded at original resolution from Wix and re-encoded
  (AVIF + JPEG, 800/1600 px; banners up to 2560 px).
- The 56 logos were cut out of the live logo-wall image and recoloured in CSS (ink in V2, gold in V3).
- The retail film was re-encoded to 720 p, sound removed (it plays muted on the live site): 1.0 MB.
- No paid generation. V3's leather and gold-leaf textures are generated procedurally (`tools/textures.py`).
- Fonts: Jost, Geist, Bodoni Moda, all SIL Open Font License (licence files in `assets/fonts/`).
  The live site's Brandon Grotesque and Futura are licensed to Wix and were not copied.

## Behaviour
- No cookies, no analytics, no third-party request before a click: YouTube (`youtube-nocookie.com`)
  and Google Maps load only when the visitor asks. No cookie banner is therefore needed.
- The contact form has no server: it validates, then opens the visitor's mail app with the message
  addressed to contact@cobaltcreation.com, and says so under the button. Email and message are
  required (the live form only requires email; an empty mail would be useless).
- Pages keep the live slugs; canonical tags point to www.cobaltcreation.com; every page is
  `noindex, nofollow` and robots.txt disallows everything until launch.
- Light/dark: V2 is locked light and V3 locked dark, by brand choice rather than system setting.

## Second pass (2026-10-10): motion and presentation
- **Motion engine:** GSAP 3.12.5 + ScrollTrigger, self-hosted in `assets/vendor/` (free under the GSAP
  standard licence). Used for pinning, scrubbing and the horizontal gallery; plain IntersectionObserver
  for simple reveals, with a safety sweep so a fast scroll can never leave content hidden.
- **V2 « Maison »:** full-screen banner (still the live slides, right to left, one advance every 3 s),
  manifesto lit word by word, stacking métiers, pinned horizontal works gallery, book turning in 3D,
  marquee that answers the scroll speed, mosaic wipes with photo parallax, next-rubric links,
  cross-page view transitions where supported.
- **V3 « Atelier »:** the hero is rendered live in WebGL2 (`assets/hero-gl.js`): procedural pebbled
  leather lit per pixel at the screen's own resolution, the monogram pressed into it in four finishes,
  a light that follows the pointer, a breathing camera, and a scroll story (the hide tilts back while
  the agency's three sentences arrive, as in V1). Without WebGL2 or with reduced motion, the vector
  SVG monogram is used instead. Measured 60 fps (median 16.7 ms, worst 16.8 ms) at 1440 x 900.
- **Presentation of the photographs (V3):** the client's photos are mostly white studio shots; set as
  small frames on a flat ink ground they read as stickers. They are now shown as full-bleed surfaces:
  a full-height half-screen panel for the techniques, an edge-to-edge image wall for the works, edge-to-edge
  contact sheets, captions laid over the photographs, a paper-toned viewer. The dark grounds carry a
  quiet leather grain instead of a flat colour.
- Band sentences in the V3 hero are cut from the live « Notre agence » text at their first comma,
  ending with a full stop.
- **Image sharpness:** five live banner images are small panoramic crops (as low as 1711 x 462). Full screen,
  they would be stretched up to 3.9x on a retina display. Each full-width slot now uses a live banner image
  only when it covers the box without stretching; otherwise the page's own high-resolution landscape
  photograph takes its place (the home « Édition limitée - peinture » slide shows the full 3056 px Lalique
  photograph it was cropped from). Panoramas get derivatives tall enough for a full-height hero, and `sizes`
  states their real rendered width under `object-fit: cover`, so browsers fetch a sharp file.
