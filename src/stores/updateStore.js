import { defineStore } from 'pinia';
import { ref } from 'vue';
import { APP_VERSION } from '@/config/version.js';
import { fetchLatestRelease, compareVersions } from '@/services/updateService.js';
import { openExternalUrl } from '@/utils/appLauncher.js';

export const useUpdateStore = defineStore('update', () => {
  const isChecking = ref(false);
  const hasUpdate = ref(false);
  const versionDiffStatus = ref('up_to_date'); // 'update_available' | 'ahead_of_release' | 'up_to_date'
  const latestRelease = ref(null);
  const downloadStatus = ref('idle'); // 'idle' | 'downloading' | 'installing' | 'completed' | 'error' | 'permission_required'
  const downloadProgress = ref({
    percent: 0,
    receivedBytes: 0,
    totalBytes: 0,
    message: ''
  });
  const errorMessage = ref('');
  const isModalOpen = ref(false);
  const lastCheckTime = ref(null);

  // 初始化全局原生进度回调监听
  if (typeof window !== 'undefined') {
    window.onAlpineDownloadProgress = (data) => {
      if (!data) return;
      window.dispatchEvent(new CustomEvent('alpine-download-progress', { detail: data }));
      if (data.status) {
        downloadStatus.value = data.status;
      }
      downloadProgress.value = {
        percent: data.percent || 0,
        receivedBytes: data.receivedBytes || 0,
        totalBytes: data.totalBytes || 0,
        message: data.message || ''
      };
      if (data.status === 'error') {
        errorMessage.value = data.message || '更新下载失败';
      }
    };

    // 监听应用切屏与页面焦点重获：从系统设置授予权限返回时自动继续安装
    const handleRecheckOnResume = () => {
      if (downloadStatus.value === 'permission_required') {
        if (window.AlpineNative?.canRequestPackageInstalls?.()) {
          downloadStatus.value = 'installing';
          downloadProgress.value.message = '已获取安装权限，正在调起系统安装...';
          startDownloadAndInstall();
        }
      }
    };
    document.addEventListener('visibilitychange', () => {
      if (document.visibilityState === 'visible') {
        handleRecheckOnResume();
      }
    });
    window.addEventListener('focus', handleRecheckOnResume);
  }

  /**
   * 检查新版本
   * @param {boolean} silent 是否为静默后台检查（若为 true 且发现新版本，仅打标记不强弹窗）
   */
  async function checkForUpdate(silent = false) {
    if (isChecking.value) return;
    isChecking.value = true;
    errorMessage.value = '';

    try {
      const release = await fetchLatestRelease();
      latestRelease.value = release;
      lastCheckTime.value = new Date().toISOString();

      const cmp = compareVersions(APP_VERSION, release.version);
      if (cmp > 0) {
        // 远端版本高于本地当前版本：存在新版本
        versionDiffStatus.value = 'update_available';
        hasUpdate.value = true;
        if (!silent) {
          isModalOpen.value = true;
        }
      } else if (cmp < 0) {
        // 本地当前版本高于远端稳定发布版：先行内测版/测试机
        versionDiffStatus.value = 'ahead_of_release';
        hasUpdate.value = false;
        if (!silent) {
          isModalOpen.value = true;
        }
      } else {
        // 版本完全一致：当前已是最新发布版
        versionDiffStatus.value = 'up_to_date';
        hasUpdate.value = false;
        if (!silent) {
          isModalOpen.value = true;
        }
      }
    } catch (err) {
      console.warn('[updateStore] 检查更新异常:', err);
      if (!silent) {
        errorMessage.value = err.message || '检查更新失败，请检查网络';
        isModalOpen.value = true;
      }
    } finally {
      isChecking.value = false;
    }
  }

  /**
   * 开始下载并安装 APK
   */
  async function startDownloadAndInstall() {
    if (!latestRelease.value) return;

    downloadStatus.value = 'downloading';
    downloadProgress.value = {
      percent: 0,
      receivedBytes: 0,
      totalBytes: latestRelease.value.assetSize || 0,
      message: '正在连接高速下载节点...'
    };
    errorMessage.value = '';

    const downloadUrl = latestRelease.value.downloadUrl || latestRelease.value.rawDownloadUrl;
    const targetVersion = latestRelease.value.version;

    // 1. Android 原生容器环境：直接调用 Java 原生流式下载与安装
    if (typeof window !== 'undefined' && window.AlpineNative?.downloadAndInstallApk) {
      window.AlpineNative.downloadAndInstallApk(downloadUrl, targetVersion);
      return;
    }

    // 2. Web 浏览器/预览环境回退：调起浏览器下载
    downloadStatus.value = 'idle';
    await openExternalUrl(downloadUrl);
  }

  /**
   * 取消下载任务
   */
  function cancelDownload() {
    if (typeof window !== 'undefined' && window.AlpineNative?.cancelDownload) {
      window.AlpineNative.cancelDownload();
    }
    downloadStatus.value = 'idle';
    downloadProgress.value = { percent: 0, receivedBytes: 0, totalBytes: 0, message: '' };
  }

  /**
   * 打开系统安装未知应用设置
   */
  function openInstallPermissionSettings() {
    if (typeof window !== 'undefined' && window.AlpineNative?.openInstallPermissionSettings) {
      window.AlpineNative.openInstallPermissionSettings();
    }
  }

  function openModal() {
    isModalOpen.value = true;
  }

  function closeModal() {
    if (downloadStatus.value === 'downloading') {
      // 正在下载时关闭仅隐藏弹窗，不中断后台任务
      isModalOpen.value = false;
      return;
    }
    isModalOpen.value = false;
  }

  // 挂载至全局供调试、自动化测试与原生集成
  if (typeof window !== 'undefined') {
    window.AlpineUpdateStore = {
      checkForUpdate,
      startDownloadAndInstall,
      cancelDownload,
      openInstallPermissionSettings,
      openModal,
      closeModal,
      setMockRelease(release, forceStatus = null) {
        latestRelease.value = release;
        if (forceStatus) {
          versionDiffStatus.value = forceStatus;
          hasUpdate.value = forceStatus === 'update_available';
        } else {
          const cmp = compareVersions(APP_VERSION, release?.version || '0.0.1.000');
          if (cmp > 0) {
            versionDiffStatus.value = 'update_available';
            hasUpdate.value = true;
          } else if (cmp < 0) {
            versionDiffStatus.value = 'ahead_of_release';
            hasUpdate.value = false;
          } else {
            versionDiffStatus.value = 'up_to_date';
            hasUpdate.value = false;
          }
        }
        downloadStatus.value = 'idle';
        errorMessage.value = '';
        isModalOpen.value = true;
      }
    };
  }

  return {
    isChecking,
    hasUpdate,
    versionDiffStatus,
    latestRelease,
    downloadStatus,
    downloadProgress,
    errorMessage,
    isModalOpen,
    lastCheckTime,
    checkForUpdate,
    startDownloadAndInstall,
    cancelDownload,
    openInstallPermissionSettings,
    openModal,
    closeModal
  };
});
