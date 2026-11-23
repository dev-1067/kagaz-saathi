"""Captures 4K screenshots of the running app (http://localhost:8030) for the demo video.  python video/capture.py"""
import re
import sys
from pathlib import Path

from playwright.sync_api import expect, sync_playwright

BASE = (sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8030").rstrip("/")
OUT = Path(__file__).parent / "shots"
OUT.mkdir(exist_ok=True)
HIDE = ("document.addEventListener('DOMContentLoaded', () => { const s = document.createElement('style');"
        " s.textContent = '.fx-cursor,.fx-dot{display:none!important} .toast{display:none!important}'; document.head.appendChild(s); });")

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_context(viewport={"width": 1600, "height": 900}, device_scale_factor=2.4).new_page()
    pg.add_init_script(HIDE)
    pg.goto(BASE + "/")
    pg.wait_for_timeout(3800)
    pg.screenshot(path=str(OUT / "v01_landing.png"))
    pg.locator("#samples .chip").first.scroll_into_view_if_needed()
    pg.evaluate("document.querySelector('#try').scrollIntoView()")
    pg.wait_for_timeout(600)
    pg.locator("#samples .chip").nth(1).click()
    expect(pg.locator("#t-out .vtitle")).to_be_visible(timeout=10000)
    pg.wait_for_timeout(1500)
    pg.screenshot(path=str(OUT / "v02_landing_try.png"))

    pg.goto(BASE + "/signin")
    pg.wait_for_timeout(1200)
    pg.screenshot(path=str(OUT / "v03_signin.png"))
    pg.locator(".demos button[data-p='parent']").click()
    pg.wait_for_url(re.compile(r"/app"), timeout=20000)
    expect(pg.locator(".kpi").first).to_be_visible(timeout=10000)
    pg.wait_for_timeout(2600)
    pg.screenshot(path=str(OUT / "v04_dashboard.png"))

    pg.goto(BASE + "/app#/check")
    expect(pg.locator("#smp .chip").first).to_be_visible(timeout=10000)
    pg.locator("#c-lang button[data-l='en']").click()       # the demo parent defaults to Hindi; the scam scene is narrated in English
    pg.locator("#smp .chip").nth(1).click()
    expect(pg.locator("#out .vtitle")).to_be_visible(timeout=10000)
    pg.wait_for_timeout(1800)
    pg.screenshot(path=str(OUT / "v05_check_scam.png"))
    pg.locator("#c-lang button[data-l='hi']").click()
    pg.wait_for_timeout(1800)
    pg.screenshot(path=str(OUT / "v06_check_hindi.png"))
    pg.locator("#c-lang button[data-l='en']").click()
    pg.locator("#smp .chip").nth(2).click()
    pg.wait_for_timeout(1800)
    pg.screenshot(path=str(OUT / "v07_check_genuine.png"))
    pg.locator("#smp .chip").nth(0).click()
    expect(pg.locator("#alert")).to_be_visible(timeout=10000)
    pg.wait_for_timeout(900)
    pg.locator("#alert").click()
    pg.wait_for_timeout(1200)
    pg.goto(BASE + "/app#/family")
    expect(pg.locator(".hlc", has_text="To ")).to_be_visible(timeout=10000)
    pg.wait_for_timeout(1200)
    pg.screenshot(path=str(OUT / "v08_family.png"))
    pg.goto(BASE + "/app#/history")
    expect(pg.locator("#hrows tr.click").first).to_be_visible(timeout=10000)
    pg.wait_for_timeout(900)
    pg.screenshot(path=str(OUT / "v09_history.png"))
    pg.goto(BASE + "/app#/accuracy")
    expect(pg.get_by_text("Confusion matrix")).to_be_visible(timeout=10000)
    pg.wait_for_timeout(1500)
    pg.screenshot(path=str(OUT / "v10_accuracy.png"))
    pg.evaluate("document.querySelector('#view').scrollTo?.(0,0); window.scrollTo(0, 900)")
    pg.wait_for_timeout(800)
    pg.screenshot(path=str(OUT / "v11_accuracy2.png"))
    b.close()
print(sorted(x.name for x in OUT.glob("*.png")))
