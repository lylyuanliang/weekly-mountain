import os
import json

def cleanup_test_item(test_prefix):
    scratch_dir = os.path.dirname(os.path.abspath(__file__))
    feedback_file = os.path.join(scratch_dir, "mobile_feedback.json")
    if os.path.exists(feedback_file):
        with open(feedback_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        # remove items matching test_prefix or starting with 自动化自测
        filtered = [
            item for item in data
            if not item.get("content", "").startswith("自动化自测")
            and not (test_prefix and test_prefix in item.get("content", ""))
        ]
        with open(feedback_file, "w", encoding="utf-8") as f:
            json.dump(filtered, f, ensure_ascii=False, indent=2)
        print(f"Cleaned up test submissions from {feedback_file}")
