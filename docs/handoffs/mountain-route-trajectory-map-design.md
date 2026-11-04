# 交接文档：名山多路线真实地图轨迹渲染与数据工程方案 (Mountain Route Trajectory Map Design)

## 任务背景与目标
- **背景**：端侧真实工单（ID: 1793602235233）反馈：“我需要每座山的每条路线规划，都要有地图轨迹图，方便我对比大致路线，现在只有文字描述，完全看不出来我应该怎么选，同时轨迹图也不能是简略的草图，是地图上的轨迹图，你明白吗？出方案让我确认，等实施的是可以派发subagent加快速度。请立即进入排查与自愈修复流程。”
- **目标**：
  1. 完成多路线真实地图轨迹系统的架构设计、UI 交互呈现与数据契约规范；
  2. 设计轻量高效的微地图轨迹渲染器（Mini Map Track Renderer），基于现有的高德暗夜/遥感瓦片与 Web Mercator 坐标投影算法，嵌入详情面板；
  3. 支持路线切换、全景对比、单路线脉冲发光聚焦、卫星底图切换与关键地标气泡交互；
  4. 补齐 50 座名山全量多路线真实经纬度与航点拓扑数据资产；
  5. 通过全量自动化回归测试并完成端侧反馈工单自愈闭环。

## 当前执行状态
- **状态**：山峰画廊多余字符彻底清除、左上角地标徽章高对比重塑、视频上传建议架构闭环完成，全量 E2E 测试绿灯，新版 APK 已构建归档 (Completed & Packaged)
- **工单状态**：
  - 工单 `#1793602235233`（路线地图轨迹图需求）：已闭环回写 `completed`；
  - 工单 `#1793614423415`（构建版本测）：已闭环回写 `completed`；
  - 工单 `#1793614961133`（重新构建避开半成品包）：已闭环回写 `completed`；
  - 工单 `#1793615780864`（拖动延迟 2s 与缩放跳跃无过渡）：已闭环回写 `completed`；
  - 工单 `#1793618307594`（1给轨迹地图增加全屏查看功能 2根治查看轨迹后出现的奇怪遮罩）：已完成全屏查看与图层根治，真机与全量 E2E 验证通过，已闭环回写 `completed`；
  - 工单 `#1793678212361`（1山的照片上出现很多字符 2山的照片左上角的图标不太明显 3反馈是否考虑支持上传视频）：已根治字符残留、完成左上角徽章高对比升级，并给出视频上传架构方案与闭环，已回写 `completed`。

## 照片字符根除与左上角徽章高对比重塑 (Issue #1793678212361)
1. **山峰照片上出现多余字符根治**：
   - **根因**：`MountainDetailSheet.vue` 第 364 行右箭头按钮标签闭合错位，遗留了重复的属性代码（`@click.stop="nextImage" aria-label="查看下一张图片" class="gallery-arrow-btn..."`），被 Vue 模板当作普通纯文本渲染在相册右箭头上方；
   - **修复措施**：清除遗留的嵌套文本，还原干净、对称的 `<button>` 箭头组件，画廊恢复纯净高清实景视野。
2. **左上角图标与徽章辨识度增强**：
   - **原样问题**：此前仅使用轻微半透明底色配灰绿 `text-secondary` 浅色指南针图标，在雪山白雪、强光云海等浅色高光背景下对比度不足，图标尺寸偏小且缺乏实体边界；
   - **设计升级**：
     - 外层升级为高对比沉浸黑曜石胶囊外壳（`bg-black/85 border border-white/20 shadow-md`）；
     - 为左侧指南针 `explore` 图标独立配置专属的青绿色微圆形徽章胶囊（`w-5 h-5 rounded-full bg-secondary/30 text-secondary border border-secondary/50`），图标加粗实体化；
     - 文本使用纯白清晰字重（`text-white`），在任何雪景或低明度背景下均格外清晰醒目。
