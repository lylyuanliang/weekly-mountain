import sys
import os
import time
from playwright.sync_api import sync_playwright

def inspect_bottom_sheet_height():
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=True)
        context = browser.new_context(
            viewport={"width": 400, "height": 795},
            has_touch=True,
            user_agent="Mozilla/5.0 (Linux; Android 16; 24129PN74C Build/BP2A.250605.031.A3; wv) AppleWebKit/537.36"
        )
        page = context.new_page()
        page.goto("http://localhost:5173/", wait_until="domcontentloaded")
        time.sleep(2)

        # Measure drawer container and card
        metrics = page.evaluate("""() => {
          const sheet = document.querySelector('.bottom-sheet');
          const drawer = document.querySelector('.bottom-sheet > div');
          const card = document.querySelector('.hero-mountain-card');
          const carousel = card ? card.parentElement : null;

          return {
            sheetHeight: sheet?.offsetHeight,
            drawerClientHeight: drawer?.clientHeight,
            drawerScrollHeight: drawer?.scrollHeight,
            cardHeight: card?.offsetHeight,
            carouselHeight: carousel?.offsetHeight,
            cardBottom: card ? card.getBoundingClientRect().bottom : 0,
            drawerBottom: drawer ? drawer.getBoundingClientRect().bottom : 0,
            gap: drawer && card ? (drawer.getBoundingClientRect().bottom - card.getBoundingClientRect().bottom) : 0
          };
        }""")

        print("Current Layout Metrics:")
        for k, v in metrics.items():
            print(f"  {k}: {v}")

        browser.close()

if __name__ == "__main__":
    inspect_bottom_sheet_height()
