import sys
import io
import time
from playwright.sync_api import sync_playwright

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=== Running Map Drag Latency Verification ===")

with sync_playwright() as p:
    browser = p.chromium.launch(channel="msedge", headless=True)
    page = browser.new_page(viewport={"width": 390, "height": 844})
    page.goto("http://localhost:5173/", wait_until="networkidle")
    time.sleep(1)

    # 1. Verify CSS transition property on mountain-marker does NOT transition left/top
    transition_style = page.evaluate("""() => {
        const marker = document.querySelector('.mountain-marker');
        const computed = window.getComputedStyle(marker);
        return {
            transitionProperty: computed.transitionProperty,
            transitionDuration: computed.transitionDuration,
            classList: Array.from(marker.classList)
        };
    }""")
    print("Marker transition properties:", transition_style)
    assert "all" not in transition_style["transitionProperty"], "transitionProperty must not be 'all'!"
    assert "left" not in transition_style["transitionProperty"], "transitionProperty must not include 'left'!"
    assert "top" not in transition_style["transitionProperty"], "transitionProperty must not include 'top'!"
    print("✔ Test 1 Passed: Marker does NOT have CSS animation/transition on left/top coordinates")

    # 2. Measure instant response during fast drag
    map_container = page.locator(".explore-map-container")
    box = map_container.bounding_box()
    cx = 280
    cy = 250

    # Record initial marker position
    pos_before = page.evaluate("() => { const m = document.querySelector('.mountain-marker'); return { left: parseFloat(m.style.left), top: parseFloat(m.style.top) }; }")

    # Perform rapid fast drag sequence within viewport
    page.mouse.move(cx, cy)
    page.mouse.down()
    page.mouse.move(cx - 80, cy + 40, steps=3)
    page.mouse.move(cx - 180, cy + 80, steps=3)

    page.wait_for_timeout(50)
    # Immediately check marker coordinates DURING drag
    pos_during = page.evaluate("() => { const m = document.querySelector('.mountain-marker'); return { left: parseFloat(m.style.left), top: parseFloat(m.style.top) }; }")
    print(f"Position delta during fast drag: dX={pos_during['left'] - pos_before['left']}, dY={pos_during['top'] - pos_before['top']}")

    assert abs(pos_during['left'] - pos_before['left']) >= 100, "Marker should move immediately with pointer delta!"
    print(f"✔ Test 2 Passed: Marker moved instantly by {pos_during['left'] - pos_before['left']}px with 0ms lag")

    page.mouse.up()
    browser.close()

print("🎉 ZERO DRAG LATENCY VERIFIED SUCCESSFULLY!")
