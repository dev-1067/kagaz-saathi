"""Builds the two Round 1 documents (Idea Brief, Build Summary) as PDFs from results/*.json and docs/config.json.

    python docs/build_docs.py

docs/config.json holds the values that only exist after deployment (live URL, Builder Center alias). Until they are filled in,
the PDFs say "to be added after deployment" instead of inventing them.
"""
import json
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
CFG = json.loads((ROOT / "docs" / "config.json").read_text(encoding="utf-8"))
M = json.loads((ROOT / "results" / "model_report.json").read_text(encoding="utf-8"))
S = json.loads((ROOT / "results" / "stress_report.json").read_text(encoding="utf-8"))
URL = CFG.get("live_url") or ""
ALIAS = CFG.get("builder_alias") or ""
url_html = f'<a href="{URL}">{URL}</a>' if URL else '<span class="todo">to be added after deployment</span>'
alias_html = ALIAS if ALIAS else '<span class="todo">to be added</span>'
acc = f"{100 * M['test_accuracy']:.1f}%"
s2 = S["stress2"]
s3, s4 = S["stress3"], S["stress4"]

CSS = """
@page { size: A4; margin: 15mm 16mm; }
:root { --ink:#241f19; --body:#3b352c; --indigo:#1f5f4a; --saf:#e0762a; --mute:#7b7262; --line:#e7dcc8; }
body { margin:0; font-family:"Segoe UI","Noto Sans Devanagari",Arial,sans-serif; color:var(--body); font-size:10.4pt; line-height:1.48; }
.head { display:flex; justify-content:space-between; align-items:flex-end; border-bottom:2pt solid var(--indigo); padding-bottom:7pt; margin-bottom:9pt; }
.k { font-size:8pt; letter-spacing:.1em; text-transform:uppercase; color:var(--saf); font-weight:700; }
h1 { font-size:22pt; margin:2pt 0 0; color:var(--ink); letter-spacing:-.01em; } h1 span { color:var(--indigo); }
.meta { text-align:right; font-size:8.6pt; color:var(--mute); }
h2 { font-size:11.8pt; color:var(--ink); margin:10pt 0 3pt; } p { margin:0 0 5pt; text-align:justify; } b { color:var(--ink); }
ul { margin:2pt 0 5pt; padding-left:15pt; } li { margin-bottom:2pt; }
table { width:100%; border-collapse:collapse; margin:4pt 0 6pt; font-size:9.4pt; } th { text-align:left; background:#eef0fa; color:var(--ink); padding:4pt 6pt; font-size:8.6pt; }
td { padding:4pt 6pt; border-bottom:1px solid var(--line); vertical-align:top; }
.box { background:#f4f5fc; border-left:3pt solid var(--saf); padding:6pt 9pt; margin:6pt 0; border-radius:3pt; }
.todo { background:#fff1d9; color:#8a4b00; padding:0 4pt; border-radius:3pt; font-weight:600; }
.foot { margin-top:8pt; padding-top:5pt; border-top:.6pt solid var(--line); font-size:8.2pt; color:var(--mute); }
a { color:var(--indigo); }
"""

