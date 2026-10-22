import re

with open('docs/handoffs/app-modular-redesign.md', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Update current status
text = re.sub(
    r"- 当前状态：.*?\n",
    "- 当前状态：已全量落地「多反馈并发排队与智能防抖收集系统」，支持 10s 连发防抖收集、队列位次动态展示、新建反馈友好排队提示、悬浮球排队总数感知、主会话睡前扫尾检查与子代理并发调度判定\n",
    text
)

# 2. Add Item 16 before ## 3. 关键决策
item16 = """16. **手机端「多反馈并发排队与智能防抖收集系统」全量落地**：
    - **10 秒连击防抖收集窗口 (Debounce Window)**：
      - 升级 `scripts/watch_mobile_feedback.py`，检测到第 1 条新反馈后自动进入 10s 收集倒计时，若用户在此期间补发截图或连发文字，哨兵自动聚合为一个多反馈批次（Batch），收集完成后一次性唤醒 AI 主会话，杜绝高频碎片化打断；
    - **移动端持久化队列排队与位次动态感知**：
      - 在 `MobileFeedbackWidget.vue` 历史列表中，为排队中的反馈动态计算并展示位次徽章：`排队待处理 (第 N 位)`；
      - 在新建反馈界面中，检测到已有任务在执行时自动弹出友好横幅：`当前有 N 条反馈正在排队处理中，新提交将自动加入队列`，彻底消除用户顾虑；
      - 悬浮球根据队列状态动态展示 `处理中 (N排队)`，实时感知后台负荷；
    - **主会话睡前扫尾检查门禁 (Drain Queue Before Sleep)**：
      - 封装 `scripts/feedback_queue.py` 队列管理器，主会话在每次修复自测完毕后，必须先检查池中是否仍有处理期间新提交的 `pending` 反馈；只有当待处理队列完全清空为 0 时，才重新拉起哨兵休眠；若仍有排队项，直接连贯处理，从根本上杜绝临界时间窗口（Race Condition）漏单；
    - **自动化端到端流转验证**：
      - 编写 Playwright 脚本 `scratch/test_multi_feedback_queue.py`，模拟真机连续提交两条反馈，验证排队横幅弹出、队列位次计算、悬浮球文案与清除机制，自测 100% PASS。

"""

if "16. **手机端「多反馈并发排队与智能防抖收集系统」全量落地**" not in text:
    text = text.replace("## 3. 关键决策", item16 + "## 3. 关键决策")

# 3. Add test result
test_line = "- `python scratch/test_multi_feedback_queue.py`: PASS (多反馈并发提交、排队位次显示、浮窗动态感知、扫尾检查 100% 通过)\n"
if "test_multi_feedback_queue.py" not in text:
    text = text.replace(
        "- `python scripts/package_deploy.py`: PASS",
        test_line + "- `python scripts/package_deploy.py`: PASS"
    )

with open('docs/handoffs/app-modular-redesign.md', 'w', encoding='utf-8') as f:
    f.write(text)

print("Handoff document updated successfully with Item 16")
