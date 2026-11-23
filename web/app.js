/* Kagaz Saathi app: vanilla JS, hash router, no build step. */
"use strict";
const view = $("#view");
const state = { me: null, demo: false, lang: "en", family: [], last: null };
const ICONS = {
  grid: '<path d="M3 3h6v6H3zM11 3h6v6h-6zM3 11h6v6H3zM11 11h6v6h-6z"/>', shield: '<path d="M10 2l6 2.5v5c0 4-2.6 6.6-6 8-3.4-1.4-6-4-6-8v-5z"/><path d="M7.5 10l2 2 3.5-4"/>',
  clock: '<circle cx="10" cy="10" r="7.5"/><path d="M10 5.5V10l3 2"/>', users: '<circle cx="7.5" cy="7" r="3"/><path d="M2 16c.5-3 3-4.5 5.5-4.5S12.5 13 13 16M13 4.5a3 3 0 010 5.5M15 12c1.8.5 2.8 2 3 4"/>',
  book: '<path d="M4 3.5h8a2 2 0 012 2V17H6a2 2 0 01-2-2zM4 15.5a2 2 0 012-2h8"/>', phone: '<path d="M5 3h3l1.5 4-2 1.5a9 9 0 004 4L13 10.5 17 12v3a2 2 0 01-2 2A12 12 0 013 5a2 2 0 012-2z"/>',
  chart: '<path d="M3 17h14M5 14V9M10 14V4M15 14v-6"/>', gear: '<circle cx="10" cy="10" r="2.6"/><path d="M10 2.5v2M10 15.5v2M2.5 10h2M15.5 10h2M4.7 4.7l1.4 1.4M13.9 13.9l1.4 1.4M15.3 4.7l-1.4 1.4M6.1 13.9l-1.4 1.4"/>',
};
$$(".ico").forEach(e => e.innerHTML = `<svg viewBox="0 0 20 20" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">${ICONS[e.dataset.i]}</svg>`);
$("#logo").innerHTML = LOGO + `<span>Kagaz Saathi</span>`; $("#tip-owl").innerHTML = mascot(46);

/* ---------- theme, language, account menu */
function setTheme(t) { document.documentElement.dataset.theme = t === "dark" ? "dark" : "light"; $$("#theme-seg button").forEach(b => b.classList.toggle("on", b.dataset.t === t)); try { localStorage.setItem("kz-theme", t); } catch (e) { } }
$$("#theme-seg button").forEach(b => b.onclick = () => setTheme(b.dataset.t));
let st = "light"; try { st = localStorage.getItem("kz-theme") || "light"; } catch (e) { } setTheme(st);
function setLang(l, silent) { state.lang = l; $$("#lang-seg button").forEach(b => b.classList.toggle("on", b.dataset.l === l)); try { localStorage.setItem("kz-lang", l); } catch (e) { } if (!silent) { toast("Explanations will be in " + LANGS[l]); if (state.page === "learn") route(); } }
$$("#lang-seg button").forEach(b => b.onclick = () => setLang(b.dataset.l));
$("#who").onclick = e => { e.stopPropagation(); const o = !$("#menu").classList.contains("open"); $("#menu").classList.toggle("open", o); $("#who").setAttribute("aria-expanded", o); };
document.addEventListener("click", e => { if (!e.target.closest(".who-wrap")) { $("#menu").classList.remove("open"); $("#who").setAttribute("aria-expanded", "false"); } if (!e.target.closest(".side,#menu-btn")) $("#side").classList.remove("open"); });
$$("#menu a").forEach(a => a.addEventListener("click", () => $("#menu").classList.remove("open")));
$("#menu-btn").onclick = e => { e.stopPropagation(); $("#side").classList.toggle("open"); };
async function signOut() { try { await fetch("/api/auth/logout", { method: "POST" }); } catch (e) { } location.href = "/signin"; }
$("#signout").onclick = signOut;
function setMe(u, demo) {
  state.me = u; state.demo = demo;
  $("#av").textContent = u.name.split(/\s+/).filter(Boolean).slice(0, 2).map(w => w[0].toUpperCase()).join("") || "?";
  $("#who-n").textContent = u.name; $("#who-r").textContent = demo ? "Demo account" : "Member"; $("#c-home").textContent = u.home || "My home";
}
$("#dx").onclick = () => $("#drawer").classList.remove("open");
$("#drawer").onclick = e => { if (e.target.id === "drawer") $("#drawer").classList.remove("open"); };
document.addEventListener("keydown", e => { if (e.key === "Escape") $("#drawer").classList.remove("open"); });

