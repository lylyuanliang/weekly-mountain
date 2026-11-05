# 主题：底栏抽屉三段式高度与全屏紧凑列表（方案 B）交互升级

- 当前状态：已完成全量实现并通过 Playwright 端到端验收 (completed)
- 最后更新时间：2026-11-05
- 恢复入口：`src/components/drawer/BottomSheet.vue`

## 1. 目标与背景
实现底栏抽屉由既有 2 档（收起 / 半屏）升级为 3 档（收起 66px / 半屏 364px / 全屏 `calc(100vh - 72px)`）。
向上滑动或点击展开全屏时，将卡片排列从横向轮播平滑转变为纵向紧凑条目列表（方案 B · Compact List），单屏可清晰扫视 4~8 座山峰，解决 51 座名山横滑疲劳问题。

## 2. 核心落地与修改清单

1. **`src/components/card/CompactMountainCard.vue` (新增)**：
   - 几何规范：高度标准 84px，左侧 68x68px 封面图 + 难度角标（L1~L4）；
   - 三行高密度信息排版：名称+海拔、行政区+距中心车程里程、累计爬升+往返里程+实况天气胶囊+特色标签；
   - 交互绑定：整卡点击触发选中高亮（`border-primary glow-primary`），右侧箭头指示符呼出详情，天气胶囊呼出实况天气；
   - 容错机制：图片加载失败自动平滑降级为暗黑 SVG 几何矢量占位图。

2. **`src/components/drawer/BottomSheet.vue` (三段式与手势接力重构)**：
   - **三段式高度状态机 (`snapState`)**：
     - `'collapsed'`: `66px`（极简收起条，保留选中山峰名称与展开按钮）；
     - `'half'`: `clamp(180px, min(364px, calc(100vh - 180px)), 364px)`（半屏横滑大卡片轮播）；
     - `'expanded'`: `calc(100vh - 72px)`（顶部预留 72px 给 Top App Bar 与状态栏，底部与 BottomNav 零重叠遮挡）；
     - 动效过渡：`transition: height 0.28s cubic-bezier(0.16, 1, 0.3, 1), bottom 0.28s cubic-bezier(0.16, 1, 0.3, 1)`。
   - **视觉稳定锚点区 (Visual Anchor)**：
     - 居中拖拽指示手柄 `drawer-handle`；
     - 恒定标题栏 `Active Peaks` / `51 TRACKS`（或搜索匹配状态），不发生跨模式撕裂位移；
     - 模式操作按钮联动：`'half'` 下提供「收起大图 ▾」与「展开全屏 ▴」；`'expanded'` 下提供「收回半屏 ▾」。
   - **双模式交叉淡入淡出 (`<Transition name="drawer-content-fade" mode="out-in">`)**：
     - 进入：`opacity: 0 -> 1, translateY: 10px -> 0` (0.18s)；
     - 离开：`opacity: 1 -> 0, translateY: 0 -> -8px` (0.15s)；
     - 彻底消除半屏横滑与全屏纵向列表切换时的视觉跳闪。
   - **纵向滚动与手势接力锁 (Scroll Chaining Gate)**：
     - 全屏紧凑列表容器绑定 `ref="compactListRef"`；
     - 当 `snapState === 'expanded'` 时，若触摸点在列表内部且 `compactListRef.scrollTop > 0`，原生纵向滚动放行，禁止触发抽屉下拉；
     - 只有当 `compactListRef.scrollTop <= 0` 且向下拉动超过门限（`deltaY < -10`）时，手势接力移交给抽屉外壳收缩回 half；
     - 顶部手柄始终支持任意状态的上下拖动与循环吸附切换。
   - **桌面与自动化测试支持**：
     - 全局 `window.addEventListener('mousemove', onMouseMove)` 与 `mouseup` 接管，拖拽超出视口不丢帧；
     - 状态与方法完备暴露：`expandToFull`, `expandToHalf`, `collapse`, `cycleSnapState`, `snapState`。

