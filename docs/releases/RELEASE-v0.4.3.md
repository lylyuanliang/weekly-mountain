<!-- RELEASE_METADATA_START
title: "v0.4.3"
changelog:
  - "【依赖升级】升级 @lylyuanliang/agent-feedback 全家桶至 v1.5.0 最新规范版本；"
  - "【补丁彻底清理】全面移除宿主工程历史过渡补丁，彻底拥抱 agent-feedback 官方标准原生 API；"
  - "【工程极致瘦身】物理删除 61.5KB 早期孤儿组件 MobileFeedbackWidget.vue，精简 vite.config.js 45 行手抄密钥逻辑；"
  - "【地域状态韧性修复】修复多地域切换与页面刷新时的状态持久化自愈，优化画册资源未就绪时的平滑降级。"
RELEASE_METADATA_END -->

> [!WARNING]
> **【历史版本技术存档说明】**
> 本 Release 记录及对应构建产物仅作为软件工程研发历史技术存档，**不反映当前自然地理环境、气象灾害与属地管制政策的动态认知，严禁作为户外出行依据**。请始终以项目最新主分支（`main`）中包含的最新风险警示为准。

# 版本升级与发布记录 (Release Notes) - v0.4.3

- **主版本线**：v0.4.3 (agent-feedback v1.5.0 接入、历史补丁彻底清理与地域状态韧性修复)
- **发布日期**：2026-11-19
- **适用平台**：Android APK (Release / Debug) & Web H5
- **文档维护规范**：依据项目规约集中维护在 `docs/releases/` 目录。

---

## 🌟 本次版本核心主题与摘要 (Highlights)

> **v0.4.3 核心演进：全面拥抱 `@lylyuanliang/agent-feedback` v1.5.0 官方原生生态，彻底清理每周一山宿主工程中残留的 6 处早期给反馈组件“打补丁”的代码，安全删除 61.5KB 早期孤儿文件；同步加固多地域持久化与画册降级渲染机制。**

1. **全面接入 `agent-feedback` v1.5.0 官方原生能力**：
   - 全量升级 `@lylyuanliang/agent-feedback-client`、`@lylyuanliang/agent-feedback-vite-plugin` 等核心依赖至 `^1.5.0`；
   - 彻底废除手拼 `window.__AGENT_FEEDBACK_OPTIONS__` 的补丁写法，统一使用官方推荐的标准 API `initAgentFeedback()` 与 `registerExtensionTab()`。

2. **工程瘦身与打补丁代码彻底归零 (Workarounds Zeroing)**：
   - 物理删除 2,647 行、61.5KB 的历史遗留组件 [`src/components/debug/MobileFeedbackWidget.vue`](file:///d:/file_save/workspace/github/weekly-mountain/src/components/debug/MobileFeedbackWidget.vue)；
   - 彻底清理 [`vite.config.js`](file:///d:/file_save/workspace/github/weekly-mountain/vite.config.js) 中 45 行手抄的 `resolveAccessControlConfig()` 密钥解析与全局宏下发，直接采用插件的 `enableInBuild: true` 原生能力；
   - 移除 [`src/App.vue`](file:///d:/file_save/workspace/github/weekly-mountain/src/App.vue) 中防御性重复异步加载代码。

3. **地域切换与画册降级自愈 (Region Resilience)**：
   - 修复多地域（重庆/成都）切换后页面刷新时的持久化与标杆名山热挂载机制；
   - 优化画册离线包未下载时的本地高斯模糊与暗黑高山纯色优雅降级。

---

## 📝 详细变更清单 (Changelog)

### 🛠️ 智能体反馈与开发者工具 (Agent Feedback & Dev Tools)
- **客户端容器标准重构**：在 [`src/debug/setupAgentFeedback.js`](file:///d:/file_save/workspace/github/weekly-mountain/src/debug/setupAgentFeedback.js) 中直接调用 `initAgentFeedback` 与 `registerExtensionTab`，移除全部补丁；
- **Vite 构建插件原生接入**：在 [`vite.config.js`](file:///d:/file_save/workspace/github/weekly-mountain/vite.config.js) 中启用 `agentFeedback({ enableInBuild: true, accessControl: { enabled: true } })`；
- **组件清理**：删除废弃的 [`src/components/debug/MobileFeedbackWidget.vue`](file:///d:/file_save/workspace/github/weekly-mountain/src/components/debug/MobileFeedbackWidget.vue)；
- **依赖升级**：在 [`package.json`](file:///d:/file_save/workspace/github/weekly-mountain/package.json) 中将 `@lylyuanliang/agent-feedback-*` 全套依赖升级至 `^1.5.0`。
