# 任务交接与状态记录：Android APK 下载切屏保持、权限返回自动安装与防重复下载优化 (APK Download Resume & Permission Flow)

> 规范依据：`AGENTS.md` / `GEMINI.md` 全局规约与任务交接硬门禁

---

## 1. 任务背景与核心问题

### 1.1 用户反馈痛点
1. **下载中切屏丢失**：“在下载中的任务, 我切换一下应用, 再切回来, 就要重新下载了”；
2. **权限跳转返回丢失**：“下载完准备安装了, 然后提示打开‘手机第三方安装许可’, 我打开之后, 然后切换回来, 又要重新下载了”；
3. **时间轴指示点与日期文本错位重叠**：手机端截图反馈今天时间轴发光点与 `2026-10-28` 首位字符重叠。

### 1.2 根因深度剖析
1. **Activity `onResume` 盲目清缓存抹除正在下载与刚下好的包**：
   - 此前在 `MainActivity.onResume()` 中无条件调用 `cleanUpdateApkCache(this)`；
   - 用户只要切屏去回微信、看其他 App 或跳系统设置开启安装权限，切回应用时 `onResume()` 会立即在子线程将 `cache/updates/` 下的所有 `.apk` 暴力删除；
   - 导致下载流句柄写入失败报中断，或刚下载完 100% 的安装包被物理抹除。
2. **下载未做临时文件隔离**：
   - 原下载流直接写入最终 `.apk`，下载中途没有任何临时状态隔离保护。
3. **缺乏本地安装包命中复用检查**：
   - `downloadAndInstallApk` 每次调用时不检查本地是否已存在完整同版本 APK，总是强行重拉 29MB。
4. **权限跳转缺乏状态闭环与自动续装机制**：
   - 用户跳到“允许安装未知应用”设置页面后，Native 未保存待安装包指针；开启权限切回应用后，没有自动唤起安装器，前端也未提供重试入口，导致用户只能从头下载。
5. **CSS 绝对定位偏置不足**：
   - 时间轴发光圆点此前采用 `absolute -left-[5px]` 且容器内边距仅 `pl-5`，在部分移动端分辨率下导致圆点侵入文字排版区域，遮挡 `2026-10-28` 开头的数字 `2`。

---

## 2. 方案落地与关键修改

### 2.1 Android 原生底层彻底重构 ([`MainActivity.java`](file:///d:/file_save/workspace/github/weekly-mountain/android/app/src/main/java/com/weeklymountain/app/MainActivity.java))
1. **新增状态跟踪**：
   - `pendingInstallApk`: 存储当前已完整下载待安装的 APK 文件；
   - `waitingForInstallPermission`: 记录是否正处于未知应用安装权限申请等待态；
   - `isDownloading`: 原子防重入标志；
   - `lastPercent` / `lastReceived` / `lastTotal` / `lastStatus` / `lastMessage`: 缓存最新下载进度快照。
2. **临时文件与原子重命名**：
   - 下载过程流式写入 `weekly-mountain-v${ver}.apk.download`；
   - 100% 完成后原子重命名为正式 `.apk`，杜绝未下完被误用。
3. **Partial WakeLock 保护**：
   - 下载期间向系统申请 `PowerManager.PARTIAL_WAKE_LOCK`，确保用户切到微信或锁屏时 CPU 持续运行网络下载。
4. **已就绪安装包命中复用**：
   - 每次触发安装前优先检查 `targetFile.exists() && targetFile.length() > 1024 * 1024`，若本地已有完整包则直接进入安装，**0 毫秒重入，耗费 0 流量**。
5. **权限返回自动拉起安装闭环**：
   - 在 `onResume()` 中检查 `waitingForInstallPermission` 与 `pendingInstallApk`，一旦检测到用户已在系统设置开启权限，**立即全自动弹出系统安装器对话框**，无需任何额外手动操作。
6. **切屏返回进度即时补发**：
   - 在 `onResume()` 中若正在下载中，立即向 WebView 补发一次最新下载百分比，防止切屏导致前端进度条卡住。
7. **彻底移除 `onResume()` 中的盲目缓存清理**：
   - 仅在应用冷启动 `onCreate()` 或用户显式调用清理时执行清理，且清理时严格排除正在下载的临时包与待安装包。

### 2.2 前端更新体验与重试强化
1. **[`src/stores/updateStore.js`](file:///d:/file_save/workspace/github/weekly-mountain/src/stores/updateStore.js)**：
   - 增加 `visibilitychange` 与 `window.focus` 监听，切回页面时若处于 `permission_required` 状态，主动探测系统权限并自动启动安装。
2. **[`src/components/common/AppUpdateModal.vue`](file:///d:/file_save/workspace/github/weekly-mountain/src/components/common/AppUpdateModal.vue)**：
   - 在“等待授予未知应用安装权限”面板中增加“我已开启权限，立即调起安装”显式兜底按钮，双保险覆盖。

### 2.3 移动端时间轴指示点错位修复 ([`MobileFeedbackWidget.vue`](file:///d:/file_save/workspace/github/weekly-mountain/src/components/debug/MobileFeedbackWidget.vue))
- 将容器内边距由 `pl-5` 提升至 `pl-7` (28px)，竖线位置对齐至 `left-[11px]`；
- 将发光圆点位置修正为 `left-[3px]`（16px 宽圆点，中心位于 11px，与贯通竖线完美垂直同轴）；
- 日期标题文字起始于 28px，与圆点右边缘保持 9px 独立安全呼吸间距，彻底消除重叠。

---

## 3. 验证与交付产物

1. **Java 原生编译**：
   - `compileDebugJavaWithJavac` 100% 编译通过。
2. **自动化测试回归**：
   - 执行 Playwright 移动端视口时间轴测试，验证对齐后发光圆点与 `2026-10-28` 零重叠，截图留存：
     `C:\Users\lylyu\.gemini\antigravity\brain\66cdabf9-ca17-464c-957c-28b829d5bc91\test_feedback_timeline_aligned.png`
3. **最新 APK 打包**：
   - 执行流水线：`pwsh -File scripts/build_app.ps1 -Variant debug -NoPause`
   - 版本号：`0.0.1.202610281340` (Code: `1793166004`)
   - 产物路径：`releases/weekly-mountain-v0.0.1.202610281340-debug.apk` (28.08 MB)
   - 在线最新镜像：`releases/weekly-mountain-latest-debug.apk`
4. **工单反馈回写**：
   - 反馈 ID `1793165588167` 状态已更新为 `completed`，并写入了详细的修复说明。

---

## 4. 后台服务状态与恢复入口
- **Vite 预览/热重载服务**：正常运行 (`task-4980`, 端口 5173)
- **反馈监听智能哨兵**：交付回复前拉起最新进程
