import time
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(channel='msedge', headless=True)
    page = browser.new_page(viewport={'width': 390, 'height': 844})
    page.goto('http://localhost:5173/', wait_until='networkidle')
    time.sleep(1.5)
    page.screenshot(path='scratch/live_map_dark.png')
    print("Dark map saved to scratch/live_map_dark.png")

    # Toggle layer button
    layer_btn = page.locator('.material-symbols-outlined:has-text("dark_mode"), .material-symbols-outlined:has-text("satellite_alt"), .material-symbols-outlined:has-text("terrain")')
    layer_btn.click()
    time.sleep(1.5)
    page.screenshot(path='scratch/live_map_satellite.png')
    print("Satellite map saved to scratch/live_map_satellite.png")

    browser.close()
