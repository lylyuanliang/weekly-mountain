# 任务交接与状态记录：移动端版本号时间戳驱动化重构与 App 内部下载打通 (Timestamp Versioning & In-App OTA)

> 规范依据：`AGENTS.md` / `GEMINI.md` 全局规约与任务交接硬门禁

---

## 1. 任务背景与核心目标

### 1.1 背景来源
- **用户指令**：
  > “你打的包没有升版本吗, 你版本号不变化,我app内部怎么下载? 第四位改为时间戳吧, 不采用00x这种格式了”
- **核心痛点**：
  1. 过去版本号第 4 位使用 `00x`（如 `001, 002... 005, 006`）手工维护，容易遗漏递增；
  2. 手机真机已安装旧版本（如 `0.0.1.005`），若打包或远端更新源版本号未提升，在 App 内部检查更新时会判定为“当前已是最新发布版”或“先行体验版”，导致无法出现【立即在线升级】按钮；
  3. Android 原生工程的 `versionCode` 此前固定为整数 `5`，若不提升底层 `versionCode`，真机安装 APK 时可能被 Android 系统拦截并报错 `INSTALL_FAILED_VERSION_DOWNGRADE`。

### 1.2 核心目标
1. **重构版本规范**：彻底废弃 `00x` 格式，第 4 位统一采用时间戳格式 `YYYYMMDDHHmm`（如 `0.0.1.202610281045`）；
2. **多端自动化同步**：编写原子化同步脚本 [`scripts/sync_version.py`](file:///d:/file_save/workspace/github/weekly-mountain/scripts/sync_version.py)，统一对齐 `package.json`、`src/config/version.js`、`public/version.json` 和 `android/app/build.gradle`；
3. **Android 底层 versionCode 升级**：采用单调递增的 Unix 秒级时间戳（`int(time.time())`），确保每次构建均高于上一次，彻底杜绝安装降级限制；
4. **App 内部免跳转下载打通**：
   - 调试弹窗与正式在线升级均优先通过 Android 原生容器 `window.AlpineNative.downloadAndInstallApk` 在 App 内部流式下载与安装，不再跳转外部浏览器；
   - 更新服务纳入活动穿透/局域网候选通道，真机联调时毫秒级拉取最新本地热打包版本；
5. **编译构建与自动化回归**：产出最新 Release / Debug APK，全量 E2E 回归测试验证通过。


---

## 2. 方案落地与实施记录

### 2.1 自动化时间戳版本同步脚本 (`scripts/sync_version.py`)
- 自动生成 `0.0.1.YYYYMMDDHHmm` 时间戳版本号及 Unix 秒级时间戳 `versionCode`；
- 一键原子化同步更新 4 大配置文件：
  1. [`package.json`](file:///d:/file_save/workspace/github/weekly-mountain/package.json): `"version": "0.0.1.202610281045"`
  2. [`src/config/version.js`](file:///d:/file_save/workspace/github/weekly-mountain/src/config/version.js): `APP_VERSION`, `BUILD_DATE`, `BUILD_TIME`, `BUILD_TIMESTAMP`, `BUILD_CODE`
  3. [`public/version.json`](file:///d:/file_save/workspace/github/weekly-mountain/public/version.json): `version`, `versionTag`, `assetName`, `downloadUrl`
  4. [`android/app/build.gradle`](file:///d:/file_save/workspace/github/weekly-mountain/android/app/build.gradle): `versionCode 1793155505`, `versionName "0.0.1.202610281045"`

### 2.2 打包流水线自动升版集成 (`scripts/build_app.ps1`)
- 在 Step 1 前端构建前增加 Step 0.5，默认自动触发 `python scripts/sync_version.py`，保证每次生成的 APK 包自带当前最新时间戳，彻底告别手工编辑；
- 增加 `-NoBump` 开关，支持需要重打同版本时跳过升版；
- 产物自动命名为 `weekly-mountain-v0.0.1.YYYYMMDDHHmm-release.apk`，并同步更新软链镜像 `weekly-mountain-latest-release.apk`。

### 2.3 App 内部流式下载升级打通
- [`src/stores/debugStore.js`](file:///d:/file_save/workspace/github/weekly-mountain/src/stores/debugStore.js): `downloadAndInstallApk` 在 Android 原生环境下优先调用 `window.AlpineNative.downloadAndInstallApk`，实现免跳浏览器、App 内部原生流式下载；
- [`src/services/updateService.js`](file:///d:/file_save/workspace/github/weekly-mountain/src/services/updateService.js): 自动识别 `localStorage` 中的联调穿透/局域网地址 `wm_debug_tunnel_url`，并将其置于优先竞速通道，在本地热打包后手机 App 能毫秒级检测到本地新版本。

### 2.4 全量测试与产物验证
- **全量 E2E 自动化回归测试 (`scratch/test_app_e2e_full.py`)**：100% 通过（地图、点卡联动、详情抽屉、计划排期、个人中心 5 大板块均零报错通过）；
- **全弹窗防穿透测试 (`scratch/verify_modal_scroll_lock.py`)**：100% 通过；
- **产物归档**：
  - Release APK: `releases/weekly-mountain-v0.0.1.202610281045-release.apk` (28.06 MB)
  - Release 镜像: `releases/weekly-mountain-latest-release.apk`
  - Debug APK: `releases/weekly-mountain-v0.0.1.202610281045-debug.apk` (28.69 MB)
  - Debug 镜像: `releases/weekly-mountain-latest-debug.apk`
- **后台服务**：Vite 开发服务器 (`task-4980`) 与反馈哨兵 (`task-5650`) 持续平稳运行中。

### 2.5 工单 `#1793155777033` 处理记录与调试面板流式进度条落地
- **工单诉求**：“现在调试包下载，还是要跳转浏览器，这个能在app内下载吗，可以实现吗”
- **根因分析**：用户当时手机运行的是此前旧版 APK，旧版代码调用 `openExternalUrl` 打开系统浏览器；而最新代码已包含 `window.AlpineNative.downloadAndInstallApk`。
- **进一步增强**：
  - 在 [`src/stores/debugStore.js`](file:///d:/file_save/workspace/github/weekly-mountain/src/stores/debugStore.js) 中加入 `downloadStatus`、`downloadProgress` 监听与取消能力；
  - 在 [`src/components/debug/AlpineDebugModal.vue`](file:///d:/file_save/workspace/github/weekly-mountain/src/components/debug/AlpineDebugModal.vue) 中落地原生流式下载进度条（百分比、速度、取消下载按钮）与状态提示；
  - 自动将 `localhost:5173` 替换为活动的 `tunnelUrl`，彻底杜绝手机端网络隔离导致的无法访问；
  - 同步编译归档最新时间戳版本 `weekly-mountain-v0.0.1.202610281053-release.apk` 与 `weekly-mountain-v0.0.1.202610281053-debug.apk`；
  - 工单状态已置为 `completed`。

### 2.6 APK 安装包自动清理与调试模块崩溃根因修复
- **用户反馈**：
  1. “安装完或升级完成后,安装包要自动清理掉,这个能实现吗”
  2. “调试包是不是给错了, 我现在点击进入调试没反应, 而且也没有ai反馈悬浮按钮了”
- **根因深度诊断与修复**：
  1. **安装包自动清理机制 (100% 达成)**：
     - 在 [`MainActivity.java`](file:///d:/file_save/workspace/github/weekly-mountain/android/app/src/main/java/com/weeklymountain/app/MainActivity.java) 中实现静态安全清理方法 `cleanUpdateApkCache(Context context)`；
     - 触发时机覆盖完整生命周期：
       - `onCreate()`：用户完成安装首次冷启动新 App 时，静默异步清空 `context.getCacheDir()/updates` 目录下的所有 `.apk` 文件；
       - `onResume()`：用户从系统 `PackageInstaller` 界面切回应用时，自动触发异步清理；
       - `downloadAndInstallApk()`：在启动新一轮下载前，预先清理历史残留的更新包释放存储空间；
       - 同时在 `AlpineNativeBridge` 中暴露 `@JavascriptInterface public boolean cleanApkCache()`，供前端 JS 主动清理。
  2. **进入调试没反应 & 缺失 AI 悬浮球根本原因**：
     - 并非给错安装包，而是此前 `debugStore.js` 在 `return` 对象中导出了 `downloadStatus` 与 `downloadProgress`，但未在函数体内通过 `ref()` 定义该变量；
     - 导致运行时抛出 `ReferenceError: downloadStatus is not defined`，导致 `useDebugStore()` 实例化崩溃；
     - 因为 [`AlpineDebugModal.vue`](file:///d:/file_save/workspace/github/weekly-mountain/src/components/debug/AlpineDebugModal.vue) 与 [`MobileFeedbackWidget.vue`](file:///d:/file_save/workspace/github/weekly-mountain/src/components/debug/MobileFeedbackWidget.vue) 均深度依赖 `useDebugStore()`，Vue 组件挂载直接中断报错，导致悬浮球未挂载，个人中心点击「进入调试」因弹窗组件崩溃而无响应；
     - **修复实施**：在 `debugStore.js` 中完整定义响应式 `downloadStatus` 与 `downloadProgress`，接入 `alpine-download-progress` 原生流式事件；调整 `ProfileView.vue` 中 `IS_DEBUG_BUILD` 的 import 顺序；
     - **双变体升级隔离保障**：在 [`src/services/updateService.js`](file:///d:/file_save/workspace/github/weekly-mountain/src/services/updateService.js) 中加入变体自适应路由——当前为调试版时优先拉取 `debugDownloadUrl`，避免调试用户意外被升级至剥离了调试能力的纯净 Release 版。
- **验证结果**：
  - Playwright UI 交互测试：悬浮球正常渲染展示，点击「进入调试」成功拉起调试抽屉，控制台 0 报错；
  - 全量 E2E 自动化回归测试（`scratch/test_app_e2e_full.py`）：100% 全部通过；
  - 生成全新时间戳版本 `weekly-mountain-v0.0.1.202610281126-debug.apk` (28.08 MB) 并同步更新 `weekly-mountain-latest-debug.apk`。

### 2.7 工单 `#1793158626762` 处理记录与“热重载”混淆移除
- **工单诉求**：“这个开启热重载什么意思，我点击后跳转浏览器打开网页版了，这有啥用”
- **根因分析**：
  1. 此前调试面板中保留了面向前端开发者本地联调的“实时穿透热重载”按钮，意图通过 `window.location.href` 将 WebView 切到远程 Vite 穿透地址；
  2. 但因 Capacitor 原生容器拦截外部跨域非 localhost 域名，系统自动调起手机外部浏览器打开，产生体验断层；
  3. 对于移动端公测和内测用户而言，已有更成熟更稳定的【在 App 内重新下载当前最新 APK】全自动免跳转流式 OTA 升级，该按钮不仅鸡肋且极易造成误解。
- **优化实施**：
  1. 在 [`src/components/debug/AlpineDebugModal.vue`](file:///d:/file_save/workspace/github/weekly-mountain/src/components/debug/AlpineDebugModal.vue) 中彻底移除“实时穿透热重载”区块，调试面板精炼为聚焦于“在线更新”与“真机反馈”；
  2. 工单状态已在 [`scratch/mobile_feedback.json`](file:///d:/file_save/workspace/github/weekly-mountain/scratch/mobile_feedback.json) 与 [`scratch/latest_feedback.json`](file:///d:/file_save/workspace/github/weekly-mountain/scratch/latest_feedback.json) 中置为 `completed` 并写入详尽回复；
  3. 编译发布时间戳版本 `0.0.1.202610281139`（`weekly-mountain-v0.0.1.202610281139-debug.apk`）。

---

## 3. 当前交付产物与快速恢复入口

| 产物/资源 | 路径/标识 | 说明 |
| :--- | :--- | :--- |
| **最新调试 APK** | [`releases/weekly-mountain-v0.0.1.202610281139-debug.apk`](file:///d:/file_save/workspace/github/weekly-mountain/releases/weekly-mountain-v0.0.1.202610281139-debug.apk) | 包含 AI 反馈悬浮球、调试弹窗、免跳转流式下载及 APK 自动清理 |
| **最新调试镜像** | [`releases/weekly-mountain-latest-debug.apk`](file:///d:/file_save/workspace/github/weekly-mountain/releases/weekly-mountain-latest-debug.apk) | 供快速分发或在线直链下载 |
| **版本元数据** | [`public/version.json`](file:///d:/file_save/workspace/github/weekly-mountain/public/version.json) | 已对齐版本 `0.0.1.202610281139` (Code: 1793158770) |
| **后台开发服务** | `task-4980` | `http://localhost:5173` 正常服务中 |
| **后台反馈哨兵** | 见最新唤醒任务 | `python scripts/watch_mobile_feedback.py` 静默监听中 |
