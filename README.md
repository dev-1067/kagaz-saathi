# Kagaz Saathi (कागज़ साथी)

**Got a strange message? Ask Kagzi first.** Paste any SMS, WhatsApp message, bill or notice (or upload a photo). Kagaz Saathi
tells you if it is genuine, suspicious or a scam, lists the exact reasons, explains it in **English, Hindi or Marathi** with
voice, tells you what to do next (and by when), offers one-tap reporting to **1930 / Chakshu**, and can alert a family member.

Built by Team HackBots for the *Campus to Cloud Hackathon sponsored by AWS* (Techfest, IIT Bombay 2026-27).

## Run it locally (no account, no internet needed)
```powershell
pip install -r requirements-dev.txt        # only for training and tests; the app itself is Python standard library + SQLite
python -m kagaz.server                     # http://localhost:8030
```
Open http://localhost:8030 and click **Try the live demo**, or create an account. Three demo personas (Parent, Student, Family) have seeded history.

## What is inside
| Part | Where | Notes |
|---|---|---|
| Classifier | `model/`, `kagaz/notice_model.json` | TF-IDF (char 2-5 + word 1-2) + logistic regression trained by SGD epoch by epoch; exported to pure Python (no numpy at run time) |
| Analyzer | `kagaz/analyzer.py` | Model + transparent rules (asks for OTP/PIN, fee first, threat, secrecy, remote-access app, fake/short links). Every verdict lists its reasons |
| Content | `kagaz/content.py` | Hand-written explanations in English, Hindi, Marathi; helplines; official-domain list |
| Web app | `web/`, `kagaz/server.py` | Landing page, sign-up/sign-in, dashboard, checker, history, family circle, scam guide, helplines, accuracy page |
| Storage | `kagaz/store.py`, `infra/dynamo_store.py` | SQLite locally, DynamoDB on AWS (same interface). Salted PBKDF2 passwords, HttpOnly sessions |
| AWS | `infra/` | Lambda Function URL + DynamoDB + CloudWatch, one SAM template (optional SES). **Deployed and tested live.** See `infra/DEPLOY.md` |

## Results (all reproducible)
| Test | Result |
|---|---|
| 15-way classifier, **150 unseen hand-written messages** (never used for training or tuning) | **99.3%** (149/150) |
| Scam vs genuine on the same messages | 99.3% |
| Hard stress set 1 (40 tricky messages), full pipeline | 100% of scams flagged, 0 real messages called "scam" (used to find weaknesses, then fixed) |
| Hard stress set 2 (20 new tricky messages, written after the fixes) | 100% of scams flagged (50% called "scam", 50% "suspicious"), 0 real messages called "scam", 60% of real ones left alone, 40% "suspicious" |
| Stress sets 3 and 4 (54 more tricky messages, set 4 fully blind) | 100% of scams flagged, none called genuine, 0 real messages called "scam"; about 92% of real ones left alone, the rest "suspicious" |
| Unit + API + AWS-mock tests | 31 pass (`python -m pytest tests --ignore=tests/e2e.py`) |
| Browser test of every page and button (Chromium) | 11 steps, 0 console errors (`python tests/e2e.py`, server running) |

**Honest limits.** The 150 test messages were written by the team that built the model, in the same few languages, so real-world accuracy
will be lower on new scam styles; the stress sets are the more realistic guide. The AWS stack passes tests against a *mock* of AWS (moto) and the
11-step browser test passes against the **real deployment** (Lambda + DynamoDB, Sydney); Textract is blocked on Free-plan accounts, so photos are read in the browser. Hindi and Marathi text is hand-written, not reviewed by a native speaker, and should be before public launch.
Abuse protection: per-network and per-account rate limits stored in the database (SQLite / DynamoDB), 30 KB request cap. Share target: install the site to the phone home screen and share a WhatsApp message to it. A wrong verdict is possible; the app always says to verify in the official app and to call 1930 if money was lost.

## Reproduce training
```powershell
python model/make_fresh_test.py   # frozen test + dev sets (hand-written)
python model/make_data.py         # training templates -> model/data/train.jsonl
python model/train.py             # trains, picks settings on dev only, scores the test set once, exports the model
python model/make_stress.py ; python model/eval_stress.py
```

## Deploy to AWS
See [`infra/DEPLOY.md`](infra/DEPLOY.md). You create the AWS account and student verification yourself; the package and template are ready.