/* ---------- small charts */
function bars14(per) {
  const days = [...Array(14)].map((_, i) => { const d = new Date(Date.now() - (13 - i) * 864e5); return d.toISOString().slice(0, 10); });
  const m = Object.fromEntries(per.map(p => [p.d, p.n])); const vals = days.map(d => m[d] || 0); const mx = Math.max(3, ...vals);
  const W = 560, H = 170, bw = 22, g = (W - 14 * bw) / 15;
  return `<svg viewBox="0 0 ${W} ${H}" width="100%" role="img" aria-label="Checks in the last 14 days">${[0, .5, 1].map(f => `<line x1="0" x2="${W}" y1="${130 - f * 110}" y2="${130 - f * 110}" stroke="var(--line2)"/>`).join("")}
  ${vals.map((v, i) => { const h = v / mx * 110; return `<rect x="${g + i * (bw + g)}" y="${130 - h}" width="${bw}" height="${Math.max(h, 2)}" rx="6" fill="${v ? "var(--indigo2)" : "var(--line)"}"><title>${days[i]}: ${v} checks</title></rect>
    <text x="${g + i * (bw + g) + bw / 2}" y="152" text-anchor="middle" font-size="10" fill="var(--mute)">${new Date(days[i]).getDate()}</text>`; }).join("")}</svg>`;
}
function donut(s) {
  const parts = [["scam", s.scams, "#d63448"], ["suspicious", s.suspicious, "#ff8a4c"], ["genuine", s.genuine, "#12935f"]]; const tot = parts.reduce((a, p) => a + p[1], 0) || 1;
  let acc = 0; const R = 52, C = 2 * Math.PI * R;
  const arcs = parts.map(([n, v, c]) => { const len = v / tot * C; const o = `<circle r="${R}" cx="70" cy="70" fill="none" stroke="${c}" stroke-width="20" stroke-dasharray="${len} ${C - len}" stroke-dashoffset="${-acc}" transform="rotate(-90 70 70)"/>`; acc += len; return o; }).join("");
  return `<div style="display:flex;align-items:center;gap:18px;flex-wrap:wrap"><svg viewBox="0 0 140 140" width="140" role="img" aria-label="Verdict split"><circle r="52" cx="70" cy="70" fill="none" stroke="var(--gray-bg)" stroke-width="20"/>${arcs}<text x="70" y="68" text-anchor="middle" font-size="24" font-weight="800" fill="var(--ink)">${s.checks}</text><text x="70" y="86" text-anchor="middle" font-size="11" fill="var(--mute)">checks</text></svg>
  <div style="display:grid;gap:8px;font-size:14px">${parts.map(([n, v, c]) => `<div><i style="display:inline-block;width:10px;height:10px;border-radius:3px;background:${c};margin-right:8px"></i>${n === "scam" ? "Scams" : n === "suspicious" ? "Suspicious" : "Genuine"} <b>${v}</b></div>`).join("")}</div></div>`;
}
const kpi = (k, v, f, color, icon) => `<div class="card kpi"><div class="ic" style="background:${color}22;color:${color}">${icon}</div><div><div class="k">${k}</div><div class="v"><span data-count="${v}">${v}</span></div><div class="f">${f}</div></div></div>`;
const vpill = v => `<span class="pill ${VT[v].cls}">${VT[v].icon} ${VT[v].en}</span>`;
const kindName = k => ({ digital_arrest: "Digital arrest", kyc_block: "Fake KYC", otp_theft: "OTP theft", prize_lottery: "Prize / lottery", job_fraud: "Fake job", parcel_customs: "Parcel / customs", bill_cutoff: "Bill cut-off", refund_fraud: "Fake refund", investment_loan: "Investment / loan", impersonation_advance: "Urgent-money / impersonation", bank_alert: "Bank alert", otp_notice: "OTP message", bill_reminder: "Bill reminder", govt_notice: "Govt notice", delivery_update: "Delivery", general: "Personal" }[k] || k);

