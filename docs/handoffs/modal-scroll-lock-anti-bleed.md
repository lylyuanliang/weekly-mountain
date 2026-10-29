# 任务交接与状态记录：全应用弹窗背景滚动穿透治理 (Modal Scroll Lock & Anti-Bleed)

> 规范依据：`AGENTS.md` / `GEMINI.md` 全局规约与任务交接硬门禁

---

## 1. 任务背景与核心目标

### 1.1 背景来源
- **工单 ID**：`#1793153175228`
- **页面**：`/profile`
- **用户反馈原文**：
  > “在这个弹窗界面，我还能上下滑动底下的内容（注意看滚动条），分析下，不止这个弹窗，还有其他的弹窗也有这个问题”
- **附带截图**：`scratch/feedback_screenshot_1793153175228_1.jpg`
  - 呈现《真机联调与内测服务》（`AlpineDebugModal.vue`）打开时，右侧背景依然存在且移动的页面滚动条。

### 1.2 根因分析 (Root Cause Analysis)
1. **移动端默认手势冒泡机制**：在移动端 Web / WebView 中，遮罩层（Backdrop）或弹窗不可滚动区滑动手势冒泡至 `document.body`；弹窗可滚动区域到达滚动边界（Boundary Bounce）时，动量滚动手势（Overscroll）发生穿透链（Scroll Chaining）。
2. **缺乏统一全局滚动锁定器**：目前项目中所有弹窗组件均未在打开时对 `body` 施加滚动锁定。
3. **层叠弹窗安全恢复**：若只简单置空 `overflow`，在多层弹窗关闭时会导致外层弹窗未关闭时底层提早解锁。需设计引用计数型全局滚动锁机制（`useScrollLock`）。

