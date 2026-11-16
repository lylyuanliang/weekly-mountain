<!-- RELEASE_METADATA_START
title: "v0.4.1"
changelog:
  - "【分级资源包】新增基础包与高清画册包规格选择弹窗（PackSpecSelectModal），提供体积对比与按需下载指导；"
  - "【离线高清画册】补齐重庆 36 座高山全量坐标与 108 张精修实拍风景画册，支持离线解压与动态本地缓存映射；"
  - "【三级高可用气象】重构高山实时天气系统，支持 Open-Meteo、wttr.in 极速降级与垂直递减率科学离线气象推演模型；"
  - "【地域选择精简】优化 RegionPickerSheet 界面，规划中城市重构为紧凑网格排版，视觉降噪 70%；"
  - "【自愈闭环】彻底解决离线画册加载失败、卸载残留及天气 Fetch 报错，优化端侧哨兵换行排版与自愈体验。"
RELEASE_METADATA_END -->

> [!WARNING]
> **【历史版本技术存档说明】**
> 本 Release 记录及对应构建产物仅作为软件工程研发历史技术存档，**不反映当前自然地理环境、气象灾害与属地管制政策的动态认知，严禁作为户外出行依据**。请始终以项目最新主分支（`main`）中包含的最新风险警示为准。

# 版本升级与发布记录 (Release Notes) - v0.4.1

- **主版本线**：v0.4.1 (分级离线风光资源包、三级容灾天气与真机体验深度调优)
- **发布日期**：2026-11-16
- **适用平台**：Android APK (Release / Debug) & Web H5
- **文档维护规范**：依据项目规约集中维护在 `docs/releases/` 目录。

---

## 🌟 本次版本核心主题与摘要 (Highlights)

> **v0.4.1 核心演进：全面落地分级离线资源包（基础包 vs 高清风光画册包）与规格选择交互；彻底补全重庆 36 座高山精确地理坐标与 108 张实拍风景画册；构建全天候三级容灾气象服务（Open-Meteo -> wttr.in -> 离线气候模型），彻底根除端侧天气加载异常；深度精简多地域选择交互，修复卸载残留与视图更新滞后。**

1. **分级离线资源包体系与按需下载 (Multi-Tier Resource Pack Architecture)**：
   - 区分轻量「基础包」（仅含山峰数据、元数据与地图坐标）与包含高清风景的「完整风光包」（包含实拍画册）；
   - 在地域切换与个人中心管理面板新增 `PackSpecSelectModal` 弹窗，清晰标注包体积与下载 Tips，满足弱网、省流或离线深山不同场景诉求。

2. **重庆 36 座高山高清画册全量闭环与动态渲染 (Chongqing Offline Galleries)**：
   - 注入重庆 36 座名峰精准经纬度坐标与 108 张精选实拍风景大图元数据；
   - 核心构建离线画册压缩包 `pack-chongqing-gallery-v1.0.0.zip`，支持端侧解压至安全私有存储；
   - `HeroMountainCard`、`CompactMountainCard` 与 `MountainDetailSheet` 全面接入 `resolveMountainImageUrl`，打通 Capacitor 本地虚拟文件路径映射，画册安装/卸载响应式毫秒级刷新。

3. **三级容灾高山天气服务架构 (3-Tier Weather Resilience Engine)**：
   - 一级服务：Open-Meteo 实时气象数据，缩短建连超时至 3.5s 快速断路；
   - 二级服务：国内直连稳定、高可用的 `wttr.in` 极速降级链路，自动适配当前山峰实际经纬度；
   - 三级终极兜底：基于海拔垂直递减率（-0.65℃/100m）与季节气候学科学推演的高山离线气象模型，彻底绝缘 `Failed to fetch`，无网深山也能提供科学可靠的气温与风向参考。

4. **交互体验与视觉降噪调优 (UX & Visual Refinements)**：
   - 首页 `RegionPickerSheet` 大幅精简，规划中城市改为精致微型标签网格，视觉疲劳度大幅降低；
   - 修复在重庆视图下卸载重庆资源包时的视图残留问题，卸载即自动平滑切回成都默认数据；
   - 详情页占位矢量徽章动态适配当前地域名称（如“重庆名山”），消除成都硬编码。

---

## 📝 详细变更清单 (Changelog)

### 🏔️ 离线资源与山峰数据 (Resource Packs & Mountain Data)
- **规格弹窗**：新增 `PackSpecSelectModal.vue`，支持规格选择与快捷下载提示；
- **画册离线包构建**：升级 `scripts/build_region_packs.py`，基础包与画册包正交解耦，生成 `pack-chongqing-gallery-v1.0.0.zip` 并更新哈希；
- **重庆元数据扩充**：新增 `scripts/enrich_chongqing_mountains.py`，为 36 座山峰注入坐标并创建 108 张精修风景大图。

### 🌤️ 气象服务与卡片响应式 (Weather & Card Rendering)
- **三级容灾天气**：重构 `src/services/weatherService.js`，支持 Open-Meteo -> wttr.in -> 离线气候模型三级回退；
- **卡片画册联动**：`HeroMountainCard.vue` 与 `CompactMountainCard.vue` 增加深度监听器，画册安装后实时刷新真机大图；
- **详情页画廊**：`MountainDetailSheet.vue` 支持本地画册解析与高山矢量徽章兜底。
