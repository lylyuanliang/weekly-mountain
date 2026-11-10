# 主题：agent-feedback v1.3.0 通用受限门禁与连接配置升级及每周一山集成

- 当前状态：已完成 (completed)
- 最后更新时间：2026-11-04
- 对应提交：`v0.3.0.202611041610`
- 恢复入口：`packages/` (@lylyuanliang/agent-feedback-*@1.3.0), `src/views/ProfileView.vue`, `src/components/common/AppUpdateModal.vue`, `src/stores/updateStore.js`, `vite.config.js`

## 1. 目标与背景
根据用户要求，完成两大核心任务：
1. **Web 网页端暴露 Android APK 下载与版本选择入口**：
   - 网页版与原生 App 共享统一的 `AppUpdateModal.vue`；
   - 在个人中心版本栏增加「下载 Android App」胶囊按钮；
   - 在底部社区与法律支持矩阵增加常设「下载 Android 客户端」入口；
   - 弹窗适配 Web 环境标题、拉取最新 GitHub Release 双版本（正式发布版 / 内测调试版）、选择调试版时弹出受限警示条，支持直接调起浏览器高速下载。
2. **沉淀通用受限访问控制与穿透配置至 agent-feedback v1.3.0**：
   - `@lylyuanliang/agent-feedback-core`：新增 `AccessControlConfig`、`HostChannelConfig` 等协议与类型定义；
   - `@lylyuanliang/agent-feedback-client`：
     - 原生支持受限安全门禁（未授权时阻断 AI 反馈提交并展示受限提示与宿主GitHub Issues 引导）；
     - 原生提供「⚙️ 联调设置」(Settings) 内置扩展 Tab（自动持久化穿透地址 `apiBase` 与配对秘钥至 `localStorage`，支持一键连通性测试与配对密钥解绑）；
     - 开放宿主渠道配置（`hostChannel.url` / `name` / `description`）；
   - `@lylyuanliang/agent-feedback-vite-plugin`：透传相关配置，安全下发 SHA-256 哈希值；
   - 构建并打包 agent-feedback 各模块产物至 `releases/v1.3.0/` 与宿主 `packages/`。
3. **每周一山对接 v1.3.0 并重新发版**：
   - 依赖升级至 `1.3.0` 并内置在 `packages/` 中，确保 GitHub Actions CI/CD 流水线离线免依赖外部 npm 镜像稳定构建；
   - 彻底删除 `src/components/debug/AlpineDebugExtensionView.vue`，精简 `setupAgentFeedback.js`，无缝接入框架原生安全门禁与设置面板；
   - 运行自动化端到端测试；
   - 同步升级版本号时间戳至 `0.3.0.202611041610`，提交并推送 Git Tag 触发 GitHub Actions 自动重新构建发布新版双 APK。

## 2. 验证结果与交付证据
1. **Web APK 下载入口自测通过**：
   - 执行 `python scratch/test_web_apk_download.py`：
     - 个人中心胶囊按钮 `.btn-download-apk` 正常展示与点击；
     - 底部社区入口 `button:has-text('下载 Android 客户端')` 正常呼出；
     - `AppUpdateModal` 自适应呈现「Android 客户端下载」，双安装包卡片正常展示；
     - 选择调试版时受限警示条即时渲染；
     - 截图留存：`scratch/web_apk_download_modal.png`。
2. **agent-feedback v1.3.0 安全门禁与设置 Tab 自测通过**：
   - 执行 `python scratch/test_feedback_v130_gate.py`：
     - 未授权状态下，AI 反馈 Tab 被受限屏障（Lockout Shield）全面拦截；
     - 宿主 GitHub Issues 直达按钮 `.btn-host-jump` 正常渲染；
     - 原生内置「⚙️ 联调设置」Tab 正常展示，API 穿透基地址与开发者配对密钥即时持久化；
     - 输入开发机生成的配对密钥后点击验证，就地解锁反馈表单；
     - 截图留存：`scratch/v130_lockout_shield.png`、`scratch/v130_unlocked_form.png`。
3. **全项目回归测试通过**：
   - `python scratch/test_app_e2e_full.py`：全流程 5 大模块、51 座山峰、双向联动、路书计划、打卡导出恢复、零控制台错误，100% 绿灯通过；
   - `npm run build:release`：生产环境纯净构建通过，严格保持 100% Zero-DCE 剥离。
4. **版本同步与 Git Tag**：
   - 版本统一对齐至 `0.3.0.202611041610`；
   - 生成 Git Tag `v0.3.0.202611041610`，推送后将由 GitHub Actions 自动化编译正式版与调试版双 APK。
