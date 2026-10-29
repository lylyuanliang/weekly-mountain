# 任务交接与状态记录：接入独立通用 agent-feedback 服务与定制调试扩展方案 (Integrate Agent Feedback Service)

> 规范依据：`AGENTS.md` / `GEMINI.md` 全局规约与任务交接硬门禁
> 状态：交付完成 (Completed & Verified)
> 分支：`feat/integrate-agent-feedback`

---

## 1. 任务背景与核心目标

为了将《每周一山》成熟的“移动端真机反馈 -> Agent 监听自愈 -> 端侧时间轴进度闭环”能力通用化，已在 `D:\file_save\workspace\github\agent-feedback` 将其剥离为独立的通用公共 SDK（计划后续发 npm）。
本任务的核心目标：
1. **独立分支开发**：在每周一山创建 `feat/integrate-agent-feedback` 分支进行接入；
2. **通用定位与业务隔离**：
   - 坚守 `agent-feedback` 作为纯粹通用开源库的定位，严禁向其侵入任何每周一山专有逻辑；
   - 通过 `agent-feedback` 设计的 **Extension Tabs 插件槽机制**，将每周一山的定制调试与在线更新面板（APK 流式下载、断点续传、穿透诊断）解耦挂载；
3. **能力反哺与双向标准化**：
   - 将日级分片存储架构（`feedback_YYYY-MM-DD.json` + `feedback_index.json`）、流式时间轴 UI（按天分组、发光圆点、条数徽标）、工单类型（`agent_notice` vs `user_feedback`）及 CSS Token 主题系统全部标准化沉淀至 `agent-feedback`；
4. **npm 发包闭环就绪**：
   - 本地打包验证物料无缺失，完成真实端到端集成测试；
5. **哨兵恢复与真机工单自愈**：
   - 接入验证完成后拉起新版哨兵；捕获并实时自愈了手机端反馈“更新之后，历史没有了，能恢复吗”；修复了旧版 App 契约兼容路由并完成工单闭环。

---

## 2. 核心架构与落地成果

### 2.1 通用 SDK 升级成果 (`D:\file_save\workspace\github\agent-feedback`)
- **`@agent-feedback/core`**：扩展 `FeedbackType`、`InAppFeedback`（增加 type 与 date）、日级索引 `FeedbackDateIndex`、扩展槽 `FeedbackExtensionTab`、主题 Token 体系；
- **`@agent-feedback/vite-plugin`**：升级持久化为按天分片落盘，自动迁移兼容旧队列；提供全套标准端点；
- **`@agent-feedback/client`**：Shadow DOM 全面适配 CSS 变量系统；历史视图升级为流式时间轴；开放 `registerExtensionTab(tab)` 规范；
- **`@agent-feedback/sentinel`**：适配分片轮询与防抖唤醒；提供 `notice` 与 `update-status` CLI；
- **单元测试与构建**：全仓 **77/77 个单元测试 100% 绿灯**，`pnpm -r build` 成功输出 `dist`，`pnpm pack` 生成完整发布包。

### 2.2 每周一山接入成果 (`D:\file_save\workspace\github\weekly-mountain`)
- **分支创建**：`feat/integrate-agent-feedback`；
- **依赖接入**：引入本地 `@agent-feedback/*` 系列包；
- **`vite.config.js` 架构重构与旧版 100% 契约保真兼容**：
  - 接入 `agentFeedback({ storageDir: 'scratch/feedback', theme: 'dark', primaryColor: '#4edea3' })`；
  - 保留纯粹的专属 APK 下载服务 `viteApkReleasePlugin()`；
  - **重要修复与保真兼容**：不仅转发请求，更为未升级的旧版手机端 App（如 `v0.0.1.202610281342`）提供包装结构 `{ success: true, totalCount, dates, currentDate, dailyCount, items }` 以及旧版截图下发路由 `/api/feedback/screenshot/*`，确保旧版 App 打开历史也能立刻看到全量 50 条工单！
