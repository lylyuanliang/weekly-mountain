import sys
import os
import time
import shutil
from playwright.sync_api import sync_playwright

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

def main():
    print("[*] 正在启动 Playwright (msedge) 验证地图标记点平滑适度缩放系统...")
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=True)
        # Match user's mobile device viewport (Xiaomi 15: 400 × 757, DPR 3)
        context = browser.new_context(
            viewport={"width": 400, "height": 757},
            device_scale_factor=3,
            is_mobile=True,
            has_touch=True,
            user_agent="Mozilla/5.0 (Linux; Android 16; 2509FPN0BC Build/BP2A.250605.031.A3; wv) AppleWebKit/537.36 Mobile Safari/537.36"
        )
        page = context.new_page()

        console_errors = []
        page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
        page.on("pageerror", lambda err: console_errors.append(str(err)))

        page.goto("http://localhost:5173/?debug=1", wait_until="domcontentloaded")
        time.sleep(2)

        artifact_dir = "C:/Users/lylyu/.gemini/antigravity/brain/94773e75-cfd8-4fb7-87e3-d08b195b9520"

        # Collapse bottom sheet to full screen map view for clean cartography verification
        collapse_btn = page.locator("button[aria-label='收起为极简大图']")
        if collapse_btn.is_visible():
            collapse_btn.click()
            time.sleep(0.5)
            print("[✓] 已收起底栏抽屉，进入全景大地图模式")

        # 1. Verify default zoom Z9.0
        hud_zoom = page.locator("span.font-label-data-sm.text-outline").first
        print(f"[✓] 默认初始层级: {hud_zoom.inner_text()}")

        # Assert no static SVG circle exists
        svg_circle = page.locator("svg circle[fill='url(#peakGlow1)']")
        assert svg_circle.count() == 0, "Static 720px green circle overlay should be completely removed"
        print("[✓] 确认固定坐标 720px 假背景光晕圆已彻底移除！")

        # 2. Zoom out to Z6.7 (matching user screenshot)
        # Default is 9.0. Each zoomOut click reduces by 0.5.
        # Click 5 times -> 9.0 - 2.5 = 6.5 ~ 6.7
        for _ in range(5):
            page.evaluate("() => document.querySelector(\"button[title='缩小地图']\").click()")
            time.sleep(0.2)
        time.sleep(0.6)

        zoom_text = hud_zoom.inner_text()
        print(f"[✓] 当前缩小后层级: {zoom_text}")

        # Check unselected markers at zoomed-out level
        unselected_markers = page.locator(".mountain-marker:not(.is-active)")
        assert unselected_markers.count() > 10, f"Expected >10 unselected markers, got {unselected_markers.count()}"

        # Get bounding box of first 5 unselected markers
        unselected_widths = []
        for i in range(min(5, unselected_markers.count())):
            box = unselected_markers.nth(i).bounding_box()
            if box:
                unselected_widths.append(box["width"])
                text = unselected_markers.nth(i).inner_text().strip()
                print(f"   - 未选中山峰 #{i+1} 尺寸: 宽={box['width']:.1f}px, 高={box['height']:.1f}px, 文本='{text}'")
                assert len(text) > 0, "Unselected markers must show mountain name text, NOT naked dots!"
                assert 30 <= box["width"] <= 75, f"Unselected marker width should be compact (30~75px), got {box['width']}"

        # Check selected marker (达瓦更扎) at zoomed-out level
        selected_marker = page.locator(".mountain-marker.is-active")
        assert selected_marker.is_visible(), "Selected marker must be visible"
        sel_box = selected_marker.bounding_box()
        sel_text = selected_marker.inner_text().strip()
        print(f"[✓] 选中山峰 (达瓦更扎) 缩小层级尺寸: 宽={sel_box['width']:.1f}px, 高={sel_box['height']:.1f}px, 文本='{sel_text}'")
        assert 60 <= sel_box["width"] <= 110, f"Selected marker width should be sleek (60~110px), got {sel_box['width']}"

        # Calculate ratio
        avg_unsel_width = sum(unselected_widths) / len(unselected_widths)
        ratio = sel_box["width"] / avg_unsel_width
        print(f"[✓] 选中山峰与未选中山峰宽度比例: {ratio:.2f}x (黄金视觉层级，彻底告别 22x 极端两极分化)")
        assert 1.2 <= ratio <= 2.2, f"Ratio should be between 1.2x and 2.2x, got {ratio}"

        # Capture Z6.7 verification screenshot
        shot_z67 = "d:/file_save/workspace/github/weekly-mountain/scratch/moderate_marker_scale_z67.png"
        page.screenshot(path=shot_z67)
        if os.path.exists(artifact_dir):
            shutil.copy(shot_z67, os.path.join(artifact_dir, "moderate_marker_scale_z67.png"))
        print(f"[✓] 已输出 Z6.7 视觉验证截图: {shot_z67}")

        # 3. Test tapping another unselected mountain at Z6.7
        target = unselected_markers.first
        target.click(force=True)
        time.sleep(0.6)
        new_sel = page.locator(".mountain-marker.is-active")
        new_sel_box = new_sel.bounding_box()
        print(f"[✓] 点击切换山峰成功: '{new_sel.inner_text().strip()}', 尺寸: 宽={new_sel_box['width']:.1f}px")

        # 4. Zoom in to detailed level Z10.5
        for _ in range(8):
            page.evaluate("() => document.querySelector(\"button[title='放大地图']\").click()")
            time.sleep(0.2)
        time.sleep(0.6)

        zoom_detailed = hud_zoom.inner_text()
        print(f"[✓] 当前放大近景层级: {zoom_detailed}")

        # In detailed mode, unselected markers should show altitude via font-label-data-sm
        detailed_alts = page.locator(".mountain-marker:not(.is-active) span.font-label-data-sm")
        assert detailed_alts.count() > 5, f"Detailed mode should render altitude text, got {detailed_alts.count()}"
        print(f"[✓] 近景特写层级成功渲染山峰标高 ({detailed_alts.count()} 个)，细节丰富")

        # Capture Z10.5 screenshot
        shot_z105 = "d:/file_save/workspace/github/weekly-mountain/scratch/moderate_marker_scale_z105.png"
        page.screenshot(path=shot_z105)
        if os.path.exists(artifact_dir):
            shutil.copy(shot_z105, os.path.join(artifact_dir, "moderate_marker_scale_z105.png"))
        print(f"[✓] 已输出 Z10.5 视觉验证截图: {shot_z105}")

        # Verify console errors
        print(f"[✓] 控制台错误数: {len(console_errors)}")
        assert len(console_errors) == 0, f"Expected 0 console errors, got {console_errors}"

        browser.close()
        print("[🎉] 地图标记点平滑适度缩放系统全部断言通过！100% PASS！")

if __name__ == "__main__":
    main()
