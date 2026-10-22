import asyncio
import os
import sys
from playwright.async_api import async_playwright

SCREENSHOT_PATH = r"C:\Users\lylyu\.gemini\antigravity\brain\94773e75-cfd8-4fb7-87e3-d08b195b9520\distance_sorting_and_guangwushan_verified.png"
URL = "http://localhost:5173/"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(channel="msedge", headless=True)
        context = await browser.new_context(viewport={"width": 412, "height": 915})
        page = await context.new_page()

        console_errors = []
        page.on("console", lambda msg: console_errors.append(msg.text) if msg.type in ["error"] else None)
        page.on("pageerror", lambda exc: console_errors.append(str(exc)))

        print("Navigating to", URL)
        await page.goto(URL, wait_until="networkidle")
        await page.wait_for_timeout(1000)

        # 1. Assert Active Peaks count is 51
        count_text = await page.locator("text=/51\\s*TRACKS/").first.text_content()
        print("Found active peaks count text:", count_text)
        assert "51" in count_text, f"Expected 51 tracks, got {count_text}"

        # 2. Check the cards in the carousel
        cards = page.locator(".hero-mountain-card")
        card_count = await cards.count()
        print(f"Total cards rendered in DOM: {card_count}")
        assert card_count == 51, f"Expected 51 cards, got {card_count}"

        # Read the first 5 cards names and distances
        top_names = []
        for i in range(5):
            c = cards.nth(i)
            name = await c.locator("h3").first.text_content()
            dist_badge = await c.locator("span:has-text('距中心')").first.text_content()
            telemetry_dist = await c.locator(".telemetry-dist-drive").first.text_content()
            top_names.append((name.strip(), dist_badge.strip(), telemetry_dist.strip()))
            print(f"Card {i+1}: {name.strip()} | Badge: {dist_badge.strip()} | Grid: {telemetry_dist.strip()}")

        assert "龙泉山" in top_names[0][0], f"Card 1 should be 龙泉山, got {top_names[0][0]}"
        assert "37.8" in top_names[0][1], f"Card 1 distance badge should contain 37.8, got {top_names[0][1]}"
        assert "38km" in top_names[0][2] and "0.5h" in top_names[0][2], f"Card 1 grid should contain 38km · 0.5h, got {top_names[0][2]}"

        assert "云顶山" in top_names[1][0], f"Card 2 should be 云顶山, got {top_names[1][0]}"
        assert "41" in top_names[1][1], f"Card 2 distance badge should contain 41, got {top_names[1][1]}"

        assert "凤栖山" in top_names[2][0], f"Card 3 should be 凤栖山, got {top_names[2][0]}"
        assert "54.8" in top_names[2][1], f"Card 3 distance badge should contain 54.8, got {top_names[2][1]}"

        # 3. Test search for 光雾山
        print("Searching for '光雾山'...")
        search_input = page.locator("input[type='text'], input[placeholder*='搜索']").first
        await search_input.fill("光雾山")
        await page.wait_for_timeout(500)

        filtered_cards = page.locator(".hero-mountain-card")
        filtered_count = await filtered_cards.count()
        print(f"Search result cards count: {filtered_count}")
        assert filtered_count == 1, f"Expected 1 card for 光雾山, got {filtered_count}"

        first_card = filtered_cards.first
        first_title = await first_card.locator("h3").first.text_content()
        first_dist_badge = await first_card.locator("span:has-text('距中心')").first.text_content()
        first_grid = await first_card.locator(".telemetry-dist-drive").first.text_content()
        print(f"Guangwushan card: {first_title.strip()} | {first_dist_badge.strip()} | {first_grid.strip()}")

        assert "光雾山" in first_title, f"Expected 光雾山, got {first_title}"
        assert "347.9" in first_dist_badge or "348" in first_dist_badge
        assert "348km" in first_grid and "5.5h" in first_grid

        # 4. Open Detail Sheet for Guangwushan
        print("Opening Guangwushan 12-module detail sheet...")
        detail_btn = first_card.locator("button:has-text('路线详情')").first
        await detail_btn.click()
        await page.wait_for_timeout(800)

        detail_sheet = page.locator(".mountain-detail-sheet")
        await detail_sheet.wait_for(state="visible")
        sheet_title = await detail_sheet.locator("h2").first.text_content()
        print("Detail sheet title:", sheet_title.strip())
        assert "光雾山" in sheet_title

        # Check waypoints in module 3
        waypoints_items = page.locator(".waypoint-item")
        wp_count = await waypoints_items.count()
        print(f"Guangwushan waypoints count in detail sheet: {wp_count}")
        assert wp_count == 6, f"Expected 6 waypoints for Guangwushan, got {wp_count}"

        # Close detail sheet
        close_btn = page.locator(".mountain-detail-sheet .btn-close-detail").first
        await close_btn.click()
        await page.wait_for_timeout(600)

        # Clear search
        await search_input.fill("")
        await page.wait_for_timeout(500)

        # Capture final screenshot
        await page.screenshot(path=SCREENSHOT_PATH)
        print("Screenshot saved to", SCREENSHOT_PATH)

        # Check console errors
        print(f"Console errors recorded: {len(console_errors)}")
        if console_errors:
            print("Errors:", console_errors)
        assert len(console_errors) == 0, f"Found {len(console_errors)} console errors"

        print("=== ALL VERIFICATION CHECKS PASSED SUCCESSFULLY ===")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
