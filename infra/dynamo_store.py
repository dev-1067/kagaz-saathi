"""DynamoDB implementation of the Store interface (kagaz/store.py), for the AWS deployment.

One table, keys (pk, sk):
  USER#<id> / PROFILE                profile + password hash        EMAIL#<email> / EMAIL   -> user id (login lookup, unique email)
  SESSION#<token> / SESSION          user id + `ttl` (DynamoDB TTL deletes expired sessions)
  USER#<id> / CHECK#<00000id>        saved checks                   USER#<id> / FAM#<00000id>   family   USER#<id> / OUT#<00000id>   outbox
  COUNTER# / <name>                  atomic id counters
Passwords are salted PBKDF2-SHA256 hashes, exactly as in the SQLite store. Tested locally with moto (tests/test_dynamo.py).
"""
import hashlib
import hmac
import json
import re
import secrets
import time
from decimal import Decimal

import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

from kagaz.store import DEMOS, EMAIL_RE, ITER, AuthError


def _h(pw, salt):
    return hashlib.pbkdf2_hmac("sha256", pw.encode("utf-8"), bytes.fromhex(salt), ITER).hex()


def _py(x):
    if isinstance(x, Decimal):
        return int(x) if x == x.to_integral_value() else float(x)
    if isinstance(x, dict):
        return {k: _py(v) for k, v in x.items()}
    if isinstance(x, list):
        return [_py(v) for v in x]
    return x


