from playwright.sync_api import sync_playwright

def inspect():
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=True)
        # Mobile viewport similar to user's phone (e.g. 390x844 iPhone 12/13/14 or Android)
        context = browser.new_context(
            viewport={'width': 390, 'height': 844},
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
            device_scale_factor=2,
            is_mobile=True,
            has_touch=True
        )
        page = context.new_page()

        console_logs = []
        page.on("console", lambda msg: console_logs.append(f"[{msg.type}] {msg.text}"))
        page.on("pageerror", lambda err: console_logs.append(f"[PAGE_ERR] {err}"))

        print("Navigating to https://s-eM08SdZd.html2.link ...")
        response = page.goto("https://s-eM08SdZd.html2.link", timeout=30000, wait_until="networkidle")
        print(f"Status: {response.status if response else 'No response'}")

        page.screenshot(path="scratch/deployed_initial.png")

        # Let's inspect the DOM
        bottom_sheet = page.locator(".bottom-sheet")
        print(f"Bottom sheet count: {bottom_sheet.count()}")
        if bottom_sheet.count() > 0:
            box = bottom_sheet.first.bounding_box()
            print(f"Bottom sheet box: {box}")

        # Now simulate user gesture: swipe up on bottom sheet
        print("Swiping up...")
        page.touchscreen.tap(200, 600)
        page.wait_for_timeout(300)
        # Drag from (200, 600) up to (200, 200)
        page.mouse.move(200, 600)
        page.mouse.down()
        for y in range(600, 200, -20):
            page.mouse.move(200, y)
            page.wait_for_timeout(10)
        page.mouse.up()
        page.wait_for_timeout(500)

        page.screenshot(path="scratch/deployed_after_swipe_up.png")

        print("Console logs:")
        for log in console_logs[-20:]:
            print(log)

        browser.close()

if __name__ == "__main__":
    inspect()
