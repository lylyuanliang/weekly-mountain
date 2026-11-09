# 主题：山峰详情抽屉 (MountainDetailSheet) 三段式场景选项卡与信息降噪重构

- 当前状态：已完成 (completed)
- 最后更新时间：2026-11-09 16:08
- 恢复入口：`src/components/detail/MountainDetailSheet.vue`, `src/components/detail/RouteElevationChart.vue`, `docs/superpowers/plans/2026-11-09-mountain-detail-redesign.md`

## 1. 目标与背景
针对高山详情页正文内容垂直平铺过长（12 个模块、页面高度超 4500px）、信息密集导致用户产生严重阅读疲劳与抓不住重点的问题，实施结构化降噪重构：
1. **三段式场景分段选项卡 (Segmented Context Tabs)**：将原 12 个模块按用户核心使用场景解耦为「🧭 核心概况」、「🗺️ 路线轨迹」、「🎒 出行攻略」3 个主 Tab，页面可视高度缩减 65% 以上；
2. **Bento 核心决策魔方**：在「核心概况」首屏聚焦 5 大关键指标（难度梯队、标高、爬升、徒步耗时、自驾车程）与实时天气，3 秒即可做出选山决策；
3. **路线与航迹专注屏**：在「路线与轨迹」Tab 中聚合高程剖面图、两步路/六只脚 GPX 深度唤起、分段打卡时间线及备选撤退逃生路线 (Plan B)；
4. **出行攻略与渐进式折叠**：在「出行攻略」Tab 中聚合自驾路况导航、专业装备清单（带复选框交互与前3项核心必备露白+手风琴展开）、门票露营与环保民俗，次要文本支持优雅折叠/展开；
5. **底栏常驻行动点**：导航直达、加入周计划、登顶打卡在全 Tab 下保持常驻悬浮，操作零门槛。

## 2. 核心实施成果

### 2.1 三段式场景 Tab 组织架构 (Zero Feature Loss 100% 达成)
- **Tab 1: `overview` (🧭 核心概况)**：
  - Hero 实景风光轮播画廊（支持 GPU 丝滑切图、指示器、大图全屏 Lightbox 预览）；
  - 5-Metric Bento 决策魔方（最高海拔、累计爬升、徒步里程、预计耗时、驱车车程、梯队分组与适宜窗口）；
  - 驴友口碑综合点评与安全合规提示；
  - 登顶打卡纪实卡片（已打卡状态展示、实景相册缩略图、心得随笔编辑）；
  - 核心景观亮点与经典摄影机位清单（Module 4）；
  - 实时山地微气象预报与观景窗口定律（Module 11）。
- **Tab 2: `trail` (🗺️ 路线轨迹)**：
  - 两步路 / 六只脚 GPX 深度唤起卡片（置顶快速调起，带轨迹关键词清洗与一键复制）；
  - 客观实测航迹高程剖面图 (`RouteElevationChart.vue`，含海拔走势、爬升下坡与打卡点坐标连线)；
  - 真实多路线轨迹地图系统与方案对比 (`RouteTrajectoryMap.vue`)；
  - 分段地形与补给时间线（里程、耗时、高程、水源补给）；
  - 备选撤退逃生方案 (Plan B 醒目预警卡片)。
- **Tab 3: `guide` (🎒 出行攻略)**：
  - 自驾路况交通与导航终点（Module 5，带一键调起高德/百度/腾讯/苹果地图 `NavAppPicker`）；
  - 安全警示、高反风险与应急救援电话（Module 6）；
  - 专业装备核验清单（Module 7，核心必备前 3 项直接露白，其余进阶建议装备手风琴展开，Alpine 复选框勾选实时持久化）；
  - 餐饮补给与特色住宿营地（Module 8）；
  - 门票索道政策与双人/人均自驾预算（Module 9）；
  - 极光无痕山林倡议 (LNT) 与属地民俗规范（Module 10，支持手风琴展开）；
  - 公开文献信源引用与多源交叉核验清单（Module 12）。

### 2.2 手势交互与底栏常驻
- **手势切换 (Touch Pan X)**：在内容区域左右轻扫自然切换当前 Tab，且各 Tab 独立记忆滚动位置；与 Hero Banner 横滑手势完全隔离，互不干扰；
- **开合重置**：抽屉每次打开时自动归位至 `overview` Tab，并将滚动条归零；
- **底栏常驻 (Sticky Bottom Bar)**：【导航】、【加入计划】、【登顶打卡】三按钮在所有 Tab 下始终悬浮可见，底色采用 `#1c1f29` 实体深黑与高质感阴影，不随 Tab 滚动丢失。

