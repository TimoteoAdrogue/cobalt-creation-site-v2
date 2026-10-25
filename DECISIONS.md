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

## Third pass (2026-10-11): V2 gets ideas of its own
- **Opening (home, once per visit):** the house's own C (the logo's ink crescent and gold drop, cut from the
  logotype at 12x) frames the first banner photograph on white, then opens to full screen. Decided before the
  first paint (no flash), skipped with reduced motion.
- **The book, leafed through:** 20 pages of the client's real book (their PDF: cover, contents, the four chapter
  openers and spreads from each) turn in 3D with the scroll; the chapter name above the book follows the book's
  own titles. Phones and reduced motion get a swipeable page strip. The PDF download stays.
- **Typography:** Jost italic for the emphasis words of the main statements (same family, second voice).
- Headings split into words for reveals stay fully readable by screen readers (both V2 and V3).

## Fourth pass (2026-10-11): the pages after the hero become scenes
Feedback: the heroes were strong, but below them both sites read as ordinary pages with no transitions.
- **Both sites:** weighted smooth scrolling on mouse and trackpad (Lenis 1.1.13, MIT, self-hosted, driven by
  GSAP's clock so every scrubbed scene moves in step); touch screens keep native scrolling and reduced motion
  turns it off. The header steps aside while reading down and returns on the way up. The footer became an end
  panel that the page lifts off (only when it fits on screen), its call to contact rising out of the depth.
- **V2 « Maison »:** the hero stays in place and darkens while the manifesto slides over it like a sheet; the
  mission opens from a small frame to a full-screen photograph (the client's Givenchy notebooks, from their
  Studio graphique works); the three métiers are full-screen panels that stack, each settling back as the next
  covers it; the works gallery shows each photograph at its own proportions, sliding inside its frame, with the
  title drifting behind; the ground colour flows white → cream → ink → white between scenes; the book rises and
  comes upright; the logo rows slide in from opposite sides; the next rubric opens from a frame to full screen.
- **V3 « Atelier »:** the signature techniques hold still as an index of ten; each photograph opens from a slit
  (the cut of an engraving tool) and the last one widens over the screen before the page moves on; the logo wall
  assembles out of depth; a gold light crosses the book's cover; on rubric pages a gold light passes through the
  opening paragraph, and the next rubric is cut open by a gold line that parts like a slit.
- The mission sentence in V2 is the live one, split at its own colon into a label and a statement.

## Fifth pass (2026-10-11): the remaining plain parts
- **Page transitions (both sites, every browser):** clicking an internal link closes the page under a curtain
  (V2: ink with the house's mark; V3: a gold cut runs across and the page closes onto it), and the next page
  opens from it. Decided before the first paint from a one-time session flag; the opening is pure CSS, so it
  cannot leave a page covered if a script fails. Off with reduced motion. The Chrome-only cross-document fade
  was removed so the two never stack.
- **A "Voir" label follows the pointer over the works** (mouse and trackpad only; decorative, hidden from
  assistive technology).
- **Contact pages:** a photograph of one of the client's ateliers beside the details and the form (V2: Guerlain,
  Xmas 2024; V3: Guerlain, Xmas 2022, both from their « Animations retail » works), the team as an editorial list
  (one line per person), the address as a large band instead of a boxed panel.
- **V3 home team:** one band per group with large serif names instead of five narrow columns.
- **V2 works gallery:** three works per rubric instead of four (the horizontal run was about nine screens long).
- **Phones:** métier and technique photographs open as they arrive; photographs in the viewers open from inside
  their frame (V2) or from a slit (V3).

## Sixth pass (2026-10-25): no edge between scenes
Feedback: every section boundary showed as a line, so the pages read as a stack of slides and the transitions felt
less smooth (V3 most, V2 to a lesser degree).
- **V3:** the sections no longer carry a ground of their own. One leather ground runs the whole page; its colour flows
  from ink to deep ink as the scenes change and deepens to the end panel's colour before the page lifts off it, so no
  boundary can show. The deep sections no longer open as framed cards. The hero's lower half dissolves into the ground
  at the end of its story; the techniques photograph, once it has widened over the screen, dissolves upward into the
  ground as the page moves on (during the exit, so no empty screen follows). Each section rises in slightly behind the
  scroll and recedes (drifts up, dims) as the next one arrives. The next-rubric panel shows the page's ground too.
- **V2:** the photograph washes out to paper from the bottom up while the manifesto rises into it as a mist (eased
  ramps: a linear one shows a band where it ends); the sheet's shadow is gone. The métiers dissolve into each other
  through a soft top edge instead of sliding over as cards that shrink; the covered panel darkens and its text drifts
  away. The last métier holds, then dissolves into the cream of the works that follow (a cream run-out in the flow:
  a margin would not hold it, sticky counts the margin).
- Measured: 60 fps on both sites with wheel input (median 16.7 ms, p99 16.8 ms), all runtime and static checks pass.
