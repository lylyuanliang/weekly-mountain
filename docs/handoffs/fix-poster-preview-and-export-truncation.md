# 主题：fix-poster-preview-and-export-truncation (修复成就长图海报预览与导出截断问题)

- 当前状态：已完成 (Completed)
- 关联反馈工单：`#1793332599860`
- 最后更新时间：2026-10-30 12:12
- 恢复入口：`docs/handoffs/fix-poster-preview-and-export-truncation.md`

---

## 1. 用户反馈与问题现象
- **反馈工单 ID**：`1793332599860`
- **反馈现象**：
  1. 预览图不完整，被截断了，弹窗内无法上下滑动查看完整长图海报；
  2. 最终点击“一键生成并保存海报到相册”生成的图片也是被硬生生截断的（只有上半截）。
- **真机环境**：
  - Viewport: 369x821, DPR 3.25
  - 设备: Android 16 (Xiaomi 15)
  - 页面路径: `/#/profile` (成就长图海报生成弹窗)

---

## 2. 根因剖析 (Root Causes)

### 2.1 为什么预览图被截断且无法上下滑动？
1. **Flex 弹性挤压陷阱 (`flex-shrink: 1`)**：
   - 弹窗外层为 `flex flex-col items-center justify-start`，高度为 `fixed inset-0`（821px）。
   - 在 Flexbox 默认规则下，子元素 `flex-shrink: 1`。当子项（顶栏、参数控制卡片、海报容器、底部按钮）总自然高度超过 821px 时，Flexbox 强行按比例压缩子项，导致海报容器被压缩至 381px。
   - 海报容器带有 `overflow-hidden`，多出部分直接在容器内部被裁切。
   - 压缩后四个子项总高度刚好等于 821px，导致外层 `overflow-y-auto` 未产生任何滚动行程（`scrollHeight == clientHeight == 821`），用户手指上下划动完全无法滚动。
2. **手势阻断与触摸行为限制**：
   - `stitch-tokens.css` 中 `body.body-scroll-locked` 包含了 `touch-action: none !important;`，导致部分移动浏览器阻断了子元素的触摸平移滚动手势；
   - 弹窗根节点包含了 `@touchmove.self.prevent`，阻断了边距与空白区域的手势冒泡。

### 2.2 为什么最终生成的图片也是硬生生截断的？
1. **容器高度被压缩裁切**：
   - 因上述 Flexbox 弹性压缩，目标 DOM 节点 `posterRef.value` 自身实际渲染高度仅有 381px，超出部分被父容器 `overflow: hidden` 裁剪；
2. **html2canvas 虚拟视口与定位裁切**：
   - `html2canvas` 默认使用宿主视口高度（821px），未指定 `width / height / windowHeight / scrollY: 0`；
   - 在未配置克隆节点展开（`onclone`）的情况下，`html2canvas` 会继承外层容器的裁剪和溢出隐藏，导致导出的图片直接在 821px 视口边界被硬生生切除。

---

## 3. 落地实施与修复方案 (Implementation)

1. **防弹性挤压与全高度自然展开**：
   - 在 `AlpineAchievementPosterModal.vue` 中为所有直接子元素显式添加 `shrink-0`，并在 `<style scoped>` 中加入 `.alpine-poster-modal > * { flex-shrink: 0 !important; }`，彻底杜绝海报被挤压；
   - 顶栏改造为 `sticky top-0 z-30` 毛玻璃浮顶，长图上下滑动时随时可点击关闭；
   - 移除弹窗根节点上的 `@touchmove.self.prevent`，底部操作按钮增加安全边距。
2. **移动端平滑手势与平移放行**：
   - 修改 `src/styles/stitch-tokens.css`：从 `body.body-scroll-locked` 中移除全局 `touch-action: none`；
   - 为 `.modal-backdrop-scroll-contain`、`.alpine-poster-modal`、`.alpine-scroll-viewport` 添加 `touch-action: pan-y !important; -webkit-overflow-scrolling: touch !important;`。
3. **html2canvas 视网膜全高度捕获算法**：
   - 测量真实全尺寸：`fullWidth = el.offsetWidth`，`fullHeight = el.scrollHeight`；
   - 配置 `windowWidth: fullWidth, windowHeight: fullHeight + 200, width: fullWidth, height: fullHeight, scrollX: 0, scrollY: 0`；
   - 在 `onclone` 阶段递归解除克隆树上所有父级容器的 `overflow: visible; maxHeight: none; height: auto`，并将海报节点从 `(0, 0)` 展开至完整全高。
4. **生成海报查看弹窗体验升级**：
   - `isPosterReadyModalOpen` 展示区升级为支持手势上下滑动的 `alpine-scroll-viewport overflow-y-auto`，解除 `max-h-[60vh]` 强行缩放限制，用户可顺畅查看视网膜长图所有细节。

---

## 4. 修改文件清单
- `package.json` / `package-lock.json` (全面移除本地 `file:../` 路径，规范安装 npm 官方源 `@lylyuanliang/agent-feedback-*@^1.1.0`)
- `src/styles/stitch-tokens.css` (放行平滑滚动手势，优化 touch-action)
- `src/components/achievement/AlpineAchievementPosterModal.vue` (海报全高展开、防 Flex 挤压、浮顶与全高视网膜捕获算法)
- `src/config/version.js` / `public/version.json` / `android/app/build.gradle` (升版至 0.2.0.202610301322)
- `GEMINI.md` / `AGENTS.md` (落地分批次提交规则与版本号四位进位场景规范)
- `docs/handoffs/fix-poster-preview-and-export-truncation.md`

---

## 5. 自动化测试与验证结果
- **测试脚本**：`scratch/verify_poster_export.py`（基于 Playwright，模拟小米15 Android 16 视口 369x821，DPR 3.0）；
- **验证项与输出**：
  - 弹窗滚动测试：`Modal scrollTop after programmatic scroll: 300`（原先为 0 无法滚动，现已完全畅通）；
  - 单峰实拍海报：Canvas 高度 706px，导出视网膜海报尺寸 `690x1408px`（无截断）；
  - 3峰实拍长图：Canvas 高度 1241px，导出视网膜长图尺寸 `690x2478px`（完全无截断，实拍照片、心得、防伪码、认证印章全部完整捕获）；
  - 测试截图存档：`C:\Users\lylyu\.gemini\antigravity\brain\66cdabf9-ca17-464c-957c-28b829d5bc91\poster_verified.png`。

---

## 6. 打包与归档产物
- **最新时间戳版本**：`0.2.0.202610301337` (VersionCode: `1793338662`)
- **生成产物**：
  - `releases/weekly-mountain-v0.2.0.202610301337-debug.apk` (28.08 MB, 构建完成时间: 2026-10-30 13:41:05)
  - `releases/weekly-mountain-latest-debug.apk` (28.08 MB)
- **编译状态**：已执行 Gradle Clean 全量重新编译，确保 100% 纳入 npm 官方源 `@lylyuanliang/agent-feedback@1.1.0` 与海报截断全套修复代码。
