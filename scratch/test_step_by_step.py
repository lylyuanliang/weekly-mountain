from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    b = p.chromium.launch(channel='msedge', headless=True)
    page = b.new_page(viewport={'width': 390, 'height': 844})
    page.on('console', lambda msg: print(f"CONSOLE: {msg.text}"))
    page.goto('http://localhost:5173')
    page.wait_for_timeout(1000)
    sheet = page.locator(".bottom-sheet")

    # 6. Drag map
    mx, my = 100, 250
    page.mouse.move(mx, my)
    page.mouse.down()
    page.mouse.move(mx + 60, my + 60, steps=5)
    page.mouse.up()
    page.wait_for_timeout(400)
    print("1. After drag, height:", sheet.bounding_box()['height'])

    # Expand
    expand_btn = page.locator("button[title*='展开山峰卡片']")
    expand_btn.click()
    page.wait_for_timeout(500)
    print("2. After expand, height:", sheet.bounding_box()['height'])

    # Click map
    print("3. Clicking map container...")
    page.locator('.explore-map-container').click(position={'x': 20, 'y': 180})
    page.wait_for_timeout(500)
    print("4. After click, height:", sheet.bounding_box()['height'])

    b.close()
