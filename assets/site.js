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

  /* ---------- split words for mask reveals ---------- */
  $$(".split").forEach((el) => {
    const words = el.textContent.trim().split(/\s+/);
    el.setAttribute("aria-label", el.textContent.trim());
    const safe = (w) => w.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
    el.innerHTML = words.map((w, i) => `<span class="sw" aria-hidden="true"><span class="sw__in" style="--w:${i}">${safe(w)}</span></span>`).join(" ");
  });

  /* ---------- reveals (IntersectionObserver; also catches content jumped past) ---------- */
  const revealEls = $$("[data-reveal], [data-wipe], .split, .reveal-soft");
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
  if (hd && heroEl && io) {
    new IntersectionObserver(([e]) => hd.classList.toggle("is-over", e.isIntersecting), { rootMargin: "-76px 0px 0px 0px", threshold: 0 }).observe(heroEl);
  } else if (hd) hd.classList.remove("is-over");

  /* ---------- mobile menu ---------- */
  const menuBtn = $(".hd__menu"), menu = $("[data-menu]");
  if (menuBtn && menu) {
    const label = $("[data-menu-label]", menuBtn);
    const set = (open) => {
      menuBtn.setAttribute("aria-expanded", String(open));
      menu.classList.toggle("is-open", open);
      hd.classList.toggle("is-menu", open);
      document.documentElement.style.overflow = open ? "hidden" : "";
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
    const blocked = () => userPaused || hovering || focused || !visible || document.hidden || busy;
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
    // the hero recedes as the page takes over
    if (G) {
      G.to("[data-hero-content]", { yPercent: -18, opacity: 0, ease: "none", scrollTrigger: { trigger: heroEl, start: "top top", end: "bottom 30%", scrub: true } });
      G.to("[data-slides]", { yPercent: 14, ease: "none", scrollTrigger: { trigger: heroEl, start: "top top", end: "bottom top", scrub: true } });
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
    mm.add("(min-width: 901px)", () => {
      // stacking métiers: each card settles back as the next one slides over it
      const cards = $$(".card");
      cards.forEach((card, k) => {
        if (k === cards.length - 1) return;
        const st = { trigger: cards[k + 1], start: "top bottom", end: "top 30%", scrub: true };
        G.to($(".card__in", card), { scale: 0.92, ease: "none", scrollTrigger: st });
        G.to($(".card__veil", card), { opacity: 0.38, ease: "none", scrollTrigger: { ...st } });
      });

      // pinned horizontal gallery
      const hx = $("[data-hx]");
      if (hx) {
        const track = $("[data-hx-track]", hx), bar = $("[data-hx-bar]", hx);
        const dist = () => Math.max(0, track.scrollWidth - innerWidth);
        G.to(track, { x: () => -dist(), ease: "none", scrollTrigger: {
          trigger: hx, start: "top top", end: () => "+=" + dist(), pin: $(".hx__pin", hx), scrub: 0.6, invalidateOnRefresh: true,
          onUpdate: (s) => { if (bar) bar.style.transform = `scaleX(${s.progress})`; } } });
      }

      // mosaic photographs drift inside their frames
      $$(".tile__img").forEach((img) => {
        G.fromTo(img, { yPercent: -5 }, { yPercent: 5, ease: "none", scrollTrigger: { trigger: img.closest(".tile"), start: "top bottom", end: "bottom top", scrub: true } });
      });
    });

    // the book turns toward the reader
    const book = $("[data-book-obj]");
    if (book) G.fromTo(book, { rotateY: -38, rotateX: 9, y: 60 }, { rotateY: -6, rotateX: 0, y: -30, ease: "none",
      scrollTrigger: { trigger: "[data-book]", start: "top bottom", end: "bottom top", scrub: true } });

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
      }
      show(k);
      $(".lb__close", lb).focus();
    };
    const close = (viaHistory = false) => {
      if (!lb.open) return;
      lb.close();
      document.documentElement.style.overflow = "";
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
