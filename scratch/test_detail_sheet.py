import os
import sys
import time
import subprocess
import urllib.request
from playwright.sync_api import sync_playwright

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

WORKSPACE_DIR = r"d:\file_save\workspace\github\weekly-mountain"
PORT = 5189
BASE_URL = f"http://127.0.0.1:{PORT}"
SCREENSHOT_PATH = os.path.join(WORKSPACE_DIR, "scratch", "detail_sheet_render.png")

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

def test_detail_sheet():
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

            # 收集控制台运行时错误与警告
            def handle_console(msg):
                if msg.type in ("error", "warning"):
                    text = msg.text
                    # 忽略非关键外部资源加载 404 与常规提示
                    if "favicon" in text.lower() or "fonts.gstatic" in text.lower():
                        return
                    if "Download the Vue Devtools" in text or "cdn.tailwindcss.com" in text:
                        return
                    console_errors.append(f"Console {msg.type}: {text}")

            def handle_pageerror(err):
                console_errors.append(f"Page error: {str(err)}")

            page.on("console", handle_console)
            page.on("pageerror", handle_pageerror)

            print(f"Navigating to {BASE_URL}/#/explore ...")
            page.goto(f"{BASE_URL}/#/explore", wait_until="networkidle")
            page.wait_for_timeout(2000)

            # -------------------------------------------------------------
            # 断言 0: 详情抽屉初始状态未展示
            # -------------------------------------------------------------
            detail_sheet = page.locator(".mountain-detail-sheet")
            assert not detail_sheet.is_visible(), "Assertion Failed: .mountain-detail-sheet should not be visible initially!"
            print("[PASS] Assertion 0: Detail sheet is hidden initially")

            # -------------------------------------------------------------
            # 断言 1: 点击卡片上的「🧭 路线详情」按钮触发打开
            # -------------------------------------------------------------
            detail_btn = page.locator(".hero-mountain-card button:has-text('路线详情')").first
            assert detail_btn.is_visible(), "Assertion Failed: Card '路线详情' button not found!"
            detail_btn.click()
            page.wait_for_timeout(600)

            assert detail_sheet.is_visible(), "Assertion Failed: .mountain-detail-sheet did not become visible after clicking '路线详情'!"
            print("[PASS] Assertion 1: MountainDetailSheet opened smoothly")

            # -------------------------------------------------------------
            # 断言 2: 抽屉内 12 个核心模块全部正确渲染
            # -------------------------------------------------------------
            modules = [
                ("1. 概况", ".detail-module-overview"),
                ("2. 路线", ".detail-module-routes"),
                ("3. 高程打卡点", ".detail-module-waypoints"),
                ("4. 亮点", ".detail-module-highlights"),
                ("5. 路况驾驶", ".detail-module-road"),
                ("6. 安全高反", ".detail-module-safety"),
                ("7. 装备清单", ".detail-module-gear"),
                ("8. 餐饮住宿", ".detail-module-food-stay"),
                ("9. 门票费用", ".detail-module-tickets"),
                ("10. 环保倡议", ".detail-module-eco"),
                ("11. 天气预报", ".detail-module-weather"),
                ("12. 核验来源", ".detail-module-sources"),
            ]

            for name, selector in modules:
                mod_el = page.locator(f".mountain-detail-sheet {selector}")
                assert mod_el.count() > 0, f"Assertion Failed: Module '{name}' ({selector}) not found in sheet!"
                assert mod_el.is_visible(), f"Assertion Failed: Module '{name}' ({selector}) is not visible!"
                scroll_mt = page.evaluate(f"() => window.getComputedStyle(document.querySelector('.mountain-detail-sheet {selector}')).scrollMarginTop")
                assert scroll_mt and scroll_mt != "0px", f"Assertion Failed: Module '{name}' missing scroll-margin-top, got: {scroll_mt}"
                print(f"[PASS] Assertion 2.{name}: Module rendered correctly with scrollMarginTop={scroll_mt}")

            # -------------------------------------------------------------
            # 断言 3: 路线高程剖面可视化图表与打卡点列表渲染
            # -------------------------------------------------------------
            chart = page.locator(".mountain-detail-sheet .route-elevation-chart")
            assert chart.is_visible(), "Assertion Failed: .route-elevation-chart not visible!"

            waypoints = page.locator(".mountain-detail-sheet .waypoint-item")
            wp_count = waypoints.count()
            assert wp_count >= 2, f"Assertion Failed: Expected at least 2 waypoints, got {wp_count}!"
            print(f"[PASS] Assertion 3: Elevation chart visible and {wp_count} waypoints rendered")

            # 装备清单勾选测试
            gear_checkbox = page.locator(".mountain-detail-sheet .detail-module-gear input[type='checkbox']").first
            if gear_checkbox.is_visible():
                gear_checkbox.check()
                assert gear_checkbox.is_checked(), "Gear checkbox should be checked after check()"
                print("[PASS] Assertion 3.1: Gear checkbox checked successfully")

            # 截图保存展开首屏状态
            os.makedirs(os.path.dirname(SCREENSHOT_PATH), exist_ok=True)
            page.screenshot(path=SCREENSHOT_PATH)
            print(f"[OK] Screenshot saved to {SCREENSHOT_PATH}")

            # 滚动并截取高程走势图与打卡点列表
            chart_screenshot_path = os.path.join(WORKSPACE_DIR, "scratch", "detail_sheet_chart.png")
            page.locator("#mod-waypoints").scroll_into_view_if_needed()
            page.wait_for_timeout(400)
            page.screenshot(path=chart_screenshot_path)
            print(f"[OK] Chart screenshot saved to {chart_screenshot_path}")

            # -------------------------------------------------------------
            # 断言 4: 点击打卡切换按钮，成功切换打卡状态并同步触发状态更新
            # -------------------------------------------------------------
            checkin_btn = page.locator(".mountain-detail-sheet .btn-checkin-toggle")
            assert checkin_btn.is_visible(), "Assertion Failed: .btn-checkin-toggle not visible in detail sheet!"
            initial_text = checkin_btn.inner_text()
            checkin_btn.click()
            page.wait_for_timeout(400)
            toggled_text = checkin_btn.inner_text()
            assert initial_text != toggled_text, f"Assertion Failed: Checkin button text did not change! ({initial_text} vs {toggled_text})"
            print(f"[PASS] Assertion 4: Checkin toggle works ('{initial_text}' -> '{toggled_text}')")

            # 恢复打卡状态（再点一次）
            checkin_btn.click()
            page.wait_for_timeout(300)

            # -------------------------------------------------------------
            # 断言 5: 点击抽屉右上角关闭按钮，抽屉平滑关闭，重新打开时装备勾选已重置
            # -------------------------------------------------------------
            close_btn = page.locator(".mountain-detail-sheet .btn-close-detail")
            assert close_btn.is_visible(), "Assertion Failed: .btn-close-detail not visible!"
            close_btn.click()
            page.wait_for_timeout(600)
            assert not detail_sheet.is_visible(), "Assertion Failed: .mountain-detail-sheet should be hidden after closing!"
            print("[PASS] Assertion 5: Detail sheet closed successfully via close button")

            # 重新打开抽屉，验证 gearCheckedMap 已重置
            detail_btn.click()
            page.wait_for_timeout(600)
            assert detail_sheet.is_visible(), "Detail sheet should be visible again"
            gear_checkbox_again = page.locator(".mountain-detail-sheet .detail-module-gear input[type='checkbox']").first
            if gear_checkbox_again.is_visible():
                assert not gear_checkbox_again.is_checked(), "Assertion Failed: Gear checkbox should be unchecked after reopen!"
                print("[PASS] Assertion 5.1: Gear checkbox state reset cleanly upon drawer reopen/change")
            close_btn.click()
            page.wait_for_timeout(600)

            # -------------------------------------------------------------
            # 断言 6: 控制台 0 运行时错误与警告
            # -------------------------------------------------------------
            assert len(console_errors) == 0, f"Assertion Failed: Found {len(console_errors)} console errors: {console_errors}"
            print("[PASS] Assertion 6: Zero console runtime errors detected")

            print("\n🎉 ALL DETAIL SHEET END-TO-END TESTS PASSED!")
    finally:
        # 关闭 vite 子进程
        if proc:
            try:
                subprocess.run(f"taskkill /F /T /PID {proc.pid}", shell=True, capture_output=True)
            except Exception:
                pass

if __name__ == "__main__":
    test_detail_sheet()
