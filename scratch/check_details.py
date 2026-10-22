from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.launch(channel='msedge', headless=True)
    page = browser.new_page(viewport={'width': 400, 'height': 820})
    page.goto('http://localhost:5173/')
    time.sleep(2)

    # Click first card detail
    page.locator('.hero-mountain-card').first.locator('button', has_text='路线详情').click()
    time.sleep(1)

    mod_wx = page.locator('#mod-weather')
    mod_wx.scroll_into_view_if_needed()
    time.sleep(1)

    # Check details element
    details_el = mod_wx.locator('details')
    assert details_el.is_visible(), 'details element should be visible'
    is_open = details_el.get_attribute('open')
    assert is_open is None, f'details should NOT be open by default, got: {is_open}'
    print('PASS: details is collapsed by default!')

    page.screenshot(path='scratch/weather_keywords_collapsed.png')

    # Click to expand
    details_el.locator('summary').click()
    time.sleep(0.5)
    assert details_el.get_attribute('open') is not None, 'details should be open after click'
    print('PASS: details expands cleanly on click!')

    page.screenshot(path='scratch/weather_keywords_expanded.png')
    browser.close()
    print('All checks passed!')
