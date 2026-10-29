# 主题：release-v0.2.0 (正式发版 v0.2.0 里程碑构建与在线更新部署)

- 当前状态：已完成并已推送发布 (Completed & Pushed)
- 最后更新时间：2026-10-29 15:27
- Git 提交：`bf8bd1d` (chore: 发布 v0.2.0 里程碑正式版并完成 Native APK 编译分发)
- Git 标签：`v0.2.0` (已推送到 origin)
- 恢复入口：`docs/handoffs/release-v0.2.0.md`

---

## 1. 目标与背景
将《每周一山 · 成都周边50座山》正式发布为 `v0.2.0` 里程碑版本。
代码已由用户合并至 `main` 分支。
版本核心包括：
- 接入 npm 官方源 `@lylyuanliang/agent-feedback` 闭环体系；
- 彻底根除真机切换 Tab 闪烁与上下跳动缺陷（DOM 多面板 KeepAlive 架构，耗时降至 3~5ms）；
- 移动真机手势防抖与 450ms 穿透门禁；
- Android 原生断点续传流式 OTA 更新与自动安装包清理；
- 51 座高山拓扑与 12 大户外模块完备。

---

## 2. 版本元数据
- 版本号：`0.2.0` (Tag: `v0.2.0`)
- Android 原生版本号 (versionCode)：`1793258285` (单调严格递增，杜绝降级安装报错)
- 产物文件：
  - `releases/weekly-mountain-v0.2.0-release.apk` (28.08 MB, 纯净发布版，剥离 AI 调试工具)
  - `releases/weekly-mountain-latest-release.apk` (28.08 MB, 供发布版在线静默更新镜像)
  - `releases/weekly-mountain-v0.2.0-debug.apk` (28.08 MB, 开发者联调版)
  - `releases/weekly-mountain-latest-debug.apk` (28.08 MB, 供联调版在线静默更新镜像)

---

## 3. 已完成工作与改动文件清单
1. **代码与元数据升版**：
   - `package.json`: version -> `0.2.0`
   - `android/app/build.gradle`: versionName -> `0.2.0`, versionCode -> `1793258285`
   - `src/config/version.js`: APP_VERSION / RELEASE_VERSION -> `0.2.0`, BUILD_CODE -> `1793258285`
   - `public/version.json`: 完整正式发版更新日志与元数据
2. **Android Native APK 构建**：
   - 运行 `pwsh -File scripts/build_app.ps1 -NoPause`，耗时 7s 成功产出 28.08 MB 安装包。
3. **在线更新与分发验证**：
   - 本地 `http://localhost:5173/version.json` 响应 200 (Ver: 0.2.0)
   - 穿透 `https://682d099a.r31.cpolar.top/version.json` 响应 200 (Ver: 0.2.0)
   - 穿透 `https://682d099a.r31.cpolar.top/api/app-update` 响应 200 (Ver: 0.2.0)
   - 穿透 `https://682d099a.r31.cpolar.top/releases/weekly-mountain-latest-debug.apk` 支持 HTTP 206 断点分块续传流式下载。

---

## 4. 自测与验证记录
- **APK 编译**：BUILD SUCCESSFUL in 7s，包含所有 153 个山峰与风景资源。
- **分发路由**：Range header bytes 0-1023 返回 206 Partial Content (Total 29,444,902 字节)。
- **后台守护**：Vite 开发服务器 (`task-9597`) 与静默哨兵 (`task-9320`) 持续健康常驻。
