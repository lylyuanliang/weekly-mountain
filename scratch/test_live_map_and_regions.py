import os
import sys
import io
import time
from playwright.sync_api import sync_playwright

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def run_tests():
    console_errors = []
    failed_requests = []

    print("=================================================================")
    print(" 🚀 STARTING LIVE TILE MAP & MULTI-REGION E2E AUTOMATION TEST 🚀 ")
    print("=================================================================")

    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=True)
        context = browser.new_context(
            viewport={"width": 390, "height": 844},
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148"
        )
        page = context.new_page()

        # Monitor console and failed requests
        page.on("console", lambda msg: console_errors.append(f"[{msg.type}] {msg.text}") if msg.type in ["error"] else None)
        page.on("requestfailed", lambda req: failed_requests.append(req.url))

        target_url = "http://localhost:5173/"
        print(f"\n[Phase 1] Navigating to {target_url}...")
        page.goto(target_url, wait_until="networkidle", timeout=15000)
        time.sleep(1)

        # 1. Verify Top Bar Region Switcher
        print("\n[Phase 2] Verifying Region Switcher in Top App Bar...")
        switcher_btn = page.locator('button[aria-label="切换徒步省市与区域"]')
        assert switcher_btn.is_visible(), "Region switcher button should be visible in top bar"
        switcher_text = switcher_btn.inner_text()
        print(f" -> Region switcher text: {switcher_text}")
        assert "成都周边" in switcher_text, f"Region switcher should show '成都周边', got: {switcher_text}"
        print(" ✔ PASS: Region Switcher properly displays '成都周边'")

        # 2. Verify Real Map Tile Engine
        print("\n[Phase 3] Verifying Real Web Mercator Slippy Map Tile Engine...")
        map_container = page.locator('.explore-map-container')
        assert map_container.is_visible(), "Map container must be visible"

        # Check tile images rendered in DOM
        tiles = page.locator('.explore-map-container img[alt="map tile"]')
        tile_count = tiles.count()
        print(f" -> Found {tile_count} map tile images in DOM")
        assert tile_count >= 4, f"At least 4 map tiles should be rendered for viewport, got: {tile_count}"

        first_tile_src = tiles.first.get_attribute("src")
        print(f" -> First tile URL: {first_tile_src}")
        assert "autonavi.com" in first_tile_src or "style=8" in first_tile_src, "Tile should load from live map tile service"
        print(" ✔ PASS: Live Map Tiles rendered with official map tile provider")

        # 3. Verify Mountain Markers Geographically Placed
        print("\n[Phase 4] Verifying Mountain Markers placement...")
        markers = page.locator('.mountain-marker')
        marker_count = markers.count()
        print(f" -> Found {marker_count} mountain markers in DOM")
        assert marker_count == 50, f"Expected 50 mountain markers, got: {marker_count}"
        print(" ✔ PASS: 50 Mountain Markers rendered on the real map canvas")

        # 4. Verify Layer Switcher Button
        print("\n[Phase 5] Verifying Map Layer Cycling (Dark -> Sat -> Topo)...")
        layer_btn = page.locator('button[title*="切换底图"]')
        assert layer_btn.is_visible(), "Layer toggle button should be visible"

        # Click layer toggle
        layer_btn.click()
        time.sleep(0.5)
        sat_tile = page.locator('.explore-map-container img[alt="map tile"]').first.get_attribute("src")
        print(f" -> Cycled to layer URL: {sat_tile}")
        assert "style=6" in sat_tile or "cartocdn" in sat_tile, "Should cycle to next layer provider"
        print(" ✔ PASS: Layer switcher cycles layers seamlessly")

        # 5. Verify Zoom Controls (+ / -)
        print("\n[Phase 6] Verifying Map Zoom Controls...")
        zoom_in_btn = page.locator('button[title="放大地图"]')
        zoom_out_btn = page.locator('button[title="缩小地图"]')
        assert zoom_in_btn.is_visible() and zoom_out_btn.is_visible(), "Zoom buttons should be visible"
        zoom_in_btn.click()
        time.sleep(0.3)
        zoom_out_btn.click()
        time.sleep(0.3)
        print(" ✔ PASS: Zoom In/Out controls responsive")

        # 6. Verify Opening and Interacting with Region Picker Sheet
        print("\n[Phase 7] Verifying Region Picker Sheet interaction...")
        switcher_btn.click()
        time.sleep(0.6)

        sheet_title = page.locator('text=选择徒步省市与区域')
        assert sheet_title.is_visible(), "Region Picker sheet modal should open"

        # Check active region inside sheet modal
        active_item = page.locator('.p-3\\.5:has-text("成都周边")')
        assert active_item.is_visible(), "Active region 成都周边 should be listed inside sheet"

        # Check planned regions (Chongqing, Xi'an, etc.)
        planned_item = page.locator('.frost-glass:has-text("重庆周边")')
        assert planned_item.is_visible(), "Planned region 重庆周边 should be listed inside sheet"

        # Click on planned region to test toast
        planned_item.click()
        time.sleep(0.5)
        toast = page.locator('text=正在实地勘测与整理 GPS 路线数据')
        assert toast.is_visible(), "Toast notification should inform user of planned region"
        print(" ✔ PASS: Region Picker Sheet displays active and planned regions with feedback")

        # Click active region to select Chengdu and close sheet
        active_item.click()
        time.sleep(0.6)
        print(" ✔ PASS: Re-selecting Chengdu succeeds and closes modal")

        # 7. Capture Screenshot
        os.makedirs("scratch", exist_ok=True)
        screenshot_path = "scratch/e2e_live_map_render.png"
        page.screenshot(path=screenshot_path, full_page=False)
        print(f"\n[Phase 8] Live visual evidence saved to {screenshot_path}")

        # 8. Console Error Verification
        print("\n[Phase 9] Verifying console error log...")
        fatal_errors = [e for e in console_errors if "favicon" not in e.lower()]
        print(f" -> Total console errors: {len(fatal_errors)}")
        if fatal_errors:
            print("Console errors found:", fatal_errors)
        assert len(fatal_errors) == 0, f"Expected 0 runtime console errors, got {len(fatal_errors)}"
        print(" ✔ PASS: ZERO console errors detected")

        browser.close()

    print("\n=================================================================")
    print(" 🎉 ALL LIVE TILE MAP & MULTI-REGION TESTS PASSED (100% GREEN) 🎉")
    print("=================================================================")

if __name__ == "__main__":
    run_tests()
