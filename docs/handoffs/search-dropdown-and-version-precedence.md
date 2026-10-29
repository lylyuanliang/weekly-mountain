# 任务交接与状态记录：搜索下拉候选浮层、搜索结果体验重塑与高版本防降级策略

> 规范依据：`AGENTS.md` / `GEMINI.md` 全局规约与任务交接硬门禁

---

## 1. 任务背景与核心目标

### 1.1 背景来源
- **工单 1 (`#1793098663495`)**：
  1. “搜索给出下拉候选项”
  2. “这个样式分析下看看能不能优化下，现在体现不出我的搜索结果，好好分析”
  3. “版本号继续迭代增加”
- **工单 2 (`#1793098834226`)**：
  1. “正式功能里面的更新按照我们当前版本的沟通处理即可”
  2. “调试里面的更新依然要保持内网穿透的地址，方便我及时下载最新包进行测试”
  3. “如果我下载了高版本的测试包，然后又点击了正式功能里面的检查更新，交互结果你想想怎么处理合适（降版本肯定不行）”

### 1.2 核心目标与完成情况
- [x] **搜索体验重构**：
  - 在 `TopSearchBar.vue` 下方实现黑曜石 Alpine 风格下拉候选列表，实时展示山峰缩略图、关键词高亮、所属区县、海拔、市中心直线距离与难度标签；
  - 点击候选项直接收起软键盘（`blur()`）、关闭浮层、精准聚焦并展开该山峰；
  - 支持无结果空状态提示与快捷热门搜索词推荐（赵公山、虹口、青城后山等）。
- [x] **搜索结果视觉重塑**：
  - 在 `BottomSheet.vue` 中，当处于搜索态时，抽屉标题动态切换为中文**`搜索结果`**，副标突出**`匹配 X 座`**；
  - 提供快捷“清除搜索”按钮；
  - 搜索态自动收纳巴朗山等非核心路况预警条幅，释放移动端下半屏空间，彻底解决软键盘遮挡痛点；
  - 在 `HeroMountainCard.vue` 轮播卡片中增加脉冲金绿「搜索匹配」徽章，使搜索结果一目了然。
- [x] **高版本防降级策略与调试源隔离**：
  - 在 `updateStore.js` 与 `AppUpdateModal.vue` 中实现先行内测版防降级三态判定：
    - `cmp > 0`：存在新稳定版，提供免跳转升级；
    - `cmp === 0`：当前已是最新稳定发布版；
    - `cmp < 0`：当前运行版本高于官方稳定版（内测先行版），自动弹出专属「当前为先行内测版」勋章态，明确提示“防降级保护机制已拦截，根据 Android 规范无法向低版本覆盖安装，无需也不可降级更新”，消除降级覆盖报错风险；
  - 调试面板（`debugStore.js`）继续维持内网穿透与本地 APK 直连下载通道。
- [x] **版本号升级**：
  - 递增至 **`0.0.1.006`**，`BUILD_CODE = 6`；
  - 同步更新 `src/config/version.js`、`package.json`、`public/version.json`。
- [x] **自动化测试与双变体 APK 归档**：
  - 编写并执行 `scratch/verify_search_and_version_flow.py`，端到端 5 步场景 100% 通过；
  - 编译归档 `weekly-mountain-v0.0.1.006-release.apk` (28.39 MB) 与 `weekly-mountain-v0.0.1.006-debug.apk` (29.03 MB)；
  - Release APK 经敏感信息扫描确认 0 泄露。
- [x] **工单闭环与哨兵机制**：
  - 工单 `#1793098663495` 与 `#1793098834226` 均已标记为 `completed` 并附带详细决策回复。

---

## 2. 修改文件清单
1. `src/config/version.js`：版本升级为 `0.0.1.006`，`BUILD_CODE = 6`
2. `package.json`：同步升级为 `0.0.1.006`
3. `public/version.json`：生成 `v0.0.1.006` 发版元数据与优化日志
4. `src/services/updateService.js`：优先查询远端 CDN 确保真实版本比对
5. `src/stores/updateStore.js`：实现 `versionDiffStatus` 三态比较与防降级
6. `src/components/common/AppUpdateModal.vue`：新增先行内测版专属火箭勋章与防降级说明
7. `src/components/common/TopSearchBar.vue`：实现搜索建议下拉浮层、关键词高亮与热门词推荐
8. `src/views/ExploreView.vue`：接入 `@mountain-select` 事件联动
9. `src/components/drawer/BottomSheet.vue`：搜索态专属标题「搜索结果 (匹配 X 座)」、收起预警、清除搜索
10. `src/components/card/HeroMountainCard.vue`：卡片增加「搜索匹配」脉冲徽章
11. `scratch/verify_search_and_version_flow.py`：5 步端到端自动化测试脚本

---

## 3. 自测验证结果
- **E2E 自动化测试**: `python scratch/verify_search_and_version_flow.py`
  - 步骤 1: 搜索输入“虹”，下拉浮层弹出，展示“虹口·高原村 L1 轻松 都江堰市 · 1000m · 距市中心 64.1km” -> PASS
  - 步骤 2: 点击条目，输入法软键盘收起，抽屉标题切换为“搜索结果”，卡片展示“搜索匹配”徽章 -> PASS
  - 步骤 3: 无结果词搜索，空状态提示友好展现，点击热门推荐词“赵公山”成功刷新候选列表 -> PASS
  - 步骤 4: 先行版版本检查（本地 0.0.1.006 vs 远端稳定版 0.0.1.005），触发先行内测版弹窗并展示防降级保护机制 -> PASS
  - 步骤 5: 点击先行版确认按钮关闭弹窗 -> PASS
- **生成的快照证据**:
  - `test_search_suggestions_open.png`
  - `test_search_result_card.png`
  - `test_ahead_of_release_modal.png`
- **安全检查**: `releases/weekly-mountain-v0.0.1.006-release.apk` 0 敏感泄露（无 cpolar、无调试面板）。

---

## 4. 恢复入口与后续维护
- 后台开发服务: `npm run dev -- --host --port 5173` (持续运行)
- 哨兵监听服务: `python scripts/watch_mobile_feedback.py` (必须非 daemon 异步重启)
- APK 产物路径: `releases/weekly-mountain-v0.0.1.006-release.apk`
