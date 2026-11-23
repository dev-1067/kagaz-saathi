"""Optional AWS integrations. Everything here is OFF unless its environment variable is set, so the app runs fully offline.

  KAGAZ_TEXTRACT=1        read photos of letters/bills with Amazon Textract (otherwise the browser reads them with Tesseract.js)
  ALERT_FROM_EMAIL=...    deliver family alerts to e-mail contacts with Amazon SES (the address must be verified in SES)
boto3 is imported lazily; it is available by default inside AWS Lambda.
"""
import base64
import os


def textract_enabled():
    return os.environ.get("KAGAZ_TEXTRACT") == "1"


def textract_text(image_bytes):
    """Plain text of an image (JPEG/PNG up to 5 MB) using Amazon Textract DetectDocumentText."""
    import boto3
    r = boto3.client("textract", region_name=os.environ.get("AWS_REGION")).detect_document_text(Document={"Bytes": image_bytes})
    return "\n".join(b["Text"] for b in r.get("Blocks", []) if b.get("BlockType") == "LINE").strip()


def decode_image(b64):
    if not isinstance(b64, str) or len(b64) > 7_000_000:
        raise ValueError("The image is too large. Please use a photo under 5 MB.")
    raw = base64.b64decode(b64.split(",")[-1], validate=False)
    if not (raw[:3] == b"\xff\xd8\xff" or raw[:8] == b"\x89PNG\r\n\x1a\n"):
        raise ValueError("Please upload a JPEG or PNG photo.")
    if len(raw) > 5_000_000:
        raise ValueError("The image is too large. Please use a photo under 5 MB.")
    return raw


def email_enabled():
    return bool(os.environ.get("ALERT_FROM_EMAIL"))


def send_alert_email(to_addr, subject, body):
    import boto3
    boto3.client("ses", region_name=os.environ.get("AWS_REGION")).send_email(
        Source=os.environ["ALERT_FROM_EMAIL"], Destination={"ToAddresses": [to_addr]},
        Message={"Subject": {"Data": subject[:120], "Charset": "UTF-8"}, "Body": {"Text": {"Data": body, "Charset": "UTF-8"}}})