/* ---------- pages */
async function pageDashboard() {
  const [s, list] = await Promise.all([api("/api/stats"), api("/api/checks")]);
  const h = new Date().getHours(), greet = h < 12 ? "Good morning" : h < 17 ? "Good afternoon" : "Good evening";
  const first = state.me.name.split(" ")[0];
  const msg = s.checks ? `${s.scams} of your ${s.checks} checks were scams. Every one you caught is money that stayed in your pocket.` : "Paste your first message and Kagzi will tell you if it is real.";
  const maxK = Math.max(1, ...s.kinds.map(k => k.n));
  view.innerHTML = `
  <section class="greet"><div><h2>${greet}, ${esc(first)}.</h2><p>${esc(msg)}</p><div style="display:flex;gap:10px;flex-wrap:wrap"><a class="btn accent" href="#/check">Check a message</a><a class="btn" style="background:rgba(255,255,255,.12);color:#fff;border-color:rgba(255,255,255,.25)" href="#/family">Family circle</a><a class="btn" style="background:rgba(255,255,255,.12);color:#fff;border-color:rgba(255,255,255,.25)" href="#/learn">Scam guide</a></div></div>
    <div style="display:flex;align-items:center;gap:18px"><div class="gstats"><div class="gchip"><div class="k">Checked</div><div class="v">${s.checks}</div></div><div class="gchip"><div class="k">Scams stopped</div><div class="v">${s.scams}</div></div></div><div>${mascot(104)}</div></div></section>
  <div class="grid g4" style="margin-bottom:14px">
    ${kpi("Messages checked", s.checks, "all time", "#4a3fb0", "🔍")}${kpi("Scams caught", s.scams, "verdict: very likely scam", "#d63448", "⚠")}
    ${kpi("Suspicious", s.suspicious, "needs a second look", "#b86a00", "?")}${kpi("Family alerts", s.alerts, `${s.family} ${s.family === 1 ? "person" : "people"} in your circle`, "#12935f", "♥")}</div>
  <div class="grid g2" style="margin-bottom:14px">
    <div class="card"><h3>Checks in the last 14 days</h3><div class="sub">Each bar is a day</div>${bars14(s.per_day)}</div>
    <div class="card"><h3>Verdicts</h3><div class="sub">How your messages turned out</div>${s.checks ? donut(s) : '<div class="empty">No checks yet.</div>'}
      ${s.kinds.length ? `<h3 style="font-size:14px;margin-top:16px">Top scam types you saw</h3><div style="display:grid;gap:8px;margin-top:8px">${s.kinds.map(k => `<div><div style="display:flex;justify-content:space-between;font-size:13px"><span>${kindName(k.kind)}</span><b>${k.n}</b></div><div class="bar"><span style="width:${k.n / maxK * 100}%"></span></div></div>`).join("")}</div>` : ""}</div></div>
  <div class="card"><div style="display:flex;justify-content:space-between;align-items:center"><div><h3>Recent checks</h3><div class="sub">Click a row to open it</div></div><a class="btn" href="#/history">See all</a></div>
    <table><thead><tr><th>Message</th><th>Verdict</th><th>Type</th><th>When</th></tr></thead><tbody>${list.slice(0, 5).map(c => `<tr class="click" data-id="${c.id}"><td>${esc(c.text.slice(0, 70))}${c.text.length > 70 ? "…" : ""}</td><td>${vpill(c.verdict)}</td><td>${kindName(c.kind)}</td><td class="small mute">${when(c.created_at)}</td></tr>`).join("") || '<tr><td colspan="4"><div class="empty">Nothing here yet. <a href="#/check">Check your first message →</a></div></td></tr>'}</tbody></table></div>`;
  $$("tr.click", view).forEach(tr => tr.onclick = () => openCheck(tr.dataset.id));
}

