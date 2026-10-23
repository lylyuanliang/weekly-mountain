/**
 * 手机原生 App 唤起与户外导航工具库 (App Launcher)
 * 支持唤起高德地图、百度地图、腾讯地图、Apple 地图、两步路 (2bulu)、六只脚 (Foottouch)
 */

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
 */
function tryDeepLink(schemeUrl, fallbackUrl = null) {
  const start = Date.now();

  // 对于大部分现代移动浏览器，直接变更 location.href 即可唤起对应已安装应用
  window.location.href = schemeUrl;

  // 如果提供了 fallback 且 2.5 秒内页面未失焦/未挂起（说明手机未安装该 App），则降级打开 fallbackUrl
  if (fallbackUrl) {
    setTimeout(() => {
      // 若页面仍在前台且时间差在合理范围内，提示或跳转
      if (document.hidden || Date.now() - start > 3000) {
        return;
      }
      window.open(fallbackUrl, '_blank');
    }, 2000);
  }
}

// ==========================================
// 户外轨迹 App 唤起 (两步路 & 六只脚)
// ==========================================

/**
 * 唤起两步路户外助手 App
 * 1. 自动写入剪贴板
 * 2. 尝试打开 twostep://
 * 3. 失败时降级到两步路网页端搜索
 */
export async function launchTwoBulu(keyword) {
  const cleanKw = cleanTrackKeyword(keyword);
  await copyToClipboard(cleanKw);

  const encoded = encodeURIComponent(cleanKw);
  // 两步路 URL Scheme 规范
  const scheme = `twostep://search?keyword=${encoded}`;
  const webFallback = `https://www.2bulu.com/track/track_search.htm?keyword=${encoded}`;

  tryDeepLink(scheme, webFallback);

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

  tryDeepLink(scheme, webFallback);

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
    launch: (dest) => {
      const scheme = `amapuri://route/plan/?dlat=${dest.lat}&dlon=${dest.lng}&dname=${encodeURIComponent(dest.name)}&dev=0&t=0`;
      const web = `https://uri.amap.com/navigation?to=${dest.lng},${dest.lat},${encodeURIComponent(dest.name)}&mode=car&policy=1&src=weeklymountain&coordinate=gaode&callnative=1`;
      tryDeepLink(scheme, web);
    }
  },
  {
    id: 'baidu',
    name: '百度地图',
    badge: '常用',
    color: '#3385ff',
    icon: 'explore',
    desc: '全景卫星视图 · 路线规划详尽',
    launch: (dest) => {
      const scheme = `baidumap://map/direction?destination=latlng:${dest.lat},${dest.lng}|name:${encodeURIComponent(dest.name)}&mode=driving&coord_type=wgs84`;
      const web = `https://api.map.baidu.com/direction?destination=latlng:${dest.lat},${dest.lng}|name:${encodeURIComponent(dest.name)}&mode=driving&output=html&src=weeklymountain`;
      tryDeepLink(scheme, web);
    }
  },
  {
    id: 'tencent',
    name: '腾讯地图',
    badge: '微信同源',
    color: '#10b981',
    icon: 'near_me',
    desc: '微信位置直达 · 绿道指引清晰',
    launch: (dest) => {
      const scheme = `qqmap://map/routeplan?type=drive&to=${encodeURIComponent(dest.name)}&tocoord=${dest.lat},${dest.lng}`;
      const web = `https://apis.map.qq.com/uri/v1/routeplan?type=drive&to=${encodeURIComponent(dest.name)}&tocoord=${dest.lat},${dest.lng}&policy=1`;
      tryDeepLink(scheme, web);
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
    launch: (dest) => {
      const scheme = `maps://?daddr=${dest.lat},${dest.lng}&q=${encodeURIComponent(dest.name)}`;
      tryDeepLink(scheme, null);
    }
  },
  {
    id: 'web',
    name: '网页版高德直接导航',
    badge: '免装 App',
    color: '#4edea3',
    icon: 'public',
    desc: '无需安装应用，浏览器内直接路线规划',
    launch: (dest) => {
      const web = `https://uri.amap.com/navigation?to=${dest.lng},${dest.lat},${encodeURIComponent(dest.name)}&mode=car&policy=1&src=weeklymountain&coordinate=gaode&callnative=1`;
      window.open(web, '_blank');
    }
  }
];

export function launchNavigation(appId, dest) {
  const app = NAVIGATION_APPS.find((a) => a.id === appId);
  if (app) {
    app.launch(dest);
  }
}
