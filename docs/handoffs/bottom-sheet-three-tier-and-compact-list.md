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
   - 8 阶段场景全量通过：
     - `[2/8]` 初始 `half` 状态高度 364.0px，横向轮播卡片可见，操作按钮完整；
     - `[3/8]` 展开至 `expanded` 全屏，高度精确到达 772.0px (`calc(100vh - 72px)`)，顶部预留 72.0px，单屏可见 8 座紧凑卡片（符合 4~5 座设计标准），手柄与标题稳定可见；
     - `[4/8]` 紧凑卡片点击选中，高亮类名 `border-primary glow-primary` 激活，地图居中联动，抽屉保持全屏稳定；
     - `[5/8]` 触发「收回半屏 ▾」平滑缩回 364.0px，横滑卡片平滑淡入；
     - `[6/8]` 触发「收起大图 ▾」缩回 66.0px 极简状态条，展开按钮与山峰名称可见；
     - `[7/8]` 点击极简折叠条恢复至半屏 364.0px；
     - `[8/8]` Handle 点击循环切换、鼠标/触控拖拽就近吸附（half ⇄ expanded）、全屏纵向滚动接力锁（`scrollTop > 0` 锁定纵向原生滚动，`scrollTop == 0` 接力下拉收回半屏）全量通过；
   - 零控制台报错（Zero Console Errors）。
3. **视觉留存产物**：
   - `scratch/bottom_sheet_three_tier_verified.png`
   - `scratch/bottom_sheet_expanded.png`
   - `scratch/bottom_sheet_half.png`
   - `scratch/bottom_sheet_collapsed.png`
   - `scratch/compact_card_render_verified.png`
