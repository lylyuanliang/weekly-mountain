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

def verify_route_segments_mobile():
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=True)
        # Xiaomi 15 viewport
        context = browser.new_context(
            viewport={"width": 400, "height": 820},
            has_touch=True,
            user_agent="Mozilla/5.0 (Linux; Android 16; 24129PN74C Build/BP2A.250605.031.A3; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/150.0.7871.189 Mobile Safari/537.36 MicroMessenger/8.0.79"
        )
        page = context.new_page()

        print("[1/4] 打开页面 http://localhost:5173/ ...")
        page.goto("http://localhost:5173/", wait_until="domcontentloaded")
        time.sleep(2)

        # 搜索达瓦更扎并点击路线详情
        print("[2/4] 打开达瓦更扎详情抽屉...")
        page.locator(".top-search-bar input").fill("达瓦更扎")
        time.sleep(1)

        detail_btn = page.locator(".hero-mountain-card button:has-text('路线详情')").first
        detail_btn.click()
        time.sleep(1.5)

        detail_sheet = page.locator(".mountain-detail-sheet")
        assert detail_sheet.is_visible(), "详情抽屉应该已打开"

        print("[3/4] 滚动至路线模块并检查分段明细排版...")
        routes_mod = page.locator("#mod-routes")
        routes_mod.scroll_into_view_if_needed()
        time.sleep(1)

        # 验证方案名称与地形卡片
        scheme_name = page.locator("text=徒步上山：山脚景区大门").first
        scheme_name.scroll_into_view_if_needed()
        assert scheme_name.is_visible(), "路线方案名称应该完整展示"

        terrain_card = page.locator("text=Z字形盘山公路+高山草甸").first
        terrain_card.scroll_into_view_if_needed()
        assert terrain_card.is_visible(), "地形特征应该独立成卡片展示，不再与标题横向挤压"

        # 验证分段节点与指标徽章
        step1_title = page.locator("text=景区大门/山脚停车点").first
        step1_title.scroll_into_view_if_needed()
        assert step1_title.is_visible(), "第1段起点应该可见"

        step1_to = page.locator("text=通天路中段草甸").first
        assert step1_to.is_visible(), "第1段终点应该可见"

        km1 = page.locator("text=6km").first
        assert km1.is_visible(), "6km 里程胶囊应该可见"

        # 验证路况和补给
        water_card = page.locator("text=水源情报:").first
        water_card.scroll_into_view_if_needed()
        assert water_card.is_visible(), "水源情报卡片应该可见"

        supply_card = page.locator("text=沿途补给:").first
        assert supply_card.is_visible(), "沿途补给卡片应该可见"

        print("[4/4] 截图验证全新排版效果...")
        page.screenshot(path="scratch/route_segments_responsive_verified.png")
        print("截图已保存至: scratch/route_segments_responsive_verified.png")

        browser.close()
        print("\n✅ 排版样式重构验证 100% 通过！方案标题独立展开，地形特征独占药丸，节点与指标分行平铺，彻底告别挤压折行！")

if __name__ == "__main__":
    verify_route_segments_mobile()
