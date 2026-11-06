# 主题：法律免责合规、项目性质消歧与历史版本存档声明落地

- 当前状态：已完成 (completed)
- 最后更新时间：2026-11-06
- 恢复入口：`README.md`, `src/views/PlanView.vue`, `src/stores/planStore.js`, `src/config/version.js`, `src/App.vue`, `src/components/common/LegalDisclaimerModal.vue`, `src/components/detail/MountainDetailSheet.vue`, `.github/workflows/build-apk.yml`

## 1. 目标与背景
防范户外路线信息传播中被“合理信赖为专业安全指南”或“安全保证承诺”的民事法律风险，结合核心法律与合规指导原则全面排查与修正：
1. **明确性质 (Explicit Nature)**：首屏与弹窗显著说明本仓库为个人业余路线记录/互联网公开数据整理，绝非专业安全指南，不构成对路线安全性、可行性的保证或推荐；
2. **具体提示已知风险 (Specific Known Risks)**：保留并强化具体客观危险点，杜绝笼统的“注意安全”；
3. **避免安全承诺式表述 (Eliminate Safety Commitment Words)**：全面清理“新手友好”、“老少皆宜”、“亲子友好”、“安全替代路线”、“路况安全”、“毫无难度”、“小白慎徒”等主观适宜性保证词汇，替换为客观物理特征描述；
4. **剔除身份背书风险（如“资深领队调优”）**：彻底消除 UI 与数据层中任何自称或暗示“资深领队”、“领队调优”的背书字眼，避免反向击穿《民法典》第 1198 条“非组织者、非领队、不承担安全保障义务”的免责抗辩；
5. **朋友圈分享与海报去背书化 (Neutral Sharing & De-officialization)**：将海报与导出中的“官方认证数字档案”、“ALPINE VERIFIED”、“防伪认证编码”替换为“个人高山足迹记录”、“ALPINE LOG”、“个人打卡编码”；
6. **历史版本与旧版性质明确隔离 (Historical Versions as Archive Only)**：在 `README.md` 首屏、`docs/releases/` 以及 `.github/workflows/build-apk.yml` 的 Release Notes 自动化生成模版中统一定位旧版为“技术研发历史存档”，明确声明“不反映当前的地理与风险认知，严禁作为出行依据，请始终以最新版本为准”；
7. **免责公约协议版本化与内容变更重弹确认门禁 (Disclaimer Versioning & Re-confirmation Gate)**：根据民法典格式条款显著提示与意思表示原则，若免责声明内容发生实质性合规修改，系统必须对所有用户（包括此前同意过旧版本的用户）自动重新弹出弹窗并展示升级横幅，用户重新独立勾选确认后方可写入最新版本标记；
8. **README 徽标本地矢量化固化 (Local Vector Badges)**：根治第三方 shields.io 因网络延迟导致 GitHub Camo 代理报 `HTTP 504 Gateway Timeout` 裂图的问题，将徽章全量本地静态化保存在 `assets/badges/` 中，实现 0 外链依赖、100% 极速加载。

## 2. 关键决策与实施内容
1. **周计划去“领队背书”重构 (`PlanView.vue`, `planStore.js`)**：
   - 将“资深领队调优难度梯度，循序渐进”修正为“按公开爬升与海拔梯次归类，循序渐进”；
   - 将“可直接套用下方资深领队精选路线”修正为“可直接套用下方经典预设路线”；
   - 将 DOM 中的 `official-presets` 类名与 ID 重命名为 `curated-presets`；
   - 清除数据层中残余的“领队”字眼，确保全库唯一的“领队”仅存在于免责声明中声明“非领队、非组织者”。
2. **`README.md` 顶栏与口号重构**：
   - 顶部增加 GitHub Alert `> [!IMPORTANT]`，包含明确性质声明与历史版本时效性特别声明；
   - Slogan 从“一站式现代化移动端高山拓扑手册 & 智能路线规划器”修正为“个人高山拓扑记录与开源离线数据看板”；
   - 强化文末开源协议与安全免责第 3 条，明确非安全指南与历史存档性质。
3. **README 徽标转为本地高精 SVG (`assets/badges/`)**：
   - 抓取并固化全套 1:1 像素矢量 SVG 徽标；
   - `README.md` 切换为仓库相对路径引用，彻底绕开 GitHub Camo 504 裂图；
   - `scripts/sync_version.py` 增补对 `badge-version.svg` 的原子化版本文本同步。
4. **`index.html` 网页标题去手册化**：
   - 标题由 `<title>成都周边每周一山 · 攻略手册</title>` 修正为 `<title>成都周边每周一山 · Alpine Explorer (个人足迹记录与数据看板)</title>`；
   - description 移除“徒步攻略”导向。
