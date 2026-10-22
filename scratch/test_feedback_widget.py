import sys
import os
import time
import json
from playwright.sync_api import sync_playwright

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

def test_feedback():
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=True)
        # Xiaomi 15 viewport emulation
        context = browser.new_context(
            viewport={"width": 400, "height": 820},
            device_scale_factor=3.0,
            user_agent="Mozilla/5.0 (Linux; Android 15; 24129PN74C Build/AQ3A.240822.001) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36"
        )
        page = context.new_page()

        print("[1/4] Navigating to http://localhost:5173/ ...")
        page.goto("http://localhost:5173/", wait_until="networkidle")
        time.sleep(2)

        print("[2/4] Verifying floating feedback pill...")
        pill = page.locator("button:has-text('反馈给 AI')")
        assert pill.is_visible(), "Floating feedback trigger pill should be visible"
        pill.click()
        time.sleep(1)

        print("[3/4] Verifying feedback modal & device capture...")
        modal = page.locator("[role='dialog'][aria-label='真机调试即时反馈']")
        assert modal.is_visible(), "Feedback modal should appear"

        # Check captured viewport text
        modal_text = modal.inner_text()
        print("Captured modal text preview:")
        print(modal_text[:200])
        assert "400 × 820" in modal_text, "Should capture 400 × 820 viewport"

        # Click a quick tag
        tag_btn = modal.locator("button:has-text('真机操作流畅')")
        tag_btn.click()

        # Fill text
        textarea = modal.locator("#mobile-feedback-text")
        textarea.fill("真机调试联调测试：手机端反馈直达通道已连通，流畅顺手！")

        page.screenshot(path="scratch/feedback_modal_open.png")
        print("Saved screenshot: scratch/feedback_modal_open.png")

        # Submit
        print("[4/4] Submitting feedback...")
        submit_btn = modal.locator("button:has-text('发送给 AI 助手')")
        submit_btn.click()

        # Check success notice immediately
        success_notice = page.locator("text=已送达")
        success_notice.wait_for(state="visible", timeout=5000)
        assert success_notice.is_visible(), "Success message should be displayed"

        page.screenshot(path="scratch/feedback_modal_success.png")
        print("Saved screenshot: scratch/feedback_modal_success.png")

        browser.close()

        # Verify scratch/latest_feedback.json
        feedback_file = os.path.join(r"d:\file_save\workspace\github\weekly-mountain", "scratch", "latest_feedback.json")
        assert os.path.exists(feedback_file), "scratch/latest_feedback.json should exist"
        with open(feedback_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        print("Successfully read latest_feedback.json:")
        print("  ReceivedAt:", data.get("receivedAt"))
        print("  Content:", data.get("content"))
        print("  Device:", data.get("device"))

        print("\nALL FEEDBACK WIDGET VERIFICATIONS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test_feedback()