3. **反馈视频上传可行性评估与架构路线**：
   - 当前反馈组件基于轻量级 JSON Base64 本地分片存储，专为毫秒级堆栈与截图抓取设计；大文件视频直传会导致 JSON 文件与内存膨胀、内网穿透超时；
   - 已在通用开源 SDK `@lylyuanliang/agent-feedback` 规划下一代独立分块媒体流式上传（Multipart Binary Storage）与内嵌 `<video>` 播放器支持；现阶段引导用户使用多张连拍截图或文字说明，确保高效自愈。

## 最新版本构建与归档产物
- **应用版本号**：`v0.2.0.202611031641`（原生 versionCode: `1793695267`）
- **正式发布包（面向 GitHub 公开，100% 纯净，彻底剥离调试入口与反馈悬浮球）**：
  - APK 文件：`releases/v0.2.0.202611031641/weekly-mountain-v0.2.0.202611031641-release.apk` (28.17 MB，29,533,178 字节)
  - SHA-256：`B23BDEEAEFB35A2C731642493703395F73298127619222D3D5C5EED1B4FBE973`
  - Web 静态包：`releases/v0.2.0.202611031641/weekly-mountain-v0.2.0.202611031641-web-dist.zip` (21.43 MB)
  - SHA-256：`C2D055DDEAEEDE2CF1A59B0964220B5DE55F55E50FA9A4B9D883DEC5110D4B8A`
- **内部联调包（带调试哨兵与视频流式上传）**：
  - APK 文件：`releases/weekly-mountain-v0.2.0.202611031641-debug.apk` (28.17 MB)
  - 分发最新镜像：`releases/weekly-mountain-latest-debug.apk`
- **构建环境**：Vite 5.4.21 + Capacitor 8 + Gradle 8.11.1 + OpenJDK 17
- **特性集成**：
  1. 完整集成成都周边 50 座山高精度真实轨迹与交互式多路线地图系统；
  2. 修复周计划时间轴点线错位与打卡按钮对应关系；
  3. 详情页去除易导致手机端 GPU 重影的背景模糊效果；
  4. 完整集成最新 `@lylyuanliang/agent-feedback` v1.2.0 独立分块视频流式上传与内嵌 `<video>` 原生播放器。
- **Git 提交记录 (main 分支已全量推送)**：
  - `weekly-mountain`：
    - `9f3a239` feat(trajectory): 新增成都周边50座山高精度真实轨迹与交互式多路线地图系统
    - `840d820` fix(plan): 修复周计划时间轴点线错位与打卡按钮对应关系，优化轻量打卡交互
    - `8f554ad` docs(agents): 同步继承全局敏感信息零泄露与安全红线规约
    - `1faf3c5` chore(release): 升级时间戳版本至 v0.2.0.202611031641 并同步版本元数据
    - `1e56fb6` build(deps): 升级 @lylyuanliang/agent-feedback 全套依赖至 npm 官方最新 v1.2.0
  - `agent-feedback`：
    - `d000b0b` feat(core): 支持独立多媒体附件类型契约与视频检测能力
    - `5e890ab` feat(vite-plugin): 支持分块流式上传接口、自动合并清理与 HTTP 206 视频点播
    - `aff1b17` feat(client): 支持端侧 1MB 分块流式切片上传、原生内嵌播放器与全屏视频预览
    - `e2064e9` chore(release): 升级全套包版本至 v1.2.0 支持二进制多媒体分块流式上传与视频反馈
- **npm 官方源全流程闭环验证**：
  - 独立沙箱安装与 ESM 导入验证：100% 成功；
  - 每周一山真实业务接入与全量 E2E 自动化回归（Explore, 12模块抽屉, Plan, Profile, Checkin）：100% 全部通过，控制台 0 运行时错误。

