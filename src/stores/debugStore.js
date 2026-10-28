import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { APP_VERSION, BUILD_CODE, DEFAULT_CPOLAR_TUNNEL } from '@/config/version.js';
import { openExternalUrl } from '@/utils/appLauncher.js';

function getInitialTunnelUrl() {
  if (typeof window === 'undefined') return DEFAULT_CPOLAR_TUNNEL;
  let saved = localStorage.getItem('wm_debug_tunnel_url');
  if (saved && saved.startsWith('http://') && saved.includes('cpolar.top')) {
    saved = saved.replace('http://', 'https://');
    localStorage.setItem('wm_debug_tunnel_url', saved);
  }
  return saved || DEFAULT_CPOLAR_TUNNEL;
}

export const useDebugStore = defineStore('debug', () => {
  // 穿透服务基地址 (支持用户在调试面板中动态修改或重置)
  const tunnelUrl = ref(getInitialTunnelUrl());

  // 浮动反馈胶囊显示开关 (默认在调试与内测版中开启，但允许用户一键关闭以防遮挡)
  const isCapsuleVisible = ref(
    typeof window !== 'undefined'
      ? localStorage.getItem('wm_debug_capsule_visible') !== 'false'
      : true
  );

  // 实时穿透热重载模式状态 (Live Tunnel / HMR)
  const isLiveTunnelMode = ref(
    typeof window !== 'undefined' &&
      window.location.href.includes('cpolar.top')
  );

  // 更新检测状态
  const isCheckingUpdate = ref(false);
  const updateInfo = ref(null);
  const updateError = ref('');
  const lastCheckTime = ref('');

  // 穿透连通性状态
  const tunnelStatus = ref({
    checking: false,
    healthy: null, // true | false | null
    latencyMs: 0,
    msg: ''
  });

  /**
   * 判断当前运行环境是否为 Capacitor 原生 Android 容器
   */
  const isCapacitorNative = computed(() => {
    if (typeof window === 'undefined') return false;
    if (window.Capacitor && window.Capacitor.isNativePlatform()) return true;
    return (
      window.location.protocol === 'capacitor:' ||
      (window.location.hostname === 'localhost' && window.location.port !== '5173')
    );
  });

  /**
   * 获取针对当前运行环境的 API 请求基准前缀
   * - 若在 Android 原生离线包环境运行，必须走 cpolar 穿透地址；
   * - 若在开发机浏览器 (localhost:5173) 运行，可直接走相对路径 '' 或穿透地址。
   */
  const apiBase = computed(() => {
    if (isCapacitorNative.value) {
      return tunnelUrl.value.replace(/\/+$/, '');
    }
    // Web 环境：若当前就是穿透域名，直接相对路径；若其他则优先相对路径
    return '';
  });

  /**
   * 保存穿透地址
   */
  function setTunnelUrl(url) {
    let cleanUrl = (url || '').trim().replace(/\/+$/, '');
    if (cleanUrl.startsWith('http://') && cleanUrl.includes('cpolar.top')) {
      cleanUrl = cleanUrl.replace('http://', 'https://');
    }
    tunnelUrl.value = cleanUrl || DEFAULT_CPOLAR_TUNNEL;
    if (typeof window !== 'undefined') {
      localStorage.setItem('wm_debug_tunnel_url', tunnelUrl.value);
    }
  }

  /**
   * 切换浮动反馈胶囊显示
   */
  function toggleCapsuleVisibility(val) {
    isCapsuleVisible.value = typeof val === 'boolean' ? val : !isCapsuleVisible.value;
    if (typeof window !== 'undefined') {
      localStorage.setItem('wm_debug_capsule_visible', String(isCapsuleVisible.value));
    }
  }

  /**
   * 测试穿透服务连通性
   */
  async function testTunnelHealth() {
    tunnelStatus.value.checking = true;
    tunnelStatus.value.msg = '正在探测穿透服务器响应...';
    const startTime = Date.now();
    try {
      const target = `${tunnelUrl.value.replace(/\/+$/, '')}/api/app-update?t=${Date.now()}`;
      const res = await fetch(target, { method: 'GET', cache: 'no-cache' });
      const latency = Date.now() - startTime;
      if (res.ok) {
        tunnelStatus.value.healthy = true;
        tunnelStatus.value.latencyMs = latency;
        tunnelStatus.value.msg = `连通正常 (${latency}ms)`;
        return true;
      } else {
        tunnelStatus.value.healthy = false;
        tunnelStatus.value.latencyMs = latency;
        tunnelStatus.value.msg = `HTTP 错误: ${res.status}`;
        return false;
      }
    } catch (err) {
      tunnelStatus.value.healthy = false;
      tunnelStatus.value.latencyMs = Date.now() - startTime;
      tunnelStatus.value.msg = `无法连接: ${err.message || '网络超时或穿透已断开'}`;
      return false;
    } finally {
      tunnelStatus.value.checking = false;
    }
  }

  /**
   * 检查在线版本更新
   */
  async function checkUpdate() {
    isCheckingUpdate.value = true;
    updateError.value = '';
    try {
      const target = `${tunnelUrl.value.replace(/\/+$/, '')}/api/app-update?t=${Date.now()}`;
      const res = await fetch(target, { method: 'GET', cache: 'no-cache' });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      if (data && data.success) {
        updateInfo.value = data;
        lastCheckTime.value = new Date().toLocaleTimeString('zh-CN', { hour12: false });
        return data;
      } else {
        throw new Error(data?.message || '获取更新信息失败');
      }
    } catch (err) {
      console.warn('检查更新失败:', err);
      updateError.value = `检查更新失败 (${err.message})，请确认穿透服务是否正常。`;
      return null;
    } finally {
      isCheckingUpdate.value = false;
    }
  }

  // 流式下载与安装状态管理
  const downloadStatus = ref('idle'); // 'idle' | 'downloading' | 'installing' | 'completed' | 'cancelled' | 'error'
  const downloadProgress = ref({
    percent: 0,
    receivedBytes: 0,
    totalBytes: 0,
    speed: '',
    message: ''
  });

  // 监听来自 Android 原生 AlpineNative 的下载进度事件
  if (typeof window !== 'undefined') {
    window.addEventListener('alpine-download-progress', (e) => {
      const data = e.detail;
      if (!data) return;
      if (data.status) {
        downloadStatus.value = data.status;
      }
      downloadProgress.value = {
        percent: data.percent || 0,
        receivedBytes: data.receivedBytes || 0,
        totalBytes: data.totalBytes || 0,
        speed: data.message || '',
        message: data.message || ''
      };
      if (data.status === 'completed' || data.status === 'cancelled' || data.status === 'error') {
        setTimeout(() => {
          if (downloadStatus.value === data.status) {
            downloadStatus.value = 'idle';
          }
        }, 3000);
      }
    });
  }

  /**
   * 取消当前正在进行的 APK 下载
   */
  function cancelDownloadApk() {
    if (typeof window !== 'undefined' && window.AlpineNative?.cancelDownload) {
      window.AlpineNative.cancelDownload();
    }
    downloadStatus.value = 'idle';
  }

  /**
   * 一键在线下载并安装最新 APK
   */
  async function downloadAndInstallApk() {
    const url = updateInfo.value?.downloadUrl || `${tunnelUrl.value.replace(/\/+$/, '')}/releases/weekly-mountain-latest-debug.apk`;
    if (typeof window !== 'undefined' && window.AlpineNative?.downloadAndInstallApk) {
      downloadStatus.value = 'downloading';
      downloadProgress.value = {
        percent: 0,
        receivedBytes: 0,
        totalBytes: 0,
        speed: '0 KB/s',
        message: '准备下载...'
      };
      window.AlpineNative.downloadAndInstallApk(url, updateInfo.value?.latestVersion || 'latest');
      return;
    }
    return await openExternalUrl(url);
  }

  /**
   * 切换实时穿透热重载模式 (Live Tunnel Mode)
   * 允许在手机 App 内直接加载电脑的 Vite 热重载服务，电脑改代码手机秒级同步！
   */
  function switchLiveTunnelMode(enable) {
    if (typeof window === 'undefined') return;
    if (enable) {
      const target = tunnelUrl.value.replace(/\/+$/, '');
      if (confirm(`即将切换到实时穿透热重载模式：\n${target}\n\n开启后，电脑端代码保存手机将实时生效。是否立即重载？`)) {
        window.location.href = target;
      }
    } else {
      if (confirm('即将切回本地内置离线包运行模式。是否立即重载？')) {
        window.location.href = 'http://localhost';
      }
    }
  }

  return {
    tunnelUrl,
    isCapsuleVisible,
    isLiveTunnelMode,
    isCheckingUpdate,
    updateInfo,
    updateError,
    lastCheckTime,
    tunnelStatus,
    isCapacitorNative,
    apiBase,
    setTunnelUrl,
    toggleCapsuleVisibility,
    testTunnelHealth,
    checkUpdate,
    downloadStatus,
    downloadProgress,
    downloadAndInstallApk,
    cancelDownloadApk,
    switchLiveTunnelMode
  };
});
