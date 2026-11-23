/* SAUDA motion layer: click ripples, magnetic buttons, cursor spotlight, card tilt, cursor ring,
   scroll reveal and count-up numbers. Everything switches off under prefers-reduced-motion. */
"use strict";
(function () {
  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const finePointer = window.matchMedia("(pointer: fine)").matches;
  const FX = window.FX = {};

  /* ripple: any .btn, button or [data-ripple] gets an ink drop where it was pressed */
  document.addEventListener("pointerdown", e => {
    if (reduce) return;
    const el = e.target.closest(".btn, .cta, .seg button, .tabs button, [data-ripple]");
    if (!el || el.disabled) return;
    const r = el.getBoundingClientRect(), d = Math.max(r.width, r.height) * 2.2;
    const ink = document.createElement("span");
    ink.className = "fx-ink";
    ink.style.cssText = `width:${d}px;height:${d}px;left:${e.clientX - r.left - d / 2}px;top:${e.clientY - r.top - d / 2}px`;
    if (getComputedStyle(el).position === "static") el.style.position = "relative";
    el.classList.add("fx-clip");
    el.appendChild(ink);
    ink.addEventListener("animationend", () => ink.remove());
  });

  /* magnetic: [data-magnet] elements lean toward the cursor */
  function magnet(el) {
    if (reduce || !finePointer || el._mag) return;
    el._mag = true;
    el.addEventListener("pointermove", e => {
      const r = el.getBoundingClientRect();
      const x = (e.clientX - r.left - r.width / 2) / r.width, y = (e.clientY - r.top - r.height / 2) / r.height;
      el.style.transform = `translate(${x * 8}px, ${y * 6}px)`;
    });
    el.addEventListener("pointerleave", () => { el.style.transform = ""; });
  }

  /* spotlight + tilt: .spot cards light up under the cursor, .tilt cards lean */
  function spot(el) {
    if (el._spot) return;
    el._spot = true;
    el.addEventListener("pointermove", e => {
      const r = el.getBoundingClientRect();
      el.style.setProperty("--mx", `${e.clientX - r.left}px`);
      el.style.setProperty("--my", `${e.clientY - r.top}px`);
      if (!reduce && el.classList.contains("tilt")) {
        const x = (e.clientX - r.left) / r.width - .5, y = (e.clientY - r.top) / r.height - .5;
        el.style.transform = `perspective(900px) rotateX(${-y * 4}deg) rotateY(${x * 5}deg) translateY(-2px)`;
      }
    });
    el.addEventListener("pointerleave", () => { if (el.classList.contains("tilt")) el.style.transform = ""; });
  }

  /* reveal on scroll */
  const io = "IntersectionObserver" in window ? new IntersectionObserver(entries => {
    for (const en of entries) if (en.isIntersecting) { en.target.classList.add("in"); io.unobserve(en.target); if (en.target.dataset.count != null) count(en.target); }
  }, { threshold: .15 }) : null;

  /* count-up numbers: <span data-count="54.3" data-dec="1" data-suffix="%"> */
  function count(el) {
    const end = parseFloat(el.dataset.count), dec = +(el.dataset.dec || 0), suf = el.dataset.suffix || "", pre = el.dataset.prefix || "";
    if (isNaN(end)) return;
    if (reduce) { el.textContent = pre + end.toFixed(dec) + suf; return; }
    const t0 = performance.now(), dur = 1100;
    const step = t => {
      const k = Math.min(1, (t - t0) / dur), v = end * (1 - Math.pow(1 - k, 3));
      el.textContent = pre + v.toFixed(dec) + suf;
      if (k < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  }
  FX.count = count;

  /* cursor ring that follows the pointer and grows over things you can press */
  function cursor() {
    if (reduce || !finePointer || document.querySelector(".fx-cursor")) return;
    const ring = document.createElement("div"), dot = document.createElement("div");
    ring.className = "fx-cursor"; dot.className = "fx-dot";
    document.body.append(ring, dot);
    let x = innerWidth / 2, y = innerHeight / 2, rx = x, ry = y;
    addEventListener("pointermove", e => {
      x = e.clientX; y = e.clientY;
      dot.style.transform = `translate(${x}px, ${y}px)`;
      const hot = e.target.closest && e.target.closest("a, button, select, input, textarea, label, [data-hot], tr.click");
      ring.classList.toggle("hot", !!hot);
      ring.classList.add("on"); dot.classList.add("on");
    });
    addEventListener("pointerdown", () => ring.classList.add("press"));
    addEventListener("pointerup", () => ring.classList.remove("press"));
    document.addEventListener("pointerleave", () => { ring.classList.remove("on"); dot.classList.remove("on"); });
    const loop = () => { rx += (x - rx) * .2; ry += (y - ry) * .2; ring.style.transform = `translate(${rx}px, ${ry}px)`; requestAnimationFrame(loop); };
    loop();
  }

  /* bind everything currently in the page (call again after rendering new content) */
  FX.bind = function (root = document) {
    root.querySelectorAll("[data-magnet]").forEach(magnet);
    root.querySelectorAll(".spot").forEach(spot);
    root.querySelectorAll("[data-reveal]:not(.in), [data-count]:not(.counted)").forEach(el => {
      if (el.dataset.count != null) el.classList.add("counted");
      if (io && !reduce) io.observe(el); else { el.classList.add("in"); if (el.dataset.count != null) count(el); }
    });
  };
  /* safety net: if the observer is throttled (background tab), reveal whatever is on screen anyway */
  let pending = false;
  function sweep() {
    pending = false;
    document.querySelectorAll("[data-reveal]:not(.in)").forEach(el => {
      const r = el.getBoundingClientRect();
      if (r.top < innerHeight * 1.05 && r.bottom > 0) { el.classList.add("in"); if (el.dataset.count != null) count(el); }
    });
  }
  addEventListener("scroll", () => { if (!pending) { pending = true; setTimeout(sweep, 120); } }, { passive: true });
  setTimeout(sweep, 1200);

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", () => { cursor(); FX.bind(); });
  else { cursor(); FX.bind(); }
})();
