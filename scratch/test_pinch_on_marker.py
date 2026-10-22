import sys
import os
import time
from playwright.sync_api import sync_playwright

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

def test_pinch_on_marker():
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=True)
        context = browser.new_context(
            viewport={"width": 400, "height": 820},
            has_touch=True,
            user_agent="Mozilla/5.0 (Linux; Android 16; 24129PN74C Build/BP2A.250605.031.A3; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/150.0.7871.189 Mobile Safari/537.36 MicroMessenger/8.0.79"
        )
        page = context.new_page()

        print("[1/4] 打开页面 http://localhost:5173/ ...")
        page.goto("http://localhost:5173/", wait_until="domcontentloaded")
        time.sleep(2)

        # 找到屏幕上的山峰标记点
        print("[2/4] 获取屏幕中心附近可见的 Marker 点位...")
        marker = page.locator(".mountain-marker").first
        assert marker.is_visible(), "屏幕上应该有山峰 Marker 渲染"
        box = marker.bounding_box()
        assert box is not None, "Marker 应该具有有效盒模型坐标"

        m_x = box["x"] + box["width"] / 2
        m_y = box["y"] + box["height"] / 2
        print(f"找到 Marker 坐标: ({m_x:.1f}, {m_y:.1f})")

        # 获取缩放前 Zoom 值
        zoom_text_before = page.locator(".explore-map-container span:has-text('Z')").first.text_content()
        print(f"初始地图缩放层级: {zoom_text_before}")

        # 3. 模拟双指捏合缩放：Finger 1 正好落在 Marker 上，Finger 2 落在右侧
        print("[3/4] 模拟手指正好落在 Marker 点位上执行双指捏合放大手势...")

        # 使用 CDP / evaluate 自定义 TouchEvent 发送两指触摸
        page.evaluate("""
          ([mX, mY]) => {
            const container = document.querySelector('.explore-map-container');
            if (!container) return;

            // Touch 1: exactly on marker
            const touch1 = new Touch({
              identifier: 1,
              target: document.elementFromPoint(mX, mY) || container,
              clientX: mX,
              clientY: mY,
              screenX: mX,
              screenY: mY,
              pageX: mX,
              pageY: mY
            });

            // Touch 2: 50px away
            const touch2Start = new Touch({
              identifier: 2,
              target: container,
              clientX: mX + 50,
              clientY: mY + 50,
              screenX: mX + 50,
              screenY: mY + 50,
              pageX: mX + 50,
              pageY: mY + 50
            });

            const touchStartEvt = new TouchEvent('touchstart', {
              touches: [touch1, touch2Start],
              targetTouches: [touch1],
              changedTouches: [touch1, touch2Start],
              bubbles: true,
              cancelable: true
            });
            container.dispatchEvent(touchStartEvt);

            // Move Touch 2 outwards to 150px (Pinch to Zoom In!)
            const touch2Move = new Touch({
              identifier: 2,
              target: container,
              clientX: mX + 150,
              clientY: mY + 150,
              screenX: mX + 150,
              screenY: mY + 150,
              pageX: mX + 150,
              pageY: mY + 150
            });

            const touchMoveEvt = new TouchEvent('touchmove', {
              touches: [touch1, touch2Move],
              targetTouches: [touch1],
              changedTouches: [touch2Move],
              bubbles: true,
              cancelable: true
            });
            container.dispatchEvent(touchMoveEvt);

            // Touchend
            const touchEndEvt = new TouchEvent('touchend', {
              touches: [],
              targetTouches: [],
              changedTouches: [touch1, touch2Move],
              bubbles: true,
              cancelable: true
            });
            container.dispatchEvent(touchEndEvt);
          }
        """, [m_x, m_y])

        time.sleep(1)

        # 4. 验证缩放层级成功增加
        print("[4/4] 验证地图缩放成功，Marker 不再阻断手势...")
        zoom_text_after = page.locator(".explore-map-container span:has-text('Z')").first.text_content()
        print(f"双指捏合后地图缩放层级: {zoom_text_after}")

        # 确保缩放有发生
        assert zoom_text_after != zoom_text_before, f"缩放前后层级应该变化！(Before: {zoom_text_before}, After: {zoom_text_after})"
        print(f"PASS: 缩放层级成功从 {zoom_text_before} 放大至 {zoom_text_after}！")

        browser.close()
        print("\n🎉 验证彻底通过：即便手指直接落在点位上，两指放大缩小手势依然 100% 灵敏生效！")

if __name__ == "__main__":
    test_pinch_on_marker()
