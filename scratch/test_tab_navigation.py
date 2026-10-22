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
PORT = 5190
BASE_URL = f"http://127.0.0.1:{PORT}"
PLAN_SCREENSHOT_PATH = os.path.join(WORKSPACE_DIR, "scratch", "tab_plan_render.png")
PROFILE_SCREENSHOT_PATH = os.path.join(WORKSPACE_DIR, "scratch", "tab_profile_render.png")

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

def test_tab_navigation():
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
                viewport={"width": 390, "height": 844},
                user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15"
            )
            page = context.new_page()

            def handle_console(msg):
                if msg.type == "error":
                    console_errors.append(f"Console error: {msg.text}")

            def handle_pageerror(err):
                console_errors.append(f"Page error: {str(err)}")

            page.on("console", handle_console)
            page.on("pageerror", handle_pageerror)

            print(f"Navigating to {BASE_URL}/#/explore ...")
            page.goto(f"{BASE_URL}/#/explore", wait_until="networkidle")
            page.wait_for_timeout(1500)

            # -------------------------------------------------------------
            # 断言 0: 全局底部导航栏存在
            # -------------------------------------------------------------
            bottom_nav = page.locator(".stitch-bottom-nav, .bottom-nav")
            assert bottom_nav.is_visible(), "Assertion Failed: BottomNav component is not visible!"
            print("[PASS] Assertion 0: BottomNav is visible")

            # -------------------------------------------------------------
            # 步骤 1: 点击底部导航【📅 周计划】，路由切换至 #/plan
            # -------------------------------------------------------------
            plan_tab = page.locator(".nav-tab-plan, a[href*='#/plan']").first
            assert plan_tab.is_visible(), "Assertion Failed: Plan tab button is not visible!"
            plan_tab.click()
            page.wait_for_timeout(800)

            assert "#/plan" in page.url, f"Assertion Failed: URL did not update to #/plan, current: {page.url}"
            plan_view = page.locator(".plan-view")
            assert plan_view.is_visible(), "Assertion Failed: .plan-view is not visible!"

            # 验证周计划时间线与官方精选路线区域存在
            presets_section = page.locator(".official-presets")
            assert presets_section.is_visible(), "Assertion Failed: Official presets section is not visible!"
            print("[PASS] Assertion 1: Switched to #/plan, .plan-view and .official-presets rendered")

            # -------------------------------------------------------------
            # 步骤 2: 在周计划中套用「川西日出云海线」，卡片成功增加 4 周
            # -------------------------------------------------------------
            # 查找川西日出云海线套用按钮
            seacloud_preset_btn = page.locator(".preset-card:has-text('川西日出云海线'), .preset-card:has-text('云海观景台')").locator(".btn-apply-preset, button:has-text('套用')").first
            assert seacloud_preset_btn.is_visible(), "Assertion Failed: Seacloud preset apply button not visible!"
            seacloud_preset_btn.click()
            page.wait_for_timeout(800)

            # 验证时间线卡片呈现 4 周
            timeline_cards = page.locator(".timeline-week-card")
            card_count = timeline_cards.count()
            print(f"Applied preset, timeline week cards count: {card_count}")
            assert card_count >= 4, f"Assertion Failed: Expected at least 4 timeline cards, found {card_count}"
            print("[PASS] Assertion 2: Applied '川西日出云海线' preset, successfully rendered 4 weeks")

            # 在第 1 周打卡牛背山
            first_checkin_btn = timeline_cards.first.locator("button:has-text('打卡')").first
            assert first_checkin_btn.is_visible(), "Assertion Failed: First card checkin button not visible"
            first_checkin_btn.click()
            page.wait_for_timeout(500)
            print("[PASS] Assertion 2.1: Toggled checkin for first mountain in weekly plan")

            # -------------------------------------------------------------
            # 步骤 2.2: 测试【新建周计划】与【删除本周计划】功能
            # -------------------------------------------------------------
            add_week_btn = page.locator(".btn-add-week, button:has-text('新建周计划')").first
            assert add_week_btn.is_visible(), "Assertion Failed: Add week button is not visible!"
            add_week_btn.click()
            page.wait_for_timeout(500)

            new_card_count = timeline_cards.count()
            print(f"Clicked '新建周计划', week cards count: {new_card_count}")
            assert new_card_count == card_count + 1, f"Assertion Failed: Week count did not increase by 1, expected {card_count + 1}, got {new_card_count}"
            print(f"[PASS] Assertion 2.2: Week count increased from {card_count} to {new_card_count}")

            # 点击新增周的【删除本周计划】按钮
            last_card = timeline_cards.last
            delete_week_btn = last_card.locator(".btn-delete-week, button[title='删除本周计划']").first
            assert delete_week_btn.is_visible(), "Assertion Failed: Delete week button on last card not visible!"
            delete_week_btn.click()
            page.wait_for_timeout(500)

            deleted_card_count = timeline_cards.count()
            print(f"Clicked '删除本周计划', week cards count: {deleted_card_count}")
            assert deleted_card_count == card_count, f"Assertion Failed: Week count did not decrease by 1, expected {card_count}, got {deleted_card_count}"
            print(f"[PASS] Assertion 2.3: Week count decreased from {new_card_count} to {deleted_card_count}")

            # -------------------------------------------------------------
            # 步骤 3: 点击底部导航【🏆 我的】，路由切换至 #/profile
            # -------------------------------------------------------------
            profile_tab = page.locator(".nav-tab-profile, a[href*='#/profile']").first
            assert profile_tab.is_visible(), "Assertion Failed: Profile tab button is not visible!"
            profile_tab.click()
            page.wait_for_timeout(800)

            assert "#/profile" in page.url, f"Assertion Failed: URL did not update to #/profile, current: {page.url}"
            profile_view = page.locator(".profile-view")
            assert profile_view.is_visible(), "Assertion Failed: .profile-view is not visible!"

            # 验证 Telemetry 仪表盘、环状进度条、Bento 勋章
            telemetry_dashboard = page.locator(".telemetry-dashboard")
            assert telemetry_dashboard.is_visible(), "Assertion Failed: .telemetry-dashboard is not visible!"

            progress_circle = page.locator(".circular-progress-widget, .progress-circle")
            assert progress_circle.is_visible(), "Assertion Failed: Circular progress widget is not visible!"

            bento_grid = page.locator(".bento-badges-grid, .badge-grid")
            assert bento_grid.is_visible(), "Assertion Failed: Bento badges grid is not visible!"
            badge_cards = page.locator(".bento-badge-card")
            assert badge_cards.count() >= 4, f"Assertion Failed: Expected at least 4 badges, found {badge_cards.count()}"

            # 验证打卡后有勋章被点亮
            unlocked_badges = page.locator(".bento-badge-card:has-text('已点亮')")
            assert unlocked_badges.count() >= 1, f"Assertion Failed: Expected at least 1 unlocked badge, found {unlocked_badges.count()}"
            print(f"[PASS] Assertion 3: Switched to #/profile, Telemetry dashboard and {unlocked_badges.count()} unlocked Bento badges rendered")

            # -------------------------------------------------------------
            # 步骤 4: 点击「导出备份」与「切换主题」，功能顺畅
            # -------------------------------------------------------------
            export_btn = page.locator(".btn-export-backup, button:has-text('导出备份'), button:has-text('备份')").first
            assert export_btn.is_visible(), "Assertion Failed: Export backup button is not visible!"
            export_btn.click()
            page.wait_for_timeout(500)
            print("[PASS] Assertion 4.1: Export backup clicked smoothly")

            theme_btn = page.locator(".btn-cycle-theme, button:has-text('主题')").first
            assert theme_btn.is_visible(), "Assertion Failed: Cycle theme button is not visible!"
            initial_theme = page.evaluate("() => document.documentElement.getAttribute('data-theme') || 'stitch'")
            theme_btn.click()
            page.wait_for_timeout(500)
            next_theme = page.evaluate("() => document.documentElement.getAttribute('data-theme')")
            print(f"Theme switched from {initial_theme} -> {next_theme}")
            assert initial_theme != next_theme, f"Assertion Failed: Theme did not change! (Still {initial_theme})"
            print("[PASS] Assertion 4.2: Theme cycled successfully")

            # -------------------------------------------------------------
            # 步骤 5: 点击底部导航【🧭 探索】，顺利回到全景地图主屏
            # -------------------------------------------------------------
            explore_tab = page.locator(".nav-tab-explore, a[href*='#/explore']").first
            assert explore_tab.is_visible(), "Assertion Failed: Explore tab button is not visible!"
            explore_tab.click()
            page.wait_for_timeout(800)

            assert "#/explore" in page.url, f"Assertion Failed: URL did not update to #/explore, current: {page.url}"
            map_container = page.locator(".explore-map-container")
            assert map_container.is_visible(), "Assertion Failed: .explore-map-container is not visible after returning to explore!"
            print("[PASS] Assertion 5: Returned to #/explore, map container is active")

            # -------------------------------------------------------------
            # 截图输出：周计划与成就页面渲染截图
            # -------------------------------------------------------------
            plan_tab.click()
            page.wait_for_timeout(600)
            page.screenshot(path=PLAN_SCREENSHOT_PATH, full_page=False)
            print(f"[PASS] Plan screenshot saved to: {PLAN_SCREENSHOT_PATH}")

            profile_tab.click()
            page.wait_for_timeout(600)
            page.screenshot(path=PROFILE_SCREENSHOT_PATH, full_page=False)
            print(f"[PASS] Profile screenshot saved to: {PROFILE_SCREENSHOT_PATH}")

            # -------------------------------------------------------------
            # 断言 6: 控制台 0 运行时错误
            # -------------------------------------------------------------
            real_errors = [e for e in console_errors if "font" not in e.lower() and "favicon" not in e.lower()]
            if real_errors:
                print("Captured Errors:", real_errors)
            assert len(real_errors) == 0, f"Assertion Failed: Console had {len(real_errors)} error(s): {real_errors}"
            print("[PASS] Assertion 6: 0 Console runtime errors")

            browser.close()
            print("\n>>> ALL TAB NAVIGATION TESTS PASSED! <<<")

    finally:
        if proc:
            subprocess.run(f"taskkill /F /T /PID {proc.pid}", shell=True, capture_output=True)
            print("[OK] Dev server process cleaned up")

if __name__ == "__main__":
    test_tab_navigation()
