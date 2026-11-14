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
- The last two photograph edges dissolve too: on V3's home the techniques block arrives through a soft top edge, and on
  the rubric pages of both sites the closing "next rubric" photograph dissolves from the bottom as the page lifts off
  the end panel.
- Measured: 60 fps on both sites with wheel input (median 16.7 ms, p99 16.8 ms), all runtime and static checks pass.

## Seventh pass (2026-11-02 → 11-10): V2 as one designed system
Feedback: scrolling through, the specs were not that impressive; the bar is the best sites on the market. A critique
(benchmarked on Alaïa, Immersive Garden, le19M, Cartier Watches & Wonders 2026, Loewe Craft Prize) found the joins and
the composition between V2's set pieces weak. The answers follow five rules rather than patches
(full judgement: `reviews/v2/3-decisions.md`, outside the published site).
- **Three pure grounds, never mixed.** Paper `#FFF` under every photograph, cream `#F3EEE4` only for the house's own
  words on the home page (agency text, mission), ink for the book and the end. The per-scroll colour mixer is gone (its
  in-between colours were slate). A ground changes only under a full-screen photograph or through a mist, the next
  ground rising as an eased gradient. Rubric and contact pages are one paper ground. Home order: … réalisations →
  logos → book → end, so the book's ink runs into the ink end panel and is the last image before « Nous contacter ».
- **Three voices from one Jost.** The variable axis is unlocked (it was capped at 300–500). Display 500 (titles in
  uppercase +0.03 em, statements −0.02 em with their emphasis in italic 300), Text 400, Label 500 at 11 px in wide caps.
  Word-by-word lighting is gone: the agency text is its first sentence as a statement and its second as a paragraph
  (verbatim, split at its full stop). Specimen: `reviews/v2/type-specimen.png`.
- **Three movements.** Mist (grounds), Open (photographs open from a frame as they arrive, never held small), Rise
  (lines of type rise together, one after the other).
- **The caption is always there.** Every work shows its maison and its campaign · atelier line under the photograph,
  on desktop as on phones; hover only moves (the photograph settles, a gold underline draws), the description rises on
  hover. The pointer disc, ink veils, numbered « 01 / 03 » panels, outlined ghost word, progress lines, footer and
  header rules, bordered buttons and the mosaic contact tile are gone.
- **Rhythm and continuity.** Rubric galleries are paced by plates: a work given a whole screen at its own proportions,
  its caption in the margin (3–4 per page; only square or portrait sources at least 1800 px high, so never stretched).
  The métiers are one sticky photograph column beside the scrolling text, each photograph replacing the last through a
  soft edge. Home works open in place; the next-rubric photograph becomes the next page's hero; page changes are a 1 s
  paper breath with the logo; the viewer shows the object large with its caption and slides like the banner.
- **Fixed on the way:** the rubric hero painted through the top of the mosaic (it is no longer painted once covered);
  the hero's push-in and darkening ran one screen late (trigger offsets); « Nous contacter » was cut by the page edge
  (it now rises only once clear); the book's twenty face shadows formed a halo (one contact shadow, paper edges that
  thicken and thin); logos are sized to an equal optical area.
- **Images:** a few V2-only sharper cuts from the client's originals (mission photograph 3840 px, métier photographs,
  plates at 1900 px high), generated by `tools/build_v2.py` into `media/v2/`. No new photograph, no download.
- Measured: verify 0 problems (7 pages × 3 widths + reduced motion), static checks 0 failures, 0 px overflow at
  390 px, 60 fps on wheel input (median 16.7 ms, p99 16.8 ms, home and rubric pages).

## Seventh pass (2026-11-04 to 11-10): V3 « Atelier » after its hero
Feedback: the hero is the best screen; below it the specs were "not that impressive". A three-stage review (critique,
solutions, decisions: `reviews/v3/`) set five rules for the whole page, applied here.
- **Light, not colour.** The hide keeps its ink; chapters change by light. Every white photograph falls off into ink by
  *multiplying* through ink's own blues (never an alpha ramp, which turns white photos grey), then fades to the grain.
  One chapter is lit gold: the 56 maisons are pressed in ink into a gold-leaf board under a lamp (brightness rises as it
  arrives; its edge falls to near black before it meets the hide, so gold and ink never mix). The client's photographs
  are not graded.
