from playwright.sync_api import sync_playwright

def inspect():
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=True)
        context = browser.new_context(
            viewport={'width': 390, 'height': 844},
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
            device_scale_factor=2,
            is_mobile=True,
            has_touch=True
        )
        page = context.new_page()

        print("Navigating to https://s-eM08SdZd.html2.link ...")
        page.goto("https://s-eM08SdZd.html2.link", timeout=30000, wait_until="networkidle")

        # Let's inspect the BottomSheet and HeroMountainCard before swipe
        info_before = page.evaluate("""() => {
            const sheet = document.querySelector('.bottom-sheet');
            const sheetInner = sheet ? sheet.firstElementChild : null;
            const cards = document.querySelectorAll('.hero-mountain-card');
            const map = document.querySelector('.explore-map-container');

            return {
                sheet: sheet ? {
                    offsetHeight: sheet.offsetHeight,
                    computedStyle: {
                        position: getComputedStyle(sheet).position,
                        bottom: getComputedStyle(sheet).bottom,
                        height: getComputedStyle(sheet).height,
                        zIndex: getComputedStyle(sheet).zIndex,
                        transform: getComputedStyle(sheet).transform,
                    }
                } : null,
                sheetInner: sheetInner ? {
                    computedStyle: {
                        backgroundColor: getComputedStyle(sheetInner).backgroundColor,
                        opacity: getComputedStyle(sheetInner).opacity,
                        display: getComputedStyle(sheetInner).display,
                        overflow: getComputedStyle(sheetInner).overflow,
                    }
                } : null,
                cardsCount: cards.length,
                firstCard: cards.length > 0 ? {
                    offsetHeight: cards[0].offsetHeight,
                    offsetWidth: cards[0].offsetWidth,
                    backgroundColor: getComputedStyle(cards[0]).backgroundColor,
                    opacity: getComputedStyle(cards[0]).opacity,
                    zIndex: getComputedStyle(cards[0]).zIndex,
                } : null
            };
        }""")
        print("Before swipe:", info_before)

        # Now trigger the swipe up gesture using touch
        # The bottom sheet handle is at roughly (195, 844 - 400 = 444)
        print("Performing touch swipe up...")
        page.touchscreen.tap(195, 500)
        page.wait_for_timeout(100)

        # Use CDPSession or touch events to dispatch real touchmove
        page.evaluate("""() => {
            const sheet = document.querySelector('.bottom-sheet > div');
            if (!sheet) return;
            const startY = 600;
            const endY = 200;

            const touchObjStart = new Touch({
                identifier: Date.now(),
                target: sheet,
                clientX: 195,
                clientY: startY,
                pageX: 195,
                pageY: startY,
                radiusX: 2.5,
                radiusY: 2.5,
                rotationAngle: 10,
                force: 0.5,
            });

            sheet.dispatchEvent(new TouchEvent('touchstart', {
                cancelable: true,
                bubbles: true,
                touches: [touchObjStart],
                targetTouches: [touchObjStart],
                changedTouches: [touchObjStart]
            }));

            const touchObjMove = new Touch({
                identifier: touchObjStart.identifier,
                target: sheet,
                clientX: 195,
                clientY: endY,
                pageX: 195,
                pageY: endY,
                radiusX: 2.5,
                radiusY: 2.5,
                rotationAngle: 10,
                force: 0.5,
            });

            sheet.dispatchEvent(new TouchEvent('touchmove', {
                cancelable: true,
                bubbles: true,
                touches: [touchObjMove],
                targetTouches: [touchObjMove],
                changedTouches: [touchObjMove]
            }));

            const touchObjEnd = new Touch({
                identifier: touchObjStart.identifier,
                target: sheet,
                clientX: 195,
                clientY: endY,
                pageX: 195,
                pageY: endY,
                radiusX: 2.5,
                radiusY: 2.5,
                rotationAngle: 10,
                force: 0.5,
            });

            sheet.dispatchEvent(new TouchEvent('touchend', {
                cancelable: true,
                bubbles: true,
                touches: [],
                targetTouches: [],
                changedTouches: [touchObjEnd]
            }));
        }""")

        page.wait_for_timeout(600)

        info_after = page.evaluate("""() => {
            const sheet = document.querySelector('.bottom-sheet');
            const sheetInner = sheet ? sheet.firstElementChild : null;
            const cards = document.querySelectorAll('.hero-mountain-card');

            return {
                sheet: sheet ? {
                    offsetHeight: sheet.offsetHeight,
                    computedStyle: {
                        position: getComputedStyle(sheet).position,
                        bottom: getComputedStyle(sheet).bottom,
                        height: getComputedStyle(sheet).height,
                        zIndex: getComputedStyle(sheet).zIndex,
                        transform: getComputedStyle(sheet).transform,
                    }
                } : null,
                sheetInner: sheetInner ? {
                    computedStyle: {
                        backgroundColor: getComputedStyle(sheetInner).backgroundColor,
                        opacity: getComputedStyle(sheetInner).opacity,
                        display: getComputedStyle(sheetInner).display,
                        overflow: getComputedStyle(sheetInner).overflow,
                    }
                } : null,
                firstCard: cards.length > 0 ? {
                    offsetHeight: cards[0].offsetHeight,
                    offsetWidth: cards[0].offsetWidth,
                    backgroundColor: getComputedStyle(cards[0]).backgroundColor,
                    opacity: getComputedStyle(cards[0]).opacity,
                    zIndex: getComputedStyle(cards[0]).zIndex,
                } : null
            };
        }""")
        print("After swipe:", info_after)
        page.screenshot(path="scratch/deployed_after_touch_swipe.png")

        browser.close()

if __name__ == "__main__":
    inspect()
