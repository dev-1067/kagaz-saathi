"""SQLite storage: accounts, sessions, saved checks, family contacts and the alert outbox.

Passwords are stored only as salted PBKDF2-HMAC-SHA256 hashes. Sessions are random tokens (7 days).
On AWS the same interface is implemented over DynamoDB (infra/dynamo_store.py).
"""
import hashlib
import os
import hmac
import json
import re
import secrets
import sqlite3
import threading
import time
from pathlib import Path

DB_PATH = Path(os.environ.get("KAGAZ_DB") or Path(__file__).resolve().parents[1] / "data" / "kagaz.db")
ITER = 200_000
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[A-Za-z]{2,}$")
LOCK = threading.RLock()
DEMOS = {"parent": ("Savitri Devi", "parent@kagaz.demo", "Savitri's home"), "student": ("Rohan Patil", "student@kagaz.demo", "Rohan (student)"),
         "family": ("Neha Sharma", "family@kagaz.demo", "Sharma family")}

SCHEMA = """
CREATE TABLE IF NOT EXISTS rate (k TEXT PRIMARY KEY, n INTEGER NOT NULL, exp REAL NOT NULL);
CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, email TEXT NOT NULL UNIQUE COLLATE NOCASE,
  home TEXT NOT NULL DEFAULT '', lang TEXT NOT NULL DEFAULT 'en', pw_hash TEXT NOT NULL, salt TEXT NOT NULL, created_at REAL NOT NULL);
CREATE TABLE IF NOT EXISTS sessions (token TEXT PRIMARY KEY, user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  expires_at REAL NOT NULL);
CREATE TABLE IF NOT EXISTS checks (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  text TEXT NOT NULL, verdict TEXT NOT NULL, kind TEXT NOT NULL, risk INTEGER NOT NULL, lang TEXT NOT NULL, created_at REAL NOT NULL,
  result TEXT NOT NULL, reported INTEGER NOT NULL DEFAULT 0);
CREATE TABLE IF NOT EXISTS family (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  name TEXT NOT NULL, relation TEXT NOT NULL, contact TEXT NOT NULL, created_at REAL NOT NULL);
CREATE TABLE IF NOT EXISTS outbox (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  check_id INTEGER, member_name TEXT NOT NULL, contact TEXT NOT NULL, body TEXT NOT NULL, created_at REAL NOT NULL);
CREATE INDEX IF NOT EXISTS checks_user ON checks(user_id, created_at DESC);
"""


class _Result:
    def __init__(self, cur):
        self.rows, self.rowcount, self.lastrowid = cur.fetchall() if cur.description else [], cur.rowcount, cur.lastrowid

    def fetchone(self):
        return self.rows[0] if self.rows else None

    def fetchall(self):
        return self.rows

    def __iter__(self):
        return iter(self.rows)


class _Conn:
    """One shared SQLite connection used by many server threads: every statement runs under a lock and its rows are
    fetched before the lock is released, so threads can never interleave on the same cursor."""
    def __init__(self, conn):
        self.conn = conn

    def execute(self, sql, params=()):
        with LOCK:
            return _Result(self.conn.execute(sql, params))

    def executescript(self, sql):
        with LOCK:
            self.conn.executescript(sql)

    def commit(self):
        with LOCK:
            self.conn.commit()


class AuthError(ValueError):
    pass


def _hash(pw, salt):
    return hashlib.pbkdf2_hmac("sha256", pw.encode("utf-8"), bytes.fromhex(salt), ITER).hex()