- **Two voices.** Bodoni Moda at its automatic optical size for display (the forced display cut broke hairlines at text
  sizes), a declared text cut (opsz 14, weight 450) for names under 44 px, one chapter size (up to 152 px) for chapter
  headings and openings; Geist for every index, label and caption, one label style at 13 px in sentence case (no
  tracked caps). Specimen: `reviews/v3/type-specimen.png`.
- **Overlap, never gap; light, never lines.** The techniques heading rises into the hero's dissolving lower half, the
  works rise under the dissolving techniques photograph, photographs open from an 18 % band (never a hairline) and
  settle; no resting 1 px rule anywhere (header bar, team, footer, next-rubric frame lines all gone; the header is a
  fade).
- **The lamp.** Over each photograph a warm light follows the pointer and brings it to full light (the « Voir » disc is
  gone).
- **Sharp, whole, at three scales.** V3-only derivatives cut from the client's originals in `src-media/` by
  `tools/build_v3.py` (`v3-*` files, written only to `site-v3/assets/media/`, kept between builds), with `sizes` that
  state the real rendered width; no non-square photograph is cropped square; captions under the photographs.
- **Hero:** the story is 220 vh (was 320), the hide stays lit, the letters rise to a hallmark while the agency's three
  sentences take the centre at display size. The monogram mask uses a stamping cut of Bodoni (opsz 24) so hairlines
  carry foil, leaf or the cut; the default « C·C » now gets its true bevel (the canvas blur test no longer reads an
  empty centre pixel); wide initials shrink to fit and the mask border no longer draws lines. The field shows itself
  (three slots, a caret), the finishes are material swatches, and typing re-presses from where the letters are.
- **Techniques:** the photograph is the room (62 % of the screen, falling off under the index); the index is Geist, the
  active technique Bodoni italic, its description in one fixed slot (nothing in the list moves). Phones: the photograph
  holds at the top while the names pass beneath.
- **Works:** one editorial run per rubric on the home page (a lead and six, ratio-true, anchored to the screen's edges,
  offset), the whole catalogue in the same run on rubric pages. The filter swaps only decoded photographs and no longer
  pops the header. Home leads: Dior / Xmas Parties 2024, Guerlain / Holidays 2024, Guerlain / Néroli Plein Sud,
  La Gravure (an editorial pick among the client's own works).
- **Rubric pages** open full screen on one photograph cut to the screen's shape (ateliers signatures: the gold-leaf
  coasters slide; animations retail: the Dior counter engraver slide; studio graphique: its own Guerlain / Néroli Plein
  Sud, its portrait banner being soft full screen; atelier parisien: the Caron painting slide), title in the empty
  quarter, the intro rising over the fall-off. The next-rubric panel *is* the next page's opening frame: clicking it
  brings the panel whole and hands over without a curtain.
- **Book** at chapter size beside a larger cover with a cast shadow, a line link instead of a boxed button. **Footer:**
  the phone and email once each; the lift-off is retired (it had become invisible on the continuous ground and its edge
  cut through « Nous contacter »). **Viewer:** fades up from the page, shows the tile's photograph at once (the large
  file replaces it once decoded), arrows beside the counter. **Page transitions:** the arriving page's entrances wait for
  the lid to open.
