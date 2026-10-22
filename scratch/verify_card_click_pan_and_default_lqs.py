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
    print("[*] 启动 Playwright 验证：首屏默认选中龙泉山 (第一张卡片) + 点击下方卡片地图平滑移动并选中对应点位...")
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=True)
        # Mobile viewport matching user's Xiaomi 15 device (400 × 795, DPR 3)
        context = browser.new_context(
            viewport={"width": 400, "height": 795},
            device_scale_factor=3,
            is_mobile=True,
            has_touch=True,
            user_agent="Mozilla/5.0 (Linux; Android 16; 24129PN74C Build/BP2A.250605.031.A3; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/150.0.7871.189 Mobile Safari/537.36"
        )
        page = context.new_page()

        console_errors = []
        page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
        page.on("pageerror", lambda err: console_errors.append(str(err)))

        page.goto("http://localhost:5173/?debug=1", wait_until="domcontentloaded")
        time.sleep(2)

        artifact_dir = "C:/Users/lylyu/.gemini/antigravity/brain/94773e75-cfd8-4fb7-87e3-d08b195b9520"

        # -------------------------------------------------------------
        # 1. 验证首屏默认选中「龙泉山」且排在下方卡片列表第 1 位
        # -------------------------------------------------------------
        # 验证第一张卡片 ID
        first_card = page.locator(".hero-mountain-card").first
        first_card_id = first_card.get_attribute("id")
        first_card_text = first_card.inner_text()
        print(f"[✓] 下方列表第 1 张卡片 ID: {first_card_id}")
        assert "longquanshan" in first_card_id, f"Expected first card to be longquanshan, got {first_card_id}"
        assert "龙泉山" in first_card_text, "Expected first card text to contain '龙泉山'"
        print("[✓] 确认下方卡片列表第 1 位为【龙泉山】！")

        # 验证第一张卡片带有高亮激活类
        first_card_classes = first_card.get_attribute("class")
        assert "border-primary" in first_card_classes or "glow-primary" in first_card_classes, "First card should have active styling"
        print("[✓] 确认首屏第 1 张卡片带有高亮激活状态 (border-primary / glow-primary)")

        # 验证地图顶部 HUD 坐标展示龙泉山
        hud_coord = page.locator("div.top-44 span.font-label-data-sm").first.inner_text()
        print(f"[✓] 地图 HUD 坐标指示: {hud_coord}")
        assert "龙泉山" in hud_coord or "LONGQUANSHAN" in hud_coord or "104." in hud_coord, f"HUD coordinate should reflect Longquanshan, got {hud_coord}"

        # 验证地图上的龙泉山标记点被选中展开高亮徽章
        lqs_marker = page.locator(".mountain-marker[data-mountain-id='longquanshan']")
        assert lqs_marker.is_visible(), "Longquanshan marker should be visible on map"
        assert "is-active" in lqs_marker.get_attribute("class"), "Longquanshan marker must have is-active class"
        assert "selected" in lqs_marker.get_attribute("class"), "Longquanshan marker must have selected class"
        print(f"[✓] 地图上【龙泉山】标记点确认处于 is-active selected 选中高亮状态！文本: '{lqs_marker.inner_text().strip()}'")

        # 截图保存首屏默认龙泉山
        shot_default = "d:/file_save/workspace/github/weekly-mountain/scratch/default_longquanshan_verified.png"
        page.screenshot(path=shot_default)
        if os.path.exists(artifact_dir):
            shutil.copy(shot_default, os.path.join(artifact_dir, "default_longquanshan_verified.png"))
        print(f"[✓] 已输出首屏龙泉山验证截图: {shot_default}")

        # -------------------------------------------------------------
        # 2. 验证点击下方卡片 -> 地图移动并选中对应的山峰点位
        # -------------------------------------------------------------
        # 获取第 2 张卡片进行点击（比如达瓦更扎或者列表中下一座名山）
        second_card = page.locator(".hero-mountain-card").nth(1)
        second_card_id = second_card.get_attribute("id").replace("mountain-card-", "")
        second_name = second_card.locator("h3").inner_text().strip()
        print(f"[*] 准备点击下方第 2 张卡片: 【{second_name}】 (ID: {second_card_id})...")

        # 点击第 2 张卡片
        second_card.click()

        # 等待平滑平移动画 (380ms) 完成
        time.sleep(0.8)

        # 验证第 2 张卡片变为激活状态
        assert "border-primary" in second_card.get_attribute("class"), f"Card {second_name} should now be active"
        print(f"[✓] 第 2 张卡片【{second_name}】成功变为激活态！")

        # 验证地图上对应的 Marker 变为 is-active selected
        target_marker = page.locator(f".mountain-marker[data-mountain-id='{second_card_id}']")
        assert target_marker.is_visible(), f"Marker for {second_name} should be visible"
        assert "is-active" in target_marker.get_attribute("class"), f"Marker {second_name} must have is-active class"
        print(f"[✓] 地图上【{second_name}】点位成功联动高亮并选中！文本: '{target_marker.inner_text().strip()}'")

        # 验证地图 HUD 切换为新山峰
        new_hud = page.locator("div.top-44 span.font-label-data-sm").first.inner_text()
        print(f"[✓] 点击卡片后地图 HUD 坐标已更新为: {new_hud}")
        assert second_name in new_hud or second_name.upper() in new_hud, f"HUD should contain {second_name}"

        # -------------------------------------------------------------
        # 3. 验证再次点击第 3 张卡片
        # -------------------------------------------------------------
        third_card = page.locator(".hero-mountain-card").nth(2)
        third_card_id = third_card.get_attribute("id").replace("mountain-card-", "")
        third_name = third_card.locator("h3").inner_text().strip()
        print(f"[*] 准备点击下方第 3 张卡片: 【{third_name}】 (ID: {third_card_id})...")

        third_card.click()
        time.sleep(0.8)

        assert "border-primary" in third_card.get_attribute("class"), f"Card {third_name} should now be active"
        third_marker = page.locator(f".mountain-marker[data-mountain-id='{third_card_id}']")
        assert "is-active" in third_marker.get_attribute("class"), f"Marker {third_name} must be active on map"
        print(f"[✓] 点击第 3 张卡片【{third_name}】地图再次成功平移并高亮对应点位！")

        # 截图保存点击卡片联动后视图
        shot_clicked = "d:/file_save/workspace/github/weekly-mountain/scratch/card_click_panned_verified.png"
        page.screenshot(path=shot_clicked)
        if os.path.exists(artifact_dir):
            shutil.copy(shot_clicked, os.path.join(artifact_dir, "card_click_panned_verified.png"))
        print(f"[✓] 已输出卡片点击联动验证截图: {shot_clicked}")

        # 控制台 0 错误断言
        print(f"[✓] 控制台错误数: {len(console_errors)}")
        assert len(console_errors) == 0, f"Expected 0 console errors, got {console_errors}"

        browser.close()
        print("[🎉] 卡片点击地图平移联动 & 首屏默认龙泉山排第一 全部断言 100% PASS！")

if __name__ == "__main__":
    main()
