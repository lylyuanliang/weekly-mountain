import sys
import os
import time
from playwright.sync_api import sync_playwright

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

def test_feedback_over_detail():
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=True)
        # Xiaomi 15 WeChat viewport
        context = browser.new_context(
            viewport={"width": 400, "height": 820},
            has_touch=True,
            user_agent="Mozilla/5.0 (Linux; Android 16; 24129PN74C Build/BP2A.250605.031.A3; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/150.0.7871.189 Mobile Safari/537.36 MicroMessenger/8.0.79"
        )
        page = context.new_page()

        print("[1/3] Navigating to http://localhost:5173/ ...")
        page.goto("http://localhost:5173/", wait_until="domcontentloaded")
        time.sleep(2)

        # 1. Open mountain detail
        print("[2/3] Opening MountainDetailSheet...")
        detail_btn = page.locator(".hero-mountain-card button:has-text('路线详情')").first
        detail_btn.click()
        time.sleep(1.5)

        detail_sheet = page.locator(".mountain-detail-sheet")
        assert detail_sheet.is_visible(), "MountainDetailSheet should be open"
        print("MountainDetailSheet is open.")

        # 2. Check if feedback button is visible on top of detail sheet
        feedback_btn = page.locator("button:has-text('反馈给 AI')")
        assert feedback_btn.is_visible(), "Feedback button should be visible on top of detail sheet"
        print("PASS: Feedback button is visible on top of MountainDetailSheet!")

        page.screenshot(path="scratch/feedback_btn_over_detail.png")

        # 3. Click feedback button while detail sheet is open
        print("[3/3] Clicking feedback button while MountainDetailSheet is open...")
        feedback_btn.click()
        time.sleep(1)

        modal = page.locator("[role='dialog'][aria-label='真机调试即时反馈']")
        assert modal.is_visible(), "Feedback modal should appear over detail sheet"
        print("PASS: Feedback modal opened cleanly on top of MountainDetailSheet!")

        page.screenshot(path="scratch/feedback_modal_over_detail.png")

        browser.close()
        print("\nALL VERIFICATIONS PASSED: Feedback button is now permanently on top!")

if __name__ == "__main__":
    test_feedback_over_detail()