- **Fixed:** the home page no longer pans sideways on phones (the logo wall's depth counted as overflow); the works'
  column parallax that played off screen is gone with the columns; the logo masks load only when the board is near.
- Not done this pass: the menu with each rubric's photograph (kept for later).

## Round 2 (2026-11-13 → 11-14): V3 « Atelier » after the owner's review
Feedback: below the hero V3 looked cheap and broken (plates popping one way, late and blank images, a cyan haze on
white photographs, one blue for everything, a 1.2 s curtain). Three stages under `reviews/v3/round2/` (critique,
solutions, decisions); the judge's report is `3-decisions.md`, the gates are in `tests/`, before/after frames in `ba/`.
- **Rules.** Everything the scroll drives is a pure function of the scroll position (no class toggle, no CSS transition,
  no timer), so it plays backwards exactly as forwards and a fast scroll only plays it faster. Movement is translation:
  frames that slide over each other and pictures that drift inside their frames. No photograph is graded or tinted.
- **Palette: combo A « Encre, papier, or »** (ink `#02374F`, eggshell paper `#EAE7DC`, vanilla gold field `#D8C3A5`,
  bronze `#6E5434`; body `#CFC6B8` and captions `#B8AE9F` on ink, `#5C5852` on paper). Ink stays the dominant register
  (about half the home's scroll); paper only where the client's white-ground photographs are (works, book, rubric
  catalogues), always entered and left under a full-bleed photograph so ink never ramps into paper on screen. The
  multiply fall-off (`.fo`) is deleted: it was the cyan haze.
- **Readiness.** Sections marked `data-warm` turn their images eager and decode them 1.5 screens ahead; a rubric's spreads
  decode on tab hover/focus; nothing that can come on screen is `display: none`. The first screen's photograph (rubric
  opening, contact) shows only once decoded, over a ground of its own average colour; every frame of the works and the
  techniques has its photograph's average colour as ground, so a frame never shows a foreign colour.
- **Hero:** unchanged (220 vh). Hand-off: the hallmark dissolves in place with the hide's top. Without JavaScript the
  hero shows its three sentences, as with reduced motion.
- **Techniques:** ten plates, each the client's strongest photograph of that technique under that work's own title
  (cards on their own white, never enlarged). The plates slide up over each other (each holds still for 45 % of its
  step), the picture drifts ±5 % inside its plate only while it slides, the index lights by position, the descriptions
  pass through zero.
- **Bridges:** two full-bleed photographs (the gold-leaf coasters in, « 44 » out) rise over the held stage.
- **Works (paper):** one spread per rubric, its strongest photograph first; weak or campaign pictures are never a lead;
  nothing the techniques already show. Pictures drift ±4 % in their frames, the second of a pair and each lead's
  caption pass at their own rate; the frames themselves never slit, fade or scale.
- **Maisons:** the paper eases to the gold field and back; the marks are pressed in ink and hold still, the wall drifts.
- **Book:** the four pages are dealt from the stack while the section rises, upright and still from 20 % up.
- **Team:** back on the ink after the « 44 » bridge (gold Bodoni group names, cream names); no motion beyond the type;
  it hands straight to the footer's « Nous contacter » (the empty screen between them is gone).
- **Contact:** the photograph shows once decoded; on phones the name and first name stay side by side, so the form
  reads as one block rather than a column of lines.
- **Rubric pages:** the opening photograph at full light (wide crop for screens, tall crop for phones), then an ink sheet
  with the title and intro rises over it, then the catalogue's paper rises over the held sheet; the next-rubric panel
  and footer are ink. The bar takes the ink on light grounds (measured under the logo and the links).
- **Page changes:** the JS curtain is deleted. Cross-document View Transitions (CSS only): a 380 ms cross-fade, and the
  next-rubric panel's photograph becomes the next page's opening. The ink is inlined in the head, so no white frame;
  browsers without them (Firefox) navigate plainly; reduced motion: none.
- **Viewer:** opens from its tile (FLIP, 560 ms); next/previous slide in the arrow's direction, the outgoing picture a
  decoded copy (no empty frame), the incoming one after its file is decoded; swipe follows the finger; closing fades
  the viewer to reveal the page underneath.
- **Grounds, measured** (screen centre every 40 px of scroll, 1440 × 900): home ink 47 %, paper 34 %, full-bleed
  photographs 11 %, gold 7 % (V2's home: paper 58 %). A rubric page is as light as V2's by area (création: paper 77 %);
  it stays apart by its ink opening sheet, Bodoni/Geist and vertical spreads. Switch if needed: catalogue on ink with a
  paper mount per white-ground photograph (not built).
- **Gates** (`reviews/v3/round2/tests/`, results in `judge/`): at 1440/1280/1024/390 on the home, the four rubrics and
  contact, a cold-cache wheel burst at ≥ 3,000 px/s shows 0 late, 0 blank and 0 flickering images; down/up shots at rest
  match (max 1.71 of 255, the hero excepted: its live shimmer); 0 hazy edges; steady down/up on the home matches (mean
  ≤ 1.93, p95 ≤ 4.12). Round 1's gates: `verify.mjs` 0 problems, `verify_static.py` 0 failures, fps median 16.7 ms with
  no frame over 25 ms, `scrollWidth` 390 on the 7 pages, no dead screen, copy check 0 new texts, reduced motion and
  no-JS 0 unreachable elements. Viewer and page changes: 0 empty frames.
