# 任务交接与状态记录：工单记录按日期分文件存储与移动端时间轴分页流式展示 (Daily Feedback Partitioning & Timeline UI)

> 规范依据：`AGENTS.md` / `GEMINI.md` 全局规约与任务交接硬门禁

---

## 1. 任务背景与核心目标

### 1.1 背景来源与用户诉求
1. **工单按日期分文件存储**：避免随着工单累积单一 `mobile_feedback.json` 文件体积膨胀、并发读写冲突与查询困难；
2. **手机端时间轴呈现与滚动分页**：
   - 首屏默认仅拉取并展示最新一天的工单（首屏秒开，轻量渲染）；
   - 滚动触底流式分页加载上一天的工单；
   - 每一天的记录带有 Alpine 暗黑高山设计规范的时间轴 UI 标识（垂直贯通连接线、发光指示节点、日期标题）；
3. **统计口径明确分工**：
   - 浮动胶囊角标与弹窗 Header 始终统计**全量同级所有工单总数**；
   - 时间轴每一个日期节点头部明确注明**当天有多少条**（例如 `2026-10-28 · 今天 · 当日共 4 条`）；
4. **工单类型扩展与区分 (新增诉求)**：
   - 数据模型支持 `type: 'agent_notice' | 'user_feedback'`；
   - UI 差异化卡片与徽标（AI 主动通知专属青绿高光卡片与 `smart_toy` 徽章，用户反馈为黑曜石卡片与 `chat_bubble` 徽章）；
5. **就绪通报注入 (新增诉求)**：
   - 完成改造后向今日分片插入一条简略的 `agent_notice` 记录，方便用户在移动端打开立即验证时间轴、当日数量及工单类型区分。

---

## 2. 方案落地与实施记录

