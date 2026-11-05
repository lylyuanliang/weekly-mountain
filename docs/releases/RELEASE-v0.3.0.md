<!-- RELEASE_METADATA_START
title: "服务端门禁拦截、远程动态密钥校验与真机双变体联调"
changelog:
  - "【安全门禁】集成 @lylyuanliang/agent-feedback 1.4.0，服务端数据接口全面实施 HTTP 401 鉴权拦截；"
  - "【动态配对】解决独立编译 Debug APK 本地无密钥导致的配对失败，支持端侧向开发机 (/auth/verify) 动态校验并持久化；"
  - "【历史保护】端侧历史面板未授权状态下展示受限遮罩，阻断轮询，严防历史工单与排查日志外泄；"
  - "【开发机直连】本地 scratch/.agent-feedback-secret 零明文下发与防泄露机制，完善 README 开发者联调配对指南；"
  - "【签名固化】固化 Android 原生 debug.keystore 签名配置，消除跨机器覆盖安装签名不一致 (INSTALL_FAILED_UPDATE_INCOMPATIBLE)；"
  - "【流水线硬门禁】隔离 Release (Zero-DCE) 与 Debug (集成哨兵) 双包变体，锁定 20MB 产物体积硬门禁。"
RELEASE_METADATA_END -->

# 版本升级与发布记录 (Release Notes) - v0.3.0

- **主版本线**：v0.3.0
- **当前最新构建**：`0.3.0.202611051055` (Tag: `v0.3.0.202611051055`)
- **发布日期**：2026-11-05
- **适用平台**：Android APK (Release / Debug) & Web H5
- **文档维护规范**：依据项目规约 `docs/releases/` 规范维护，严禁直接平铺在 `docs/` 根目录。

---

## 🌟 本次版本核心主题与摘要 (Highlights)

> **v0.3.0 核心演进：全面落地 Android 原生双变体流水线、签名一致性防御、真机 AI 哨兵直连联调与服务端受限访问门禁。**

1. **安全与鉴权升级 (Security & Access Control)**：
   - 升级集成 `@lylyuanliang/agent-feedback` 1.4.0 核心套件；
   - 服务端所有历史工单读取（`/list`, `/dates`）、反馈提交（`/submit`）及状态写入（`/status`）实施全面 HTTP 401 鉴权拦截，杜绝历史排查日志与敏感信息外泄；
   - 解决 CI/CD 独立编译生成的 Debug APK 密钥不一致问题，支持端侧向开发机（`/auth/verify`）发起动态配对校验并持久化信任；
   - 客户端「历史与进度」面板新增未授权拦截保护层，未授权状态下禁止发起轮询与查询请求；
   - 开发机配对密钥自动落盘至本地未追踪文件 `scratch/.agent-feedback-secret`，运行时仅下发 SHA-256 安全哈希，严守零凭据泄漏红线。

2. **Android 产物流水线与签名防御 (CI/CD & Signing)**：
   - 固化 Android 原生 `debug.keystore` 签名证书与 Gradle 配置，根治不同 CI 构建机器或开发机覆盖安装导致的 `INSTALL_FAILED_UPDATE_INCOMPATIBLE` 签名冲突；
   - 隔离双变体构建：正式发布版（Release）完全剔除调试浮球与诊断代码（Zero-DCE 纯净构建），开发者内测版（Debug）原生内置 AI 哨兵与「📦 本地包」开发机直连面板；
   - 设立 20MB 产物体积硬门禁与 `index.html` 资源解压断言，彻底杜绝 CI 归档残缺 APK 的严重缺陷。

3. **应用内更新状态机与 Web 导航体验优化 (App Experience)**：
   - 修复在线更新弹窗在安装中断或取消后卡死在「您正在使用最新版本」的状态停滞，增设「安装包已就绪」直接安装入口；
   - 微信内置浏览器访问时，增设系统浏览器打开引导卡片，主动指引右上角在浏览器中打开直达高德/百度/腾讯地图导航。

---

## 📝 详细变更清单 (Changelog)

### ✨ 新增特性 (Features)
- **真机联调基地址与密钥配对 (Debug APK)**：在悬浮窗「📦 本地包」面板中支持实时编辑开发机穿透基地址（如 cpolar / ngrok 域名），输入开发机生成的配对密钥一键解锁直连；
- **动态校验 Fallback 探针**：端侧配对在本地静态哈希比对失败时，自动调用开发机 `/api/__agent_feedback/auth/verify` 接口执行远程校验；
- **微信环境一键唤起地图**：针对微信内置浏览器拦截地图 App 唤起协议的痛点，新增轻量级外跳系统浏览器引导。

### 🐛 缺陷修复 (Bug Fixes)
- **修复历史工单匿名泄露**：未输入内测密钥前，端侧历史与进度面板展示受限遮罩，接口直接返回 401，不再暴露历史排查数据；
- **修复 Debug APK 报 `ERR_CONNECTION_REFUSED`**：初始化基地址时放行在原生 Native 容器下先展示编辑面板，允许用户手动填入内网穿透地址后再发请求；
- **修复 Android 覆盖安装降级与签名冲突**：`versionCode` 全面切换为秒级时间戳（Unix Epoch Seconds），并固化签名配置；
- **修复更新状态机死锁**：在 Native 离线下载完成但用户取消安装后，保持安装状态并提示重新安装，避免必须重启 App 的糟糕体验。

### 🔒 安全防护 (Security)
- 遵循零明文泄露规范：无论在客户端代码块、编译产物、日志回显还是 Git 提交中，绝不暴露开发机真实配对秘钥；
- 本地 `scratch/.agent-feedback-secret` 纳入 `.gitignore` 保护。

### 🔧 工程与规范 (Tooling & Architecture)
- 引入 `docs/releases/` 版本升级内容文档体系，规范版本记录；
- 改造 `scripts/sync_version.py` 动态提取版本标题与更新日志，杜绝多版本发布日志硬编码重合；
- 全套版本号采用规范四位格式：`0.3.0.YYYYMMDDHHmm`。

---

## 📦 安装包与分发说明

| 构建版本 | APK 文件名 | 文件大小 | 适用场景说明 |
| :--- | :--- | :--- | :--- |
| **正式发布版 (Release)** | `weekly-mountain-v0.3.0.<timestamp>-release.apk` | 约 27.1 MB | 推荐日常使用：采用 Zero-DCE 纯净精简构建，已剔除调试悬浮球与哨兵诊断模块，启动飞快、性能最优。 |
| **开发者内测版 (Debug)** | `weekly-mountain-v0.3.0.<timestamp>-debug.apk` | 约 29.8 MB | 开发者联调专属：内置真机智能哨兵与开发机直连面板，支持边测边自愈，免除发布等待。 |
