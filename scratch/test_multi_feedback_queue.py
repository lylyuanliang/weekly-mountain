import sys
import os
import time
import json
import shutil
from playwright.sync_api import sync_playwright

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

def main():
    print("[*] 正在启动 Playwright (msedge) 验证多反馈排队队列与聚合展示...")
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=True)
        context = browser.new_context(
            viewport={"width": 400, "height": 795},
            device_scale_factor=3,
            is_mobile=True,
            has_touch=True,
            user_agent="Mozilla/5.0 (Linux; Android 16; 24129PN74C Build/BP2A.250605.031.A3; wv) AppleWebKit/537.36 Mobile Safari/537.36"
        )
        page = context.new_page()

        console_errors = []
        page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
        page.on("pageerror", lambda err: console_errors.append(str(err)))

        page.goto("http://localhost:5173/?debug=1", wait_until="networkidle")
        time.sleep(1)

        # 1. Open feedback modal
        trigger_btn = page.locator("button[aria-label='真机调试反馈给 AI']")
        assert trigger_btn.is_visible(), "Floating feedback trigger button must be visible"
        trigger_btn.click()
        time.sleep(0.5)

        tab_create = page.locator("button[data-tab='create']")
        tab_history = page.locator("button[data-tab='history']")

        # 2. Check tab create
        tab_create.click()
        time.sleep(0.3)

        # 3. Submit 1st test feedback
        textarea = page.locator("#mobile-feedback-text")
        test_content_1 = "多反馈自测A：第一个排队任务"
        textarea.fill(test_content_1)
        send_btn = page.locator("button:has-text('发送给 AI')")
        send_btn.click()
        print("[✓] 已发送第 1 条测试反馈...")
        time.sleep(1.8)

        # 4. Switch back to create tab and submit 2nd test feedback
        tab_create.click()
        time.sleep(0.5)

        # Verify active banner is shown!
        active_banner = page.locator("text='当前有'")
        assert active_banner.is_visible(), "Active feedback banner should be shown in create tab"
        print("[✓] 提新反馈页面成功展示『当前已有反馈在排队中』友好提示横幅！")

        test_content_2 = "多反馈自测B：第二个连发任务"
        textarea.fill(test_content_2)
        send_btn.click()
        print("[✓] 已发送第 2 条测试反馈...")
        time.sleep(1.8)

        # 5. In history tab, verify both items and queue positions
        tab_history.click()
        time.sleep(0.5)

        item_a = page.locator(f"text='{test_content_1}'")
        item_b = page.locator(f"text='{test_content_2}'")
        assert item_a.is_visible(), "First feedback must be visible in history"
        assert item_b.is_visible(), "Second feedback must be visible in history"
        print("[✓] 历次并发连发反馈均完整在列表中展示！")

        # 6. Close modal and check floating trigger pill text
        close_btn = page.locator("button[aria-label='关闭反馈窗口']")
        close_btn.click()
        time.sleep(0.5)

        pill_text = trigger_btn.inner_text()
        print(f"[✓] 悬浮球动态感知文字: '{pill_text.strip()}'")
        assert "处理中" in pill_text, "Pill should show processing status"

        # 7. Take screenshot of the history list with multiple items
        trigger_btn.click()
        time.sleep(0.5)
        tab_history.click()
        time.sleep(0.5)

        screenshot_path = "d:/file_save/workspace/github/weekly-mountain/scratch/multi_feedback_queue_verified.png"
        page.screenshot(path=screenshot_path)
        print(f"[✓] 已截取多反馈排队队列验证图: {screenshot_path}")

        artifact_dir = "C:/Users/lylyu/.gemini/antigravity/brain/94773e75-cfd8-4fb7-87e3-d08b195b9520"
        if os.path.exists(artifact_dir):
            shutil.copy(screenshot_path, os.path.join(artifact_dir, "multi_feedback_queue_verified.png"))

        # Clean up test items
        from update_status_helper import cleanup_test_item
        cleanup_test_item("多反馈自测")

        assert len(console_errors) == 0, f"Expected 0 console errors, got {console_errors}"
        print("[✓] 控制台 0 运行时错误！多反馈并发排队自测 100% PASS！")

        browser.close()

if __name__ == "__main__":
    main()
