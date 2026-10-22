import os
import sys
import time
import http.server
import socketserver
import threading
from playwright.sync_api import sync_playwright

WORKSPACE_DIR = r"d:\file_save\workspace\github\weekly-mountain"
DIST_DIR = os.path.join(WORKSPACE_DIR, "dist")
PORT = 8089

# 1. 启动一个纯静态 http.server 模拟 html2.link 静态站点托管
class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIST_DIR, **kwargs)

    def log_message(self, format, *args):
        pass  # 静默请求日志

httpd = socketserver.TCPServer(("127.0.0.1", PORT), Handler)
server_thread = threading.Thread(target=httpd.serve_forever, daemon=True)
server_thread.start()
print(f"[OK] Static HTTP server hosting dist/ at http://127.0.0.1:{PORT}")

errors = []

try:
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(
                channel="msedge",
                headless=True,
                args=["--allow-file-access-from-files"]
            )
        except Exception:
            browser = p.chromium.launch(headless=True, args=["--allow-file-access-from-files"])

        page = browser.new_page(viewport={"width": 390, "height": 844})

        page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
        page.on("pageerror", lambda e: errors.append(str(e)))

        print(f"Loading static deployment: http://127.0.0.1:{PORT}/")
        page.goto(f"http://127.0.0.1:{PORT}/", wait_until="networkidle")
        page.wait_for_timeout(1500)

        # 验证 Explore 地图容器与 50 个标记
        map_container = page.locator(".explore-map-container")
        assert map_container.is_visible(), "Assertion Failed: Map container not visible on static file!"
        markers = page.locator(".mountain-marker").count()
        assert markers == 50, f"Assertion Failed: Expected 50 markers, found {markers}"
        print(f"[PASS] Static dist loaded cleanly with {markers} markers")

        # 验证切换到 #/plan
        plan_tab = page.locator(".nav-tab-plan, a[href*='#/plan']").first
        plan_tab.click()
        page.wait_for_timeout(600)
        assert page.locator(".plan-view").is_visible(), "Plan view not visible"
        print("[PASS] Static dist navigated to #/plan smoothly")

        # 验证切换到 #/profile
        profile_tab = page.locator(".nav-tab-profile, a[href*='#/profile']").first
        profile_tab.click()
        page.wait_for_timeout(600)
        assert page.locator(".profile-view").is_visible(), "Profile view not visible"
        print("[PASS] Static dist navigated to #/profile smoothly")

        # 错误审查
        real_errors = [e for e in errors if "font" not in e.lower() and "favicon" not in e.lower()]
        if real_errors:
            print("Errors:", real_errors)
        assert len(real_errors) == 0, f"Errors: {real_errors}"
        print("[PASS] Zero console errors during static hosting load!")

        browser.close()
        print("\n>>> ALL STATIC DEPLOYMENT TESTS PASSED! <<<")
finally:
    httpd.shutdown()
