import os
import sys
import json
from datetime import datetime, timezone, timedelta

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

def get_cst_date_str(item):
    ts = item.get("timestamp") or item.get("id")
    if ts and isinstance(ts, (int, float)) and ts > 100000000000:
        tz_cst = timezone(timedelta(hours=8))
        dt = datetime.fromtimestamp(ts / 1000.0, tz=tz_cst)
        return dt.strftime("%Y-%m-%d")

    rec = item.get("receivedAt") or ""
    if rec:
        try:
            clean_rec = rec.replace("Z", "+00:00")
            dt = datetime.fromisoformat(clean_rec)
            tz_cst = timezone(timedelta(hours=8))
            dt_cst = dt.astimezone(tz_cst)
            return dt_cst.strftime("%Y-%m-%d")
        except Exception:
            return rec[:10]

    return datetime.now().strftime("%Y-%m-%d")

def migrate():
    scratch_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scratch")
    feedback_file = os.path.join(scratch_dir, "mobile_feedback.json")
    feedback_dir = os.path.join(scratch_dir, "feedback")
    os.makedirs(feedback_dir, exist_ok=True)

    if not os.path.exists(feedback_file):
        print(f"[!] No mobile_feedback.json found at {feedback_file}")
        return

    with open(feedback_file, "r", encoding="utf-8") as f:
        history = json.load(f)

    print(f"[*] Migrating {len(history)} items into {feedback_dir}...")

    partitions = {}
    for item in history:
        date_str = get_cst_date_str(item)
        if date_str not in partitions:
            partitions[date_str] = []
        partitions[date_str].append(item)

    for date_str, items in partitions.items():
        items.sort(key=lambda x: x.get("timestamp") or x.get("id") or 0, reverse=True)
        out_file = os.path.join(feedback_dir, f"feedback_{date_str}.json")
        with open(out_file, "w", encoding="utf-8") as out_f:
            json.dump(items, out_f, ensure_ascii=False, indent=2)
        print(f"  [OK] {out_file}: {len(items)} items")

    print("[SUCCESS] Feedback migration complete!")

if __name__ == "__main__":
    migrate()
