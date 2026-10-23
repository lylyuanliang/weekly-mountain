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
OUT_SCREENSHOT = r"d:\file_save\workspace\github\weekly-mountain\scratch\verify_coaxial_marker_dot.png"

def check_server():
    try:
        with urllib.request.urlopen(f"{BASE_URL}/", timeout=3) as resp:
            return resp.status == 200
    except Exception:
        return False

def main():
    print("=== 开始执行真机反馈 (ID: 1792650711180) 自动化回归测试 ===")
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
        # 步骤 1: 验证 Compact 模式下 (Z9.0) 闪烁光环与圆点 100% 同轴重合 (0 错位)
        # ----------------------------------------------------
        print("\n--- 步骤 1: 验证 Compact 模式下 (Z9.0) 脉冲光环与圆点同心重合 ---")
        active_marker = page.locator(".mountain-marker.is-active")
        assert active_marker.is_visible(), "Active marker should be visible"

        # 检查同心容器
        concentric_container = active_marker.locator(".relative.flex.items-center.justify-center.w-2.h-2")
        assert concentric_container.is_visible(), "Must have coaxial wrapper container for pin dot"

        # 获取 ping 光环与实心圆点
        ping_dot = concentric_container.locator(".animate-ping")
        solid_dot = concentric_container.locator(".relative.w-2.h-2.rounded-full")
        assert ping_dot.count() > 0, "Must have ping animation element"
        assert solid_dot.count() > 0, "Must have solid center dot element"

        ping_box = ping_dot.bounding_box()
        solid_box = solid_dot.bounding_box()
        ping_cx = ping_box['x'] + ping_box['width'] / 2.0
        ping_cy = ping_box['y'] + ping_box['height'] / 2.0
        solid_cx = solid_box['x'] + solid_box['width'] / 2.0
        solid_cy = solid_box['y'] + solid_box['height'] / 2.0
        print(f"[*] Compact 模式: Ping 几何中心 ({ping_cx:.2f}, {ping_cy:.2f}) | Solid 几何中心 ({solid_cx:.2f}, {solid_cy:.2f})")

        # 核心断言: 几何中心偏差必须严格 < 0.5px（完美同心同轴！）
        dx = abs(ping_cx - solid_cx)
        dy = abs(ping_cy - solid_cy)
        print(f"[*] 坐标中心同轴偏差: dx={dx:.2f}px, dy={dy:.2f}px")
        assert dx < 0.5, f"REGRESSION: Ping dot is horizontally misaligned by {dx}px!"
        assert dy < 0.5, f"REGRESSION: Ping dot is vertically misaligned by {dy}px!"

        # 验证胶囊中再也没有游离在胶囊外壳边缘 (-left-0.5) 的第二个错位绿点
        free_ping = active_marker.locator(".-left-0\\.5")
        assert free_ping.count() == 0, "Must NOT have misplaced -left-0.5 element!"
        print("[PASS] Compact 模式下闪烁光环与圆点 100% 同轴重合，完全消除错位与双点现象！")

        # ----------------------------------------------------
        # 步骤 2: 放大地图至 Z10.5+，验证 Detailed 模式下同轴对齐
        # ----------------------------------------------------
        print("\n--- 步骤 2: 放大地图验证 Detailed 模式下同轴对齐 ---")
        zoom_in_btn = page.locator('button[title="放大地图"]')
        for _ in range(3):
            zoom_in_btn.click()
            page.wait_for_timeout(300)
        page.wait_for_timeout(800)

        # 再次检查 Detailed 模式下的同心容器
        concentric_detailed = active_marker.locator(".relative.flex.items-center.justify-center.w-2.h-2")
        assert concentric_detailed.is_visible(), "Detailed mode must also have coaxial container"

        detailed_ping = concentric_detailed.locator(".animate-ping")
        detailed_solid = concentric_detailed.locator(".relative.w-2.h-2.rounded-full")
        p_box = detailed_ping.bounding_box()
        s_box = detailed_solid.bounding_box()
        det_ping_cx = p_box['x'] + p_box['width'] / 2.0
        det_ping_cy = p_box['y'] + p_box['height'] / 2.0
        det_solid_cx = s_box['x'] + s_box['width'] / 2.0
        det_solid_cy = s_box['y'] + s_box['height'] / 2.0
        print(f"[*] Detailed 模式: Ping 几何中心 ({det_ping_cx:.2f}, {det_ping_cy:.2f}) | Solid 几何中心 ({det_solid_cx:.2f}, {det_solid_cy:.2f})")

        dx_det = abs(det_ping_cx - det_solid_cx)
        dy_det = abs(det_ping_cy - det_solid_cy)
        print(f"[*] Detailed 坐标偏差: dx={dx_det:.2f}px, dy={dy_det:.2f}px")
        assert dx_det < 0.5, f"Detailed mode ping dot misaligned by {dx_det}px"
        assert dy_det < 0.5, f"Detailed mode ping dot misaligned by {dy_det}px"
        print("[PASS] Detailed 模式下同样保持 100% 同轴居中！")

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
    print("🎉 真机反馈 (ID: 1792650711180) 100% 回归测试通过！")
    print("==========================================")

if __name__ == "__main__":
    main()
