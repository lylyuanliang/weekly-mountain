<!-- RELEASE_METADATA_START
title: "v0.4.2"
changelog:
  - "【安装包极致瘦身】根除安装包冗余资源污染，APK 净减负 14.2MB（Release 27.7MB / Debug 28.9MB），重回极致轻量；"
  - "【架构边界隔离】严格遵循资源包正交设计，重庆 108 张精修画册彻底移出 base assets，仅由独立画册包按需下载；"
  - "【构建流水线加固】升级 CI 与 assets 同步脚本，在 Release 页面自动完整挂载多地域离线资源包（dist-packs/*.zip）并计算 SHA-256；"
  - "【版本校验与下载链路】注入应用内版本全局元数据，打通高速镜像与多通道离线包下载链路。"
RELEASE_METADATA_END -->

> [!WARNING]
> **【历史版本技术存档说明】**
> 本 Release 记录及对应构建产物仅作为软件工程研发历史技术存档，**不反映当前自然地理环境、气象灾害与属地管制政策的动态认知，严禁作为户外出行依据**。请始终以项目最新主分支（`main`）中包含的最新风险警示为准。

# 版本升级与发布记录 (Release Notes) - v0.4.2

- **主版本线**：v0.4.2 (安装包物理瘦身、离线资源包正交隔离与构建资产同步加固)
- **发布日期**：2026-11-17
- **适用平台**：Android APK (Release / Debug) & Web H5
- **文档维护规范**：依据项目规约集中维护在 `docs/releases/` 目录。

---

## 🌟 本次版本核心主题与摘要 (Highlights)

> **v0.4.2 核心演进：全面根除 base APK 安装包内的冗余资源，严格践行“核心包极简轻量、扩展画册按需下载”的多地域资源包正交架构。清理误入基线 assets 的 108 张重庆未压缩风景图片与 7.14MB 离线 zip 压缩包，Android 安装包体积立减 14.2MB（Release 版从 41.96MB 降至 27.74MB，Debug 版从 43.15MB 降至 28.93MB）；同步加固构建同步流水线，彻底杜绝资源包污染 base 安装包。**

1. **核心安装包极致瘦身 (APK Size Optimization)**：
   - 彻底移出 base APK 中的 108 张重庆风景摄影大图与 `dist-packs/` 离线压缩包；
   - Android 原生 Assets 体积从 43.4MB 压降至 28.5MB，正式版 Release APK 压降至 27.74MB，内测调试版 Debug APK 压降至 28.93MB，净节省 14.2MB 流量与空间。

2. **资源包正交架构边界加固 (Resource Pack Strict Boundary)**：
   - 严格规范资产目录职责：`assets/mountains/` 仅承载成都基线名山的 153 张核心底图；
   - 重庆 108 张精修画册大图全量归属于 `src/data/regions/chongqing/gallery/`，仅作为 `pack-chongqing-gallery-v1.0.0.zip` 独立离线包在端侧按需下载并解压至私有数据沙箱，绝不占用基础包空间。

3. **构建与资产同步脚本加固 (Build Pipeline Hardening)**：
   - `scripts/sync_android_assets.js` 增加路径过滤，同步至 Android 原生工程时物理忽略并自动清理 `dist-packs` 目录；
   - `scripts/copy_assets.js` 引入自动清理机制，防范任何历史扩展图片残留；
   - `scripts/enrich_chongqing_mountains.py` 去除跨目录多余拷贝逻辑。

---

## 📝 详细变更清单 (Changelog)

### 📦 资产管理与工程构建 (Asset Management & Build Scripts)
- **同步脚本重构**：更新 [scripts/sync_android_assets.js](file:///d:/file_save/workspace/github/weekly-mountain/scripts/sync_android_assets.js)，物理隔离 `dist-packs`；
- **图片同步精简**：优化 [scripts/copy_assets.js](file:///d:/file_save/workspace/github/weekly-mountain/scripts/copy_assets.js)，增加目标目录陈旧图片清理；
- **数据源生成脚本修正**：优化 [scripts/enrich_chongqing_mountains.py](file:///d:/file_save/workspace/github/weekly-mountain/scripts/enrich_chongqing_mountains.py)，仅写入离线画册目录；
- **基线资产精简**：从 `assets/mountains/` 物理删除 108 张重庆未压缩 JPG；
- **CI 流水线加固**：更新 [.github/workflows/build-apk.yml](file:///d:/file_save/workspace/github/weekly-mountain/.github/workflows/build-apk.yml)，在 Release 附件中自动挂载 `dist-packs/*.zip` 与 SHA-256 校验列表；
- **客户端版本注入与下载链路**：在 [src/main.js](file:///d:/file_save/workspace/github/weekly-mountain/src/main.js) 与 [src/services/resourcePackService.js](file:///d:/file_save/workspace/github/weekly-mountain/src/services/resourcePackService.js) 注入全局版本元数据并完善多候选下载通道。
