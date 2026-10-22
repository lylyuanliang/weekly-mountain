import asyncio
import os
import shutil
import sys
from playwright.async_api import async_playwright

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

ARTIFACT_DIR = r"C:\Users\lylyu\.gemini\antigravity\brain\94773e75-cfd8-4fb7-87e3-d08b195b9520"

async def main():
    console_errors = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(channel='msedge', headless=True)
        page = await browser.new_page(viewport={'width': 400, 'height': 795})

        page.on('console', lambda msg: console_errors.append(msg.text) if msg.type == 'error' else None)

        print("[Step 1] 访问首页 http://localhost:5173/ ...")
        await page.goto('http://localhost:5173/', wait_until='networkidle')
        await page.wait_for_timeout(1000)

        # 检查初始默认山峰（龙泉山）标记点位置
        sheet = page.locator('.bottom-sheet').first
        sheet_box = await sheet.bounding_box()
        assert sheet_box is not None, "未找到 BottomSheet"
        print(f"  BottomSheet 抽屉顶端坐标: y={sheet_box['y']} (高 {sheet_box['height']}px)")

        lqs_marker = page.locator('.mountain-marker.selected, .mountain-marker.is-active').first
        lqs_box = await lqs_marker.bounding_box()
        assert lqs_box is not None, "未找到默认选中的龙泉山标记点"
        print(f"  [初始状态] 龙泉山标记点: x={lqs_box['x']:.1f}, y={lqs_box['y']:.1f}, w={lqs_box['width']:.1f}, h={lqs_box['height']:.1f}")
        assert lqs_box['y'] > 140, f"标记点不应被顶栏遮挡 (当前 y={lqs_box['y']})"
        assert lqs_box['y'] + lqs_box['height'] < sheet_box['y'] - 30, (
            f"龙泉山标记点被卡片遮挡！Marker底端={lqs_box['y'] + lqs_box['height']}, 抽屉顶端={sheet_box['y']}"
        )
        print(f"  ✓ 龙泉山标记点完美悬浮在开阔视野中（距抽屉顶 {sheet_box['y'] - (lqs_box['y'] + lqs_box['height']):.1f}px）")

        # [Step 2] 点击「云顶山」卡片
        print("\n[Step 2] 点击下方卡片轮播中的「云顶山」卡片...")
        yd_card = page.locator('#mountain-card-yudingshan').first
        assert await yd_card.count() > 0, "未找到云顶山卡片"
        await yd_card.click()
        await page.wait_for_timeout(600)  # 等待 380ms 平移动画完成

        # 测量选中的云顶山标记点
        yd_marker = page.locator('.mountain-marker.selected, .mountain-marker.is-active').first
        yd_box = await yd_marker.bounding_box()
        assert yd_box is not None, "未找到选中山峰标记点"
        print(f"  [点击后] 云顶山标记点: x={yd_box['x']:.1f}, y={yd_box['y']:.1f}, w={yd_box['width']:.1f}, h={yd_box['height']:.1f}")

        sheet_box_after = await sheet.bounding_box()
        print(f"  BottomSheet 抽屉顶端坐标: y={sheet_box_after['y']}")

        # 断言云顶山标记点在开阔可见天际中央
        assert yd_box['y'] > 140, f"云顶山标记点不应被顶栏遮挡 (当前 y={yd_box['y']})"
        clearance = sheet_box_after['y'] - (yd_box['y'] + yd_box['height'])
        assert clearance >= 40, f"云顶山标记点距离卡片顶部留白不足: {clearance}px"
        print(f"  ✓ 云顶山标记点完美悬浮在开阔视野中央！距卡片抽屉顶部留白 {clearance:.1f}px，距顶部栏留白 {yd_box['y'] - 150:.1f}px")

        # [Step 3] 验证选中山峰文字与数据
        marker_text = await yd_marker.text_content()
        print(f"  选中山峰标记点文本: {marker_text.strip()}")
        assert "云顶山" in marker_text, f"标记点文本应包含云顶山，实际为 {marker_text}"

        # 截图验证
        screenshot_path = "scratch/marker_visible_above_sheet_verified.png"
        await page.screenshot(path=screenshot_path)
        print(f"\n[Step 4] 截图已保存至: {screenshot_path}")

        # 复制到 artifact 目录
        if os.path.isdir(ARTIFACT_DIR):
            artifact_img = os.path.join(ARTIFACT_DIR, "marker_visible_above_sheet_verified.png")
            shutil.copyfile(screenshot_path, artifact_img)
            print(f"  已同步至脑图产物目录: {artifact_img}")

        # 断言控制台无错误
        print(f"\n[Step 5] 控制台错误检查: {len(console_errors)} 个错误")
        assert len(console_errors) == 0, f"控制台存在错误: {console_errors}"
        print("✓ 全部断言验证通过，控制台 0 运行时错误！")

        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
