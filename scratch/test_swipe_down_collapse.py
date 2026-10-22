import sys
import os
import time
from playwright.sync_api import sync_playwright

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

def test_swipe_down():
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=True)
        # Emulate the exact WeChat viewport from user's latest feedback: 400 x 476
        context = browser.new_context(
            viewport={"width": 400, "height": 476},
            has_touch=True,
            user_agent="Mozilla/5.0 (Linux; Android 16; 24129PN74C Build/BP2A.250605.031.A3; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/150.0.7871.189 Mobile Safari/537.36 MicroMessenger/8.0.79"
        )
        page = context.new_page()

        print("[1/4] Navigating to http://localhost:5173/ ...")
        page.goto("http://localhost:5173/", wait_until="domcontentloaded")
        time.sleep(2)

        sheet = page.locator(".bottom-sheet")
        assert sheet.is_visible(), "BottomSheet should be visible"
        initial_box = sheet.bounding_box()
        print(f"Initial BottomSheet height: {initial_box['height']}px (expected ~380-400px)")
        assert initial_box['height'] > 300, "Should start in half state"

        # 2. Test swiping down on the card
        print("[2/4] Simulating touch swipe down on card (deltaY = -35px)...")
        card = page.locator(".hero-mountain-card").first
        card_box = card.bounding_box()
        start_x = card_box["x"] + card_box["width"] / 2
        start_y = card_box["y"] + 40
        end_y = start_y + 45  # Swipe DOWN by 45px

        page.touchscreen.tap(start_x, start_y)
        time.sleep(0.1)

        # Dispatch touch drag
        page.evaluate("""({ startX, startY, endY }) => {
            const el = document.querySelector('.bottom-sheet div');
            const touchStart = new Touch({
                identifier: 1,
                target: el,
                clientX: startX,
                clientY: startY
            });
            el.dispatchEvent(new TouchEvent('touchstart', { touches: [touchStart], changedTouches: [touchStart], bubbles: true, cancelable: true }));

            // Move in steps
            for (let y = startY + 10; y <= endY; y += 10) {
                const touchMove = new Touch({
                    identifier: 1,
                    target: el,
                    clientX: startX,
                    clientY: y
                });
                el.dispatchEvent(new TouchEvent('touchmove', { touches: [touchMove], changedTouches: [touchMove], bubbles: true, cancelable: true }));
            }

            const touchEnd = new Touch({
                identifier: 1,
                target: el,
                clientX: startX,
                clientY: endY
            });
            el.dispatchEvent(new TouchEvent('touchend', { touches: [], changedTouches: [touchEnd], bubbles: true, cancelable: true }));
        }""", {"startX": start_x, "startY": start_y, "endY": end_y})

        time.sleep(1)

        # After swipe down, it should be COLLAPSED (~54px)
        collapsed_box = sheet.bounding_box()
        print(f"After swipe down BottomSheet height: {collapsed_box['height']}px")
        assert collapsed_box['height'] < 80, f"BottomSheet should collapse to peek bar, got {collapsed_box['height']}px"
        print(" PASS: Swipe down collapsed successfully!")

        page.screenshot(path="scratch/swipe_down_collapsed.png")

        # 3. Test swiping up or clicking peek bar to re-expand
        print("[3/4] Testing tap on peek bar to expand back...")
        peek_bar = page.locator("button:has-text('展开')")
        peek_bar.click()
        time.sleep(1)

        expanded_box = sheet.bounding_box()
        print(f"After expand BottomSheet height: {expanded_box['height']}px")
        assert expanded_box['height'] > 300, f"BottomSheet should expand back to half, got {expanded_box['height']}px"
        print(" PASS: Expanded back successfully!")

        # 4. Test explicit '收起大图' button
        print("[4/4] Testing '收起大图' button click...")
        collapse_btn = page.locator("button:has-text('收起大图')")
        collapse_btn.click()
        time.sleep(1)

        re_collapsed_box = sheet.bounding_box()
        print(f"After click '收起大图' height: {re_collapsed_box['height']}px")
        assert re_collapsed_box['height'] < 80, "Should collapse on '收起大图' click"
        print(" PASS: '收起大图' button works perfectly!")

        browser.close()
        print("\nALL SWIPE DOWN & COLLAPSE TESTS PASSED 100%!")

if __name__ == "__main__":
    test_swipe_down()
