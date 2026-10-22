"""
静默智能哨兵脚本：监听手机端实时调试反馈 (支持多反馈防抖收集与队列化聚合)
- 当无新反馈时：0% CPU，保持静默休眠，不消耗任何大模型 Token，不触发会话唤醒。
- 当手机端提交第 1 条新反馈时：启动 10 秒防抖收集窗口 (Debounce Window)，自动合并此期间连发的多条补充反馈。
- 收集窗口结束后：输出结构化批次摘要并退出，触发 Antigravity 响应式自动唤醒。
"""
import os
import sys
import time
import json

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

WORKSPACE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRATCH_DIR = os.path.join(WORKSPACE_DIR, "scratch")
FEEDBACK_FILE = os.path.join(SCRATCH_DIR, "latest_feedback.json")
LAST_PROCESSED_FILE = os.path.join(SCRATCH_DIR, "last_processed_feedback.txt")
HISTORY_FILE = os.path.join(SCRATCH_DIR, "mobile_feedback.json")

DEBOUNCE_SECONDS = 10  # 连发收集缓冲窗口秒数

def get_last_processed_timestamp():
    if not os.path.exists(LAST_PROCESSED_FILE):
        return 0
    try:
        with open(LAST_PROCESSED_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
            return int(content) if content.isdigit() else 0
    except Exception:
        return 0

def main():
    last_processed = get_last_processed_timestamp()
    print(f"[*] 移动端多反馈智能哨兵已启动... 基准时间戳: {last_processed}")
    print(f"[*] 正在静默监听中 (无新反馈时不唤醒；检测到提交时启动 {DEBOUNCE_SECONDS}s 防抖收集)...")
    sys.stdout.flush()

    while True:
        try:
            if os.path.exists(HISTORY_FILE):
                with open(HISTORY_FILE, "r", encoding="utf-8") as hf:
                    history = json.load(hf)

                # 寻找所有时间戳大于基准且状态为 pending 的新反馈
                new_pending = [
                    item for item in history
                    if (item.get("timestamp", 0) > last_processed or item.get("id", 0) > last_processed)
                    and item.get("status") in ("pending", None)
                ]

                if new_pending:
                    print(f"\n[*] 📥 捕获到新反馈，启动 {DEBOUNCE_SECONDS} 秒防抖收集窗口 (等待可能的连发补充)...")
                    sys.stdout.flush()

                    # 开启 10 秒收集倒计时
                    start_time = time.time()
                    while time.time() - start_time < DEBOUNCE_SECONDS:
                        time.sleep(1.5)
                        try:
                            with open(HISTORY_FILE, "r", encoding="utf-8") as hf2:
                                h2 = json.load(hf2)
                            cur_pending = [
                                item for item in h2
                                if (item.get("timestamp", 0) > last_processed or item.get("id", 0) > last_processed)
                                and item.get("status") in ("pending", None)
                            ]
                            if len(cur_pending) > len(new_pending):
                                print(f"[*] ➕ 窗口内又收到新提交，当前聚合批次数量: {len(cur_pending)} 条...")
                                sys.stdout.flush()
                                new_pending = cur_pending
                        except Exception:
                            pass

                    # 收集完毕，将这批反馈全部标记为 processing
                    now_iso = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
                    for item in history:
                        for np in new_pending:
                            if item.get("id") == np.get("id") or item.get("timestamp") == np.get("timestamp"):
                                item["status"] = "processing"
                                item["reply"] = f"AI 智能体已被自动唤醒，已聚合批次 (共 {len(new_pending)} 条反馈)，正在分析排查..."
                                item["updatedAt"] = now_iso

                    with open(HISTORY_FILE, "w", encoding="utf-8") as hf:
                        json.dump(history, hf, ensure_ascii=False, indent=2)

                    # 同步更新 latest_feedback.json
                    if os.path.exists(FEEDBACK_FILE):
                        try:
                            with open(FEEDBACK_FILE, "r", encoding="utf-8") as ff:
                                ldata = json.load(ff)
                            ldata["status"] = "processing"
                            ldata["reply"] = f"AI 智能体已被自动唤醒，已聚合批次 (共 {len(new_pending)} 条反馈)，正在分析排查..."
                            ldata["updatedAt"] = now_iso
                            with open(FEEDBACK_FILE, "w", encoding="utf-8") as ff:
                                json.dump(ldata, ff, ensure_ascii=False, indent=2)
                        except Exception:
                            pass

                    print("\n===========================================================")
                    print(f"🔔 [防抖收集完毕！共聚合 {len(new_pending)} 条反馈，唤醒 AI 主会话]")
                    print("⚠️ 【远程无人值守协作守则 (AGENTS.md / GEMINI.md)】：")
                    print("  1. 用户当前处于移动端公测/离线状态，严禁在 IDE 中挂起提问！")
                    print("  2. 请基于安全默认值自主推进修复，并将决策与结果写回反馈 reply；")
                    print("  3. 修复验证完成后，必须在回复用户前重新拉起哨兵进程！")
                    print("-----------------------------------------------------------")
                    for idx, fb in enumerate(reversed(new_pending), 1):
                        print(f"  [{idx}] 时间: {fb.get('receivedAt', '')} | 页面: {fb.get('state', {}).get('route', '')}")
                        print(f"      内容: \"{fb.get('content', '')}\"")
                        if fb.get('screenshotPath'):
                            print(f"      截图: {fb.get('screenshotPath')} ({fb.get('screenshotSizeKb', 0)} KB)")
                    print("===========================================================\n")
                    sys.stdout.flush()

                    # 退出以触发 Antigravity 响应式自动唤醒
                    sys.exit(0)
        except Exception as e:
            # 容错：文件正在被写入等情况时跳过本次循环
            pass

        time.sleep(2)

if __name__ == "__main__":
    main()