async function pageCheck() {
  state.family = await api("/api/family"); const samples = await api("/api/samples");
  const pre = sessionStorage.getItem("kz-prefill") || ""; sessionStorage.removeItem("kz-prefill");
  view.innerHTML = `<h1>Check a message</h1><p class="lead">Paste an SMS, WhatsApp message or notice, or upload a photo of it.</p>
  <div class="grid g2e"><div class="card"><h3>1. Add the message</h3><div class="sub">Examples to try</div><div class="chips" id="smp">${samples.map((s, i) => `<button class="chip" data-i="${i}">${esc(s.title.en)}</button>`).join("")}</div>
    <div class="input-area"><textarea id="txt" maxlength="4000" placeholder="Paste the message here…">${esc(pre)}</textarea><span class="count" id="cnt">0 / 4000</span></div>
    <div class="dropzone" id="drop" style="margin-top:12px">📷 Drop a photo of a letter or screenshot here, or <label style="color:var(--indigo2);font-weight:700;cursor:pointer">choose a file<input type="file" id="file" accept="image/*" style="display:none"></label><div class="small" id="ocr-s"></div></div>
    <div style="display:flex;gap:10px;margin-top:14px;align-items:center;flex-wrap:wrap"><span class="small mute">Explain in</span><div class="seg" id="c-lang"><button data-l="en">English</button><button data-l="hi">हिन्दी</button><button data-l="mr">मराठी</button></div>
      <button class="btn" id="clr">Clear</button><button class="btn primary" id="go" style="margin-left:auto" data-magnet>Check this message</button></div></div>
    <div class="card" id="out"><div style="text-align:center;padding:24px 8px">${mascot(96)}<p class="mute">Kagzi is ready. Add a message and press Check.</p></div></div></div>`;
  const setLangSeg = () => $$("#c-lang button").forEach(b => b.classList.toggle("on", b.dataset.l === state.lang)); setLangSeg();
  $$("#c-lang button").forEach(b => b.onclick = () => { setLang(b.dataset.l, true); setLangSeg(); if (state.last && $("#txt").value.trim()) run(); });
  const cnt = () => $("#cnt").textContent = `${$("#txt").value.length} / 4000`; cnt(); $("#txt").addEventListener("input", cnt);
  $$("#smp .chip").forEach(b => b.onclick = () => { $("#txt").value = samples[+b.dataset.i].text; cnt(); run(); });
  $("#clr").onclick = () => { $("#txt").value = ""; cnt(); $("#ocr-s").textContent = ""; $("#out").innerHTML = `<div class="empty">Cleared.</div>`; state.last = null; };
  $("#go").onclick = run;
  const drop = $("#drop"); ["dragover", "dragenter"].forEach(ev => drop.addEventListener(ev, e => { e.preventDefault(); drop.classList.add("over"); }));
  ["dragleave", "drop"].forEach(ev => drop.addEventListener(ev, e => { e.preventDefault(); drop.classList.remove("over"); }));
  drop.addEventListener("drop", e => e.dataTransfer.files[0] && ocr(e.dataTransfer.files[0])); $("#file").onchange = e => e.target.files[0] && ocr(e.target.files[0]);
  if (pre) run();
}
let tess;
async function ocr(file) {
  const s = $("#ocr-s");
  if (!file.type.startsWith("image/")) { s.textContent = "Please choose an image file."; return; }
  if (file.size > 8e6) { s.textContent = "That image is over 8 MB. Please choose a smaller one."; return; }
  try {
    s.innerHTML = `<span class="spin"></span> Reading the photo…`;
    const b64 = await new Promise((res, rej) => { const fr = new FileReader(); fr.onload = () => res(fr.result); fr.onerror = () => rej(new Error("Could not open that file.")); fr.readAsDataURL(file); });
    const sr = await fetch("/api/ocr", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ image: b64 }) });
    if (sr.ok) { const j = await sr.json(); if (j.text) { $("#txt").value = j.text.slice(0, 4000); $("#cnt").textContent = `${$("#txt").value.length} / 4000`; s.textContent = "Text read from the photo (Amazon Textract). Please check it, then press Check."; return; } }
    /* 501 (not enabled) or any other server-side failure: read the photo in the browser instead */
    s.innerHTML = `<span class="spin"></span> Loading the text reader…`;
    if (!tess) await new Promise((res, rej) => { const sc = document.createElement("script"); sc.src = "https://cdn.jsdelivr.net/npm/tesseract.js@5.1.1/dist/tesseract.min.js"; sc.onload = res; sc.onerror = () => rej(new Error("The text reader could not be loaded. Check your internet, or paste the text instead.")); document.head.appendChild(sc); });
    tess = true;
    const r = await Tesseract.recognize(file, state.lang === "en" ? "eng" : "eng+hin", { logger: m => { if (m.status === "recognizing text") s.innerHTML = `<span class="spin"></span> Reading… ${Math.round(m.progress * 100)}%`; } });
    const t = (r.data.text || "").replace(/\n{2,}/g, "\n").trim();
    if (!t) { s.textContent = "No text found in that photo. Try a clearer picture, or paste the text."; return; }
    $("#txt").value = t.slice(0, 4000); $("#cnt").textContent = `${$("#txt").value.length} / 4000`; s.textContent = "Text read from the photo. Please check it, then press Check."; toast("Text read from your photo");
  } catch (e) { s.textContent = e.message; }
}
async function run() {
  const text = $("#txt").value.trim(); if (!text) { toast("Add a message first."); $("#txt").focus(); return; }
  const b = $("#go"), l = b.innerHTML; b.disabled = true; b.innerHTML = `<span class="spin"></span> Checking…`;
  try { const r = await api("/api/analyze", { text, lang: state.lang }); state.last = r; showResult($("#out"), r, text); }
  catch (e) { toast(e.message); } finally { b.disabled = false; b.innerHTML = l; }
}
function showResult(box, r, text) {
  const fam = state.family.length ? `<select id="fam" style="width:auto;padding:8px 10px">${state.family.map(f => `<option value="${f.id}">${esc(f.name)} (${esc(f.relation)})</option>`).join("")}</select><button class="btn" id="alert">♥ Alert family</button>` : `<a class="btn" href="#/family">♥ Add family to alert</a>`;
  box.innerHTML = resultHtml(r, { actions: `<div style="display:flex;gap:8px;margin-top:16px;flex-wrap:wrap;align-items:center"><button class="btn primary" id="say">🔊 Read aloud</button><button class="btn" id="copy">Copy summary</button>
    ${r.verdict !== "genuine" ? `<button class="btn danger" id="rep">Report scam</button>` : ""}${fam}</div><div class="small mute" style="margin-top:10px">Saved to your history.</div>` });
  $("#say", box).onclick = () => speak(resultText(r), r.lang);
  $("#copy", box).onclick = async () => { try { await navigator.clipboard.writeText(`Kagaz Saathi: ${r.verdict_label} (${r.kind_label}, risk ${r.risk}/100)\n${r.explanation}\n${r.steps.join("\n")}`); toast("Summary copied"); } catch (e) { toast("Could not copy on this browser."); } };
  const rep = $("#rep", box); if (rep) rep.onclick = async () => { await api("/api/check/report", { id: r.id }); window.open("https://sancharsaathi.gov.in", "_blank", "noopener"); toast("Marked as reported. If you lost money, call 1930 now."); rep.disabled = true; rep.textContent = "Reported ✓"; };
  const al = $("#alert", box); if (al) al.onclick = async () => { al.disabled = true; try { const o = await api("/api/family/alert", { check_id: r.id, member_id: +$("#fam", box).value }); toast(`Alert for ${o.to} saved in your outbox`); al.textContent = "Alerted ✓"; } catch (e) { toast(e.message); al.disabled = false; } };
  FX.bind(box);
}

