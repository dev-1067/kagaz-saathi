"""Tests the AWS build locally with moto (a mock of DynamoDB): the DynamoStore and the Lambda entry point.

No AWS account is used. Skipped automatically if boto3/moto are not installed.
"""
import json
import os
import sys
from pathlib import Path

import pytest

pytest.importorskip("boto3")
pytest.importorskip("moto")
from moto import mock_aws  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "infra")]
os.environ.setdefault("AWS_ACCESS_KEY_ID", "test")
os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "test")
os.environ.setdefault("AWS_DEFAULT_REGION", "ap-south-1")

from kagaz.analyzer import analyze  # noqa: E402
from kagaz.store import AuthError  # noqa: E402


def make_table():
    import boto3
    boto3.client("dynamodb", region_name="ap-south-1").create_table(
        TableName="kagaz", BillingMode="PAY_PER_REQUEST",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}, {"AttributeName": "sk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}, {"AttributeName": "sk", "KeyType": "RANGE"}])


@pytest.fixture()
def store():
    with mock_aws():
        make_table()
        from dynamo_store import DynamoStore
        yield DynamoStore("kagaz", region="ap-south-1")


def test_dynamo_accounts_and_isolation(store):
    a = store.create_user("Asha Verma", "Asha@Example.com", "goodpass1")
    b = store.create_user("Ravi", "r@b.co", "goodpass1")
    assert store.verify("asha@example.com", "goodpass1") == a
    with pytest.raises(AuthError, match="already exists"):
        store.create_user("Other", "ASHA@example.com", "goodpass2")
    with pytest.raises(AuthError, match="incorrect"):
        store.verify("asha@example.com", "wrong1234")
    res = analyze("Update KYC at bit.ly/x or your account is blocked")
    cid = store.save_check(a, "Update KYC", res)
    assert store.check(b, cid) is None and store.delete_check(b, cid) == 0 and store.checks(b) == []
    assert store.check(a, cid)["result"]["verdict"] == res["verdict"]
    assert store.mark_reported(a, cid) == 1 and store.checks(a)[0]["reported"] == 1
    st = store.stats(a)
    assert st["checks"] == 1 and st["scams"] + st["suspicious"] == 1 and st["reported"] == 1
    assert store.delete_check(a, cid) == 1 and store.checks(a) == []


def test_dynamo_sessions_family_outbox(store):
    u = store.create_user("Asha", "a@b.co", "goodpass1")
    tok = store.new_session(u)
    assert store.session_user(tok)["id"] == u and store.session_user("forged") is None
    store.end_session(tok)
    assert store.session_user(tok) is None
    f = store.add_family(u, "Neha", "Daughter", "neha@example.com")
    for bad in [("", "x", "a@b.co"), ("N", "x", "nope")]:
        with pytest.raises(AuthError):
            store.add_family(u, *bad)
    assert store.member(u, f)["name"] == "Neha"
    oid = store.add_outbox(u, 1, store.member(u, f), "hello")
    assert store.outbox(u)[0]["id"] == oid and store.stats(u)["alerts"] == 1
    assert store.delete_family(u, f) == 1 and store.family(u) == []


def event(method, path, body=None, cookie=None):
    return {"rawPath": path.split("?")[0], "rawQueryString": path.split("?")[1] if "?" in path else "",
            "requestContext": {"http": {"method": method}}, "headers": {"content-type": "application/json", "x-forwarded-for": "1.2.3.4"},
            "cookies": [cookie] if cookie else [], "body": json.dumps(body) if body is not None else "", "isBase64Encoded": False}


def test_lambda_serves_the_whole_app():
    with mock_aws():
        make_table()
        os.environ["TABLE_NAME"] = "kagaz"
        import importlib
        import lambda_handler as L
        importlib.reload(L)
        try:
            r = L.handler(event("GET", "/"))
            assert r["statusCode"] == 200 and "Kagaz Saathi" in r["body"]
            assert L.handler(event("GET", "/kagaz.css"))["statusCode"] == 200
            assert L.handler(event("GET", "/app"))["statusCode"] == 302
            assert L.handler(event("GET", "/api/checks"))["statusCode"] == 401
            r = L.handler(event("POST", "/api/public/analyze", {"text": "Your bank account will be blocked, click the link to verify KYC"}))
            assert r["statusCode"] == 200 and json.loads(r["body"])["verdict"] == "scam"
            r = L.handler(event("POST", "/api/auth/signup", {"name": "Lambda User", "email": "l@example.com", "password": "Passw0rdOK"}))
            assert r["statusCode"] == 200 and r["cookies"]
            ck = r["cookies"][0].split(";")[0]
            r = L.handler(event("POST", "/api/analyze", {"text": "482915 is your OTP. Do not share it.", "lang": "hi"}, ck))
            out = json.loads(r["body"])
            assert r["statusCode"] == 200 and out["verdict"] == "genuine" and out["id"]
            assert json.loads(L.handler(event("GET", "/api/checks", cookie=ck))["body"])[0]["id"] == out["id"]
            r = L.handler(event("POST", "/api/auth/demo", {"persona": "parent"}))
            assert r["statusCode"] == 200
            dck = r["cookies"][0].split(";")[0]
            assert len(json.loads(L.handler(event("GET", "/api/checks", cookie=dck))["body"])) >= 3
            assert L.handler(event("GET", "/nothing"))["statusCode"] == 404
        finally:
            os.environ.pop("TABLE_NAME", None)
            importlib.reload(L)


def test_ses_alert_and_textract_switches(monkeypatch):
    import base64
    import boto3
    from kagaz import aws
    import kagaz.server as S
    from kagaz.store import Store
    import tempfile
    with mock_aws():
        boto3.client("ses", region_name="ap-south-1").verify_email_identity(EmailAddress="alerts@example.com")
        monkeypatch.setenv("ALERT_FROM_EMAIL", "alerts@example.com")
        monkeypatch.setenv("AWS_REGION", "ap-south-1")
        aws.send_alert_email("neha@example.com", "Test", "Hello")        # no exception = SES accepted it
        sent = boto3.client("ses", region_name="ap-south-1").get_send_quota()["SentLast24Hours"]
        assert sent >= 1
    assert not aws.textract_enabled()
    monkeypatch.setenv("KAGAZ_TEXTRACT", "1")
    assert aws.textract_enabled()
    png = base64.b64encode(b"\x89PNG\r\n\x1a\n" + b"0" * 20).decode()
    assert aws.decode_image("data:image/png;base64," + png)[:4] == b"\x89PNG"
    for bad in ("not-an-image", base64.b64encode(b"hello world").decode(), None):
        with pytest.raises(ValueError):
            aws.decode_image(bad)


def test_dynamo_rate_limit_counter(store):
    assert [store.hit("ip1", 2, 60) for _ in range(3)] == [True, True, False]
    assert store.hit("ip2", 2, 60)
