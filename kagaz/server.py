"""Kagaz Saathi web app server (Python standard library + SQLite).

    python -m kagaz.server            then open http://localhost:8030

Pages: /  landing · /signin, /signup  · /app  the dashboard (needs a session)
Public API:  POST /api/public/analyze   (no account, rate limited, nothing saved)   GET /api/public/stats  GET /api/samples
Account API (JSON): /api/auth/{signup,login,demo,logout,me}  /api/profile
App API (need a session): POST /api/analyze · GET /api/checks, /api/check?id= · POST /api/check/delete, /api/check/report
                          GET/POST /api/family, /api/family/delete · POST /api/family/alert · GET /api/outbox · GET /api/stats · GET /api/model
"""
import argparse
import json
import mimetypes
import re
import time
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, quote, urlparse

from . import aws
from . import content as C
from .analyzer import analyze
from .store import AuthError, DEMOS, Store

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "web"
COOKIE = "kagaz_session"
DB = Store()
PUBLIC = {"/api/auth/signup", "/api/auth/login", "/api/auth/demo", "/api/auth/logout", "/api/auth/me", "/api/public/analyze", "/api/public/stats",
          "/api/samples", "/api/model"}

SAMPLES = [
    {"id": "digital_arrest", "title": {"en": "Police 'digital arrest' call", "hi": "पुलिस 'डिजिटल अरेस्ट' कॉल", "mr": "पोलीस 'डिजिटल अरेस्ट' कॉल"},
     "text": "This is Inspector Rao from CBI. A parcel in your name has drugs. You are under digital arrest. Stay on the video call and do not tell anyone, or pay Rs 85,000 to the RBI safe account."},
    {"id": "kyc", "title": {"en": "Bank KYC link", "hi": "बैंक KYC लिंक", "mr": "बँक KYC लिंक"},
     "text": "Dear customer your SBI account will be blocked today. Update KYC now at sbi-kyc-update.in and enter your card details."},
    {"id": "otp", "title": {"en": "Real OTP message", "hi": "असली OTP संदेश", "mr": "खरा OTP संदेश"},
     "text": "482915 is your OTP for login to your account. Valid for 10 minutes. Do not share it with anyone, including bank staff."},
    {"id": "bill", "title": {"en": "Electricity cut-off threat", "hi": "बिजली कटने की धमकी", "mr": "वीज तोडण्याची धमकी"},
     "text": "Dear consumer, your electricity connection will be disconnected tonight at 9:30 pm as last month bill is unpaid. Call 98XXXXXX45 now."},
    {"id": "bank", "title": {"en": "Bank debit alert", "hi": "बैंक डेबिट सूचना", "mr": "बँक डेबिट सूचना"},
     "text": "INR 1,250.00 debited from A/c XX4821 on 18-Nov at Zomato. Avl bal INR 14,320.55. Not you? Call the number on the back of your card."},
    {"id": "job", "title": {"en": "Task job offer", "hi": "टास्क जॉब ऑफर", "mr": "टास्क जॉब ऑफर"},
     "text": "Part time work from home, earn Rs 5,000 daily by liking YouTube videos. Join our Telegram group and pay Rs 500 registration."},
    {"id": "pension", "title": {"en": "Pension life certificate", "hi": "पेंशन जीवन प्रमाणपत्र", "mr": "पेन्शन जीवन प्रमाणपत्र"},
     "text": "Dear pensioner, please submit your Jeevan Pramaan life certificate by 30-Nov through the bank or post office to continue pension."},
]
SEED = {"parent": [SAMPLES[0]["text"], SAMPLES[1]["text"], SAMPLES[4]["text"], SAMPLES[6]["text"]],
        "student": [SAMPLES[5]["text"], SAMPLES[3]["text"], SAMPLES[2]["text"]],
        "family": [SAMPLES[1]["text"], SAMPLES[4]["text"]]}


