# -*- coding: utf-8 -*-
"""
Playwright 验证脚本：多山峰相册画廊与 Lightbox 全屏预览交互测试
覆盖 Android 移动端视口
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

def verify_galleries():
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
                if not any(x in text.lower() for x in ['favicon', 'map tile', 'fonts.gstatic']):
                    console_errors.append(text)
        page.on('console', on_console)

        print("[1/5] Navigating to http://localhost:5173/#/explore ...")
        page.goto("http://localhost:5173/#/explore", wait_until="networkidle", timeout=20000)
        page.wait_for_timeout(1800)

        # Test 1: Click first mountain (Longquanshan) card "路线详情"
        print("[2/5] Testing Longquanshan gallery...")
        hero_card = page.locator(".hero-mountain-card").first
        hero_card.wait_for(state="visible", timeout=6000)

        detail_btn = hero_card.locator("button:has-text('路线详情')").first
        assert detail_btn.is_visible(), "Assertion Failed: Card '路线详情' button not found!"
        detail_btn.click()
        page.wait_for_timeout(1000)

        sheet = page.locator(".mountain-detail-sheet")
        sheet.wait_for(state="visible", timeout=5000)

        # Check gallery carousel banner
        gallery_banner = page.locator(".hero-gallery-banner")
        gallery_banner.wait_for(state="visible", timeout=3000)

        # Check chip text: should be "1/3"
        photo_chip = gallery_banner.locator("button:has-text('1/3')").first
        assert photo_chip.is_visible(), "Assertion Failed: Photo count chip 1/3 not visible!"
        print("  [PASS] Longquanshan shows '1/3' photo chip")

        # Click next image button
        next_btn = gallery_banner.locator("button[aria-label='查看下一张图片']")
        assert next_btn.is_visible(), "Assertion Failed: Next button not visible!"
        next_btn.click()
        page.wait_for_timeout(600)

        # Now chip should show 2/3
        chip_2 = gallery_banner.locator("button:has-text('2/3')").first
        assert chip_2.is_visible(), "Assertion Failed: After next click, chip is not 2/3!"
        print("  [PASS] After clicking next, chip shows '2/3'")

        # Click the photo count button to open Lightbox Modal
        print("[3/5] Testing Lightbox Modal...")
        chip_2.click()
        page.wait_for_timeout(600)

        # Check lightbox modal (.lightbox-overlay)
        lightbox_overlay = page.locator(".lightbox-overlay")
        lightbox_overlay.wait_for(state="visible", timeout=3000)

        # Check lightbox index indicator
        lb_indicator = lightbox_overlay.locator("span:has-text('/ 3')").first
        assert lb_indicator.is_visible(), "Assertion Failed: Lightbox indicator not visible!"
        print(f"  [PASS] Lightbox open: {lb_indicator.inner_text()}")

        # Press Escape to close Lightbox
        page.keyboard.press("Escape")
        page.wait_for_timeout(600)
        assert not lightbox_overlay.is_visible(), "Assertion Failed: Lightbox did not close on Escape!"
        print("  [PASS] Lightbox closed cleanly on Escape")

        # Close Longquanshan detail sheet via .btn-close-detail
        close_btn = page.locator(".btn-close-detail")
        assert close_btn.is_visible(), "Assertion Failed: .btn-close-detail not visible!"
        close_btn.click()
        page.wait_for_timeout(800)

        # Test 2: Select Dawagengzha (second card) and inspect its gallery
        print("[4/5] Testing Dawagengzha gallery...")
        dawa_card = page.locator(".hero-mountain-card").nth(1)
        dawa_card.wait_for(state="visible", timeout=4000)

        dawa_detail_btn = dawa_card.locator("button:has-text('路线详情')").first
        dawa_detail_btn.wait_for(state="visible", timeout=3000)
        dawa_detail_btn.click()
        page.wait_for_timeout(1000)

        dawa_sheet = page.locator(".mountain-detail-sheet")
        dawa_sheet.wait_for(state="visible", timeout=5000)

        dawa_chip = dawa_sheet.locator(".hero-gallery-banner button:has-text('1/3')").first
        assert dawa_chip.is_visible(), "Assertion Failed: Dawagengzha does not show 1/3 gallery chip!"
        print("  [PASS] Dawagengzha has 3 gallery photos verified!")

        # Check Dawagengzha photo 1 title/desc in banner
        banner_title = dawa_sheet.locator(".hero-gallery-banner .text-caption").first.inner_text()
        print(f"  [PASS] Dawagengzha banner caption: {banner_title}")

        # Take screenshot
        os.makedirs("scratch", exist_ok=True)
        screenshot_path = "scratch/verify_multi_mountain_gallery.png"
        page.screenshot(path=screenshot_path)
        print(f"[5/5] Saved verification screenshot to {screenshot_path}")

        # Also copy screenshot to artifact dir
        art_dir = r"C:\Users\lylyu\.gemini\antigravity\brain\94773e75-cfd8-4fb7-87e3-d08b195b9520"
        import shutil
        shutil.copyfile(screenshot_path, os.path.join(art_dir, "verify_multi_mountain_gallery.png"))

        # Assert console errors
        print(f"Console errors count: {len(console_errors)}")
        if console_errors:
            print("Errors:", console_errors)
        assert len(console_errors) == 0, f"Found console errors: {console_errors}"

        browser.close()
        print("\n==========================================")
        print(" 🎉 MULTI-MOUNTAIN GALLERY VERIFIED 100%! 🎉")
        print("==========================================")

if __name__ == '__main__':
    verify_galleries()
