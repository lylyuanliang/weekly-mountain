/**
 * 手机原生 App 唤起与户外导航工具库 (App Launcher)
 * 支持唤起高德地图、百度地图、腾讯地图、Apple 地图、两步路 (2bulu)、六只脚 (Foottouch)
 * 完美适配 Capacitor Android 原生环境与移动端 Web
 */
import { Capacitor } from '@capacitor/core';
import { AppLauncher } from '@capacitor/app-launcher';

export function isIos() {
  if (typeof navigator === 'undefined') return false;
  return /(iPhone|iPad|iPod|Macintosh)/i.test(navigator.userAgent);
}

export function isAndroid() {
  if (typeof navigator === 'undefined') return false;
  return /Android/i.test(navigator.userAgent);
}

export function isWeChat() {
  if (typeof navigator === 'undefined') return false;
  return /MicroMessenger/i.test(navigator.userAgent);
}

/**
 * 安全复制文本到剪贴板（兼容新旧浏览器与 HTTP 环境）
 */
export async function copyToClipboard(text) {
  if (!text) return false;
  try {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      await navigator.clipboard.writeText(text);
      return true;
    }
  } catch (err) {
    // fallback below
  }

  try {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'fixed';
    textArea.style.left = '-9999px';
    textArea.style.top = '-9999px';
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    const success = document.execCommand('copy');
    document.body.removeChild(textArea);
    return success;
  } catch (err) {
    return false;
  }
}

/**
 * 清洗 GPX 轨迹搜索词，剔除无用前缀与标点
 */
export function cleanTrackKeyword(raw) {
  if (!raw) return '';
  return raw
    .replace(/^两步路\/?六只脚(搜索|已知轨迹)?\s*[:：]\s*/i, '')
    .replace(/^六只脚\/?两步路(搜索|已知轨迹)?\s*[:：]\s*/i, '')
    .replace(/^两步路(搜索|已知轨迹)?\s*[:：]\s*/i, '')
    .replace(/^六只脚(搜索|已知轨迹)?\s*[:：]\s*/i, '')
    .trim();
}

/**
 * 尝试通过 Deep Link 唤起第三方 App
 * 1. 在 Capacitor 原生容器内：通过 AppLauncher 插件唤起 Intent，杜绝 WebView 导航黑屏
 * 2. 在移动端浏览器中：通过隐藏 iframe 触发，杜绝顶层页面被篡改
 */
export async function tryDeepLink(schemeUrl, fallbackUrl = null) {
  const isNative = Capacitor && typeof Capacitor.isNativePlatform === 'function' && Capacitor.isNativePlatform();

  if (isNative) {
    try {
      // 优先尝试直接用原生 Intent 调起应用
      const result = await AppLauncher.openUrl({ url: schemeUrl });
      if (result && result.completed !== false) {
        return { success: true, method: 'app-launcher' };
      }
    } catch (err) {
      console.warn('[AppLauncher] openUrl failed, checking fallback:', err);
    }

    // 若未安装或调起失败，使用外部浏览器打开 fallback
    if (fallbackUrl) {
      try {
        await AppLauncher.openUrl({ url: fallbackUrl });
        return { success: true, method: 'browser-fallback' };
      } catch (err) {
        window.open(fallbackUrl, '_blank');
        return { success: true, method: 'window-open' };
      }
    }
    return { success: false, reason: 'app-not-installed' };
  }

  // Web 浏览器环境：利用隐藏 iframe 安全拉起 scheme
  try {
    const iframe = document.createElement('iframe');
    iframe.style.display = 'none';
    iframe.src = schemeUrl;
    document.body.appendChild(iframe);
    setTimeout(() => {
      if (iframe.parentNode) {
        document.body.removeChild(iframe);
      }
    }, 1500);
  } catch (e) {
    // ignore
  }

  if (fallbackUrl) {
    const start = Date.now();
    setTimeout(() => {
      if (document.hidden || Date.now() - start > 3000) {
        return;
      }
      window.open(fallbackUrl, '_blank');
    }, 2000);
  }

  return { success: true, method: 'web-iframe' };
}

// ==========================================
// 户外轨迹 App 唤起 (两步路 & 六只脚)
// ==========================================

/**
 * 唤起两步路户外助手 App
 */
export async function launchTwoBulu(keyword) {
  const cleanKw = cleanTrackKeyword(keyword);
  await copyToClipboard(cleanKw);

  const encoded = encodeURIComponent(cleanKw);
  const scheme = `twostep://search?keyword=${encoded}`;
  const webFallback = `https://www.2bulu.com/track/track_search.htm?keyword=${encoded}`;

  await tryDeepLink(scheme, webFallback);

  return {
    app: '两步路 (2bulu)',
    keyword: cleanKw,
    scheme,
    webFallback
  };
}

