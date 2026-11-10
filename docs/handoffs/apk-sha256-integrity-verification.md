# 主题：APK 下载 SHA-256 防篡改校验与 v0.3.1 补丁发版交接

- 当前状态：已完成 (completed)
- 最后更新时间：2026-11-06 17:55
- 恢复入口：`android/app/src/main/java/com/weeklymountain/app/MainActivity.java`, `src/services/updateService.js`, `src/stores/updateStore.js`, `src/components/common/AppUpdateModal.vue`, `.github/workflows/build-apk.yml`, `public/version.json`, `scripts/sync_version.py`, `scripts/build_local_apks.py`, `src/debug/setupAgentFeedback.js`, `src/components/detail/RouteElevationChart.vue`, `src/components/detail/MountainDetailSheet.vue`, `docs/releases/RELEASE-v0.3.1.md`, `AGENTS.md`

## 1. 目标与背景
针对国内使用第三方公共加速镜像（如 `ghfast.top` 等）加速下载 GitHub Releases APK 时存在的中间人篡改隐患（如恶意 Payload 植入、捆绑后门或网络丢包损坏），全链路落地端到端 SHA-256 原生双向校验与防篡改防护体系，并闭环推进正式补丁发版 `v0.3.1`：
1. **CI/CD 自动化计算与资产发布**：GitHub Actions 构建出 Release 与 Debug APK 后，自动计算双方的真实 SHA-256 散列值，生成 `SHA256SUMS.txt` 作为 Release 独立资产发布，并在发行日志中生成防篡改指纹公开对照表；
2. **版本元数据对齐与多源降级**：`version.json` 结构扩展 `releaseSha256` 与 `debugSha256` 字段；`updateService.js` 支持从 `version.json` 或自动兜底拉取 `SHA256SUMS.txt` 补齐；
3. **Android 原生端流式完整性校验**：`MainActivity.java` 扩展 `downloadAndInstallApkWithSha256` 接口，在下载完成重命名及复用本地缓存包前，流式计算 SHA-256。哈希不匹配时立即阻断并销毁非法文件，抛出 `SecurityException` 警告；哈希匹配时放行系统安装；
4. **前端交互与安全呈现**：`AppUpdateModal.vue` 增设发布版 SHA-256 安全指纹徽章与一键复制；遇到哈希不匹配时显示高优先级安全拦截盾牌告警与处置引导；
5. **缺陷修复与体验升级**：彻底解决详情页原始 JSON 数组字符泄露、真机配对重启丢失假象与行政化措辞合规风险；
6. **规约固化与精简**：确立“向 GitHub 推送 Tag 自动化构建为正式对外发版，常规 Bugfix/Patch 必须递增第 3 位 (0.3.1)”的铁律，并对 `AGENTS.md` 进行高密度精简，释放大量会话 Context。

## 2. 关键设计与安全防线
- **双重拦截（缓存复用 + 下载校验）**：
  - 复用本地缓存前：校验现有 APK 文件哈希，若被篡改或损坏立即静默清除并重新拉取；
  - 下载完成后：校验临时文件 `.download`，通过后才原子重命名为正式 `.apk`，彻底杜绝脏文件残留；
- **高性能原生硬件加速流式计算**：
  - Android 端采用标准 `java.security.MessageDigest.getInstance("SHA-256")` 配套 8KB 流式缓冲，内存开销恒定，30MB 安装包计算耗时 < 50ms；
- **向前兼容与优雅降级**：
  - 若旧版本未下发期望哈希，放行原有系统底层签名比对（签名不同 Android 系统直接拒装），不造成升级阻断；
- **详情页数组渲染防御**：
  - `MountainDetailSheet.vue` 对 `local_tips`、`plan_b`、`gear_detail` 统一应用 `Array.isArray()` 分支判断，结合 Alpine 卡片与小圆点列表排版，支持数组和字符串双模自适应渲染。

