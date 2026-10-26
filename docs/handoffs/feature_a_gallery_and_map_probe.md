# 主题：feature_a_gallery_and_map_probe

- 当前状态：已完成（Feature A 全量实现并经 Playwright 自动化验证通过，控制台 0 错误）
- 最后更新时间：2026-10-22
- 恢复入口：`src/components/detail/MountainDetailSheet.vue`, `src/components/detail/RouteElevationChart.vue`, `src/components/map/AppMap.vue`, `src/views/ExploreView.vue`, `scratch/verify_feature_a.py`

## 当前目标
实现【选项 A：山峰详情多图相册画廊 + 海拔图与地图探针双向联动】：
1. 山峰详情多图相册画廊 (MountainDetailSheet.vue)：
   - 支持多图轮播与滑动手势切换，优雅指示点与页码胶囊；
   - 支持 mountain.gallery 数组（自动兜底高质量实拍与高山暗黑风格插图）；
   - 支持轻触图片全屏 Lightbox Modal 放大预览与键盘导航。
2. 海拔剖面图与地图光标探针双向联动：
   - RouteElevationChart.vue: 在 SVG 上滑动或点击航点向外派发 `probe-waypoint` 与 `clear-probe`；
   - AppMap.vue: 新增探针信标光标（带有极光绿光环呼吸动画与 Tooltip），平滑将地图视口居中微调（保持可视天际留白），支持 `clearProbe()`；
   - ExploreView.vue: 详情抽屉与地图联动绑定，抽屉关闭时自动清理探针。
3. 自动化验证：编写 Playwright 自动化验证脚本 `scratch/verify_feature_a.py`，确保 100% PASS 且控制台 0 运行时错误。

## 已完成工作
1. **山峰详情多图相册画廊 (`src/components/detail/MountainDetailSheet.vue`)**
   - 顶部 Hero 区域支持多图轮播与轻扫切换：
     - 支持数据源 `mountain.gallery` 数组，未指定时自动回退为 3 图高山画廊（主峰全貌实拍 + 晨曦金山观景 SVG + GPS 地貌拓扑 SVG）；
     - 提供左右悬浮毛玻璃箭头与微型指示点（Indicator Dots），当前页以极光绿长胶囊发光呈现；
     - 增加触控手势（Swipe Left / Swipe Right）与页码角标；
     - 全屏 Lightbox Modal：通过 `<Teleport to="body">` 呈现全屏暗黑高山黑曜石大图居中画廊，支持左右切换、手势与 ESC / 方向键快捷退出。
2. **海拔剖面图与地图光标探针双向联动**
   - `RouteElevationChart.vue`:
     - 监听 SVG 剖面图鼠标/触摸滑动（`handleChartPointerMove`），计算最近航点并实时 `emit('probe-waypoint', wp)`；
     - 点击航点卡片或节点高亮并派发探针；
     - 增加极光绿垂直探针参考线与节点扩散发光动画；
     - 组件销毁或切换山峰时触发 `emit('clear-probe')`。
   - `AppMap.vue`:
     - 新增探针标记点 `probe-beacon-marker`：地表雷达呼吸光环（`animate-ping` 与 `beacon-ring`）+ 极光绿垂直激光垂线下挂 Tooltip 胶囊（航点序号、名称、标高、距起点里程与 GPS 核准状态）；
     - 平滑将地图视口居中微调至上方可视天际中心（`getVisibleSkyOffsetY` 自动避让底栏与抽屉）；
     - 暴露 `setProbeMarker(waypoint)` 与 `clearProbe()` 方法至 `defineExpose`。
   - `ExploreView.vue`:
     - 在 `MountainDetailSheet` 上绑定 `@probe-waypoint` 与 `@clear-probe`；
     - 抽屉关闭时联动清理地图探针。
3. **自动化端到端验证 (`scratch/verify_feature_a.py`)**
   - 编写 Playwright 自动化测试脚本，全面验证龙泉山与光雾山：
     - 多图轮播与指示点切换（1/3 -> 2/3 -> 3/3）正常；
     - Lightbox Modal 打开、大图渲染、ESC 退出正常；
     - 点击航点与滑动 SVG 剖面图成功向 AppMap 注入探针标记点；
     - 关闭抽屉后探针标记点彻底清除；
     - 运行时 0 控制台错误，100% 绿灯 PASS。