/**
 * 唤起六只脚户外 App
 */
export async function launchFootTouch(keyword) {
  const cleanKw = cleanTrackKeyword(keyword);
  await copyToClipboard(cleanKw);

  const encoded = encodeURIComponent(cleanKw);
  const scheme = `foottouch://search?keyword=${encoded}`;
  const webFallback = `https://www.foottouch.com/`;

  await tryDeepLink(scheme, webFallback);

  return {
    app: '六只脚 (Foottouch)',
    keyword: cleanKw,
    scheme,
    webFallback
  };
}

// ==========================================
// 手机导航地图 App 唤起 (高德/百度/腾讯/Apple)
// ==========================================

export const NAVIGATION_APPS = [
  {
    id: 'amap',
    name: '高德地图',
    badge: '推荐',
    color: '#0091ff',
    icon: 'navigation',
    desc: '山路路况精准 · 户外自驾首选',
    launch: async (dest) => {
      const scheme = `amapuri://route/plan/?dlat=${dest.lat}&dlon=${dest.lng}&dname=${encodeURIComponent(dest.name)}&dev=0&t=0`;
      const web = `https://uri.amap.com/navigation?to=${dest.lng},${dest.lat},${encodeURIComponent(dest.name)}&mode=car&policy=1&src=weeklymountain&coordinate=gaode&callnative=1`;
      return await tryDeepLink(scheme, web);
    }
  },
  {
    id: 'baidu',
    name: '百度地图',
    badge: '常用',
    color: '#3385ff',
    icon: 'explore',
    desc: '全景卫星视图 · 路线规划详尽',
    launch: async (dest) => {
      const scheme = `baidumap://map/direction?destination=latlng:${dest.lat},${dest.lng}|name:${encodeURIComponent(dest.name)}&mode=driving&coord_type=wgs84`;
      const web = `https://api.map.baidu.com/direction?destination=latlng:${dest.lat},${dest.lng}|name:${encodeURIComponent(dest.name)}&mode=driving&output=html&src=weeklymountain`;
      return await tryDeepLink(scheme, web);
    }
  },
  {
    id: 'tencent',
    name: '腾讯地图',
    badge: '微信同源',
    color: '#10b981',
    icon: 'near_me',
    desc: '微信位置直达 · 绿道指引清晰',
    launch: async (dest) => {
      const scheme = `qqmap://map/routeplan?type=drive&to=${encodeURIComponent(dest.name)}&tocoord=${dest.lat},${dest.lng}`;
      const web = `https://apis.map.qq.com/uri/v1/routeplan?type=drive&to=${encodeURIComponent(dest.name)}&tocoord=${dest.lat},${dest.lng}&policy=1`;
      return await tryDeepLink(scheme, web);
    }
  },
  {
    id: 'apple',
    name: 'Apple 地图',
    badge: 'iOS 原生',
    color: '#94a3b8',
    icon: 'map',
    desc: 'iPhone / iPad 原生平滑导航',
    showOnlyIos: true,
    launch: async (dest) => {
      const scheme = `maps://?daddr=${dest.lat},${dest.lng}&q=${encodeURIComponent(dest.name)}`;
      return await tryDeepLink(scheme, null);
    }
  },
  {
    id: 'web',
    name: '网页版高德直接导航',
    badge: '免装 App',
    color: '#4edea3',
    icon: 'public',
    desc: '无需安装应用，浏览器内直接路线规划',
    launch: async (dest) => {
      const web = `https://uri.amap.com/navigation?to=${dest.lng},${dest.lat},${encodeURIComponent(dest.name)}&mode=car&policy=1&src=weeklymountain&coordinate=gaode&callnative=1`;
      window.open(web, '_blank');
      return { success: true, method: 'web-direct' };
    }
  }
];

export async function launchNavigation(appId, dest) {
  const app = NAVIGATION_APPS.find((a) => a.id === appId);
  if (app) {
    return await app.launch(dest);
  }
}

/**
 * 唤起外部浏览器或系统下载器打开指定 URL (用于 APK 在线更新下载与外链访问)
 */
export async function openExternalUrl(url) {
  if (!url) return false;
  if (Capacitor.isNativePlatform()) {
    try {
      await AppLauncher.openUrl({ url });
      return true;
    } catch (err) {
      console.warn('AppLauncher.openUrl failed, falling back to window.open:', err);
    }
  }
  try {
    const a = document.createElement('a');
    a.href = url;
    a.target = '_blank';
    a.download = '';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    return true;
  } catch {
    window.open(url, '_blank');
    return true;
  }
}