class DynamoStore:
    def __init__(self, table_name, region=None, endpoint_url=None):
        self.t = boto3.resource("dynamodb", region_name=region, endpoint_url=endpoint_url).Table(table_name)

    # ---- helpers
    def _next(self, name):
        r = self.t.update_item(Key={"pk": "COUNTER#", "sk": name}, UpdateExpression="ADD n :one", ExpressionAttributeValues={":one": 1}, ReturnValues="UPDATED_NEW")
        return int(r["Attributes"]["n"])

    def _query(self, pk, prefix, reverse=False, limit=None):
        kw = {"KeyConditionExpression": Key("pk").eq(pk) & Key("sk").begins_with(prefix), "ScanIndexForward": not reverse}
        if limit:
            kw["Limit"] = limit
        return [_py(i) for i in self.t.query(**kw)["Items"]]

    # ---- accounts
    def create_user(self, name, email, password, home="", lang="en"):
        name, email, home = (name or "").strip(), (email or "").strip().lower(), (home or "").strip()
        if not 2 <= len(name) <= 60:
            raise AuthError("Please enter your name (2 to 60 characters).")
        if not EMAIL_RE.match(email) or len(email) > 120:
            raise AuthError("Please enter a valid email address.")
        if len(password or "") < 8 or not re.search(r"[A-Za-z]", password) or not re.search(r"\d", password):
            raise AuthError("Use at least 8 characters, with at least one letter and one number.")
        uid = self._next("user")
        try:
            self.t.put_item(Item={"pk": f"EMAIL#{email}", "sk": "EMAIL", "uid": uid}, ConditionExpression="attribute_not_exists(pk)")
        except ClientError as e:
            if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
                raise AuthError("An account with this email already exists. Try signing in.")
            raise
        salt = secrets.token_hex(16)
        self.t.put_item(Item={"pk": f"USER#{uid}", "sk": "PROFILE", "id": uid, "name": name, "email": email, "home": home or f"{name}'s home",
                              "lang": lang if lang in ("en", "hi", "mr") else "en", "pw_hash": _h(password, salt), "salt": salt, "created_at": Decimal(str(time.time()))})
        return uid

    def _profile(self, uid):
        r = self.t.get_item(Key={"pk": f"USER#{uid}", "sk": "PROFILE"}).get("Item")
        return _py(r) if r else None

    def verify(self, email, password):
        e = self.t.get_item(Key={"pk": f"EMAIL#{(email or '').strip().lower()}", "sk": "EMAIL"}).get("Item")
        row = self._profile(int(e["uid"])) if e else None
        if not row or not hmac.compare_digest(row["pw_hash"], _h(password or "", row["salt"])):
            raise AuthError("Email or password is incorrect.")
        return row["id"]

    def user(self, uid):
        r = self._profile(uid)
        return {k: r[k] for k in ("id", "name", "email", "home", "lang", "created_at")} if r else None

    def update_profile(self, uid, name, home, lang):
        name, home = (name or "").strip(), (home or "").strip()
        if not 2 <= len(name) <= 60 or not 1 <= len(home) <= 60:
            raise AuthError("Name and household name are required (up to 60 characters).")
        self.t.update_item(Key={"pk": f"USER#{uid}", "sk": "PROFILE"}, UpdateExpression="SET #n=:n, home=:h, lang=:l",
                           ExpressionAttributeNames={"#n": "name"}, ExpressionAttributeValues={":n": name, ":h": home, ":l": lang if lang in ("en", "hi", "mr") else "en"})
        return self.user(uid)

    def demo_user(self, persona):
        name, email, home = DEMOS.get(persona, DEMOS["parent"])
        e = self.t.get_item(Key={"pk": f"EMAIL#{email}", "sk": "EMAIL"}).get("Item")
        if e:
            return int(e["uid"])
        return self.create_user(name, email, secrets.token_urlsafe(18) + "a1", home, "hi" if persona == "parent" else "en")

    def is_demo(self, user):
        return bool(user) and user["email"].endswith("@kagaz.demo")

    # ---- sessions
    def new_session(self, uid):
        tok = secrets.token_urlsafe(32)
        self.t.put_item(Item={"pk": f"SESSION#{tok}", "sk": "SESSION", "uid": uid, "ttl": int(time.time()) + 7 * 86400})
        return tok

    def session_user(self, token):
        if not token:
            return None
        r = self.t.get_item(Key={"pk": f"SESSION#{token}", "sk": "SESSION"}).get("Item")
        if not r or int(r["ttl"]) < time.time():
            return None
        return self.user(int(r["uid"]))

    def end_session(self, token):
        self.t.delete_item(Key={"pk": f"SESSION#{token or ''}", "sk": "SESSION"})

    # ---- checks
    def save_check(self, uid, text, res):
        cid = self._next("check")
        self.t.put_item(Item={"pk": f"USER#{uid}", "sk": f"CHECK#{cid:012d}", "id": cid, "text": text[:4000], "verdict": res["verdict"], "kind": res["kind"],
                              "risk": res["risk"], "lang": res["lang"], "created_at": Decimal(str(time.time())), "result": json.dumps(res, ensure_ascii=False), "reported": 0})
        return cid

    def checks(self, uid, limit=200):
        items = self._query(f"USER#{uid}", "CHECK#", reverse=True, limit=limit)
        return [{k: i[k] for k in ("id", "text", "verdict", "kind", "risk", "lang", "created_at", "reported")} for i in items]

    def check(self, uid, cid):
        r = self.t.get_item(Key={"pk": f"USER#{uid}", "sk": f"CHECK#{int(cid):012d}"}).get("Item")
        if not r:
            return None
        d = _py(r)
        d["result"] = json.loads(d["result"])
        return d

    def delete_check(self, uid, cid):
        try:
            self.t.delete_item(Key={"pk": f"USER#{uid}", "sk": f"CHECK#{int(cid):012d}"}, ConditionExpression="attribute_exists(pk)")
            return 1
        except ClientError:
            return 0

    def mark_reported(self, uid, cid):
        try:
            self.t.update_item(Key={"pk": f"USER#{uid}", "sk": f"CHECK#{int(cid):012d}"}, UpdateExpression="SET reported=:one",
                               ConditionExpression="attribute_exists(pk)", ExpressionAttributeValues={":one": 1})
            return 1
        except ClientError:
            return 0

    def stats(self, uid):
        rows = self.checks(uid, limit=1000)
        kinds = {}
        for r in rows:
            if r["verdict"] != "genuine":
                kinds[r["kind"]] = kinds.get(r["kind"], 0) + 1
        per = {}
        cutoff = time.time() - 14 * 86400
        for r in rows:
            if r["created_at"] > cutoff:
                d = time.strftime("%Y-%m-%d", time.gmtime(r["created_at"]))
                per[d] = per.get(d, 0) + 1
        return {"checks": len(rows), "scams": sum(r["verdict"] == "scam" for r in rows), "suspicious": sum(r["verdict"] == "suspicious" for r in rows),
                "genuine": sum(r["verdict"] == "genuine" for r in rows), "reported": sum(bool(r["reported"]) for r in rows),
                "family": len(self.family(uid)), "alerts": len(self.outbox(uid)),
                "kinds": [{"kind": k, "n": n} for k, n in sorted(kinds.items(), key=lambda x: -x[1])[:6]],
                "per_day": [{"d": d, "n": n} for d, n in sorted(per.items())]}

    # ---- family + outbox
    def family(self, uid):
        return [{k: i[k] for k in ("id", "name", "relation", "contact")} for i in self._query(f"USER#{uid}", "FAM#")]

    def add_family(self, uid, name, relation, contact):
        name, relation, contact = (name or "").strip(), (relation or "").strip(), (contact or "").strip()
        if not 1 <= len(name) <= 40:
            raise AuthError("Please enter the person's name.")
        if not (EMAIL_RE.match(contact) or re.fullmatch(r"\+?\d[\d\s-]{8,14}\d", contact)):
            raise AuthError("Enter a valid mobile number or email for this person.")
        if len(self.family(uid)) >= 10:
            raise AuthError("You can add up to 10 family members.")
        fid = self._next("family")
        self.t.put_item(Item={"pk": f"USER#{uid}", "sk": f"FAM#{fid:012d}", "id": fid, "name": name, "relation": relation[:30] or "Family", "contact": contact})
        return fid

    def delete_family(self, uid, fid):
        try:
            self.t.delete_item(Key={"pk": f"USER#{uid}", "sk": f"FAM#{int(fid):012d}"}, ConditionExpression="attribute_exists(pk)")
            return 1
        except ClientError:
            return 0

    def member(self, uid, fid):
        r = self.t.get_item(Key={"pk": f"USER#{uid}", "sk": f"FAM#{int(fid):012d}"}).get("Item")
        return {k: _py(r)[k] for k in ("id", "name", "relation", "contact")} if r else None

    def add_outbox(self, uid, check_id, member, body):
        oid = self._next("outbox")
        self.t.put_item(Item={"pk": f"USER#{uid}", "sk": f"OUT#{oid:012d}", "id": oid, "check_id": check_id, "member_name": member["name"], "contact": member["contact"],
                              "body": body, "created_at": Decimal(str(time.time()))})
        return oid

    def outbox(self, uid):
        return [{k: i[k] for k in ("id", "check_id", "member_name", "contact", "body", "created_at")} for i in self._query(f"USER#{uid}", "OUT#", reverse=True, limit=50)]

    # `DB.c.execute(...)` is used once by the demo seeder to back-date seeded checks; DynamoDB seeds with real timestamps instead.
    class _Noop:
        def execute(self, *a, **k):
            return self

        def commit(self):
            pass
    c = _Noop()
