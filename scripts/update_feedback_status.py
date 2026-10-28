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
    feedback_dir = os.path.join(scratch_dir, "feedback")
    feedback_file = os.path.join(scratch_dir, "mobile_feedback.json")
    latest_file = os.path.join(scratch_dir, "latest_feedback.json")

    # 1. 尝试在分片目录中检索目标工单
    target_item = None
    target_date_file = None

    if os.path.exists(feedback_dir):
        files = sorted([f for f in os.listdir(feedback_dir) if f.startswith("feedback_") and f.endswith(".json")], reverse=True)
        if target_id is None and files:
            # 默认最新一条
            latest_partition = os.path.join(feedback_dir, files[0])
            with open(latest_partition, "r", encoding="utf-8") as f:
                items = json.load(f)
            if items:
                target_item = items[0]
                target_id = target_item.get("id") or target_item.get("timestamp")
                target_date_file = latest_partition
        elif target_id is not None:
            clean_id = int(target_id) if str(target_id).isdigit() else target_id
            for fn in files:
                fpath = os.path.join(feedback_dir, fn)
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        items = json.load(f)
                    for it in items:
                        if (it.get("id") == clean_id) or (it.get("timestamp") == clean_id):
                            target_item = it
                            target_date_file = fpath
                            break
                    if target_item:
                        break
                except Exception:
                    pass

    # 2. 如果在分片目录没找到，回退到 mobile_feedback.json
    if not target_item and os.path.exists(feedback_file):
        with open(feedback_file, "r", encoding="utf-8") as f:
            history = json.load(f)
        if target_id is None and history:
            target_item = history[0]
            target_id = target_item.get("id") or target_item.get("timestamp")
        elif target_id is not None:
            clean_id = int(target_id) if str(target_id).isdigit() else target_id
            for it in history:
                if (it.get("id") == clean_id) or (it.get("timestamp") == clean_id):
                    target_item = it
                    break

    if not target_item:
        print(f"[!] 未找到 ID 为 {target_id} 的工单")
        return False

    now_iso = datetime.now().isoformat()
    target_item["status"] = status
    if reply:
        target_item["reply"] = reply
    target_item["updatedAt"] = now_iso

    # 3. 回写分片文件
    if target_date_file and os.path.exists(target_date_file):
        try:
            with open(target_date_file, "r", encoding="utf-8") as f:
                p_items = json.load(f)
            for it in p_items:
                if (it.get("id") == target_item.get("id")) or (it.get("timestamp") == target_item.get("timestamp")):
                    it["status"] = status
                    if reply:
                        it["reply"] = reply
                    it["updatedAt"] = now_iso
                    break
            with open(target_date_file, "w", encoding="utf-8") as f:
                json.dump(p_items, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[*] 回写分片警告: {e}")

    # 4. 回写 mobile_feedback.json
    if os.path.exists(feedback_file):
        try:
            with open(feedback_file, "r", encoding="utf-8") as f:
                history = json.load(f)
            for it in history:
                if (it.get("id") == target_item.get("id")) or (it.get("timestamp") == target_item.get("timestamp")):
                    it["status"] = status
                    if reply:
                        it["reply"] = reply
                    it["updatedAt"] = now_iso
                    break
            with open(feedback_file, "w", encoding="utf-8") as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[*] 回写 mobile_feedback 警告: {e}")

    # 5. 回写 latest_feedback.json
    if os.path.exists(latest_file):
        try:
            with open(latest_file, "r", encoding="utf-8") as f:
                latest_data = json.load(f)
            if (latest_data.get("id") == target_item.get("id")) or (latest_data.get("timestamp") == target_item.get("timestamp")):
                latest_data["status"] = status
                if reply:
                    latest_data["reply"] = reply
                latest_data["updatedAt"] = now_iso
                with open(latest_file, "w", encoding="utf-8") as f:
                    json.dump(latest_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[*] 回写 latest_feedback 警告: {e}")

    print(f"[OK] 已更新反馈 [{target_id}]: 状态 -> {status}, 答复 -> {reply}")
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="更新手机反馈处理进度与答复")
    parser.add_argument("--id", type=str, default=None, help="反馈时间戳ID，默认最新一条")
    parser.add_argument("--status", type=str, default="completed", choices=["pending", "processing", "completed", "rejected", "answered", "explained"], help="状态")
    parser.add_argument("--reply", type=str, default="", help="AI处理进展与答复说明")
    args = parser.parse_args()

    update_status(args.id, args.status, args.reply)
