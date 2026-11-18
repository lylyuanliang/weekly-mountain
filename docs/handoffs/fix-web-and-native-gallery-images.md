# 主题：修复 Web 与 Native 画册图片加载及地域刷新数据集错乱问题交接

- 当前状态：已完成 (completed)
- 涉及阶段：
  1. 根因深度排查：
     - **Web 网页端画册根因**：先前为给 Android APK 瘦身（从 43MB 降至 27.7MB），清理了 `assets/mountains/` 下的 108 张重庆画册大图。旧的 `scripts/copy_assets.js` 仅以 `assets/mountains/` 为唯一图片源拷贝至 `dist/assets/mountains`，且 Vite 开发服务器在请求 `/assets/mountains/*.jpg` 时仅查找根目录 `assets/mountains/`，导致 Web 模式下重庆山峰实景大图返回 404（Vite SPA 降级返回 text/html），最终触发 `<img>` 标签 `@error` 降级显示几何拓扑占位图；
     - **Native 原生端画册根因**：`src/services/resourcePackService.js` 中的 `_extractZipEntries` 针对画册包中的 JPG 二进制文件错误地采用了 `entry.async('string')` 和 `Encoding.UTF8` 写入本地私有目录，导致二进制字节序列严重损坏，Android WebView 无法正常解码；且 `downloadAndInstallGallery` 在下载失败时静默捕获并错误写入已安装标记；
     - **切换地域刷新后数据与视图错乱根因**：
       - `src/stores/regionStore.js`: 页面刷新时从 `localStorage` 读取到 `currentRegionId = 'chongqing'`，但未触发 `loadActiveRegion`；
       - `src/stores/mountainStore.js`: `mountains` 被静态初始化为 `mountainsData`（成都 51 座山），`selectedMountainId` 默认写死为成都龙泉山（`longquanshan`），页面刷新无生命周期自动载入持久化地域数据；
       - `src/stores/mountainStore.js`: `filteredMountains` 曾存在 `allSameRegion` 判断，导致在重庆视图下异常穿透显示成都 51 座山峰并计算距重庆中心的荒谬距离；
       - `src/components/common/TopSearchBar.vue`: 按照 `m.region_id === 'chongqing'` 统计成都数据集得出 0，导致筛选芯片显示 `全部 (0)`；
       - `src/components/map/AppMap.vue`: `onMounted` 钩子盲目使用 `mountainStore.selectedMountainId`（`longquanshan`，成都坐标）强行覆写地图中心，导致地图视口跳回成都并显示成都经纬度。
  2. 架构级分层治理与自愈：
     - **Vite 开发服务器中间件升级**（[`vite.config.js`](file:///d:/file_save/workspace/github/weekly-mountain/vite.config.js)）：在 `configureServer` 中新增 `/assets/mountains` 中间件，请求静态图片时优先查找基线 `assets/mountains/`，未命中时无缝自动穿透至各地域画册目录（`src/data/regions/*/gallery/`），并设置正确的 `image/jpeg` MIME 与缓存头；
     - **Web 生产构建全量汇聚**（[`scripts/copy_assets.js`](file:///d:/file_save/workspace/github/weekly-mountain/scripts/copy_assets.js)）：构建 Web 产物时，将成都基线底图（153张）与所有扩展地域画册图片（108张重庆画册）全量同步至 `dist/assets/mountains`（共 261 张，27.09MB），确保 Web 线上部署免下载全量畅享实景大图；
     - **Android 安装包严格边界隔离**（[`scripts/sync_android_assets.js`](file:///d:/file_save/workspace/github/weekly-mountain/scripts/sync_android_assets.js)）：在将 `dist/` 资产同步至 Android 原生工程时，严格基于成都基线白名单进行物理隔离，自动剥离非基线画册大图，确保 Android 原生 assets 保持仅 153 张基线底图（20.22MB），安装包严格锁定在 27.7MB 极致轻量；
     - **Native 资源包二进制安全解压**（[`src/services/resourcePackService.js`](file:///d:/file_save/workspace/github/weekly-mountain/src/services/resourcePackService.js)）：`_extractZipEntries` 识别 `.(jpg|jpeg|png|webp|bin|zip)` 二进制文件后缀，采用 `entry.async('base64')` 读取并以原生二进制安全写入 Capacitor 本地数据目录，保证解压图片 100% 字节一致性；修复画册下载失败时的假安装状态漏洞；
     - **Store 启动期自愈联动**（[`src/stores/mountainStore.js`](file:///d:/file_save/workspace/github/weekly-mountain/src/stores/mountainStore.js)、[`src/stores/regionStore.js`](file:///d:/file_save/workspace/github/weekly-mountain/src/stores/regionStore.js)）：`mountainStore` 感知持久化地域 `weekly_mountain_region`，若为非成都地域，初始集合安全置空且 `selectedMountainId` 为 null，并在 store 构造期立即触发 `loadActiveRegion` 异步热挂载；`regionStore` 在 `refreshInstalledPacks` 中双向校验 mountainStore 挂载地域强一致性；
     - **地图挂载与标记强隔离**（[`src/components/map/AppMap.vue`](file:///d:/file_save/workspace/github/weekly-mountain/src/components/map/AppMap.vue)）：`onMounted` 增加归属地域判定，仅当选中山峰归属于当前地域时才以此为中心，否则平滑居中当前地域城市中心；`mountainPositions` 标记点渲染增加地域过滤防闪烁；
     - **顶部搜索与抽屉计数兜底**（[`src/components/common/TopSearchBar.vue`](file:///d:/file_save/workspace/github/weekly-mountain/src/components/common/TopSearchBar.vue)、[`src/components/drawer/BottomSheet.vue`](file:///d:/file_save/workspace/github/weekly-mountain/src/components/drawer/BottomSheet.vue)）：异步加载中若数据尚未就绪，自动回退取用当前地域收录名额（36 / 51），杜绝瞬时闪烁 `全部 (0)`；路况预警通报区分成都与重庆。
- 恢复入口：
  - Vite 开发配置：[`vite.config.js`](file:///d:/file_save/workspace/github/weekly-mountain/vite.config.js)
  - 生产资产同步：[`scripts/copy_assets.js`](file:///d:/file_save/workspace/github/weekly-mountain/scripts/copy_assets.js)
  - Android 资产隔离：[`scripts/sync_android_assets.js`](file:///d:/file_save/workspace/github/weekly-mountain/scripts/sync_android_assets.js)
  - 资源包解压服务：[`src/services/resourcePackService.js`](file:///d:/file_save/workspace/github/weekly-mountain/src/services/resourcePackService.js)
  - 山峰 Store 挂载：[`src/stores/mountainStore.js`](file:///d:/file_save/workspace/github/weekly-mountain/src/stores/mountainStore.js)
  - 地域 Store 联动：[`src/stores/regionStore.js`](file:///d:/file_save/workspace/github/weekly-mountain/src/stores/regionStore.js)
  - 地图中心联动：[`src/components/map/AppMap.vue`](file:///d:/file_save/workspace/github/weekly-mountain/src/components/map/AppMap.vue)
  - 探索视图防护：[`src/views/ExploreView.vue`](file:///d:/file_save/workspace/github/weekly-mountain/src/views/ExploreView.vue)

---

## 自测验证结果与证据记录

1. **页面刷新自愈模拟实测 (Node.js ESM)**：
   - 模拟 `weekly_mountain_region = 'chongqing'` 重新启动 Pinia：
     - `regionStore.currentRegionId` ➔ `chongqing`
     - `mountainStore.mountains.length` ➔ `36`（重庆 36 座山）
     - `mountainStore.selectedMountainId` ➔ `jinyunshan`（缙云山，首座标杆名山）
     - `mountainStore.filteredMountains.length` ➔ `36`
     - 首座名山名称 ➔ `缙云山`
2. **Vite 开发服务器实测**：
   - 请求重庆铁山坪画册：`curl -I http://localhost:5173/assets/mountains/tieshanping.jpg` ➔ `HTTP/1.1 200 OK`, `Content-Type: image/jpeg`, 返回 58,993 字节完整图片；
   - 请求重庆副图画册：`curl -I http://localhost:5173/assets/mountains/tieshanping-2.jpg` ➔ `HTTP/1.1 200 OK`, `Content-Type: image/jpeg`；
   - 请求成都基线图片：`curl -I http://localhost:5173/assets/mountains/longquanshan.jpg` ➔ `HTTP/1.1 200 OK`, `Content-Type: image/jpeg`。
3. **Web 生产构建 (`npm run build:release`) 资产审计**：
   - `dist/assets/mountains/`：精确收纳 261 张全量名山风光大图（成都 153 + 重庆 108），Web 端免安装体验 100% 完整；
   - `android/app/src/main/assets/public/assets/mountains/`：精准过滤保留 153 张成都基线底图（20.22MB），扩展地域画册 0 冗余混入。
4. **自动化测试套件通过率**：
   - `node tests/test_store_multi_region.js`（7/7 项 100% 通过）；
   - `node tests/test_resource_pack_service.js`（11/11 项 100% 通过）；
   - `node tests/test_weather_and_gallery_resilience.js`（5/5 项 100% 通过）。
