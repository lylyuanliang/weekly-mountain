# 主题：GitHub Release 离线资源包挂载、APK 物理瘦身与临时测试 Tag 验证交接

- 当前状态：已完成 (completed)
- 涉及阶段：
  1. APK 物理瘦身：根除基线 APK 中对重庆画册图片与离线 zip 的冗余打包（单包净瘦身 14.2MB）；
  2. GitHub Actions 流水线修复：`.github/workflows/build-apk.yml` 自动编译并挂载 `dist-packs/*.zip` 离线资源包与 SHA-256 清单；
  3. 临时 Tag 隔离防污染：使用 `v0.4.2-preview.1` 临时预发布 Tag 触发 CI 流水线（Run ID `44000290228`），不占用正式 Tag；
  4. 资源包下载与端侧候选通道健全性验证：Release 附件、直链与加速镜像链路验证。
- 恢复入口：
  - CI 工作流：[`.github/workflows/build-apk.yml`](file:///d:/file_save/workspace/github/weekly-mountain/.github/workflows/build-apk.yml)
  - 资源包服务：[`src/services/resourcePackService.js`](file:///d:/file_save/workspace/github/weekly-mountain/src/services/resourcePackService.js)
  - 资产同步脚本：[`scripts/sync_android_assets.js`](file:///d:/file_save/workspace/github/weekly-mountain/scripts/sync_android_assets.js)
  - 地域包构建脚本：[`scripts/build_region_packs.py`](file:///d:/file_save/workspace/github/weekly-mountain/scripts/build_region_packs.py)
  - 本地构建脚本：[`scripts/build_local_apks.py`](file:///d:/file_save/workspace/github/weekly-mountain/scripts/build_local_apks.py)

---

## 一、背景与核心痛点

1. **APK 体积翻倍根因**：
   - 之前构建中，重庆 108 张精修风景大图误同步进 `assets/mountains/`（~6.8MB），同时 `public/dist-packs/` 下的离线 zip 包（~7.14MB）又被全量复制进 Android assets，导致双重冗余，APK 体积由 ~28MB 暴增至 43.15MB（Debug）和 41.96MB（Release）。
2. **GitHub Release 资源包缺失根因**：
   - 用户反馈在 GitHub Release 页面中只有 APK 与 `SHA256SUMS.txt`，完全没有 `dist-packs/*.zip` 附件，导致端侧按需下载无法拉取。
   - 根因为 `.github/workflows/build-apk.yml` 的 `softprops/action-gh-release@v2` 中的 `files:` 列表仅配置了 `*.apk` 与 `SHA256SUMS.txt`，未添加 `dist-packs/*.zip`。
3. **测试规范硬门禁**：
   - 调试流水线与验证期间，严禁占用或污染正式版本 Tag，必须使用包含连字符的临时 Tag（如 `v0.4.2-preview.1`），GitHub Actions 自动标记为 Pre-release 且不覆盖 Latest 标签。

---

## 二、修复实施细节

1. **安装包物理瘦身与架构隔离**：
   - 清理 `assets/mountains/` 中的 108 张重庆未压缩风景图，仅保留成都基线 51 座山的 153 张底图（20.22MB）；
   - 重庆画册 108 张大图专门由 `src/data/regions/chongqing/gallery/` 经 `scripts/build_region_packs.py` 打包为独立画册包 `pack-chongqing-gallery-v1.0.0.zip`（6.81MB）；
   - 更新 `scripts/sync_android_assets.js` 与 `scripts/copy_assets.js`，在同步 Android assets 时物理忽略并清理 `dist-packs` 目录；
   - 本地构建验证：Release APK 成功降至 27.74MB，Debug APK 成功降至 28.93MB，单包净瘦身 14.22MB。

2. **GitHub Actions 流水线自动化挂载**：
   - 修改 `.github/workflows/build-apk.yml`：
     - 在构建前运行 `python scripts/build_region_packs.py` 确保生成最新资源包；
     - 在 SHA-256 计算步骤加入 `dist-packs/*.zip` 散列；
     - 在 `softprops/action-gh-release@v2` 中将 `dist-packs/*.zip` 纳入 `files:` 挂载列表；
     - 增加 `prerelease: ${{ contains(env.TAG, '-') }}` 机制，确保带短横线的临时 Tag 绝不篡改 Latest 正式版。

3. **客户端下载链路健全性增强**：
   - 修改 `src/services/resourcePackService.js`：
     - 优化多通道下载优先级：本地开发服务 ➔ 动态版本 Tag Release 资源链接（含加速通道）➔ 临时预览 Tag 备选 ➔ Latest 兜底 ➔ CDN ➔ GitHub Raw；
     - 解决原硬编码 `/releases/download/packs/` 路径引发的 404 错误。

---

## 三、自测与流水线核验结果

1. **本地单元测试套件全部通过**：
   - `node tests/test_weather_and_gallery_resilience.js`（5/5 通过）；
   - `node tests/test_resource_pack_service.js`（11/11 通过）；
   - `node tests/test_store_multi_region.js`（6/6 通过）。

2. **GitHub Actions 临时流水线核验 (Run ID 44000290228)**：
   - 触发 Tag：`v0.4.2-preview.1`
   - 流水线状态：`completed` / `conclusion: success`
   - Release 资产列表（共 6 个附件全部挂载就绪）：
     - `pack-chengdu-v1.0.0.zip` (0.43 MB)
     - `pack-chongqing-gallery-v1.0.0.zip` (6.81 MB)
     - `pack-chongqing-v1.0.0.zip` (0.09 MB)
     - `SHA256SUMS.txt` (0.00 MB)
     - `weekly-mountain-v0.4.2-preview.1-debug.apk` (28.93 MB)
     - `weekly-mountain-v0.4.2-preview.1-release.apk` (27.74 MB)

3. **离线包下载直链实测校验**：
   - `curl -I -L "https://github.com/lylyuanliang/weekly-mountain/releases/download/v0.4.2-preview.1/pack-chongqing-gallery-v1.0.0.zip"`
   - 响应状态：`HTTP/1.1 302 Found` ➔ `HTTP/1.1 200 OK`，下载直链完全通畅。
