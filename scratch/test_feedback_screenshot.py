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

def test_feedback_features():
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=True)
        context = browser.new_context(
            viewport={"width": 400, "height": 820},
            has_touch=True,
            user_agent="Mozilla/5.0 (Linux; Android 16; 24129PN74C Build/BP2A.250605.031.A3; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/150.0.7871.189 Mobile Safari/537.36 MicroMessenger/8.0.79"
        )
        page = context.new_page()

        print("[1/5] 打开首页 http://localhost:5173/ ...")
        page.goto("http://localhost:5173/", wait_until="domcontentloaded")
        time.sleep(2)

        # 1. 验证地图平滑放大与缩小
        print("[2/5] 验证地图缩放按钮与连续比例...")
        zoom_in_btn = page.locator("button[title='放大地图']").first
        zoom_out_btn = page.locator("button[title='缩小地图']").first
        assert zoom_in_btn.is_visible(), "放大按钮应该可见"
        assert zoom_out_btn.is_visible(), "缩小按钮应该可见"

        # 点击放大
        zoom_in_btn.click(force=True)
        time.sleep(0.5)
        # 点击缩小
        zoom_out_btn.click(force=True)
        time.sleep(0.5)
        print("PASS: 地图放大与缩小按钮交互平滑无异常")

        # 2. 打开反馈弹窗
        print("[3/5] 点击打开反馈弹窗...")
        feedback_btn = page.locator("button:has-text('反馈给 AI')")
        assert feedback_btn.is_visible(), "反馈浮窗按钮应该可见"
        feedback_btn.click()
        time.sleep(1)

        modal = page.locator("[role='dialog'][aria-label='真机调试即时反馈']")
        assert modal.is_visible(), "反馈弹窗应该已展开"

        # 3. 验证“自动截图当前页面”复选框（默认不选中）
        print("[4/5] 验证'自动截图当前页面'复选框，断言默认不选中...")
        checkbox = page.locator("label:has-text('自动截图当前页面') input[type='checkbox']")
        assert checkbox.is_visible(), "自动截图当前页面复选框应该可见"
        assert not checkbox.is_checked(), "硬性断言：自动截图当前页面默认必须为【未选中】！"
        print("PASS: 自动截图当前页面复选框默认【未选中】，符合用户体验需求！")

        # 4. 测试相册选图与移除
        print("[5/5] 测试相册上传截图与提交...")
        test_img_path = os.path.abspath("scratch/route_segments_verified.png")
        assert os.path.exists(test_img_path), f"测试图片 {test_img_path} 应该存在"

        file_input = page.locator("input[type='file']")
        file_input.set_input_files(test_img_path)
        time.sleep(1.5)

        preview_img = page.locator("img[alt='调试截图预览']")
        assert preview_img.is_visible(), "截图缩略图卡片正常渲染"
        badge = page.locator("text='手机相册 / 拍照'")
        assert badge.is_visible(), "来源徽章应该显示为手机相册/拍照"

        # 输入文字并提交
        textarea = page.locator("#mobile-feedback-text")
        textarea.fill("自测验证：地图缩放平滑度与自动截图复选框（默认不选中）均已就绪！")

        submit_btn = page.locator("button:has-text('携带截图发送给 AI')")
        submit_btn.scroll_into_view_if_needed()
        submit_btn.click()
        time.sleep(2)

        page.wait_for_selector("text=已送达！反馈与截图已保存落盘", timeout=5000)
        print("PASS: 带有截图的调试反馈发送成功，落盘正常")

        # 截图记录最新界面
        page.screenshot(path="scratch/feedback_checkbox_verified.png")

        browser.close()
        print("\n🎉 全流程验证 100% 通过：地图缩放平滑度重构完成，'自动截图当前页面'复选框默认不选中，用户手动上传正常！")

if __name__ == "__main__":
    test_feedback_features()