async function pageHistory() {
  const rows = await api("/api/checks"); const f = state.hf || (state.hf = { v: "all", q: "" });
  const counts = { all: rows.length, scam: 0, suspicious: 0, genuine: 0 }; rows.forEach(r => counts[r.verdict]++);
  const draw = () => {
    const q = f.q.toLowerCase(); const list = rows.filter(r => (f.v === "all" || r.verdict === f.v) && (!q || r.text.toLowerCase().includes(q)));
    $("#hrows").innerHTML = list.map(c => `<tr class="click" data-id="${c.id}"><td>${esc(c.text.slice(0, 90))}${c.text.length > 90 ? "…" : ""}</td><td>${vpill(c.verdict)}${c.reported ? ' <span class="pill gray">reported</span>' : ""}</td><td>${kindName(c.kind)}</td><td class="num small mute">${c.risk}</td><td class="small mute">${when(c.created_at)}</td><td><button class="icon-btn" data-del="${c.id}" title="Delete" aria-label="Delete">🗑</button></td></tr>`).join("") || `<tr><td colspan="6"><div class="empty">${rows.length ? "No checks match." : 'No checks yet. <a href="#/check">Check a message →</a>'}</div></td></tr>`;
    $$("#hrows tr.click").forEach(tr => tr.onclick = e => { if (!e.target.closest("[data-del]")) openCheck(tr.dataset.id); });
    $$("[data-del]").forEach(b => b.onclick = async e => { e.stopPropagation(); if (b.dataset.arm !== "1") { b.dataset.arm = "1"; b.textContent = "Delete?"; b.classList.add("armed"); setTimeout(() => { if (b.isConnected) { b.dataset.arm = ""; b.textContent = "🗑"; b.classList.remove("armed"); } }, 2500); return; }
      await api("/api/check/delete", { id: +b.dataset.del }); b.closest("tr").classList.add("gone"); toast("Check deleted"); setTimeout(route, 280); });
  };
  view.innerHTML = `<div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px"><div><h1>History</h1><p class="lead">Every message you checked, saved to your account.</p></div>${rows.length ? '<button class="btn" id="exp">⤓ Export JSON</button>' : ""}</div>
  <div class="card"><div style="display:flex;gap:12px;flex-wrap:wrap;margin-bottom:12px;align-items:center"><div class="seg" id="hseg">${[["all", "All"], ["scam", "Scams"], ["suspicious", "Suspicious"], ["genuine", "Genuine"]].map(([k, t]) => `<button data-v="${k}" class="${f.v === k ? "on" : ""}">${t} ${counts[k]}</button>`).join("")}</div>
    <input id="hq" type="search" placeholder="Search your checks…" value="${esc(f.q)}" style="max-width:280px"></div>
    <div style="overflow:auto"><table><thead><tr><th>Message</th><th>Verdict</th><th>Type</th><th>Risk</th><th>When</th><th></th></tr></thead><tbody id="hrows"></tbody></table></div></div>`;
  $$("#hseg button").forEach(b => b.onclick = () => { f.v = b.dataset.v; $$("#hseg button").forEach(x => x.classList.toggle("on", x === b)); draw(); }); $("#hq").oninput = e => { f.q = e.target.value; draw(); }; draw();
  const ex = $("#exp"); if (ex) ex.onclick = () => { const u = URL.createObjectURL(new Blob([JSON.stringify(rows, null, 2)], { type: "application/json" })); const a = document.createElement("a"); a.href = u; a.download = "kagaz_history.json"; a.click(); setTimeout(() => URL.revokeObjectURL(u), 1000); };
}
async function openCheck(id) {
  const c = await api("/api/check?id=" + id); state.family = await api("/api/family");
  $("#dbody").innerHTML = `<h1 style="font-size:20px">Check #${c.id}</h1><p class="small mute">${when(c.created_at)}</p><div class="card" style="margin:12px 0"><div class="small mute">The message</div><p style="white-space:pre-wrap;margin:6px 0 0">${esc(c.text)}</p></div><div class="card" id="dres"></div>`;
  showResult($("#dres"), Object.assign(c.result, { id: c.id }), c.text); $("#dres").querySelector(".small.mute:last-child")?.remove();
  $("#drawer").classList.add("open");
}