### 1.3 核心目标
1. 创建高可用、引用计数、无内存泄漏的全局滚动锁组合式函数 [`src/composables/useScrollLock.js`](file:///d:/file_save/workspace/github/weekly-mountain/src/composables/useScrollLock.js)。
2. 在全局样式中注入 `.body-scroll-locked` 规范类，配合 `touch-action: none; overscroll-behavior: none;`。
3. 全面覆盖并治理应用内全部 10 处弹窗与抽屉组件：
   - `AlpineDebugModal.vue`（增加 `<Teleport to="body">` 及滚动锁）
   - `AppUpdateModal.vue`
   - `LegalDisclaimerModal.vue`
   - `MobileFeedbackWidget.vue`
   - `AlpineAchievementPosterModal.vue`
   - `CheckinDetailModal.vue`
   - `MountainWeatherModal.vue`
   - `RegionPickerSheet.vue`
   - `MountainDetailSheet.vue`
   - `ProfileView.vue`（全屏大图预览弹窗）
4. 为所有弹窗遮罩层与可滚动区域补充 `overscroll-behavior: contain` 与 `@touchmove.self.prevent` 阻断。
5. 编写端到端 Playwright 自动化测试脚本验证弹窗打开时底层页面绝对不可滚动、弹窗关闭后平滑恢复。
6. 打包归档 Release / Debug APK，更新工单状态并重启后台哨兵。


---

## 2. 治理实施与架构设计

### 2.1 组合式全局滚动锁 (`src/composables/useScrollLock.js`)
- **引用计数模型 (`lockCount`)**：支持多层弹窗/抽屉/图片灯箱层叠打开场景（如从个人中心 -> 开发者调试弹窗 -> 反馈悬浮窗 -> 截图大图预览），每个组件各自申请锁，仅当全部弹窗关闭且 `lockCount === 0` 时才安全恢复 `html` 与 `body` 的原生滚动样式，防止外层弹窗尚未关闭时底层提前解锁。
- **双层样式与滚动条跳动补偿**：
  - 同时锁定 `document.documentElement` 与 `document.body` 的 `overflow: hidden` 与 `overscroll-behavior: none`；
  - 自动计算并补偿 `scrollBarWidth = window.innerWidth - document.documentElement.clientWidth`，防止 PC / 桌面端滚动条消失引起的页面布局抖动；
  - 动态增删 `.body-scroll-locked` 统一语义类。

### 2.2 覆盖组件清单与改动文件
1. [`src/composables/useScrollLock.js`](file:///d:/file_save/workspace/github/weekly-mountain/src/composables/useScrollLock.js)：新建引用计数型滚动锁定 Composable。
2. [`src/styles/stitch-tokens.css`](file:///d:/file_save/workspace/github/weekly-mountain/src/styles/stitch-tokens.css)：注入 `.body-scroll-locked` 与 `.modal-backdrop-scroll-contain` 类。
3. [`src/components/debug/AlpineDebugModal.vue`](file:///d:/file_save/workspace/github/weekly-mountain/src/components/debug/AlpineDebugModal.vue)：使用 `<Teleport to="body">` 提升层级，接入 `useScrollLock`，遮罩层增加 `@touchmove.self.prevent`。
4. [`src/components/common/AppUpdateModal.vue`](file:///d:/file_save/workspace/github/weekly-mountain/src/components/common/AppUpdateModal.vue)：接入 `useScrollLock(() => updateStore.isModalOpen)`。
5. [`src/components/common/LegalDisclaimerModal.vue`](file:///d:/file_save/workspace/github/weekly-mountain/src/components/common/LegalDisclaimerModal.vue)：接入 `useScrollLock(visible)`，遮罩层拦截手势穿透。
6. [`src/components/debug/MobileFeedbackWidget.vue`](file:///d:/file_save/workspace/github/weekly-mountain/src/components/debug/MobileFeedbackWidget.vue)：接入 `useScrollLock(() => isOpen.value || lightboxOpen.value)`。
7. [`src/components/achievement/AlpineAchievementPosterModal.vue`](file:///d:/file_save/workspace/github/weekly-mountain/src/components/achievement/AlpineAchievementPosterModal.vue)：接入 `useScrollLock(() => visible.value || isPosterReadyModalOpen.value)`。
8. [`src/components/checkin/CheckinDetailModal.vue`](file:///d:/file_save/workspace/github/weekly-mountain/src/components/checkin/CheckinDetailModal.vue)：接入 `useScrollLock(() => visible.value || isPreviewLightboxOpen.value)`。
9. [`src/components/weather/MountainWeatherModal.vue`](file:///d:/file_save/workspace/github/weekly-mountain/src/components/weather/MountainWeatherModal.vue)：使用 `<Teleport to="body">` 提升层级，接入 `useScrollLock`。
10. [`src/components/common/RegionPickerSheet.vue`](file:///d:/file_save/workspace/github/weekly-mountain/src/components/common/RegionPickerSheet.vue)：接入 `useScrollLock(() => props.modelValue)`。
11. [`src/components/detail/MountainDetailSheet.vue`](file:///d:/file_save/workspace/github/weekly-mountain/src/components/detail/MountainDetailSheet.vue)：接入 `useScrollLock(() => props.modelValue && props.mountain)`。
12. [`src/views/ProfileView.vue`](file:///d:/file_save/workspace/github/weekly-mountain/src/views/ProfileView.vue)：全屏打卡照片大图预览接入 `useScrollLock(isPreviewOpen)`。

---

## 3. 验证与交付记录

### 3.1 自动化测试结果
- **专项防穿透验证 (`scratch/verify_modal_scroll_lock.py`)**：
  - [PASS] 初始页面滚动正常，无滚动锁定
  - [PASS] Alpine 开发者联调弹窗打开 -> body 锁定 -> 内部滚动正常 -> 关闭 -> 恢复正常滚动
  - [PASS] 官方在线更新弹窗打开 -> body 锁定 -> 关闭 -> 恢复
  - [PASS] 法律免责声明弹窗打开 -> body 锁定 -> 关闭 -> 恢复
  - [PASS] 移动端真机反馈弹窗打开 -> body 锁定 -> 关闭 -> 恢复
- **全量 E2E 回归测试 (`scratch/test_app_e2e_full.py`)**：
  - [PASS] SECTION 1: Explore 地图主屏 (51 座山峰标定、搜索过滤、手势与抽屉吸附)
  - [PASS] SECTION 2: 地图点位与山峰卡片双向高亮联动
  - [PASS] SECTION 3: 12 个模块 MountainDetailSheet 抽屉与打卡交互
  - [PASS] SECTION 4: 计划路线切换、增删周计划
  - [PASS] SECTION 5: 个人中心勋章、数据导入导出、主题切换
  - [PASS] 零控制台运行时错误 (0 console errors)

### 3.2 移动端 APK 编译产物
- **Release APK**: `releases/weekly-mountain-v0.0.1.006-release.apk` (29.03 MB)
- **Release 最新镜像**: `releases/weekly-mountain-latest-release.apk`
- **Debug APK**: `releases/weekly-mountain-v0.0.1.006-debug.apk` (29.03 MB)
- **Debug 最新镜像**: `releases/weekly-mountain-latest-debug.apk`

### 3.3 工单与后台哨兵恢复
- **工单 `#1793153175228` 状态**：已置为 `completed`，并写入结构化答复。
- **后台反馈哨兵 (`watch_mobile_feedback.py`)**：已重新拉起，处于无缝监听状态。
