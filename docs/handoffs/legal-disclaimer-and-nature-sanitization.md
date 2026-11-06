# 主题：法律免责合规、项目性质消歧与历史版本存档声明落地

- 当前状态：已完成 (completed)
- 最后更新时间：2026-11-06
- 恢复入口：`README.md`, `src/data/mountains.json`, `src/components/common/LegalDisclaimerModal.vue`, `src/components/detail/MountainDetailSheet.vue`, `src/components/achievement/AlpineAchievementPosterModal.vue`, `.github/workflows/build-apk.yml`

## 1. 目标与背景
防范户外路线信息传播中被“合理信赖为专业安全指南”或“安全保证承诺”的民事法律风险，结合两份核心法律与合规指导原则全面排查与修正：
1. **明确性质 (Explicit Nature)**：首屏与弹窗显著说明本仓库为个人业余路线记录/互联网公开数据整理，绝非专业安全指南，不构成对路线安全性、可行性的保证或推荐；
2. **具体提示已知风险 (Specific Known Risks)**：保留并强化具体客观危险点，杜绝笼统的“注意安全”；
3. **避免安全承诺式表述 (Eliminate Safety Commitment Words)**：全面清理“新手友好”、“老少皆宜”、“亲子友好”、“安全替代路线”、“路况安全”、“毫无难度”、“小白慎徒”等主观适宜性保证词汇，替换为客观物理特征描述；
4. **朋友圈分享与海报去背书化 (Neutral Sharing & De-officialization)**：将海报与导出中的“官方认证数字档案”、“ALPINE VERIFIED”、“防伪认证编码”替换为“个人高山足迹记录”、“ALPINE LOG”、“个人打卡编码”；
5. **历史版本与旧版性质明确隔离 (Historical Versions as Archive Only)**：在 `README.md` 首屏、`docs/releases/` 以及 `.github/workflows/build-apk.yml` 的 Release Notes 自动化生成模版中统一定位旧版为“技术研发历史存档”，明确声明“不反映当前的地理与风险认知，严禁作为出行依据，请始终以最新版本为准”。

## 2. 关键决策与实施内容
1. **`README.md` 顶栏与口号重构**：
   - 顶部增加 GitHub Alert `> [!IMPORTANT]`，包含明确性质声明与历史版本时效性特别声明；
   - Slogan 从“一站式现代化移动端高山拓扑手册 & 智能路线规划器”修正为“个人高山拓扑记录与开源离线数据看板”；
   - 强化文末开源协议与安全免责第 3 条，明确非安全指南与历史存档性质。
2. **`index.html` 网页标题去手册化**：
   - 标题由 `<title>成都周边每周一山 · 攻略手册</title>` 修正为 `<title>成都周边每周一山 · Alpine Explorer (个人足迹记录与数据看板)</title>`；
   - description 移除“徒步攻略”导向。
3. **法律免责弹窗强化 (`LegalDisclaimerModal.vue`)**：
   - 注入核心黄金声明：“本应用与数据库纯属个人业余路线记录及公开地理数据整理，绝非专业安全指南，亦不构成对任何户外路线安全性、可行性的保证或推荐”；
   - 定位从“数字向导工具”修正为“个人开源之非营利性数字记录工具”。
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
- `README.md`: 顶栏重要性质与旧版存档声明、去手册化 Slogan、文末免责条款强化
- `index.html`: 网页标题去手册化
- `src/components/common/LegalDisclaimerModal.vue`: 注入法定免责黄金句
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
1. **代码规范与格式检查**：`git diff --check` 结果 0 错误；
2. **违规词汇全量复核**：扫描 `src/` 与 `public/`，违规主观词（“新手友好”、“老少皆宜”、“亲子友好”、“安全替代”、“官方认证”、“官方推荐”、“毫无难度”、“小白慎徒”、“安全性高”）存量降为 0；
3. **JSON 结构完整性**：`src/data/mountains.json`、`mountain_tracks.json`、`waypoints.json` 经 `json.loads` 严格校验，解析 100% 成功；
4. **构建编译**：`npm run build` 成功完成，模块转换与打包零报错，Android 资产自动同步验证全部通过。

## 5. 恢复与后续步骤
所有修改均已就绪。根据用户要求，后续如需提交代码，严格采用原子提交规范分批提交并推送到远端，但**坚决不打 tag**。
