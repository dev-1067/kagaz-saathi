"""AWS Lambda entry point. Serves the whole app (pages, static files, JSON API) behind a Lambda Function URL.

It reuses kagaz/server.py unchanged: each invocation feeds the incoming request to the same
BaseHTTPRequestHandler through an in-memory socket and turns the raw HTTP response back into a Function-URL response.
Storage is DynamoDB (infra/dynamo_store.py) when TABLE_NAME is set, otherwise SQLite in /tmp (local tests).
"""
import base64
import io
import os
import sys
from http.client import HTTPResponse
from pathlib import Path

os.environ.setdefault("KAGAZ_DB", "/tmp/kagaz.db")          # Lambda's only writable folder (used only without DynamoDB)
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import kagaz.server as S  # noqa: E402

if os.environ.get("TABLE_NAME"):
    from dynamo_store import DynamoStore  # noqa: E402
    S.DB = DynamoStore(os.environ["TABLE_NAME"], region=os.environ.get("AWS_REGION"), endpoint_url=os.environ.get("DDB_ENDPOINT") or None)


class _Sock:
    def __init__(self, raw):
        self.rin, self.out = io.BytesIO(raw), io.BytesIO()

    def makefile(self, mode, *a, **k):
        return self.rin if "r" in mode else self.out

    def sendall(self, data):
        self.out.write(data)

    def close(self):
        pass


class _Srv:
    server_name, server_port = "lambda", 443


def handler(event, context=None):
    http = event.get("requestContext", {}).get("http", {})
    method = http.get("method", event.get("httpMethod", "GET"))
    path = event.get("rawPath", event.get("path", "/")) + (("?" + event["rawQueryString"]) if event.get("rawQueryString") else "")
    body = event.get("body") or ""
    body = base64.b64decode(body) if event.get("isBase64Encoded") else body.encode("utf-8")
    headers = {k.lower(): v for k, v in (event.get("headers") or {}).items()}
    if event.get("cookies"):
        headers["cookie"] = "; ".join(event["cookies"])
    lines = [f"{method} {path} HTTP/1.1", f"Content-Length: {len(body)}"] + [f"{k}: {v}" for k, v in headers.items() if k not in ("content-length", "host", "connection")]
    raw = ("\r\n".join(lines) + "\r\n\r\n").encode("utf-8") + body
    sock = _Sock(raw)
    S.H(sock, (headers.get("x-forwarded-for", "0.0.0.0").split(",")[0].strip(), 0), _Srv())
    resp = HTTPResponse(_Resp(sock.out.getvalue()))
    resp.begin()
    data = resp.read()
    hdrs, cookies = {}, []
    for k, v in resp.getheaders():
        if k.lower() == "set-cookie":
            cookies.append(v)
        elif k.lower() not in ("content-length", "server", "date"):
            hdrs[k] = v
    ctype = hdrs.get("Content-Type", "")
    is_text = ctype.startswith(("text/", "application/json", "image/svg", "application/javascript"))
    out = {"statusCode": resp.status, "headers": hdrs, "isBase64Encoded": not is_text, "body": data.decode("utf-8") if is_text else base64.b64encode(data).decode()}
    if cookies:
        out["cookies"] = cookies
    return out


class _Resp:
    def __init__(self, raw):
        self.raw = io.BytesIO(raw)

    def makefile(self, mode):
        return self.raw
