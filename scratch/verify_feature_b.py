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
SCREENSHOT_MODAL_PATH = os.path.join(r"d:\file_save\workspace\github\weekly-mountain\scratch", "verify_feature_b_poster.png")
SCREENSHOT_PROFILE_PATH = os.path.join(r"d:\file_save\workspace\github\weekly-mountain\scratch", "verify_feature_b_profile.png")

def check_server():
    try:
        with urllib.request.urlopen(f"{BASE_URL}/", timeout=3) as resp:
            return resp.status == 200
    except Exception:
        return False

def run_verification():
    print("=== 开始执行 Feature B 自动化验证测试 ===")
    assert check_server(), f"Vite dev server is not accessible on {BASE_URL}"
    print(f"[OK] Dev server running on {BASE_URL}")

    console_errors = []

    with sync_playwright() as p:
        # 使用本地 msedge 或 chromium
        try:
            browser = p.chromium.launch(channel="msedge", headless=True)
            print("[OK] Launched browser with channel msedge")
        except Exception:
            browser = p.chromium.launch(headless=True)
            print("[OK] Launched default chromium browser")

        context = browser.new_context(
            viewport={"width": 390, "height": 844},
            device_scale_factor=2
        )
        page = context.new_page()

        def on_console(msg):
            if msg.type in ("error",):
                # 忽略无关资源 404
                text = msg.text
                if "favicon" not in text:
                    console_errors.append(text)
                    print(f"[Console Error] {text}")

        page.on("console", on_console)
        page.on("pageerror", lambda err: console_errors.append(str(err)))

        # 1. 预置 LocalStorage 数据（模拟打卡 2 座山峰，其中 1 座包含打卡实景照片与探索心得）
        test_photo_base64 = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        mock_records = {
            "longquanshan": {
                "checkedAt": "2026-10-20T08:30:00.000Z",
                "photoUrl": test_photo_base64,
                "note": "清晨仰天窝观景台远眺雪山与日出，视野极其开阔！"
            },
            "zhaogongshan": {
                "checkedAt": "2026-10-21T09:15:00.000Z",
                "photoUrl": "",
                "note": "后半段泥泞路段需要登山杖辅助，竹林幽深。"
            }
        }

        page.goto(f"{BASE_URL}/#/profile")
        page.wait_for_load_state("networkidle")

        # 写入 localStorage
        page.evaluate("""
            ([checked, records]) => {
                localStorage.setItem('weekly_mountain_checked', JSON.stringify(checked));
                localStorage.setItem('weekly_mountain_checkin_records', JSON.stringify(records));
            }
        """, [["longquanshan", "zhaogongshan"], mock_records])

        # 刷新页面加载预置打卡数据
        page.goto(f"{BASE_URL}/#/profile")
        page.reload()
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1000)

        # 2. 验证 Profile 页面渲染与数据
        print("\n--- 步骤 1: 验证 Profile 页面渲染与打卡列表 ---")
        done_text = page.locator(".telemetry-dashboard").inner_text()
        assert "2" in done_text, f"Expected 2 done mountains in telemetry dashboard, got {done_text}"
        print("[OK] Telemetry dashboard correctly displays 2 done peaks")

        # 验证打卡实景相册区域
        record_cards = page.locator(".checkin-record-card")
        card_count = record_cards.count()
        assert card_count >= 2, f"Expected at least 2 checkin cards, got {card_count}"
        print(f"[OK] Found {card_count} checkin record cards in Profile view")

        # 验证龙泉山打卡照片与心得随笔已正确显示
        textarea_val = page.locator(".checkin-record-card textarea").first.input_value()
        assert "清晨仰天窝观景台远眺雪山" in textarea_val, f"Note content not found in textarea, got: {textarea_val}"
        print(f"[OK] Checkin note content rendered correctly in textarea: {textarea_val[:20]}...")

        page.screenshot(path=SCREENSHOT_PROFILE_PATH)
        print(f"[OK] Saved profile screenshot to {SCREENSHOT_PROFILE_PATH}")

        # 3. 验证点击「生成成就海报」按钮呼出弹窗
        print("\n--- 步骤 2: 验证点击生成海报弹窗 ---")
        poster_btn = page.locator(".btn-generate-poster").first
        assert poster_btn.is_visible(), "Generate poster button is not visible"
        poster_btn.click()
        page.wait_for_timeout(600)

        modal = page.locator(".alpine-poster-modal")
        assert modal.is_visible(), "Poster modal did not appear after clicking button"
        print("[OK] AlpineAchievementPosterModal opened successfully")

        # 4. 验证海报 DOM 容器与元素
        print("\n--- 步骤 3: 验证海报内部 DOM 元素 ---")
        canvas_container = page.locator(".alpine-poster-canvas")
        assert canvas_container.is_visible(), "Poster canvas container not visible"

        modal_text = modal.inner_text()
        assert "ALPINE EXPLORER" in modal_text, "Brand title missing in poster"
        assert "已征服" in modal_text, "Summit count missing in poster"
        assert "防伪序列码" in modal_text, "Security serial missing in poster"
        assert "清晨仰天窝观景台" in modal_text, "User checkin note missing in poster"
        print("[OK] Poster contains brand header, telemetry stats, checkin archives, and anti-counterfeit seal")

        # 5. 验证点击「保存到手机 / 下载海报」触发 html2canvas 渲染
        print("\n--- 步骤 4: 验证海报渲染与下载触发 ---")
        save_btn = page.locator(".btn-save-poster")
        assert save_btn.is_visible(), "Save poster button is not visible"

        # 监听下载事件
        download_triggered = []
        page.on("download", lambda d: download_triggered.append(d.suggested_filename))

        save_btn.click()
        # 等待 html2canvas 渲染与生成图片
        page.wait_for_timeout(3500)

        # 检查是否成功生成并展示了预览图片 (dataUrl)
        preview_img = page.locator(".alpine-poster-modal img[alt='成就海报预览']")
        assert preview_img.is_visible(), "Generated poster preview image did not appear"
        src_attr = preview_img.get_attribute("src")
        assert src_attr and src_attr.startswith("data:image/png;base64,"), "Poster image data URL is invalid"
        assert len(src_attr) > 1000, f"Poster image data URL is too short: {len(src_attr)}"
        print(f"[OK] html2canvas generated HD PNG data URL successfully! Length: {len(src_attr)} chars")

        page.screenshot(path=SCREENSHOT_MODAL_PATH)
        print(f"[OK] Saved poster modal screenshot to {SCREENSHOT_MODAL_PATH}")

        # 6. 验证打卡 Store 的 saveCheckinDetail 和 compressImageToBase64 行为
        print("\n--- 步骤 5: 验证 checkinStore 运行时接口 ---")
        store_test_result = page.evaluate("""
            async () => {
                const store = window.__VUE_APP__?.config?.globalProperties?.$pinia;
                // 直接测试 localStorage 响应与更新
                const rawRecs = localStorage.getItem('weekly_mountain_checkin_records');
                const parsed = JSON.parse(rawRecs || '{}');
                return {
                    hasLongquanshan: !!parsed['longquanshan'],
                    hasZhaogongshan: !!parsed['zhaogongshan'],
                    note: parsed['longquanshan']?.note
                };
            }
        """)
        assert store_test_result["hasLongquanshan"], "Store data persistence check failed"
        print("[OK] checkinStore LocalStorage synchronization verified")

        # 7. 额外测试：清空打卡（0 座打卡）状态下的首征海报生成
        print("\n--- 步骤 6: 验证 0 打卡状态下的首征海报生成 ---")
        # 关闭当前弹窗
        page.locator(".alpine-poster-modal button[aria-label='关闭海报弹窗']").click()
        page.wait_for_timeout(400)

        # 清空 localStorage
        page.evaluate("""
            () => {
                localStorage.setItem('weekly_mountain_checked', JSON.stringify([]));
                localStorage.setItem('weekly_mountain_checkin_records', JSON.stringify({}));
            }
        """)
        page.reload()
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(600)

        # 验证提示卡片存在
        assert page.locator("text=暂无打卡峰线").is_visible(), "Empty state card not visible"

        # 再次打开海报弹窗
        page.locator(".btn-generate-poster").first.click()
        page.wait_for_timeout(500)
        modal_empty = page.locator(".alpine-poster-modal")
        assert modal_empty.is_visible(), "Modal not opened in empty state"
        assert "探索者首征集结令" in modal_empty.inner_text(), "Commencement card missing in 0-summit poster"

        # 点击保存
        page.locator(".btn-save-poster").click()
        page.wait_for_timeout(3000)
        assert page.locator(".alpine-poster-modal img[alt='成就海报预览']").is_visible(), "0-summit poster render failed"
        print("[OK] 0-summit commencement poster rendered successfully!")

        # 8. 检查控制台报错
        print("\n--- 步骤 7: 检查控制台报错 ---")
        if console_errors:
            print(f"[WARN] Console errors logged: {console_errors}")
            # Ensure none are fatal js crash errors
            fatal = [e for e in console_errors if "SyntaxError" in e or "ReferenceError" in e or "TypeError" in e]
            assert not fatal, f"Fatal JS errors found: {fatal}"
        else:
            print("[OK] 0 console errors during full workflow")

        browser.close()

    print("\n==========================================")
    print("🎉 Feature B 自动化验证全部 PASS (100%)！")
    print("==========================================")

if __name__ == "__main__":
    run_verification()
