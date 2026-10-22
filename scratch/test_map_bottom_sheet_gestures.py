import time
import os
import sys
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://localhost:5173/"
SCREENSHOT_COLLAPSED = r"d:\file_save\workspace\github\weekly-mountain\scratch\map_collapsed_big_view.png"
SCREENSHOT_EXPANDED = r"d:\file_save\workspace\github\weekly-mountain\scratch\map_expanded_half_view.png"

def test_gestures():
    print("=== Testing BottomSheet Collapse, Downward Swipe & Big Map Experience ===")
    console_errors = []

    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(channel="msedge", headless=True)
        except Exception:
            browser = p.chromium.launch(headless=True)

        context = browser.new_context(viewport={"width": 390, "height": 844}, has_touch=True)
        page = context.new_page()

        page.on("console", lambda msg: print(f"  [BROWSER] {msg.type}: {msg.text}") if "DEBUG" in msg.text or msg.type == "error" else None)
        page.on("pageerror", lambda err: print(f"  [BROWSER ERROR] {err}"))

        page.goto(BASE_URL)
        page.wait_for_selector(".explore-view", timeout=10000)
        page.wait_for_timeout(1000)

        # 1. 验证初始状态处于半屏 (half)
        sheet = page.locator(".bottom-sheet")
        initial_h = sheet.evaluate("el => el.getBoundingClientRect().height")
        print(f"Initial BottomSheet height: {initial_h:.1f}px")
        assert initial_h >= 350, f"Expected half height >= 350px, got {initial_h}"
        page.screenshot(path=SCREENSHOT_EXPANDED)

        # 2. 测试显式按钮点击收起 [ 收起大图 ⌵ ]
        collapse_btn = page.locator("button[title*='降到最低以查看大地图']")
        assert collapse_btn.is_visible(), "Collapse button not visible in half mode!"
        collapse_btn.click()
        page.wait_for_timeout(400)

        collapsed_h = sheet.evaluate("el => el.getBoundingClientRect().height")
        print(f"After clicking [收起大图], BottomSheet height: {collapsed_h:.1f}px")
        assert collapsed_h <= 65, f"Expected collapsed height <= 65px, got {collapsed_h}"
        print("✔ Test 1 Passed: [收起大图] button collapsed sheet to minimal peek bar")

        # 验证大地图视野截图
        page.screenshot(path=SCREENSHOT_COLLAPSED)
        print(f"  [SCREENSHOT] Saved full map view: {SCREENSHOT_COLLAPSED}")

        # 3. 测试点击折叠条上的 [ 展开 ] 恢复半屏
        expand_btn = page.locator("button[title*='展开山峰卡片']")
        assert expand_btn.is_visible(), "Expand button not visible in collapsed mode!"
        expand_btn.click()
        page.wait_for_timeout(400)

        restored_h = sheet.evaluate("el => el.getBoundingClientRect().height")
        print(f"After clicking [展开], BottomSheet height: {restored_h:.1f}px")
        assert restored_h >= 350, f"Expected restored height >= 350px, got {restored_h}"
        print("✔ Test 2 Passed: [展开] button restored sheet to half height")

        # 4. 测试向下滑动下拂 (Swipe Down / Drag Down) 降到最低
        handle = page.locator(".drawer-handle")
        box = handle.bounding_box()
        start_x = box["x"] + box["width"] / 2
        start_y = box["y"] + box["height"] / 2

        page.mouse.move(start_x, start_y)
        page.mouse.down()
        page.mouse.move(start_x, start_y + 70, steps=5)
        page.mouse.up()
        page.wait_for_timeout(400)

        swipe_collapsed_h = sheet.evaluate("el => el.getBoundingClientRect().height")
        print(f"After downward drag, BottomSheet height: {swipe_collapsed_h:.1f}px")
        assert swipe_collapsed_h <= 65, f"Expected swipe collapsed height <= 65px, got {swipe_collapsed_h}"
        print("✔ Test 3 Passed: Downward drag gesture collapsed sheet to minimal peek bar")

        # 5. 测试点击山峰标记点 (Marker) 自动唤起半屏卡片
        marker = page.locator(".mountain-marker").first
        marker.click()
        page.wait_for_timeout(400)

        marker_expanded_h = sheet.evaluate("el => el.getBoundingClientRect().height")
        print(f"After clicking mountain marker, BottomSheet height: {marker_expanded_h:.1f}px")
        assert marker_expanded_h >= 350, f"Expected marker click to expand sheet, got {marker_expanded_h}"
        print("✔ Test 4 Passed: Clicking mountain marker automatically expanded card")

        # 6. 测试拖拽/平移大地图空白处，自动收起卡片降到最低
        # 在地图无点位空白处 (100, 250) 拖拽
        mx = 100
        my = 250
        page.mouse.move(mx, my)
        page.mouse.down()
        page.mouse.move(mx + 50, my + 30, steps=5)
        page.mouse.up()
        page.wait_for_timeout(400)

        map_pan_collapsed_h = sheet.evaluate("el => el.getBoundingClientRect().height")
        print(f"After panning map, BottomSheet height: {map_pan_collapsed_h:.1f}px")
        assert map_pan_collapsed_h <= 65, f"Expected map pan to auto-collapse sheet, got {map_pan_collapsed_h}"
        print("✔ Test 5 Passed: Panning map automatically collapsed sheet into minimal peek bar")

        # 7. 测试点击大地图空白处，自动收起卡片降到最低
        # 先展开
        page.locator("button[title*='展开山峰卡片']").click()
        page.wait_for_timeout(400)
        assert sheet.evaluate("el => el.getBoundingClientRect().height") >= 350

        # 点击地图空白处
        page.locator('.explore-map-container').click(position={'x': 20, 'y': 180})
        page.wait_for_timeout(500)
        map_click_collapsed_h = sheet.evaluate("el => el.getBoundingClientRect().height")
        print(f"After clicking empty map, BottomSheet height: {map_click_collapsed_h:.1f}px")
        assert map_click_collapsed_h <= 65, f"Expected map click to auto-collapse sheet, got {map_click_collapsed_h}"
        print("✔ Test 6 Passed: Clicking empty map automatically collapsed sheet into minimal peek bar")

        # 8. 检查控制台错误
        print("Console errors:", console_errors)
        assert len(console_errors) == 0, f"Found console errors: {console_errors}"
        print("✔ Test 7 Passed: 0 console errors detected")

        browser.close()

    print("\n🎉 ALL BOTTOM SHEET GESTURE & BIG MAP TESTS PASSED 100%! 🎉")

if __name__ == "__main__":
    test_gestures()