BRIEF = f"""
<div class="head"><div><div class="k">Campus to Cloud Hackathon · Idea Brief</div><h1>Kagaz Saathi <span>· कागज़ साथी</span></h1></div>
<div class="meta">Team HackBots · Devaansh Sharma (team leader)<br>Techfest, IIT Bombay 2026-27<br>Builder Center alias: {alias_html}<br>Live prototype: {url_html}</div></div>

<h2>The problem</h2>
<p>Indians lost roughly <b>₹20,000 to ₹22,500 crore</b> to cyber fraud in 2025 (figures differ by source: I4C/NCRP data reported by ThePrint and others), and the
Department of Telecom received <b>5.2 lakh</b> reports of suspected fraud calls and messages on Chakshu in 2025, up from 2.1 lakh in 2024. Most of these scams succeed
for one reason: the victim has <b>nobody to ask in the moment</b>. A "digital arrest" caller says <i>do not tell anyone</i>; a fake KYC link says <i>your account closes
in two hours</i>; a fake task job takes a "refundable" deposit. Real messages (bank alerts, OTPs, bills, pension notices) look almost the same, so people
either trust everything or panic at everything, and scams are described in English while many victims read Hindi or Marathi.</p>

<h2>Who it is for</h2>
<ul><li><b>Parents and grandparents</b> who receive bank, pension and "police" messages and are the main target of digital-arrest and KYC scams.</li>
<li><b>Students and first-time earners</b> who meet fake internships, task jobs and loan apps.</li>
<li><b>Families</b>: the son or daughter who is usually the one asked for help, often after the money has gone.</li></ul>

<h2>How the solution works</h2>
<p><b>1. Share it.</b> Paste an SMS, WhatsApp message or notice, or upload a photo of a letter or screenshot. <b>2. Verdict with reasons.</b> Kagzi returns
<i>genuine</i>, <i>suspicious</i> or <i>very likely a scam</i> with a 0-100 risk and every reason listed (for example "asks for an OTP", "link looks like a bank site but is not
official", "tells you not to inform anyone"). A trained classifier names the type of message (16 types) and transparent rules look for scam signals, so the result is
explainable, not a black box. <b>3. Understand it.</b> A plain explanation and next steps in <b>English, Hindi or Marathi</b>, read aloud, with deadlines and facts pulled
out of the message. <b>4. Act safely.</b> One tap to the <b>1930</b> cyber-fraud helpline and Chakshu, and one tap to <b>alert a family member</b> with the verdict
and what to do. History, a scam guide and a family circle keep everything in one place.</p>

<h2>Impact and how we measure it</h2>
<table><tr><th>What we measured</th><th>Result</th></tr>
<tr><td>Classifier on {M['test_size']} unseen hand-written messages (never used for training or tuning)</td><td><b>{acc}</b> ({round(M['test_accuracy'] * M['test_size'])}/{M['test_size']}); scam-vs-genuine {100 * M['test_scam_vs_genuine_accuracy']:.1f}%</td></tr>
<tr><td>{s2['n']} extra tricky messages written after the first round of fixes (real messages that sound scary, scams in unusual wording)</td><td>{100 * s2['scam_flagged_rate']:.0f}% of scams flagged ({100 * s2['scam_caught_as_scam_rate']:.0f}% as outright scams, the rest as "suspicious"); {100 * s2['genuine_false_scam_rate']:.0f}% of real messages called a scam</td></tr>
<tr><td>{s3['n'] + s4['n']} more tricky messages in two further rounds ({s4['n']} fully blind, written after the final fixes): new scam styles and scary-sounding real notices</td><td>{100 * min(s3['scam_flagged_rate'], s4['scam_flagged_rate']):.0f}% of scams flagged, none called genuine; {100 * s3['genuine_false_scam_rate']:.0f}% of real messages called a scam; about {100 * (s3['genuine_clean_rate'] + s4['genuine_clean_rate']) / 2:.0f}% of real messages left alone, the rest marked "suspicious"</td></tr>
<tr><td>Automated tests</td><td>26 unit/API/AWS-mock tests and a 10-step browser test of every page and button, all passing, zero console errors</td></tr></table>
<p>Every scam stopped is money kept, and the first hour after a fraud matters most, which is why the app puts 1930 and a family alert one tap away. <b>We have not yet run a pilot with real users</b>, so we make no claim about people helped; a small pilot with family and
classmates is planned before Demo Day and its results will replace this sentence.</p>

<h2>What is new</h2>
<ul><li><b>It explains genuine paperwork too</b>, not just scams: the same message that is flagged teaches you why, and a real bank alert is recognised and left alone.</li>
<li><b>Family loop built in</b>: it answers the scammer's "tell no one" by telling someone you trust.</li>
<li><b>Honest, tested numbers</b>: held-out test set, two stress sets, a published confusion matrix and a list of what it gets wrong, visible inside the app.</li>
<li><b>Regional languages with voice</b>, hand-written (not machine-translated) explanations, running on a tiny pure-Python model that needs no GPU.</li></ul>

<div class="foot">Limits stated openly: the unseen test messages were written by the same team as the training data, so real-world accuracy will be lower on new scam styles; Hindi and Marathi text should be reviewed by native speakers before public launch;
Kagzi can be wrong and always tells users to verify in the official app and call 1930 if money was lost. Sources: ThePrint (I4C/NCRP data) for losses; Rajya Sabha reply (Feb 2026) on Chakshu reports.</div>
"""

