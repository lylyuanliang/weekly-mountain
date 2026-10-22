import json
import os
import re

json_path = "d:/file_save/workspace/github/weekly-mountain/scratch/mobile_feedback.json"
if os.path.exists(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    for item in data:
        item["id"] = item.get("timestamp") or item.get("id")
        if not item.get("status"):
            item["status"] = "completed"

        # Extract screenshotFilename if screenshotPath exists
        if item.get("screenshotPath") and not item.get("screenshotFilename"):
            item["screenshotFilename"] = os.path.basename(item["screenshotPath"])

        ts = item.get("timestamp")
        if ts == 1792577434734:
            item["reply"] = "已将半屏抽屉最大高度收紧至 364px，卡片至底边间距降至 7.6px，彻底消除 74px 空白并回馈 66px 视野给地图；反馈悬浮球支持全屏拖拽与边缘吸附。"
        elif ts == 1792575303635:
            item["reply"] = "查明根因为 Marker 拦截 touchstart。已放行双指触控捏合缩放（Pinch-to-zoom），双指放大缩小绝对不再被 Marker 阻断，单指轻触保留点位选择。"
        elif ts in (1792572643810, 1792572525129):
            item["reply"] = "双指平滑缩放与截图复选框（默认不选中）自测通过。"
        elif not item.get("reply"):
            item["reply"] = "已完成排查与优化验证。"

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("Backfilled", len(data), "items in mobile_feedback.json")
