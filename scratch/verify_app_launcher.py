# -*- coding: utf-8 -*-
"""
Playwright 验证脚本：
1. 两步路 / 六只脚 户外轨迹 App 自动唤起与搜索词深度联动
2. 手机原生地图导航选择器 (高德/百度/腾讯/Apple/网页版)
3. 移动端触控交互、Toast 反馈与控制台 0 错误
"""

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

def verify_app_launcher():
    console_errors = []

    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=True)
        # Mobile viewport: Android 400x795
        context = browser.new_context(
            viewport={'width': 400, 'height': 795},
            user_agent='Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36'
        )
        page = context.new_page()

        def on_console(msg):
            if msg.type in ['error']:
                text = msg.text
                if not any(x in text.lower() for x in ['favicon', 'map tile', 'fonts.gstatic', 'registered handler']):
                    console_errors.append(text)
        page.on('console', on_console)

        print("[1/5] Navigating to http://localhost:5173/#/explore ...")
        page.goto("http://localhost:5173/#/explore", wait_until="networkidle", timeout=20000)
        page.wait_for_timeout(1800)

        # Open Longquanshan detail sheet
        print("[2/5] Opening Longquanshan detail sheet...")
        hero_card = page.locator(".hero-mountain-card").first
        hero_card.wait_for(state="visible", timeout=6000)

        detail_btn = hero_card.locator("button:has-text('路线详情')").first
        detail_btn.click()
        page.wait_for_timeout(1000)

        sheet = page.locator(".mountain-detail-sheet")
        sheet.wait_for(state="visible", timeout=5000)

        # Test 1: Module 2 (GPX & 2bulu launch)
        print("[3/5] Testing TwoBulu & FootTouch launch features...")
        btn_twobulu = page.locator(".btn-launch-twobulu")
        btn_foottouch = page.locator(".btn-launch-foottouch")
        assert btn_twobulu.is_visible(), "Assertion Failed: .btn-launch-twobulu not visible!"
        assert btn_foottouch.is_visible(), "Assertion Failed: .btn-launch-foottouch not visible!"
        print("  [PASS] Outdoor App launch buttons visible in Module 2")

        # Click a track keyword card
        first_track = page.locator(".track-keyword-card").first
        first_track.scroll_into_view_if_needed()
        assert first_track.is_visible(), "Assertion Failed: .track-keyword-card not visible!"

        track_text = first_track.inner_text()
        print(f"  Clicking track keyword card: {track_text[:30]}...")
        first_track.click()
        page.wait_for_timeout(500)

        # Check Toast
        toast = page.locator("text=两步路 App").first
        assert toast.is_visible(), "Assertion Failed: Toast for TwoBulu launch not visible!"
        print(f"  [PASS] TwoBulu Toast verified: {toast.inner_text()}")
        page.wait_for_timeout(1000)

        # Test 2: Navigation App Picker from Module 5 & Bottom Bar
        print("[4/5] Testing Navigation App Picker...")
        # Bottom bar navigation button
        bottom_nav_btn = page.locator(".btn-bottom-nav")
        assert bottom_nav_btn.is_visible(), "Assertion Failed: .btn-bottom-nav not visible in footer!"
        bottom_nav_btn.click()
        page.wait_for_timeout(600)

        picker_panel = page.locator(".nav-picker-panel")
        picker_panel.wait_for(state="visible", timeout=3000)
        print("  [PASS] Navigation Picker ActionSheet opened from bottom bar")

        # Verify Navigation App Items
        app_items = page.locator(".nav-app-item")
        assert app_items.count() >= 4, f"Assertion Failed: Expected >= 4 nav apps, got {app_items.count()}"

        has_amap = page.locator(".nav-app-item:has-text('高德地图')").is_visible()
        has_baidu = page.locator(".nav-app-item:has-text('百度地图')").is_visible()
        has_tencent = page.locator(".nav-app-item:has-text('腾讯地图')").is_visible()
        has_web = page.locator(".nav-app-item:has-text('网页版高德直接导航')").is_visible()

        assert has_amap and has_baidu and has_tencent and has_web, "Assertion Failed: Missing required map apps!"
        print("  [PASS] All navigation apps verified (高德, 百度, 腾讯, 网页版)")

        # Click Amap item
        amap_item = page.locator(".nav-app-item:has-text('高德地图')").first
        amap_item.click()
        page.wait_for_timeout(600)

        # Verify navigation launch toast
        nav_toast = page.locator("text=正在为你打开 高德地图").first
        assert nav_toast.is_visible(), "Assertion Failed: Nav toast not visible!"
        print(f"  [PASS] Navigation launch toast verified: {nav_toast.inner_text()}")

        # Wait for toast to fade
        page.wait_for_timeout(1000)

        # Scroll to Module 5 and test the in-card "打开手机地图 App 导航" button
        print("[5/5] Testing in-card navigation button in Module 5...")
        btn_open_nav = page.locator(".btn-open-nav-app")
        btn_open_nav.scroll_into_view_if_needed()
        assert btn_open_nav.is_visible(), "Assertion Failed: .btn-open-nav-app in Module 5 not visible!"
        btn_open_nav.click()
        page.wait_for_timeout(500)

        assert picker_panel.is_visible(), "Assertion Failed: Picker did not open from Module 5 button!"
        print("  [PASS] Module 5 in-card navigation button verified!")

        # Close picker
        close_picker_btn = page.locator(".nav-picker-panel button:has-text('close')")
        close_picker_btn.click()
        page.wait_for_timeout(400)
        assert not picker_panel.is_visible(), "Assertion Failed: Picker did not close!"
        print("  [PASS] Navigation Picker closed cleanly")

        # Take verification screenshot
        os.makedirs("scratch", exist_ok=True)
        screenshot_path = "scratch/verify_app_launcher.png"
        page.screenshot(path=screenshot_path)
        print(f"  [SCREENSHOT] Saved verification screenshot to {screenshot_path}")

        # Copy to artifact directory
        art_dir = r"C:\Users\lylyu\.gemini\antigravity\brain\94773e75-cfd8-4fb7-87e3-d08b195b9520"
        import shutil
        shutil.copyfile(screenshot_path, os.path.join(art_dir, "verify_app_launcher.png"))

        # Check console errors
        print(f"Console errors count: {len(console_errors)}")
        if console_errors:
            print("Errors:", console_errors)
        assert len(console_errors) == 0, f"Found console errors: {console_errors}"

        browser.close()
        print("\n=======================================================")
        print(" 🎉 APP LAUNCHER (NAVIGATION & 2BULU) VERIFIED 100%! 🎉")
        print("=======================================================")

if __name__ == '__main__':
    verify_app_launcher()
