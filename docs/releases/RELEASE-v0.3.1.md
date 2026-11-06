<!-- RELEASE_METADATA_START
title: "v0.3.1"
changelog:
  - "【渲染修复】修复高山详情页民俗环保、备选撤退与装备建议直接显示原始 JSON 数组的排版缺陷；"
  - "【防篡改校验】引入 APK 安装包 SHA-256 原生双向防篡改校验，彻底杜绝第三方加速镜像篡改与传输损坏；"
  - "【真机配对自愈】修复真机反馈在重启或更新后需手动点击测试连通性才能唤醒已配对状态的时序问题；"
  - "【客观实测基准】全线高程走势图与打卡序列措辞去行政化，全面替换核准字样为客观实测航迹基准；"
  - "【规范固化】固化向 GitHub 自动化构建发版必须递增第3位(Patch)的项目智能体规约。"
RELEASE_METADATA_END -->

> [!WARNING]
> **【历史版本技术存档说明】**
> 本 Release 记录及对应构建产物仅作为软件工程研发历史技术存档，**不反映当前自然地理环境、气象灾害与属地管制政策的动态认知，严禁作为户外出行依据**。请始终以项目最新主分支（`main`）中包含的最新风险警示为准。

# 版本升级与发布记录 (Release Notes) - v0.3.1

- **主版本线**：v0.3.1 (Patch 维护版本)
- **发布日期**：2026-11-06
- **适用平台**：Android APK (Release / Debug) & Web H5
- **文档维护规范**：依据项目规约 `docs/releases/` 规范维护，集中维护在 `docs/releases/` 专属子目录。

---

## 🌟 本次版本核心主题与摘要 (Highlights)

> **v0.3.1 核心演进：全面落地 APK 原生 SHA-256 双向防篡改校验、详情页数组渲染优雅降级修复、真机配对自愈、去行政化客观航迹基准表述与发版规约精简固化。**

1. **高山详情页数组排版缺陷修复 (UI/UX Bugfix)**：
   - 彻底修复 `local_tips`（民俗环保/避坑指南）、`plan_b`（下撤路线/备选方案）及 `gear_detail`（装备建议清单）在 Vue 模板中直接插值导致显示原始 JSON 数组 `[ "...", "..." ]` 的缺陷；
   - 升级为黑曜石高山风格的结构化卡片与圆点列表排版（Alpine List Cards），支持字符串与数组数据类型的自动优雅降级，视觉层次清晰整洁。

2. **APK 原生 SHA-256 防篡改与完整性校验 (Security & Anti-Tampering)**：
   - 针对使用国内 GitHub 加速镜像（如 `ghfast.top` 等 CDN）可能存在的链路篡改风险，在 Android 原生层（`MainActivity.java`）建立双向 SHA-256 校验防火墙；
   - 本地缓存命中与实时流式下载双阶段严格核对哈希指纹，遇篡改或文件损坏立即物理销毁并拦截安装；
   - Web/H5 客户端在更新弹窗提供校验指纹展示与一键复制；
   - CI/CD 自动化构建流即时计算产物 SHA-256，生成 `SHA256SUMS.txt` 并注入发行说明。

3. **真机反馈配对自愈与去行政化合规优化 (Stability & Compliance)**：
   - **配对自愈**：修复 App 重启或更新后因未重新握手导致配对密钥在有本地缓存时仍显示“未配对”的时序问题，启动时后台静默同步服务端鉴权配置；
   - **客观实测基准**：对全线高程走势图与地标序列进行去行政化改造，全面将“已核准”、“已审核”替换为客观描述“实测基准”、“实测点”与“✓ 实测航迹 GPS”。

4. **发版规范与智能体规约优化 (Guidelines & Governance)**：
   - 明确构建边界：本地测试构建仅更新第 4 位时间戳，向 GitHub 推送 Tag 触发自动化构建属于正式发布，必须递增第 3 位 (Patch)；
   - 对 `AGENTS.md` 进行上下文高密度精简，大幅降低智能体协同的 Context 开销。

---

## 📝 详细变更清单 (Changelog)

### 🐛 缺陷修复 (Bug Fixes)
- **修复高山详情页原始数组文本泄露**：对 `mountain.local_tips`、`mountain.plan_b`、`mountain.gear_detail` 统一应用 `Array.isArray()` 判断分支，使用列表排版展示，彻底杜绝原始中括号与引号外露；
- **修复真机反馈配对状态丢失假象**：在 `setupAgentFeedback.js` 初始化阶段自动静默触发 `client.syncAccessControlFromServer(savedBase)`，免除用户反复点击“测试连通性”的繁琐步骤；
- **适配 Java 17 本地构建**：调整 Gradle `compileOptions` 为 `JavaVersion.VERSION_17`，实现 Windows 开发机（JDK 17）与 GitHub Actions（JDK 21）无缝兼容离线全量构建。

### 🔒 安全防护 (Security)
- **原生 SHA-256 完整性断言**：在 Android 原生 `downloadAndInstallApkWithSha256` 建立严格断言机制，校验不通过一律不上报安装，并由 `updateStore` 弹出安全警告提示；
- **发版产物哈希随附**：自动化构建工作流同步计算 Release 与 Debug 变体 SHA-256，发布产物附带 `SHA256SUMS.txt` 供人工和终端自动化核验。

### 🧭 合规与表述 (Compliance)
- **去行政化客观描述**：地标点位和海拔序列统一改用“客观实测”措辞，避免任何法律与监管合规风险。

---

## 📦 安装包与分发说明

| 构建版本 | APK 文件名 | 文件大小 | 适用场景说明 |
| :--- | :--- | :--- | :--- |
| **正式发布版 (Release)** | `weekly-mountain-v0.3.1.<timestamp>-release.apk` | 约 27.1 MB | 推荐日常使用：采用 Zero-DCE 纯净精简构建，已剔除调试悬浮球与哨兵诊断模块，启动飞快、性能最优。 |
| **开发者内测版 (Debug)** | `weekly-mountain-v0.3.1.<timestamp>-debug.apk` | 约 29.8 MB | 开发者联调专属：内置真机智能哨兵与开发机直连面板，支持边测边自愈，免除发布等待。 |
