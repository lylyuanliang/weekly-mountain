# 任务交接与状态记录：接入独立通用 agent-feedback 服务与定制调试扩展方案 (Integrate Agent Feedback Service)

> 规范依据：`AGENTS.md` / `GEMINI.md` 全局规约与任务交接硬门禁
> 状态：交付完成 (Completed & Verified)
> 分支：`feat/integrate-agent-feedback`

---

## 1. 任务背景与核心目标

为了将《每周一山》成熟的“移动端真机反馈 -> Agent 监听自愈 -> 端侧时间轴进度闭环”能力通用化，已在 `D:\file_save\workspace\github\agent-feedback` 将其剥离为独立的通用公共 SDK（计划后续发 npm）。
本任务的核心目标：
1. **独立分支开发**：在每周一山创建 `feat/integrate-agent-feedback` 分支进行接入；
2. **通用定位与业务隔离**：
   - 坚守 `agent-feedback` 作为纯粹通用开源库的定位，严禁向其侵入任何每周一山专有逻辑；
   - 通过 `agent-feedback` 设计的 **Extension Tabs 插件槽机制**，将每周一山的定制调试与在线更新面板（APK 流式下载、断点续传、穿透诊断）解耦挂载；
3. **能力反哺与双向标准化**：
   - 将日级分片存储架构（`feedback_YYYY-MM-DD.json` + `feedback_index.json`）、流式时间轴 UI（按天分组、发光圆点、条数徽标）、工单类型（`agent_notice` vs `user_feedback`）及 CSS Token 主题系统全部标准化沉淀至 `agent-feedback`；
4. **npm 发包闭环就绪**：
   - 本地打包验证物料无缺失，完成真实端到端集成测试；
5. **哨兵恢复与真机工单自愈**：
   - 接入验证完成后拉起新版哨兵；捕获并实时自愈了手机端反馈“更新之后，历史没有了，能恢复吗”；修复了旧版 App 契约兼容路由并完成工单闭环。

---

## 2. 核心架构与落地成果

### 2.1 通用 SDK 升级成果 (`D:\file_save\workspace\github\agent-feedback`)
- **`@agent-feedback/core`**：扩展 `FeedbackType`、`InAppFeedback`（增加 type 与 date）、日级索引 `FeedbackDateIndex`、扩展槽 `FeedbackExtensionTab`、主题 Token 体系；
- **`@agent-feedback/vite-plugin`**：升级持久化为按天分片落盘，自动迁移兼容旧队列；提供全套标准端点；
- **`@agent-feedback/client`**：Shadow DOM 全面适配 CSS 变量系统；历史视图升级为流式时间轴；开放 `registerExtensionTab(tab)` 规范；
- **`@agent-feedback/sentinel`**：适配分片轮询与防抖唤醒；提供 `notice` 与 `update-status` CLI；
- **单元测试与构建**：全仓 **77/77 个单元测试 100% 绿灯**，`pnpm -r build` 成功输出 `dist`，`pnpm pack` 生成完整发布包。

### 2.2 每周一山接入成果 (`D:\file_save\workspace\github\weekly-mountain`)
- **分支创建**：`feat/integrate-agent-feedback`；
- **依赖接入**：引入本地 `@agent-feedback/*` 系列包；
- **`vite.config.js` 架构重构与旧版 100% 契约保真兼容**：
  - 接入 `agentFeedback({ storageDir: 'scratch/feedback', theme: 'dark', primaryColor: '#4edea3' })`；
  - 保留纯粹的专属 APK 下载服务 `viteApkReleasePlugin()`；
  - **重要修复与保真兼容**：不仅转发请求，更为未升级的旧版手机端 App（如 `v0.0.1.202610281342`）提供包装结构 `{ success: true, totalCount, dates, currentDate, dailyCount, items }` 以及旧版截图下发路由 `/api/feedback/screenshot/*`，确保旧版 App 打开历史也能立刻看到全量 50 条工单！
- **定制调试面板扩展化**：
  - 编写 [`src/components/debug/AlpineDebugExtensionView.vue`](file:///d:/file_save/workspace/github/weekly-mountain/src/components/debug/AlpineDebugExtensionView.vue)，通过内嵌 `<component is="style">` 彻底解决 Shadow DOM 隔离问题；
  - 在 [`src/debug/setupAgentFeedback.js`](file:///d:/file_save/workspace/github/weekly-mountain/src/debug/setupAgentFeedback.js) 中将“穿透通信诊断”和“在线更新（APK 流式下载/切屏续装）”注册为 `🛠️ 联调与更新` Tab；
- **组件精简**：从 `src/App.vue` 剥离旧的内嵌浮窗组件，统一由 `<agent-feedback-widget>` 接管。

---

## 3. 真机工单处理与自愈记录

- **工单 ID**：`1793175462520`
- **提交时间**：`2026-10-28 16:17:42` (来自小米真机 Android 16)
- **反馈内容**：“更新之后，历史没有了，能恢复吗”
- **根因分析**：手机上运行的是旧版安装包（`v0.0.1.202610281342`），其内部组件读取 `/api/feedback` 时要求响应包含 `data.success === true` 的 Object 包装；由于新服务返回的是纯 Array，导致旧版判定失败跳过了历史渲染（底层数据 100% 完好存在）。
- **自愈方案**：在 `vite.config.js` 的前置中间件中，为旧版 `/api/feedback` 和截图路由补充契约保真逻辑，返回符合旧版期望的包装结构。
- **验证与答复**：经本地与网络模拟请求，旧路由恢复返回 `success: true` 与 `totalCount: 50`。已通过 CLI 将工单更新为 `completed` 并写回详细答复。

---

## 4. 恢复与运维入口
- **启动 Vite 开发服务**：`npm run dev`
- **拉起通用哨兵监听**：`npm run sentinel`
- **发布 Agent 系统通知**：`node ../agent-feedback/packages/sentinel/bin/cli.js notice "通知内容" --dir scratch/feedback`
- **更新工单状态**：`node ../agent-feedback/packages/sentinel/bin/cli.js update-status <id> completed "答复说明" --dir scratch/feedback`
