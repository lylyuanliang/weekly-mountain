import asyncio
import os
import sys
from playwright.async_api import async_playwright

SCREENSHOT_PATH_SEARCH = r"C:\Users\lylyu\.gemini\antigravity\brain\94773e75-cfd8-4fb7-87e3-d08b195b9520\search_focus_unobstructed_verified.png"
SCREENSHOT_PATH_CHECKBOX = r"C:\Users\lylyu\.gemini\antigravity\brain\94773e75-cfd8-4fb7-87e3-d08b195b9520\custom_checkbox_stitch_verified.png"
URL = "http://localhost:5173/"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(channel="msedge", headless=True)
        context = await browser.new_context(viewport={"width": 400, "height": 795})
        page = await context.new_page()

        console_errors = []
        page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
        page.on("pageerror", lambda exc: console_errors.append(str(exc)))

        print("Navigating to", URL)
        await page.goto(URL, wait_until="networkidle")
        await page.wait_for_timeout(1000)

        # -------------------------------------------------------------------------
        # TEST 1: TopSearchBar z-index, fixed position, and focus auto-collapse
        # -------------------------------------------------------------------------
        print("\n--- Test 1: Search Bar Visibility & Focus Auto-Collapse ---")
        search_bar = page.locator(".top-search-bar")
        assert await search_bar.is_visible(), "TopSearchBar must be visible"

        z_index = await search_bar.evaluate("el => window.getComputedStyle(el).zIndex")
        position = await search_bar.evaluate("el => window.getComputedStyle(el).position")
        print(f"TopSearchBar computed style: position={position}, z-index={z_index}")
        assert position == "fixed", f"Expected position fixed, got {position}"
        assert int(z_index) >= 50, f"Expected z-index >= 50, got {z_index}"

        # Click search input to focus
        search_input = page.locator(".top-search-bar input")
        await search_input.click()
        await page.wait_for_timeout(600)

        # Verify BottomSheet auto-collapsed to 54px
        sheet = page.locator(".bottom-sheet")
        sheet_box = await sheet.bounding_box()
        search_box = await search_bar.bounding_box()
        print(f"On search focus: SearchBar top={search_box['y']}, height={search_box['height']} | Sheet top={sheet_box['y']}, height={sheet_box['height']}")

        # In collapsed state, sheet height is around 54px (bottom-docked)
        assert sheet_box['height'] <= 70, f"BottomSheet must be collapsed (height <= 70), got {sheet_box['height']}"
        assert sheet_box['y'] > search_box['y'] + search_box['height'], "BottomSheet must be completely below SearchBar"

        # Simulate mobile virtual keyboard popup (shrink viewport height to 400px)
        print("Simulating mobile keyboard popup (viewport height=400)...")
        await page.set_viewport_size({"width": 400, "height": 400})
        await page.wait_for_timeout(500)

        search_box_kb = await search_bar.bounding_box()
        sheet_box_kb = await sheet.bounding_box()
        print(f"With keyboard (400px): SearchBar top={search_box_kb['y']}, Sheet top={sheet_box_kb['y']}, Sheet height={sheet_box_kb['height']}")
        assert search_box_kb['y'] >= 0, "SearchBar must remain in view"
        assert await search_input.is_visible(), "Search input must remain visible when keyboard appears"

        await page.screenshot(path=SCREENSHOT_PATH_SEARCH)
        print(f"[OK] Search focus screenshot saved to: {SCREENSHOT_PATH_SEARCH}")

        # Restore viewport
        await page.set_viewport_size({"width": 400, "height": 795})
        await page.wait_for_timeout(500)

        # -------------------------------------------------------------------------
        # TEST 2: Feedback to AI modal custom Stitch Alpine checkbox
        # -------------------------------------------------------------------------
        print("\n--- Test 2: Feedback Modal Custom Stitch Alpine Checkbox ---")
        feedback_fab = page.locator(".btn-feedback-trigger").first
        await feedback_fab.click()
        await page.wait_for_timeout(600)

        modal = page.locator(".mobile-feedback-modal").first
        await modal.wait_for(state="visible")

        # Switch to "提新反馈" tab if currently on history tab
        create_tab = page.locator("button[data-tab='create']").first
        if await create_tab.is_visible():
            await create_tab.click()
            await page.wait_for_timeout(400)

        # Check the custom checkbox container
        checkbox_card = modal.locator(".feedback-checkbox-card").first
        assert await checkbox_card.is_visible(), "Checkbox card must be visible"

        # Check custom icon box
        icon_box = checkbox_card.locator(".w-5.h-5")
        assert await icon_box.is_visible(), "Custom Stitch Alpine checkbox box must be visible"

        # Initial state should be unchecked
        status_text = await checkbox_card.locator("span.font-mono").text_content()
        print("Initial checkbox status text:", status_text.strip())
        assert "默认未勾选" in status_text or "未开启" in status_text

        # Click to toggle check
        print("Clicking custom checkbox...")
        await checkbox_card.click()
        await page.wait_for_timeout(1200)

        # Status should now indicate active / capturing
        toggled_text = await checkbox_card.locator("span.font-mono").text_content()
        print("Toggled checkbox status text:", toggled_text.strip())
        assert "已开启" in toggled_text or "截屏中" in toggled_text or "已勾选" in toggled_text

        # Capture screenshot of the modal with custom Stitch checkbox
        await page.screenshot(path=SCREENSHOT_PATH_CHECKBOX)
        print(f"[OK] Custom checkbox screenshot saved to: {SCREENSHOT_PATH_CHECKBOX}")

        # Check console errors
        print(f"Console errors: {len(console_errors)}")
        if console_errors:
            print("Errors:", console_errors)
        assert len(console_errors) == 0, f"Found {len(console_errors)} console errors"

        print("\n=== ALL VERIFICATION CHECKS PASSED 100% ===")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
