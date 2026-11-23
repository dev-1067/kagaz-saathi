"""Kagaz Saathi analyzer: text of a notice/SMS/WhatsApp message -> verdict, reasons, facts and next steps.

Two independent layers that must agree before something is called 'genuine':
  1. a trained classifier (notice_model.json, pure Python) that names the type of message;
  2. transparent rules that look for scam signals (asks for OTP/PIN, fee first, threat, secrecy, fake links...).
The result is deterministic and explainable: every verdict lists the exact signals that caused it.
"""
import re
from urllib.parse import urlparse

from . import content as C
from .notice_model import TacticModel

_MODEL = None


def model():
    global _MODEL
    if _MODEL is None:
        _MODEL = TacticModel()
    return _MODEL


URL_RE = re.compile(r"(?i)\b((?:https?://|www\.)[^\s<>\"']+|[a-z0-9][a-z0-9\-]*(?:\.[a-z0-9\-]+)*\.(?:com|in|co|net|org|xyz|top|club|cc|info|site|online|icu|buzz|live|click|link|win|vip|app|me|ly|gl|is|io|gov\.in|nic\.in)(?:/[^\s<>\"']*)?)")
PHONE_RE = re.compile(r"(?<![\d])(?:\+?91[\s-]?)?[6-9][\dX]{9}(?![\d])", re.I)
MONEY_RE = re.compile(r"(?i)(?:rs\.?|inr|₹)\s*([\d,]+(?:\.\d+)?)|([\d,]+)\s*(?:rupees|रुपये|रुपए)")
DATE_RE = re.compile(r"(?i)\b(\d{1,2}[-/ ](?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*(?:[-/ ]\d{2,4})?|\d{1,2}[-/]\d{1,2}[-/]\d{2,4})\b")
OTP_RE = re.compile(r"(?i)\b(?:otp|code|pin)\b[^.\n]{0,30}?\b(\d{4,8})\b|\b(\d{4,8})\b[^.\n]{0,25}\b(?:is your|otp)\b")


def _has(text, words):
    t = text.lower()
    return any(w in t for w in words)


ASK_SECRET = ("otp", "pin ", "pin.", "cvv", "password", "passcode", "verification code", "verification number", "the code", "code you", "code that",
              "ओटीपी", "पिन", "पासवर्ड", "सीवीवी", "card number", "card details", "net banking id", "last four digits", "bank details", "aadhaar number")
DONT_SHARE = ("share the delivery pin only", "share it only", "only with the rider", "only with the delivery", "ready only for the delivery", "do not share", "don't share", "never share", "do not disclose", "do not forward", "किसी के साथ साझा न", "न बताएं", "kisi ko na bataye", "share it with no")
ASK_MONEY = ("pay rs", "pay inr", "pay ₹", "deposit", "processing fee", "registration", "security amount", "clearance", "send rs", "transfer rs",
             "transfer inr", "fee ", "fees", "charges", "settlement", "tax first", "gst charges", "penalty", "bhejiye", "jama", "भेजें", "जमा", "शुल्क", "फीस",
             "pay a small", "pay the", "pay now", "pay immediately", "pay ")
URGENCY = ("immediately", "urgent", "within", "today", "tonight", "last warning", "final notice", "right now", "now or", "abhi", "turant", "तुरंत", "अभी",
           "30 minutes", "1 hour", "2 hours", "24 hours", "in 24", "expires today", "at once", "आज रात", "aaj raat")
THREAT = ("arrest", "warrant", "blocked", "block", "suspend", "freeze", "frozen", "disconnect", "cut off", "closed", "fir ", "penalty", "legal action",
          "deactivated", "barred", "seized", "giraftari", "band ho", "kaat", "गिरफ्तार", "बंद", "कट", "वारंट", "restricted")
SECRECY = ("do not tell", "tell no one", "do not inform", "don't tell", "kisi ko mat", "किसी को न", "do not disconnect", "stay on", "stay online",
           "keep this confidential", "not inform", "mat bata", "mat batai")
REMOTE = ("anydesk", "teamviewer", "quicksupport", "screen share", "share the screen", "share your screen", "install the app", "install this app",
          "download the support app", "download the app", ".apk", "allow contacts", "contacts access", "skype", "video call")
TOO_GOOD = ("won", "winner", "lottery", "lucky draw", "congratulations", "prize", "gift", "cashback", "bonus", "refund of", "refund is", "eligible for a refund",
            "guaranteed", "double your money", "sure profit", "risk free", "free recharge", "badhai", "बधाई", "लॉटरी", "इनाम", "रिफंड", "मुनाफा", "earn rs", "earn ")


MONEY_ASK = re.compile(r"(?i)\b(send|sent|transfer|pay|deposit|advance|bhej\s?do|bhejo|bhejiye|bhej\s?dijiye)\b|जमा|भेजें|भेज\s?दो|भेजिए")


def _money_request(text):
    return bool(MONEY_ASK.search(text))


def extract(text):
    urls = []
    for m in URL_RE.finditer(text):
        u = m.group(1).rstrip(".,;)")
        if "@" in u:
            continue
        urls.append(u)
    phones = sorted({re.sub(r"[\s-]", "", m.group(0)) for m in PHONE_RE.finditer(text)})
    amounts = []
    for m in MONEY_RE.finditer(text):
        raw = (m.group(1) or m.group(2) or "").replace(",", "")
        try:
            amounts.append(float(raw))
        except ValueError:
            pass
    return {"urls": list(dict.fromkeys(urls)), "phones": phones, "amounts": amounts,
            "dates": list(dict.fromkeys(m.group(1) for m in DATE_RE.finditer(text))),
            "otp": next((g for m in OTP_RE.finditer(text) for g in m.groups() if g), None)}