BUILD = f"""
<div class="head"><div><div class="k">Campus to Cloud Hackathon · Build Summary</div><h1>Kagaz Saathi <span>· on AWS</span></h1></div>
<div class="meta">Team HackBots · Devaansh Sharma<br>Builder Center alias: {alias_html}<br>Live prototype: {url_html}<br>Code: github.com/dev-1067/kagaz-saathi</div></div>

<h2>AWS services used, and why</h2>
<table><tr><th style="width:24%">Service</th><th>What it does in Kagaz Saathi</th><th style="width:26%">Why this one</th></tr>
<tr><td><b>AWS Lambda + Function URL</b></td><td>Serves the whole app (pages, static files, JSON API) from one function; the same server code runs locally and in Lambda through a small adapter</td><td>No servers to manage, free at demo traffic, one public HTTPS URL</td></tr>
<tr><td><b>Amazon DynamoDB</b></td><td>One on-demand table for accounts, sessions (with TTL), saved checks, family circle and the alert outbox</td><td>Serverless, scales to zero cost, TTL expires sessions automatically</td></tr>
<tr><td><b>IAM + CloudFormation / SAM</b></td><td>A least-privilege role for the function and one template that creates the table, function and public URL (deployed with one command)</td><td>Repeatable and deletable in one command</td></tr>
<tr><td><b>Amazon SES</b> (optional, available but not switched on)</td><td>Can deliver family alerts to e-mail contacts once a sender address is verified</td><td>Cheap, managed e-mail</td></tr>
<tr><td><b>Amazon CloudWatch</b></td><td>Logs and errors for the Lambda function</td><td>Built in</td></tr>
</table>
<p>The classifier itself deliberately does <b>not</b> need Bedrock, a GPU or any paid inference: it is a TF-IDF + logistic-regression model exported to plain Python (1.6 MB), so every
check costs effectively nothing and answers in milliseconds.</p>

<h2>How it was built</h2>
<ul><li><b>Model.</b> 16 message types (10 scam, 6 genuine; the impersonation scam type was added after stress testing). Trained on ~8,000 template-generated messages in English, Hinglish and Devanagari; settings (epoch, regularisation) chosen on a separate hand-written dev set; scored once on {M['test_size']} unseen hand-written messages: <b>{acc}</b>.</li>
<li><b>Analyzer.</b> Model probability plus transparent rules (asks for OTP/PIN/CVV, fee first, threat, secrecy, remote-access app, shortened or look-alike links, personal phone numbers). Every verdict lists the exact signals behind it.</li>
<li><b>Web app.</b> Landing page, sign-up/sign-in (salted PBKDF2 passwords, HttpOnly sessions), dashboard with charts, checker with read-aloud, history, family circle, scam guide, helplines, and a model-accuracy page. Plain HTML/CSS/JS, no build step.</li>
<li><b>Testing.</b> 31 automated tests (model, analyzer, accounts, privacy between users, API, DynamoDB store and Lambda handler against a mock of AWS) and a browser test that clicks every page and button in Chromium with zero console errors. The stress tests found real weaknesses (real messages called scams, a missing scam type); we fixed them and re-tested on fresh messages in three more rounds. Public endpoints are rate-limited per network and per account (counted in the database), request size is capped, and a share-to-Kagzi target lets a WhatsApp message be sent straight in.</li></ul>

<h2>Deployment and cost</h2>
<p>Deployed with <b>SAM</b> to <b>ap-southeast-2 (Sydney)</b>, the region this Free-plan account is tied to: Lambda and DynamoDB on-demand fit inside the free allowances at demo traffic. Package size is 3.6 MB. Steps are in <b>infra/DEPLOY.md</b>.</p>
<div class="box"><b>Status, stated plainly:</b> the stack is <b>live</b> and the 10-step browser test (sign-up, sign-in, checks, family alerts, history, demo accounts) passes against it. On this Free-plan account Amazon Textract, Translate and Comprehend are blocked by an organisation policy, so we did not use them: photos are read in the browser (Tesseract.js) and read-aloud uses the browser's voices.</div>

<h2>Key decisions</h2>
<ul><li><b>Explainable over opaque</b>: users (and jurors) can see why a message was flagged, which matters for trust in a safety tool.</li>
<li><b>Tiny model, real tests</b>: a 1.6 MB model with honest held-out numbers beats a large model we cannot evaluate.</li>
<li><b>One function, one table</b>: fewest moving parts that still use AWS properly, easy to explain and cheap to keep live until Demo Day.</li></ul>
<div class="foot">Repository: github.com/dev-1067/kagaz-saathi · README.md and infra/DEPLOY.md describe how to run, test and deploy · Authored by dev-1067.</div>
"""


def pdf(body, name):
    html = f"<!doctype html><meta charset=utf-8><style>{CSS}</style><body>{body}</body>"
    out = ROOT / "docs" / name
    tmp = ROOT / "docs" / f"_{name}.html"
    tmp.write_text(html, encoding="utf-8")
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page()
        pg.goto(tmp.as_uri())
        pg.wait_for_timeout(500)
        pg.pdf(path=str(out), format="A4", print_background=True, prefer_css_page_size=True)
        b.close()
    tmp.unlink()
    import pymupdf
    print(name, "pages:", len(pymupdf.open(str(out))))


if __name__ == "__main__":
    pdf(BRIEF, "Idea_Brief_Kagaz_Saathi.pdf")
    pdf(BUILD, "Build_Summary_Kagaz_Saathi.pdf")