class Store:
    def __init__(self, path=None):
        p = Path(path or DB_PATH)
        p.parent.mkdir(parents=True, exist_ok=True)
        raw = sqlite3.connect(str(p), check_same_thread=False, timeout=10)
        raw.row_factory = sqlite3.Row
        self.c = _Conn(raw)
        self.c.execute("PRAGMA foreign_keys = ON")
        with LOCK:
            self.c.executescript(SCHEMA)
            self.c.commit()

    # ---- abuse limits (shared by every server process, survives restarts)
    def hit(self, key, limit, per):
        """Count one hit for `key` in the current `per`-second window. True if still within `limit`."""
        now = time.time()
        k = f"{key}|{int(now // per)}"
        with LOCK:
            self.c.execute("DELETE FROM rate WHERE exp < ?", (now,))
            self.c.execute("INSERT INTO rate (k, n, exp) VALUES (?, 1, ?) ON CONFLICT(k) DO UPDATE SET n = n + 1", (k, now + per * 2))
            n = self.c.execute("SELECT n FROM rate WHERE k = ?", (k,)).fetchone()["n"]
            self.c.commit()
        return n <= limit

    # ---- accounts
    def create_user(self, name, email, password, home="", lang="en"):
        name, email, home = (name or "").strip(), (email or "").strip().lower(), (home or "").strip()
        if not 2 <= len(name) <= 60:
            raise AuthError("Please enter your name (2 to 60 characters).")
        if not EMAIL_RE.match(email) or len(email) > 120:
            raise AuthError("Please enter a valid email address.")
        if len(password or "") < 8 or not re.search(r"[A-Za-z]", password) or not re.search(r"\d", password):
            raise AuthError("Use at least 8 characters, with at least one letter and one number.")
        salt = secrets.token_hex(16)
        with LOCK:
            try:
                cur = self.c.execute("INSERT INTO users (name,email,home,lang,pw_hash,salt,created_at) VALUES (?,?,?,?,?,?,?)",
                                     (name, email, home or f"{name}'s home", lang if lang in ("en", "hi", "mr") else "en",
                                      _hash(password, salt), salt, time.time()))
                self.c.commit()
            except sqlite3.IntegrityError:
                raise AuthError("An account with this email already exists. Try signing in.")
        return cur.lastrowid

    def verify(self, email, password):
        row = self.c.execute("SELECT * FROM users WHERE email = ?", ((email or "").strip().lower(),)).fetchone()
        if not row or not hmac.compare_digest(row["pw_hash"], _hash(password or "", row["salt"])):
            raise AuthError("Email or password is incorrect.")
        return row["id"]

    def user(self, uid):
        r = self.c.execute("SELECT id,name,email,home,lang,created_at FROM users WHERE id = ?", (uid,)).fetchone()
        return dict(r) if r else None

    def update_profile(self, uid, name, home, lang):
        name, home = (name or "").strip(), (home or "").strip()
        if not 2 <= len(name) <= 60 or not 1 <= len(home) <= 60:
            raise AuthError("Name and household name are required (up to 60 characters).")
        with LOCK:
            self.c.execute("UPDATE users SET name=?, home=?, lang=? WHERE id=?", (name, home, lang if lang in ("en", "hi", "mr") else "en", uid))
            self.c.commit()
        return self.user(uid)

    def demo_user(self, persona):
        name, email, home = DEMOS.get(persona, DEMOS["parent"])
        row = self.c.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
        if row:
            return row["id"]
        uid = self.create_user(name, email, secrets.token_urlsafe(18) + "a1", home, "hi" if persona == "parent" else "en")
        return uid

    def is_demo(self, user):
        return bool(user) and user["email"].endswith("@kagaz.demo")

    # ---- sessions
    def new_session(self, uid):
        t = secrets.token_urlsafe(32)
        with LOCK:
            self.c.execute("DELETE FROM sessions WHERE expires_at < ?", (time.time(),))
            self.c.execute("INSERT INTO sessions VALUES (?,?,?)", (t, uid, time.time() + 7 * 86400))
            self.c.commit()
        return t

    def session_user(self, token):
        if not token:
            return None
        r = self.c.execute("SELECT user_id FROM sessions WHERE token=? AND expires_at>?", (token, time.time())).fetchone()
        return self.user(r["user_id"]) if r else None

    def end_session(self, token):
        with LOCK:
            self.c.execute("DELETE FROM sessions WHERE token=?", (token or "",))
            self.c.commit()

    # ---- checks
    def save_check(self, uid, text, res):
        with LOCK:
            cur = self.c.execute("INSERT INTO checks (user_id,text,verdict,kind,risk,lang,created_at,result) VALUES (?,?,?,?,?,?,?,?)",
                                 (uid, text[:4000], res["verdict"], res["kind"], res["risk"], res["lang"], time.time(),
                                  json.dumps(res, ensure_ascii=False)))
            self.c.commit()
        return cur.lastrowid

    def checks(self, uid, limit=200):
        rows = self.c.execute("SELECT id,text,verdict,kind,risk,lang,created_at,reported FROM checks WHERE user_id=? ORDER BY created_at DESC LIMIT ?",
                              (uid, limit)).fetchall()
        return [dict(r) for r in rows]

    def check(self, uid, cid):
        r = self.c.execute("SELECT * FROM checks WHERE id=? AND user_id=?", (cid, uid)).fetchone()
        if not r:
            return None
        d = dict(r)
        d["result"] = json.loads(d["result"])
        return d

    def delete_check(self, uid, cid):
        with LOCK:
            n = self.c.execute("DELETE FROM checks WHERE id=? AND user_id=?", (cid, uid)).rowcount
            self.c.commit()
        return n

    def mark_reported(self, uid, cid):
        with LOCK:
            n = self.c.execute("UPDATE checks SET reported=1 WHERE id=? AND user_id=?", (cid, uid)).rowcount
            self.c.commit()
        return n

    def stats(self, uid):
        r = self.c.execute("SELECT COUNT(*) n, SUM(verdict='scam') scam, SUM(verdict='suspicious') susp, SUM(verdict='genuine') ok, "
                           "SUM(reported) rep FROM checks WHERE user_id=?", (uid,)).fetchone()
        kinds = self.c.execute("SELECT kind, COUNT(*) n FROM checks WHERE user_id=? AND verdict!='genuine' GROUP BY kind ORDER BY n DESC LIMIT 6",
                               (uid,)).fetchall()
        fam = self.c.execute("SELECT COUNT(*) n FROM family WHERE user_id=?", (uid,)).fetchone()["n"]
        sent = self.c.execute("SELECT COUNT(*) n FROM outbox WHERE user_id=?", (uid,)).fetchone()["n"]
        day = self.c.execute("SELECT strftime('%Y-%m-%d', created_at, 'unixepoch') d, COUNT(*) n FROM checks WHERE user_id=? AND created_at>? "
                             "GROUP BY d ORDER BY d", (uid, time.time() - 14 * 86400)).fetchall()
        return {"checks": r["n"] or 0, "scams": r["scam"] or 0, "suspicious": r["susp"] or 0, "genuine": r["ok"] or 0, "reported": r["rep"] or 0,
                "family": fam, "alerts": sent, "kinds": [dict(k) for k in kinds], "per_day": [dict(d) for d in day]}

    # ---- family + outbox
    def family(self, uid):
        return [dict(r) for r in self.c.execute("SELECT id,name,relation,contact FROM family WHERE user_id=? ORDER BY id", (uid,))]

    def add_family(self, uid, name, relation, contact):
        name, relation, contact = (name or "").strip(), (relation or "").strip(), (contact or "").strip()
        if not 1 <= len(name) <= 40:
            raise AuthError("Please enter the person's name.")
        if not (EMAIL_RE.match(contact) or re.fullmatch(r"\+?\d[\d\s-]{8,14}\d", contact)):
            raise AuthError("Enter a valid mobile number or email for this person.")
        if self.c.execute("SELECT COUNT(*) n FROM family WHERE user_id=?", (uid,)).fetchone()["n"] >= 10:
            raise AuthError("You can add up to 10 family members.")
        with LOCK:
            cur = self.c.execute("INSERT INTO family (user_id,name,relation,contact,created_at) VALUES (?,?,?,?,?)",
                                 (uid, name, relation[:30] or "Family", contact, time.time()))
            self.c.commit()
        return cur.lastrowid

    def delete_family(self, uid, fid):
        with LOCK:
            n = self.c.execute("DELETE FROM family WHERE id=? AND user_id=?", (fid, uid)).rowcount
            self.c.commit()
        return n

    def member(self, uid, fid):
        r = self.c.execute("SELECT id,name,relation,contact FROM family WHERE id=? AND user_id=?", (fid, uid)).fetchone()
        return dict(r) if r else None

    def add_outbox(self, uid, check_id, member, body):
        with LOCK:
            cur = self.c.execute("INSERT INTO outbox (user_id,check_id,member_name,contact,body,created_at) VALUES (?,?,?,?,?,?)",
                                 (uid, check_id, member["name"], member["contact"], body, time.time()))
            self.c.commit()
        return cur.lastrowid

    def outbox(self, uid):
        return [dict(r) for r in self.c.execute("SELECT id,check_id,member_name,contact,body,created_at FROM outbox WHERE user_id=? ORDER BY id DESC LIMIT 50", (uid,))]
