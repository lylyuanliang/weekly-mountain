from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    b = p.chromium.launch(channel='msedge', headless=True)
    page = b.new_page(viewport={'width': 390, 'height': 844})
    page.goto('http://localhost:5173')
    page.wait_for_timeout(1000)
    sheet = page.locator(".bottom-sheet")

    # Drag map
    page.mouse.move(100, 250)
    page.mouse.down()
    page.mouse.move(160, 310, steps=5)
    page.mouse.up()
    page.wait_for_timeout(400)

    expand_btn = page.locator("button[title*='展开山峰卡片']")
    expand_btn.click()
    page.wait_for_timeout(500)

    elem_info = page.evaluate("""() => {
        const el = document.elementFromPoint(50, 350);
        return {
            tag: el ? el.tagName : null,
            class: el ? el.className : null,
            closestMarker: el ? !!el.closest('.mountain-marker') : false,
            closestBtn: el ? !!el.closest('button') : false
        };
    }""")
    print("Element at (50, 350) after drag:", elem_info)

    b.close()