def seed_demo(uid, persona):
    if DB.checks(uid):
        return
    for i, t in enumerate(SEED.get(persona, [])):
        res = analyze(t, DB.user(uid)["lang"])
        cid = DB.save_check(uid, t, res)
        DB.c.execute("UPDATE checks SET created_at=? WHERE id=?", (time.time() - (len(SEED[persona]) - i) * 86400 * 1.5, cid))
    DB.c.commit()
    if persona == "parent":
        DB.add_family(uid, "Neha", "Daughter", "neha@example.com")
        DB.add_family(uid, "Amit", "Son", "+91 98765 43210")


def alert_text(user, rec, lang):
    snippet = re.sub(r"\s+", " ", rec["text"]).strip()[:140]
    head = {"en": f"{user['name']} checked a message with Kagaz Saathi: {C.VERDICT[rec['verdict']]['en']} ({C.LABELS[rec['kind']]['en']}).",
            "hi": f"{user['name']} ने कागज़ साथी से एक संदेश जांचा: {C.VERDICT[rec['verdict']]['hi']} ({C.LABELS[rec['kind']]['hi']}).",
            "mr": f"{user['name']} यांनी कागज़ साथीने एक संदेश तपासला: {C.VERDICT[rec['verdict']]['mr']} ({C.LABELS[rec['kind']]['mr']})."}[lang]
    tail = {"en": "Please call them, and do not click links or send money. National cyber-fraud helpline: 1930.",
            "hi": "कृपया उन्हें फोन करें। लिंक न खोलें, पैसे न भेजें। साइबर ठगी हेल्पलाइन: 1930.",
            "mr": "कृपया त्यांना फोन करा. लिंक उघडू नका, पैसे पाठवू नका. सायबर फसवणूक हेल्पलाइन: 1930."}[lang]
    return f"{head}\n\"{snippet}\"\n{tail}"


