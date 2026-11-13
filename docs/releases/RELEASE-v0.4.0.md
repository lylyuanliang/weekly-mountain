<!-- RELEASE_METADATA_START
title: "v0.4.0"
changelog:
  - "【多地域架构】落地多地域资源包架构，支持成都（51座）、重庆（36座）山峰数据动态按需加载与离线包下载/卸载；"
  - "【重庆高山】全面收录重庆 36 座经典徒步与探险山峰，涵盖缙云山、金佛山、武陵山、巫山神女峰等，支持基准距离与路线决策；"
  - "【Store热挂载】Pinia 数据流升级支持多地域响应式热挂载与异常平滑降级，切换地域毫秒级即时生效；"
  - "【管理面板】个人中心新增地域资源包管理面板与顶部快捷切换抽屉，已占空间一键释放；"
  - "【哨兵调优】集成 agent-feedback v1.4.1，实现移动端模态弹窗零闪烁、小屏 Tab 自适应紧凑排版与本地包下载体验优化。"
RELEASE_METADATA_END -->

> [!WARNING]
> **【历史版本技术存档说明】**
> 本 Release 记录及对应构建产物仅作为软件工程研发历史技术存档，**不反映当前自然地理环境、气象灾害与属地管制政策的动态认知，严禁作为户外出行依据**。请始终以项目最新主分支（`main`）中包含的最新风险警示为准。

# 版本升级与发布记录 (Release Notes) - v0.4.0

- **主版本线**：v0.4.0 (多地域资源包架构与重庆高山版图扩展)
- **发布日期**：2026-11-13
- **适用平台**：Android APK (Release / Debug) & Web H5
- **文档维护规范**：依据项目规约 `docs/releases/` 规范维护，集中维护在 `docs/releases/` 专属子目录。

---

## 🌟 本次版本核心主题与摘要 (Highlights)

> **v0.4.0 核心演进：突破成都周边单一地域限制，全面落地多地域离线资源包架构（Multi-Region Resource Pack Architecture）与重庆 36 座精选高山数据；深度打通 Pinia 响应式热挂载、地域切换抽屉与离线包按需下载/卸载；同时升级集成 agent-feedback v1.4.1，实现端侧模态弹窗硬件加速零闪烁与紧凑自适应排版。**

1. **多地域离线资源包架构 (Multi-Region Resource Pack Architecture)**：
   - 为避免随着收录地域增加导致安装包体积无序膨胀，全新设计“核心应用包 + 地域资源包”架构；
   - 原生混合端支持按需下载、动态解压挂载与一键卸载释放本地存储，网页端支持全量按需动态加载；
   - 离线包内置 SHA-256 完整性防篡改签名机制，保障数据加载安全稳定。

2. **重庆高山全景收录 (Chongqing Mountains Dataset)**：
   - 突破性引入重庆周边 36 座经典名峰（缙云山、金刀峡、金佛山、巫山神女峰、武陵山等）；
   - 完整收录标高、爬升、预估耗时、自驾车程、轨迹路线与避坑指南，且自动以解放碑为核心基准计算动态车程与直线距离。

3. **Pinia 多地域动态热挂载与平滑容错降级 (Reactive Hot-Mount & Graceful Degradation)**：
   - `regionStore` 与 `mountainStore` 实现全动态解耦，切换地域即时联动顶部搜索、Bento 魔方与地图图层更新；
   - 健全容错降级机制：当遇到未收录地域或资源包受损时，自动安全回退至默认数据集，保障零白屏与零崩溃。

4. **快捷地域切换抽屉与离线包管理面板 (Interactive Region UI)**：
   - 顶部导航栏支持点击当前地域呼出底部轻量选择抽屉（`RegionPickerSheet`），支持一键无缝换城；
   - 个人中心增加「地域资源包管理」专区，清晰呈现当前地域安装状态、包体积大小与下载进度条，支持随时下载与卸载清理。

5. **端侧哨兵与反馈体验深度调优 (Agent Feedback v1.4.1 集成)**：
   - 全面升级 `@lylyuanliang/agent-feedback` 基础组件库至 v1.4.1；
   - 引入 GPU 硬件加速图层与 `toggleModalDom` 原生局部切换，根治真机模态弹窗重新渲染白屏闪烁；
   - Tab 选项卡紧凑自适应排版与选中项平滑居中，消除小屏设备截断；
   - 优化本地调试包下载界面布局，解决极窄屏 WebView 下文件体积与编译时间挤压折行问题。

---

## 📝 详细变更清单 (Changelog)

### 🗺️ 多地域与高山数据 (Multi-Region & Mountain Data)
- **多地域数据解耦**：将单体山峰数据重构为 `src/data/regions/chengdu/mountains.json` 与 `src/data/regions/chongqing/mountains.json`；
- **资源包构建器**：编写 `scripts/build_region_packs.py`，支持自动化校验、构建地域独立 zip 资源包并更新 `regions.json` 元数据哈希；
- **全量测试套件**：建立 `tests/test_region_datasets.py`、`tests/test_region_pack_builder.py`、`tests/test_resource_pack_service.js` 与 `tests/test_store_multi_region.js`，全部通过验证。

### 🎨 界面与交互 (UI / UX)
- **RegionPickerSheet.vue**：新增半屏地域切换抽屉组件，支持地域高山数量展示与当前选中态标记；
- **ProfileView.vue**：新增地域离线资源包管理模块，支持端侧下载、进度反馈与安全卸载；
- **AlpineDevApkExtensionView.vue**：优化本地调试包卡片布局，排版自适应小屏设备。

### 🤖 依赖与运维 (Dependencies & Ops)
- **依赖升级**：`package.json` 升级 `@lylyuanliang/agent-feedback-*` 全套依赖至 `^1.4.1`；
- **安全检查**：全量扫描代码与文档，确保受限词汇 0 违规，无任何敏感信息。

---

## 📦 安装包与分发说明

| 构建版本 | APK 文件名 | 文件大小 | 适用场景说明 |
| :--- | :--- | :--- | :--- |
| **🚀 正式发布版 (Release)** | `weekly-mountain-v0.4.0.<timestamp>-release.apk` | 约 27.5 MB | 推荐日常使用：采用 Zero-DCE 纯净精简构建，已剔除调试悬浮球与哨兵诊断模块，启动飞快、性能最优。 |
| **🛠️ 开发者内测版 (Debug)** | `weekly-mountain-v0.4.0.<timestamp>-debug.apk` | 约 29.5 MB | 开发者联调专属：内置真机智能哨兵与开发机直连面板，支持边测边自愈，免除发布等待。 |
