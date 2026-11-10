# 主题：本地联调 APK 直连插件开发与 agent-feedback v1.3.0 npm 发布筹备

- 当前状态：已完成 (completed)
- 完成时间：2026-11-04
- 对应模块：
  - `weekly-mountain`: `src/components/debug/AlpineDevApkExtensionView.vue`, `src/debug/alpineDevApkPlugin.js`, `src/debug/setupAgentFeedback.js`, `vite.config.js`
  - `agent-feedback`: `packages/core`, `packages/client`, `packages/sentinel`, `packages/vite-plugin` (全部就绪待发布)
- 验证截图：
  - 未解锁状态安全受限屏障：`scratch/dev_apk_tab_locked.png`
  - 解锁后开发机本地 APK 实时分发面板：`scratch/dev_apk_tab_unlocked.png`

## 1. 目标与决策复盘

根据用户指示，梳理并落地以下核心需求：
1. **正式更新 vs 调试入口本地包的双层架构分离**：
   - **正式更新下载 (App 内部 & Web 页面)**：统一指向 GitHub Releases 正式发布页及国内 CDN 镜像加速，分发已正式发布的正式版与内测调试版；
   - **调试入口更新下载 (Dev APK Bridge)**：指向开发机内网穿透地址（`apiBase`），直接拉取本机刚构建好的 APK（如 `android/app/build/outputs/apk/debug/app-debug.apk`），供开发者免去 Commit/Push/Tag 与等待 15 分钟 GitHub Actions 的烦琐流程，实现秒级真机验证。
2. **插件归属决策**：
   - **坚定落地于《每周一山》业务项目，不强塞进 `agent-feedback` 核心**；
   - 保证了 `agent-feedback` 跨 Web、跨生态通用反馈框架的纯粹性；
   - 充分利用 `agent-feedback` 的 `registerExtensionTab` 扩展机制，为生态提供了第一方的业务自定义插件实战范例（Dogfooding Plugin API）。

## 2. 核心改动清单

1. **业务级扩展插件实现 (`weekly-mountain`)**：
   - `src/components/debug/AlpineDevApkExtensionView.vue`：
     - 未授权状态防护：未输入配对密钥时展示锁闭提示，并提供一键跳转「⚙️ 联调设置」按钮；
     - 授权状态：读取开发机穿透基地址，请求 `/api/app-update` 动态展示开发机本地刚编译的 APK 文件名、大小、最后编译时间；
     - 提供「⬇️ 下载本地 Debug APK」与「⬇️ 下载本地 Release APK」按钮，支持直链复制；
     - 样式采用 `<component is="style">` 完美穿透 Web Component Shadow DOM，与深色黑曜石主题完全融为一体。
   - `src/debug/alpineDevApkPlugin.js`：
     - 声明 `alpineDevApkTab`（`id: 'alpine-dev-apk'`, `label: '本地包'`, `icon: '📦'`），采用异步按需动态加载 `createApp` 与组件，保证零多余运行时开销。
   - `src/debug/setupAgentFeedback.js`：
     - 注册 `alpineDevApkTab` 到 `@lylyuanliang/agent-feedback-client`。
   - `src/main.js`：
     - 严格在 `import.meta.env.DEV || IS_DEBUG_BUILD` 条件下启用扩展。
2. **开发机 Vite 本地 APK 分发中间件增强 (`vite.config.js`)**：
   - `GET /releases/*`：优先检查 `android/app/build/outputs/apk/debug/app-debug.apk`（若比 `releases/` 目录更新，则直接流式分发本地刚编译的最新包），支持 HTTP 206 断点续传与 Range 分块下载；
   - `GET /api/app-update`：优先聚合本地刚编译产物的最新 mtime 与体积返回前端。
3. **100% Zero-DCE 生产纯净构建**：
   - 运行 `npm run build:release`：调试插件与 `@agent-feedback/client` 完全被 Rollup/Vite 剥离，0 冗余字节侵入正式版。

## 3. 验证结果

1. **自动化 Playwright 冒烟与视觉回归**：
   - 运行 `python scratch/test_dev_apk_plugin.py`：
     - 未配对时：渲染受限卡片「开发机本地联调受限」（证据：`scratch/dev_apk_tab_locked.png`）；
     - 配对后：实时拉取开发机 `app-debug.apk (本地刚构建) 28.14 MB`，下载按钮与复制链接全部可用（证据：`scratch/dev_apk_tab_unlocked.png`）；
     - 测试 100% 通过。
2. **本地 API 与流式下载测试**：
   - `GET /api/app-update` 返回最新构建元数据；
   - `GET /releases/weekly-mountain-latest-debug.apk` 返回 HTTP 206 状态码与正确 Content-Range。
3. **agent-feedback v1.3.0 单测与打包**：
   - 全仓库 95 个单元测试 100% 绿灯通过，构建产物 `dist/` 均已生成完毕。

## 4. agent-feedback v1.3.0 npm 发布操作指引

用户终端登录后可一键执行：
```powershell
cd d:\file_save\workspace\github\agent-feedback
npm login
pnpm -r publish --access public --no-git-checks
```
发布成功后，每周一山将 `package.json` 中的依赖由本地 `file:packages/*.tgz` 改为正式 npm 源即可。