class H(BaseHTTPRequestHandler):
    server_version = "KagazSaathi/1.0"

    def log_message(self, *a):
        pass

    # ---- plumbing
    def _send(self, code, body, ctype="application/json", extra=None):
        data = body if isinstance(body, bytes) else json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype + ("; charset=utf-8" if ctype.startswith(("application/json", "text/")) else ""))
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(data)

    def _body(self):
        try:
            return json.loads(self.rfile.read(min(int(self.headers.get("Content-Length") or 0), 30_000)) or b"{}")
        except (json.JSONDecodeError, ValueError):
            return {}

    def _token(self):
        c = SimpleCookie(self.headers.get("Cookie") or "")
        return c[COOKIE].value if COOKIE in c else None

    def _user(self):
        if not hasattr(self, "_u"):
            self._u = DB.session_user(self._token())
        return self._u

    def _secure(self):
        return "; Secure" if (self.headers.get("X-Forwarded-Proto") or "").lower() == "https" else ""

    def _login(self, uid, **extra):
        tok = DB.new_session(uid)
        self._send(200, {"ok": True, "user": DB.user(uid), **extra},
                   extra={"Set-Cookie": f"{COOKIE}={tok}; Path=/; HttpOnly; SameSite=Lax; Max-Age={7 * 86400}{self._secure()}"})

    def _redirect(self, to):
        self.send_response(302)
        self.send_header("Location", to)
        self.send_header("Content-Length", "0")
        self.end_headers()

    def _page(self, name):
        self._send(200, (WEB / name).read_bytes(), "text/html")

    def _limit(self, kind, key, n, per):
        try:
            return DB.hit(f"{kind}#{key}", n, per)
        except Exception:  # never block real users because the counter failed
            return True

    # ---- GET
    def do_GET(self):
        url = urlparse(self.path)
        q = {k: v[0] for k, v in parse_qs(url.query).items()}
        p = url.path
        try:
            if p in ("/", "/index.html", "/share"):
                return self._page("landing.html")
            if p in ("/signin", "/signup", "/login"):
                return self._redirect("/app") if self._user() else self._page("auth.html")
            if p in ("/app", "/app/"):
                return self._page("app.html") if self._user() else self._redirect("/signin?next=" + quote("/app"))
            if p.startswith("/api/") and p not in PUBLIC and not self._user():
                return self._send(401, {"error": "Please sign in first."})
            u = self._user()
            if p == "/api/auth/me":
                return self._send(200, {"user": u, "demo": DB.is_demo(u)})
            if p == "/api/samples":
                return self._send(200, SAMPLES)
            if p == "/api/public/stats":
                rep = json.loads((ROOT / "results" / "model_report.json").read_text(encoding="utf-8"))
                return self._send(200, {"accuracy": rep["test_accuracy"], "test_size": rep["test_size"], "train_size": rep["train_size"],
                                        "classes": len(rep["classes"]), "scam_vs_genuine": rep["test_scam_vs_genuine_accuracy"]})
            if p == "/api/model":
                rep = json.loads((ROOT / "results" / "model_report.json").read_text(encoding="utf-8"))
                sp = ROOT / "results" / "stress_report.json"
                rep["stress"] = json.loads(sp.read_text(encoding="utf-8")) if sp.exists() else None
                bp = ROOT / "results" / "blind6_report.json"
                rep["blind"] = json.loads(bp.read_text(encoding="utf-8")) if bp.exists() else None
                return self._send(200, rep)
            if p == "/api/learn":
                lg = q.get("lang") if q.get("lang") in ("en", "hi", "mr") else u["lang"]
                return self._send(200, [{"kind": k, "label": C.LABELS[k][lg], "why": C.WHY[k][lg]} for k in C.LABELS if k in C.SCAM])
            if p == "/api/helplines":
                return self._send(200, C.HELPLINES)
            if p == "/api/checks":
                return self._send(200, DB.checks(u["id"]))
            if p == "/api/check":
                r = DB.check(u["id"], int(q.get("id", 0) or 0))
                return self._send(200, r) if r else self._send(404, {"error": "not found"})
            if p == "/api/stats":
                return self._send(200, DB.stats(u["id"]))
            if p == "/api/family":
                return self._send(200, DB.family(u["id"]))
            if p == "/api/outbox":
                return self._send(200, DB.outbox(u["id"]))
            f = (WEB / p.lstrip("/")).resolve()
            if WEB.resolve() in f.parents and f.is_file() and f.suffix != ".html":
                return self._send(200, f.read_bytes(), "application/manifest+json" if f.suffix == ".webmanifest" else mimetypes.guess_type(f.name)[0] or "application/octet-stream")
            if p.startswith("/api/"):
                return self._send(404, {"error": "unknown endpoint"})
            self._send(404, (WEB / "404.html").read_bytes(), "text/html")
        except Exception as e:
            self._send(500, {"error": f"{type(e).__name__}: {e}"})

    # ---- POST
    def do_POST(self):
        p, b, ip = urlparse(self.path).path, self._body(), self.client_address[0]
        try:
            if p.startswith("/api/") and p not in PUBLIC and not self._user():
                return self._send(401, {"error": "Please sign in first."})
            u = self._user()
            if p in ("/api/auth/login", "/api/auth/signup"):
                if not (self._limit("auth", ip, 20, 60) and self._limit("authday", ip, 400, 86400)
                        and (p == "/api/auth/login" or self._limit("signup", ip, 40, 3600))):
                    return self._send(429, {"error": "Too many attempts. Please wait a while and try again."})
                uid = (DB.create_user(b.get("name"), b.get("email"), str(b.get("password") or ""), b.get("home"), b.get("lang") or "en")
                       if p == "/api/auth/signup" else DB.verify(b.get("email"), str(b.get("password") or "")))
                return self._login(uid)
            if p == "/api/auth/demo":
                if not self._limit("demo", ip, 200, 3600):
                    return self._send(429, {"error": "Too many demo sessions from this network. Please wait a while."})
                persona = b.get("persona") if b.get("persona") in DEMOS else "parent"
                uid = DB.demo_user(persona)
                seed_demo(uid, persona)
                return self._login(uid, demo=True)
            if p == "/api/auth/logout":
                DB.end_session(self._token())
                return self._send(200, {"ok": True}, extra={"Set-Cookie": f"{COOKIE}=; Path=/; HttpOnly; SameSite=Lax; Max-Age=0{self._secure()}"})
            if p == "/api/public/analyze":
                if not (self._limit("pub", ip, 40, 60) and self._limit("pubday", ip, 3000, 86400)):
                    return self._send(429, {"error": "Too many checks from this network. Please wait a while and try again."})
                return self._send(200, analyze(str(b.get("text", "")), b.get("lang") or "en"))
            if p == "/api/analyze":
                if not (self._limit("chk", u["id"], 30, 60) and self._limit("chkday", u["id"], 500, 86400)):
                    return self._send(429, {"error": "You have checked a lot of messages. Please wait a little and try again."})
                text = str(b.get("text", ""))
                res = analyze(text, b.get("lang") or u["lang"])
                res["id"] = DB.save_check(u["id"], text.strip()[:4000], res)
                return self._send(200, res)
            if p == "/api/ocr":
                if not aws.textract_enabled():
                    return self._send(501, {"error": "Server-side photo reading is not enabled; the browser reads the photo instead.", "fallback": True})
                try:
                    return self._send(200, {"text": aws.textract_text(aws.decode_image(b.get("image")))})
                except ValueError:
                    raise
                except Exception as e:
                    return self._send(502, {"error": "Could not read that photo right now. Please paste the text instead.", "detail": type(e).__name__})
            if p == "/api/check/delete":
                n = DB.delete_check(u["id"], int(b.get("id", 0) or 0))
                return self._send(200 if n else 404, {"ok": bool(n)})
            if p == "/api/check/report":
                n = DB.mark_reported(u["id"], int(b.get("id", 0) or 0))
                return self._send(200 if n else 404, {"ok": bool(n)})
            if p == "/api/profile":
                if DB.is_demo(u):
                    raise ValueError("Demo accounts can't be edited. Create your own account to save changes.")
                return self._send(200, {"user": DB.update_profile(u["id"], b.get("name"), b.get("home"), b.get("lang"))})
            if p == "/api/family":
                if DB.is_demo(u) and len(DB.family(u["id"])) >= 5:
                    raise ValueError("Demo accounts are limited to 5 family members.")
                return self._send(200, {"id": DB.add_family(u["id"], b.get("name"), b.get("relation"), b.get("contact"))})
            if p == "/api/family/delete":
                n = DB.delete_family(u["id"], int(b.get("id", 0) or 0))
                return self._send(200 if n else 404, {"ok": bool(n)})
            if p == "/api/family/alert":
                rec = DB.check(u["id"], int(b.get("check_id", 0) or 0))
                mem = DB.member(u["id"], int(b.get("member_id", 0) or 0))
                if not rec or not mem:
                    return self._send(404, {"error": "Check or family member not found."})
                body = alert_text(u, rec, rec["lang"] if rec["lang"] in ("en", "hi", "mr") else "en")
                oid = DB.add_outbox(u["id"], rec["id"], mem, body)
                mode, note = "outbox", "Saved in your outbox. Email delivery is switched off in this environment."
                if aws.email_enabled() and "@" in mem["contact"] and not DB.is_demo(u):
                    try:
                        aws.send_alert_email(mem["contact"], f"Kagaz Saathi: {u['name']} checked a risky message", body)
                        mode, note = "ses", f"Email sent to {mem['name']} with Amazon SES."
                    except Exception as e:
                        note = f"Saved in your outbox, but the email could not be sent ({type(e).__name__})."
                elif aws.email_enabled() and "@" not in mem["contact"]:
                    note = "Saved in your outbox. SMS delivery is not enabled; add an email address to this person to send email."
                return self._send(200, {"ok": True, "id": oid, "to": mem["name"], "mode": mode, "body": body, "note": note})
            self._send(404, {"error": "unknown endpoint"})
        except AuthError as e:
            self._send(400, {"error": str(e)})
        except ValueError as e:
            self._send(400, {"error": str(e)})
        except Exception as e:
            self._send(500, {"error": f"{type(e).__name__}: {e}"})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8030)
    args = ap.parse_args()
    srv = ThreadingHTTPServer(("127.0.0.1", args.port), H)
    print(f"Kagaz Saathi on http://localhost:{args.port}", flush=True)
    srv.serve_forever()


if __name__ == "__main__":
    main()
