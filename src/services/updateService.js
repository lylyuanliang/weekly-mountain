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
 * 尝试从远端下载并解析 SHA256SUMS.txt (校验降级兜底通道)
 * @param {string} verTag 版本 Tag，如 v0.3.0.202611061139
 * @returns {Promise<Record<string, string> | null>}
 */
export async function fetchSha256Sums(verTag) {
  if (!verTag) return null;
  const urls = [
    `${ACCELERATOR_PREFIX}https://github.com/${GITHUB_REPO}/releases/download/${verTag}/SHA256SUMS.txt`,
    `https://github.com/${GITHUB_REPO}/releases/download/${verTag}/SHA256SUMS.txt`
  ];

  for (const url of urls) {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 3000);
      const res = await fetch(url, { signal: controller.signal });
      clearTimeout(timeoutId);
      if (res.ok) {
        const text = await res.text();
        const map = {};
        for (const line of text.split(/\r?\n/)) {
          const trimmed = line.trim();
          if (!trimmed || trimmed.startsWith('#')) continue;
          const parts = trimmed.split(/\s+/);
          if (parts.length >= 2) {
            const hash = parts[0].toLowerCase();
            const filename = parts[1].replace(/^\*/, '');
            map[filename] = hash;
            if (filename.includes('release')) {
              map.release = hash;
            } else if (filename.includes('debug')) {
              map.debug = hash;
            }
          }
        }
        return map;
      }
    } catch (_) {
      // 容错降级
    }
  }
  return null;
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
    // 1. 国内代理镜像 (实时直连 GitHub Raw，无 CDN 边缘缓存延迟)
    `${PROXY_RAW_ENDPOINT}?t=${timestamp}`,
    // 2. 官方 GitHub Raw 直连 (无边缘强缓存)
    `https://raw.githubusercontent.com/${GITHUB_REPO}/main/public/version.json?t=${timestamp}`,
    // 3. jsDelivr 全球加速 CDN (若有缓存则兜底)
    `${JSDELIVR_ENDPOINT}?t=${timestamp}`,
    // 4. jsDelivr package.json 兜底
    `${PACKAGE_JSON_ENDPOINT}?t=${timestamp}`,
    // 5. 本地/同源静态路径（开发与测试环境离线兜底）
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
          // 若初次获取，或当前通道版本比已缓存版本更新，则采纳
          if (!releaseData || compareVersions(releaseData.version || releaseData.versionTag, json.version || json.versionTag) > 0) {
            releaseData = json;
          }
          // 优先通道（穿透直连或 GitHub raw 实时通道）直接命中退出，防范慢速降级
          if (url === tunnelVersionUrl || url.includes('ghfast.top') || url.includes('raw.githubusercontent.com')) {
            break;
          }
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

  // 分别解析并预置「正式发布版」与「内测调试版」双下载通道 (均走 GitHub Releases)
  const rawReleaseUrl = releaseData.releaseDownloadUrl || `https://github.com/${GITHUB_REPO}/releases/download/${verTag}/weekly-mountain-${verTag}-release.apk`;
  const rawDebugUrl = releaseData.debugDownloadUrl || `https://github.com/${GITHUB_REPO}/releases/download/${verTag}/weekly-mountain-${verTag}-debug.apk`;

  const acceleratedReleaseUrl = rawReleaseUrl.startsWith('http') ? `${ACCELERATOR_PREFIX}${rawReleaseUrl}` : rawReleaseUrl;
  const acceleratedDebugUrl = rawDebugUrl.startsWith('http') ? `${ACCELERATOR_PREFIX}${rawDebugUrl}` : rawDebugUrl;

  // 根据当前运行环境默认优选下载源
  let rawDownloadUrl = IS_DEBUG_BUILD ? rawDebugUrl : rawReleaseUrl;
  let acceleratedUrl = IS_DEBUG_BUILD ? acceleratedDebugUrl : acceleratedReleaseUrl;
  let assetName = IS_DEBUG_BUILD ? `weekly-mountain-${verTag}-debug.apk` : `weekly-mountain-${verTag}-release.apk`;

  // 解析并对齐 SHA-256 安全散列值 (小写 64 位十六进制)
  let releaseSha256 = (releaseData.releaseSha256 || '').trim().toLowerCase();
  let debugSha256 = (releaseData.debugSha256 || '').trim().toLowerCase();

  // 若 version.json 尚未内嵌 SHA-256，尝试拉取 Release 附件 SHA256SUMS.txt 进行自动补齐
  if (!releaseSha256 && !debugSha256) {
    try {
      const shaMap = await fetchSha256Sums(verTag);
      if (shaMap) {
        releaseSha256 = shaMap.release || shaMap[`weekly-mountain-${verTag}-release.apk`] || '';
        debugSha256 = shaMap.debug || shaMap[`weekly-mountain-${verTag}-debug.apk`] || '';
      }
    } catch (_) {
      // 容错降级
    }
  }

  const activeSha256 = IS_DEBUG_BUILD ? debugSha256 : releaseSha256;

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
    releaseDownloadUrl: acceleratedReleaseUrl,
    debugDownloadUrl: acceleratedDebugUrl,
    rawReleaseDownloadUrl: rawReleaseUrl,
    rawDebugDownloadUrl: rawDebugUrl,
    releaseSha256: releaseSha256,
    debugSha256: debugSha256,
    sha256: activeSha256,
    htmlUrl: `https://github.com/${GITHUB_REPO}/releases/tag/${verTag}`
  };
}
