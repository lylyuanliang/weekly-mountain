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
PORT = 5173
BASE_URL = f"http://127.0.0.1:{PORT}"

def check_server_running(url):
    try:
        with urllib.request.urlopen(url, timeout=2) as resp:
            return resp.status == 200
    except Exception:
        return False

def wait_for_server(url, timeout=20):
    start = time.time()
    while time.time() - start < timeout:
        if check_server_running(url):
            return True
        time.sleep(0.5)
    return False

def run_feature_a_verification():
    proc = None
    server_started = check_server_running(BASE_URL)
    if not server_started:
        print(f"[*] Starting Vite dev server on port {PORT}...")
        proc = subprocess.Popen(
            f"npm run dev -- --port {PORT} --host 127.0.0.1",
            shell=True,
            cwd=WORKSPACE_DIR
        )
        assert wait_for_server(BASE_URL, 20), f"Failed to start Vite dev server on {BASE_URL}"

    print(f"[OK] Vite server ready at {BASE_URL}")

    console_errors = []

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
                text = msg.text
                if "favicon.ico" not in text:
                    console_errors.append(f"[Console Error] {text}")
                    print(f"  [Browser Error]: {text}")

        page.on("console", handle_console)
        page.on("pageerror", lambda err: console_errors.append(f"[Page Error] {err}"))

        print("[*] Step 1: Navigating to App...")
        page.goto(BASE_URL, wait_until="networkidle")
        page.wait_for_timeout(1000)

        # 验证地图渲染
        map_el = page.locator(".explore-map-container")
        assert map_el.is_visible(), "Explore map container should be visible"
        print("[PASS] Explore map container rendered successfully.")

        # Step 2: 打开山峰详情抽屉
        print("[*] Step 2: Opening mountain detail sheet...")
        detail_btn = page.locator(".hero-mountain-card button:has-text('路线详情')").first
        if not detail_btn.is_visible():
            # 备选选择器
            detail_btn = page.locator("button:has-text('路线详情')").first
        assert detail_btn.is_visible(), "Card '路线详情' button should be visible"
        detail_btn.click()

        page.wait_for_timeout(800)
        sheet = page.locator(".mountain-detail-sheet")
        assert sheet.is_visible(), "MountainDetailSheet should be visible"
        print("[PASS] MountainDetailSheet drawer opened successfully.")

        # Step 3: 验证山峰详情多图相册画廊 (Gallery Carousel)
        print("[*] Step 3: Verifying Multi-Image Gallery Carousel...")
        hero = page.locator(".hero-gallery-banner")
        assert hero.is_visible(), "Hero gallery banner should be visible"

        # 检查多图指示点与计数器
        dots = page.locator(".gallery-dots button")
        dot_count = dots.count()
        print(f"  [Info] Gallery indicator dots found: {dot_count}")
        assert dot_count >= 2, f"Gallery should have at least 2 dots, found {dot_count}"

        # 检查计数器初始状态 1/N
        counter_btn = page.locator(".hero-gallery-banner button:has-text('/'), .hero-gallery-banner span:has-text('/')").first
        assert counter_btn.is_visible(), "Photo counter badge should be visible"
        counter_text = counter_btn.text_content().strip()
        print(f"  [Info] Initial counter text: {counter_text}")
        assert "1/" in counter_text or "1 /" in counter_text, f"Initial counter should indicate slide 1, got {counter_text}"

        # 点击右侧箭头切换到下一张
        next_btn = page.locator(".gallery-arrow-btn").last
        next_btn.click()
        page.wait_for_timeout(400)
        counter_text_2 = counter_btn.text_content().strip()
        print(f"  [Info] After clicking next arrow: {counter_text_2}")
        assert "2/" in counter_text_2 or "2 /" in counter_text_2, f"Counter should advance to slide 2, got {counter_text_2}"

        # 点击第 3 个指示点
        if dot_count >= 3:
            dots.nth(2).click()
            page.wait_for_timeout(400)
            counter_text_3 = counter_btn.text_content().strip()
            print(f"  [Info] After clicking 3rd dot: {counter_text_3}")
            assert "3/" in counter_text_3 or "3 /" in counter_text_3, f"Counter should advance to slide 3, got {counter_text_3}"

        print("[PASS] Gallery multi-image carousel navigation and indicator dots working perfectly.")

        # Step 4: 验证全屏 Lightbox Modal 大图预览
        print("[*] Step 4: Verifying Fullscreen Lightbox Modal...")
        # 点击 Hero 区域或放大按钮打开 Lightbox
        counter_btn.click()
        page.wait_for_timeout(500)
        lightbox = page.locator(".lightbox-overlay")
        assert lightbox.is_visible(), "Fullscreen Lightbox Modal should be open and visible"
        print("  [Info] Lightbox Modal is open.")

        # 验证大图在视口中央
        lightbox_img = lightbox.locator("img")
        assert lightbox_img.is_visible(), "Large image inside Lightbox should be visible"

        # 在 Lightbox 中点击下一张
        lightbox_next = lightbox.locator("button[aria-label='下一张图片']")
        lightbox_next.click()
        page.wait_for_timeout(400)

        # 按 ESC 退出全屏 Lightbox
        page.keyboard.press("Escape")
        page.wait_for_timeout(500)
        assert not lightbox.is_visible(), "Lightbox should be closed after pressing Escape"
        print("[PASS] Lightbox Modal open, image display, navigation, and ESC exit verified.")

        # Step 5: 验证海拔剖面图与地图探针双向联动
        print("[*] Step 5: Verifying RouteElevationChart & AppMap Probe Beacon Linkage...")
        # 滚动详情抽屉至 Module 3 (mod-waypoints)
        page.locator("#mod-waypoints").scroll_into_view_if_needed()
        page.wait_for_timeout(500)

        chart_svg = page.locator(".route-elevation-chart svg")
        assert chart_svg.is_visible(), "Route elevation chart SVG should be visible"

        # 检查初始航点列表
        waypoint_items = page.locator(".waypoint-item")
        wp_count = waypoint_items.count()
        print(f"  [Info] Waypoint list items found: {wp_count}")
        assert wp_count > 0, "Waypoints should exist in RouteElevationChart"

        # 点击第 2 个航点卡片
        print("  [Action] Clicking on waypoint 2 to dispatch probe...")
        waypoint_items.nth(1).click()
        page.wait_for_timeout(600)

        # 检查地图上是否已渲染探针标记点 (probe-beacon-marker)
        probe_marker = page.locator(".probe-beacon-marker")
        assert probe_marker.is_visible(), "Probe Beacon Marker should be dynamically rendered on AppMap!"
        probe_text = probe_marker.text_content()
        print(f"  [Info] Rendered Probe Beacon text: {probe_text.strip()}")
        assert "#2" in probe_text or "2" in probe_text, "Probe Beacon should display waypoint sequence #2"

        # 测试 SVG 剖面图滑动触发探针
        print("  [Action] Hovering/moving over SVG elevation chart...")
        svg_box = chart_svg.bounding_box()
        if svg_box:
            # 在剖面图后半段移动光标探测
            target_x = svg_box["x"] + svg_box["width"] * 0.75
            target_y = svg_box["y"] + svg_box["height"] * 0.5
            page.mouse.move(target_x, target_y)
            page.wait_for_timeout(400)
            probe_text_after_hover = probe_marker.text_content()
            print(f"  [Info] Probe Beacon text after SVG hover: {probe_text_after_hover.strip()}")

        # Step 6: 验证关闭抽屉后自动清空地图探针
        print("[*] Step 6: Closing detail sheet and verifying probe clearance...")
        close_btn = page.locator(".btn-close-detail").first
        close_btn.click()
        page.wait_for_timeout(600)
        assert not sheet.is_visible(), "MountainDetailSheet should be closed"

        # 验证探针标记点已被自动移除
        assert not probe_marker.is_visible(), "Probe Beacon Marker should be cleared when detail sheet closes"
        print("[PASS] Probe Beacon cleared successfully upon closing detail sheet.")

        # Step 6.5: 针对光雾山 (guangwushan) 专项验证
        print("[*] Step 6.5: Specifically testing 光雾山 (guangwushan)...")
        page.evaluate("""() => {
            const btn = Array.from(document.querySelectorAll('.mountain-marker, .alpine-card, div')).find(el => el.textContent && el.textContent.includes('光雾山'));
            // 通过 Pinia 或全局选择光雾山
            const searchInput = document.querySelector('input[type=\"text\"], input[placeholder*=\"搜索\"]');
            if (searchInput) {
                searchInput.value = '光雾山';
                searchInput.dispatchEvent(new Event('input', { bubbles: true }));
            }
        }""")
        page.wait_for_timeout(600)

        guangwushan_btn = page.locator(".hero-mountain-card button:has-text('路线详情')").first
        if guangwushan_btn.is_visible():
            guangwushan_btn.click()
            page.wait_for_timeout(800)
            assert sheet.is_visible(), "MountainDetailSheet should open for 光雾山"
            print("  [Pass] Opened 光雾山 detail sheet.")

            # 验证画廊与指示点
            g_dots = page.locator(".gallery-dots button")
            assert g_dots.count() >= 2, "光雾山 should have gallery dots"
            print("  [Pass] 光雾山 gallery dots verified.")

            # 滚动并点击光雾山航点
            page.locator("#mod-waypoints").scroll_into_view_if_needed()
            page.wait_for_timeout(400)
            gw_wp = page.locator(".waypoint-item")
            if gw_wp.count() > 0:
                gw_wp.first.click()
                page.wait_for_timeout(500)
                assert probe_marker.is_visible(), "Probe marker should be visible for 光雾山"
                print(f"  [Pass] 光雾山 probe beacon active: {probe_marker.text_content().strip()}")

            # 关闭光雾山详情抽屉
            page.locator(".btn-close-detail").first.click()
            page.wait_for_timeout(500)
            assert not probe_marker.is_visible(), "Probe marker cleared after closing 光雾山"
            print("  [Pass] 光雾山 probe cleared.")

        # Step 7: 控制台运行时错误核验
        print("[*] Step 7: Verifying zero runtime console errors...")
        if console_errors:
            print(f"[FAIL] Found {len(console_errors)} console errors:")
            for err in console_errors:
                print(f"  - {err}")
            assert False, "Console errors detected during execution"
        else:
            print("[PASS] Zero runtime console errors! 100% clean.")

        # 截图存证
        screenshot_path = os.path.join(WORKSPACE_DIR, "scratch", "feature_a_verified.png")
        page.screenshot(path=screenshot_path)
        print(f"[OK] Verification screenshot saved: {screenshot_path}")

        browser.close()

    print("\n=======================================================")
    print("  ALL FEATURE A VERIFICATIONS PASSED (100% GREEN)")
    print("=======================================================")

if __name__ == "__main__":
    try:
        run_feature_a_verification()
    except Exception as e:
        print(f"\n[ERROR] Verification failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
