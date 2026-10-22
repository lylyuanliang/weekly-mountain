import os
import sys
import time
import subprocess
import urllib.request
from playwright.sync_api import sync_playwright

WORKSPACE_DIR = r"d:\file_save\workspace\github\weekly-mountain"
PORT = 5188
BASE_URL = f"http://127.0.0.1:{PORT}"
SCREENSHOT_PATH = os.path.join(WORKSPACE_DIR, "scratch", "explore_view_render.png")

def wait_for_server(url, timeout=30):
    start = time.time()
    while time.time() - start < timeout:
        try:
            with urllib.request.urlopen(url) as resp:
                if resp.status == 200:
                    return True
        except Exception:
            time.sleep(0.5)
    return False

def test_explore_view():
    console_errors = []

    # 1. 启动本地 Vite 开发服务器
    proc = subprocess.Popen(
        f"npm run dev -- --port {PORT} --host 127.0.0.1",
        shell=True,
        cwd=WORKSPACE_DIR
    )

    server_started = False
    try:
        server_started = wait_for_server(BASE_URL, timeout=30)
        assert server_started, f"Vite dev server failed to start at {BASE_URL}"
        print(f"[OK] Dev server running at {BASE_URL}")

        # 2. 启动 Playwright 测试 (msedge 优先，降级 chromium)
        with sync_playwright() as p:
            try:
                browser = p.chromium.launch(channel="msedge", headless=True)
            except Exception:
                browser = p.chromium.launch(headless=True)

            context = browser.new_context(
                viewport={"width": 390, "height": 844},  # Mobile standard (iPhone 12/13/14)
                user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15"
            )
            page = context.new_page()

            # 收集控制台错误
            def handle_console(msg):
                if msg.type == "error":
                    # 忽略外部字体/网络可能的 404 警告，但严格捕获 JS 运行时异常
                    console_errors.append(f"Console error: {msg.text}")

            def handle_pageerror(err):
                console_errors.append(f"Page error: {str(err)}")

            page.on("console", handle_console)
            page.on("pageerror", handle_pageerror)

            print(f"Navigating to {BASE_URL}/#/explore ...")
            page.goto(f"{BASE_URL}/#/explore", wait_until="networkidle")
            page.wait_for_timeout(2000)

            # -------------------------------------------------------------
            # 断言 1: 全屏地图容器渲染
            # -------------------------------------------------------------
            map_container = page.locator(".explore-map-container")
            assert map_container.is_visible(), "Assertion Failed: .explore-map-container is not visible!"
            print("[PASS] Assertion 1: Fullscreen map container .explore-map-container is visible")

            # -------------------------------------------------------------
            # 断言 2: 50 座山峰点位成功标定在地图上
            # -------------------------------------------------------------
            markers = page.locator(".mountain-marker")
            marker_count = markers.count()
            print(f"Detected {marker_count} mountain markers on map.")
            assert marker_count == 50, f"Assertion Failed: Expected 50 mountain markers, found {marker_count}!"
            print("[PASS] Assertion 2: 50 mountain markers successfully rendered on map")

            # -------------------------------------------------------------
            # 断言 3: 顶部浮动搜索栏与快捷筛选芯片展示
            # -------------------------------------------------------------
            search_bar = page.locator(".top-search-bar")
            assert search_bar.is_visible(), "Assertion Failed: .top-search-bar is not visible!"

            search_input = page.locator(".top-search-bar input")
            assert search_input.is_visible(), "Assertion Failed: Search input in .top-search-bar is not visible!"

            filter_chips = page.locator(".filter-chip")
            chip_count = filter_chips.count()
            assert chip_count >= 5, f"Assertion Failed: Expected at least 5 filter chips, found {chip_count}!"
            print(f"[PASS] Assertion 3: .top-search-bar and {chip_count} filter chips visible")

            # -------------------------------------------------------------
            # 断言 4: 底部三段式抽屉 .bottom-sheet
            # -------------------------------------------------------------
            bottom_sheet = page.locator(".bottom-sheet")
            assert bottom_sheet.is_visible(), "Assertion Failed: .bottom-sheet is not visible!"

            drag_handle = page.locator(".drawer-handle")
            assert drag_handle.is_visible(), "Assertion Failed: .drawer-handle is not visible!"
            print("[PASS] Assertion 4: .bottom-sheet and .drawer-handle are present and visible")

            # -------------------------------------------------------------
            # 断言 5: 点击地图第一座山峰的点位，选中山峰状态变更，抽屉卡片联动高亮
            # -------------------------------------------------------------
            first_marker = markers.first
            first_id = first_marker.get_attribute("data-mountain-id")
            first_marker.click()
            page.wait_for_timeout(800)

            # 验证选中山峰卡片或标记存在 active/selected 状态
            active_marker = page.locator(".mountain-marker.is-active, .mountain-marker.selected")
            assert active_marker.count() >= 1, "Assertion Failed: No active/selected marker after clicking!"
            print(f"[PASS] Assertion 5: Clicked mountain marker {first_id}, marker highlighted as active")

            # -------------------------------------------------------------
            # 断言 6: 搜索框输入关键词，过滤山峰联动
            # -------------------------------------------------------------
            search_input.fill("巴朗山")
            page.wait_for_timeout(600)
            filtered_markers = page.locator(".mountain-marker:not([style*='display: none'])")
            filtered_count = filtered_markers.count()
            print(f"After searching '巴朗山': {filtered_count} visible markers")
            assert 0 < filtered_count < 50, f"Assertion Failed: Filtering failed, visible markers: {filtered_count}!"

            # 清空搜索框还原
            search_input.fill("")
            page.wait_for_timeout(600)
            assert page.locator(".mountain-marker").count() == 50, "Assertion Failed: Markers not restored after clearing search"
            print("[PASS] Assertion 6: Search bar filtering dynamically updates markers")

            # -------------------------------------------------------------
            # 截取渲染图
            # -------------------------------------------------------------
            page.screenshot(path=SCREENSHOT_PATH, full_page=False)
            print(f"[PASS] Screenshot saved to: {SCREENSHOT_PATH}")

            # -------------------------------------------------------------
            # 断言 7: 控制台 0 运行时错误
            # -------------------------------------------------------------
            # 过滤网络字体警告
            real_errors = [e for e in console_errors if "font" not in e.lower() and "favicon" not in e.lower()]
            if real_errors:
                print("Captured Errors:", real_errors)
            assert len(real_errors) == 0, f"Assertion Failed: Console had {len(real_errors)} error(s): {real_errors}"
            print("[PASS] Assertion 7: 0 Console runtime errors")

            browser.close()
            print("\n>>> ALL EXPLORE VIEW TESTS PASSED! <<<")

    finally:
        if proc:
            subprocess.run(f"taskkill /F /T /PID {proc.pid}", shell=True, capture_output=True)
            print("[OK] Dev server process cleaned up")

if __name__ == "__main__":
    test_explore_view()
