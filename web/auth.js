"use strict";
$("#logo").innerHTML = LOGO + `<span>Kagaz Saathi</span>`;
$("#owl").innerHTML = mascot(120);
const EMAIL = /^[^@\s]+@[^@\s]+\.[A-Za-z]{2,}$/;
let mode = /signup/.test(location.pathname) ? "up" : "in";
const next = new URLSearchParams(location.search).get("next");
const target = next && next.startsWith("/") && !next.startsWith("//") ? next : "/app";
function clear() { $$(".field").forEach(f => { f.classList.remove("bad"); $(".err", f).textContent = ""; }); $("#ferr").classList.remove("on"); }
function setMode(m, push) {
  mode = m; const up = m === "up";
  $("#tabs").classList.toggle("up", up); $("#tab-in").classList.toggle("on", !up); $("#tab-up").classList.toggle("on", up);
  $$(".up").forEach(e => e.style.display = up ? "" : "none");
  $("#title").textContent = up ? "Create your account" : "Welcome back"; $("#sub").textContent = up ? "Free, takes under a minute." : "Sign in to your Kagaz Saathi.";
  $("#go").textContent = up ? "Create account" : "Sign in"; $("#password").autocomplete = up ? "new-password" : "current-password";
  $("#swap").innerHTML = up ? `Already have an account? <a href="/signin" data-m="in">Sign in</a>` : `New here? <a href="/signup" data-m="up">Create an account</a>`;
  $("#swap a").onclick = e => { e.preventDefault(); setMode(e.target.dataset.m, true); };
  document.title = up ? "Kagaz Saathi · Create account" : "Kagaz Saathi · Sign in"; clear();
  if (push) history.replaceState(null, "", (up ? "/signup" : "/signin") + location.search);
}
$$("#tabs button").forEach(b => b.onclick = () => setMode(b.dataset.m, true));
$$(".field input").forEach(i => i.addEventListener("input", () => { const f = i.closest(".field"); f.classList.remove("bad"); $(".err", f).textContent = ""; }));
$("#password").addEventListener("input", e => {
  if (mode !== "up") return; const p = e.target.value;
  const s = (p.length >= 8) + (p.length >= 12) + (/[a-z]/.test(p) && /[A-Z]/.test(p)) + /\d/.test(p) + /[^A-Za-z0-9]/.test(p);
  $("#meter").style.width = (s / 5 * 100) + "%"; $("#meter").style.background = s <= 1 ? "#d63448" : s <= 3 ? "#e0762a" : "#12935f";
  $("#mlabel").textContent = p ? ["Too weak", "Weak", "Okay", "Good", "Strong", "Very strong"][s] : "8+ characters with a letter and a number.";
});
$("#peek").onclick = () => { const p = $("#password"), s = p.type === "password"; p.type = s ? "text" : "password"; $("#peek").textContent = s ? "Hide" : "Show"; };
const bad = (id, m) => { const f = $("#f-" + id); f.classList.add("bad"); $(".err", f).textContent = m; };
function validate() {
  clear(); let ok = true; const em = $("#email").value.trim(), pw = $("#password").value;
  if (mode === "up" && $("#name").value.trim().length < 2) { bad("name", "Please enter your name."); ok = false; }
  if (!EMAIL.test(em)) { bad("email", "Please enter a valid email address."); ok = false; }
  if (mode === "up" && (pw.length < 8 || !/[A-Za-z]/.test(pw) || !/\d/.test(pw))) { bad("password", "Use at least 8 characters, with a letter and a number."); ok = false; }
  if (mode === "in" && !pw) { bad("password", "Please enter your password."); ok = false; }
  if (!ok) { const f = $(".field.bad input"); f && f.focus(); } return ok;
}
function busy(btn, on, txt) { btn.disabled = on; if (on) { btn._l = btn.innerHTML; btn.innerHTML = `<span class="spin"></span> ${txt}`; } else if (btn._l) btn.innerHTML = btn._l; }
$("#form").addEventListener("submit", async e => {
  e.preventDefault(); if (!validate()) return; const b = $("#go"); busy(b, true, mode === "up" ? "Creating…" : "Signing in…");
  try {
    const body = { email: $("#email").value.trim(), password: $("#password").value };
    if (mode === "up") Object.assign(body, { name: $("#name").value.trim(), home: $("#home").value.trim() });
    await api(mode === "up" ? "/api/auth/signup" : "/api/auth/login", body, { noRedirect: true }); location.href = target;
  } catch (err) { $("#ferr").textContent = err.message; $("#ferr").classList.add("on"); busy(b, false); }
});
$$(".demos button").forEach(b => b.onclick = async () => {
  busy(b, true, "…");
  try { await api("/api/auth/demo", { persona: b.dataset.p }, { noRedirect: true }); location.href = target; }
  catch (err) { $("#ferr").textContent = err.message; $("#ferr").classList.add("on"); busy(b, false); }
});
setMode(mode);
