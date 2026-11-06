# 主题：法律免责合规、项目性质消歧与历史版本存档声明落地

- 当前状态：已完成 (completed)
- 最后更新时间：2026-11-06
- 恢复入口：`README.md`, `src/config/version.js`, `src/App.vue`, `src/components/common/LegalDisclaimerModal.vue`, `src/components/detail/MountainDetailSheet.vue`, `.github/workflows/build-apk.yml`

## 1. 目标与背景
防范户外路线信息传播中被“合理信赖为专业安全指南”或“安全保证承诺”的民事法律风险，结合两份核心法律与合规指导原则全面排查与修正：
1. **明确性质 (Explicit Nature)**：首屏与弹窗显著说明本仓库为个人业余路线记录/互联网公开数据整理，绝非专业安全指南，不构成对路线安全性、可行性的保证或推荐；
2. **具体提示已知风险 (Specific Known Risks)**：保留并强化具体客观危险点，杜绝笼统的“注意安全”；
3. **避免安全承诺式表述 (Eliminate Safety Commitment Words)**：全面清理“新手友好”、“老少皆宜”、“亲子友好”、“安全替代路线”、“路况安全”、“毫无难度”、“小白慎徒”等主观适宜性保证词汇，替换为客观物理特征描述；
4. **朋友圈分享与海报去背书化 (Neutral Sharing & De-officialization)**：将海报与导出中的“官方认证数字档案”、“ALPINE VERIFIED”、“防伪认证编码”替换为“个人高山足迹记录”、“ALPINE LOG”、“个人打卡编码”；
5. **历史版本与旧版性质明确隔离 (Historical Versions as Archive Only)**：在 `README.md` 首屏、`docs/releases/` 以及 `.github/workflows/build-apk.yml` 的 Release Notes 自动化生成模版中统一定位旧版为“技术研发历史存档”，明确声明“不反映当前的地理与风险认知，严禁作为出行依据，请始终以最新版本为准”；
6. **免责公约协议版本化与内容变更重弹确认门禁 (Disclaimer Versioning & Re-confirmation Gate)**：根据民法典格式条款显著提示与意思表示原则，若免责声明内容发生实质性合规修改，系统必须对所有用户（包括此前同意过旧版本的用户）自动重新弹出弹窗并展示升级横幅，用户重新独立勾选确认后方可写入最新版本标记。

## 2. 关键决策与实施内容
1. **`README.md` 顶栏与口号重构**：
   - 顶部增加 GitHub Alert `> [!IMPORTANT]`，包含明确性质声明与历史版本时效性特别声明；
   - Slogan 从“一站式现代化移动端高山拓扑手册 & 智能路线规划器”修正为“个人高山拓扑记录与开源离线数据看板”；
   - 强化文末开源协议与安全免责第 3 条，明确非安全指南与历史存档性质。
2. **`index.html` 网页标题去手册化**：
   - 标题由 `<title>成都周边每周一山 · 攻略手册</title>` 修正为 `<title>成都周边每周一山 · Alpine Explorer (个人足迹记录与数据看板)</title>`；
   - description 移除“徒步攻略”导向。
3. **免责协议版本号与重签机制 (`version.js`, `App.vue`, `LegalDisclaimerModal.vue`)**：
   - 引入 `LEGAL_DISCLAIMER_VERSION = '2026.11.06'`；
   - `App.vue` 启动挂载时校验 `localStorage.getItem('alpine_disclaimer_agreed_version') !== LEGAL_DISCLAIMER_VERSION`；
   - 若本地仅有旧版同意标记或版本不一致，强制再次弹出《户外安全须知与法律免责声明》；
   - 弹窗顶部为旧版升级用户展示“公约内容合规升级”横幅提示，用户勾选并点击同意后原子写入新版本号；
   - 弹窗标题栏附带微缩版本号胶囊。
4. **山峰详情抽屉强化 (`MountainDetailSheet.vue`)**：
   - 顶部及底部免责卡片强化非安全指南与自主决策警示；
   - 路况章节由“驾驶指南”修正为“自驾参考”。
5. **成就海报去背书化 (`AlpineAchievementPosterModal.vue`)**：
   - 移除“官方认证数字档案”，变更为“个人高山足迹记录”；
   - 印章微缩 SVG `VERIFIED` 替换为 `LOG`；
   - “防伪认证编码”替换为“个人打卡编码”。
6. **版本管理与 CI/CD Release 模版 (`build-apk.yml`, `sync_version.py`, `public/version.json`)**：
   - `.github/workflows/build-apk.yml` 的 `generate_notes.cjs` 顶部自动注入 `> [!WARNING] 【历史版本与风险认知特别声明】`；
   - `scripts/sync_version.py` 与 `public/version.json` 注入 `disclaimer` 字段；
   - `docs/releases/RELEASE-v0.3.0.md` 注入历史版本技术存档提示。
7. **数据层深度清洗 (`mountains.json`, `mountain_tracks.json`, `waypoints.json`)**：
   - 彻底清除 49+ 处主观适宜性与安全承诺（包括“新手友好”、“老少皆宜”、“亲子友好”、“安全替代路线”、“安全性高”、“路况安全”等）；
   - 将标签 `亲子友好` 升级为客观的 `和缓步道` / `成熟步道`；
   - 移除 `叠溪松坪沟` 等点位中的“官方推荐路线/顺序”。

## 3. 修改文件清单
- `src/config/version.js`: 新增 `LEGAL_DISCLAIMER_VERSION = '2026.11.06'`
- `src/App.vue`: 支持协议版本变更动态重弹检测
- `src/components/common/LegalDisclaimerModal.vue`: 注入版本号对比、协议更新提示横幅与新版签署落盘
- `README.md`: 顶栏重要性质与旧版存档声明、去手册化 Slogan、文末免责条款强化
- `index.html`: 网页标题去手册化
- `src/components/detail/MountainDetailSheet.vue`: 免责强化与自驾参考命名
- `src/components/achievement/AlpineAchievementPosterModal.vue`: 海报个人打卡中性化
- `src/components/common/AppUpdateModal.vue`: 移除“官方”前缀
- `src/components/card/CompactMountainCard.vue`: 标签体系同步
- `src/data/mountains.json`: 49+ 处主观安全词汇客观化清洗
- `src/data/mountain_tracks.json`: 移除官方推荐用语
- `src/data/waypoints.json`: 移除官方推荐顺序
- `.github/workflows/build-apk.yml`: Release Notes 模版注入历史版本存档警示
- `scripts/sync_version.py`: 增加 disclaimer 元数据
- `public/version.json`: 注入 disclaimer 元数据
- `docs/releases/RELEASE-v0.3.0.md`: 顶部历史存档提示
- `docs/handoffs/legal-disclaimer-and-nature-sanitization.md`: 本次交接文档

## 4. 验证与自测结果
1. **自动化端到端协议版本重签测试 (`scratch/test_disclaimer_versioning.py`)**：
   - 验证旧版协议用户启动时强制弹出免责弹窗并成功展示更新横幅；
   - 验证重新勾选同意后版本号落盘为 `2026.11.06`；
   - 验证刷新后免责弹窗不再重复弹出，全部 3 个测试用例 100% 通过；
2. **代码规范与格式检查**：`git diff --check` 结果 0 错误；
3. **违规词汇全量复核**：扫描 `src/` 与 `public/`，违规主观词存量为 0；
4. **构建编译**：`npm run build` 成功完成，模块转换与打包零报错，Android 资产自动同步验证通过。

## 5. 恢复与后续步骤
所有修改均已就绪。
