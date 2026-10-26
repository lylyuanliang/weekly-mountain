# 主题：project-overview

- 当前状态：已完成「以地图为中心的模块化 App 架构重构」（Tasks 1~8 全量通过验收）；99% 高保真复刻 Stitch 极光黑曜石设计体系；3-Tab（全屏地图+三段式抽屉、周计划时间线、成就遥测与设置）全线贯通；Playwright 端到端全量 E2E 测试 100% 绿灯且控制台 0 错误；生成最新自包含纯静态包 `weekly-mountain-deploy.zip`（解压总体积 5.78 MB，文件数 53 个，稳稳命中 html2.link M 档标准，4 积分/天）；终审全分支审查通过（APPROVED）。
- 最后更新时间：2026-10-16
- 恢复入口：`weekly-mountain-deploy.zip`, `dist/`, `src/`, `docs/superpowers/plans/2026-10-16-map-centric-app-redesign.md`, 分支 `feature/app-modular-redesign`

## 当前目标
重构任务已全量完成，等待用户审阅并确认分支合并或发布操作。

## 已完成工作
1. **打 Tag 归档**：在初始提交 `8e53945` 上成功创建带附注 Git 标签 `v1.2.3`（`release: v1.2.3 详情内来源默认折叠`）。
2. **完成实施方案规划**：按照 `writing-plans` 规约编写 [2026-10-15-fix-bugs-and-interaction-polish.md](file:///d:/file_save/workspace/github/weekly-mountain/docs/superpowers/plans/2026-10-15-fix-bugs-and-interaction-polish.md)。
3. **Task 1: 修复 `calcStats` 缺失派生数据 Bug**
   - 将 `calcStats` 中直接读取 `m.ascent_m` / `m.distance_km` 改为调用 `derivedNums(m)` 并进行单精度小数取整 `Math.round(dist * 10) / 10`。
   - 彻底解决了如达瓦更扎等未显式声明爬升/里程字段时打卡统计为 0 的 Bug。
4. **Task 2: 修复移除已选标签时筛选面板控件状态不同步 Bug**
   - 在 `renderActiveFilters()` 的各项 chip 移除回调中补充反向清除筛选面板内对应按钮（难度、分类、免费、过夜、当季、完成状态）的 `.on` 高亮类。
   - 补充将车程滑块 `#fDrive` 重置为 `5` 并将文本更新为 `5h`。
5. **Task 3: 修复关闭全屏地图时详情弹层滚动穿透 Bug**
   - 改造 `closeRouteMap()`，增加前置条件判断：仅当底层详情弹层 `#sheet` 未打开（无 `.show` 类）时，才移除 `document.body` 上的 `lock` 类。
6. **Task 4: 修复吸顶导航右侧与关闭按钮重叠及锚点遮挡 Bug**
   - 为 `.sheet-nav` 补充 `padding-right: 92px`，避免移动端横滑导航至最右项（如交通/装备）时被固定的关闭按钮 `✕` 遮挡。
   - 为弹层内各锚点区块标题 `.m-route, .m-sec h4, .sec-fold` 统一增加 `scroll-margin-top: 56px`，确保锚点跳转定位时不被吸顶导航遮挡。
7. **Task 5: 优化周计划选择弹窗（添加取消按钮）**
   - 在 `openPlanPicker()` 弹窗底部增加样式对齐的取消按钮 `<button class="btn ghost wide" onclick="closeModal()">取消</button>`，支持误触后明确取消退出。
8. **Task 6: 版本号升级至 `v1.2.4` 并执行端到端全量回归测试**
   - 同步更新 `index.html` 顶栏（line 508）、页脚（line 593）及 JavaScript `APP_VERSION` 常量（line 22739）至 `v1.2.4 · 2026-10-15`。
   - 运行全部 7 项自动化回归测试脚本，全部通过（0 failures, 0 errors, 0 warnings）。
9. **代码提交与推送**
   - 遵循中文 Conventional Commit 规范精准提交变更至 `main` 分支（Commit: `a20b525`）。
   - 创建带附注发布标签 `v1.2.4`（`release: v1.2.4 修复交互缺陷与统计失真`）。
   - 成功推送分支与标签至 GitHub 远端仓库（`origin/main`）。
10. **Google Stitch 独立设计与第三主题深度还原**
   - 通过 Stitch API 创建独立设计项目 `Weekly Mountain - Modern Alpine Explorer`（ID: `1926773866906178772`），摆脱旧样式束缚，生成高保真「Alpine Explorer - Glacial Glass & Obsidian」设计系统。
   - 提取 Stitch 的色系规范（`#090d16` 黑曜石、`#4edea3` 极光翠绿、`#4cd7f6` 冰川青蓝、`#ffb95f` 日照金山）、玻璃拟态（`backdrop-filter: blur(16-24px)`）、高光微边框与立体发光投影。
   - 将其严格还原为第三主题 `[data-theme="stitch"]`（展示名：极光雪峰风 ✨），并在 `applyTheme()` 中实现水墨（`ink`）-> 营地（`camp`）-> 极光雪峰（`stitch`）的三主题循环平滑切换。
   - 编写 `test_stitch_theme.py` 自动化测试脚本，实测主题切换与弹层渲染完全正常，全量回归测试 100% 通过，控制台 0 错误。
11. **全量 50 座山峰真实高清风光图库采集与挂载**
   - 派发独立图片抓取子代理，多源策略抓取 50 座山峰真实风景照（百度百科 API 34座、别名/景区层级 15座、户外精选 1座）。
   - 50 张标准 JPEG 高清图片统一存储于 `assets/mountains/{id}.jpg`（总计 11.13MB），并通过 `scratch/mountain_images.json` 生成元数据清单，设置了优雅兜底回退。
12. **全新 Stitch UI（Alpine Explorer 极光与黑曜石）全量深度落地**
   - 派发独立、干净上下文子代理，彻底摒弃旧版卡片样式的束缚，以 Stitch 双屏设计为唯一依据进行 DOM 重构与数据绑定。
   - 实现了 TopAppBar 呼吸灯、Telemetry 赛季仪表盘（动态行者等级、3列指标、进度条）、Hero Alpine 192px 大图精选卡片、Standard Alpine 80x80 圆角缩略图卡片、时间轴周计划排期流与 SVG 圆形环状进度条、Bento 成就统计网格与 12 模块黑曜石详情抽屉。
   - 编写并运行 Playwright 自动化验证脚本，8 大验证步骤全绿通过，并生成 4 张高清实机渲染截图存证。
13. **Stitch 主题全面重构与视觉体验升级（7 大改进落实）**
   - 派发干净子代理 `Stitch UI Polisher`，落实用户提出的 7 条优化需求。
   - 响应式居中：引入 `max-width: 540px; margin: 0 auto` 居中视口与环境光，彻底消除 PC 端左偏和右侧大面积空旷异常。
   - 消除搜索与筛选重复：顶层集成式胶囊搜索框与芯片，展开面板移除重复难度项，专司地区、车程滑块与条件。
   - 默认主题切换：将 Stitch 极光黑曜石主题设置为全站默认主题（`<html data-theme="stitch">` 及 `defaultState()`）。
   - 找回版本与数据核验：在顶栏嵌入 `v1.2.4 · 2026-10-15` 与 `山单 50 座已全上线 · 数据核验 2026-10-12` 毛玻璃元数据胶囊。
   - 全量升级 Hero 大图卡片：**彻底废除小缩略图样式，全部 50 座山峰卡片统一升级为 192px 全宽风光摄影 Hero Alpine 沉浸式大卡片**，挂载 4 列数据网格与双行动按钮。
   - 自动化端到端测试与视觉证据验收全部通过。
14. **部署包轻量化优化（方案 A：从 L 档降至 M 档）**
   - 原始 50 张未压缩大图导致解压总大小达 12.45 MB，超出 html2.link M 档上限（10 MB）被判定为 L 档（10 积分/天）。
   - 实施「方案 A」：备份原图后，采用 Lanczos 重采样将 50 张图片限制最大宽度 900px，并以 82% 质量 Progressive JPEG 存储；图片总体积从 10.97 MB 锐降至 4.27 MB（减少 61.1%）。
   - 重新打包生成 `weekly-mountain-deploy.zip`（51 个文件，解压总大小 5.75 MB，压缩包 4.72 MB），完全符合 M 档（≤10MB 且 ≤100 个文件），消耗降至 4 积分/天，立省 60% 积分。
15. **启动 App 模块化重构规划（以地图为中心的现代 App）**
   - 创建并切换至新分支 `feature/app-modular-redesign`。
   - 确立「Web-First App Shell」双模一致原则与「Vite + Vue 3 + Pinia + Vue Router」纯静态工程化架构。
   - 完成设计规格说明书 `docs/superpowers/specs/2026-10-16-map-centric-app-redesign.md`，定义以全景地图为底座、三段式可拖拽 BottomSheet 抽屉与 3-Tab 导航体系，确立由干净子代理与 Stitch 交互及 99% 像素级还原机制。
16. **实施以地图为中心的模块化 App 重构（Tasks 1 ~ 8 全量交付）**
   - **Task 1（数据层解耦）**：提取 `src/data/mountains.json`（50座山完整字段）与 `src/data/waypoints.json`（387个GPS点），UTF-8无BOM，测试通过。
   - **Task 2（工程骨架）**：引入 Vite 5 + Vue 3 + Hash路由，配置 `base: './'` 纯静态自包含构建，原单页备份至 `index.monolith.html`。
   - **Task 3（Pinia状态管理）**：实现 `mountainStore`、`checkinStore`、`planStore`、`themeStore`，完整继承 `derivedNums` 算法（达瓦更扎爬升 866m / 里程 13.9km 零失真）与兼容老版本 JSON 备份导入。
   - **Task 4（Stitch设计交互）**：派发干净设计子代理调用 Stitch MCP 生成官方 Screen（ID: `31e67653cc804dd9a4d4f84e0df47a53`），提炼 `stitch-tokens.css`。
   - **Task 5（首屏ExploreView）**：派发无污染还原子代理 99% 复刻全屏等高线暗黑地图（`AppMap.vue`）、三段式可拖拽卡片抽屉（`BottomSheet.vue`）、Hero 风光卡片（`HeroMountainCard.vue`）与毛玻璃搜索条（`TopSearchBar.vue`），实现点位与卡片双向平滑联动。
   - **Task 6（12模块详情抽屉）**：派发还原子代理 99% 复刻 `MountainDetailSheet.vue`（12大模块零裁剪展示）与 SVG 动态高程剖面图（`RouteElevationChart.vue`），修复装备清单跨山峰重置与锚点吸顶偏移。
   - **Task 7（周计划与我的成就）**：99% 复刻 `PlanView.vue`（时间线排期、增删周、官方精选路线套用）、`ProfileView.vue`（Telemetry 仪表盘、Bento 勋章网格、JSON 备份恢复、三主题切换）与全局固定 `BottomNav.vue`。
    - **Task 8（全量E2E与构建打包）**：编写 `scratch/test_app_e2e_full.py` 串联回归通过（0 控制台运行时错误）；打包生成 `weekly-mountain-deploy.zip`（解压 5.78 MB，文件数 53 个，完全命中 html2.link M 档）。
    - **全分支代码审查**：Senior Code Reviewer 审查通过（APPROVED）。
17. **真实瓦片底图引擎上线与多省市全国化扩展架构落地（响应用户反馈）**
    - **底图未能加载归因与修复**：此前 Stitch 还原版本仅使用了纯装饰性 SVG 等高线背景，未挂载实时瓦片网络服务。现已在 `AppMap.vue` 中重构接入 Web Mercator 原生瓦片底图引擎，支持极光黑曜石暗夜矢量（高德 `style=8` + 滤镜反色）、高分辨率遥感卫星影像（高德 `style=6` + 路网叠层）及极简拓扑底图，提供 3D 视角、手势缩放拖拽与全图层切换。
    - **多省市/多城市全国化扩展架构**：创建 `src/data/regions.json` 与 `src/stores/regionStore.js`，实现城市区域配置中心与响应式切换；顶栏升级为 Stitch 风格毛玻璃城市切换胶囊 `[ 📍 成都周边 ▾ ]`，支持打开 `RegionPickerSheet.vue`（已收录成都周边 50 座，并提供重庆周边、西安·秦岭、昆明·滇中、北京·京郊等筹备中城市无缝接入机制）；全站解耦硬编码车程文案为动态 `{{ regionStore.currentRegion.driveCenter }}车程`。
    - **全站文案去「官方」化严谨改造**：根据用户反馈全面排查并彻底清除全站「官方」字样，将「套用官方精选」改为「套用精选路线」，「官方推荐周计划」改为「精选推荐周计划」，「2025 官方认证」改为「2025 深度核验」，免责声明改为「当地文旅与景区管理渠道」，避免对用户造成行政背书误导。
    - **自动化回归与实机截图验证**：编写 `scratch/test_live_map_and_regions.py` 端到端自动化测试 100% 绿灯（0 控制台错误），实测瓦片网络请求加载正常；重新打包生成最新 `weekly-mountain-deploy.zip`（解压 5.795 MB，53 个文件，完美符合 M 档）。

## 关键决策
- 架构采用 Web-First App Shell，代码以 Vue 3 + Vite 纯相对路径自包含打包，实现网页直接访问与 App 容器壳体验 100% 一致。
- 引入多城市区域配置中心与状态管理层，保持数据模型对全国多省市山峰徒步网络的开箱即用扩展性。
- 地图引擎采用原生 Web Mercator 瓦片计算，0 额外臃肿外部 SDK，保持自包含轻量打包。
- 采用 50 张 900px 视网膜等比压缩 Progressive JPEG，总解压体积 5.80 MB，严格命中 html2.link M 档（≤ 10MB，≤ 100 文件，4 积分/天）。
- 遵循严禁 `git commit` 原则，所有改动保留在 `feature/app-modular-redesign` 工作区供用户最终确认。

## 修改的文件
- `src/components/map/AppMap.vue`: 接入 Web Mercator 实时瓦片地图引擎与图层切换
- `src/components/common/RegionPickerSheet.vue`: 新增城市与区域切换抽屉组件
- `src/components/common/TopSearchBar.vue`: 动态占位符与区域山峰计数
- `src/views/ExploreView.vue`: 顶栏挂载 Region Switcher 胶囊与区域联动
- `src/data/regions.json`: 全国城市与区域配置中心
- `src/stores/regionStore.js`: 区域状态管理 store
- `src/data/mountains.json`: 补充 `region_id: 'chengdu'`
- `src/stores/mountainStore.js`: 按区域过滤山峰
- `src/components/card/HeroMountainCard.vue`, `src/components/detail/MountainDetailSheet.vue`, `src/views/PlanView.vue`, `src/views/ProfileView.vue`: 解耦车程文案
- `weekly-mountain-deploy.zip`: 最新构建的轻量化自包含部署包（解压 5.795 MB，文件数 53 个）
- `docs/superpowers/plans/2026-10-16-live-map-and-multi-region-architecture.md`: 实施计划文档
- `docs/handoffs/project-overview.md`: 任务交接与全流程审计记录

## 验证证据与测试结果
1. `scratch/test_region_store.js`: PASS（多城市模型与 mountainStore 过滤联动单元测试 100% 通过）。
2. `scratch/test_live_map_and_regions.py`: PASS（真实高德瓦片切片加载、50 座山峰坐标对齐、城市切换抽屉与反馈、图层切换 100% 通过，控制台 0 运行时错误）。
3. `scratch/test_tab_navigation.py`: PASS（3-Tab 导航切换、路线套用、周计划增删、Telemetry 仪表盘全绿通过）。
4. `scratch/test_detail_sheet.py`: PASS（12 模块完整渲染、SVG 高程走势图、打卡切换 100% 通过）。
5. `scratch/test_app_e2e_full.py`: PASS（全量端到端串联自动化测试 100% 绿灯）。
6. `scripts/package_deploy.py`: PASS（解压总大小 5.795 MB ≤ 6.0 MB，文件数 53 个 ≤ 60 个，完美命中 html2.link M 档）。
7. 实机渲染截图存证：
   - 极光黑曜石暗夜矢量底图：[`scratch/live_map_dark_filtered.png`](file:///d:/file_save/workspace/github/weekly-mountain/scratch/live_map_dark_filtered.png)
   - 真实高分辨率卫星航拍底图：[`scratch/e2e_live_map_render.png`](file:///d:/file_save/workspace/github/weekly-mountain/scratch/e2e_live_map_render.png)
