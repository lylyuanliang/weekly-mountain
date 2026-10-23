# -*- coding: utf-8 -*-
import os
import sys
import time
import urllib.request
from playwright.sync_api import sync_playwright

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

PORT = 5173
BASE_URL = f"http://127.0.0.1:{PORT}"
OUT_NAV_SCREENSHOT = r"d:\file_save\workspace\github\weekly-mountain\scratch\verify_fix_waypoints_nav.png"
OUT_CHART_SCREENSHOT = r"d:\file_save\workspace\github\weekly-mountain\scratch\verify_fix_chart_circle.png"

def check_server():
    try:
        with urllib.request.urlopen(f"{BASE_URL}/", timeout=3) as resp:
            return resp.status == 200
    except Exception:
        return False

def main():
    print("=== 开始执行真机反馈 (ID: 1792648489022) 自动化回归测试 ===")
    assert check_server(), f"Vite dev server is not running on {BASE_URL}"
    print(f"[OK] Dev server running on {BASE_URL}")

    console_errors = []

    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(channel="msedge", headless=True)
            print("[OK] Launched Edge browser")
        except Exception:
            browser = p.chromium.launch(headless=True)
            print("[OK] Launched default Chromium")

        # 模拟真机视口（截图同款 400 x 795，DPR 3，Android 微信）
        context = browser.new_context(
            viewport={"width": 400, "height": 795},
            device_scale_factor=3,
            user_agent="Mozilla/5.0 (Linux; Android 16; 24129PN74C Build/BP2A.250605.031.A3; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/150.0.7871.189 Mobile Safari/537.36 MicroMessenger/8.0.79.3200"
        )
        page = context.new_page()

        def on_console(msg):
            if msg.type == "error":
                text = msg.text
                if "favicon" not in text:
                    console_errors.append(text)
                    print(f"[Console Error] {text}")

        page.on("console", on_console)
        page.on("pageerror", lambda err: console_errors.append(str(err)))

        page.goto(f"{BASE_URL}/#/explore")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1000)

        # ----------------------------------------------------
        # 步骤 1: 点击卡片中的「路线详情」展开详情抽屉
        # ----------------------------------------------------
        print("\n--- 步骤 1: 点击「路线详情」展开详情抽屉 ---")
        detail_btn = page.locator('button:has-text("\u8def\u7ebf\u8be6\u60c5")').first
        assert detail_btn.is_visible(), "Should see '路线详情' button on current active card"
        detail_btn.click()
        page.wait_for_timeout(1000)

        sheet = page.locator(".mountain-detail-sheet")
        assert sheet.is_visible(), "MountainDetailSheet should be open"

        header = sheet.locator("header")
        assert header.is_visible(), "Header should be visible initially"
        sheet_box_before = sheet.bounding_box()
        header_box_before = header.bounding_box()
        header_title = header.locator("h2").inner_text()
        print(f"[*] 成功打开详情抽屉: {header_title}")
        print(f"[*] 初始几何坐标: Sheet y={sheet_box_before['y']:.1f}, Header y={header_box_before['y']:.1f}, Header h={header_box_before['height']:.1f}")

        # 断言初始 aside.scrollTop == 0
        aside_scroll_top_initial = page.evaluate('() => document.querySelector(".mountain-detail-sheet").scrollTop')
        assert aside_scroll_top_initial == 0, f"aside.scrollTop should be 0, got {aside_scroll_top_initial}"

        # ----------------------------------------------------
        # 步骤 2: 点击「高程点」锚点导航，验证 Header 不被卷出屏幕且导航栏 0 缝隙吸顶
        # ----------------------------------------------------
        print("\n--- 步骤 2: 点击「高程点」锚点导航，验证吸顶与 0 间隙 ---")
        nav_tab = sheet.locator('nav button:has-text("\u9ad8\u7a0b\u70b9")')  # 高程点
        assert nav_tab.is_visible(), "Should see '高程点' anchor nav tab"
        nav_tab.click()
        page.wait_for_timeout(1200)

        # 核心断言 1: aside.scrollTop 必须依然为 0（严禁卷走 Header！）
        aside_scroll_top_after = page.evaluate('() => document.querySelector(".mountain-detail-sheet").scrollTop')
        print(f"[*] 点击锚点后 aside.scrollTop: {aside_scroll_top_after}")
        assert aside_scroll_top_after == 0, f"REGRESSION: aside.scrollTop became {aside_scroll_top_after}, Header was scrolled off-screen!"

        # 核心断言 2: Header 依然在屏幕可见范围内且紧贴抽屉顶部
        header_box_after = header.bounding_box()
        print(f"[*] 点击锚点后: Header y={header_box_after['y']:.1f}, Header visible={header.is_visible()}")
        assert header.is_visible(), "Header must remain visible after anchor scroll"
        assert abs(header_box_after['y'] - header_box_before['y']) < 2.0, "Header vertical position must not shift!"

        # 核心断言 3: nav 吸顶在 Header 紧下方，垂直间隙必须 <= 2px（严禁空隙断层或文字从上方穿透）
        nav = sheet.locator("nav")
        nav_box = nav.bounding_box()
        gap_between_header_and_nav = nav_box['y'] - (header_box_after['y'] + header_box_after['height'])
        print(f"[*] Header 底部与 Nav 顶部间隙: {gap_between_header_and_nav:.1f}px")
        assert gap_between_header_and_nav <= 2.0, f"REGRESSION: Gap between Header and Nav is suspiciously large ({gap_between_header_and_nav}px)!"

        page.screenshot(path=OUT_NAV_SCREENSHOT)
        print(f"[PASS] 导航栏顶部间隙与 Header 卷走缺陷已彻底根治，截图保存至: {OUT_NAV_SCREENSHOT}")

        # ----------------------------------------------------
        # 步骤 3: 验证走势图扩散圆圈 0 漂移与原生 SVG SMIL 动画
        # ----------------------------------------------------
        print("\n--- 步骤 3: 验证走势图航点光环 0 漂移 ---")
        nodes = sheet.locator(".route-elevation-chart svg g.cursor-pointer")
        print(f"[*] 找到航点节点数量: {nodes.count()}")
        assert nodes.count() >= 2, "Chart should have at least 2 waypoint nodes"

        # 点击第 2 个节点
        nodes.nth(1).click()
        page.wait_for_timeout(800)

        # 断言该节点下存在脉冲光环
        beacon_circle = nodes.nth(1).locator("circle:has(animate)")
        assert beacon_circle.count() > 0, "Selected waypoint should have SMIL animated circle"

        # 检查是否有 animate-ping 类（绝对不能有，否则导致向右下角漂移）
        circle_class = beacon_circle.get_attribute("class") or ""
        print(f"[*] 光环 circle class: '{circle_class}'")
        assert "animate-ping" not in circle_class, "Beacon circle must NOT use CSS animate-ping!"

        # 检查是否包含原生 SMIL animate 标签
        r_anim = beacon_circle.locator('animate[attributeName="r"]')
        opacity_anim = beacon_circle.locator('animate[attributeName="opacity"]')
        assert r_anim.count() > 0, "Must have SVG SMIL radius animation"
        assert opacity_anim.count() > 0, "Must have SVG SMIL opacity animation"

        # 验证圆心坐标 cx, cy 与节点中心完全对齐
        cx = beacon_circle.get_attribute("cx")
        cy = beacon_circle.get_attribute("cy")
        center_dot = nodes.nth(1).locator("circle").nth(2)
        dot_cx = center_dot.get_attribute("cx")
        dot_cy = center_dot.get_attribute("cy")
        print(f"[*] 光环圆心: ({cx}, {cy}) vs 中心圆点: ({dot_cx}, {dot_cy})")
        assert cx == dot_cx and cy == dot_cy, "Beacon ring center must perfectly match node coordinates!"

        page.screenshot(path=OUT_CHART_SCREENSHOT)
        print(f"[PASS] 走势图漂移圆圈缺陷已彻底根治，截图保存至: {OUT_CHART_SCREENSHOT}")

        # ----------------------------------------------------
        # 控制台运行时错误断言
        # ----------------------------------------------------
        print("\n--- 步骤 4: 控制台 0 运行时错误校验 ---")
        assert len(console_errors) == 0, f"Found console errors: {console_errors}"
        print("[PASS] 浏览器控制台 0 错误！")

        browser.close()

    print("\n==========================================")
    print("🎉 真机反馈 (ID: 1792648489022) 100% 回归测试通过！")
    print("==========================================")

if __name__ == "__main__":
    main()
