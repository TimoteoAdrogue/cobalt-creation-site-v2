/* Cobalt Création, V2 « Maison ». No dependencies. */
(() => {
  "use strict";
  const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];

  /* ---------- F1 header: condense after the first 80px ---------- */
  const hd = $("[data-header]");
  if (hd && "IntersectionObserver" in window) {
    const s = document.createElement("div");
    s.setAttribute("aria-hidden", "true");
    s.style.cssText = "position:absolute;top:80px;left:0;width:1px;height:1px;pointer-events:none";
    document.body.prepend(s);
    new IntersectionObserver(([e]) => hd.classList.toggle("is-condensed", !e.isIntersecting && e.boundingClientRect.top < 0)).observe(s);
  }

  /* ---------- mobile menu ---------- */
  const menuBtn = $(".hd__menu"), menu = $("[data-menu]");
  if (menuBtn && menu) {
    const label = $("[data-menu-label]", menuBtn);
    const set = (open) => {
      menuBtn.setAttribute("aria-expanded", String(open));
      menu.classList.toggle("is-open", open);
      document.documentElement.style.overflow = open ? "hidden" : "";
      label.textContent = open ? "Fermer" : "Menu";
      if (open) $("a", menu)?.focus();
    };
    menuBtn.addEventListener("click", () => set(menuBtn.getAttribute("aria-expanded") !== "true"));
    document.addEventListener("keydown", (e) => { if (e.key === "Escape" && menu.classList.contains("is-open")) { set(false); menuBtn.focus(); } });
    matchMedia("(min-width: 1240px)").addEventListener("change", (m) => m.matches && set(false));
  }

  /* ---------- reveal on scroll ---------- */
  const reveal = $$("[data-reveal]");
  if (reveal.length && "IntersectionObserver" in window && !reduce) {
    const io = new IntersectionObserver((entries) => {
      for (const e of entries) {
        // also catch content already above the fold after a jump to the bottom
        if (e.isIntersecting || e.boundingClientRect.top <= 0) { e.target.classList.add("is-in"); io.unobserve(e.target); }
      }
    }, { rootMargin: "0px 0px -6% 0px", threshold: 0.08 });
    reveal.forEach((el) => io.observe(el));
  } else reveal.forEach((el) => el.classList.add("is-in"));

  /* ---------- F2 banner: same slides, right-to-left, one advance every 3 s, endless ---------- */
  const HOLD = 2000; // still frame, then a 1 s slide = 3 s per image, as on the live site
  $$("[data-banner]").forEach((el) => {
    const track = $(".bn__track", el);
    const slides = [...track.children];
    const n = slides.length;
    const dots = $$(".bn__dot", el);
    const pp = $(".bn__pp", el);
    if (n < 2) { $(".bn__ctrl", el)?.remove(); return; }
    const clone = slides[0].cloneNode(true);
    clone.setAttribute("aria-hidden", "true");
    $$("img", clone).forEach((i) => { i.loading = "eager"; i.removeAttribute("fetchpriority"); });
    track.appendChild(clone);
    el.style.setProperty("--bn-time", HOLD + "ms");

    let i = 0, timer = null, remaining = HOLD, startedAt = 0;
    let userPaused = reduce, hovering = false, focused = false, visible = true, dragging = false;
    const blocked = () => userPaused || hovering || focused || !visible || document.hidden || dragging;

    const setX = (pct, px = 0) => { track.style.transform = `translate3d(calc(${pct}% + ${px}px),0,0)`; };
    const activate = (k) => {
      dots.forEach((d, j) => {
        d.classList.remove("is-active");
        d.setAttribute("aria-current", j === k ? "true" : "false");
      });
      void el.offsetWidth; // restart the progress fill
      dots[k]?.classList.add("is-active");
      const nx = slides[(k + 1) % n];
      $$("img", nx).forEach((img) => { img.loading = "eager"; });
    };
    const clear = () => { if (timer) { clearTimeout(timer); timer = null; remaining = Math.max(0, remaining - (performance.now() - startedAt)); } };
    const schedule = () => { if (blocked() || timer) return; startedAt = performance.now(); timer = setTimeout(() => { timer = null; go(i + 1); }, remaining); };
    const sync = () => {
      el.classList.toggle("is-paused", userPaused);
      el.classList.toggle("is-held", !userPaused && blocked());
      pp.setAttribute("aria-label", userPaused ? "Relancer le diaporama" : "Mettre le diaporama en pause");
      if (blocked()) clear(); else schedule();
    };
    function go(k, animate = true) {
      clear();
      remaining = HOLD;
      if (k < 0) { track.classList.remove("is-anim"); i = n; setX(-100 * n); void track.offsetWidth; k = n - 1; }
      i = k;
      track.classList.toggle("is-anim", animate && !reduce);
      setX(-100 * i);
      activate(i % n);
      if (!animate || reduce) settle();
    }
    function settle() {
      if (i >= n) { track.classList.remove("is-anim"); i = 0; setX(0); }
      schedule();
    }
    track.addEventListener("transitionend", (e) => { if (e.target === track && e.propertyName === "transform") settle(); });

    dots.forEach((d, k) => d.addEventListener("click", () => go(k)));
    pp.addEventListener("click", () => { userPaused = !userPaused; sync(); });
    el.addEventListener("pointerenter", (e) => { if (e.pointerType === "mouse") { hovering = true; sync(); } });
    el.addEventListener("pointerleave", () => { hovering = false; sync(); });
    el.addEventListener("focusin", (e) => { focused = e.target.matches(":focus-visible"); sync(); });
    el.addEventListener("focusout", (e) => { if (!el.contains(e.relatedTarget)) { focused = false; sync(); } });
    el.addEventListener("keydown", (e) => {
      if (e.key === "ArrowRight") { e.preventDefault(); go(i + 1); }
      if (e.key === "ArrowLeft") { e.preventDefault(); go(i - 1); }
    });
    document.addEventListener("visibilitychange", sync);
    if ("IntersectionObserver" in window) new IntersectionObserver(([e]) => { visible = e.isIntersecting; sync(); }, { threshold: 0.25 }).observe(el);

    // swipe and drag
    const vp = $(".bn__viewport", el);
    let x0 = 0, dx = 0, pid = null;
    vp.addEventListener("pointerdown", (e) => {
      if (e.button !== 0) return;
      pid = e.pointerId; x0 = e.clientX; dx = 0; dragging = true; sync();
      if (i >= n) { i = 0; }
      track.classList.remove("is-anim");
      vp.setPointerCapture(pid);
    });
    vp.addEventListener("pointermove", (e) => { if (e.pointerId !== pid) return; dx = e.clientX - x0; setX(-100 * i, dx); });
    const end = (e) => {
      if (e.pointerId !== pid) return;
      pid = null; dragging = false;
      const w = vp.clientWidth || 1;
      if (dx < -Math.min(60, w * 0.12)) go(i + 1);
      else if (dx > Math.min(60, w * 0.12)) go(i - 1);
      else { track.classList.toggle("is-anim", !reduce); setX(-100 * i); remaining = HOLD; }
      sync();
    };
    vp.addEventListener("pointerup", end);
    vp.addEventListener("pointercancel", end);
    vp.addEventListener("dragstart", (e) => e.preventDefault());

    if (reduce) el.classList.add("is-static");
    activate(0);
    sync();
  });

  /* ---------- AVIF probe (for neighbour preloading in the lightbox) ---------- */
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
      src.srcset = it.avif;
      img.src = it.jpg;
      img.alt = it.alt;
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
    window.addEventListener("popstate", () => {
      const m = location.hash.match(/^#piece-(\d+)$/);
      if (!m && lb.open) { pushed = false; close(true); }
      else if (m) { const k = items.findIndex((it) => it.n === +m[1]); if (k >= 0) open(k, true); }
    });
    // swipe
    const stage = $(".lb__stage", lb);
    let sx = 0, sy = 0, sp = null;
    stage.addEventListener("pointerdown", (e) => { sp = e.pointerId; sx = e.clientX; sy = e.clientY; });
    stage.addEventListener("pointerup", (e) => {
      if (e.pointerId !== sp) return; sp = null;
      const dx = e.clientX - sx, dy = e.clientY - sy;
      if (Math.abs(dx) > 50 && Math.abs(dx) > Math.abs(dy)) show(cur + (dx < 0 ? 1 : -1));
    });
    // deep link on arrival
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
    if (reduce || !("IntersectionObserver" in window)) { manual(); return; }
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
    const fields = { nom: $("#f-nom", form), prenom: $("#f-prenom", form), email: $("#f-email", form), message: $("#f-msg", form) };
    const err = (input, msg) => {
      const field = input.closest(".field");
      field.classList.toggle("is-invalid", !!msg);
      input.setAttribute("aria-invalid", msg ? "true" : "false");
      $(".field__err", field).textContent = msg || "";
    };
    const check = () => {
      let ok = true;
      const em = fields.email.value.trim();
      if (!em) { err(fields.email, "Merci d’indiquer votre adresse email."); ok = false; }
      else if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(em)) { err(fields.email, "Cette adresse email ne semble pas complète."); ok = false; }
      else err(fields.email, "");
      if (!fields.message.value.trim()) { err(fields.message, "Merci d’écrire votre message."); ok = false; } else err(fields.message, "");
      return ok;
    };
    Object.values(fields).forEach((f) => f.addEventListener("blur", () => { if (f.closest(".field").classList.contains("is-invalid")) check(); }));
    form.addEventListener("submit", (e) => {
      e.preventDefault();
      if (!check()) { $("[aria-invalid='true']", form)?.focus(); return; }
      const who = [fields.prenom.value.trim(), fields.nom.value.trim()].filter(Boolean).join(" ");
      const subject = "Demande de contact" + (who ? " - " + who : "");
      const body = `${fields.message.value.trim()}\n\n${who}\n${fields.email.value.trim()}`;
      location.href = `mailto:${form.dataset.mailto}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
      const note = $(".form__note", form);
      if (note) note.textContent = `Votre messagerie vient de s’ouvrir avec votre message. Si rien ne s’est passé, écrivez-nous directement à ${form.dataset.mailto}.`;
    });
  });
})();
