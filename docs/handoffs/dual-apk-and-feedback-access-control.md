# 主题：双版本 APK 自动构建与反馈访问控制闭环重构

- 当前状态：已全量交付并验证通过 (verified_and_completed)
- 最后更新时间：2026-11-04
- 对应提交：`4c05e12` (`fix(android): 补充 capacitor-cordova-android-plugins 基础工程依赖文件并修正 gitignore`)
- 对应 Tag：`v0.3.0.202611041156` (已推送到远程 GitHub，GitHub Actions 流水线 Run ID: 41784669246 全绿编译发布成功)
- 交付发版地址：[GitHub Release v0.3.0.202611041156](https://github.com/lylyuanliang/weekly-mountain/releases/tag/v0.3.0.202611041156)
- 恢复入口：.github/workflows/build-apk.yml, src/views/ProfileView.vue, src/components/common/AppUpdateModal.vue, src/components/debug/AlpineDebugExtensionView.vue

## 1. 目标与背景
实现双版本发布、安全访问控制、正式渠道沉淀与网络流向解耦：
1. **GitHub Issues 景区常设反馈入口**：在个人中心（ProfileView）增加反馈入口，引导普通用户至 GitHub Issues；
2. **应用内更新弹窗双包选择**：`AppUpdateModal.vue` 提供「正式发布版」与「内测调试版」选择，选择调试版时弹出受限警告提示；
3. **网络流向彻底解耦**：APK 检测与下载统一走 GitHub Releases / 镜像 CDN；调试面板内彻底废除冗余的 APK 本地下载；
4. **调试面板访问控制与自动保存**：穿透地址与授权密钥输入实时自动持久化至 `localStorage`，无有效授权前拦截并引导至 GitHub Issues；
5. **GitHub Actions 自动化流水线**：编写 `.github/workflows/build-apk.yml`，支持 Tag 推送或手动触发自动编译 Debug + Release 双版本 APK 并发布至 GitHub Releases；
6. **工单闭环与通知**：处理历史遗留工单，并在全部任务完成后插入一条工单消息通知用户。

## 2. 核心架构与落地实现
1. **GitHub Issues 反馈矩阵** [`src/views/ProfileView.vue`](file:///d:/file_save/workspace/github/weekly-mountain/src/views/ProfileView.vue)：
   - Section 5 底部与免责声明并列增加「问题反馈 & GitHub」常设胶囊入口，通过 `openExternalUrl` 调起浏览器直达仓库 Issues。
2. **更新弹窗双版本通道与受限警示** [`src/components/common/AppUpdateModal.vue`](file:///d:/file_save/workspace/github/weekly-mountain/src/components/common/AppUpdateModal.vue)：
   - 增加「正式发布版 (推荐)」与「内测调试版」双卡片选择器；
   - 选中「内测调试版」时动态触发黄色高亮警告卡片，明确告知需要开发者密钥；
   - 升级按钮自适应显示 `立即在线升级【正式版/调试版】`。
3. **网络流向彻底解耦与下载分流** [`src/services/updateService.js`](file:///d:/file_save/workspace/github/weekly-mountain/src/services/updateService.js) 与 [`src/stores/updateStore.js`](file:///d:/file_save/workspace/github/weekly-mountain/src/stores/updateStore.js)：
   - `fetchLatestRelease` 同时解析并预置 Release 与 Debug 的 GitHub Releases 原生地址及国内加速镜像地址；
   - `startDownloadAndInstall(variant)` 支持按用户选择的目标变体流式下载对应 APK。
4. **调试面板访问控制与自动持久化** [`src/stores/debugStore.js`](file:///d:/file_save/workspace/github/weekly-mountain/src/stores/debugStore.js) 与 [`src/components/debug/AlpineDebugExtensionView.vue`](file:///d:/file_save/workspace/github/weekly-mountain/src/components/debug/AlpineDebugExtensionView.vue)：
   - 彻底移除面板内冗余的“检查在线更新与下载 APK”模块，解耦业务更新；
   - 增加开发者配对密钥管理与状态判定（`isAuthorized`）；
   - 未授权状态下展示受限保护屏障，引导普通用户至 GitHub Issues；
   - 穿透地址与密钥输入时实时静默持久化到 `localStorage`，下次进入免重复输入。
5. **GitHub Actions 自动化双版本构建** [`.github/workflows/build-apk.yml`](file:///d:/file_save/workspace/github/weekly-mountain/.github/workflows/build-apk.yml)：
   - 监听 `push tags: ['v*']` 与 `workflow_dispatch`；
   - 矩阵式构建 `weekly-mountain-${TAG}-release.apk` (Zero-DCE 纯净版) 与 `weekly-mountain-${TAG}-debug.apk` (含哨兵调试版)；
   - 自动解析 `public/version.json` 抽取日志并生成精美发版正文，挂载附件发布至 GitHub Releases。
6. **工单闭环与交付通知**：
   - 工单 `#1793694581193` 成功更新为 `completed` 并附排查根治说明；
   - 创建新工单 `#1793763933208` 记录全流程完工通知，回写状态为 `completed`。

## 3. 自测验证
- 全量自动化端到端测试 (`scratch/test_app_e2e_full.py`)：100% 绿灯通过；
- 平台隔离测试 (`scratch/verify_platform_update_gate.py`)：100% 绿灯通过；
- 本地构建验证：`npm run build:release` 与 `npm run build` 均编译成功；
- **GitHub Actions 云端流水线实测（Run ID: 41784669246，耗时 3m 48s）**：
  - 根因定位与修复：`android/.gitignore` 误忽略了 `capacitor-cordova-android-plugins/` 目录，导致云端 `cap sync` 时因找不到 `build.gradle` 无法写入 `cordova.variables.gradle`；精准解除忽略并纳入 Git 追踪后根治；
  - 流水线全部 28 个步骤全绿通过（Build Web Release -> Sync -> Compile Android Release APK -> Archive -> Build Web Debug -> Sync -> Compile Android Debug APK -> Archive -> Generate Release Notes -> Publish GitHub Release）；
  - 产物实测验证（HTTP 200 OK）：
    - 正式发布版 (3.94 MB): `https://github.com/lylyuanliang/weekly-mountain/releases/download/v0.3.0.202611041156/weekly-mountain-v0.3.0.202611041156-release.apk`
    - 内测调试版 (3.94 MB): `https://github.com/lylyuanliang/weekly-mountain/releases/download/v0.3.0.202611041156/weekly-mountain-v0.3.0.202611041156-debug.apk`