async function pageFamily() {
  const [fam, box] = await Promise.all([api("/api/family"), api("/api/outbox")]); state.family = fam;
  view.innerHTML = `<h1>Family circle</h1><p class="lead">People who are alerted when you check a risky message. Add up to 10.</p>
  <div class="grid g2e"><div class="card"><h3>Your circle</h3><div class="sub">${fam.length} of 10</div><div class="hl">${fam.map(f => `<div class="hlc"><div><b>${esc(f.name)}</b> <span class="pill gray">${esc(f.relation)}</span><div class="small mute">${esc(f.contact)}</div></div><button class="icon-btn" data-df="${f.id}">Remove</button></div>`).join("") || '<div class="empty">Nobody added yet.</div>'}</div>
    <h3 style="font-size:15px;margin-top:20px">Add someone</h3><form id="ff" class="grid" style="gap:10px;margin-top:8px" novalidate><label class="f">Name<input id="fn" maxlength="40" placeholder="Neha"></label><label class="f">Relation<input id="fr" maxlength="30" placeholder="Daughter"></label>
      <label class="f">Mobile number or email<input id="fc" placeholder="98765 43210 or neha@example.com"></label><div class="small" id="fe" style="color:var(--bad)"></div><button class="btn primary">Add to circle</button></form></div>
    <div class="card"><h3>Alert outbox</h3><div class="sub">${state.demo ? "Demo mode: alerts are saved here instead of being sent." : "Alerts that were prepared for your family."}</div>
      <div class="hl">${box.map(o => `<div class="hlc" style="align-items:flex-start"><div><b>To ${esc(o.member_name)}</b> <span class="small mute">${when(o.created_at)}</span><div class="small" style="white-space:pre-wrap;margin-top:4px">${esc(o.body)}</div></div></div>`).join("") || '<div class="empty">No alerts yet. Check a message and press "Alert family".</div>'}</div></div></div>`;
  $$("[data-df]").forEach(b => b.onclick = async () => { await api("/api/family/delete", { id: +b.dataset.df }); toast("Removed"); route(); });
  $("#ff").onsubmit = async e => { e.preventDefault(); $("#fe").textContent = ""; try { await api("/api/family", { name: $("#fn").value, relation: $("#fr").value, contact: $("#fc").value }); toast("Added to your circle"); route(); } catch (err) { $("#fe").textContent = err.message; } };
}