5. **免责协议版本号与重签机制 (`version.js`, `App.vue`, `LegalDisclaimerModal.vue`)**：
   - 引入 `LEGAL_DISCLAIMER_VERSION = '2026.11.06'`；
   - `App.vue` 启动挂载时校验 `localStorage.getItem('alpine_disclaimer_agreed_version') !== LEGAL_DISCLAIMER_VERSION`；
   - 若本地仅有旧版同意标记或版本不一致，强制再次弹出《户外安全须知与法律免责声明》；
   - 弹窗顶部为旧版升级用户展示“公约内容合规升级”横幅提示，用户勾选并点击同意后原子写入新版本号；
   - 弹窗标题栏附带微缩版本号胶囊。
6. **山峰详情抽屉强化 (`MountainDetailSheet.vue`)**：
   - 顶部及底部免责卡片强化非安全指南与自主决策警示；
   - 路况章节由“驾驶指南”修正为“自驾参考”。
7. **成就海报去背书化 (`AlpineAchievementPosterModal.vue`)**：
   - 移除“官方认证数字档案”，变更为“个人高山足迹记录”；
   - 印章微缩 SVG `VERIFIED` 替换为 `LOG`；
   - “防伪认证编码”替换为“个人打卡编码”。
8. **版本管理与 CI/CD Release 模版 (`build-apk.yml`, `sync_version.py`, `public/version.json`)**：
   - `.github/workflows/build-apk.yml` 的 `generate_notes.cjs` 顶部自动注入 `> [!WARNING] 【历史版本与风险认知特别声明】`；
   - `scripts/sync_version.py` 与 `public/version.json` 注入 `disclaimer` 字段；
   - `docs/releases/RELEASE-v0.3.0.md` 注入历史版本技术存档提示。
9. **数据层深度清洗 (`mountains.json`, `mountain_tracks.json`, `waypoints.json`)**：
   - 彻底清除 49+ 处主观适宜性与安全承诺（包括“新手友好”、“老少皆宜”、“亲子友好”、“安全替代路线”、“安全性高”、“路况安全”等）；
   - 将标签 `亲子友好` 升级为客观的 `和缓步道` / `成熟步道`；
   - 移除 `叠溪松坪沟` 等点位中的“官方推荐路线/顺序”。

## 3. 修改文件清单
- `src/views/PlanView.vue`: 彻底剥离“资深领队”称谓与 official-presets ID
- `src/stores/planStore.js`: 预设计划客观体能描述
- `assets/badges/`: 固化 7 款核心技术栈矢量 SVG 徽标
- `README.md`: 徽标切换为本地资源，彻底解决 Camo 504 裂图；顶栏重要性质与旧版存档声明
- `scripts/sync_version.py`: 增加 badge-version.svg 同步与 disclaimer 元数据
- `src/config/version.js`: 新增 `LEGAL_DISCLAIMER_VERSION = '2026.11.06'`
- `src/App.vue`: 支持协议版本变更动态重弹检测
- `src/components/common/LegalDisclaimerModal.vue`: 注入版本号对比、协议更新提示横幅与新版签署落盘
- `index.html`: 网页标题去手册化
- `src/components/detail/MountainDetailSheet.vue`: 免责强化与自驾参考命名
- `src/components/achievement/AlpineAchievementPosterModal.vue`: 海报个人打卡中性化
- `src/components/common/AppUpdateModal.vue`: 移除“官方”前缀
- `src/components/card/CompactMountainCard.vue`: 标签体系同步
- `src/data/mountains.json`: 主观安全词汇客观化清洗与商业领队词汇剔除
- `src/data/mountain_tracks.json`: 移除官方推荐用语
- `src/data/waypoints.json`: 移除官方推荐顺序
- `.github/workflows/build-apk.yml`: Release Notes 模版注入历史版本存档警示
- `public/version.json`: 注入 disclaimer 元数据
- `docs/releases/RELEASE-v0.3.0.md`: 顶部历史存档提示
- `docs/handoffs/legal-disclaimer-and-nature-sanitization.md`: 本次交接文档

## 4. 验证与自测结果
1. **“领队”字眼全库排查**：业务与展示代码存量清零，全库唯一的“领队”字眼仅保留于免责声明中声明“非领队、非组织者、不承担安全保障义务”；
2. **GitHub Camo 504 裂图根治验证**：徽标已全部本地矢量化，彻底消除对 `img.shields.io` 的网络代理依赖；
3. **自动化端到端协议版本重签测试 (`scratch/test_disclaimer_versioning.py`)**：100% 通过；
4. **代码规范与格式检查**：`git diff --check` 结果 0 错误；
5. **构建编译**：`npm run build` 成功完成，模块转换与打包零报错，Android 资产自动同步验证通过。

## 5. 恢复与后续步骤
所有修改均已就绪。
