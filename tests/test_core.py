"""Unit tests: classifier accuracy, analyzer behaviour, accounts/store, and the HTTP API."""
import json
import sys
import threading
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from kagaz import content as C  # noqa: E402
from kagaz.analyzer import analyze, extract, judge_link  # noqa: E402
from kagaz.notice_model import TacticModel  # noqa: E402
from kagaz.store import AuthError, Store  # noqa: E402


def rows(name):
    return [json.loads(l) for l in (ROOT / "model" / "data" / f"{name}.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]


# ------------------------------------------------------------------ model
def test_fresh_test_accuracy_is_at_least_95_percent():
    m, data = TacticModel(), rows("fresh_test")
    acc = sum(m.predict(r["text"])[0] == r["label"] for r in data) / len(data)
    assert len(data) == 150 and acc >= 0.95, acc


def test_report_matches_live_model():
    rep = json.loads((ROOT / "results" / "model_report.json").read_text(encoding="utf-8"))
    m, data = TacticModel(), rows("fresh_test")
    acc = sum(m.predict(r["text"])[0] == r["label"] for r in data) / len(data)
    assert abs(acc - rep["test_accuracy"]) < 0.01


def test_pipeline_scam_vs_genuine_on_fresh_test():
    data = rows("fresh_test")
    wrong = [r for r in data if (analyze(r["text"])["verdict"] == "scam") != (r["label"] in C.SCAM)]
    assert len(wrong) / len(data) <= 0.03, [w["text"][:60] for w in wrong]


def test_no_genuine_message_is_called_scam_outright():
    # the costly error: telling someone a real bank/OTP/bill message is "very likely a scam"
    bad = [r["text"][:70] for r in rows("fresh_test") if r["label"] not in C.SCAM and analyze(r["text"])["verdict"] == "scam"]
    assert not bad, bad


# ------------------------------------------------------------------ analyzer behaviour
@pytest.mark.parametrize("text,verdict", [
    ("Your SBI account will be blocked today. Update KYC at sbi-kyc-update.in and share the OTP.", "scam"),
    ("You are under digital arrest. Do not disconnect the video call and tell no one.", "scam"),
    ("Please read out the OTP just sent to your phone to reverse the wrong transaction.", "scam"),
    ("842193 is your OTP for login. Do not share it with anyone.", "genuine"),
    ("INR 500 debited from A/c XX1234 at Zomato. Avl bal INR 2,000.", "genuine"),
    ("Hi, are we meeting at 5 pm today?", "genuine"),
])
def test_known_messages(text, verdict):
    assert analyze(text)["verdict"] == verdict


def test_every_language_has_content_for_every_kind():
    for kind in C.LABELS:
        for lang in ("en", "hi", "mr"):
            assert C.LABELS[kind][lang] and C.WHY[kind][lang]
    for lang in ("en", "hi", "mr"):
        r = analyze("Your bank account will be blocked, click the link to verify KYC", lang)
        assert r["lang"] == lang and r["steps"] and r["explanation"]
        assert any("ऀ" <= ch <= "ॿ" for ch in r["verdict_label"]) == (lang != "en")


def test_empty_and_huge_input():
    with pytest.raises(ValueError):
        analyze("   ")
    assert analyze("hello " * 5000)["verdict"] in ("genuine", "suspicious", "scam")
    assert analyze("😀" * 300)["verdict"]


def test_link_judgement():
    assert judge_link("https://www.incometax.gov.in/iec") == "official"
    assert judge_link("https://bit.ly/3abc") == "short"
    assert judge_link("sbi-kyc-update.in") == "lookalike"
    assert judge_link("https://example.org/page") == "unknown"


def test_fact_extraction():
    f = extract("Pay Rs 3,850 by 25-Nov at sbi-kyc.xyz or call 98XXXXXX45")
    assert f["amounts"] == [3850.0] and f["dates"] == ["25-Nov"] and f["urls"] and f["phones"]


def test_deterministic():
    assert analyze("Update KYC now at bit.ly/xyz") == analyze("Update KYC now at bit.ly/xyz")


def test_analyzer_never_crashes_on_garbage():
    import random
    rnd = random.Random(1)
    alphabet = "abcdefgh ijk,.?!₹%/:@#\n\t0123456789अआइईकखगनमरस"
    for _ in range(300):
        t = "".join(rnd.choice(alphabet) for _ in range(rnd.randint(1, 400)))
        if t.strip():
            r = analyze(t)
            assert r["verdict"] in ("genuine", "suspicious", "scam") and 0 <= r["risk"] <= 100


# ------------------------------------------------------------------ store
@pytest.fixture()
def db(tmp_path):
    return Store(tmp_path / "t.db")


def test_accounts(db):
    uid = db.create_user("Asha Verma", "Asha@Example.com", "goodpass1")
    assert db.verify("asha@example.com", "goodpass1") == uid
    for bad in [("A", "a@b.co", "goodpass1"), ("Asha", "nope", "goodpass1"), ("Asha", "a@b.co", "short1"), ("Asha", "a@b.co", "onlyletters")]:
        with pytest.raises(AuthError):
            db.create_user(*bad)
    with pytest.raises(AuthError, match="already exists"):
        db.create_user("Other", "ASHA@example.com", "goodpass2")
    with pytest.raises(AuthError, match="incorrect"):
        db.verify("asha@example.com", "wrongpass1")
    row = db.c.execute("SELECT pw_hash FROM users").fetchone()
    assert "goodpass1" not in row["pw_hash"] and len(row["pw_hash"]) == 64


def test_data_is_private_between_users(db):
    a, b = db.create_user("Asha", "a@b.co", "goodpass1"), db.create_user("Ravi", "r@b.co", "goodpass1")
    res = analyze("Update KYC at bit.ly/x or account blocked")
    cid = db.save_check(a, "Update KYC", res)
    assert db.check(b, cid) is None and db.delete_check(b, cid) == 0 and db.checks(b) == []
    fid = db.add_family(a, "Neha", "Daughter", "neha@example.com")
    assert db.member(b, fid) is None and db.delete_family(b, fid) == 0
    assert db.check(a, cid)["result"]["verdict"] == res["verdict"]
    assert db.stats(a)["checks"] == 1 and db.stats(b)["checks"] == 0


def test_family_validation(db):
    u = db.create_user("Asha", "a@b.co", "goodpass1")
    for bad in [("", "Son", "a@b.co"), ("Neha", "Daughter", "not-valid"), ("Neha", "Daughter", "123")]:
        with pytest.raises(AuthError):
            db.add_family(u, *bad)
    db.add_family(u, "Amit", "Son", "+91 98765 43210")
    for i in range(9):
        db.add_family(u, f"P{i}", "Friend", f"p{i}@b.co")
    with pytest.raises(AuthError, match="up to 10"):
        db.add_family(u, "Extra", "Friend", "x@b.co")


def test_concurrent_writes_do_not_corrupt(db):
    u = db.create_user("Asha", "a@b.co", "goodpass1")
    res = analyze("hello there")
    errs = []

    def work():
        try:
            for _ in range(40):
                db.save_check(u, "hello there", res)
                db.stats(u)
                db.checks(u)
        except Exception as e:  # pragma: no cover
            errs.append(e)
    ts = [threading.Thread(target=work) for _ in range(8)]
    [t.start() for t in ts]
    [t.join() for t in ts]
    assert not errs and db.stats(u)["checks"] == 320


# ------------------------------------------------------------------ HTTP API
@pytest.fixture(scope="module")
def server(tmp_path_factory):
    import kagaz.server as S
    S.DB = Store(tmp_path_factory.mktemp("api") / "api.db")
    srv = ThreadingHTTPServer(("127.0.0.1", 0), S.H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{srv.server_address[1]}"
    srv.shutdown()


def call(base, path, body=None, cookie=None):
    req = urllib.request.Request(base + path, data=None if body is None else json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json", **({"Cookie": cookie} if cookie else {})})
    try:
        with urllib.request.urlopen(req) as r:
            return r.status, json.loads(r.read() or b"{}"), r.headers.get("Set-Cookie")
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b"{}"), None


def test_api_flow(server):
    assert call(server, "/api/checks")[0] == 401
    s, out, _ = call(server, "/api/public/analyze", {"text": "Your account will be blocked, update KYC at bit.ly/x", "lang": "hi"})
    assert s == 200 and out["verdict"] == "scam" and out["lang"] == "hi"
    assert call(server, "/api/public/analyze", {"text": ""})[0] == 400
    s, out, ck = call(server, "/api/auth/signup", {"name": "Test User", "email": "t@example.com", "password": "Passw0rdOK"})
    cookie = ck.split(";")[0]
    assert s == 200
    s, chk, _ = call(server, "/api/analyze", {"text": "842193 is your OTP. Do not share it.", "lang": "en"}, cookie)
    assert s == 200 and chk["verdict"] == "genuine" and chk["id"]
    assert call(server, "/api/checks", None, cookie)[1][0]["id"] == chk["id"]
    s, fam, _ = call(server, "/api/family", {"name": "Neha", "relation": "Daughter", "contact": "neha@example.com"}, cookie)
    assert s == 200
    s, al, _ = call(server, "/api/family/alert", {"check_id": chk["id"], "member_id": fam["id"]}, cookie)
    assert s == 200 and "Test User" in al["body"]
    assert call(server, "/api/outbox", None, cookie)[1][0]["member_name"] == "Neha"
    assert call(server, "/api/family/alert", {"check_id": 9999, "member_id": fam["id"]}, cookie)[0] == 404
    s, other, ck2 = call(server, "/api/auth/signup", {"name": "Other", "email": "o@example.com", "password": "Passw0rdOK"})
    assert call(server, f"/api/check?id={chk['id']}", None, ck2.split(";")[0])[0] == 404          # cannot read someone else's check
    assert call(server, "/api/check/delete", {"id": chk["id"]}, cookie)[0] == 200
    assert call(server, "/api/auth/login", {"email": "t@example.com", "password": "nope"})[0] == 400
    s, d, ck3 = call(server, "/api/auth/demo", {"persona": "parent"})
    assert s == 200 and call(server, "/api/profile", {"name": "X Y", "home": "H", "lang": "en"}, ck3.split(";")[0])[0] == 400   # demo is read-only
    assert len(call(server, "/api/checks", None, ck3.split(";")[0])[1]) >= 3       # seeded history


def test_stress_sets_hold_up():
    rep = json.loads((ROOT / "results" / "stress_report.json").read_text(encoding="utf-8"))
    for name in ("stress", "stress2"):
        r = rep[name]
        assert r["scam_flagged_rate"] >= 0.9, (name, r["scam_flagged_rate"])   # a scam is never left as 'genuine' (stress sets)
        assert r["genuine_false_scam_rate"] == 0.0, name                          # a real message is never called 'scam'
    live = [analyze(json.loads(l)["text"])["verdict"] for l in (ROOT / "model" / "data" / "stress2.jsonl").read_text(encoding="utf-8").splitlines()]
    assert live.count("scam") == rep["stress2"]["scam_called_scam"] + rep["stress2"]["genuine_called_scam"]


def test_stress_sets_3_and_4_hold_up():
    rep = json.loads((ROOT / "results" / "stress_report.json").read_text(encoding="utf-8"))
    for name in ("stress3", "stress4"):
        r = rep[name]
        assert r["scam_called_genuine"] == 0, name              # a scam is never waved through as genuine
        assert r["genuine_called_scam"] == 0, name
        assert r["scam_flagged_rate"] >= 0.95, (name, r["scam_flagged_rate"])


def test_rate_limits_survive_in_the_database(tmp_path):
    a = Store(tmp_path / "r.db")
    assert [a.hit("k", 3, 60) for _ in range(5)] == [True, True, True, False, False]
    assert a.hit("other", 3, 60)                                  # a different key has its own count
    b = Store(tmp_path / "r.db")                                   # a restarted / second process sees the same count
    assert b.hit("k", 3, 60) is False


def test_public_endpoint_is_rate_limited_and_body_capped(server):
    codes = [call(server, "/api/public/analyze", {"text": "Your KYC is blocked, click bit.ly/x"})[0] for _ in range(25)]
    assert 429 in codes and codes[0] == 200
    big = call(server, "/api/auth/login", {"email": "a@b.co", "password": "x" * 100_000})
    assert big[0] in (400, 429)                                    # oversize body is cut off, never processed


def test_install_and_share_target_files(server):
    for path, ctype in (("/manifest.webmanifest", "manifest"), ("/sw.js", "javascript"), ("/icon-192.png", "png"), ("/icon-512.png", "png"), ("/share", "html")):
        with urllib.request.urlopen(server + path) as r:
            assert r.status == 200 and ctype in r.headers["Content-Type"], path
    with urllib.request.urlopen(server + "/manifest.webmanifest") as r:
        assert json.loads(r.read())["share_target"]["action"] == "/share"
