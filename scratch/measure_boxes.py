import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(channel='msedge', headless=True)
        page = await browser.new_page(viewport={'width': 400, 'height': 795})
        await page.goto('http://localhost:5173/')
        await page.wait_for_timeout(1000)

        nav_box = await page.locator('.bottom-nav').bounding_box()
        sheet_box = await page.locator('.bottom-sheet').bounding_box()
        print('BottomNav box:', nav_box)
        print('BottomSheet box (half):', sheet_box)

        # Collapse sheet
        await page.locator('.drawer-handle').click()
        await page.wait_for_timeout(500)

        collapsed_box = await page.locator('.bottom-sheet').bounding_box()
        print('BottomSheet box (collapsed):', collapsed_box)

        btn = page.locator('.bottom-sheet button:has-text("展开")').first
        btn_box = await btn.bounding_box()
        print('Expand button box:', btn_box)

        sheet_bottom = collapsed_box['y'] + collapsed_box['height']
        nav_top = nav_box['y']
        btn_bottom = btn_box['y'] + btn_box['height'] if btn_box else 0
        print(f'Sheet bottom: {sheet_bottom}, Nav top: {nav_top}, Overlap: {sheet_bottom - nav_top}')
        print(f'Btn top: {btn_box["y"]}, Btn height: {btn_box["height"]}, Sheet top: {collapsed_box["y"]}')

        screenshot_path = r"C:\Users\lylyu\.gemini\antigravity\brain\94773e75-cfd8-4fb7-87e3-d08b195b9520\expand_button_unobstructed_verified.png"
        await page.screenshot(path=screenshot_path)
        print(f"Screenshot saved to {screenshot_path}")
        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
