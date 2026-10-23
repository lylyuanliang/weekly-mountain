import os
import sys
import time
import urllib.request
from playwright.sync_api import sync_playwright

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

PORT = 5173
BASE_URL = f"http://127.0.0.1:{PORT}"
OUT_SCREENSHOT = r"d:\file_save\workspace\github\weekly-mountain\scratch\verify_feedback_fix_1792647942079.png"
OUT_GALLERY_SCREENSHOT = r"d:\file_save\workspace\github\weekly-mountain\scratch\verify_real_photo_gallery.png"

def check_server():
    try:
        with urllib.request.urlopen(f"{BASE_URL}/", timeout=3) as resp:
            return resp.status == 200
    except Exception:
        return False

def main():
    print("=== 开始执行真机反馈 (ID: 1792647942079) 修复回归测试 ===")
    assert check_server(), f"Vite dev server is not running on {BASE_URL}"
    print(f"[OK] Dev server running on {BASE_URL}")

    console_errors = []

    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(channel="msedge", headless=True)
            print("[OK] Launched browser with channel msedge")
        except Exception:
            browser = p.chromium.launch(headless=True)
            print("[OK] Launched default chromium browser")

        # 模拟真机视口（截图同款 400 x 795，DPR 3）
        context = browser.new_context(
            viewport={"width": 400, "height": 795},
            device_scale_factor=3,
            user_agent="Mozilla/5.0 (Linux; Android 16; 24129PN74C) WeChat/arm64"
        )
        page = context.new_page()

        def on_console(msg):
            if msg.type == "error":
                text = msg.text
                if "favicon" not in text:
                    console_errors.append(text)
                    print(f"[Console Error] {text}")

        page.on("console", on_console)
        page.on("pageerror", lambda err: console_errors.append(str(err)))

        page.goto(f"{BASE_URL}/#/explore")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1000)

        # ----------------------------------------------------
        # 测试 1: 验证「反馈给 AI」胶囊按钮无竖向挤压走位
        # ----------------------------------------------------
        print("\n--- 步骤 1: 验证悬浮「反馈给 AI」胶囊尺寸与排版 ---")
        trigger_btn = page.locator(".btn-feedback-trigger")
        assert trigger_btn.is_visible(), "Feedback trigger button should be visible"

        btn_box = trigger_btn.bounding_box()
        print(f"[*] 初始按钮尺寸: width={btn_box['width']:.1f}px, height={btn_box['height']:.1f}px, left={btn_box['x']:.1f}px, top={btn_box['y']:.1f}px")

        # 断言按钮高度必须是单行优雅药丸（30px - 45px），绝不是竖向折行撑高的 80px+ 胖椭圆
        assert btn_box['height'] < 48, f"Button height is suspiciously large ({btn_box['height']}px), likely vertical wrapping!"
        assert btn_box['width'] >= 100, f"Button width should comfortably accommodate content ({btn_box['width']}px)"

        # 模拟向右拖拽贴边
        print("[*] 模拟触摸向右拖拽至屏幕极右侧边缘...")
        page.evaluate("""() => {
            const btn = document.querySelector('.btn-feedback-trigger');
            const rect = btn.getBoundingClientRect();
            const touchStart = new Touch({
                identifier: 1,
                target: btn,
                clientX: rect.left + 20,
                clientY: rect.top + 10
            });
            btn.dispatchEvent(new TouchEvent('touchstart', { touches: [touchStart], targetTouches: [touchStart], changedTouches: [touchStart], bubbles: true }));

            const touchMove = new Touch({
                identifier: 1,
                target: btn,
                clientX: 395,
                clientY: rect.top + 10
            });
            btn.dispatchEvent(new TouchEvent('touchmove', { touches: [touchMove], targetTouches: [touchMove], changedTouches: [touchMove], bubbles: true }));

            btn.dispatchEvent(new TouchEvent('touchend', { touches: [], targetTouches: [], changedTouches: [touchMove], bubbles: true }));
        }""")
        page.wait_for_timeout(300)

        dragged_box = trigger_btn.bounding_box()
        print(f"[*] 拖拽吸附后按钮尺寸: width={dragged_box['width']:.1f}px, height={dragged_box['height']:.1f}px, right-margin={400 - (dragged_box['x'] + dragged_box['width']):.1f}px")

        # 再次断言高度依然保持单行药丸（< 48px），绝无文字折行！
        assert dragged_box['height'] < 48, f"After drag snap, button height became {dragged_box['height']}px (expected single-row < 48px)!"
        assert 400 - (dragged_box['x'] + dragged_box['width']) >= 8, "Button should preserve at least 8px margin from right border!"
        print("[PASS] 「反馈给 AI」按钮在拖拽与吸附后文字 100% 保持单行横排，未发生胖椭圆折行走位！")

        page.screenshot(path=OUT_SCREENSHOT)
        print(f"[OK] 已保存按钮验证截图至 {OUT_SCREENSHOT}")

        # ----------------------------------------------------
        # 测试 2: 验证山峰画廊仅放真实实拍风景照，绝无折线图
        # ----------------------------------------------------
        print("\n--- 步骤 2: 验证山峰画廊只展示真实实景图 ---")
        detail_btn = page.locator(".hero-mountain-card button:has-text('路线详情')").first
        if not detail_btn.is_visible():
            detail_btn = page.locator("button:has-text('路线详情')").first
        assert detail_btn.is_visible(), "Card '路线详情' button should be visible"
        detail_btn.click()
        page.wait_for_timeout(800)

        detail_sheet = page.locator(".mountain-detail-sheet")
        assert detail_sheet.is_visible(), "MountainDetailSheet should be open"

        # 检查画廊大图
        hero_img = page.locator(".hero-gallery-banner img")
        img_src = hero_img.get_attribute("src")
        print(f"[*] 当前画廊展示图片 src: {img_src}")

        # 断言图片来源为真实资产 jpg，且绝对不是伪造的 svg/折线图！
        assert "assets/mountains/" in img_src and img_src.endswith(".jpg"), f"Expected real photo jpg asset, got: {img_src}"
        assert not img_src.startswith("data:image/svg+xml"), "Gallery should NEVER contain simulated SVG charts!"

        # 断言只有真实风景照时，多余箭头与指示点全部自动隐藏
        arrow_btns = page.locator(".gallery-arrow-btn")
        dots = page.locator(".gallery-dots")
        print(f"[*] 箭头按钮数量: {arrow_btns.count()}, 指示点元素数量: {dots.count()}")
        assert arrow_btns.count() == 0, "When having only single real photo, navigation arrows must be hidden!"
        assert dots.count() == 0, "When having only single real photo, indicator dots must be hidden!"

        # 打开全屏 Lightbox 验证
        hero_img.click()
        page.wait_for_timeout(500)

        lightbox = page.locator(".fixed.inset-0.z-\\[120\\]")
        assert lightbox.is_visible(), "Lightbox should open smoothly"

        lb_img = lightbox.locator("img")
        lb_src = lb_img.get_attribute("src")
        print(f"[*] Lightbox 全屏大图 src: {lb_src}")
        assert "assets/mountains/" in lb_src and lb_src.endswith(".jpg"), f"Lightbox must display real scenic photo, got: {lb_src}"

        # 验证全屏下没有假折线图和多余翻页
        lb_arrows = lightbox.locator(".frost-glass.rounded-full:has(.material-symbols-outlined)")
        assert lb_arrows.count() == 0, "Lightbox must not show arrow controls for single photo"
        print("[PASS] 画廊 100% 仅呈现真实实拍风景大图，完全剔除伪造 SVG 折线图！")

        page.screenshot(path=OUT_GALLERY_SCREENSHOT)
        print(f"[OK] 已保存画廊验证截图至 {OUT_GALLERY_SCREENSHOT}")

        # 关闭 Lightbox
        close_btn = lightbox.locator("button[aria-label='关闭大图预览']")
        close_btn.click()
        page.wait_for_timeout(300)

        # ----------------------------------------------------
        # 控制台报错检查
        # ----------------------------------------------------
        assert len(console_errors) == 0, f"Found console errors: {console_errors}"
        print("[PASS] 全程控制台 0 错误 (0 console errors)！")

        print("\n=======================================================")
        print("  🎉 真机反馈 (ID: 1792647942079) 修复回归测试 100% 通过！")
        print("=======================================================")

if __name__ == "__main__":
    main()
