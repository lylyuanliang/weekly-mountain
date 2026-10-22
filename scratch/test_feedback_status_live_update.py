import sys
import os
import time
import shutil
import json
from playwright.sync_api import sync_playwright

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

def main():
    print("[*] 启动 Playwright 验证：无需刷新页面/无需打开弹窗，处理中悬浮按钮自动实时感知完成状态...")
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=True)
        context = browser.new_context(
            viewport={"width": 400, "height": 795},
            device_scale_factor=3,
            is_mobile=True,
            has_touch=True,
            user_agent="Mozilla/5.0 (Linux; Android 16; 24129PN74C Build/BP2A.250605.031.A3; wv) AppleWebKit/537.36 Mobile Safari/537.36"
        )
        page = context.new_page()

        console_errors = []
        page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
        page.on("pageerror", lambda err: console_errors.append(str(err)))

        # Step 1: 确保反馈 #1792588279425 处于 processing 状态
        scratch_dir = "d:/file_save/workspace/github/weekly-mountain/scratch"
        feedback_file = os.path.join(scratch_dir, "mobile_feedback.json")
        with open(feedback_file, "r", encoding="utf-8") as f:
            items = json.load(f)
        for item in items:
            if item.get("id") == 1792588279425 or item.get("timestamp") == 1792588279425:
                item["status"] = "processing"
                item["reply"] = "正在实时排查中..."
        with open(feedback_file, "w", encoding="utf-8") as f:
            json.dump(items, f, ensure_ascii=False, indent=2)

        page.goto("http://localhost:5173/?debug=1", wait_until="domcontentloaded")
        time.sleep(2)

        # 检查初始悬浮按钮：弹窗未打开，处于处理中
        btn = page.locator("button[aria-label='真机调试反馈给 AI']")
        assert btn.is_visible(), "Floating button should be visible"
        btn_text = btn.inner_text().strip()
        print(f"[✓] 初始悬浮按钮文案: '{btn_text}' (弹窗处于关闭状态)")
        assert "处理中" in btn_text, f"Expected button to show '处理中', got '{btn_text}'"

        # Step 2: 服务端将任务标记为 completed，模拟 AI 修复完毕
        print("[*] 模拟后台 AI 完成修复并更新 mobile_feedback.json 为 completed...")
        for item in items:
            if item.get("id") == 1792588279425 or item.get("timestamp") == 1792588279425:
                item["status"] = "completed"
                item["reply"] = "已彻底修复处理中按钮自适应轮询更新！"
        with open(feedback_file, "w", encoding="utf-8") as f:
            json.dump(items, f, ensure_ascii=False, indent=2)

        # Step 3: 不刷新页面、不打开弹窗，等待 4 秒自适应轮询生效
        print("[*] 保持页面静止与弹窗关闭，等待后台自适应轮询生效 (约 3.5~4.5 秒)...")
        time.sleep(4.5)

        # Step 4: 断言悬浮按钮已自动恢复为「反馈给 AI」
        updated_btn_text = btn.inner_text().strip()
        print(f"[✓] 4.5秒后悬浮按钮最新文案: '{updated_btn_text}'")
        assert "反馈给 AI" in updated_btn_text, f"Expected button to auto-update to '反馈给 AI', got '{updated_btn_text}'"
        assert "处理中" not in updated_btn_text, "Active '处理中' state should be completely cleared"
        print("[✓] 验证通过！无需刷新页面，悬浮按钮已自动由【处理中】瞬时切换为【反馈给 AI】！")

        # 截图保存
        shot_path = os.path.join(scratch_dir, "live_status_updated_verified.png")
        page.screenshot(path=shot_path)
        artifact_dir = "C:/Users/lylyu/.gemini/antigravity/brain/94773e75-cfd8-4fb7-87e3-d08b195b9520"
        if os.path.exists(artifact_dir):
            shutil.copy(shot_path, os.path.join(artifact_dir, "live_status_updated_verified.png"))
        print(f"[✓] 截图保存: {shot_path}")

        assert len(console_errors) == 0, f"Expected 0 console errors, got {console_errors}"
        browser.close()
        print("[🎉] 处理中按钮状态自适应实时轮询更新 100% PASS！")

if __name__ == "__main__":
    main()
