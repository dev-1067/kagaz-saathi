/* Shared helpers for every Kagaz Saathi page. */
"use strict";
const $ = (s, el = document) => el.querySelector(s);
const $$ = (s, el = document) => [...el.querySelectorAll(s)];
const esc = s => String(s ?? "").replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
const inr = n => "₹" + Math.round(n).toLocaleString("en-IN");

/* Kagzi, the paper owl (original artwork) */
function mascot(size = 120, mood = "calm") {
  const eye = mood === "alert" ? 7 : 6;
  return `<svg class="mascot float" width="${size}" height="${size}" viewBox="0 0 120 120" role="img" aria-label="Kagzi the owl">
    <defs><linearGradient id="kb${size}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#3f8f72"/><stop offset="1" stop-color="#1f5f4a"/></linearGradient></defs>
    <path d="M24 34 L34 14 L50 28 Z M96 34 L86 14 L70 28 Z" fill="#1f5f4a"/>
    <ellipse cx="60" cy="68" rx="42" ry="44" fill="url(#kb${size})"/>
    <ellipse cx="60" cy="80" rx="26" ry="28" fill="#fdf3e3"/>
    <path d="M44 66 q5 -3 10 0 M66 66 q5 -3 10 0" stroke="#e8d6bd" stroke-width="2" fill="none" stroke-linecap="round" opacity=".7"/>
    <circle cx="44" cy="52" r="15" fill="#fff"/><circle cx="76" cy="52" r="15" fill="#fff"/>
    <g class="blink"><circle cx="46" cy="53" r="${eye}" fill="#241f19"/><circle cx="74" cy="53" r="${eye}" fill="#241f19"/>
    <circle cx="48" cy="50" r="2.2" fill="#fff"/><circle cx="76" cy="50" r="2.2" fill="#fff"/></g>
    <path d="M54 62 L66 62 L60 73 Z" fill="#e0762a"/>
    <path d="M30 78 q-12 6 -6 24 q10 -6 12 -14 Z M90 78 q12 6 6 24 q-10 -6 -12 -14 Z" fill="#1f5f4a"/>
    <rect x="46" y="86" width="28" height="22" rx="3" fill="#fff" stroke="#d9cdb8"/><path d="M51 92 h18 M51 97 h18 M51 102 h11" stroke="#a39880" stroke-width="2" stroke-linecap="round"/>
    <circle cx="68" cy="102" r="4.2" fill="#e0762a"/>
    <path d="M48 112 l-4 6 M72 112 l4 6" stroke="#e0762a" stroke-width="4" stroke-linecap="round"/></svg>`;
}
const LOGO = `<svg width="34" height="34" viewBox="0 0 64 64" aria-hidden="true"><rect width="64" height="64" rx="18" fill="#17382f"/><path d="M14 22 L22 10 L32 18 L42 10 L50 22 Q50 46 32 54 Q14 46 14 22Z" fill="#e0762a"/><circle cx="25" cy="29" r="5.5" fill="#fff"/><circle cx="39" cy="29" r="5.5" fill="#fff"/><circle cx="26" cy="30" r="2.6" fill="#241f19"/><circle cx="38" cy="30" r="2.6" fill="#241f19"/><path d="M29 37 h6 l-3 5z" fill="#17382f"/></svg>`;

function toast(msg) {
  const t = $("#toast"); if (!t) return;
  t.textContent = msg; t.classList.add("on"); clearTimeout(t._h); t._h = setTimeout(() => t.classList.remove("on"), 3000);
}
async function api(path, body, opts = {}) {
  const r = await fetch(path, body !== undefined ? { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) } : {});
  if (r.status === 401 && !opts.noRedirect) { location.href = "/signin?next=" + encodeURIComponent("/app" + location.hash); throw new Error("Please sign in again."); }
  const d = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(d.error || `Request failed (${r.status})`);
  return d;
}
const VT = {
  scam: { en: "Very likely a scam", cls: "bad", color: "#d63448", icon: "⚠" },
  suspicious: { en: "Suspicious", cls: "warn", color: "#b86a00", icon: "?" },
  genuine: { en: "Looks genuine", cls: "ok", color: "#12935f", icon: "✓" },
};
const when = t => { const d = new Date(t * 1000); return d.toLocaleDateString("en-IN", { day: "numeric", month: "short" }) + ", " + d.toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit" }); };
const LANGS = { en: "English", hi: "हिन्दी", mr: "मराठी" };
const VOICE = { en: "en-IN", hi: "hi-IN", mr: "mr-IN" };

/* read aloud with the browser's own voices (works offline; AWS build can swap in Amazon Polly) */
function speak(text, lang) {
  if (!("speechSynthesis" in window)) { toast("This browser cannot read aloud."); return false; }
  speechSynthesis.cancel();
  const u = new SpeechSynthesisUtterance(text); u.lang = VOICE[lang] || "en-IN"; u.rate = .92;
  const v = speechSynthesis.getVoices().find(x => x.lang === u.lang) || speechSynthesis.getVoices().find(x => x.lang.startsWith(u.lang.slice(0, 2)));
  if (v) u.voice = v; else if (lang !== "en") toast("No " + LANGS[lang] + " voice installed on this device; using the default voice.");
  speechSynthesis.speak(u); return true;
}
function resultText(r) { return `${r.verdict_label}. ${r.kind_label}. ${r.explanation} ${r.steps.join(" ")}`; }

/* shared result card, used by the landing demo and the app */
function resultHtml(r, { actions = "" } = {}) {
  const v = VT[r.verdict];
  const ring = `style="--p:${r.risk};--c:${v.color}"`;
  const reasons = r.signals.map((s, i) => `<li class="${s === "no_share" || s === "official_link" ? "good" : ""}">${esc(r.reasons[i])}</li>`).join("");
  const links = r.facts.links.map(l => `<div class="fact"><b>${l.judgement === "official" ? "✓ Official" : l.judgement === "short" ? "⚠ Shortened" : l.judgement === "lookalike" ? "⚠ Look-alike" : "Unknown"}</b><br>${esc(l.url)}</div>`).join("");
  const phones = r.facts.phones.map(p => `<div class="fact"><b>Phone</b><br>${esc(p)}</div>`).join("");
  const amounts = r.facts.amounts.slice(0, 3).map(a => `<div class="fact"><b>Amount</b><br>${inr(a)}</div>`).join("");
  const dates = r.facts.dates.slice(0, 2).map(d => `<div class="fact"><b>Date</b><br>${esc(d)}</div>`).join("");
  return `<div class="result">
    <div class="verdict-big ${r.verdict}"><div class="vhead"><div class="ring" ${ring}><div style="text-align:center"><b>${r.risk}</b><small>risk</small></div></div>
      <div><div class="vtitle">${v.icon} ${esc(r.verdict_label)}</div><div class="small mute">${esc(r.kind_label)} · model confidence ${Math.round(r.confidence * 100)}%</div></div></div></div>
    <p style="margin:6px 0 10px">${esc(r.explanation)}</p>
    ${reasons ? `<h3 style="font-size:14px;margin-top:12px">Why we think so</h3><ul class="reasons">${reasons}</ul>` : ""}
    <h3 style="font-size:14px;margin-top:12px">What to do</h3><ol class="steps2">${r.steps.map(s => `<li>${esc(s)}</li>`).join("")}</ol>
    ${links || phones || amounts || dates ? `<h3 style="font-size:14px;margin-top:12px">Found in the message</h3><div class="facts">${links}${phones}${amounts}${dates}</div>` : ""}
    ${actions}</div>`;
}
