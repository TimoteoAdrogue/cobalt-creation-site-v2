/* Cobalt Création, V2 « Maison ».
   GSAP + ScrollTrigger (self-hosted) drive the scroll choreography; everything else is plain DOM.
   Without GSAP, or with reduced motion, every element is shown in place and nothing moves on its own. */
(() => {
  "use strict";
  const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const io = "IntersectionObserver" in window;
  const G = window.gsap && window.ScrollTrigger && !reduce ? window.gsap : null;
  if (G) G.registerPlugin(window.ScrollTrigger);
  else document.documentElement.classList.add("no-gsap");
  const desktop = () => matchMedia("(min-width: 901px)").matches;
  const root = document.documentElement;

  /* ---------- smooth scrolling (fine pointers only), on GSAP's clock so scrubbed scenes stay in step ---------- */
  let lenis = null;
  if (G && window.Lenis && matchMedia("(pointer: fine)").matches) {
    lenis = new window.Lenis({ lerp: 0.1, wheelMultiplier: 0.9 });
    lenis.on("scroll", window.ScrollTrigger.update);
    G.ticker.add((t) => lenis.raf(t * 1000));
    G.ticker.lagSmoothing(0);
  }
  const hold = (on) => { if (lenis) on ? lenis.stop() : lenis.start(); };

  /* ---------- split words for mask reveals ---------- */
  // words stay readable by screen readers (no aria-hidden); <em> survives as italic words
  const safe = (w) => w.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  $$(".split").forEach((el) => {
    const words = [];
    el.childNodes.forEach((node) => {
      const em = node.nodeType === 1 && node.tagName === "EM";
      (node.textContent || "").split(/\s+/).filter(Boolean).forEach((w) => words.push({ w, em }));
    });
    el.innerHTML = words.map((o, i) => `<span class="sw"><span class="sw__in${o.em ? " is-em" : ""}" style="--w:${i}">${safe(o.w)}</span></span>`).join(" ");
  });

  /* ---------- reveals (IntersectionObserver; also catches content jumped past) ---------- */
  const revealEls = $$("[data-reveal], [data-wipe], .split, .reveal-soft").filter((el) => !(G && desktop() && el.closest("[data-frame]")));
  if (io && !reduce) {
    const o = new IntersectionObserver((es) => {
      for (const e of es) if (e.isIntersecting || e.boundingClientRect.top <= 0) { e.target.classList.add("is-in"); o.unobserve(e.target); }
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.06 });
    revealEls.forEach((el) => o.observe(el));
    // safety sweep: a fast scroll can jump over an element without the observer ever reporting it
    const sweep = setInterval(() => {
      const left = revealEls.filter((el) => !el.classList.contains("is-in"));
      if (!left.length) return clearInterval(sweep);
      left.forEach((el) => { if (el.getBoundingClientRect().top < innerHeight) { el.classList.add("is-in"); o.unobserve(el); } });
    }, 500);
  } else revealEls.forEach((el) => el.classList.add("is-in"));

  /* ---------- header: transparent over the hero, solid after ---------- */
  const hd = $("[data-header]");
  const heroEl = $("[data-banner]");
  const afterHero = heroEl && heroEl.nextElementSibling;
  if (hd && heroEl && G && afterHero) {
    // the hero is pinned under the next sheet, so it never leaves the screen: follow the sheet instead
    window.ScrollTrigger.create({ trigger: afterHero, start: () => `top ${hd.offsetHeight}px`, end: "max",
      onEnter: () => hd.classList.remove("is-over"), onLeaveBack: () => hd.classList.add("is-over") });
  } else if (hd && heroEl && io) {
    new IntersectionObserver(([e]) => hd.classList.toggle("is-over", e.isIntersecting), { rootMargin: "-76px 0px 0px 0px", threshold: 0 }).observe(heroEl);
  } else if (hd) hd.classList.remove("is-over");
  if (hd && G) {
    window.ScrollTrigger.create({ start: 0, end: "max", onUpdate: (s) => {
      hd.classList.toggle("is-hidden", s.direction === 1 && s.scroll() > innerHeight * 0.8 && !hd.classList.contains("is-menu") && !hd.contains(document.activeElement));
    } });
    hd.addEventListener("focusin", () => hd.classList.remove("is-hidden"));
  }

  /* ---------- mobile menu ---------- */
  const menuBtn = $(".hd__menu"), menu = $("[data-menu]");
  if (menuBtn && menu) {
    const label = $("[data-menu-label]", menuBtn);
    const set = (open) => {
      menuBtn.setAttribute("aria-expanded", String(open));
      menu.classList.toggle("is-open", open);
      hd.classList.toggle("is-menu", open);
      document.documentElement.style.overflow = open ? "hidden" : "";
      hold(open);
      label.textContent = open ? "Fermer" : "Menu";
      if (open) setTimeout(() => $("a", menu)?.focus(), 60);
    };
    menuBtn.addEventListener("click", () => set(menuBtn.getAttribute("aria-expanded") !== "true"));
    document.addEventListener("keydown", (e) => { if (e.key === "Escape" && menu.classList.contains("is-open")) { set(false); menuBtn.focus(); } });
    matchMedia("(min-width: 1240px)").addEventListener("change", (m) => m.matches && set(false));
  }

  /* ---------- F2 hero banner: live slides, right to left, 2 s still + 1 s slide = 3 s per image ---------- */
  const HOLD = 2000, MOVE = 1;
  if (heroEl) {
    const slides = $$(".sl", heroEl);
    const imgs = slides.map((s) => $("img", s));
    const dots = $$(".bn__dot", heroEl);
    const pp = $(".bn__pp", heroEl);
    const nameEl = $("[data-slide-name]", heroEl);
    const n = slides.length;
    heroEl.style.setProperty("--bn-time", HOLD + "ms");
    let i = 0, timer = null, remaining = HOLD, startedAt = 0, busy = false;
    let userPaused = reduce, hovering = false, focused = false, visible = true;
    const blocked = () => userPaused || hovering || focused || !visible || document.hidden || busy || document.documentElement.classList.contains("is-opening");
    const activate = (k) => {
      dots.forEach((d, j) => { d.classList.remove("is-active"); d.setAttribute("aria-current", j === k ? "true" : "false"); });
      void heroEl.offsetWidth;
      dots[k]?.classList.add("is-active");
      const nx = imgs[(k + 1) % n]; if (nx) nx.loading = "eager";
      if (nameEl && slides[k].dataset.name) {
        nameEl.classList.add("is-swap");
        setTimeout(() => { nameEl.textContent = slides[k].dataset.name; nameEl.classList.remove("is-swap"); }, 380);
      }
      if (G) G.fromTo(imgs[k], { scale: 1.08 }, { scale: 1, duration: (HOLD / 1000) + MOVE + 1, ease: "none", overwrite: "auto" });
    };
    const clear = () => { if (timer) { clearTimeout(timer); timer = null; remaining = Math.max(0, remaining - (performance.now() - startedAt)); } };
    const schedule = () => { if (blocked() || timer || n < 2) return; startedAt = performance.now(); timer = setTimeout(() => { timer = null; go(i + 1, 1); }, remaining); };
    const sync = () => {
      heroEl.classList.toggle("is-paused", userPaused);
      heroEl.classList.toggle("is-held", !userPaused && blocked());
      if (pp) pp.setAttribute("aria-label", userPaused ? "Relancer le diaporama" : "Mettre le diaporama en pause");
      if (blocked()) clear(); else schedule();
    };
    function go(k, dir) {
      if (busy || n < 2) return;
      clear();
      const from = i, to = ((k % n) + n) % n;
      if (to === from) return;
      remaining = HOLD;
      i = to;
      const a = slides[from], b = slides[to];
      b.classList.add("is-on");
      if (G) {
        busy = true;
        // parallax slide: the new image enters from the right while the old one leaves at half speed
        G.set(b, { xPercent: 100 * dir, zIndex: 2 }); G.set(a, { zIndex: 1 });
        G.set(imgs[to], { xPercent: -50 * dir });
        G.timeline({ defaults: { duration: MOVE, ease: "power3.inOut" }, onComplete: () => {
          a.classList.remove("is-on"); G.set([a, imgs[from]], { xPercent: 0 }); busy = false; schedule();
        } })
          .to(a, { xPercent: -30 * dir }, 0)
          .to(b, { xPercent: 0 }, 0)
          .to(imgs[to], { xPercent: 0 }, 0);
      } else { a.classList.remove("is-on"); schedule(); }
      activate(to);
    }
    if (n < 2) $(".bn__ctrl", heroEl)?.remove();
    dots.forEach((d, k) => d.addEventListener("click", () => go(k, k > i ? 1 : -1)));
    pp?.addEventListener("click", () => { userPaused = !userPaused; sync(); });
    heroEl.addEventListener("pointerenter", (e) => { if (e.pointerType === "mouse") { hovering = true; sync(); } });
    heroEl.addEventListener("pointerleave", () => { hovering = false; sync(); });
    heroEl.addEventListener("focusin", (e) => { focused = e.target.matches(":focus-visible"); sync(); });
    heroEl.addEventListener("focusout", (e) => { if (!heroEl.contains(e.relatedTarget)) { focused = false; sync(); } });
    heroEl.addEventListener("keydown", (e) => {
      if (e.key === "ArrowRight") { e.preventDefault(); go(i + 1, 1); }
      if (e.key === "ArrowLeft") { e.preventDefault(); go(i - 1, -1); }
    });
    document.addEventListener("visibilitychange", sync);
    if (io) new IntersectionObserver(([e]) => { visible = e.isIntersecting; sync(); }, { threshold: 0.25 }).observe(heroEl);
    // swipe
    const stage = $("[data-slides]", heroEl);
    let x0 = 0, pid = null;
    stage.addEventListener("pointerdown", (e) => { if (e.button === 0) { pid = e.pointerId; x0 = e.clientX; } });
    stage.addEventListener("pointerup", (e) => {
      if (e.pointerId !== pid) return; pid = null;
      const dx = e.clientX - x0;
      if (dx < -50) go(i + 1, 1); else if (dx > 50) go(i - 1, -1);
    });
    stage.addEventListener("dragstart", (e) => e.preventDefault());
    if (reduce) heroEl.classList.add("is-static");
    activate(0);
    sync();
    // opening: the house's C (logo crescent + gold drop) frames the first photograph, then opens to full screen
    const rootEl = document.documentElement;
    if (rootEl.classList.contains("is-opening") && !(G && heroEl.hasAttribute("data-intro"))) rootEl.classList.remove("is-opening");
    if (rootEl.classList.contains("is-opening")) {
      try { sessionStorage.setItem("cc-intro", "1"); } catch (e) {}
      const M = { w: 2028, h: 2340, sx: 0.127, stem: 0.2135 };   // mask size, stem centre and stem thickness (fractions of width)
      const title = $(".hero__title .split", heroEl);
      title?.classList.remove("is-in");
      const st = { e: 0, drop: 1 };
      const apply = () => {
        const vw = heroEl.clientWidth, vh = heroEl.clientHeight;
        const h0 = Math.min(vh * 0.62, vw * 0.92 * M.h / M.w), w0 = h0 * M.w / M.h;
        const w1 = (vw * 1.3) / M.stem, h1 = w1 * M.h / M.w;
        const mh = h0 * Math.pow(h1 / h0, st.e), mw = mh * M.w / M.h;
        const ax0 = vw / 2 - w0 / 2 + M.sx * w0, ay0 = vh / 2;
        const ax = ax0 + (vw / 2 - ax0) * Math.min(1, st.e * 1.6), ay = ay0;
        heroEl.style.setProperty("--mw", mw.toFixed(1) + "px"); heroEl.style.setProperty("--mh", mh.toFixed(1) + "px");
        heroEl.style.setProperty("--mx", (ax - M.sx * mw).toFixed(1) + "px"); heroEl.style.setProperty("--my", (ay - 0.5 * mh).toFixed(1) + "px");
        const drop = $("[data-drop]", heroEl); if (drop) drop.style.opacity = st.drop;
      };
      apply();
      addEventListener("resize", apply);
      G.timeline({ onUpdate: apply, onComplete: () => {
        removeEventListener("resize", apply);
        rootEl.classList.remove("is-opening");
        ["--mw", "--mh", "--mx", "--my"].forEach((v) => heroEl.style.removeProperty(v));
        requestAnimationFrame(() => title?.classList.add("is-in"));
        sync();
      } })
        .to(st, { drop: 0, duration: 0.5, ease: "power2.in" }, 1.0)
        .to(st, { e: 1, duration: 1.6, ease: "expo.inOut" }, 1.0);
    }
    // the hero recedes as the page takes over
    if (G) {
      // explicit start values: a .to() would capture whatever state the opening left (trap: start values are read at creation)
      G.fromTo("[data-hero-content]", { yPercent: 0, opacity: 1 }, { yPercent: -18, opacity: 0, ease: "none", scrollTrigger: { trigger: heroEl, start: "top top", end: "bottom 30%", scrub: true } });
      const span = { trigger: heroEl, start: "top top", end: "bottom top", scrub: true };
      G.matchMedia().add({ wide: "(min-width: 901px)", narrow: "(max-width: 900px)" }, (ctx) => {
        if (ctx.conditions.wide) {
          // the next section slides over the hero like a sheet; the photograph pushes in and darkens beneath it
          window.ScrollTrigger.create({ trigger: heroEl, start: "top top", end: "bottom top", pin: true, pinSpacing: false });
          G.fromTo("[data-slides]", { scale: 1 }, { scale: 1.09, ease: "none", scrollTrigger: { ...span } });
          G.fromTo(heroEl, { "--dim": 0 }, { "--dim": 0.66, ease: "none", scrollTrigger: { ...span } });
        } else G.fromTo("[data-slides]", { yPercent: 0 }, { yPercent: 14, ease: "none", scrollTrigger: { ...span } });
      });
    }
  }

  /* ---------- scroll choreography (GSAP) ---------- */
  if (G) {
    const ST = window.ScrollTrigger;

    // words light up as the paragraph crosses the screen
    $$("[data-lit]").forEach((p) => {
      const words = $$(".w", p);
      let lit = 0;
      ST.create({ trigger: p, start: "top 82%", end: "bottom 50%", scrub: true, onUpdate: (s) => {
        const k = Math.round(s.progress * words.length);
        if (k === lit) return;
        words.forEach((w, j) => w.classList.toggle("is-lit", j < k));
        lit = k;
      } });
    });

    const mm = G.matchMedia();

    // the frame opens: a photograph grows from a small frame to full screen, then the métiers slide over it
    const frame = $("[data-frame]");
    if (frame) {
      const media = $("[data-frame-media]", frame), fimg = $("img", media), fp = $(".frame__p", frame);
      mm.add("(min-width: 901px)", () => {
        frame.classList.add("is-live");
        const tl = G.timeline({ defaults: { ease: "power2.inOut" }, scrollTrigger: { trigger: frame, start: "top top", end: () => "+=" + innerHeight * 1.3, scrub: 0.7,
          onUpdate: (s) => fp.classList.toggle("is-in", s.progress > 0.58) } });
        tl.fromTo(media, { clipPath: "inset(23% 33% 23% 33%)" }, { clipPath: "inset(0% 0% 0% 0%)", duration: 1 }, 0)
          .fromTo(fimg, { scale: 1.4 }, { scale: 1, duration: 1 }, 0)
          .fromTo([".frame__k", ".frame__cap"], { opacity: 0, y: 16 }, { opacity: 1, y: 0, duration: 0.25, ease: "power2.out" }, 0.72)
          .to({}, { duration: 0.35 });
        return () => frame.classList.remove("is-live");
      });
      mm.add("(max-width: 900px)", () => {
        G.fromTo(media, { clipPath: "inset(10% 7% 10% 7%)" }, { clipPath: "inset(0% 0% 0% 0%)", ease: "none", scrollTrigger: { trigger: frame, start: "top bottom", end: "top 15%", scrub: true } });
      });
    }

    mm.add("(min-width: 901px)", () => {
      // métiers: full-screen panels; each settles back and darkens as the next one slides over it
      const cards = $$(".card");
      cards.forEach((card, k) => {
        G.fromTo($(".card__img", card), { scale: 1.24, yPercent: -5 }, { scale: 1, yPercent: 0, ease: "none", scrollTrigger: { trigger: card, start: "top bottom", end: "top top", scrub: true } });
        if (k === cards.length - 1) return;
        const st = { trigger: cards[k + 1], start: "top bottom", end: "top top", scrub: true };
        G.to($(".card__in", card), { scale: 0.88, ease: "none", scrollTrigger: st });
        G.to($(".card__veil", card), { opacity: 0.55, ease: "none", scrollTrigger: { ...st } });
      });

      // pinned horizontal gallery: the title drifts behind, each photograph slides inside its frame
      const hx = $("[data-hx]");
      if (hx) {
        const track = $("[data-hx-track]", hx), bar = $("[data-hx-bar]", hx), ghost = $("[data-hx-ghost]", hx);
        const dist = () => Math.max(0, track.scrollWidth - innerWidth);
        const run = G.to(track, { x: () => -dist(), ease: "none", scrollTrigger: {
          trigger: hx, start: "top top", end: () => "+=" + dist(), pin: $(".hx__pin", hx), scrub: 0.6, invalidateOnRefresh: true,
          onUpdate: (s) => { if (bar) bar.style.transform = `scaleX(${s.progress})`; } } });
        if (ghost) G.fromTo(ghost, { xPercent: 4 }, { xPercent: -42, ease: "none", scrollTrigger: { trigger: hx, start: "top bottom", end: () => "+=" + (dist() + innerHeight), scrub: 0.6, invalidateOnRefresh: true } });
        $$(".hx__img", track).forEach((img) => G.fromTo(img, { xPercent: 6 }, { xPercent: -6, ease: "none",
          scrollTrigger: { trigger: img.closest(".hx__item"), containerAnimation: run, start: "left right", end: "right left", scrub: true } }));
        G.fromTo($$(".hx__item", track).slice(0, 5), { y: 90 }, { y: 0, ease: "none", stagger: 0.08, scrollTrigger: { trigger: hx, start: "top bottom", end: "top top", scrub: true } });
      }

      // the book: its real pages turn with the scroll, chapter by chapter
      const fb = $("[data-fb]");
      if (fb) {
        const book = $("[data-fb-book]", fb), leaves = $$(".fb__leaf", book), N = leaves.length;
        const chapEl = $("[data-fb-chapter]", fb);
        let chap = chapEl ? chapEl.textContent : "";
        const setChap = (t) => {
          if (!chapEl || t === chap) return;
          chap = t; chapEl.classList.add("is-swap");
          setTimeout(() => { chapEl.textContent = t; chapEl.classList.remove("is-swap"); }, 280);
        };
        const render = (total) => {
          leaves.forEach((lf, k) => {
            const f = Math.min(Math.max(total - k, 0), 1), e = f * f * (3 - 2 * f);
            lf.style.setProperty("--r", (-180 * e).toFixed(2) + "deg");
            lf.style.setProperty("--shade", (Math.sin(e * Math.PI) * 0.85).toFixed(3));
            lf.style.zIndex = f > 0 && f < 1 ? 300 : f >= 1 ? 100 + k : 100 - k;
          });
          const open = Math.min(Math.max(total, 0), 1), close = Math.min(Math.max(total - (N - 1), 0), 1);
          book.style.transform = `translateX(calc(var(--pw) * ${(-0.5 * (1 - open) + 0.5 * close).toFixed(4)}))`;
          book.style.setProperty("--spine", Math.min(open, 1 - close).toFixed(3));
          const k = Math.round(total);
          setChap(k <= 0 ? "Le book" : leaves[Math.min(k, N) - 1].dataset.chapter);
        };
        render(0);
        window.ScrollTrigger.create({ trigger: fb, start: "top top", end: () => "+=" + Math.round(innerHeight * 0.55 * N), pin: $(".fb__pin", fb),
          scrub: 0.6, invalidateOnRefresh: true, onUpdate: (s) => render(s.progress * N) });
        // the book rises and comes upright as the ink scene arrives
        G.fromTo($(".fb__stage", fb), { y: 160, rotateX: 26, scale: 0.84, transformPerspective: 1800 }, { y: 0, rotateX: 0, scale: 1, ease: "none",
          scrollTrigger: { trigger: fb, start: "top bottom", end: "top top", scrub: true } });
      }

      // next rubric: the photograph opens from a frame to full screen while the link holds still
      const nx = $("[data-nx]");
      if (nx) {
        const media = $("[data-nx-media]", nx);
        G.timeline({ defaults: { ease: "power2.inOut" }, scrollTrigger: { trigger: nx, start: "top top", end: () => "+=" + innerHeight * 0.9, pin: $(".next", nx), scrub: 0.7 } })
          .fromTo(media, { clipPath: "inset(20% 28% 20% 28%)" }, { clipPath: "inset(0% 0% 0% 0%)" }, 0)
          .fromTo($("img", media), { scale: 1.35 }, { scale: 1 }, 0)
          .fromTo($(".next__t", nx), { scale: 0.8 }, { scale: 1 }, 0);
      }

      // mosaic photographs drift inside their frames
      $$(".tile__img").forEach((img) => {
        G.fromTo(img, { yPercent: -5 }, { yPercent: 5, ease: "none", scrollTrigger: { trigger: img.closest(".tile"), start: "top bottom", end: "bottom top", scrub: true } });
      });
    });

    mm.add("(max-width: 900px)", () => {
      // phones: each métier photograph opens out of its margins as it arrives
      $$(".card__media").forEach((m) => G.fromTo(m, { clipPath: "inset(14% 9% 14% 9%)" }, { clipPath: "inset(0% 0% 0% 0%)", ease: "none",
        scrollTrigger: { trigger: m, start: "top bottom", end: "top 30%", scrub: true } }));
      const media = $("[data-nx-media]");
      if (media) G.fromTo(media, { clipPath: "inset(9% 7% 9% 7%)" }, { clipPath: "inset(0% 0% 0% 0%)", ease: "none", scrollTrigger: { trigger: "[data-nx]", start: "top bottom", end: "top 20%", scrub: true } });
    });

    // the two logo rows slide in from opposite sides
    $$("[data-mq] .mq__row").forEach((row, k) => G.fromTo(row, { xPercent: k ? 14 : -14 }, { xPercent: 0, ease: "none",
      scrollTrigger: { trigger: "[data-mq]", start: "top bottom", end: "center 55%", scrub: true } }));

    // the end panel: its call-out rises out of the depth as the page lifts off it
    const endEl = $("[data-end]"), endIn = $("[data-end-in]");
    if (endEl && endIn) G.fromTo(endIn, { yPercent: -35, scale: 0.94 }, { yPercent: 0, scale: 1, ease: "none",
      scrollTrigger: { trigger: "main", start: "bottom bottom", end: () => `bottom ${innerHeight - endEl.offsetHeight}px`, scrub: true, invalidateOnRefresh: true } });

    // the logo marquee answers the scroll: faster with speed, reversing with direction
    const tracks = $$("[data-mq] .mq__track");
    if (tracks.length) {
      const anims = tracks.map((t) => t.getAnimations ? t.getAnimations()[0] : null).filter(Boolean);
      let boost = 0, dirSign = 1;
      ST.create({ trigger: "[data-mq]", start: "top bottom", end: "bottom top", onUpdate: (s) => {
        boost = Math.min(Math.abs(s.getVelocity()) / 250, 6); dirSign = s.direction;
      } });
      G.ticker.add(() => {
        boost *= 0.92;
        anims.forEach((a) => { a.playbackRate = dirSign * (1 + boost); });
      });
    }

    // images and fonts change heights: measure again once they are in
    addEventListener("load", () => ST.refresh());
    document.fonts?.ready.then(() => ST.refresh());
  }

  /* ---------- scenes: the ground colour flows from one section into the next ---------- */
  // Each [data-scene] section keeps its own colour at rest (so it reads correctly without script);
  // while the next one arrives, both take the same in-between colour, so the whole screen changes at once.
  const scenes = $$("[data-scene]");
  if (scenes.length && !reduce) {
    const RGB = { paper: [255, 255, 255], cream: [243, 238, 228], ink: [2, 55, 79] };
    const linked = scenes.map((el, i) => i > 0 && scenes[i - 1] === el.previousElementSibling);
    const mix = (a, b, k) => a.map((v, j) => v + (b[j] - v) * k);
    const last = new Map();
    const paint = () => {
      const vh = innerHeight;
      const rects = scenes.map((el) => el.getBoundingClientRect());
      const k = (i) => Math.min(1, Math.max(0, (vh * 0.85 - rects[i].top) / (vh * 0.55)));
      scenes.forEach((el, i) => {
        const own = RGB[el.dataset.scene];
        let col = own;
        if (rects[i].bottom > 0 && rects[i].top < vh) {
          if (linked[i] && k(i) < 1) col = mix(RGB[scenes[i - 1].dataset.scene], own, k(i));
          if (linked[i + 1] && k(i + 1) > 0) col = mix(own, RGB[scenes[i + 1].dataset.scene], k(i + 1));
        }
        const css = `rgb(${col.map(Math.round).join(",")})`;
        if (last.get(el) !== css) { el.style.backgroundColor = css; last.set(el, css); }
      });
    };
    addEventListener("scroll", paint, { passive: true });
    addEventListener("resize", paint);
    paint();
  }

  /* ---------- end panel: revealed from under the page when it fits on screen ---------- */
  const endPanel = $("[data-end]");
  if (endPanel && !reduce) {
    const fit = () => endPanel.classList.toggle("is-reveal", endPanel.offsetHeight < innerHeight * 0.92);
    fit();
    addEventListener("resize", fit);
  }

  /* ---------- page transition: an ink curtain closes over the page; the next page lifts it (CSS) ---------- */
  if (!reduce) {
    document.addEventListener("click", (e) => {
      const a = e.target.closest && e.target.closest("a[href]");
      if (!a || e.defaultPrevented || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
      if ((a.target && a.target !== "_self") || a.hasAttribute("download")) return;
      const url = new URL(a.href, location.href);
      if (url.origin !== location.origin || !url.protocol.startsWith("http")) return;
      if (url.pathname === location.pathname && url.search === location.search) return;   // same page: anchors, works
      e.preventDefault();
      try { sessionStorage.setItem("cc-pt", "1"); } catch (err) {}
      const pt = document.createElement("div");
      pt.className = "pt"; pt.setAttribute("aria-hidden", "true");
      document.body.appendChild(pt);
      setTimeout(() => { location.href = url.href; }, 560);
    });
    // back/forward restores the page from memory with the curtain still drawn
    addEventListener("pageshow", (e) => { if (e.persisted) $$(".pt").forEach((x) => x.remove()); });
  }

  /* ---------- a label follows the pointer over the works (fine pointers) ---------- */
  if (!reduce && matchMedia("(pointer: fine)").matches) {
    const tag = document.createElement("div");
    tag.className = "cur"; tag.setAttribute("aria-hidden", "true"); tag.textContent = "Voir";
    document.body.appendChild(tag);
    root.classList.add("has-cur");
    let x = 0, y = 0, tx = 0, ty = 0, on = false, raf = 0;
    const loop = () => {
      x += (tx - x) * 0.22; y += (ty - y) * 0.22;
      tag.style.transform = `translate3d(${x.toFixed(1)}px,${y.toFixed(1)}px,0)`;
      raf = on || Math.abs(tx - x) + Math.abs(ty - y) > 0.5 ? requestAnimationFrame(loop) : 0;
    };
    addEventListener("pointermove", (e) => {
      tx = e.clientX; ty = e.clientY;
      const hit = !!(e.target.closest && e.target.closest("[data-lb], .hx__item a, .card__media"));
      if (hit && !on) { x = tx; y = ty; }
      if (hit !== on) { on = hit; tag.classList.toggle("is-on", on); }
      if (on && !raf) raf = requestAnimationFrame(loop);
    }, { passive: true });
  }

  /* ---------- AVIF probe (neighbour preloading in the lightbox) ---------- */
  let avif = false;
  const probe = new Image();
  probe.onload = () => { avif = probe.width > 0; };
  probe.src = "data:image/avif;base64,AAAAIGZ0eXBhdmlmAAAAAGF2aWZtaWYxbWlhZk1BMUIAAADrbWV0YQAAAAAAAAAhaGRscgAAAAAAAAAAcGljdAAAAAAAAAAAAAAAAAAAAAAOcGl0bQAAAAAAAQAAAB5pbG9jAAAAAEQAAAEAAQAAAAEAAAETAAAAFwAAAChpaW5mAAAAAAABAAAAGmluZmUCAAAAAAEAAGF2MDFDb2xvcgAAAABqaXBycAAAAEtpcGNvAAAAFGlzcGUAAAAAAAAAAQAAAAEAAAAQcGl4aQAAAAADCAgIAAAADGF2MUOBAAwAAAAAE2NvbHJuY2x4AAEADQAGgAAAABdpcG1hAAAAAAAAAAEAAQQBAoMEAAAAH21kYXQSAAoFGAAGBCAyDBgACiiihAAAsBKamA==";

  /* ---------- F6 lightbox ---------- */
  const lb = $("[data-lightbox]");
  const links = $$("[data-lb]");
  if (lb && links.length && typeof lb.showModal === "function") {
    const items = links.map((a) => ({ n: +a.dataset.lb, ...JSON.parse(a.dataset.item) }));
    const img = $(".lb__stage img", lb), src = $(".lb__stage source", lb);
    const count = $(".lb__count", lb), t = $(".lb__t", lb), s = $(".lb__s", lb), d = $(".lb__d", lb);
    let cur = 0, opener = null, pushed = false;
    const preload = (k) => { const it = items[(k + items.length) % items.length]; const p = new Image(); p.src = avif ? it.avif : it.jpg; };
    const show = (k) => {
      cur = (k + items.length) % items.length;
      const it = items[cur];
      img.classList.add("is-loading");
      src.srcset = it.avif; img.src = it.jpg; img.alt = it.alt;
      count.textContent = `${cur + 1} / ${items.length}`;
      t.textContent = it.t; s.textContent = it.s; d.textContent = it.d;
      t.hidden = !it.t; s.hidden = !it.s; d.hidden = !it.d;
      preload(cur + 1); preload(cur - 1);
      const hash = `#piece-${it.n}`;
      if (location.hash !== hash) history.replaceState(history.state, "", hash);
    };
    img.addEventListener("load", () => img.classList.remove("is-loading"));
    const open = (k, fromHistory = false) => {
      opener = document.activeElement;
      if (!lb.open) {
        if (!fromHistory) { history.pushState({ lb: true }, "", `#piece-${items[k].n}`); pushed = true; }
        lb.showModal();
        document.documentElement.style.overflow = "hidden";
        hold(true);
      }
      show(k);
      $(".lb__close", lb).focus();
    };
    const close = (viaHistory = false) => {
      if (!lb.open) return;
      lb.close();
      document.documentElement.style.overflow = "";
      hold(false);
      if (!viaHistory && pushed) { pushed = false; history.back(); }
      else if (!viaHistory) history.replaceState(null, "", location.pathname + location.search);
      const back = links.find((a) => +a.dataset.lb === items[cur].n);
      (back || opener)?.focus({ preventScroll: true });
    };
    links.forEach((a, k) => a.addEventListener("click", (e) => { e.preventDefault(); open(k); }));
    $(".lb__prev", lb).addEventListener("click", () => show(cur - 1));
    $(".lb__next", lb).addEventListener("click", () => show(cur + 1));
    $(".lb__close", lb).addEventListener("click", () => close());
    lb.addEventListener("cancel", (e) => { e.preventDefault(); close(); });
    lb.addEventListener("keydown", (e) => {
      if (e.key === "ArrowRight") { e.preventDefault(); show(cur + 1); }
      if (e.key === "ArrowLeft") { e.preventDefault(); show(cur - 1); }
    });
    addEventListener("popstate", () => {
      const m = location.hash.match(/^#piece-(\d+)$/);
      if (!m && lb.open) { pushed = false; close(true); }
      else if (m) { const k = items.findIndex((it) => it.n === +m[1]); if (k >= 0) open(k, true); }
    });
    const stage = $(".lb__stage", lb);
    let sx = 0, sy = 0, sp = null;
    stage.addEventListener("pointerdown", (e) => { sp = e.pointerId; sx = e.clientX; sy = e.clientY; });
    stage.addEventListener("pointerup", (e) => {
      if (e.pointerId !== sp) return; sp = null;
      const dx = e.clientX - sx, dy = e.clientY - sy;
      if (Math.abs(dx) > 50 && Math.abs(dx) > Math.abs(dy)) show(cur + (dx < 0 ? 1 : -1));
    });
    const m = location.hash.match(/^#piece-(\d+)$/);
    if (m) { const k = items.findIndex((it) => it.n === +m[1]); if (k >= 0) { history.replaceState(null, "", location.pathname + location.search); open(k); } }
  }

  /* ---------- F7 film tile: muted loop, only while on screen ---------- */
  $$("video[data-autoplay]").forEach((v) => {
    const fig = v.closest(".tile");
    const manual = () => {
      fig.classList.add("is-manual");
      $(".tile__play", fig)?.addEventListener("click", (e) => { e.currentTarget.remove(); fig.classList.remove("is-manual"); v.controls = true; v.play().catch(() => {}); }, { once: true });
    };
    if (reduce || !io) { manual(); return; }
    new IntersectionObserver(([e]) => {
      if (e.isIntersecting) { v.preload = "auto"; v.play().catch((err) => { if (err && err.name === "NotAllowedError") manual(); }); } else v.pause();
    }, { threshold: 0.2 }).observe(v);
  });

  /* ---------- F8 YouTube facade: nothing loads before the click ---------- */
  $$("[data-film]").forEach((f) => {
    $(".film__btn", f).addEventListener("click", () => {
      const ifr = document.createElement("iframe");
      ifr.src = `https://www.youtube-nocookie.com/embed/${f.dataset.film}?autoplay=1&rel=0&modestbranding=1`;
      ifr.title = f.dataset.title;
      ifr.allow = "autoplay; encrypted-media; picture-in-picture; fullscreen";
      ifr.allowFullscreen = true;
      f.replaceChildren(ifr);
      ifr.focus();
    }, { once: true });
  });

  /* ---------- map facade ---------- */
  $$("[data-map]").forEach((m) => {
    $("[data-map-load]", m)?.addEventListener("click", () => {
      const ifr = document.createElement("iframe");
      ifr.src = m.dataset.map;
      ifr.title = "Plan d’accès : 35, Boulevard Berthier, 75017 Paris";
      ifr.loading = "lazy";
      ifr.referrerPolicy = "no-referrer-when-downgrade";
      m.replaceChildren(ifr);
    }, { once: true });
  });

  /* ---------- contact form: validated, then opens the visitor's mail app ---------- */
  $$("form[data-mailto]").forEach((form) => {
    const f = { nom: $("#f-nom", form), prenom: $("#f-prenom", form), email: $("#f-email", form), message: $("#f-msg", form) };
    const err = (input, msg) => {
      const field = input.closest(".field");
      field.classList.toggle("is-invalid", !!msg);
      input.setAttribute("aria-invalid", msg ? "true" : "false");
      $(".field__err", field).textContent = msg || "";
    };
    const check = () => {
      let ok = true;
      const em = f.email.value.trim();
      if (!em) { err(f.email, "Merci d’indiquer votre adresse email."); ok = false; }
      else if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(em)) { err(f.email, "Cette adresse email ne semble pas complète."); ok = false; }
      else err(f.email, "");
      if (!f.message.value.trim()) { err(f.message, "Merci d’écrire votre message."); ok = false; } else err(f.message, "");
      return ok;
    };
    Object.values(f).forEach((x) => x.addEventListener("blur", () => { if (x.closest(".field").classList.contains("is-invalid")) check(); }));
    form.addEventListener("submit", (e) => {
      e.preventDefault();
      if (!check()) { $("[aria-invalid='true']", form)?.focus(); return; }
      const who = [f.prenom.value.trim(), f.nom.value.trim()].filter(Boolean).join(" ");
      const subject = "Demande de contact" + (who ? " - " + who : "");
      const body = `${f.message.value.trim()}\n\n${who}\n${f.email.value.trim()}`;
      location.href = `mailto:${form.dataset.mailto}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
      const note = $(".form__note", form);
      if (note) note.textContent = `Votre messagerie vient de s’ouvrir avec votre message. Si rien ne s’est passé, écrivez-nous directement à ${form.dataset.mailto}.`;
    });
  });
})();