def host_of(url):
    u = url if "://" in url else "http://" + url
    try:
        return (urlparse(u).hostname or "").lower()
    except ValueError:
        return ""


def judge_link(url):
    """'official' | 'short' | 'lookalike' | 'unknown'."""
    h = host_of(url)
    if not h:
        return "unknown"
    if any(h == s.lstrip(".") or h.endswith(s) for s in C.OFFICIAL_SUFFIXES):
        return "official"
    if h in C.SHORTENERS:
        return "short"
    brandy = any(b in h for b in C.BRAND_WORDS)
    risky = h.endswith(C.RISKY_TLDS) or h.count("-") >= 1
    if brandy and (risky or not h.endswith(".in")):
        return "lookalike"
    if brandy or h.endswith(C.RISKY_TLDS):
        return "lookalike" if brandy else "unknown"
    return "unknown"


def analyze(text, lang="en"):
    lang = lang if lang in ("en", "hi", "mr") else "en"
    text = (text or "").strip()[:4000]
    if not text:
        raise ValueError("Paste a message or upload a photo first.")
    facts = extract(text)
    probs = model().proba(text)
    top = max(probs, key=probs.get)
    p_scam = sum(v for k, v in probs.items() if k in C.SCAM)

    links = [(u, judge_link(u)) for u in facts["urls"]]
    sig = {}
    dont = _has(text, DONT_SHARE)
    if _has(text, ASK_SECRET) and not dont:
        sig["asks_secret"] = True
    if _has(text, ASK_MONEY) and (top in C.SCAM or facts["amounts"]) and not (top in ("bank_alert", "bill_reminder", "govt_notice") and not links):
        sig["asks_money"] = top in C.SCAM or p_scam > 0.3
    if _has(text, URGENCY) and (top in C.SCAM or p_scam > 0.3):
        sig["urgency"] = True
    if _has(text, THREAT) and (top in C.SCAM or p_scam > 0.3):
        sig["threat"] = True
    if _has(text, SECRECY):
        sig["secrecy"] = True
    if _has(text, REMOTE):
        sig["remote_app"] = True
    if any(k == "short" for _, k in links):
        sig["short_link"] = True
    if any(k == "lookalike" for _, k in links):
        sig["fake_domain"] = True
    if facts["phones"] and top in C.SCAM:
        sig["personal_number"] = True
    if _has(text, TOO_GOOD) and top in ("prize_lottery", "refund_fraud", "investment_loan", "job_fraud"):
        sig["too_good"] = True
    good = []
    if dont:
        good.append("no_share")
    if any(k == "official" for _, k in links) and not sig.get("fake_domain"):
        good.append("official_link")
    sig = {k: v for k, v in sig.items() if v}

    # --- score: model probability + transparent rule weights
    weights = {"asks_secret": 0.45, "asks_money": 0.25, "urgency": 0.12, "threat": 0.18, "secrecy": 0.30, "remote_app": 0.35, "short_link": 0.25,
               "fake_domain": 0.40, "personal_number": 0.12, "too_good": 0.15}
    rule = min(1.0, sum(weights[k] for k in sig))
    score = max(p_scam, min(1.0, 0.55 * p_scam + 0.75 * rule)) if sig else p_scam * 0.9
    hard = bool(sig.get("asks_secret") and top not in ("otp_notice", "bank_alert")) or bool(sig.get("fake_domain") and sig.get("urgency")) \
        or bool(sig.get("secrecy") and (sig.get("threat") or sig.get("asks_money"))) or bool(sig.get("remote_app") and top in C.SCAM)
    if top in C.SCAM and probs[top] >= 0.6:
        verdict = "scam"
    elif hard or score >= 0.75:
        verdict = "scam"
    elif score >= 0.35 or sig.get("fake_domain") or sig.get("short_link"):
        verdict = "suspicious"
    else:
        verdict = "genuine"
    # An impersonation scam always ends in a request for money. A new-number message from a relative that asks for none
    # (very common and harmless) is only worth a second look.
    if verdict == "scam" and top == "impersonation_advance" and not _money_request(text) and not sig.get("asks_secret")             and not sig.get("secrecy") and not sig.get("remote_app"):
        verdict = "suspicious"
    if verdict == "genuine" and top in C.SCAM:
        verdict = "suspicious"
    risk = int(round(100 * (score if verdict != "genuine" else min(score, 0.3))))
    if verdict == "scam":
        risk = max(risk, 80)
    kind = top if (verdict != "genuine" or top not in C.SCAM) else "general"
    if verdict == "scam" and kind not in C.SCAM:
        kind = max((k for k in probs if k in C.SCAM), key=probs.get)

    steps = {"scam": C.STEPS_SCAM, "suspicious": C.STEPS_SUSPICIOUS, "genuine": C.STEPS_GENUINE}[verdict][lang]
    reasons = [C.SIGNALS[k][lang] for k in sig] + [C.SIGNALS[k][lang] for k in good]
    return {
        "verdict": verdict, "verdict_label": C.VERDICT[verdict][lang], "risk": risk,
        "kind": kind, "kind_label": C.LABELS[kind][lang], "confidence": round(probs[top], 3),
        "explanation": C.WHY[kind][lang], "reasons": reasons, "signals": list(sig) + good, "steps": steps,
        "facts": {"links": [{"url": u, "judgement": k} for u, k in links], "phones": facts["phones"], "amounts": facts["amounts"],
                  "dates": facts["dates"], "otp": bool(facts["otp"])},
        "helplines": C.HELPLINES if verdict != "genuine" else C.HELPLINES[:2], "lang": lang,
        "model": {"top": top, "p_scam": round(p_scam, 3)},
    }
