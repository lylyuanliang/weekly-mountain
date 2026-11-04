# 主题：Web 端与 Native App 平台形态感知与检查更新门禁隔离

- 当前状态：已交付推送 (delivered_and_pushed)
- 最后更新时间：2026-11-04
- 对应提交：`039a6f3` (`feat(platform): 增加 Web 与 Native 运行形态感知，隔离网页端更新检查入口与弹窗`)
- 恢复入口：src/utils/platform.js, src/views/ProfileView.vue, src/App.vue

## 1. 目标与背景
用户将前端 SPA 部署至 Cloudflare Pages (https://weekly-mountain.pages.dev/)。
在 Web 浏览器形态下，网页访问通过页面加载或刷新即可获取最新静态资源，不需要也不应该存在“下载并覆盖安装 APK”的交互，因此：
1. 网页版（桌面浏览器、手机浏览器、微信内置浏览器、PWA 等）不应展示“检查更新”按钮；
2. 网页版启动时不应在后台触发静默检查更新网络请求 (`updateStore.checkForUpdate(true)`)；
3. 检查更新入口与弹窗逻辑仅在 Android 原生 App (Capacitor Native) 环境下展示与生效；
4. 版本号标签在 Web 端自适应展示为 `Web版`，避免混淆用户。

## 2. 核心架构与落地实现
1. **抽象通用平台感知工具模块** [`src/utils/platform.js`](file:///d:/file_save/workspace/github/weekly-mountain/src/utils/platform.js)：
   - `isNativeApp()`：多层防御检测（`window.location.search/hash` 参数模拟 `?native=1`、`Capacitor.isNativePlatform()`、`window.location.protocol === 'capacitor:'`、`window.AlpineNative` 原生注入对象）；
   - `isWebPlatform()`：`!isNativeApp()`；
   - `getPlatform()`：返回 `'android' | 'ios' | 'web'`。
2. **版本元数据自适应扩展** [`src/config/version.js`](file:///d:/file_save/workspace/github/weekly-mountain/src/config/version.js)：
   - 新增 `getVersionLabel()`：在 Web 环境下自动格式化为 `v${RELEASE_VERSION} (Web版)`（开发态为 `(Web Dev)`），在 Native App 环境下保持原生版本标签。
3. **视图层门禁隔离** [`src/views/ProfileView.vue`](file:///d:/file_save/workspace/github/weekly-mountain/src/views/ProfileView.vue)：
   - 个人中心 Section 5 底部“检查更新”按钮增加 `v-if="isNativeAppEnv"`；
   - 版本徽章胶囊绑定 `displayVersionLabel = computed(() => getVersionLabel())`，Web 端居中仅展示 Web 版标识，彻底隐藏更新按钮。
4. **状态与全局弹窗门禁** [`src/App.vue`](file:///d:/file_save/workspace/github/weekly-mountain/src/App.vue) 与 [`src/stores/updateStore.js`](file:///d:/file_save/workspace/github/weekly-mountain/src/stores/updateStore.js)：
   - `App.vue` 中的 `AppUpdateModal` 弹窗仅在 `v-if="isNativeAppEnv"` 时挂载；
   - `App.vue` 启动 2 秒后的静默检查仅在 `if (isNativeAppEnv)` 时执行；
   - `updateStore.checkForUpdate` 内置首道门禁：非原生环境直接拦截并安全返回，杜绝后台无意义网络探测。

## 3. 自测验证与回归结果
1. **定向平台隔离自动化验证** (`scratch/verify_platform_update_gate.py`)：
   - Web 模式访问：`.btn-check-update` 元素数量为 0，底部文本正确包含 `Web` 标签；
   - Native 模拟访问 (`?native=1`)：`.btn-check-update` 正常可见且功能完整；
   - 输出存证截图：`scratch/test_web_profile_no_update_btn.png` 与 `scratch/test_native_profile_with_update_btn.png`。
2. **全量端到端回归测试** (`scratch/test_app_e2e_full.py`)：
   - 探索、轨迹地图、详情页 12 大模块、周计划时间轴、个人中心 5 大核心流程全部 100% 绿灯通过，控制台 0 报错。
3. **Release 纯净构建验证** (`npm run build:release`)：
   - 顺利编译通过，Zero-DCE 自动剔除调试入口。

## 4. 提交信息与推送记录
- 提交哈希：`039a6f3`
- 提交信息：`feat(platform): 增加 Web 与 Native 运行形态感知，隔离网页端更新检查入口与弹窗`
- 远端分支：`origin/main`（已推送至 GitHub，触发 Cloudflare Pages 自动构建）
