# 成都周边每周一山 · 攻略站

**线上地址：https://broken-surf-e858.lylyuanliang.workers.dev/**（Cloudflare Workers 静态资源托管）

# 成都周边每周一山 · 攻略站

单文件手机网页攻略：50 座成都周边可周爬的山，含深度攻略、真实坐标打卡点与可缩放地图、人均费用、未来 7 天天气、自定义排期与打卡统计。

## 本地打开

直接双击 `index.html`（或拷到手机用 Safari / Chrome 打开）即可，无需服务器。

## 免费发布方案

### 方案 A：Cloudflare Pages（推荐，国内访问相对最好）

1. 注册 https://dash.cloudflare.com （免费）
2. 左侧 **Workers & Pages → Create → Pages → Upload assets**
3. 把本 `site/` 目录里的文件（`index.html`、`.nojekyll`）整个拖进去上传
4. 得到 `https://<项目名>.pages.dev` 免费域名，自动 HTTPS + 全球 CDN
5. 之后每次更新：重新上传覆盖即可（也可绑定 Git 仓库自动构建）

- 免费额度：无限带宽、每月 500 次构建
- 优点：无需备案、访问速度通常优于 GitHub Pages、可绑自定义域名

### 方案 B：GitHub Pages（Git 工作流，最省心）

1. 在 GitHub 新建仓库（Public），例如 `weekly-mountain`
2. 把本目录内容推上去：

```bash
cd site
git init
git add .
git commit -m "init: 成都周边每周一山攻略站"
git branch -M main
git remote add origin git@github.com:lylyuanliang/weekly-mountain.git
git push -u origin main
```

3. 仓库 **Settings → Pages → Source: Deploy from a branch → Branch: main / (root) → Save**
4. 一两分钟后访问 `https://lylyuanliang.github.io/weekly-mountain/`

- 免费额度：仓库 1GB、每月 100GB 流量、软性 10 万次/月请求
- 注意：首页必须是 `index.html`（本目录已就绪）；`.nojekyll` 用于跳过 Jekyll 处理
- 注意：国内访问 GitHub Pages **时快时慢**，介意的话用方案 A 或 C

### 方案 C：Gitee Pages（码云，国内服务器）

- 免费，但**需要实名认证**；Pages 服务对公开仓库有审核/开关限制，且自定义域名通常要求已备案
- 适合：只在国内访问、且愿意走实名 + 备案流程

### 方案 D：Vercel / Netlify

- 免费额度充足（Netlify Drop 支持拖拽即得临时链接），但国内访问稳定性不如 Cloudflare
- Netlify Drop：https://app.netlify.com/drop 直接把 `site/` 拖进去

## 发布前必读（重要）

1. **地图底图授权**：默认底图用 **OpenStreetMap**（要求保留 “© OpenStreetMap contributors” 署名，轻量个人站点可用；大流量请换正规瓦片服务如 MapTiler/Carto 免费额度）。页面里的「高德」底图**仅限个人自用**——高德栅格瓦片未经授权用于公开站点属于违规，正式发布请勿对外默认开启。
2. **天气数据**：Open-Meteo 免费非商业使用，已在页面标注来源。
3. **内容与数据**：攻略数据均来自公开网页的事实性信息（票价/里程/海拔/开放状态等），页面已标注核验日期与来源域名，并附免责声明。**如用于商业用途**（挂广告、带货、付费导流），请先复核各来源站点的转载政策与地图/天气服务的商用条款。
4. **备案**：托管在境外（Cloudflare Pages / GitHub Pages）**无需 ICP 备案**；若使用国内服务器 + 自有域名（阿里云 OSS、腾讯云 COS 等），则**必须备案**，且 OSS 默认域名不能直接用于网站访问。
5. **时效性**：票价、封山、开放状态会变，页面已把不确定项标注「待核验」，建议每季度复核一次（核验日期 2026-10-12）。

## 更新流程

```bash
# 1) 仓库根目录改数据/样式/逻辑
# 2) 重新构建单文件
pwsh -File design/build/build.ps1
# 3) 同步到站点目录并提交
cp 成都周边爬山攻略.html site/index.html
cd site && git add . && git commit -m "update: 数据更新" && git push
```
