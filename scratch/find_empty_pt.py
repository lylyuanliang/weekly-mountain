from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    b = p.chromium.launch(channel='msedge', headless=True)
    page = b.new_page(viewport={'width': 390, 'height': 844})
    page.goto('http://localhost:5173')
    page.wait_for_timeout(1000)

    # Drag map
    page.mouse.move(100, 250)
    page.mouse.down()
    page.mouse.move(160, 310, steps=5)
    page.mouse.up()
    page.wait_for_timeout(400)

    empty_pt = page.evaluate("""() => {
        // Search
        for (let y = 180; y <= 350; y += 10) {
            for (let x = 20; x <= 370; x += 10) {
                const el = document.elementFromPoint(x, y);
                if (el && !el.closest('.mountain-marker') && !el.closest('button') && !el.closest('header') && !el.closest('.bottom-sheet') && !el.closest('.top-search-bar')) {
                    return { x, y, tag: el.tagName, cls: el.className };
                }
            }
        }
        return null;
    }""")
    print("Empty point after drag:", empty_pt)

    b.close()
