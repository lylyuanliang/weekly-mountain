import { IS_DEBUG_BUILD } from '@/config/version.js';

/**
 * 在线更新服务 (Update Service)
 * 基于 GitHub Releases、jsDelivr CDN 与国内高可用加速镜像
 * 彻底杜绝 GitHub API 60次/小时 IP 限流与 CORS 问题
 */

const GITHUB_REPO = 'lylyuanliang/weekly-mountain';
const JSDELIVR_ENDPOINT = `https://cdn.jsdelivr.net/gh/${GITHUB_REPO}@main/public/version.json`;
const PROXY_RAW_ENDPOINT = `https://ghfast.top/https://raw.githubusercontent.com/${GITHUB_REPO}/main/public/version.json`;
const PACKAGE_JSON_ENDPOINT = `https://cdn.jsdelivr.net/gh/${GITHUB_REPO}@main/package.json`;
const ACCELERATOR_PREFIX = 'https://ghfast.top/';

/**
 * 语义化版本号对比
 * 支持 3 位 (0.0.1) 与 4 位 (0.0.1.005) 比较
 * @param {string} current 当前版本
 * @param {string} latest 线上最新版本
 * @returns {number} 1: 有更新; 0: 同版本; -1: 当前版本较新
 */
export function compareVersions(current, latest) {
  if (!current || !latest) return 0;

  const clean = (v) => v.replace(/^v/i, '').trim();
  const cParts = clean(current).split('.').map((n) => parseInt(n, 10) || 0);
  const lParts = clean(latest).split('.').map((n) => parseInt(n, 10) || 0);

  const maxLen = Math.max(cParts.length, lParts.length);
  for (let i = 0; i < maxLen; i++) {
    const cVal = cParts[i] || 0;
    const lVal = lParts[i] || 0;
    if (lVal > cVal) return 1;
    if (lVal < cVal) return -1;
  }
  return 0;
}

/**
 * 字节数转可读文本 (如 27.72 MB)
 */
export function formatBytes(bytes) {
  if (!bytes || bytes <= 0) return '0 B';
  const units = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(1024));
  return `${(bytes / Math.pow(1024, i)).toFixed(i === 0 ? 0 : 2)} ${units[i]}`;
}

/**
 * 获取最新版本元数据 (多通道高可用竞速)
 */
export async function fetchLatestRelease() {
  const timestamp = Date.now();
  const savedTunnel = typeof window !== 'undefined' && window.localStorage ? window.localStorage.getItem('wm_debug_tunnel_url') : '';
  const tunnelVersionUrl = savedTunnel ? `${savedTunnel.replace(/\/+$/, '')}/version.json?t=${timestamp}` : null;

  const candidateUrls = [
    // 0. 穿透联调高速通道 (若已配置 cpolar/局域网，优先获取本机热打包版本)
    tunnelVersionUrl,
    // 1. jsDelivr 全球加速 CDN (CORS 友好，无 Rate-limit，保证获取真实远端发布版本)
    `${JSDELIVR_ENDPOINT}?t=${timestamp}`,
    // 2. 国内代理镜像
    `${PROXY_RAW_ENDPOINT}?t=${timestamp}`,
    // 3. jsDelivr package.json 兜底
    `${PACKAGE_JSON_ENDPOINT}?t=${timestamp}`,
    // 4. 本地/同源静态路径（开发与测试环境离线兜底）
    typeof window !== 'undefined' ? `/version.json?t=${timestamp}` : null
  ].filter(Boolean);

  let releaseData = null;

  for (const url of candidateUrls) {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 3500);
      const res = await fetch(url, { signal: controller.signal });
      clearTimeout(timeoutId);

      if (res.ok) {
        const json = await res.json();
        if (json && (json.version || json.versionTag)) {
          releaseData = json;
          break;
        }
      }
    } catch (e) {
      // 继续下一个通道
    }
  }

  if (!releaseData || (!releaseData.version && !releaseData.versionTag)) {
    throw new Error('网络连接超时或无法解析最新版本信息');
  }

  const ver = releaseData.version || releaseData.versionTag.replace(/^v/i, '');
  const verTag = releaseData.versionTag || `v${ver}`;

  // 根据当前运行环境变体 (Debug 调试版 vs Release 纯净版) 自动匹配对应的 APK 下载源
  let rawDownloadUrl = releaseData.downloadUrl || '';
  let assetName = releaseData.assetName || '';

  if (IS_DEBUG_BUILD) {
    if (releaseData.debugDownloadUrl) {
      rawDownloadUrl = releaseData.debugDownloadUrl;
    } else if (rawDownloadUrl && rawDownloadUrl.includes('-release.apk')) {
      rawDownloadUrl = rawDownloadUrl.replace('-release.apk', '-debug.apk');
    } else if (!rawDownloadUrl) {
      rawDownloadUrl = `https://github.com/${GITHUB_REPO}/releases/download/${verTag}/weekly-mountain-${verTag}-debug.apk`;
    }
    if (assetName && assetName.includes('-release.apk')) {
      assetName = assetName.replace('-release.apk', '-debug.apk');
    } else if (!assetName) {
      assetName = `weekly-mountain-${verTag}-debug.apk`;
    }
  } else {
    if (releaseData.releaseDownloadUrl) {
      rawDownloadUrl = releaseData.releaseDownloadUrl;
    } else if (!rawDownloadUrl) {
      rawDownloadUrl = `https://github.com/${GITHUB_REPO}/releases/download/${verTag}/weekly-mountain-${verTag}-release.apk`;
    }
    if (!assetName) {
      assetName = `weekly-mountain-${verTag}-release.apk`;
    }
  }

  // 拼装国内高速代理加速地址
  const acceleratedUrl = rawDownloadUrl.startsWith('http')
    ? `${ACCELERATOR_PREFIX}${rawDownloadUrl}`
    : rawDownloadUrl;

  return {
    version: ver,
    versionTag: verTag,
    title: releaseData.title || `每周一山 ${verTag}`,
    changelog: releaseData.changelog || '常规功能优化与性能稳定性提升。',
    publishedAt: releaseData.publishedAt || new Date().toLocaleDateString('zh-CN'),
    assetName: assetName,
    assetSizeText: releaseData.assetSizeText || '约 29 MB',
    downloadUrl: acceleratedUrl,
    rawDownloadUrl: rawDownloadUrl,
    htmlUrl: `https://github.com/${GITHUB_REPO}/releases/tag/${verTag}`
  };
}
