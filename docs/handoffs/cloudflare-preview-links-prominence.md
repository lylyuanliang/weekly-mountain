# 主题：全域显眼位置集成 Cloudflare Pages 免安装在线预览地址

- 当前状态：已完成 (completed)
- 最后更新时间：2026-11-10 10:35
- 恢复入口：`README.md`, `src/views/ProfileView.vue`, `docs/DEPLOYMENT.md`, `src/data/mountains.json`

## 1. 目标与背景
1. 《每周一山 · 成都周边50座山》拥有基于 Cloudflare Pages 全球 Anycast CDN 部署的在线免安装体验站点（`https://weekly-mountain.pages.dev/`），具备国内极速直连、免下载安装包、PWA 移动端轻应用秒开体验。此前预览地址入口与 Releases 下载入口分散，需要统一归拢至 README 顶部最显眼位置。
2. **严格去行政化背书要求**：全站文案、页面组件、山峰数据库及文档中严禁出现“官方”字样，防止对个人非营利开源户外项目产生误解，全面替换为中立、严谨、客观的措辞（如“景区”、“正规渠道”、“公开公示”、“门市价”等）。

## 2. 核心落地与修改清单

### 2.1 主 README 显眼入口双链路聚合 (`README.md`)
1. **中轴大徽标 (Hero Badge)**：在标题下方居中醒目位置增设专用 Shields 徽标：
   `🌐 Cloudflare Pages 在线免安装预览 · weekly-mountain.pages.dev`
2. **快速导航首屏锚点 (Quick Navigation)**：在导航栏首位双线并行展示：
   `🚀 立即在线体验 • 📦 APK 下载 • 核心特性 • 界面预览 ...`
3. **顶栏醒目提示块双链路合并 (Prominent Callout Box)**：将原本分散在多处的在线体验与 Releases 下载提示统一收敛至首屏 `[!TIP]` 卡片：
   - 🌐 **【在线免安装直达】**：`https://weekly-mountain.pages.dev/`
   - 📱 **【Android 原生安装包下载】**：`https://github.com/lylyuanliang/weekly-mountain/releases`
4. **移除冗余低位提示**：移除此前淹没在界面预览 6 张大图底部的重复体验提示段落，保持版面清爽聚焦；
5. **线上部署与发布方案**：标明 `🌐 Cloudflare Pages（生产托管站 · 极速直达）`。

### 2.2 全站文案严禁“官方”字样彻底清洗
1. **数据库清洗 (`src/data/mountains.json`, `mountain_tracks.json`, `waypoints.json`)**：
   - 覆盖 835 处历史遗留数据字段（包括门票公示、公众号、救援电话、打卡顺序、线路推荐等）；
   - 转换为“门市公示价”、“景区微信公众号”、“属地应急救援”、“推荐打卡顺序”、“经典小环线”等客观用语；
2. **UI 组件与系统服务**：
   - `ProfileView.vue`：替换为「在线体验版 (Cloudflare)」；
   - `AppUpdateModal.vue`：替换为「备用发布渠道下载」；
   - `LegalDisclaimerModal.vue`：替换为「正规合规渠道」；
   - `updateService.js` / `platform.js` / `setupAgentFeedback.js` / `vite.config.js` 全量去“官方”化；
   - 修复 Vendor 依赖库回显，确保构建打包出的 `dist/` 与 Android assets 中 `官方` 计数为 0。

### 2.3 部署指引文档 (`docs/DEPLOYMENT.md`)
- 更新第五节《线上托管地址与回查索引》首行，将生产主站明确标注为 `https://weekly-mountain.pages.dev/`。

### 2.4 工程元数据 (`package.json`)
- 新增 `"homepage": "https://weekly-mountain.pages.dev"`。

## 3. 自测验证
- `git grep -n "官方"`：全库精确扫描返回 **0 处**匹配；
- `dist/` & Android assets：构建产物二次扫描返回 **0 处**匹配；
- `npm run build`：0 错误，0 警告，51 座山峰数据校验完整（JSON Validated: 51）；
- `git diff --check`：0 空格与换行警告。
