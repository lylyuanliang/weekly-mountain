# 主题：全域显眼位置集成 Cloudflare Pages 官方免安装预览地址

- 当前状态：已完成 (completed)
- 最后更新时间：2026-11-10 09:53
- 恢复入口：`README.md`, `src/views/ProfileView.vue`, `docs/DEPLOYMENT.md`, `package.json`

## 1. 目标与背景
《每周一山 · 成都周边50座山》拥有基于 Cloudflare Pages 全球 Anycast CDN 部署的在线免安装体验站点（`https://weekly-mountain.pages.dev/`），具备国内极速直连、免下载安装包、PWA 移动端轻应用秒开体验。
为解决此前预览地址入口分散、不易被初次访问者发现的问题，需在项目最显眼的位置（README 顶部中轴、徽标区、快速导航、界面画廊、部署方案、工程元数据以及客户端「我的」页面）进行全方位显眼曝光。

## 2. 核心落地与修改清单

### 2.1 主 README 显眼入口矩阵 (`README.md`)
1. **中轴大徽标 (Hero Badge)**：在标题下方居中醒目位置增设专用 Shields 徽标：
   `🌐 Cloudflare Pages 在线免安装预览 · weekly-mountain.pages.dev`
2. **快速导航锚点 (Quick Navigation)**：在导航栏首位加入加粗直达入口：
   `🚀 立即在线体验 • 核心特性 • 界面预览 ...`
3. **顶栏醒目提示块 (Prominent Callout Box)**：紧随头部之后增设 GitHub Alert `[!TIP]` 卡片，详细说明免安装、手机浏览器添加到主屏幕（PWA）的操作指引；
4. **高山体验精选画廊横幅 (Gallery Banner)**：在真机实测画廊尾部追加直达链接提示；
5. **线上部署与发布方案 (Deployment Section)**：在云端托管清单首位标明 `🌐 Cloudflare Pages（官方生产站 · 极速直达）`。

### 2.2 部署指引文档 (`docs/DEPLOYMENT.md`)
- 更新第五节《线上托管地址与回查索引》首行，将官方生产主站明确标注为 `https://weekly-mountain.pages.dev/`。

### 2.3 客户端「我的」页面常设矩阵 (`src/views/ProfileView.vue`)
- 在底部社区与开源入口矩阵中，新增「🌐 官方在线体验 (Cloudflare)」按钮，支持在移动端浏览器或原生客户端中一键外链跳转。

### 2.4 工程元数据 (`package.json`)
- 新增 `"homepage": "https://weekly-mountain.pages.dev"`，使 GitHub 仓库主页侧边栏（About 区域）直接展示官方演示直链。

## 3. 自测验证
- `npm run build`：0 错误，0 警告，静态资源同步成功；
- `git diff --check`：0 空格与换行警告；
- 远程连通性校验：`https://weekly-mountain.pages.dev/` 返回 HTTP 200，HTML 正常加载渲染。
