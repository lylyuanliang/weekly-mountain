import time
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(channel="msedge", headless=True)
    page = browser.new_page(viewport={"width": 400, "height": 757})
    page.goto("http://localhost:5173/?debug=1", wait_until="domcontentloaded")
    time.sleep(2)

    # Check button
    btn = page.locator("button[title='缩小地图']")
    print("Button count:", btn.count())
    print("Button is visible:", btn.is_visible())

    # Check initial zoom HUD
    hud = page.locator("span.font-label-data-sm.text-outline").first
    print("Initial HUD:", hud.inner_text())

    # Dispatch click via JS evaluate
    page.evaluate("() => document.querySelector(\"button[title='缩小地图']\").click()")
    time.sleep(0.5)
    print("HUD after JS click:", hud.inner_text())

    # Dispatch click via Playwright click
    btn.click(force=True)
    time.sleep(0.5)
    print("HUD after Playwright click:", hud.inner_text())

    browser.close()
