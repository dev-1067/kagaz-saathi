"use strict";
$("#logo").innerHTML = LOGO + `<span>Kagaz Saathi<small>कागज़ साथी</small></span>`;
$("#logo2").innerHTML = LOGO + `<span>Kagaz Saathi</span>`;
$("#hero-owl").innerHTML = mascot(150, "alert");
setTimeout(() => { $("#g1").style.width = "96%"; }, 600);
const nav = $("#nav");
addEventListener("scroll", () => nav.classList.toggle("scrolled", scrollY > 8), { passive: true });
$("#burger").onclick = () => { const o = !$("#mmenu").classList.contains("open"); $("#mmenu").classList.toggle("open", o); $("#burger").setAttribute("aria-expanded", o); };
$$("#mmenu a").forEach(a => a.onclick = () => { $("#mmenu").classList.remove("open"); $("#burger").setAttribute("aria-expanded", "false"); });

fetch("/api/auth/me").then(r => r.json()).then(d => {
  if (!d.user) return;
  $("#n-in").textContent = "Hi, " + d.user.name.split(" ")[0]; $("#n-in").href = "/app";
  $("#n-up").textContent = "Open dashboard"; $("#n-up").href = "/app";
}).catch(() => { });

async function demo(btn) {
  const l = btn.innerHTML; btn.disabled = true; btn.innerHTML = `<span class="spin"></span> Opening…`;
  try { await api("/api/auth/demo", { persona: "parent" }, { noRedirect: true }); location.href = "/app"; }
  catch (e) { toast(e.message); btn.disabled = false; btn.innerHTML = l; }
}
$("#demo-btn").onclick = e => demo(e.currentTarget); $("#demo-btn2").onclick = e => demo(e.currentTarget);

fetch("/api/public/stats").then(r => r.json()).then(s => {
  const pct = x => +(100 * x).toFixed(1);
  $("#h-acc").textContent = pct(s.accuracy) + "%";
  const set = (id, v) => { const el = $(id); el.dataset.count = v; el.classList.remove("counted"); };
  set("#p-acc", pct(s.accuracy)); set("#p-sg", pct(s.scam_vs_genuine)); set("#p-cls", s.classes);
  $("#p-n").textContent = `${s.test_size} unseen messages · trained on ${s.train_size.toLocaleString("en-IN")}`;
  FX.bind();
}).catch(() => { });

let lang = "en", samples = [];
$$("#t-lang button").forEach(b => b.onclick = () => { lang = b.dataset.l; $$("#t-lang button").forEach(x => x.classList.toggle("on", x === b)); if ($("#t-text").value.trim()) check(); });
$("#t-text").addEventListener("input", e => $("#t-count").textContent = `${e.target.value.length} / 4000`);
fetch("/api/samples").then(r => r.json()).then(list => {
  samples = list;
  $("#samples").innerHTML = list.map((s, i) => `<button class="chip" data-i="${i}">${esc(s.title.en)}</button>`).join("");
  $$("#samples .chip").forEach(b => b.onclick = () => { $("#t-text").value = samples[+b.dataset.i].text; $("#t-count").textContent = `${$("#t-text").value.length} / 4000`; check(); });
});
async function check() {
  const text = $("#t-text").value.trim();
  if (!text) { toast("Paste a message or pick an example first."); $("#t-text").focus(); return; }
  const btn = $("#t-go"); btn.disabled = true; const l = btn.innerHTML; btn.innerHTML = `<span class="spin"></span> Checking…`;
  try {
    const r = await api("/api/public/analyze", { text, lang }, { noRedirect: true });
    $("#t-out").innerHTML = resultHtml(r, { actions: `<div style="display:flex;gap:10px;margin-top:14px;flex-wrap:wrap"><button class="btn" id="t-say">🔊 Read aloud</button><a class="btn primary" href="/signup">Save and alert family</a></div>` });
    $("#t-say").onclick = () => speak(resultText(r), lang);
    FX.bind($("#t-out"));
  } catch (e) { toast(e.message); }
  finally { btn.disabled = false; btn.innerHTML = l; }
}
$("#t-go").onclick = check;

// Share target: "Share -> Kagaz Saathi" from WhatsApp or SMS lands here with the message already filled in and checked.
if ("serviceWorker" in navigator) navigator.serviceWorker.register("/sw.js").catch(() => { });
(() => {
  const q = new URLSearchParams(location.search);
  const shared = [q.get("title"), q.get("text"), q.get("url")].filter(Boolean).join(" ").trim().slice(0, 4000);
  if (!shared || location.pathname !== "/share") return;
  $("#t-text").value = shared;
  $("#t-count").textContent = `${shared.length} / 4000`;
  history.replaceState(null, "", "/");
  $("#try").scrollIntoView();
  check();
})();