async function pageLearn() {
  const items = await api("/api/learn?lang=" + state.lang);
  view.innerHTML = `<h1>Scam guide</h1><p class="lead">The ten scams Kagzi knows best, in ${LANGS[state.lang]}. Change the language at the top.</p><div class="grid g3">${items.map(i => `<div class="card spot tilt"><h3>${esc(i.label)}</h3><p style="font-size:14.5px;margin:8px 0 12px">${esc(i.why)}</p><div style="display:flex;gap:8px"><button class="btn" data-say="${esc(i.label)}. ${esc(i.why)}">🔊 Listen</button><button class="btn" data-try="${i.kind}">See an example</button></div></div>`).join("")}</div>`;
  $$("[data-say]").forEach(b => b.onclick = () => speak(b.dataset.say, state.lang));
  const EX = { digital_arrest: "This is Inspector Rao from CBI. You are under digital arrest. Stay on the video call and do not tell anyone.", kyc_block: "Your bank account will be blocked today. Update KYC at the link.", otp_theft: "I sent money by mistake. Approve the collect request and enter your UPI PIN to return it.", prize_lottery: "Congratulations! You won Rs 25 lakh. Pay Rs 15,000 processing fee to claim.", job_fraud: "Earn Rs 5,000 daily by liking videos. Pay Rs 500 registration to join.", parcel_customs: "Your parcel is held at customs. Pay Rs 3,850 clearance fee at the link.", bill_cutoff: "Your electricity will be disconnected tonight. Call 98XXXXXX45 now.", refund_fraud: "Income tax refund of Rs 18,540 approved. Enter your bank details at the link.", investment_loan: "Guaranteed 300 percent returns in 15 days. Deposit Rs 20,000.", impersonation_advance: "Hello mom, this is my new number. Please send Rs 15,000 urgently to this account, I will explain later." };
  $$("[data-try]").forEach(b => b.onclick = () => { sessionStorage.setItem("kz-prefill", EX[b.dataset.try] || ""); location.hash = "#/check"; });
  FX.bind(view);
}
async function pageHelp() {
  const h = await api("/api/helplines");
  view.innerHTML = `<h1>Helplines</h1><p class="lead">If money was lost, the first hour matters most. Call 1930 right away.</p><div class="card" style="max-width:760px"><div class="hl">${h.map(x => `<div class="hlc"><div><b>${esc(x.name)}</b><div class="small mute">${esc(x.note)}</div></div><div style="display:flex;gap:8px;align-items:center">${x.number ? `<a class="btn primary" href="tel:${x.number}">📞 ${x.number}</a>` : ""}${x.url ? `<a class="btn" href="${esc(x.url)}" target="_blank" rel="noopener">Open site</a>` : ""}</div></div>`).join("")}</div></div>`;
}
async function pageAccuracy() {
  const m = await api("/api/model"); const pc = m.per_class; const hist = m.history;
  const names = m.classes;
  view.innerHTML = `<h1>Model accuracy</h1><p class="lead">The classifier was trained, tuned on a dev set, and scored once on messages it never saw. No numbers are hidden.</p>
  <div class="grid g4" style="margin-bottom:14px">
    <div class="card kpi"><div><div class="k">Accuracy · ${m.test_size} unseen messages</div><div class="v">${(100 * m.test_accuracy).toFixed(1)}%</div><div class="f">${names.length}-way classification</div></div></div>
    <div class="card kpi"><div><div class="k">Scam vs genuine</div><div class="v">${(100 * m.test_scam_vs_genuine_accuracy).toFixed(1)}%</div><div class="f">verdict-level</div></div></div>
    <div class="card kpi"><div><div class="k">Dev set (settings)</div><div class="v">${(100 * m.dev_accuracy).toFixed(1)}%</div><div class="f">${m.dev_size} messages, used to pick epoch + alpha</div></div></div>
    <div class="card kpi"><div><div class="k">Trained on</div><div class="v">${m.train_size.toLocaleString("en-IN")}</div><div class="f">epoch ${m.best_epoch}, alpha ${m.alpha}</div></div></div></div>
  <div class="grid g2"><div class="card"><h3>Training curve</h3><div class="sub">Accuracy by epoch (train vs dev)</div>${curve(hist)}</div>
    <div class="card"><h3>Per type (F1)</h3><div class="sub">Test set</div><div style="display:grid;gap:7px">${names.map(n => `<div><div style="display:flex;justify-content:space-between;font-size:12.5px"><span>${kindName(n)}</span><b>${(100 * pc[n]["f1-score"]).toFixed(0)}%</b></div><div class="bar"><span style="width:${100 * pc[n]["f1-score"]}%"></span></div></div>`).join("")}</div></div></div>
  <div class="card" style="margin-top:14px"><h3>Confusion matrix</h3><div class="sub">Rows = truth, columns = prediction</div><div style="overflow:auto"><table class="cm"><thead><tr><th></th>${names.map(n => `<th title="${n}">${kindName(n).slice(0, 7)}</th>`).join("")}</tr></thead><tbody>${m.confusion.map((row, i) => `<tr><th style="text-align:right">${kindName(names[i]).slice(0, 12)}</th>${row.map((v, j) => `<td style="background:${v ? (i === j ? `rgba(18,147,95,${Math.min(.55, .12 + v / 25)})` : "rgba(214,52,72,.5)") : "transparent"}">${v || ""}</td>`).join("")}</tr>`).join("")}</tbody></table></div></div>
  ${stressCard(m.stress)}
  <div class="card" style="margin-top:14px"><h3>What it got wrong</h3>${m.errors.length ? m.errors.map(e => `<p class="small"><span class="pill bad">${kindName(e.true)} → ${kindName(e.pred)}</span> ${esc(e.text)}</p>`).join("") : '<p class="mute">Nothing.</p>'}
    <p class="small mute" style="margin-top:12px"><b>Honest limits.</b> The test messages were hand-written by the same team that built the model, in English, Hinglish and Hindi. Real-world messages are wilder, so expect lower accuracy on new scam styles. That is why every verdict also shows transparent rules and reasons, and Kagzi always tells you to verify in the official app.</p></div>`;
}
function stressCard(st) {
  if (!st) return "";
  const row = (name, x, note) => `<tr><td><b>${name}</b><div class="small mute">${note}</div></td><td class="num">${x.n}</td><td class="num">${(100 * x.scam_flagged_rate).toFixed(0)}%</td><td class="num">${(100 * x.scam_caught_as_scam_rate).toFixed(0)}%</td><td class="num">${(100 * x.genuine_clean_rate).toFixed(0)}%</td><td class="num">${(100 * x.genuine_false_scam_rate).toFixed(0)}%</td></tr>`;
  return `<div class="card" style="margin-top:14px"><h3>Hard stress tests</h3><div class="sub">Tricky messages: real ones that sound scary, and scams in unusual wording. Whole pipeline (model + rules).</div>
  <div style="overflow:auto"><table><thead><tr><th>Set</th><th>Msgs</th><th>Scams flagged</th><th>Scams called "scam"</th><th>Genuine left alone</th><th>Genuine called "scam"</th></tr></thead><tbody>
  ${row("Stress set 1", st.stress, "used to find weaknesses, then fixed (new scam type + hard-negative training data)")}${row("Stress set 2", st.stress2, "written after the fixes, never used to tune")}</tbody></table></div>
  <p class="small mute" style="margin-top:10px">"Flagged" means suspicious or scam. A real message marked "suspicious" is the cautious error; marking a real one "scam" is the costly one, and it did not happen on either set.</p></div>`;
}
function curve(h) {
  const W = 520, H = 190, pad = 34, x = i => pad + i * (W - pad - 8) / Math.max(1, h.length - 1), lo = Math.min(...h.map(p => Math.min(p.train_acc, p.dev_acc)), .9), y = v => 12 + (1 - (v - lo) / (1 - lo + 1e-9)) * (H - 44);
  const path = k => h.map((p, i) => (i ? "L" : "M") + x(i).toFixed(1) + "," + y(p[k]).toFixed(1)).join("");
  return `<svg viewBox="0 0 ${W} ${H}" width="100%" role="img" aria-label="Training curve">${[0, .5, 1].map(f => { const v = lo + f * (1 - lo); return `<line x1="${pad}" x2="${W - 8}" y1="${y(v)}" y2="${y(v)}" stroke="var(--line2)"/><text x="${pad - 6}" y="${y(v) + 4}" text-anchor="end" font-size="10" fill="var(--mute)">${(100 * v).toFixed(0)}%</text>`; }).join("")}
  <path d="${path("train_acc")}" fill="none" stroke="var(--indigo2)" stroke-width="2.4"/><path d="${path("dev_acc")}" fill="none" stroke="var(--saffron)" stroke-width="2.4" stroke-dasharray="5 4"/>
  <text x="${W / 2}" y="${H - 6}" text-anchor="middle" font-size="10" fill="var(--mute)">epoch</text></svg><div class="small mute"><b style="color:var(--indigo2)">━</b> train &nbsp; <b style="color:var(--saffron)">╍</b> dev</div>`;
}
async function pageSettings() {
  const u = state.me;
  view.innerHTML = `<h1>Settings</h1><p class="lead">${state.demo ? "This is a demo account, so it can't be edited. Create your own account to save changes." : "Your name, household and language."}</p>
  <div class="grid g2e"><div class="card"><h3>Profile</h3><form id="pf" class="grid" style="gap:12px;margin-top:10px" novalidate><label class="f">Your name<input id="pn" value="${esc(u.name)}" maxlength="60" ${state.demo ? "disabled" : ""}></label><label class="f">Household name<input id="ph" value="${esc(u.home)}" maxlength="60" ${state.demo ? "disabled" : ""}></label>
    <label class="f">Default language<select id="pl" ${state.demo ? "disabled" : ""}>${Object.entries(LANGS).map(([k, v]) => `<option value="${k}" ${u.lang === k ? "selected" : ""}>${v}</option>`).join("")}</select></label><label class="f">Email<input value="${esc(u.email)}" disabled></label>
    <div style="display:flex;gap:10px;align-items:center"><button class="btn primary" ${state.demo ? "disabled" : ""}>Save changes</button><span class="small" id="pm"></span></div></form></div>
    <div class="card"><h3>Privacy and security</h3><table><tbody><tr><td>Passwords</td><td>Stored only as salted PBKDF2-SHA256 hashes</td></tr><tr><td>Sessions</td><td>Random token in an HttpOnly cookie, 7 days</td></tr><tr><td>Your checks</td><td>Visible only to you; delete any time from History</td></tr><tr><td>Member since</td><td>${when(u.created_at)}</td></tr></tbody></table><div style="margin-top:14px"><button class="btn" id="so">Sign out</button></div></div></div>`;
  $("#so").onclick = signOut;
  $("#pf").onsubmit = async e => { e.preventDefault(); try { const r = await api("/api/profile", { name: $("#pn").value, home: $("#ph").value, lang: $("#pl").value }); setMe(r.user, state.demo); setLang(r.user.lang, true); $("#pm").textContent = "✓ Saved"; toast("Profile saved"); } catch (err) { $("#pm").textContent = err.message; $("#pm").style.color = "var(--bad)"; } };
}