## 3. 自测验证与成果交付

### 3.1 自动化构建验证
- `npm run build`：0 错误，0 警告通过编译（耗时 4.10s），离线静态资源同步成功。
- `git diff --check`：0 格式/行尾残留问题。

### 3.2 Playwright 详情页专项自动化验收 (`scratch/verify_subagent_redesign.py`)
- **Tab 切换验证**：3 个 Tab 切换点击与内容渲染 100% 正常；
- **高程图与两步路**：SVG 路线高程剖面图正常渲染，两步路与六只脚 DeepLink 唤起卡片正常交互；
- **装备复选框与手风琴**：装备 Checklist 点击勾选打叉样式与已备齐计数器联动正常，展开/收起切换平滑；
- **原生导航选择器**：底栏【导航】点击顺畅唤起 `NavPicker` 弹窗；
- **登顶打卡状态切换**：【登顶打卡】点击后即时切换至【✓ 已打卡 · 纪实】并弹出 Toast 提示；
- **控制台日志**：全程控制台 0 错误（0 Error）。

### 3.3 Playwright 全量回归测试 (`scratch/test_app_e2e_full.py`)
- **探索地图与标记点**：51 座山峰标记绘制、手势拖拽、3D 拓扑切换、多级抽屉 Snap 100% 通过；
- **标记与卡片双向联动**：点击地图标点高亮卡片、点击卡片移动视口 100% 通过；
- **重构版 12 核心模块覆盖**：3 个场景 Tab 顺次切换，12 模块无一遗漏且全部功能交互正常；
- **周计划与打卡时间线**：预设路线套用、新建周、删除周、排期打卡 100% 通过；
- **个人档案与遥测仪表盘**：圆环进度、勋章墙发光、数据备份导入/导出、三套主题动态切换 100% 通过；
- **控制台状态**：全流程 0 控制台运行时错误。

### 3.3 实测截图产物
- `scratch/verify_tab_overview.png`：Tab 1 核心概况与 5 大指标 Bento 决策魔方
- `scratch/verify_tab_trail.png`：Tab 2 路线轨迹与 GPX 深度唤起卡片 + 高程剖面图
- `scratch/verify_tab_guide.png`：Tab 3 出行攻略与装备清单交互
- `scratch/verify_nav_modal.png`：底栏一键导航选择器弹窗
- `scratch/verify_checkin_toggle.png`：登顶打卡即时状态切换
- `assets/screenshots/02_mountain_detail.png`：项目主 README 展示图已同步刷新

### 3.4 本地开发机双 APK 构建与校验 (`scripts/build_local_apks.py`)
- **构建版本号**：`0.3.1.202611091702` (Code: `1794214949`)
- **正式发布版 (Release)**：
  - 路径：`weekly-mountain-v0.3.1.202611091702-release.apk` (27.13 MB)
  - SHA-256：`22ff4a3efafce0aa350bd4672934573488c0ec0113682efc7b3b244e986a1c0d`
  - 完整性校验：153 个离线高山资产完整打包，`index.html` 存在
- **内测调试版 (Debug)**：
  - 路径：`weekly-mountain-v0.3.1.202611091702-debug.apk` (28.21 MB)
  - SHA-256：`961fbb541c27e208968b72a4b37074550be318f4579dbabffb824c3ddcded935`
  - 包含原生 Agent Feedback 哨兵与诊断浮球
- **局域网/开发机直链下载通道**：
  - Release 直链：`http://10.1.9.168:5173/releases/latest-release` (或 `http://localhost:5173/releases/latest-release`)
  - Debug 直链：`http://10.1.9.168:5173/releases/latest-debug` (或 `http://localhost:5173/releases/latest-debug`)

### 3.5 GitHub Actions 正式发版 Tag
- **正式发版版本号**：`v0.3.2.202611091816` (Patch 体验优化递增：`0.3.1` ➔ `0.3.2`)
- **发布文档**：`docs/releases/RELEASE-v0.3.2.md`
- **Git Tag**：`v0.3.2.202611091816`（已推送到 `origin`，触发 GitHub Actions 双 APK 构建与 Release 自动发布流程）