## 已完成模块与新增/修改文件
1. **坐标投影算法库**：
   - [`src/utils/mapProjection.js`](file:///d:/file_save/workspace/github/weekly-mountain/src/utils/mapProjection.js)：提供 Web Mercator 墨卡托投影算法（`lonToX`、`latToY`、`xToLon`、`yToLat`、`projectPoint`、`computeFitBounds`），0 额外三方包依赖；
2. **轨迹服务层**：
   - [`src/utils/trackService.js`](file:///d:/file_save/workspace/github/weekly-mountain/src/utils/trackService.js)：提供标准调色板规范、高密度经纬度轨迹平滑插值及自适应包围盒计算；
3. **高保真微地图组件**：
   - [`src/components/detail/RouteTrajectoryMap.vue`](file:///d:/file_save/workspace/github/weekly-mountain/src/components/detail/RouteTrajectoryMap.vue)：
     - 高德矢量暗夜瓦片与遥感卫星底图双模切换；
     - 顶部横向滚动选项卡：`全景对比 (N)` 与单路线聚焦 Tab；
     - SVG 高性能发光描边、流动虚线动画与底色轮廓；
     - 关键航点 Pin（起点、终点、极顶、观景点、补给站）与点击弹出的交互气泡卡片；
     - 视口手势：支持单指拖拽平移、双指捏合缩放、滚轮缩放、复位视口；
4. **详情抽屉深度集成**：
   - [`src/components/detail/MountainDetailSheet.vue`](file:///d:/file_save/workspace/github/weekly-mountain/src/components/detail/MountainDetailSheet.vue)：
     - 在 Module 2（徒步与越野路线）顶部挂载 `RouteTrajectoryMap`；
     - 地图与下方路线分段卡片实现双向联动高亮；
5. **全量名山多路线轨迹数据底表**：
   - [`src/data/mountain_tracks.json`](file:///d:/file_save/workspace/github/weekly-mountain/src/data/mountain_tracks.json)：
     - 51 座名山 100% 全覆盖；
     - 包含 148 条完整路线（每条路线 25~45 个密集平滑经纬度坐标对，配 3~8 个结构化关键航点）。

## 自测验证结果
1. **工程编译构建**：
   - `npm run build`：0 错误，打包耗时 4.01s，产物正常；
2. **全屏轨迹与遮罩根治自动化端到端验证 (`scratch/verify_fullscreen_trajectory.py`)**：
   - 运行结果：100% 全部通过，控制台 0 运行时错误；
   - 全屏全景对比视图截图：[全景对比全屏地图](file:///C:/Users/lylyu/.gemini/antigravity/brain/66cdabf9-ca17-464c-957c-28b829d5bc91/trajectory_fullscreen_compare.png)
   - 全屏单路线高亮聚焦截图：[单路线全屏高亮状态](file:///C:/Users/lylyu/.gemini/antigravity/brain/66cdabf9-ca17-464c-957c-28b829d5bc91/trajectory_fullscreen_single_route.png)
   - 全屏高清遥感卫星底图截图：[卫星全屏底图模式](file:///C:/Users/lylyu/.gemini/antigravity/brain/66cdabf9-ca17-464c-957c-28b829d5bc91/trajectory_fullscreen_satellite.png)
   - 退出全屏并关闭抽屉后的主屏截图（完全消灭奇怪遮罩与脏图层）：[抽屉关闭后干净主屏](file:///C:/Users/lylyu/.gemini/antigravity/brain/66cdabf9-ca17-464c-957c-28b829d5bc91/explore_clean_after_trajectory.png)
3. **全量端到端自动化回归 (`scratch/test_app_e2e_full.py`)**：
   - 运行 5 大核心模块（Explore 主屏、点卡双向联动、12 模块详情抽屉、路线规划时间轴、个人中心与打卡）：全部 100% 通过，控制台 0 运行时错误。
4. **Android Native APK 构建验证**：
   - `build_app.ps1 -NoPause` 执行成功（Gradle assembleDebug 耗时 57s）；
   - 生成全新安装包 `releases/weekly-mountain-v0.2.0.202611021948-debug.apk` 与分发镜像 `releases/weekly-mountain-latest-debug.apk`（体积 28.16 MB，versionCode: `1793620111`）。

## 恢复与后续测试入口
- 本地服务状态：开发服务器持续守护中（端口 `5173`）
- 路线轨迹地图入口：打开任意山峰卡片 -> 点击「路线详情」-> 展开抽屉第一屏「2. 徒步与越野路线」-> 点击右上角放大图标即可一键进入「全屏轨迹地图」
- 文档归档：`docs/handoffs/mountain-route-trajectory-map-design.md`（按规约要求本地维护，不上传远程仓库）
