from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    b = p.chromium.launch(channel='msedge', headless=True)
    page = b.new_page(viewport={'width': 390, 'height': 844})
    page.goto('http://localhost:5173')
    page.wait_for_timeout(1000)
    sheet = page.locator(".bottom-sheet")

    page.evaluate("""() => {
        const map = document.querySelector('.explore-map-container');
        map.addEventListener('mousedown', (e) => console.log('MAP_MOUSEDOWN', e.clientX, e.clientY, e.target.tagName, e.target.className));
        map.addEventListener('mouseup', (e) => console.log('MAP_MOUSEUP', e.clientX, e.clientY));
        window.addEventListener('click', (e) => console.log('WINDOW_CLICK', e.clientX, e.clientY, e.target.tagName));
    }""")
    page.on('console', lambda msg: print(f"[{msg.type}] {msg.text}"))

    # 6. Drag map
    mx, my = 100, 250
    page.mouse.move(mx, my)
    page.mouse.down()
    page.mouse.move(mx + 60, my + 60, steps=5)
    page.mouse.up()
    page.wait_for_timeout(400)
    print("After drag:", sheet.bounding_box()['height'])

    # Expand
    expand_btn = page.locator("button[title*='展开山峰卡片']")
    expand_btn.click()
    page.wait_for_timeout(500)
    print("After expand click:", sheet.bounding_box()['height'])

    # Click empty map
    print("Now clicking empty map...")
    page.mouse.click(mx, my)
    page.wait_for_timeout(500)
    print("After click map:", sheet.bounding_box()['height'])

    b.close()
