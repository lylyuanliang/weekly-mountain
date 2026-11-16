# Handoff: 修复山峰车程数据缺失、区域资源包名称遮挡及下载卡 5% 问题

## 1. 任务背景与问题诊断
收到端侧真实反馈哨兵上报的四项工单：
- **工单 1 (`#1794816183822`)**: 云顶山山峰详情中「成都车程」显示 `-- h` 和 `约 -- 小时直达`。
  - *根因*: `src/data/mountains.json` 与 `src/data/regions/chengdu/mountains.json` 中包括云顶山在内的 10 座山峰缺失 `drive_hours` 字段。
- **工单 2 (`#1794816293508`)**: 区域切换面板中「重庆周边」名称在「下载离线包（约 87KB）」长按钮下被挤压遮挡，只露出一个“重”字。
  - *根因*: `RegionPickerSheet.vue` 中未给区域名称设置 `shrink-0` 保护，右侧长按钮占用了 168px，在 369px 紧凑移动端屏幕下挤压了标题。
- **工单 3 & 4 (`#1794816384369` & `#1794816486129`)**: 点击下载重庆资源包，进度条一直停滞在「下载中 5%」随后报错失败。
  - *根因*:
    1. `.gitignore` 中配置了 `*.zip`，导致 `public/dist-packs/*.zip` 与 `dist-packs/*.zip` 未被 Git 跟踪上传，外部 GitHub/jsDelivr 源返回 404；
    2. `resourcePackService.js` 候选源优先请求根本不存在的加速镜像，缺乏单次超时（导致 fetch 挂起数十秒停在 5%）；
    3. SPA 路由对缺失文件返回 `index.html`（200 OK），未做 Content-Type 与 ZIP 文件头魔数校验，导致当成损坏包校验 SHA 失败；
    4. 原生 Capacitor WebView 环境下未能优先尝试同源直连路径。

---

## 2. 解决方案与修改文件

| 文件路径 | 修改类型 | 说明 |
| :--- | :--- | :--- |
| `src/data/mountains.json` | 修改 | 补齐云顶山 (1.5h)、轿顶山 (4h)、猫鼻梁 (3.5h) 等 10 座山峰的 `drive_hours` 数据 |
| `src/data/regions/chengdu/mountains.json` | 修改 | 同步补齐 10 座山峰的 `drive_hours`，保持全同构 |
| `src/data/regions.json` | 修改 | 重新运行 `build_region_packs.py`，更新包大小与 SHA-256 元数据 |
| `.gitignore` | 修改 | 显式解禁 `!public/dist-packs/*.zip` 与 `!dist-packs/*.zip`，允许静态离线包纳入版本跟踪 |
| `public/dist-packs/*.zip` | 刷新 | 重新构建并同步最新地域压缩包 |
| `src/components/common/RegionPickerSheet.vue` | 修改 | 为区域名称设定 `shrink-0` 强制保护，优化卡片与按钮 padding/gap，杜绝挤压 |
| `src/services/resourcePackService.js` | 修改 | 候选源优先尝试同源相对路径与 DevServer，加入 6s 超时熔断，核验 ZIP `PK\x03\x04` 文件头 |
| `docs/handoffs/fix-drive-hours-and-region-pack-download.md` | 新增 | 本次自愈修复的完整交接记录 |

---

## 3. 自测与回归验证结果
1. **数据一致性验证**:
   - `mountains.json`: 51 座山峰 `drive_hours` 缺失数为 0；
   - `chengdu/mountains.json`: 51 座山峰 `drive_hours` 缺失数为 0；
   - `chongqing/mountains.json`: 36 座山峰 `drive_hours` 缺失数为 0。
2. **测试套件回归**:
   - `tests/test_region_datasets.py`: 5/5 PASSED (100%)
   - `tests/test_region_pack_builder.py`: 5/5 PASSED (100%)
   - `tests/test_resource_pack_service.js`: 9/9 PASSED (100%)
   - `tests/test_store_multi_region.js`: 6/6 PASSED (100%)
   - 全文受限词扫描：0 处违规。
3. **前端生产构建与 Android 资产同步**:
   - `npm run build` 成功，153 个图片资产与 `dist-packs` 完整同步到 Android。
4. **工单闭环回写**:
   - 已通过 CLI 将 5 条反馈全部更新为 `completed` 并附上详细回复说明：
     - `1794816183822` (云顶山车程缺失)
     - `1794816293508` (重庆名称遮挡)
     - `1794816384369` (下载卡 5%)
     - `1794816486129` (下载失败异常)
     - `1794820057174` (资源包无图片说明：首期轻量包 87KB 专注核心地理与轨迹数据，暂未捆绑数十兆高清实拍图；展示暗黑高山等高线剪影兜底图)

---

## 4. 本地 APK 构建与真机联测包归档
- **构建版本**: `v0.4.0.202611161656`
- **正式发布版 (Release)**:
  - 路径: `weekly-mountain-v0.4.0.202611161656-release.apk` (28.25 MB)
  - SHA-256: `e1bd18577e2bcc93b5929856a3a7f9c2b960368a85512284b249fe2bf60ba83c`
- **内测调试版 (Debug)**:
  - 路径: `weekly-mountain-v0.4.0.202611161656-debug.apk` (29.44 MB)
  - SHA-256: `aa45421fef7ad05f14abb4fc18b0b6c24da831091e910953e7c6242f037c1b8f`
- **局域网/应用内下载路径**: 已自动同步至 `releases/weekly-mountain-latest-debug.apk`，在 App 内点击「本地调试包」或在手机浏览器中访问 `http://10.1.9.168:5173/releases/weekly-mountain-latest-debug.apk` 即可极速下载安装。