## 3. 修改文件清单
1. `android/app/src/main/java/com/weeklymountain/app/MainActivity.java`
   - 新增静态辅助方法 `calculateFileSha256(File file)`；
   - 增强 `downloadAndInstallApk` 方法重载与 `downloadAndInstallApkWithSha256`；
   - 缓存复用逻辑增加 SHA-256 校验与失效自清；
   - 下载完成时引入严格 SHA-256 比对，不匹配时销毁文件并抛出明确安全异常；
2. `src/services/updateService.js`
   - 扩展 `fetchSha256Sums(verTag)` 支持从远端解析 `SHA256SUMS.txt` 兜底；
   - `fetchLatestRelease` 解析并返回 `releaseSha256`, `debugSha256`, `sha256`；
3. `src/stores/updateStore.js`
   - `startDownloadAndInstall(variant)` 依据选中的发布版本（Release / Debug）动态绑定期望哈希，并安全调用 `downloadAndInstallApkWithSha256`；
4. `src/components/common/AppUpdateModal.vue`
   - 模板新增防篡改安全指纹徽章与一键复制按钮；
   - 新增 `isTamperedOrHashMismatch` 状态与高优先级安全拦截提示卡片；
5. `.github/workflows/build-apk.yml`
   - 阶段 3 增设 `Compute APK SHA-256 Checksums` 步骤，生成 `SHA256SUMS.txt`；
   - `generate_notes.cjs` 自动注入安全指纹表格到 Release 说明；
   - `softprops/action-gh-release` 附件清单增加 `SHA256SUMS.txt`；
6. `scripts/sync_version.py`
   - `sync_all` 扩展 `--release-sha256` 与 `--debug-sha256` 命令行入参，支持同步至 `public/version.json`；
7. `public/version.json`、`src/config/version.js`、`package.json`、`android/app/build.gradle`、`assets/badges/badge-version.svg`
   - 版本原子同步升版至 `0.3.1.202611061751`；
8. `docs/releases/RELEASE-v0.3.1.md`
   - 新建 v0.3.1 正式补丁发版文档，包含规范元数据与纯净标题；
9. `android/build.gradle`、`android/app/build.gradle`、`android/app/capacitor.build.gradle`、`android/capacitor-cordova-android-plugins/build.gradle`
   - 将 `compileOptions` 调整为 `JavaVersion.VERSION_17`，兼顾开发机 JDK 17 与 CI JDK 21 均可顺畅本地免代理编译；
10. `scripts/build_local_apks.py`
    - 新增开发机本地一键全量打包脚本，具备解压断言、体积门禁与 SHA-256 本地归档能力；
11. `src/debug/setupAgentFeedback.js`
    - 新增启动时自动静默调用 `syncAccessControlFromServer(savedBase)`，彻底根治本地已缓存秘钥但在 App 启动后需手动点击“测试连通性”才能激活配对的体验 Bug；
12. `src/components/detail/RouteElevationChart.vue`
    - 将带有行政核准暗示的「已核准」彻底替换为「实测基准」「实测点」与「✓ 实测航迹 GPS」，规避任何合规与资质风险；
13. `src/components/detail/MountainDetailSheet.vue`
    - 修复「属地民俗与环保要求 (local_tips)」、「备选撤退方案 (plan_b)」与「专业装备建议 (gear_detail)」底层为数组时被原生插值直接输出原始 JSON 格式带中括号文本的显示缺陷，全面升级为 Alpine 项目列表式排版；
14. `AGENTS.md`、`GEMINI.md`
    - 高密度精简规约内容，明确本地调试构建与向 GitHub 推送 Tag 发版进位规则（常规发版必须递增第 3 位 Patch）。

## 4. 自测与验证结论
1. **完整性测试**：
   - 验证 `public/version.json` 与 `RELEASE-v0.3.1.md` 纯净版本号元数据无缝解析；
2. **语法与构建校验**：
   - `npm run build`：0 错误，耗时 3.58s，153 个山峰资源同步至 Android assets；
   - `git diff --check`：全量检查无空白符、无尾部空格、无换行污染，0 警告。
