"""
移动端反馈持久化队列管理工具 (Feedback Queue Manager)
用于支持主会话与子代理对真机反馈进行并发拉取、批次调度与状态流转。
"""
import os
import sys
import json
import time

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

SCRATCH_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scratch")
FEEDBACK_FILE = os.path.join(SCRATCH_DIR, "mobile_feedback.json")
LATEST_FILE = os.path.join(SCRATCH_DIR, "latest_feedback.json")
LAST_PROCESSED_FILE = os.path.join(SCRATCH_DIR, "last_processed_feedback.txt")

def load_queue():
    if not os.path.exists(FEEDBACK_FILE):
        return []
    try:
        with open(FEEDBACK_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def save_queue(history):
    with open(FEEDBACK_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def get_pending_feedbacks():
    """获取所有处于排队待处理 (pending) 状态的反馈"""
    queue = load_queue()
    return [item for item in queue if item.get("status") == "pending"]

def get_active_feedbacks():
    """获取所有处于排队或处理中 (pending 或 processing) 状态的反馈"""
    queue = load_queue()
    return [item for item in queue if item.get("status") in ("pending", "processing")]

def update_feedback(target_id, status="completed", reply=""):
    """更新指定反馈的状态与 AI 答复说明"""
    queue = load_queue()
    now_iso = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    target_id = int(target_id) if str(target_id).isdigit() else target_id
    updated_item = None

    for item in queue:
        if item.get("id") == target_id or item.get("timestamp") == target_id:
            item["status"] = status
            if reply:
                item["reply"] = reply
            item["updatedAt"] = now_iso
            updated_item = item
            break

    if updated_item:
        save_queue(queue)
        # 同步更新 latest_feedback.json
        if os.path.exists(LATEST_FILE):
            try:
                with open(LATEST_FILE, "r", encoding="utf-8") as lf:
                    latest = json.load(lf)
                if latest.get("id") == target_id or latest.get("timestamp") == target_id:
                    latest["status"] = status
                    if reply:
                        latest["reply"] = reply
                    latest["updatedAt"] = now_iso
                    with open(LATEST_FILE, "w", encoding="utf-8") as lf:
                        json.dump(latest, lf, ensure_ascii=False, indent=2)
            except Exception:
                pass
        return updated_item
    return None

def update_last_processed(timestamp):
    """更新已处理基准时间戳"""
    with open(LAST_PROCESSED_FILE, "w", encoding="utf-8") as f:
        f.write(str(timestamp))

def drain_queue_summary():
    """睡前扫尾检查门禁：打印当前队列概况，返回是否仍有待处理任务"""
    pending = get_pending_feedbacks()
    active = get_active_feedbacks()
    print(f"[*] 待处理队列扫尾检查: {len(pending)} 条待处理, {len(active)} 条进行中")
    for idx, p in enumerate(pending, 1):
        print(f"    - 排队 [{idx}]: #{p.get('id')} \"{p.get('content')}\"")
    return pending

if __name__ == "__main__":
    drain_queue_summary()
