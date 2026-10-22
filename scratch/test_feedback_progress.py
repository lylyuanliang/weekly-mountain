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
    print("[*] 正在启动 Playwright (msedge) 验证手机端反馈进度与追踪列表...")
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=True)
        # Xiaomi 15 mobile viewport
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

        # 1. Check floating button
        trigger_btn = page.locator("button[aria-label='真机调试反馈给 AI']")
        assert trigger_btn.is_visible(), "Floating feedback trigger button must be visible"
        print("[✓] 悬浮反馈触发按钮已渲染并可见")

        # 2. Click trigger button to open modal
        trigger_btn.click()
        time.sleep(0.5)

        # Check modal header and tabs
        tab_create = page.locator("button[data-tab='create']")
        tab_history = page.locator("button[data-tab='history']")
        assert tab_create.is_visible(), "Tab '提新反馈' must be visible"
        assert tab_history.is_visible(), "Tab '进度与历史' must be visible"
        print("[✓] 反馈弹窗顶部双 Tab 切换器渲染正常")

        # 3. Switch to '进度与历史' tab
        tab_history.click()
        time.sleep(0.6)

        history_list = page.locator("[data-testid='feedback-history-list']")
        assert history_list.is_visible(), "Feedback history list must be visible"
        print("[✓] 反馈历史与进度追踪列表已成功展示")

        # Check badges
        completed_badges = page.locator("text='已修复并验证'")
        badge_count = completed_badges.count()
        assert badge_count > 0, f"Expected completed badges, got {badge_count}"
        print(f"[✓] 成功检测到 {badge_count} 条『已修复并验证』历史反馈卡片")

        # Check AI reply box
        reply_boxes = page.locator("text='AI 进度与处理答复：'")
        assert reply_boxes.count() > 0, "AI reply callout box must exist"
        print("[✓] AI 答复与进度说明卡片完整展示")

        # 4. Check historical screenshot thumbnail and lightbox
        img_thumb = page.locator("img[alt='反馈截图缩略图']").first
        if img_thumb.is_visible():
            print("[✓] 检测到历史截图缩略图，点击测试放大灯箱...")
            thumb_container = page.locator("text='查看提交时截图凭证'").first
            thumb_container.click()
            time.sleep(0.4)

            lightbox = page.locator(".fixed.inset-0.z-\\[1010\\]")
            assert lightbox.is_visible(), "Lightbox modal must be visible"
            print("[✓] 全屏灯箱预览正常弹出")

            # Close lightbox
            close_lightbox_btn = lightbox.locator("button")
            close_lightbox_btn.click()
            time.sleep(0.3)
            print("[✓] 灯箱关闭正常")

        # 5. Capture screenshot of the history tab
        screenshot_path = "d:/file_save/workspace/github/weekly-mountain/scratch/feedback_progress_verified.png"
        page.screenshot(path=screenshot_path)
        print(f"[✓] 已截取进度追踪验证图: {screenshot_path}")

        # Sync to artifacts dir
        artifact_dir = "C:/Users/lylyu/.gemini/antigravity/brain/94773e75-cfd8-4fb7-87e3-d08b195b9520"
        if os.path.exists(artifact_dir):
            shutil.copy(screenshot_path, os.path.join(artifact_dir, "feedback_progress_verified.png"))

        # 6. Switch back to '提新反馈' tab and test submitting a new feedback with auto-switch
        tab_create.click()
        time.sleep(0.4)

        textarea = page.locator("#mobile-feedback-text")
        test_content = "自动化自测：提交新反馈并验证进度自动切换与排队状态"
        textarea.fill(test_content)

        send_btn = page.locator("button:has-text('发送给 AI')")
        send_btn.click()
        print("[✓] 已点击发送反馈，等待自动切至进度追踪...")

        # Wait for auto-switch to history tab (timeout 3s)
        time.sleep(2)
        assert history_list.is_visible(), "Should automatically switch to history tab after submit"

        # Check that top item is pending or processing (watcher updates in real-time)
        pending_badge = page.locator("text='排队待处理'").first
        is_pending = pending_badge.is_visible()
        processing_badge = page.locator("text='AI 正在排查修复'").first
        is_processing = processing_badge.is_visible()
        assert is_pending or is_processing, "Newly submitted feedback should have '排队待处理' or 'AI 正在排查修复' badge"
        status_label = '排队待处理' if is_pending else 'AI 正在排查修复'
        print(f"[✓] 新提交反馈成功置顶并展示状态: 『{status_label}』！")

        # Capture submitted state screenshot
        submitted_shot = "d:/file_save/workspace/github/weekly-mountain/scratch/feedback_submitted_pending.png"
        page.screenshot(path=submitted_shot)
        if os.path.exists(artifact_dir):
            shutil.copy(submitted_shot, os.path.join(artifact_dir, "feedback_submitted_pending.png"))

        # Clean up the test submission from mobile_feedback.json so we don't pollute user's list
        from update_status_helper import cleanup_test_item
        cleanup_test_item(test_content)

        assert len(console_errors) == 0, f"Expected 0 console errors, got {console_errors}"
        print("[✓] 控制台 0 运行时错误！所有自测 100% PASS！")

        browser.close()

if __name__ == "__main__":
    main()
