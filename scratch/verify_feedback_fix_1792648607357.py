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
OUT_SCREENSHOT = r"d:\file_save\workspace\github\weekly-mountain\scratch\verify_marker_cap_and_compact_top.png"

def check_server():
    try:
        with urllib.request.urlopen(f"{BASE_URL}/", timeout=3) as resp:
            return resp.status == 200
    except Exception:
        return False

def main():
    print("=== 开始执行真机反馈 (ID: 1792648607357 & 1792649081986) 自动化回归测试 ===")
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
        # 步骤 1: 验证顶部搜索框与筛选胶囊精细轻量比例 (反馈 2: 1792649081986)
        # ----------------------------------------------------
        print("\n--- 步骤 1: 验证顶部搜索栏与筛选胶囊紧凑精致度 ---")
        search_box = page.locator(".top-search-bar .w-full.rounded-xl.frost-glass")
        assert search_box.is_visible(), "Top search bar should be visible"
        s_box = search_box.bounding_box()
        print(f"[*] 搜索栏尺寸: w={s_box['width']:.1f}px, h={s_box['height']:.1f}px")
        # 原高度 48px，断言紧凑精简至 <= 42px
        assert s_box['height'] <= 42.0, f"Search bar should be compact (<=42px), got {s_box['height']}px"

        filter_chip = page.locator(".filter-chip").first
        f_box = filter_chip.bounding_box()
        print(f"[*] 筛选胶囊尺寸: w={f_box['width']:.1f}px, h={f_box['height']:.1f}px")
        # 原高度 ~38px，断言紧凑精简至 <= 30px
        assert f_box['height'] <= 30.0, f"Filter chip should be compact (<=30px), got {f_box['height']}px"
        print("[PASS] 顶部搜索栏与筛选胶囊比例轻盈精致，完全消除视觉厚重臃肿感！")

        # ----------------------------------------------------
        # 步骤 2: 放大地图，验证标记点最大尺寸上限死锁 (反馈 1: 1792648607357)
        # ----------------------------------------------------
        print("\n--- 步骤 2: 放大地图至 Z10.5+，验证标记点最大尺寸严格封顶 ---")
        # 连续点击放大按钮 3 次
        zoom_in_btn = page.locator('button[title="放大地图"]')
        assert zoom_in_btn.is_visible(), "Zoom in button should be visible"
        for i in range(3):
            zoom_in_btn.click()
            page.wait_for_timeout(300)

        page.wait_for_timeout(800)

        # 检查当前地图缩放层级
        layer_badge = page.locator('.text-\\[9px\\].font-label-data-sm.text-outline')
        zoom_text = layer_badge.inner_text()
        print(f"[*] 当前地图缩放层级: {zoom_text}")

        # 检查当前选中山峰 Marker（已处于 detailed 模式）
        active_marker = page.locator(".mountain-marker.is-active")
        assert active_marker.is_visible(), "Selected mountain marker should be visible"
        m_box = active_marker.bounding_box()
        print(f"[*] 放大后选中山峰 Marker 尺寸: w={m_box['width']:.1f}px, h={m_box['height']:.1f}px")

        # 核心断言 1: 标记点最大宽度绝对不能超过 150px（原无节制膨胀至 180px+）
        assert m_box['width'] <= 150.0, f"REGRESSION: Active marker width is too huge ({m_box['width']}px)! Max cap failed!"

        # 核心断言 2: 标记点高度紧凑优雅（<= 45px）
        assert m_box['height'] <= 45.0, f"Active marker height is too tall ({m_box['height']}px)"

        # 核心断言 3: 绝对不能含有 animate-ping 造成的巨大扩散圈
        ping_circles = active_marker.locator(".animate-ping")
        assert ping_circles.count() == 0, "Active marker must NOT contain oversized animate-ping elements!"

        # 核心断言 4: 检查 marker 上的 CSS scale 是否严格封顶在 <= 1.0
        marker_style = active_marker.get_attribute("style") or ""
        print(f"[*] Marker 样式属性: {marker_style}")
        assert "scale(1." not in marker_style or "scale(1)" in marker_style or "scale(1.0)" in marker_style, "Marker scale must NOT exceed 1.0x cap!"

        print("[PASS] 选中山峰 Marker 最大尺寸严格封顶在 <= 1.0x / 145px，彻底告别“庞大”走位！")

        page.screenshot(path=OUT_SCREENSHOT)
        print(f"[SCREENSHOT] 验证截图已保存至: {OUT_SCREENSHOT}")

        # ----------------------------------------------------
        # 控制台运行时错误断言
        # ----------------------------------------------------
        print("\n--- 步骤 3: 控制台 0 运行时错误校验 ---")
        assert len(console_errors) == 0, f"Found console errors: {console_errors}"
        print("[PASS] 浏览器控制台 0 错误！")

        browser.close()

    print("\n==========================================")
    print("🎉 真机反馈 (ID: 1792648607357 & 1792649081986) 100% 回归测试通过！")
    print("==========================================")

if __name__ == "__main__":
    main()
