import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(channel='msedge', headless=True)
        page = await browser.new_page(viewport={'width': 400, 'height': 795})
        await page.goto('http://localhost:5173/')
        await page.wait_for_timeout(1000)

        # 1. Click card for yudingshan
        yudingshan_card = page.locator('#mountain-card-yudingshan').first
        await yudingshan_card.click()
        await page.wait_for_timeout(800)

        # 2. Get bounding box of selected marker
        marker = page.locator('.mountain-marker.selected, .mountain-marker.is-active').first
        marker_box = await marker.bounding_box()
        sheet_box = await page.locator('.bottom-sheet').bounding_box()

        print(f"Marker box: {marker_box}")
        print(f"Sheet box: {sheet_box}")
        print(f"Is marker covered by sheet? Marker Y={marker_box['y']}, Sheet top={sheet_box['y']}")
        if marker_box['y'] >= sheet_box['y']:
            print(f"--> YES! Marker is {marker_box['y'] - sheet_box['y']}px BELOW sheet top! Completely obscured!")
        else:
            print(f"--> NO! Marker is {sheet_box['y'] - marker_box['y']}px above sheet.")

        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
