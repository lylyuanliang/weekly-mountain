# 主题：全面清理每周一山中 agent-feedback 补丁代码与切换官方原生 API 交接

- 当前状态：已完成 (completed)
- 涉及阶段：
  1. 现状盘点与补丁清理：
     - **补丁 1~4 清理**：彻底重构 [`src/debug/setupAgentFeedback.js`](file:///d:/file_save/workspace/github/weekly-mountain/src/debug/setupAgentFeedback.js)，从 97 行样板补丁精简至 35 行纯净业务扩展代码，直接调用官方推荐的 `initAgentFeedback()` 与 `registerExtensionTab()`，完全移除手动拼接 `window.__AGENT_FEEDBACK_OPTIONS__`、手动调用底层 `setAccessControl` / `setHostChannel`、手动 `syncAccessControlFromServer` 与手写 `DOMContentLoaded` 守候逻辑；
     - **补丁 5 清理**：重构 [`vite.config.js`](file:///d:/file_save/workspace/github/weekly-mountain/vite.config.js)，彻底删除手抄的 35 行 `resolveAccessControlConfig()` 密钥解析与哈希计算函数，删除全局宏 `define: { __WM_ACCESS_CONTROL_CONFIG__ }`，直接采用官方 `agentFeedback({ enableInBuild: true, accessControl: { enabled: true }, ... })` 原生能力托管；
     - **补丁 6 清理**：在 [`src/App.vue`](file:///d:/file_save/workspace/github/weekly-mountain/src/App.vue) 中移除多余的防御性 `await import('@lylyuanliang/agent-feedback-client')`；
     - **孤儿死代码清理**：安全物理删除 [`src/components/debug/MobileFeedbackWidget.vue`](file:///d:/file_save/workspace/github/weekly-mountain/src/components/debug/MobileFeedbackWidget.vue)（61.5KB、2647 行旧代内嵌式死代码，0 引用）。
  2. 验证与产物比对：
     - 执行 `npm run build`：生产构建 100% 成功；
     - 产物校验：`dist/index.html` 自动注入标准 JavaScript 原生配置 `window.__AGENT_FEEDBACK_OPTIONS__`，门禁、`keyHash`、`showSettings: true` 与 `body` 脚本入口均无缝生效；
     - 全量单元与端到端测试：
       - `test_resource_pack_service.js` ➔ 11/11 项通过
       - `test_store_multi_region.js` ➔ 6/6 项通过
       - `test_weather_and_gallery_resilience.js` ➔ 5/5 项通过
       - `test_region_datasets.py` ➔ 5/5 项通过
       - `test_region_pack_builder.py` ➔ 5/5 项通过
       - 全部测试 100% 绿灯通过。
- 恢复入口：
  - `src/debug/setupAgentFeedback.js`
  - `vite.config.js`
  - `src/App.vue`
