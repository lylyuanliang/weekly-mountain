# 主题：in-app-online-update (基于 GitHub Releases 的应用内无缝在线更新)

- 当前状态：已全部完成落地，全量自动化验证 100% 通过，Release 与 Debug 原生 APK 构建归档就绪
- 最后更新时间：2026-10-27
- 恢复入口：`docs/handoffs/in-app-online-update.md`

---

## 1. 目标与背景
实现《每周一山》移动端（Android）基于 **GitHub Releases** 的正式在线更新闭环：
1. **免翻高速元数据获取**：优先走边缘 CDN / 高速镜像获取最新 Release 信息（版本号、更新日志、产物直链），避免 GitHub API 60次/小时 IP 限流与 CORS 问题；
2. **免翻高速下载通道**：国内公共高可用加速节点优先代理下载（可达 10MB/s+），自动超时降级回退至 GitHub 原链；
3. **应用内原生下载与黑曜石 UI**：黑曜石风格新版本弹窗、应用内实时下载进度条（百分比、速度、字节进度），彻底告别跳浏览器；
4. **原生自动调起安装**：通过 `AlpineNativeBridge` 与 `FileProvider` 发送 `Intent.ACTION_VIEW`，直接唤起系统安装抽屉，一键更新；
5. **正式化解耦**：将原本位于 `debugStore` 的临时代码重构为正规独立模块 `src/services/updateService.js` 与 `src/stores/updateStore.js`，完全纳入 Release 构建（不受 DCE 剔除）。

---

## 2. 核心架构与方案决策
- **多源版本探测与防封机制**：
  - 首选通道：`https://cdn.jsdelivr.net/gh/lylyuanliang/weekly-mountain@main/public/version.json`（全局无鉴权、无限流、国内极速）；
  - 备用通道：`https://ghfast.top/https://raw.githubusercontent.com/.../public/version.json`；
  - 兜底通道：`https://cdn.jsdelivr.net/gh/.../package.json`；
  - 本地同源通道：`/version.json`（开发与本地测试快速命中）。
- **国内免翻高速代理机制**：
  - 自动为下载地址追加 `https://ghfast.top/` 加速前缀，国内手机可达 10MB/s+ 跑满带宽。
- **Android 原生安装闭环**：
  - `AndroidManifest.xml`：配置 `<uses-permission android:name="android.permission.REQUEST_INSTALL_PACKAGES" />`；
  - `MainActivity.java`：在 `AlpineNativeBridge` 中增加 `downloadAndInstallApk`、`cancelDownload`、`openInstallPermissionSettings`；
  - 流式写入私有缓存目录 `context.getCacheDir() / "updates/weekly-mountain-v*.apk"`；
  - 实时通过 `evaluateJavascript` 触发 `window.onAlpineDownloadProgress` 回传下载百分比与速率；
  - 下载完成后通过 `FileProvider` 构造 `content://` URI，使用 `Intent.ACTION_VIEW` 调起 Android 原生安装器；
  - 若遇未授权未知应用安装，自动安全引导跳转至系统设置授权。
- **UI 与视图层**：
  - `AppUpdateModal.vue`：黑曜石风格多状态弹窗（新版本提示、下载进度条、唤起安装、权限引导、错误重试、当前已是最新版）；
  - `ProfileView.vue`：Section 5 版本信息旁新增「检查更新」按钮与新版本红点指示；
  - `App.vue`：启动 2 秒后在后台静默检测，发现更新时标记红点，不强弹打扰用户。

---

## 3. 完成清单与修改文件
1. **Android 原生配置与 Java Bridge 扩展**：
   - `android/app/src/main/AndroidManifest.xml`（增加未知应用安装权限）
   - `android/app/src/main/java/com/weeklymountain/app/MainActivity.java`（新增流式下载、进度回调与原生安装逻辑）
2. **前端服务与状态管理**：
   - `public/version.json`（版本元数据文件）
   - `src/services/updateService.js`（多通道版本探测、版本语义对比、字节格式化、加速链接拼装）
   - `src/stores/updateStore.js`（全局更新状态、原生事件监听、模拟与调试钩子）
3. **UI 弹窗与页面入口**：
   - `src/components/common/AppUpdateModal.vue`（高山黑曜石更新弹窗）
   - `src/views/ProfileView.vue`（个人中心「检查更新」按钮）
   - `src/App.vue`（顶层挂载与启动静默检测）
4. **移动端实拍图优化（闭环手机端工单 #1793092200344）**：
   - `assets/mountains/hongkou-gaoyuan.jpg`（替换为高清龙门山脉白沙河高山峡谷实拍大图）
   - `assets/mountains/hongkou-gaoyuan-2.jpg`（河谷戏水去水印优化）
   - `assets/mountains/hongkou-gaoyuan-3.jpg`（森林步道去水印优化）

---

## 4. 验证结果
- `node test`: PASS (版本语义对比与字节换算 100% 正确)
- `node test fetch`: PASS (302 探针与版本解析正常)
- `gradlew compileDebugJavaWithJavac`: BUILD SUCCESSFUL (Java 编译 0 错误)
- `npm run build:release`: BUILD SUCCESSFUL (81 modules transformed, 3.57s)
- `python scratch/verify_in_app_update_flow.py`: PASS (100% 全部 5 个步骤通过，已截取黑曜石下载进度面板截图 `scratch/test_in_app_update_modal.png`)
- `python scratch/verify_apk_security.py`: PASS (0 敏感私有泄露)
- APK 归档：
  - `releases/weekly-mountain-v0.0.1.005-release.apk` (28.39 MB，正式纯净发布版，包含全新在线升级闭环)
  - `releases/weekly-mountain-v0.0.1.005-debug.apk` (29.02 MB)

---

## 5. 待办与恢复
- 恢复入口：`npm run dev` (访问 http://localhost:5173/)，后台静默反馈监听哨兵 `python scripts/watch_mobile_feedback.py` 持续运行中。
