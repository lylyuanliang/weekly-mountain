# 主题：修复 GitHub CI APK 体积与签名不一致、更新状态机卡死及微信导航适配

- 当前状态：已完成 (completed)
- 完成时间：2026-11-04
- 对应模块：
  - `weekly-mountain`:
    - CI/CD 构建流水线：`.github/workflows/build-apk.yml`
    - 原生签名配置：`android/app/build.gradle`, `android/app/debug.keystore`
    - 静态资源复制防静默退出：`scripts/copy_assets.js`
    - 更新状态机与弹窗：`src/stores/updateStore.js`, `src/components/common/AppUpdateModal.vue`
    - 微信浏览器导航引导：`src/components/detail/MountainDetailSheet.vue`, `src/utils/appLauncher.js`

## 1. 核心问题定位与根因分析

### 1.1 覆盖安装签名冲突问题 (INSTALL_FAILED_UPDATE_INCOMPATIBLE)
- **现象**：用户在手机安装旧版后，通过 App 内更新下载最新版安装失败，系统提示“签名不一致，请卸载重装”。
- **根因**：用户手机安装的历史包来自开发机本地构建，使用的是 Windows 本机 `~/.android/debug.keystore`（公钥证书指纹固定：`1D:82:AB:3B:36:C8:96:4B:F3:C3:24:21:24:D3:FA:5B:FC:E4:B4:62:88:F1:76:5D:DD:D3:8C:FD:36:2C:E1:FD`）。而 GitHub Actions CI 运行在全新 Ubuntu 虚拟机上，无预置 keystore，由 AGP 动态生成临时私钥签名，导致两次打包签名不一致。
- **解决**：将宿主机 `debug.keystore` 固化并提交至项目 `android/app/debug.keystore`，在 `android/app/build.gradle` 中显式指定 `signingConfigs.debug` 和 `signingConfigs.release` 均绑定该密钥，确保无论开发机本地还是 GitHub CI 构建的 APK 均拥有 100% 相同证书签名。

### 1.2 更新弹窗状态机停滞在“您正在使用最新版本”
- **现象**：安装失败或退出系统安装界面后，打开更新弹窗时，顶部仍显示“发现新版本”，但主体内容却显示“(✓) 您正在使用最新版本”，无法再次点击安装或重新下载；杀死 App 进程重启后恢复正常。
- **根因**：原生 `MainActivity.java` 唤起安装时发送了 `notifyJsUpdateStatus("completed", 100, ...)`，前端 `updateStore.downloadStatus` 被置为 `'completed'`。然而 `AppUpdateModal.vue` 中缺少 `downloadStatus === 'completed'` 的视图分支，导致跳过 `hasUpdate` 视图直接进入 `v-else`（“您正在使用最新版本”）。且 `updateStore.checkForUpdate()` 和 `closeModal()` 未将 `downloadStatus` 重置为 `'idle'`。
- **解决**：
  1. 在 `updateStore.js` 中增加状态重置：每次重新检测版本或关闭弹窗时重置 `downloadStatus` 为 `'idle'`（若非活跃下载中）；
  2. 在 `AppUpdateModal.vue` 中新增专门的 `completed` 视图卡片（“新版本安装包已就绪”），并提供「再次调起系统安装」与「重新下载」双按钮。

### 1.3 GitHub Actions 构建产物体积异常 (3.94 MB vs 28+ MB)
- **现象**：GitHub Releases 发布的 release/debug 两个 APK 均为 3.94 MB，且 SHA256 完全相同，远小于本地正常包（约 28 MB）。
- **根因**：
  1. `.github/workflows/build-apk.yml` 中归档 APK 使用了 `find android/ -name "*.apk" | head -n 1`。在 Linux 文件系统遍历中，`build/intermediates/` 字典序先于 `build/outputs/`，导致抓取到了中间临时或未合并资源的残缺 APK；
  2. `scripts/copy_assets.js` 若发生目录未找到时执行了 `process.exit(0)`，会造成静默成功而漏打包 21MB 山峰图片；
  3. CI 缺少产物体积门禁校验。
- **解决**：
  1. 将归档路径精准固化为 `android/app/build/outputs/apk/debug/app-debug.apk`；
  2. `scripts/copy_assets.js` 增加断言防御：源目录不存在、复制计数为 0 或总大小 < 10MB 时立即 `process.exit(1)` 抛错阻断构建；
  3. GitHub Actions 流水线中增加产物体积硬门禁：要求生成的 APK 大小必须大于 20 MB，否则立刻失败报警。

### 1.4 微信内部浏览器导航直接跳转受限
- **现象**：微信内置浏览器出于安全沙箱限制，直接点击第三方地图 Deep Link（高德、百度等）会被拦截或无响应，但在手机外部系统浏览器打开可以正常调起。
- **解决**：
  1. 利用已有的 `isWeChat()` 检测微信内部浏览器环境；
  2. 在 `MountainDetailSheet.vue` 导航弹窗顶部增设醒目橙色提示条：“微信内置浏览器限制提示：受微信限制无法直接唤起手机导航 App，建议点击右上角「···」选择「在浏览器打开」”；
  3. 在微信内点击时给出更精准的交互引导，同时保留「网页版高德直接导航」与「复制终点坐标」兜底能力。

## 2. 验证与自测结果

1. **证书指纹对齐**：
   - 运行 keytool 对比 `android/app/debug.keystore` 与 `~/.android/debug.keystore`，证书指纹 SHA256 均为 `1D:82:AB:3B:36:C8:96:4B:F3:C3:24:21:24:D3:FA:5B:FC:E4:B4:62:88:F1:76:5D:DD:D3:8C:FD:36:2C:E1:FD`，100% 一致；
2. **静态资源复制断言**：
   - 运行 `node scripts/copy_assets.js`，成功复制 153 个图片文件共 20.22 MB，断言通过；
3. **前端构建验证**：
   - `npm run build` 和 `npm run build:release` 均成功完成构建，产物完整；
4. **微信导航提示**：
   - `MountainDetailSheet.vue` 引入 `isWeChat` 计算属性，微信环境下自动呈现暖色引导卡片并在调起时精准提示。

## 3. 分批原子提交与发版记录

- **目标发版 Tag**：`v0.3.0.202611041803`
- **原子提交批次**：
  1. `6bd3acc` - `fix(update): 修复更新弹窗状态机停滞与微信内置浏览器导航引导卡片`
  2. `34d388e` - `fix(android): 固化 debug.keystore 签名配置并增设静态资源复制断言`
  3. `8b5d9df` - `fix(ci): 锁定 APK 规范归档路径并增设 20MB 产物体积硬门禁`
  4. `76159b2` - `chore(release): 升级时间戳版本至 v0.3.0.202611041803 并同步版本元数据`
  5. `docs(handoff): 更新签名对齐、CI双包体积硬门禁与微信导航交接文档`