3. **`src/views/ExploreView.vue` (联动调优)**：
   - 优化 `onMountainSelected`：仅在 `bottomSheetRef.snapState === 'collapsed'` 时自动弹开至半屏；若已处于全屏紧凑列表，保持全屏浏览，避免误收回。

## 3. 自测验证与成果验收

1. **紧凑卡片组件单体测试 (`scratch/test_compact_card_render.py`)**：
   - 6 项断言全部通过：5 张卡片渲染数量、84px 几何尺寸、三行字段数据、天气/选中事件派发、SVG 降级回退、零控制台错误。
2. **三段式底栏抽屉全量端到端测试 (`scratch/test_bottom_sheet_three_tier.py`)**：
   - 8 阶段场景全量通过（在 369x821 窄屏真机视口下验证）：
     - `[2/8]` 初始 `half` 状态高度 364.0px，底部稳定距底 66px，横向轮播卡片可见，图标按钮不换行；
     - `[3/8]` 展开至 `expanded` 全屏，高度精确到达 683.0px (`calc(100vh - 66px - 72px)`)，顶部预留 72.0px，底部固定 66px 露出 BottomNav，单屏可见 8 座紧凑卡片，手柄与标题稳定可见；
     - `[4/8]` 紧凑卡片点击选中，高亮类名 `border-primary glow-primary` 激活，地图居中联动，抽屉保持全屏稳定，无误触发详情弹窗；
     - `[5/8]` 触发「收回半屏」图标按钮平滑缩回 364.0px，横滑卡片平滑淡入；
     - `[6/8]` 触发「收起大图」图标按钮缩回 66.0px 极简状态条，展开按钮与山峰名称可见；
     - `[7/8]` 点击极简折叠条恢复至半屏 364.0px；
     - `[8/8]` Handle 点击循环切换（half ⇄ expanded）、拖拽吸附与纵向滚动接力锁全量通过；
   - 零控制台报错（Zero Console Errors）。
3. **视觉留存产物**：
   - `scratch/bottom_sheet_three_tier_verified.png`
   - `scratch/bottom_sheet_expanded_fixed.png`
   - `scratch/bottom_sheet_half_fixed.png`
   - `scratch/bottom_sheet_collapsed.png`
   - `scratch/compact_card_render_verified.png`

## 4. 移动端真机反馈自愈修复记录 (Feedback #1793868620344 & #1793868698963)

1. **标题栏防换行与纯图标按钮重构**：
   - 根因：369px 宽屏手机上，"收起大图 ∨" 与 "展开全屏 ∧" 字符过长引发折行成两行；
   - 修复：全量升级为无字纯图标圆形按钮（`w-8 h-8 rounded-full`），配以 `expand_more` 与 `expand_less` 图标，并在标题 `Active Peaks` 与数量角标容器添加 `whitespace-nowrap flex-shrink-0`。
2. **抽屉底部锚点固定与下拉零跳闪**：
   - 根因：原全屏状态下抽屉采用 `bottom: 0px` 覆盖了 `BottomNav`，在向下拖拽时 `bottom` 从 0px 突跳回 66px 造成剧烈跳闪；
   - 修复：将抽屉底部永久固定在 `bottom: 66px`，全屏高度调整为 `calc(100vh - 66px - 72px)`，彻底解决底部跳闪，使底栏导航（探索 / 周计划 / 我的）全时段零遮挡。
3. **切换过渡动效纯化与空白空隙消除**：
   - 根因：原动效含 `translateY` 垂直跳跃且过渡时间偏长，导致两模式切换时产生空隙感；
   - 修复：纯化为 0.12s 进入 / 0.08s 离开的极速纯透明度交叉淡入淡出，消除视觉间隙。
4. **紧凑卡片点击行为边界规范**：
   - 根因：原 `handleClick()` 同时派发了 `select` 与 `detail`，导致用户点击卡片意图查看地图时却误弹出全屏详情；
   - 修复：卡片主体点击仅触发 `select(mountain.id)` 进行地图定位与高亮，右侧详情箭头按钮单独触发 `detail(mountain)`。
