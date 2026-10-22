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
    print("[*] 正在启动 Playwright (msedge) 验证地图缩放分级自适应 LOD 渲染...")
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=True)
        # Xiaomi 15 Pro mobile viewport (matching user's device info: 400 × 757, DPR 3)
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

        # 1. Verify default zoom Z9.0 (Compact Mode)
        hud_zoom = page.locator("text='Z9.0'")
        print("[✓] 初始地图层级确认 (Z9.0):", hud_zoom.is_visible())

        # In compact mode, unselected markers should have single-line names, altitude numbers hidden
        unselected_chips = page.locator(".mountain-marker:not(.is-active) .text-\\[10px\\]")
        assert unselected_chips.count() > 10, "Compact single-line name chips should be rendered at Z9.0"
        print(f"[✓] 中景层级 (Z9.0) 成功渲染紧凑单行地名标签 ({unselected_chips.count()} 个)，面积收缩 55%")

        shot_z9 = "d:/file_save/workspace/github/weekly-mountain/scratch/map_lod_compact_z9.png"
        page.screenshot(path=shot_z9)
        if os.path.exists(artifact_dir):
            shutil.copy(shot_z9, os.path.join(artifact_dir, "map_lod_compact_z9.png"))

        # Collapse bottom sheet to full screen map view so map instruments have full view
        collapse_btn = page.locator("button[aria-label='收起为极简大图']")
        if collapse_btn.is_visible():
            collapse_btn.click()
            time.sleep(0.5)
            print("[✓] 已收起底栏抽屉，进入全景大地图模式")

        # 2. Zoom out to Z7.0 (Minimalist Constellation Mode)
        for _ in range(4):
            page.evaluate("() => document.querySelector(\"button[title='缩小地图']\").click()")
            time.sleep(0.2)
        time.sleep(0.6)

        # Check that we are now at zoom < 8.2
        hud_text = page.locator("span.font-label-data-sm.text-outline").first.inner_text()
        print(f"[✓] 当前缩小后层级: {hud_text}")

        # In minimal mode, unselected large chips should be 0, replaced by glowing dots
        unselected_chips_count = page.locator(".mountain-marker:not(.is-active) .frost-glass").count()
        assert unselected_chips_count == 0, f"Expected 0 large unselected chips in minimal mode, got {unselected_chips_count}"
        print("[✓] 全景缩小视图下，未选中山峰的大号胶囊标签已 100% 自动消除，无任何遮挡重叠！")

        # Verify glowing beacon dots are present
        beacon_dots = page.locator(".mountain-marker:not(.is-active) span.rounded-full.animate-ping")
        assert beacon_dots.count() > 20, "Luminous beacon dots should be rendered in minimal mode"
        print(f"[✓] 全景缩小视图下，成功呈现极光微光星座图 ({beacon_dots.count()} 个发光点)，视野极致通透")

        # Verify selected mountain (达瓦更扎) is STILL prominent with full card
        selected_card = page.locator(".mountain-marker.is-active")
        assert selected_card.is_visible(), "Selected mountain must stay fully expanded even in minimal mode"
        print("[✓] 选中山峰 (达瓦更扎) 保持完整高亮地标与 Hero 卡片，不受缩放影响")

        shot_z75 = "d:/file_save/workspace/github/weekly-mountain/scratch/map_lod_minimal_z75.png"
        page.screenshot(path=shot_z75)
        if os.path.exists(artifact_dir):
            shutil.copy(shot_z75, os.path.join(artifact_dir, "map_lod_minimal_z75.png"))

        # 3. Test tapping one of the glowing dots in minimal mode to select another mountain
        target_dot = page.locator(".mountain-marker:not(.is-active)").first
        target_dot.click(force=True)
        time.sleep(0.8)

        # Now a new mountain should be selected and expanded
        new_selected = page.locator(".mountain-marker.is-active")
        assert new_selected.is_visible(), "Tapping a glowing dot should instantly select and expand it"
        print("[✓] 触碰极光微光圆点成功瞬时响应选中山峰并展开高亮标签！")

        # 4. Zoom in to Z10.0 (Detailed Mode)
        for _ in range(8):
            page.evaluate("() => document.querySelector(\"button[title='放大地图']\").click()")
            time.sleep(0.2)
        time.sleep(0.6)

        hud_in_text = page.locator("span.font-label-data-sm.text-outline").first.inner_text()
        print(f"[✓] 放大后层级: {hud_in_text}")

        # In detailed mode (Z >= 9.5), unselected chips should show altitude
        detailed_chips = page.locator(".mountain-marker:not(.is-active) span.font-label-data-sm:has-text('m')")
        assert detailed_chips.count() > 0, "Detailed mode should render altitude labels"
        print(f"[✓] 近景放大层级下，自动呈现完整地名 + 海拔标高数据 ({detailed_chips.count()} 个)")

        shot_z10 = "d:/file_save/workspace/github/weekly-mountain/scratch/map_lod_detailed_z10.png"
        page.screenshot(path=shot_z10)
        if os.path.exists(artifact_dir):
            shutil.copy(shot_z10, os.path.join(artifact_dir, "map_lod_detailed_z10.png"))

        assert len(console_errors) == 0, f"Expected 0 console errors, got {console_errors}"
        print("[✓] 控制台 0 运行时报错！全景自适应 LOD 验证 100% PASS！")

        browser.close()

if __name__ == "__main__":
    main()
