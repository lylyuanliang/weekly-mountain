# 主题：fix-tab-switch-flicker (彻底根除反馈调试弹窗切换 Tab 界面闪烁缺陷)

- 当前状态：已完成并验证通过 (Completed & Verified)
- 最后更新时间：2026-10-29
- 恢复入口：`docs/handoffs/fix-tab-switch-flicker.md`

---

## 1. 目标与背景
用户在真机上操作反馈与调试弹窗时，录屏（`D:\file_save\workspace\github\mp4\f57cb6160c10256ee386b7d94e792bae.mp4`）反馈：
在切换顶部 Tab（「新建反馈」、「历史与进度」、「🛠️ 联调与更新」）时，界面出现明显的“闪烁”与抖动。

## 2. 根因深度剖析 (Root Cause Analysis)
经过对视频逐帧对比与 `@lylyuanliang/agent-feedback-client` 源码审查，精准定位到以下核心根因：
1. **入场动画重演导致的瞬间黑白闪烁（最致命）**：
   `.modal-container` 上配置了 `animation: modal-pop 0.2s cubic-bezier(0.16, 1, 0.3, 1)`（从 `opacity: 0; transform: scale(0.96) translateY(8px)` 到 `opacity: 1`）。
   组件的 `setTab()` 每次都调用了全量 `this.render()`，将 `this.shadow.innerHTML` 彻底重置。导致 `.modal-container` 被彻底销毁并重新插入 DOM，每一次点击 Tab 都在 0.2 秒内重新播放一次透明度与位移动画，肉眼看就是整个弹窗闪黑重绘一次。
2. **样式表（`<style>`）全量销毁重建引发 FOUC (Flash of Unstyled Content)**：
   每次 `this.render()` 都在 innerHTML 头部拼接 500 多行的 `<style>`。浏览器在重新解析 CSSOM 期间会丢失样式计算，产生 1~2 帧的页面重排重绘闪烁。
3. **内容互斥条件渲染导致大块空白闪现**：
   原代码在 `.modal-body` 采用三元表达式互斥渲染，切换到历史 Tab 时，立即将已有列表抹除并展示居中的“正在获取进度...”，待请求返回后再重绘时间轴，导致大面积黑底闪白。

## 3. 根治优化落地 (Implementation Details)
1. **多面板常驻体系 (Multi-panel Architecture in `.modal-body`)**：
   将 `.modal-body` 内部重构为三类面板共存结构：
   - `<div class="af-tab-panel af-tab-panel-submit">...</div>`（新建反馈）
   - `<div class="af-tab-panel af-tab-panel-history">...</div>`（历史与进度）
   - `<div class="af-tab-panel af-tab-panel-ext ext-tab-container" data-tab-id="...">...</div>`（扩展槽）
   在 DOM 中同时实例化存在，通过 `display: block` 与 `display: none` 进行轻量可见性控制。
2. **零 DOM 销毁与零动画重放切换 (`switchTabDom`)**：
   在 `setTab(tab)` 中，实现真正的 0 毫秒原地切换：
   - 仅就地切换 `.tab-btn` 的 `active` 类名；
   - 仅就地切换目标面板的 `display`；
   - 保持 `.modal-container` 在 DOM 中绝对静止，**彻底杜绝 `modal-pop` 动画重演**！
3. **历史时间轴 SWR 缓存优先策略 (`loadHistory`)**：
   - 切换到历史 Tab 时，若内存中已有缓存数据，立即呈现已有时间轴，后台静默请求更新；
   - 新增 `updateHistoryDom()` 局部刷新时间轴节点，不再调用全量 `this.render()`；
   - 彻底消除了“正在获取进度...”的大块空白闪烁。
4. **扩展 Tab 生命周期兼容**：
   严格遵循单测契约在切出时触发 cleanup，切入时局部更新容器，不污染其他面板。

## 4. 验证结果
1. **单测套件**：`agent-feedback` 全仓 79/79 测试项 100% 绿灯全通；新增 `should maintain multi-panel architecture for zero-flicker tab transitions` 用例；
2. **端到端多 Tab 切换性能测试（Playwright / Edge 真机视口）**：
   - `switch to 'history'`: **4.80ms** (0 闪烁)
   - `switch to 'alpine-debug'`: **5.37ms** (0 闪烁)
   - `switch to 'submit'`: **3.80ms** (0 闪烁)
   - 切换耗时由原先的数百毫秒动画淡入降低至 **3~5 毫秒** 瞬间响应！
3. **移动端 Native 打包就绪**：
   - 升版至 `0.0.1.202610291426`（`versionCode: 1793255200`）；
   - 生成全新的 Debug APK（28.08 MB）覆盖 `releases/weekly-mountain-latest-debug.apk`；
   - cpolar 外网穿透端点验证通过，支持手机端 App 打开后一键免跳转在线更新。