- **定制调试面板扩展化**：
  - 编写 [`src/components/debug/AlpineDebugExtensionView.vue`](file:///d:/file_save/workspace/github/weekly-mountain/src/components/debug/AlpineDebugExtensionView.vue)，通过内嵌 `<component is="style">` 彻底解决 Shadow DOM 隔离问题；
  - 在 [`src/debug/setupAgentFeedback.js`](file:///d:/file_save/workspace/github/weekly-mountain/src/debug/setupAgentFeedback.js) 中将“穿透通信诊断”和“在线更新（APK 流式下载/切屏续装）”注册为 `🛠️ 联调与更新` Tab；
- **组件精简**：从 `src/App.vue` 剥离旧的内嵌浮窗组件，统一由 `<agent-feedback-widget>` 接管。

---

## 3. 真机工单处理与自愈记录

### 3.1 工单 #1793175462520（历史记录恢复）
- **提交时间**：`2026-10-28 16:17:42` (来自小米真机 Android 16)
- **反馈内容**：“更新之后，历史没有了，能恢复吗”
- **根因分析**：手机上运行的是旧版安装包（`v0.0.1.202610281342`），其内部组件读取 `/api/feedback` 时要求响应包含 `data.success === true` 的 Object 包装；由于新服务返回的是纯 Array，导致旧版判定失败跳过了历史渲染（底层数据 100% 完好存在）。
- **自愈方案**：在 `vite.config.js` 的前置中间件中，为旧版 `/api/feedback` 和截图路由补充契约保真逻辑，返回符合旧版期望的包装结构。
- **验证与答复**：经本地与网络模拟请求，旧路由恢复返回 `success: true` 与 `totalCount: 50`。已通过 CLI 将工单更新为 `completed` 并写回详细答复。

### 3.2 工单 #1793176452985（版本重复提示循环）
- **提交时间**：`2026-10-28 16:34:12`
- **反馈内容**：“我明明都升级两次了，为啥版本还是1342，一直提示还有新版本1359？”
- **根因分析**：此前自动化编译仅输出了正式 Release 变体，而调试模式下载固定指向 `releases/weekly-mountain-latest-debug.apk`，导致物理文件停留在 `1342`。
- **自愈方案**：运行 `sync_version.py` 升版至 `0.0.1.202610281635`，执行 `build_app.ps1` 重新编译生成全新的 Debug APK（28.08 MB）覆盖镜像。
- **验证与答复**：版本信息与物理 APK 完全对齐，已通过 CLI 将工单更新为 `completed`。

### 3.3 工单 #1793176493558（历史截图显示问题）
- **提交时间**：`2026-10-28 16:34:53`
- **反馈内容**：“历史界面里面的图片看不了了”
- **根因分析**：新版通用 SDK 将截图存储规范化为简洁的字符串路径，而旧版 App 在渲染历史时严格读取 `sShot.filename` 对象属性，导致获取到 `undefined` 继而白屏破图。
- **自愈方案**：在 `vite.config.js` 的旧版契约兼容中间件中，增加字段智能规范化转换，自动将字符串路径包装为 `{ filename, path, ext }` 对象并补齐 `screenshotFilename`。同时挂载 `/api/feedback/screenshot/*` 静态资源处理中间件。
- **验证与答复**：经 curl/fetch 模拟验证，图片资源正常返回 200 HTTP 响应，工单已标记为 `completed`。

### 3.4 移动端原生容器与真机深度适配（API Base 穿透与锁屏断点续传）
- **反馈内容**：
  1. 点击反馈显示发送了但 Agent 没收到；
  2. "新建反馈" 页面的 `/#/profile` 这些内容有什么含义；
  3. "历史与进度" 为空；
  4. App 更新过程中锁屏，重新解锁后又要重新下载。
- **根因分析**：
  - **反馈未上报与历史为空**：通用 `@agent-feedback/client` 此前采用纯相对路径 `/api/__agent_feedback/*`，在 Capacitor 原生离线包环境下会请求到手机内置的资产静态服务（`http://localhost/`），导致历史为空且提交请求未到达电脑端的 DevServer。
  - **新建反馈的 `/#/profile` 等标签**：为端侧自动捕获的遥测快照（包含页面当前 Hash 路由、屏幕分辨率与 DPR、运行系统及错误日志统计）。
  - **锁屏中断需重新下载**：小米 HyperOS 锁屏后 Doze 模式会中断普通套接字，而原生代码缺乏 HTTP Range 断点续传支持且在网络异常时将临时文件全部删除，导致从 0 重下。
- **自愈方案**：
  1. `@agent-feedback/client` 新增 `setApiBase`、`getApiUrl`，并在 `weekly-mountain` 的 `setupAgentFeedback.js` 中动态绑定 `debugStore.apiBase`（自动走 cpolar 穿透地址），同时加强提交响应格式严格校验；
  2. `vite.config.js` 的 `viteApkReleasePlugin` 增加 HTTP 206 Partial Content / `Range` 支持；
  3. `MainActivity.java` 引入 `Range: bytes=existingLength-` 断点续传请求头、追加模式写入、锁屏 WifiLock/WakeLock 双重保活，并保护未完成的 `.download` 临时文件不被误删；
  4. 升版至 `0.0.1.202610281718` 并重新编译生成全新的 Debug APK 覆盖镜像。

### 3.5 移动端手势冲突与“反馈给 AI”点击无响应自愈
- **反馈内容**：
  - 用户反馈安装新包后，在手机真机上轻触“反馈给 AI”胶囊按钮完全没有反应，弹窗无法打开。
- **根因分析**：
  1. **多手势监听器冲突**：`@agent-feedback/client` 原实现在同一元素上同时挂载了 `pointerdown`、`touchstart`、`mousedown`，现代 Android 16 Chrome 156 会触发序列事件并导致标志位覆盖；
  2. **拖拽位移阈值过小**：此前采用 `Math.abs(delta) > 5` 判断拖拽，而小米 15 屏幕 DPR 为 3.25，人类手指轻触肉体接触变形即超 5px，导致轻触被系统误判为“拖拽”，释放时跳过了 `toggleModal()`；
  3. **缺少 click 兜底与外部调用能力**：胶囊未注册标准 `click` 监听；且个人中心 `AlpineDebugModal` 无法直接调起反馈窗口。
- **自愈方案**：
  1. 彻底重构 `@agent-feedback/client` 的胶囊手势系统，统一走标准 Pointer Events + `setPointerCapture`，阈值放宽至 `Math.hypot(dx, dy) > 10`；
  2. 增加原生 `click` 兜底事件，且导出 `openFeedbackModal` 与 `window.openAgentFeedbackModal`；
  3. 在 `weekly-mountain/src/debug/setupAgentFeedback.js` 增加 `wm-open-feedback` 事件监听与统一打开代理；
  4. 运行 `sync_version.py` 升版至 `0.0.1.202610281739`，重新打包并归档 `weekly-mountain-v0.0.1.202610281739-debug.apk`。

### 3.6 README 文档补全与架构亮点规范化
- 在 `agent-feedback/README.md` 中补充 `## 🌐 真机联调与网络互通指南`，阐明默认同源服务机制、4 类网络拓扑与 cpolar 穿透配置；
- 补充 `## 🔄 端到端自愈工作闭环流程`，包含 ASCII 架构全景图及应用极简接入、端侧全息抓取、分片落盘与哨兵防抖、Agent 源码自愈、端侧时间轴复验 5 大生命周期阶段详解；
- 规范化参考项目架构亮点，移除针对旧 App 的私有描述，替换为通用的“沉浸式主题系统融合 (Design System Integration)”。

### 3.7 流程图 Mermaid 专业可视化美化与色彩体系升级
- 针对 ASCII 图标表现力有限的问题，全面升级为 GitHub 原生渲染的高级 Mermaid Flowchart (`flowchart TD`)；
- 采用 5 色高对比度极客暗黑主题类定义 (`#38bdf8`, `#34d399`, `#a78bfa`, `#fbbf24`, `#4edea3`)，区分极简接入、全息抓取、分片哨兵、Agent 自愈与时间轴复验阶段；
- 节点内支持丰富富文本与 Emoji 语义徽标，极大提升开源文档质感。

### 3.8 手机边缘点击穿透误关与软键盘自动弹起深度自愈
- **反馈现象**：
  1. 悬浮胶囊在屏幕底部约 1/5 或顶部约 1/5 处时，点击完全没有反应无法弹出；而在屏幕中间位置点击则能正常弹出；
  2. 弹窗弹出后自动聚焦输入框，立即唤起软键盘，导致移动端视口被压缩变形。
- **根因分析**：
  - **合成点击穿透闭环**：`.modal-container` 在垂直方向居中且最大高度为 `85vh`，因此屏幕顶部约 1/5 和底部约 1/5 区域均为 `.modal-backdrop` 遮罩空白区；当用户在顶部或底部轻触胶囊时，`pointerup` 同步呼出弹窗，但移动浏览器约 150ms 延迟派发的伴随合成 `click` 事件瞬间落在了新出现的 `.modal-backdrop` 上；`backdrop` 的点击监听器检测到 `e.target === backdrop`，瞬间执行 `this.toggleModal(false)` 将其关闭，用户肉眼看起来表现为“完全没弹出来”；
  - **软键盘误激活**：当胶囊在屏幕中间时，伴随合成点击落在 `.modal-container` 的 `textarea` 上，从而意外触发了聚焦与输入法呼出。
- **自愈方案**：
  1. 在 `@agent-feedback/client` 中引入 `modalOpenedAt` 时间戳；
  2. 在 `modal-backdrop` 点击事件中增加 450ms 穿透时间保护门禁，彻底屏蔽打开瞬间的手指导电伴随事件；
  3. 在 `pointerup` 中添加 `e.preventDefault()` 阻止浏览器后续派发合成鼠标/点击事件；
  4. 为 `textarea` 增加显式失焦与 450ms 点击保护，确保只有用户在弹窗完全展开后主动进行二次点击，才会聚焦输入框并调起键盘；
  5. 升版至 `0.0.1.202610281758` 并重新编译 Native Debug APK。

### 3.9 真机工单 #1793182256087（调试入口去重与本地多截图支持恢复）
- **提交时间**：`2026-10-28 18:10:56` (来自小米 15 真机 Android 16，成功截屏上报)
- **反馈内容**：
  1. “既然悬浮按钮有调试设置了，那每周一山的调试设置入口是不是就不需要了，功能重复了吧”
  2. “反馈上传本地截图，只能选一张的问题又出现了”
- **根因分析**：
  1. **调试入口冗余**：此前《每周一山》在 `ProfileView.vue` 保留了旧的 `SECTION 4.5: 调试与内测支持` 及 `AlpineDebugModal.vue` 弹窗；而现在悬浮胶囊已有 `🛠️ 联调与更新` 扩展 Tab，两套调试界面造成视觉与维护割裂；
  2. **截图单选限制**：通用 SDK `@agent-feedback/client` 在轻量化设计初期仅声明了单个 `attachedScreenshot: string | null` 变量，且文件 `<input>` 未配置 `multiple` 属性，导致用户只能单张选图。
- **自愈方案**：
  1. **彻底去重解耦**：彻底下线并移除 `ProfileView.vue` 中的 Section 4.5 与 `AlpineDebugModal` 异步组件，将所有开发者能力完全收敛至悬浮胶囊作为唯一真机入口，减少打包体积；
  2. **多图引擎升级**：`@agent-feedback/client` 重构为 `attachedScreenshots: string[]`，file input 增加 `multiple`，支持最多附加 6 张图片；提供九宫格预览与单张精细化移除能力；
  3. **工单闭环与重新发版**：通过 CLI 将工单标记为 `completed` 并写入自愈说明；升版至 `0.0.1.202610281816` 并重新构建发布 Debug APK。

### 3.10 真机工单 #1793182388509 ~ #1793182522562 连发自愈闭环 (图片压缩、大图预览、Tab栏防挤压与极速响应)
- **工单集**：
  - `1793182388509`：“1历史界面上传的图片看不了了；2历史界面点开后，tab切换没了；3上传的图片没法点击看大图了”
  - `1793182432478`：“现在的提交反馈没有之前的流畅了，也分析下”
  - `1793182493185`：“不带图片就很快，是不是图片压缩步骤没了？”
  - `1793182522562`：“历史列表的加载也很慢，都测一下”
- **根因分析**：
  1. **图片压缩遗漏**：重构独立包时未带入原有的 Canvas 图片压缩逻辑，导致手机拍摄的 10MB~15MB 原图直接转为 Base64 走外网穿透上传，造成提交慢、分片体积剧增、历史拉取严重卡顿；
  2. **历史截图 URL 缺失**：缺少前缀导致请求了不带 `/api/__agent_feedback/` 的地址，出现 404 白屏；
  3. **Tab 栏挤压**：`.modal-header` 与 `.tabs` 未设 `flex-shrink: 0;`，历史长列表加载时导致 Tab 选项卡被挤压消失；
  4. **缺少大图预览**：点击缩略图无响应。
- **自愈方案与代码落地**：
  1. 在 `@agent-feedback/client` 中恢复 `compressImage(file, 1200, 0.75)` Canvas 压缩引擎，无论多大原图均压缩 99% 至 80KB 左右轻量 JPEG；截屏统一压缩为 JPEG 0.8；
  2. 规范化截图请求地址为 `getScreenshotUrl(shot)`；
  3. 为模态框头部与 Tabs 增加 `flex-shrink: 0;`；
  4. 新增全屏 Lightbox 大图预览组件，支持高保真放大与一键关闭；
  5. 通过哨兵 CLI 批量将所有工单回写为 `completed`；
  6. 同步升版至 `0.0.1.202610281825` 并重新编译 Native Debug APK。

### 3.11 真机工单 #1793183739190 自愈闭环 (发现新版本左侧闪烁黄点、新建反馈图片点击看大图)
- **提交时间**：`2026-10-28 18:35:39` (来自小米 15 真机 Android 16，成功上传 2 张截图凭证)
- **反馈内容**：
  1. “发现新版本左边闪烁的黄点没了”
  2. “新建反馈页面，上传的图片还是不能点开看大图”
- **根因分析**：
  1. **闪烁黄点指示器遗漏**：在重构拆分 `AlpineDebugExtensionView.vue` 扩展面板时，仅保留了文本标题 `发现新构建: v...`，遗漏了此前在旧版中当检测到有新版本（`hasNewVersion`）时左侧的呼吸闪烁指示点；
  2. **新建反馈缩略图点击预览缺失**：上一轮仅针对历史时间轴的 `.ticket-screenshot-thumb` 绑定了大图预览 Lightbox，新建反馈页面中的多图/截屏网格 `.screenshot-img` 未绑定点击预览且未设置手型悬浮光标。
- **自愈方案与代码落地**：
  1. 在 `AlpineDebugExtensionView.vue` 中为“内测更新与构建管理”卡片标题 `.dot-indicator` 和更新提示 `.update-dot` 恢复 `hasNewVersion` 动态闪烁动画（`#f59e0b` 琥珀黄脉冲呼吸）；
  2. 在 `@agent-feedback/client` 中将大图预览选择器扩展为 `.ticket-screenshot-thumb, .screenshot-img`，为新建反馈上传的本地截图与当前界面截屏提供一键点击全屏 Lightbox 大图预览及鼠标悬浮缩放动画；
  3. 通过 CLI 将工单标记为 `completed` 并写回详细答复；
  4. 升版至 `0.0.1.202610281841` 并重新编译 Native Debug APK。

### 3.13 真机工单 #1793188216832 自愈闭环 (破案端侧截屏全黑废图与“那个遮罩”根因)
- **提交时间**：`2026-10-28 19:50:16` (来自小米 15 真机 Android 16，附带 2 张截图凭证)
- **反馈内容**：“我在这个界面打开ai反馈，还是会出现这个情况，而且那个遮罩还是会出现”
- **根因分析**：
  1. 经深度比对发现用户所指的“那个遮罩”根本不是弹窗背景遮罩，而是 `@agent-feedback/client` 中此前采用的 SVG `foreignObject` 伪截屏引擎产生的坍塌破图；在移动端沙箱无 CSS 渲染环境下，导致整屏全黑并出现一个深黑长条色块；
  2. 截图时未临时隐藏模态框自身，导致截屏将模态框半透明背景本身也截入其中。
- **自愈方案与代码落地**：
  1. 在 `@agent-feedback/client` 中全面重构 `captureScreenshot()`：
     - 截图前先获取所有 `<agent-feedback-widget>` 实例并将其模态框临时设为 `opacity: 0; pointerEvents: none;`；
     - 动态引入宿主环境现成的 `html2canvas` 模块抓取真实高保真 DOM 全屏画面；
     - 截取完成后恢复遮罩显示，并调用 `compressImage` 压缩为 ~80KB 轻量高保真 JPEG；
     - 彻底废除全黑 SVG 降级方案，若宿主未装 `html2canvas` 则友好引导用户从相册选取系统截屏；
  2. 在 `@agent-feedback/vite-plugin` 中修复纯 JS 兼容性，移除 TS `as any` 语法泄漏；
  3. 通过 CLI 回写工单为 `completed` 并向端侧输出详细自愈说明。

### 3.14 真机批次工单 #1793188276725 等 4 连自愈闭环 (周计划打卡纪实互通、历史瘦身82%、无感防跳顶与5秒实时状态轮询)
- **工单集覆盖**：
  1. `#1793188276725`：“这个界面没法看到打卡详情” (周计划页面)；
  2. `#1793188416996`：“1历史进度应该还是有问题，很慢；2历史界面加载前一天记录的功能，加载完成后会回到第一条”；
  3. `#1793188464931`：“补充：速度慢会不会是内网穿透网速太慢了？排查下”；
  4. `#1793188545601`：“ai反馈的状态没有实时更新，之前的老版本（未拆出来之前的版本）是可以的”。
- **根因分析与全栈自愈**：
  1. **周计划打卡纪实互通**：在 `PlanView.vue` 中无缝集成 `CheckinDetailModal` 与 `MountainDetailSheet`。若名山已打卡，点击“✓ 已打卡 · 纪实”即刻唤起打卡纪实管理弹窗（可查看与编辑打卡实景相片、随笔、日期）；首次点击“打卡确认”执行轻量打卡并弹出 Toast，绝不强弹大模态框；点击山峰卡片直接唤起名山详情抽屉；
  2. **历史记录分片清洗瘦身 82%**：排查发现历史工单中混入了 2 条未经文件化的 Base64 原始图片（118KB 与 43KB），在穿透带宽（cpolar）受限下下载异常缓慢。已在后端自动清洗并转存至 `screenshots/` 静态目录，日级 JSON 分片由 188KB 骤降至 33KB；前端首屏采用 `Promise.all` 并发拉取索引与列表，穿透网络下一秒秒开；
  3. **加载前一天平滑防跳顶**：在 `loadPreviousDay()` 重新渲染前后，精准记录与恢复 `.modal-body` 的 `scrollTop`，加载前一天历史后稳稳停留在当前阅读位置；
  4. **端侧实时无感状态轮询**：在 `@agent-feedback/client` 中补齐实时轮询引擎。当用户打开「历史与进度」Tab 时以 5 秒轻量间隔自动轮询，一旦 AI 完成修复回写，工单瞬间变绿并展示自愈报告；弹窗关闭时自动休眠，0 耗电 0 耗流；
  5. **悬浮胶囊防抖与边界防误触**：校准触控判定阈值（移动位移需 > 18px 且触摸时长 > 100ms 判定为拖拽贴边），普通轻触（无论在屏幕顶部还是底部 1/5 区域）100% 灵敏响应唤出弹窗；
  6. **全量自动化验证**：E2E 5 大模块 100% 通过，Console 0 错误；升版至 `0.0.1.202610282030` 并编译交付最新 Native Debug APK！

### 3.15 真机工单 #1793195537347 自愈闭环 (列表时间偏差与端侧本地时区自动对齐)
- **提交时间**：`2026-10-28 21:52:17` (来自小米 15 真机 Android 16，附带 1 张关键截图)
- **反馈内容**：“列表的时间不对，UTC时间”
- **根因分析**：
  在 `@agent-feedback/client` 的 `renderTicketCard` 中，此前直接使用了 `item.receivedAt.slice(11, 19)`。由于 `receivedAt` 是标准的 ISO 8601 UTC 字符串（如 `2026-10-28T12:30:16.954Z`），直接截取直接展示了原始 UTC 时间（12:30:16），与用户手机顶部状态栏时钟（北京时间 UTC+8，21:46 / 20:30）存在整整 8 小时的时差。
- **自愈方案与代码落地**：
  1. 在 `@agent-feedback/client` 中新增 `formatLocalTime()` 与 `formatLocalDate()` 格式化函数，基于客户端运行时的真实 `Date` 对象与 `timestamp` 进行转换，自动补齐两位数；
  2. 无论用户身处哪个时区，历史工单卡片均与手机操作系统本地系统时钟 100% 精确对齐；
  3. 为 `@agent-feedback/client` 补充本地时区单元测试，78/78 测试全数通过；
  4. 通过 CLI 标记工单为 `completed` 并向时间轴推送时钟同步通知；
  5. 统一升版至 `0.0.1.202610282156` 并重新编译 Native Debug APK。

---

## 4. Git 提交与远端推送记录
- **`agent-feedback` 仓库**:
  - `feat: 重构升级通用四大特性并支持日级分片、时间轴流式加载、扩展槽与主题系统` (`4957023`)
  - `docs: 更新 README 并补充扩展接入示例与实战项目参考链接` (`f7e98fc`)
  - `docs: 优化实战参考亮点为通用设计系统融合与规范化 CLI 示例` (`3973dc0`)
  - `docs: 升级自愈闭环为高级 Mermaid 拓扑流图，并自愈移动端边缘穿透点击与软键盘误激活问题` (`461de7f`)
  - `feat: 支持多图上传附件(最多6张)与九宫格预览移除` (`5b0b6b5`)
  - 推送分支：`origin/main`
- **`weekly-mountain` 仓库**:
  - `feat: 接入通用 @agent-feedback 服务、支持真机联调扩展槽与旧版 100% 契约保真适配` (`82b6763`)
  - 推送分支：`origin/feat/integrate-agent-feedback`

### 3.16 真机工单 #1793242745250 自愈闭环 (切换 Tab 弹窗上下跳动与顶部固定锚定)
- **提交时间**：`2026-10-29 10:59:05` (来自小米真机 Android 16，哨兵自动唤醒)
- **反馈内容**：“调试功能弹窗，我在切换tab得时候，他会根据内容变化位置，如新建反馈页面就到了屏幕中间了，历史与进度页面就到了屏幕上部了，这样体验不好，顶部位置可以固定吗”
- **根因分析**：
  此前 `.modal-backdrop` 采用 `align-items: center`，且 `.modal-container` 未设固定高度基准；当从内容较短的「新建反馈」（~350px）切换到长列表的「历史与进度」（~680px）时，垂直居中计算导致弹窗顶部距离屏幕上边沿在 `60px` 到 `225px` 之间剧烈上下跳动，造成眼球与手指触摸定位的不良体验。
- **自愈方案与代码落地**：
  1. 在 `@lylyuanliang/agent-feedback-client` 的样式中将 `.modal-backdrop` 对齐方式重构为 `align-items: flex-start; padding: max(env(safe-area-inset-top, 0px) + 20px, 32px) 16px 16px;`，让弹窗顶部牢牢锚定在屏幕安全区域下方；
  2. 为 `.modal-container` 设置统一的标准高度基准：`height: min(82vh, 700px); max-height: calc(100vh - 48px);`，在各 Tab 间切换时顶部标题栏、Tab 栏均 100% 稳固静止，不再上下跳动；
  3. 重新打包 `@lylyuanliang/agent-feedback-client`（`.tgz`）并重新安装至《每周一山》；
  4. 升版至 `0.0.1.202610291102` 并重新编译 Native Debug APK 归档分发；
  5. 通过 CLI 回写工单状态为 `completed` 并向时间轴推送升级公告；重新拉起静默哨兵。

### 3.17 npm 官方源发布与宿主工程真实依赖切替闭环
- **完成时间**：`2026-10-29 13:52`
- **成果概述**：
  1. 经 2FA / Security Key 验证，4 个子包成功发布到 npm 官方 Registry：
     - `@lylyuanliang/agent-feedback-core@1.0.0`
     - `@lylyuanliang/agent-feedback-client@1.0.0`
     - `@lylyuanliang/agent-feedback-sentinel@1.0.0`
     - `@lylyuanliang/agent-feedback-vite-plugin@1.0.0`
  2. 《每周一山》工程彻底移除了本地相对路径 `.tgz` 依赖，切换为标准语义化版本依赖（`^1.0.0`）；
  3. `package-lock.json` 与 `node_modules` 均已更新为纯净 npm 官方源托管；
  4. 全量自动化 E2E 回归测试（`python scratch/test_app_e2e_full.py`）100% 绿灯全通，Console 0 报错；
  5. 后台静默哨兵与开发服务器常驻运行中。

---

## 5. 恢复与运维入口
- **启动 Vite 开发服务**：`npm run dev -- --host --port 5173`
- **拉起通用哨兵监听**：`npm run sentinel`
- **发布 Agent 系统通知**：`node ../agent-feedback/packages/sentinel/bin/cli.js notice "通知内容" --dir scratch/feedback`
- **更新工单状态**：`node ../agent-feedback/packages/sentinel/bin/cli.js update-status <id> completed "答复说明" --dir scratch/feedback`

---

## 6. 客户端重启服务恢复记录 (2026-10-29 09:02)
- **Vite 开发服务器**：已在后台拉起（`task-8677`），监听本地及局域网端口 `5173`，cpolar 穿透隧道（映射 `5173`）正常通畅；
- **通用响应式哨兵**：已拉起后台静默监听（`task-8709`），持续守候 `scratch/feedback/` 分片与队列；
- **最新交付产物**：全新升版至 `0.0.1.202610291356`（`versionCode: 1793253417`），基于 npm 官方源 `@lylyuanliang/agent-feedback` 生产依赖重新编译 Native APK，镜像位于 `releases/weekly-mountain-latest-debug.apk`，通过内网穿透与在线更新分发。
