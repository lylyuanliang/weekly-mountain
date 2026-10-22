from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    b = p.chromium.launch(channel='msedge', headless=True)
    page = b.new_page(viewport={'width': 390, 'height': 844})
    page.goto('http://localhost:5173')
    page.wait_for_timeout(1000)

    page.on('console', lambda msg: print(f"[{msg.type}] {msg.text}"))

    # Expand sheet if collapsed
    sheet = page.locator(".bottom-sheet")
    print("Initial sheet height:", sheet.bounding_box()['height'])

    # Click empty map
    print("Clicking at (100, 250)...")
    page.mouse.click(100, 250)
    page.wait_for_timeout(500)
    print("After click sheet height:", sheet.bounding_box()['height'])

    b.close()