5. **历史反馈视频媒体框宽度坍缩修复**：
   - 根因：竖屏录屏（9:16/9:20）在 Chrome WebView 加载元数据后，原生 video 元素受 `max-height: 220px` 约束，导致宽度自适应坍缩至不足 100px；
   - 修复：在 `@agent-feedback/client` 核心源码及应用全局 CSS 中注入 `width: 100%; aspect-ratio: 16/9; object-fit: contain; background: #000;`，彻底锁定媒体框全宽，横竖屏录屏均居中等比完整展示。
6. **反馈工单闭环**：
   - `#1793868620344`：状态已更新为 `completed`；
   - `#1793868698963`：状态已更新为 `completed`。

## 5. 双模态卡片切换连续平滑动效与手势插值架构重构 (Smooth Card Switching & Gesture Morphing)

1. **彻底消除 `<Transition mode="out-in">` 带来的断裂与掉帧**：
   - 根因：原 `mode="out-in"` 强制等待旧视图离场完毕后才挂载新视图，导致 80ms 的容器空白空隙；且在抽屉高度拉伸期间同步挂载 51 张卡片 DOM，造成手机端掉帧抖动；
   - 重构：采用**双模态同层绝对定位架构**（`carousel-mode-view` 与 `compact-list-container` 均常驻 DOM，`position: absolute; inset: 0;`），实现 0% DOM 重新挂载开销与零垃圾回收卡顿。
2. **手势拖拽 60fps 实时线性插值 (Real-time Touch Interpolation)**：
   - 抽屉在拖拽过程中动态计算高度插值进度 $t = (h - \text{halfPx}) / (\text{expandedPx} - \text{halfPx})$；
   - 轮播卡片与紧凑列表的透明度根据手势实时呈现 $1-t$ 与 $t$ 线性渐变，并配以 $-20px$ 与 $24px$ 随动位移；拖到哪，两套卡片就平滑融合到哪，彻底消除拖拽释放时的突变跳闪。
3. **按钮点击物理阻尼平滑过渡 (CSS Hardware Accelerated Transition)**：
   - 非拖拽状态下点击模式切换按钮，两套卡片基于 `0.28s cubic-bezier(0.16, 1, 0.3, 1)` 曲线执行硬件加速交叉过渡，配合 `translateZ(0)`，如丝般顺滑。
4. **天气警报横条一体化收纳**：
   - 将天气横条置于轮播容器内部统一平滑渐隐，全屏紧凑列表不再受 38px 高度差挤压，彻底根除内容区垂直跳动。
5. **卡片激活选中动效平滑化与 GPU 分层**：
   - `HeroMountainCard.vue`：引入 `transition: transform 0.28s, border-color 0.24s, box-shadow 0.24s; will-change: transform; transform: translateZ(0);`，卡片点击选中 scale 缩放与高亮自然过渡；
   - `CompactMountainCard.vue`：统一重构独立 `box-shadow`，消除与 Tailwind `ring-1` 的样式冲突，配置 `0.24s cubic-bezier(0.16, 1, 0.3, 1)` 渐变。
6. **双向跨模态卡片聚焦同步**：
   - 监听 `snapState` 变更，半屏展开至全屏或全屏收回半屏时，自动通过 `scrollIntoView({ behavior: 'smooth', block: 'center' })` 对齐聚焦当前选中山峰，防止视角丢失。
7. **自动化测试验收 (`scratch/test_card_switch_animation.py`)**：
   - `[1/4]` 轮播卡片连续点击切换平滑高亮通过；
   - `[2/4]` 跨模态展开自动对齐与视角锁定通过；
   - `[3/4]` 紧凑列表切换并收回轮播平滑同步通过；
   - `[4/4]` 手势拖拽中途（524px）实时线性插值测量：轮播透明度 0.50，列表透明度 0.50，平滑融合断言通过；
   - 视觉产物：`scratch/bottom_sheet_mid_drag_morph.png`。
