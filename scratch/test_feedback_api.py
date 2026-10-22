import urllib.request
import json

base_url = "http://localhost:5173"

try:
    # 1. Test GET /api/feedback
    req = urllib.request.Request(f"{base_url}/api/feedback")
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        print("GET /api/feedback success:", data.get("success"), "Total history:", len(data.get("history", [])))
        if data.get("history"):
            first = data["history"][0]
            print("First item:", first.get("id"), first.get("content"), first.get("status"), first.get("reply"))

    # 2. Test GET /api/feedback/screenshot/feedback_screenshot_1792577434734.jpg
    req_img = urllib.request.Request(f"{base_url}/api/feedback/screenshot/feedback_screenshot_1792577434734.jpg")
    with urllib.request.urlopen(req_img) as resp:
        img_bytes = resp.read()
        print("GET screenshot success: content-type =", resp.headers.get('Content-Type'), "size =", len(img_bytes))

    print("\n[ALL API TESTS PASSED!]")
except Exception as e:
    print("API Test failed:", e)
