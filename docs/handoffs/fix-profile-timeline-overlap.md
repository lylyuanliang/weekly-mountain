# 主题：修复真机反馈时间轴圆点与日期文本重叠错位 (fix-profile-timeline-overlap)

- 当前状态：已修复并验证，完成打包发布 (Completed)
- 最后更新时间：2026-10-28
- 关联工单 ID：`1793165588167`
- 恢复入口：`src/components/debug/MobileFeedbackWidget.vue`

## 1. 用户反馈与问题复现
- **来源**：移动端真机公测即时反馈（Xiaomi 15 / Android 16，视口 369 × 821，DPR: 3.25）
- **现象描述**：用户在「进度与历史」面板截图标注反馈“这里错位了”；
- **排查根因**：
  1. 日期分组节点指示圆点使用了硬编码负边距 `class="absolute -left-[5px] top-0.5 ..."`，圆点几何中心位于 `3px`，而垂直时间轴连接线位于 `before:left-[11px]`（几何中心位于 `12px`），导致指示圆点与轴线发生 9px 的严重偏置，甚至在部分机型上被外层滚动容器左边界半裁切；
  2. 时间轴内容区内边距原先较窄（`pl-5` 仅 20px），扣除圆点宽度后仅剩 4px 甚至更窄空间，导致日期文本 `2026-10-28` 的首个字符 `2` 与圆点及其高光光晕发生严重视觉重叠。

## 2. 解决方案与实施代码
在 `src/components/debug/MobileFeedbackWidget.vue` 中进行精准样式重构：
1. **精确轴线居中**：将指示圆点调整为 `left-[4px]`，配合圆点宽度 16px（`w-4`），使其水平几何中心正好为 `4 + 8 = 12px`，与左侧垂直轴线（`before:left-[11px]` + 2px 宽）达成 100% 绝对居中对齐；添加 `z-10` 避免被层叠遮挡；
2. **充分呼吸留白**：将时间轴内容区域内边距提升至 `pl-8 sm:pl-9`（32px），使日期标题文字距离指示圆点右边界保留舒适的 12px 视觉间距，彻底消除文字与圆点的任何交叉碰撞；
3. **轴线连接平滑**：将时间轴垂直连接线的起始顶部设为 `before:top-2`，使其平滑藏于指示圆点内部自然向下延伸至所有工单卡片。

## 3. 自测验证与成果交付
- **Playwright 真机环境渲染测试**：模拟真实移动端视口（369 × 821, DPR: 3.25）生成截图 `scratch/current_history_render.png`，视觉核验指示圆点垂直居中于轴线，与日期文本留白匀称，无任何重叠与裁切；
- **全量 E2E 自动化回归**：运行 `python scratch/test_app_e2e_full.py`，22 项端到端全流程测试 100% 全部通过，零控制台报错；
- **原生 Android 打包**：通过 `pwsh -File scripts/build_app.ps1 -NoPause -NoBump` 自动化生成最新版本 APK：
  - 版本号：`v0.0.1.202610281342` (versionCode: 1793166160)
  - 产物归档：`releases/weekly-mountain-v0.0.1.202610281342-debug.apk` 和 `releases/weekly-mountain-latest-debug.apk`
- **状态回写**：已调用 `scripts/update_feedback_status.py` 将工单 `1793165588167` 状态回写为 `completed` 并附带详细修复说明。