### 2.1 数据存储架构按天分片迁移
- 编写并执行迁移脚本 [`scripts/migrate_feedback_partitions.py`](file:///d:/file_save/workspace/github/weekly-mountain/scripts/migrate_feedback_partitions.py)，将既有历史 43 条工单按各自北京时间 (CST) 真实日期无损归档至 `scratch/feedback/`：
  - `feedback_2026-10-28.json`: 3 条（后注入 1 条 notice 增至 4 条）
  - `feedback_2026-10-27.json`: 3 条
  - `feedback_2026-10-26.json`: 4 条
  - `feedback_2026-10-23.json`: 5 条
  - `feedback_2026-10-22.json`: 9 条
  - `feedback_2026-10-21.json`: 19 条
- 保持 `scratch/mobile_feedback.json` 与 `scratch/latest_feedback.json` 同步回写，确保向后兼容。

### 2.2 服务端分片索引与分页 API 重构 (`vite.config.js`)
- `GET /api/feedback`：默认返回全量总数 `totalCount`、可用日期索引 `dates`、最新日期 `currentDate`、最新一天数量 `dailyCount`、当日数据 `items` 及分页指示；
- `GET /api/feedback?date=YYYY-MM-DD`：按需检索指定日期分片文件并下发数据，降低移动端单次传输与解析开销；
- `POST /api/feedback`：提交新工单时支持识别 `type`，自动存入当天分片并同步索引；
- `POST /api/feedback/status`：跨分片检索 ID 并原子化回写状态。

### 2.3 工具链分片支持
- 升级 [`scripts/update_feedback_status.py`](file:///d:/file_save/workspace/github/weekly-mountain/scripts/update_feedback_status.py)，优先在 `scratch/feedback/` 分片中检索工单 ID 并原子化更新，同时同步主文件。

### 2.4 移动端高山时间轴 UI 与滚动分页 (`MobileFeedbackWidget.vue`)
- 在 [`src/components/debug/MobileFeedbackWidget.vue`](file:///d:/file_save/workspace/github/weekly-mountain/src/components/debug/MobileFeedbackWidget.vue) 中落地：
  - 顶部与胶囊：绑定 `totalFeedbackCount`，确保即使分页也始终显示全量总工单数；
  - 骨架与时间轴：每个日期分组使用 `before:absolute before:bg-gradient-to-b` 绘制贯通时间轴竖线，今天节点带有青绿光晕发光圆点，昨天/历史节点采用次级圆点；
  - 当日数量徽标：日期标题旁配有 `当日共 X 条` 独立药丸徽标；
  - 工单类型徽章：
    - `type === 'agent_notice'`: 显示 `AI 主动通知` 青绿高光徽章，卡片边框为 `border-emerald-500/40`，背景带有青绿微光，左侧加粗高光引线；
    - 默认 `user_feedback`: 显示 `用户反馈` 灰度徽章；
  - 分页与触底加载：监听滚动容器 `onHistoryScroll`（距底部 < 50px 自动拉取上一天），底部配有显式“向下滚动或点击加载上一天 (YYYY-MM-DD)”按钮，全量加载完毕后提示已加载全部天数。

### 2.5 插入完成就绪通知工单
- 执行 [`scratch/insert_agent_notice.py`](file:///d:/file_save/workspace/github/weekly-mountain/scratch/insert_agent_notice.py)，在今日分片顶部插入一条 `type: 'agent_notice'`、`status: 'completed'` 的通知记录，内容为功能就绪简报，今日工单总数变为 4 条，全量总数变为 44 条。

---

## 3. 自测验证与成果检验

### 3.1 端到端浏览器自动化验证 (`scratch/test_feedback_timeline.py`)
- 执行 Playwright 真实浏览器模拟移动设备 (390x844)：
  - [x] 浮动胶囊正确显示全局总数：`chat_bubble 反馈给 AI 44`；
  - [x] 弹窗头部正确显示全量统计：`全量: 44 条`；
  - [x] 首屏仅加载今天（2026-10-28），节点显示 `当日共 4 条`；
  - [x] 首条工单清晰渲染 `[AI 主动通知]` 发光徽章与系统升级就绪详情；
  - [x] 点击加载上一天，成功追加渲染 `2026-10-27 昨天` 节点与 `当日共 3 条`，时间轴竖线平滑延展；
  - [x] 零控制台报错与页面异常。
- 自动化快照留存：
  - 首屏时间轴与 AI 主动通知卡片：`C:\Users\lylyu\.gemini\antigravity\brain\66cdabf9-ca17-464c-957c-28b829d5bc91\test_feedback_timeline_with_notice.png`
  - 分页追加上一天后时间轴：`C:\Users\lylyu\.gemini\antigravity\brain\66cdabf9-ca17-464c-957c-28b829d5bc91\test_feedback_timeline_paginated.png`

### 3.2 编译构建与 APK 产物归档
- 执行流水线命令：`pwsh -File scripts/build_app.ps1 -Variant debug -NoPause`
- 版本号原子升级至：`0.0.1.202610281213` (Unix Code: `1793160786`)
- 生成产物：
  - `releases/weekly-mountain-v0.0.1.202610281213-debug.apk` (28.08 MB)
  - `releases/weekly-mountain-latest-debug.apk` (同步镜像，用于 App 内部快速在线下载安装)

---

## 4. 关键疑问解答（针对用户反馈）

1. **安装完或升级完成后，安装包要自动清理掉，能否实现？**
   - **已在原生底层完全实现**：`MainActivity.java` 中设计了 `cleanUpdateApkCache(context)`，分别在应用冷启动 `onCreate()` 以及从系统安装器返回/切回应用 `onResume()` 时自动触发多线程扫描清理，将 `cache/updates/` 下的所有历史 `.apk` 彻底清空，不占用手机存储空间。
2. **为什么点击“进入调试”没反应且没有悬浮球？**
   - **排查定性**：用户此前安装的包为 Release 纯净版 (`weekly-mountain-v0.0.1.202610281053-release.apk`)，根据项目安全红线，Release 变体物理剥离了调试组件 (`AlpineDebugModal` 和 `MobileFeedbackWidget` 置为 null)。
   - **本次已编译最新 Debug APK**（版本 `0.0.1.202610281213`），安装该版本后不仅悬浮球与调试弹窗全功能恢复，且全新按天时间轴、当日数量及 AI 主动通知卡片均已就绪。

---

## 5. 当前状态与恢复入口
- **当前状态**：全部功能开发、测试与 APK 构建已 100% 闭环。
- **后台服务**：
  - Vite 开发服务：正在运行 (`task-4980`, 端口 5173)
  - 反馈监听哨兵：本轮交接回复前重新拉起
