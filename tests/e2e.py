"""Browser end-to-end test: clicks every page and button of Kagaz Saathi in a real Chromium.

    python -m kagaz.server &        (port 8030)
    python tests/e2e.py [http://localhost:8030]

Fails on any console error, page error, or failed expectation. Saves screenshots to docs/screenshots.
"""
import re
import sys
import time
from pathlib import Path

from playwright.sync_api import expect, sync_playwright

BASE = (sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8030").rstrip("/")
SHOTS = Path(__file__).resolve().parents[1] / "docs" / "screenshots"
SHOTS.mkdir(parents=True, exist_ok=True)
errors, steps = [], []
ALLOW = {"http": False}


def ok(m):
    steps.append(m)
    print("  ok", m)


with sync_playwright() as p:
    browser = p.chromium.launch()
    ctx = browser.new_context(viewport={"width": 1440, "height": 900})
    ctx.grant_permissions([])
    page = ctx.new_page()
    page.on("console", lambda m: m.type == "error" and "fonts.g" not in m.text and "tesseract" not in m.text.lower()
            and not (ALLOW["http"] and "Failed to load resource" in m.text) and errors.append(f"console: {m.text}"))
    page.on("pageerror", lambda e: errors.append(f"pageerror: {e}"))
    email = f"e2e{int(time.time())}@example.com"
    pw = "Shop2026safe"

    # ---------------- WhatsApp "Share -> Kagzi" target
    page.goto(BASE + "/share?text=" + "Dear customer your SBI account will be blocked today. Update KYC now at sbi-kyc-update.in and enter your card details.".replace(" ", "%20"))
    expect(page.locator("#t-out .vtitle")).to_contain_text("scam", ignore_case=True, timeout=15000)
    assert page.evaluate("location.pathname") == "/"
    ok("shared message opens Kagzi already checked (share target)")

    # ---------------- landing page
    page.goto(BASE + "/")
    expect(page.locator(".hero h1")).to_contain_text("Ask Kagzi first")
    expect(page.locator("#h-acc")).not_to_have_text("–", timeout=10000)
    expect(page.locator("#samples .chip").first).to_be_visible(timeout=10000)
    page.locator("#samples .chip").first.click()
    expect(page.locator("#t-out .vtitle")).to_contain_text("scam", ignore_case=True, timeout=10000)
    page.locator("#t-lang button[data-l='hi']").click()
    expect(page.locator("#t-out .vtitle")).to_contain_text("ठगी", timeout=10000)
    page.locator("#t-lang button[data-l='en']").click()
    page.locator("#samples .chip").nth(2).click()            # the real OTP message
    expect(page.locator("#t-out .vtitle")).to_contain_text("genuine", ignore_case=True, timeout=10000)
    page.locator("#t-say").click()                            # speech may be unavailable headless; must not error
    page.locator("details summary").first.click()
    expect(page.locator("details").first).to_have_attribute("open", "")
    page.locator(".nav-links a[href='#proof']").click()
    page.wait_for_timeout(700)
    page.screenshot(path=str(SHOTS / "00_landing.png"))
    ok("landing page: stats load, samples give scam and genuine verdicts, Hindi switch, read aloud, FAQ, nav")

    # ---------------- protected app + 404
    ALLOW["http"] = True
    page.goto(BASE + "/app")
    expect(page).to_have_url(re.compile(r"/signin\?next="))
    r = page.goto(BASE + "/nothing-here")
    assert r.status == 404
    expect(page.get_by_text("Kagzi looked everywhere")).to_be_visible()
    ALLOW["http"] = False
    ok("app needs a session; unknown page shows 404")

    # ---------------- sign-up validation + success
    page.goto(BASE + "/signup")
    page.locator("#go").click()
    expect(page.locator(".field.bad")).to_have_count(3)
    page.fill("#name", "E2E Tester"); page.fill("#email", email); page.fill("#password", "short")
    page.locator("#go").click()
    expect(page.locator("#f-password .err")).to_contain_text("8 characters")
    page.fill("#password", pw)
    page.locator("#peek").click()
    expect(page.locator("#password")).to_have_attribute("type", "text")
    page.screenshot(path=str(SHOTS / "01_signup.png"))
    page.locator("#go").click()
    page.wait_for_url(re.compile(r"/app"), timeout=15000)
    expect(page.locator("#who-n")).to_have_text("E2E Tester", timeout=10000)
    expect(page.locator(".greet h2")).to_contain_text("E2E", timeout=10000)
    ok("sign-up: validation, strength rules, account created, dashboard greets by name")

    # ---------------- sign out, wrong password, duplicate, sign in
    page.locator("#who").click(); page.locator("#signout").click()
    page.wait_for_url(re.compile(r"/signin"))
    ALLOW["http"] = True
    page.fill("#email", email); page.fill("#password", "Wrong12345"); page.locator("#go").click()
    expect(page.locator("#ferr")).to_contain_text("incorrect")
    page.locator("#tab-up").click()
    page.fill("#name", "Other"); page.fill("#email", email); page.fill("#password", pw); page.locator("#go").click()
    expect(page.locator("#ferr")).to_contain_text("already exists")
    page.locator("#tab-in").click()
    page.fill("#email", email); page.fill("#password", pw); page.locator("#go").click()
    page.wait_for_url(re.compile(r"/app"), timeout=15000)
    ALLOW["http"] = False
    ok("sign-out, wrong password refused, duplicate email refused, sign-in works")

    # ---------------- check page: scam, genuine, Hindi, report, speak, copy
    page.goto(BASE + "/app#/check")
    expect(page.locator("#smp .chip").first).to_be_visible(timeout=10000)
    page.locator("#go").click()                                # empty: toast, no crash
    page.locator("#smp .chip").nth(0).click()
    expect(page.locator("#out .vtitle")).to_contain_text("scam", ignore_case=True, timeout=10000)
    expect(page.locator("#out .reasons li").first).to_be_visible()
    page.locator("#say").click()
    page.locator("#rep").click()
    expect(page.locator("#rep")).to_have_text("Reported ✓", timeout=10000)
    page.locator("#c-lang button[data-l='mr']").click()
    expect(page.locator("#out .vtitle")).to_contain_text("फसवणूक", timeout=10000)
    page.locator("#c-lang button[data-l='en']").click()
    page.fill("#txt", "Hi, are we meeting tomorrow at 1 pm for lunch?")
    page.locator("#go").click()
    expect(page.locator("#out .vtitle")).to_contain_text("genuine", ignore_case=True, timeout=10000)
    page.fill("#txt", "Dear customer your HDFC account will be blocked today. Update KYC at hdfc-kyc-update.xyz and share the OTP.")
    page.locator("#go").click()
    expect(page.locator("#out .vtitle")).to_contain_text("scam", ignore_case=True, timeout=10000)
    page.screenshot(path=str(SHOTS / "02_check.png"))
    ok("check page: scam, genuine and Hindi/Marathi results, reasons listed, read aloud, report, clear errors")

    # ---------------- family: add (validation), alert from check, outbox, remove
    page.goto(BASE + "/app#/family")
    expect(page.locator("#ff")).to_be_visible(timeout=10000)
    ALLOW["http"] = True
    page.locator("#ff button").click()
    expect(page.locator("#fe")).to_contain_text("name")
    page.fill("#fn", "Neha"); page.fill("#fr", "Daughter"); page.fill("#fc", "not-a-contact"); page.locator("#ff button").click()
    expect(page.locator("#fe")).to_contain_text("valid")
    ALLOW["http"] = False
    page.fill("#fc", "neha@example.com"); page.locator("#ff button").click()
    expect(page.locator(".hlc", has_text="Neha")).to_be_visible(timeout=10000)
    page.goto(BASE + "/app#/check")
    page.locator("#smp .chip").nth(0).click()
    expect(page.locator("#alert")).to_be_visible(timeout=10000)
    page.locator("#alert").click()
    expect(page.locator("#alert")).to_have_text("Alert ready ✓", timeout=10000)
    page.goto(BASE + "/app#/family")
    expect(page.locator(".hlc", has_text="To Neha")).to_be_visible(timeout=10000)
    page.screenshot(path=str(SHOTS / "03_family.png"))
    ok("family: validation, add member, alert from a check lands in the outbox")

    # ---------------- dashboard, history (filter, search, drawer, delete, export), learn, help, accuracy
    page.goto(BASE + "/app#/dashboard")
    expect(page.locator(".kpi").first).to_be_visible(timeout=10000)
    expect(page.locator("#view svg").first).to_be_visible()
    page.screenshot(path=str(SHOTS / "04_dashboard.png"))
    page.locator("tr.click").first.click()
    expect(page.locator("#drawer")).to_have_class(re.compile("open"))
    page.locator("#dx").click()
    page.goto(BASE + "/app#/history")
    expect(page.locator("#hrows tr.click").first).to_be_visible(timeout=10000)
    n = page.locator("#hrows tr.click").count()
    page.locator("#hseg button[data-v='scam']").click()
    assert page.locator("#hrows tr.click").count() >= 1
    page.locator("#hseg button[data-v='all']").click()
    page.fill("#hq", "zzzz-nothing")
    expect(page.get_by_text("No checks match")).to_be_visible()
    page.fill("#hq", "")
    page.locator("#hrows tr.click td").first.click()
    expect(page.locator("#drawer")).to_have_class(re.compile("open"))
    page.keyboard.press("Escape")
    page.locator("[data-del]").first.click()
    expect(page.locator("[data-del]").first).to_have_text("Delete?")
    page.locator("[data-del]").first.click()
    expect(page.locator("#hrows tr.click")).to_have_count(n - 1, timeout=10000)
    with page.expect_download() as dl:
        page.locator("#exp").click()
    assert dl.value.suggested_filename.endswith(".json")
    page.screenshot(path=str(SHOTS / "05_history.png"))
    ok("dashboard charts, history filter/search/drawer/two-step delete/export")

    page.goto(BASE + "/app#/learn")
    expect(page.locator("#view .card").nth(8)).to_be_visible(timeout=10000)
    page.locator("[data-say]").first.click()
    page.locator("[data-try]").first.click()
    expect(page).to_have_url(re.compile(r"#/check"))
    expect(page.locator("#out .vtitle")).to_contain_text("scam", ignore_case=True, timeout=10000)
    page.goto(BASE + "/app#/help")
    expect(page.locator("a[href='tel:1930']")).to_be_visible(timeout=10000)
    page.goto(BASE + "/app#/accuracy")
    expect(page.get_by_text("Confusion matrix")).to_be_visible(timeout=10000)
    page.screenshot(path=str(SHOTS / "06_accuracy.png"))
    page.locator("#lang-seg button[data-l='hi']").click()
    page.goto(BASE + "/app#/learn")
    expect(page.locator("#view h3").first).to_contain_text("डिजिटल", timeout=10000)
    ok("scam guide in Hindi + example hand-off to the checker, helplines, model accuracy page")

    # ---------------- settings: edit profile, theme toggle, language
    page.goto(BASE + "/app#/settings")
    page.fill("#pn", "E2E Tester Two"); page.fill("#ph", "Renamed Home"); page.locator("#pf .btn.primary").click()
    expect(page.locator("#pm")).to_have_text("✓ Saved", timeout=10000)
    expect(page.locator("#who-n")).to_have_text("E2E Tester Two")
    expect(page.locator("#c-home")).to_have_text("Renamed Home")
    page.locator("#theme-seg button[data-t='dark']").click()
    expect(page.locator("html")).to_have_attribute("data-theme", "dark")
    page.locator("#theme-seg button[data-t='light']").click()
    ok("settings: profile saved and shown in header, theme toggle")

    # ---------------- demo accounts + mobile layout
    page.locator("#who").click(); page.locator("#signout").click()
    page.wait_for_url(re.compile(r"/signin"))
    for persona in ("parent", "student", "family"):
        page.locator(f".demos button[data-p='{persona}']").click()
        page.wait_for_url(re.compile(r"/app"), timeout=15000)
        expect(page.locator("#who-r")).to_have_text("Demo account", timeout=10000)
        expect(page.locator(".kpi").first).to_be_visible(timeout=10000)
        page.locator("#who").click(); page.locator("#signout").click()
        page.wait_for_url(re.compile(r"/signin"))
    page.set_viewport_size({"width": 390, "height": 844})
    page.goto(BASE + "/")
    assert page.evaluate("document.documentElement.scrollWidth") <= 392
    page.locator("#burger").click()
    expect(page.locator("#mmenu")).to_have_class(re.compile("open"))
    page.screenshot(path=str(SHOTS / "07_mobile.png"))
    page.goto(BASE + "/signin")
    page.locator(".demos button[data-p='parent']").click()
    page.wait_for_url(re.compile(r"/app"), timeout=15000)
    page.locator("#menu-btn").click()
    expect(page.locator("#side")).to_have_class(re.compile("open"))
    assert page.evaluate("document.documentElement.scrollWidth") <= 392
    ok("three demo personas sign in with seeded data; phone layout has no sideways scroll, menus open")
    browser.close()

print(f"\n{len(steps)} steps passed")
if errors:
    print("ERRORS:")
    for e in errors:
        print(" ", e)
    sys.exit(1)
print("No console or page errors.")
