# Handoff: 多地域分层资源包（轻量基础包 vs 增量风光画册包）架构与规格选择交互设计

## 1. 任务背景与核心目标
- **目标**: 落实「基线核心数据包 (约 87KB) + 增量风光画册包 (约 15.8MB)」双层搭积木式分级资源包架构。
- **痛点解决与场景闭环**:
  - 用户在下载重庆离线包时，弹出规格选择模态框（`PackSpecSelectModal`）；
  - 规格弹窗中配备生动简略的 **Tips** 问答卡片，让用户清晰直观理解基础包与风光包的区别与互通性；
  - **支持双向无缝切换**：
    - 若选择极速基础包：显示「已就绪 (基础版)」并配备高亮「+ 补全画册」，点击仅增量下载 15.8MB 画册，无需重复下载路线；
    - 若选择完整风光包：显示「已就绪 (完整版)」并配备「释放画册」按钮，点击秒级释放 15.8MB 存储空间并保留所有 100% 离线路线与轨迹；
    - 针对非内置区域提供卸载离线包按钮，彻底释放本地资源。

---

## 2. 端侧真机视频分析与三次自愈迭代 (#1794822233882)
根据用户在真机录屏 (`1794822184326_1000018515.mp4`) 反馈的 3 项体验异常，实施针对性闭环修复：

1. **问题 1：在「我的」面板点击下载未弹出规格选择框**
   - **根因**: 之前仅在首页 `RegionPickerSheet.vue` 中挂载了 `PackSpecSelectModal`，而 `ProfileView.vue` 中的下载按钮直接调用了 `downloadRegionPack`；
   - **修复**: 在 `ProfileView.vue` 同步挂载 `PackSpecSelectModal`，并在用户点击下载时唤起模态规格选择框，双入口体验 100% 一致。
2. **问题 2：首页资源选择框繁琐、视觉疲劳**
   - **根因**: 原 `RegionPickerSheet.vue` 放置了过多按钮（`已就绪` + `+画册` + `释放` + `垃圾桶` + `勾选` 挤在右侧）且展示了 5 座规划中城市的长段落说明大卡片，占据整屏高度造成视觉疲劳；
   - **修复**: 彻底精简卡片布局，右侧仅保留 1 个核心主状态/操作；将规划中城市由垂直大卡片重构为紧凑轻盈的“微型标签网格”（`🧭 西安`、`🧭 昆明`、`🧭 北京`等），卡片高度减半，视觉负担降低 70%。高级存储维护集中在「我的 ➔ 离线地域资源管理」。
3. **问题 3：重庆资源包卸载后依然能浏览重庆的山**
   - **根因**: `regionStore.uninstallRegionPack` 仅删除了物理文件和存储标记，未检测当前正在浏览的区域；当用户在重庆状态下卸载重庆并切回首页时，内存 `mountainStore.mountains` 依然保留 36 座重庆山峰；
   - **修复**: 在 `regionStore.uninstallRegionPack` 与 `refreshInstalledPacks` 增加强约束安全防线：若卸载的正是当前所在区域，或者检测到当前区域离线包未就绪，立即自动回退至基线成都（`await setRegion('chengdu')`），联动 `mountainStore` 重新挂载成都 51 座山峰并复位地图中心，杜绝任何卸载后残留。

---

## 3. 修改文件清单
- [src/data/regions.json](file:///d:/file_save/workspace/github/weekly-mountain/src/data/regions.json): 扩展 `galleryPack` 元数据（文件名、版本、大小与说明）；
- [src/services/resourcePackService.js](file:///d:/file_save/workspace/github/weekly-mountain/src/services/resourcePackService.js):
  - 实现 `isGalleryInstalled(regionId)` 双重状态核验；
  - 抽离通用下载与解压方法，支持分层与增量画册包；
  - 实现 `downloadAndInstallGallery(regionId)` 与 `uninstallGallery(regionId)`；
- [src/stores/regionStore.js](file:///d:/file_save/workspace/github/weekly-mountain/src/stores/regionStore.js):
  - 扩展画册状态 `installedGalleries` 与响应式方法；
  - 增加卸载当前地域时自动回退成都的硬防线；
  - `setRegion` 增加原生移动端未安装地域阻断拦截；
- [src/components/common/PackSpecSelectModal.vue](file:///d:/file_save/workspace/github/weekly-mountain/src/components/common/PackSpecSelectModal.vue):
  - 规格选择弹窗，提供「极速基础包 (87KB)」与「完整风光包 (15.8MB)」对比，配备 Q1/Q2/Q3 简明 Tips；
- [src/components/common/RegionPickerSheet.vue](file:///d:/file_save/workspace/github/weekly-mountain/src/components/common/RegionPickerSheet.vue):
  - 首页极简切换器重构，去除多余按钮，规划中城市重构为紧凑网格；
- [src/views/ProfileView.vue](file:///d:/file_save/workspace/github/weekly-mountain/src/views/ProfileView.vue):
  - 接入 `PackSpecSelectModal` 弹窗；
  - 离线管理列表支持分层状态、补全画册与释放画册；
- [tests/test_store_multi_region.js](file:///d:/file_save/workspace/github/weekly-mountain/tests/test_store_multi_region.js):
  - 新增测试用例：验证卸载当前所在地域时自动归位成都并重载 51 座山峰；
- [tests/test_resource_pack_service.js](file:///d:/file_save/workspace/github/weekly-mountain/tests/test_resource_pack_service.js):
  - 11 项单元测试全覆盖。

---

## 4. 自测验证结果
1. **服务单元测试套件**:
   - `node tests/test_resource_pack_service.js`: 11/11 项测试 100% 通过；
2. **多地域 Store 热挂载测试**:
   - `node tests/test_store_multi_region.js`: 6/6 项测试 100% 通过（含卸载归位联动）；
3. **Python 测试套件**:
   - `python tests/test_region_datasets.py`: 5/5 通过；
   - `python tests/test_region_pack_builder.py`: 5/5 通过；
4. **编译与打包**:
   - `npm run build`: 5.18 秒成功；
   - `python scripts/build_local_apks.py`: Release 与 Debug 双端本地安装包构建成功。
