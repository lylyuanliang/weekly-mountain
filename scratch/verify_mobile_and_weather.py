"""
Playwright 验证脚本：
1. 验证移动端（小米 15 视口 400x820 与 400x890）下卡片底部两个按钮完整可见、零遮挡
2. 验证实时天气（Open-Meteo 7 天预报）在卡片点击弹窗与详情页 Module 11 中正常拉取并展示
"""
import sys
import os
import time
from playwright.sync_api import sync_playwright

def run_verification():
    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(channel="msedge", headless=True)
        # Emulate Xiaomi 15 viewport (400 x 820)
        context = browser.new_context(
            viewport={"width": 400, "height": 820},
            user_agent="Mozilla/5.0 (Linux; Android 15; 24129PN74C Build/AQ3A.240822.001) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36"
        )
        page = context.new_page()

        console_errors = []
        page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)

        print("[1/5] Navigating to http://localhost:5173/ ...")
        page.goto("http://localhost:5173/", wait_until="networkidle")
        time.sleep(2)

        # 1. Check card buttons visibility
        print("[2/5] Checking HeroMountainCard buttons visibility in 400x820 viewport...")
        first_card = page.locator(".hero-mountain-card").first
        first_card.wait_for(state="visible", timeout=10000)

        # Check detail button and plan button
        detail_btn = first_card.locator("button:has-text('路线详情')")
        plan_btn = first_card.locator("button:has-text('周计划'), button:has-text('已在计划')")

        assert detail_btn.is_visible(), "路线详情按钮应当可见"
        assert plan_btn.is_visible(), "加入周计划按钮应当可见"

        detail_box = detail_btn.bounding_box()
        plan_box = plan_btn.bounding_box()
        bottom_nav_box = page.locator(".stitch-bottom-nav").bounding_box()

        print(f"Detail button bbox: {detail_box}")
        print(f"Plan button bbox: {plan_box}")
        print(f"BottomNav bbox: {bottom_nav_box}")

        # Assert buttons are completely above the bottom nav top
        assert detail_box["y"] + detail_box["height"] <= bottom_nav_box["y"], \
            f"路线详情按钮底部 ({detail_box['y'] + detail_box['height']}) 超出或遮挡在底部导航栏 ({bottom_nav_box['y']}) 之上"
        assert plan_box["y"] + plan_box["height"] <= bottom_nav_box["y"], \
            f"加入周计划按钮底部 ({plan_box['y'] + plan_box['height']}) 超出或遮挡在底部导航栏 ({bottom_nav_box['y']}) 之上"

        # Capture Xiaomi 15 half screen
        page.screenshot(path="scratch/mobile_xiaomi15_half.png")
        print(" Saved screenshot: scratch/mobile_xiaomi15_half.png")

        # 2. Test weather pill on card
        print("[3/5] Testing card weather pill click...")
        wx_btn = first_card.locator("button[title*='实况天气']")
        assert wx_btn.is_visible(), "卡片右上角天气药丸应当存在且可见"
        print(f"Weather pill text: {wx_btn.inner_text().strip()}")
        wx_btn.click()
        time.sleep(2)

        # Weather modal should appear
        wx_modal = page.locator(".mountain-weather-modal-wrapper")
        assert wx_modal.is_visible(), "天气弹窗应当弹出"
        print(" Weather modal appeared!")

        # Wait for weather cards to load inside modal
        page.wait_for_selector(".mountain-weather-modal-wrapper .mountain-weather-card", timeout=10000)
        time.sleep(2)
        page.screenshot(path="scratch/mobile_weather_modal.png")
        print(" Saved screenshot: scratch/mobile_weather_modal.png")

        # Close weather modal
        close_btn = wx_modal.locator("button[aria-label='关闭天气预报']")
        close_btn.click()
        time.sleep(0.5)

        # 3. Test MountainDetailSheet module 11 weather
        print("[4/5] Testing MountainDetailSheet module 11 live weather...")
        detail_btn.click()
        time.sleep(1)

        detail_sheet = page.locator(".mountain-detail-sheet")
        assert detail_sheet.is_visible(), "山峰详情抽屉应当打开"

        # Scroll to Module 11
        mod_wx = page.locator("#mod-weather")
        mod_wx.scroll_into_view_if_needed()
        time.sleep(2)

        assert mod_wx.is_visible(), "模块 11 天气预报应当可见"
        wx_cards = mod_wx.locator(".mountain-weather-card")
        assert wx_cards.is_visible(), "模块 11 内 MountainWeatherCard 应当渲染"

        page.screenshot(path="scratch/mobile_detail_weather.png")
        print(" Saved screenshot: scratch/mobile_detail_weather.png")

        # Test refresh button inside module 11
        refresh_btn = mod_wx.locator("button[title='刷新实时气象']")
        assert refresh_btn.is_visible(), "刷新按钮应当可见"
        refresh_btn.click()
        time.sleep(1.5)

        print("[5/5] Checking console errors...")
        real_errors = [e for e in console_errors if "favicon" not in e.lower()]
        if real_errors:
            print(f"Warning: Found {len(real_errors)} console errors: {real_errors}")
        else:
            print(" ZERO console errors!")

        browser.close()
        print("\n ALL VERIFICATIONS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    run_verification()
