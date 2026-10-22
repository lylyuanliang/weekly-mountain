import os
import sys
import json
import argparse
from datetime import datetime

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

def update_status(target_id=None, status="completed", reply=""):
    scratch_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scratch")
    feedback_file = os.path.join(scratch_dir, "mobile_feedback.json")
    latest_file = os.path.join(scratch_dir, "latest_feedback.json")

    if not os.path.exists(feedback_file):
        print(f"[!] 找不到反馈文件: {feedback_file}")
        return False

    with open(feedback_file, "r", encoding="utf-8") as f:
        history = json.load(f)

    if not history:
        print("[!] 反馈历史为空")
        return False

    target_item = None
    if target_id is None:
        target_item = history[0]
        target_id = target_item.get("id") or target_item.get("timestamp")
    else:
        target_id = int(target_id) if str(target_id).isdigit() else target_id
        for item in history:
            if (item.get("id") == target_id) or (item.get("timestamp") == target_id):
                target_item = item
                break

    if not target_item:
        print(f"[!] 未找到 ID 为 {target_id} 的反馈")
        return False

    target_item["status"] = status
    if reply:
        target_item["reply"] = reply
    target_item["updatedAt"] = datetime.now().isoformat()

    with open(feedback_file, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

    # Also update latest_feedback.json if it matches target_id
    if os.path.exists(latest_file):
        try:
            with open(latest_file, "r", encoding="utf-8") as f:
                latest_data = json.load(f)
            if (latest_data.get("id") == target_id) or (latest_data.get("timestamp") == target_id):
                latest_data["status"] = status
                if reply:
                    latest_data["reply"] = reply
                latest_data["updatedAt"] = target_item["updatedAt"]
                with open(latest_file, "w", encoding="utf-8") as f:
                    json.dump(latest_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[*] 更新 latest_feedback.json 警告: {e}")

    print(f"[✓] 已更新反馈 [{target_id}]: 状态 -> {status}, 答复 -> {reply}")
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="更新手机反馈处理进度与答复")
    parser.add_argument("--id", type=str, default=None, help="反馈时间戳ID，默认最新一条")
    parser.add_argument("--status", type=str, default="completed", choices=["pending", "processing", "completed", "rejected", "answered", "explained"], help="状态")
    parser.add_argument("--reply", type=str, default="", help="AI处理进展与答复说明")
    args = parser.parse_args()

    update_status(args.id, args.status, args.reply)
