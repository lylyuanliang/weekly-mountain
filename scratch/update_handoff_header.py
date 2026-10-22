import re

with open('docs/handoffs/app-modular-redesign.md', 'r', encoding='utf-8') as f:
    text = f.read()

# Replace from "- 当前状态：" until "## 2. 完成的工作"
pattern = r"- 当前状态：.*?## 2\. 完成的工作"
new_content = """- 当前状态：正在实现「多反馈并发收集、防抖聚合与待处理队列池驱动」系统（解决用户在手机端短时间内连续提交多条反馈时的自动防抖收集、队列化排队展示、主会话睡前扫尾清空与子代理派发调度能力）
- 最后更新时间：2026-10-21
- 恢复入口：`npm run dev` (访问 http://localhost:5173/)，静默反馈监听 `python scripts/watch_mobile_feedback.py`

## 1. 当前目标
1. 落地手机端「多反馈并发排队与调度管理」系统：
   - 升级 `scripts/watch_mobile_feedback.py`：实现 10 秒静默收集防抖窗口（Debounce Window），用户短时间连发多条反馈时自动聚合为一个批次，一次性唤醒主会话；
   - 升级 `vite.config.js` 与服务端队列：所有 `status === 'pending'` 反馈按序列入持久化队列，手机端排队徽章动态显示当前排队位次；
   - 强化主会话「睡前扫尾检查（Drain Queue Before Sleep）」门禁：主会话在自测通过后，检查队列若仍有 pending 项，无缝继续处理直到全部清空，杜绝临界漏单；
   - 引入子代理（Subagent）并发调度判定：对收集到的多条反馈分析文件依赖，解耦任务派发子代理并发处理，耦合任务由主会话串行处理；
2. 保持生产打包 M 档达标与自动化自测 100% 覆盖。

## 2. 完成的工作"""

updated = re.sub(pattern, new_content, text, flags=re.DOTALL)
with open('docs/handoffs/app-modular-redesign.md', 'w', encoding='utf-8') as f:
    f.write(updated)
print("Updated handoff header cleanly")