/* ---------- router */
const PAGES = { dashboard: ["Dashboard", pageDashboard], check: ["Check a message", pageCheck], history: ["History", pageHistory], family: ["Family", pageFamily], learn: ["Scam guide", pageLearn], help: ["Helplines", pageHelp], accuracy: ["Model accuracy", pageAccuracy], settings: ["Settings", pageSettings] };
async function route() {
  const key = (location.hash.replace(/^#\//, "") || "dashboard").split("?")[0]; const [title, fn] = PAGES[key] || PAGES.dashboard; state.page = key;
  $("#drawer").classList.remove("open"); $("#side").classList.remove("open"); speechSynthesis && speechSynthesis.cancel && speechSynthesis.cancel();
  $$(".side nav a").forEach(a => a.classList.toggle("on", a.dataset.p === key)); $("#c-page").textContent = title; document.title = "Kagaz Saathi · " + title;
  view.innerHTML = `<div class="empty"><span class="spin"></span></div>`;
  try { await fn(); } catch (e) { view.innerHTML = `<div class="card"><h3>Something went wrong</h3><p class="mute">${esc(e.message)}</p></div>`; }
  view.classList.remove("page-in"); void view.offsetWidth; view.classList.add("page-in"); $$(".card", view).forEach(c => c.classList.add("spot")); FX.bind(view);
}
window.addEventListener("hashchange", route);
(async () => {
  try { const d = await api("/api/auth/me", undefined, {}); if (!d.user) { location.href = "/signin?next=/app"; return; } setMe(d.user, d.demo); let sl = d.user.lang; try { sl = localStorage.getItem("kz-lang") || sl; } catch (e) { } setLang(sl, true); route(); }
  catch (e) { /* api() already redirects on 401 */ }
})();
