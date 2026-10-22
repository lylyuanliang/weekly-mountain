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

def verify_compact_bottom_sheet():
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=True)
        context = browser.new_context(
            viewport={"width": 400, "height": 795},
            has_touch=True,
            user_agent="Mozilla/5.0 (Linux; Android 16; 24129PN74C Build/BP2A.250605.031.A3; wv) AppleWebKit/537.36"
        )
        page = context.new_page()

        print("[1/3] 打开首页 http://localhost:5173/ ...")
        page.goto("http://localhost:5173/", wait_until="domcontentloaded")
        time.sleep(2)

        # 检查卡片与抽屉底部的间距
        print("[2/3] 测量卡片与抽屉底部的间距...")
        metrics = page.evaluate("""() => {
          const drawer = document.querySelector('.bottom-sheet > div');
          const card = document.querySelector('.hero-mountain-card');
          const drawerRect = drawer.getBoundingClientRect();
          const cardRect = card.getBoundingClientRect();
          return {
            drawerHeight: drawer.offsetHeight,
            cardHeight: card.offsetHeight,
            drawerBottom: drawerRect.bottom,
            cardBottom: cardRect.bottom,
            gap: drawerRect.bottom - cardRect.bottom
          };
        }""")

        print(f"测量结果: 抽屉高度={metrics['drawerHeight']}px, 卡片高度={metrics['cardHeight']}px, 底部空隙={metrics['gap']:.1f}px")

        # 严苛断言：原空隙高达 74px，现在必须紧凑收敛至 12px 以内！
        assert metrics['gap'] <= 14, f"底部空隙必须 <= 14px，实际为: {metrics['gap']}"
        assert metrics['gap'] >= 0, f"卡片不能溢出抽屉底部，实际空隙: {metrics['gap']}"
        print("PASS: 底部巨大黑色空隙已彻底消除，卡片与底栏完美贴合，间距紧凑自然！")

        # 验证卡片按钮可点击
        detail_btn = page.locator(".hero-mountain-card button:has-text('路线详情')").first
        plan_btn = page.locator(".hero-mountain-card button:has-text('加入周计划')").first
        assert detail_btn.is_visible(), "路线详情按钮必须可见"
        assert plan_btn.is_visible(), "加入周计划按钮必须可见"

        print("[3/3] 截图留存...")
        page.screenshot(path="scratch/bottom_sheet_compact_verified.png")
        print("截图已保存: scratch/bottom_sheet_compact_verified.png")

        browser.close()
        print("\n🎉 验证彻底通过：抽屉高度已完美贴合内容，告别大空隙！")

if __name__ == "__main__":
    verify_compact_bottom_sheet()
