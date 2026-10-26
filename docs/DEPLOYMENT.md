# 《每周一山》无服务器部署与发布指南 (Deployment Guide)

> 本文档记录了《每周一山 · 成都周边50座山》静态 Web 站点的无服务器 (Serverless) 托管发布方案、注意事项与更新维护流程。<br>
> 📖 欲了解产品核心功能、特性预览与移动端原生安装包，请返回 [项目主 README](../README.md)。

---

## 目录
- [一、 本地快速打开与预览](#一-本地快速打开与预览)
- [二、 免费云端发布与托管方案](#二-免费云端发布与托管方案)
  - [方案 A：Cloudflare Pages（推荐，全球加速）](#方案-a-cloudflare-pages推荐全球加速)
  - [方案 B：GitHub Pages（Git 工作流无缝联动）](#方案-b-github-pagesgit-工作流无缝联动)
  - [方案 C：Gitee Pages（国内节点）](#方案-c-gitee-pages国内节点)
  - [方案 D：Vercel / Netlify](#方案-d-vercel--netlify)
- [三、 发布前合规与配置必读](#三-发布前合规与配置必读)
- [四、 生产构建与静态同步流程](#四-生产构建与静态同步流程)
- [五、 线上托管地址与回查索引](#五-线上托管地址与回查索引)

---

## 一、 本地快速打开与预览

### 1. 现代化 Vue 3 + Vite 工程预览
```bash
# 启动本地开发热重载服务器
npm run dev

# 构建并启动生产环境预览
npm run build
npm run preview
```

### 2. 独立单文件 HTML 离线查看
直接双击 `成都周边爬山攻略.html`（或拷到手机用 Safari / Chrome / Kiwi 打开）即可，无需依赖任何后端服务。

---

## 二、 免费云端发布与托管方案

### 方案 A：Cloudflare Pages（推荐，国内访问相对最好）

1. 注册登录 [Cloudflare Dashboard](https://dash.cloudflare.com)（免费）；
2. 进入左侧导航 **Workers & Pages → Create → Pages → Upload assets**；
3. 将生产构建产物 `dist/` 目录（或 `site/` 单文件目录）打包上传；
4. 获得 `https://<项目名>.pages.dev` 免费二级域名，自动开启 HTTPS 全球 Anycast CDN；
5. 后续每次更新：重新上传构建产物覆盖即可（亦可直接绑定 GitHub 仓库触发 CI/CD 自动构建）。

- **免费额度**：无限流量带宽、每月 500 次构建；
- **核心优势**：免 ICP 备案、全球 CDN 边缘节点、支持绑定自定义二级域名并自动申请 SSL 证书。

---

### 方案 B：GitHub Pages（Git 工作流，最省心）

1. 在 GitHub 上创建公开仓库，例如 `weekly-mountain`；
2. 推送静态构建资源至分支（如 `gh-pages` 或 `main` 根目录）：

```bash
# 示例推送工作流
cd dist
git init
git add .
git commit -m "deploy: 发布最新静态生产产物"
git branch -M gh-pages
git remote add origin git@github.com:lylyuanliang/weekly-mountain.git
git push -u origin gh-pages --force
```

3. 仓库 **Settings → Pages → Source: Deploy from a branch → Branch: gh-pages / (root) → Save**；
4. 约 1~2 分钟后即可访问 `https://<username>.github.io/weekly-mountain/`。

- **免费额度**：仓库 1GB、每月 100GB 流量；
- **注意事项**：根目录包含 `.nojekyll` 文件以跳过 Jekyll 引擎对 `_` 前缀资源的过滤；国内部分运营商直连访问稳定性差异较大，可配合 Cloudflare CDN 代理。

---

### 方案 C：Gitee Pages（码云，国内服务器）

- **优势**：国内机房节点，网络握手延迟低；
- **注意**：需完成实名认证；公开仓库 Pages 服务需提交安全审核，自定义域名需绑定已完成工信部 ICP 备案的域名。

---

### 方案 D：Vercel / Netlify

- **免费额度**：充足个人免费层，支持 CLI 一键部署或 Git Push 自动触发；
- **拖拽即用**：[Netlify Drop](https://app.netlify.com/drop) 支持直接将 `dist/` 文件夹拖入网页，3 秒内生成在线体验链接。

---

## 三、 发布前合规与配置必读

1. **地图底图授权与商用规范**：
   - 默认底图采用 **OpenStreetMap (OSM)**，遵循 ODbL 协议，已保留 “© OpenStreetMap contributors” 声明；
   - 页面内高德栅格图层**仅限个人研发自用**，未经商业授权的公开部署站点请使用 OSM 或申请合规商业瓦片密钥。
2. **气象遥测数据源**：
   - 气象预报对接 [Open-Meteo API](https://open-meteo.com/)，遵循 CC-BY 4.0 免费非商业许可，页面内已标注数据源归属。
3. **攻略内容与路线时效性**：
   - 所有山峰标高、里程、耗时、路况及管制信息均汇总自实地复核与公开地学资料；
   - 部分高海拔或林场路线存在季节性封山或修路管制，出行前请务必以属地主管部门最新通告为准。
4. **域名备案与国内托管**：
   - 托管于海外平台（Cloudflare Pages / GitHub Pages / Vercel）无需大陆 ICP 备案；
   - 若将静态资源部署在国内云厂商对象存储（如阿里云 OSS、腾讯云 COS）并绑定自定义域名，域名必须具备有效工信部 ICP 备案号。

---

## 四、 生产构建与静态同步流程

```bash
# 1. 安装项目依赖
npm install

# 2. 执行现代化生产环境打包 (包含名山高清画廊与矢量资源)
npm run build

# 3. 亦可执行单文件独立 HTML 编译脚本 (若需要单 HTML 归档)
pwsh -File design/build/build.ps1

# 4. 同步至分发归档目录
node scripts/copy_assets.js
```

---

## 五、 线上托管地址与回查索引

| 站点与服务 | 在线预览地址 | 运维管理平台 |
| :--- | :--- | :--- |
| **主站 (Cloudflare Workers)** | [https://broken-surf-e858.lylyuanliang.workers.dev/](https://broken-surf-e858.lylyuanliang.workers.dev/) | [Cloudflare Dashboard](https://dash.cloudflare.com) |
| **镜像站 (html2.link)** | [https://a3puoei5.html2.link/](https://a3puoei5.html2.link/) | [html2.link Console](https://html2.link) |
| **GitHub 官方源码仓库** | [https://github.com/lylyuanliang/weekly-mountain](https://github.com/lylyuanliang/weekly-mountain) | [GitHub Repository](https://github.com) |

> 提示：线上平台地址若有更新，请同步维护本表；回查时优先登录对应云平台后台查看域名绑定与 CDN 状态。
