/**
 * src/services/resourcePackService.js
 * 客户端地域资源包动态生命周期管理器 (ResourcePackService)
 *
 * 核心架构特性：
 * 1. 环境自适应感知：
 *    - Web 浏览器端：全量在线动态导入（Dynamic Import），所有已收录地域默认 100% 可用、零下载摩擦；
 *    - 原生移动端 (Capacitor Android/iOS)：精准识别内置默认地域（如 chengdu 内置在本地资产中），
 *      对动态扩展地域（如 chongqing）按需从加速镜像通道下载、校验 SHA-256、解压至 Capacitor 本地存储。
 * 2. 容错与优雅降级：
 *    - 若读取指定地域离线包遇到文件损坏或缺失，优雅回退至默认内置成都数据，严禁导致 App 崩溃或白屏。
 * 3. 存储统计与空间释放：
 *    - 实时统计各地域磁盘占用大小，支持安全卸载动态地域并回收存储空间。
 */

import { Filesystem, Directory, Encoding } from '@capacitor/filesystem';
import { Capacitor } from '@capacitor/core';
import JSZip from 'jszip';
import regionsData from '../data/regions.json' with { type: 'json' };
import { isNativeApp } from '../utils/platform.js';

// 静态 Web 全量按地域打包映射
const WEB_STATIC_BUNDLES = {
  chengdu: () => import('../data/regions/chengdu/mountains.json', { with: { type: 'json' } }),
  chongqing: () => import('../data/regions/chongqing/mountains.json', { with: { type: 'json' } })
};

const PACK_STORAGE_PREFIX = 'weekly_mountain_pack_';
const PACK_STORAGE_META_PREFIX = 'weekly_mountain_pack_meta_';
const PACK_GALLERY_STORAGE_PREFIX = 'weekly_mountain_pack_gallery_';
const PACKS_DIR = 'packs';
const GITHUB_REPO = 'lylyuanliang/weekly-mountain';
const ACCELERATOR_PREFIX = 'https://ghfast.top/';

/**
 * 计算 ArrayBuffer 的 SHA-256 散列值
 * @param {ArrayBuffer} arrayBuffer
 * @returns {Promise<string>} 64 位小写十六进制字符串
 */
export async function computeSha256(arrayBuffer) {
  const subtle = globalThis?.crypto?.subtle || (typeof window !== 'undefined' && window.crypto?.subtle);
  if (subtle?.digest) {
    const hashBuffer = await subtle.digest('SHA-256', arrayBuffer);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    return hashArray.map((b) => b.toString(16).padStart(2, '0')).join('');
  }
  return '';
}

export class ResourcePackService {
  constructor(options = {}) {
    this._filesystem = options.filesystem || Filesystem;
    this._forcedNative = options.isNative !== undefined ? options.isNative : null;
    this._downloadHandlerForTesting = null;
    this._memoryStorage = null;
    this._galleryBaseUris = {};
  }

  /**
   * 判断当前运行形态是否为原生 App
   * @returns {boolean}
   */
  isNativePlatform() {
    if (this._forcedNative !== null) {
      return Boolean(this._forcedNative);
    }
    return isNativeApp();
  }

  /**
   * 测试辅助：手动指定平台形态
   * @param {boolean|null} isNative
   */
  setNativePlatformForTesting(isNative) {
    this._forcedNative = isNative;
  }

  /**
   * 测试辅助：注入模拟下载通道
   * @param {Function|null} handler
   */
  setDownloadHandlerForTesting(handler) {
    this._downloadHandlerForTesting = handler;
  }

  /**
   * 测试辅助：注入文件系统适配器
   * @param {object} adapter
   */
  setFilesystemAdapterForTesting(adapter) {
    this._filesystem = adapter;
  }

  /**
   * 读取持久化存储
   * @private
   */
  _getStorageItem(key) {
    if (typeof window !== 'undefined' && window.localStorage) {
      return window.localStorage.getItem(key);
    }
    if (typeof globalThis !== 'undefined' && globalThis.localStorage) {
      return globalThis.localStorage.getItem(key);
    }
    return this._memoryStorage ? this._memoryStorage.get(key) || null : null;
  }

  /**
   * 写入持久化存储
   * @private
   */
  _setStorageItem(key, val) {
    if (typeof window !== 'undefined' && window.localStorage) {
      window.localStorage.setItem(key, String(val));
      return;
    }
    if (typeof globalThis !== 'undefined' && globalThis.localStorage) {
      globalThis.localStorage.setItem(key, String(val));
      return;
    }
    if (!this._memoryStorage) this._memoryStorage = new Map();
    this._memoryStorage.set(key, String(val));
  }

  /**
   * 移除持久化存储
   * @private
   */
  _removeStorageItem(key) {
    if (typeof window !== 'undefined' && window.localStorage) {
      window.localStorage.removeItem(key);
      return;
    }
    if (typeof globalThis !== 'undefined' && globalThis.localStorage) {
      globalThis.localStorage.removeItem(key);
      return;
    }
    if (this._memoryStorage) {
      this._memoryStorage.delete(key);
    }
  }

  /**
   * 检查指定区域资源包是否就绪可用
   * @param {string} regionId 地域唯一标识
   * @returns {Promise<boolean>}
   */
  async isPackInstalled(regionId) {
    if (!this.isNativePlatform()) {
      // Web 端全量在线可用，只要属于已收录活跃地域即直接判定可用
      const region = regionsData.find((r) => r.id === regionId);
      return Boolean(region && region.status === 'active');
    }

    const region = regionsData.find((r) => r.id === regionId);
    if (!region) return false;

    // 默认内置地域（如成都）随应用直接发布，始终处于就绪状态
    if (region.packInfo?.isDefaultInstalled) {
      return true;
    }

    // 动态下载地域：核验本地存储标记与物理文件完整性
    const isMarked = this._getStorageItem(`${PACK_STORAGE_PREFIX}${regionId}`) === 'true';
    if (!isMarked) return false;

    try {
      const stat = await this._filesystem.stat({
        path: `${PACKS_DIR}/${regionId}/mountains.json`,
        directory: Directory.Data
      });
      return Boolean(stat);
    } catch {
      return false;
    }
  }

  /**
   * 获取当前环境中已安装就绪的全部地域标识列表
   * @returns {Promise<string[]>}
   */
  async getInstalledPacks() {
    if (!this.isNativePlatform()) {
      return regionsData.filter((r) => r.status === 'active').map((r) => r.id);
    }

    const installed = [];
    for (const region of regionsData) {
      if (await this.isPackInstalled(region.id)) {
        installed.push(region.id);
      }
    }
    return installed;
  }

  /**
   * 动态读取并返回指定区域山峰数据数组
   * 若遇到文件损坏、未安装或异常，自动优雅降级回退至默认内置成都数据，严禁引发白屏
   * @param {string} regionId 地域唯一标识
   * @returns {Promise<Array<object>>} 山峰对象列表
   */
  async loadRegionMountains(regionId) {
    // 1. Web 浏览器端：直连静态动态导入
    if (!this.isNativePlatform()) {
      try {
        const loader = WEB_STATIC_BUNDLES[regionId];
        if (loader) {
          const mod = await loader();
          const data = mod.default || mod;
          if (Array.isArray(data) && data.length > 0) {
            return data;
          }
        }
      } catch (err) {
        console.warn(`[ResourcePack] Web 动态载入地域 [${regionId}] 异常，降级回退至默认数据:`, err);
      }
      const defaultMod = await WEB_STATIC_BUNDLES.chengdu();
      return defaultMod.default || defaultMod;
    }

    // 2. 原生 App 端
    const region = regionsData.find((r) => r.id === regionId);

    // 默认内置地域直接加载内置静态资源
    if (region?.packInfo?.isDefaultInstalled) {
      const loader = WEB_STATIC_BUNDLES[regionId] || WEB_STATIC_BUNDLES.chengdu;
      const mod = await loader();
      return mod.default || mod;
    }

    // 动态下载扩展地域：从文件系统中读取
    try {
      const fileRes = await this._filesystem.readFile({
        path: `${PACKS_DIR}/${regionId}/mountains.json`,
        directory: Directory.Data,
        encoding: Encoding.UTF8
      });

      const parsed = JSON.parse(fileRes.data);
      if (Array.isArray(parsed) && parsed.length > 0) {
        return parsed;
      }
      throw new Error(`离线包 mountains.json 格式异常或数据为空`);
    } catch (err) {
      console.warn(`[ResourcePack] 原生读取地域离线包 [${regionId}] 失败，安全降级至默认成都数据集:`, err);
      const fallbackMod = await WEB_STATIC_BUNDLES.chengdu();
      return fallbackMod.default || fallbackMod;
    }
  }

  /**
   * 检查指定区域画册扩展包是否已就绪
   * @param {string} regionId
   * @returns {Promise<boolean>}
   */
  async isGalleryInstalled(regionId) {
    if (!this.isNativePlatform()) {
      return true;
    }
    const region = regionsData.find((r) => r.id === regionId);
    if (!region) return false;
    if (region.packInfo?.isDefaultInstalled) return true;

    const isMarked = this._getStorageItem(`${PACK_GALLERY_STORAGE_PREFIX}${regionId}`) === 'true';
    if (!isMarked) return false;

    try {
      const stat = await this._filesystem.stat({
        path: `${PACKS_DIR}/${regionId}/gallery`,
        directory: Directory.Data
      });
      return Boolean(stat);
    } catch {
      return false;
    }
  }

  /**
   * 初始化/刷新本地画册原生文件 URI 基准映射表
   */
  async refreshGalleryBaseUris() {
    if (!this._galleryBaseUris) {
      this._galleryBaseUris = {};
    }
    if (!this.isNativePlatform() || !this._filesystem?.getUri) {
      return;
    }

    for (const region of regionsData) {
      const regId = region.id;
      if (regId === 'chengdu') continue;
      const isMarked = this._getStorageItem(`${PACK_GALLERY_STORAGE_PREFIX}${regId}`) === 'true';
      if (isMarked) {
        try {
          const res = await this._filesystem.getUri({
            path: `${PACKS_DIR}/${regId}/gallery`,
            directory: Directory.Data
          });
          if (res?.uri) {
            const converted = typeof Capacitor !== 'undefined' && Capacitor.convertFileSrc
              ? Capacitor.convertFileSrc(res.uri)
              : res.uri;
            this._galleryBaseUris[regId] = converted.replace(/\/+$/, '');
          }
        } catch (_) {}
      } else {
        delete this._galleryBaseUris[regId];
      }
    }
  }

  /**
   * 解析山峰图片展示 URL (支持 Native 本地文件转换、Web 静态资源与分层优雅降级)
   * @param {object} mountain 山峰对象
   * @param {string|number} [srcOrIndex=0] 相对路径或画廊序号
   * @returns {string|null} 可用于 <img :src> 的直接 URL，若未安装画册则返回 null 触发优雅降级
   */
  resolveMountainImageUrl(mountain, srcOrIndex = 0) {
    if (!mountain) return null;

    const mid = mountain.id;
    const regionId = mountain.region_id || 'chengdu';

    let rawSrc = '';
    if (typeof srcOrIndex === 'number') {
      if (Array.isArray(mountain.gallery) && mountain.gallery[srcOrIndex]?.src) {
        rawSrc = mountain.gallery[srcOrIndex].src;
      } else {
        rawSrc = `assets/mountains/${mid}${srcOrIndex > 0 ? `-${srcOrIndex + 1}` : ''}.jpg`;
      }
    } else if (typeof srcOrIndex === 'string') {
      rawSrc = srcOrIndex;
    }

    if (!rawSrc) {
      rawSrc = `assets/mountains/${mid}.jpg`;
    }

    const filename = rawSrc.split('/').pop();

    // 默认内置地域 (如成都) 始终可用，直接返回 assets/mountains/ 相对路径
    if (regionId === 'chengdu') {
      return `assets/mountains/${filename}`;
    }

    // 针对扩展地域 (如重庆)：检查画册包是否就绪
    const isReady = this._getStorageItem(`${PACK_GALLERY_STORAGE_PREFIX}${regionId}`) === 'true' || !this.isNativePlatform();
    if (!isReady) {
      return null;
    }

    // 若运行于 Capacitor 原生 App 且已获取到本地物理文件映射
    if (this._galleryBaseUris && this._galleryBaseUris[regionId]) {
      return `${this._galleryBaseUris[regionId]}/${filename}`;
    }

    // 兜底路径 (Web 模式或已编译内置静态资源)
    return `assets/mountains/${filename}`;
  }

  /**
   * 高可用多通道下载通用压缩包并返回 ArrayBuffer
   * @private
   */
  async _downloadZipArrayBuffer(filename, regionId) {
    let arrayBuffer = null;

    if (typeof this._downloadHandlerForTesting === 'function') {
      arrayBuffer = await this._downloadHandlerForTesting(regionId, filename);
      return arrayBuffer;
    }

    let configuredApiBase = '';
    try {
      if (typeof window !== 'undefined' && window.localStorage) {
        configuredApiBase = (window.localStorage.getItem('__agent_feedback_api_base__') || '').trim().replace(/\/+$/, '');
      }
    } catch (_) {}

    const candidateUrls = [
      typeof window !== 'undefined' ? `./dist-packs/${filename}` : null,
      typeof window !== 'undefined' ? `/dist-packs/${filename}` : null,
      configuredApiBase ? `${configuredApiBase}/dist-packs/${filename}` : null,
      `https://cdn.jsdelivr.net/gh/${GITHUB_REPO}@main/public/dist-packs/${filename}`,
      `${ACCELERATOR_PREFIX}https://raw.githubusercontent.com/${GITHUB_REPO}/main/public/dist-packs/${filename}`,
      `https://raw.githubusercontent.com/${GITHUB_REPO}/main/public/dist-packs/${filename}`,
      `${ACCELERATOR_PREFIX}https://github.com/${GITHUB_REPO}/releases/download/packs/${filename}`,
      `https://github.com/${GITHUB_REPO}/releases/download/packs/${filename}`
    ].filter(Boolean);

    let lastError = null;
    for (const url of candidateUrls) {
      try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 6000);

        const res = await fetch(url, {
          signal: controller.signal,
          headers: { 'Accept': 'application/zip, application/octet-stream, */*' }
        });
        clearTimeout(timeoutId);

        if (!res.ok) continue;

        const contentType = (res.headers.get('content-type') || '').toLowerCase();
        if (contentType.includes('text/html')) continue;

        const buf = await res.arrayBuffer();
        if (buf.byteLength < 22) continue;
        const header = new Uint8Array(buf.slice(0, 4));
        if (header[0] !== 0x50 || header[1] !== 0x4b || header[2] !== 0x03 || header[3] !== 0x04) continue;

        arrayBuffer = buf;
        break;
      } catch (e) {
        lastError = e;
      }
    }

    if (!arrayBuffer) {
      throw new Error(`下载离线包文件 [${filename}] 失败: ${lastError?.message || '网络连接超时'}`);
    }
    return arrayBuffer;
  }

  /**
   * 解压 Zip 内部条目至指定目标目录
   * @private
   */
  async _extractZipEntries(arrayBuffer, targetBaseDir, onProgress, startPct = 70, endPct = 95) {
    const zip = await JSZip.loadAsync(arrayBuffer);
    const fileEntries = Object.keys(zip.files);
    const totalCount = fileEntries.length;
    let completedCount = 0;

    for (const relName of fileEntries) {
      const entry = zip.files[relName];
      const targetPath = `${targetBaseDir}/${relName}`;

      if (entry.dir) {
        try {
          await this._filesystem.mkdir({
            path: targetPath,
            directory: Directory.Data,
            recursive: true
          });
        } catch (_) {}
      } else {
        const textContent = await entry.async('string');
        await this._filesystem.writeFile({
          path: targetPath,
          data: textContent,
          directory: Directory.Data,
          encoding: Encoding.UTF8,
          recursive: true
        });
      }

      completedCount++;
      const currentPct = startPct + Math.round((completedCount / totalCount) * (endPct - startPct));
      if (typeof onProgress === 'function') onProgress(Math.min(endPct, currentPct));
    }
  }

  /**
   * 下载、校验并安装指定地域离线资源包（支持指定规格：基础包 或 附带画册）
   * @param {string} regionId 地域唯一标识
   * @param {Function} [onProgress] 进度回调函数 (0 - 100)
   * @param {object} [options] 扩展参数 { withGallery?: boolean }
   * @returns {Promise<void>}
   */
  async downloadAndInstallPack(regionId, onProgress, options = {}) {
    const region = regionsData.find((r) => r.id === regionId);
    if (!region) {
      throw new Error(`未找到指定地域配置: ${regionId}`);
    }
    if (!region.packInfo) {
      throw new Error(`地域 [${regionId}] 尚未配置离线包元数据`);
    }

    // 若为默认内置地域，无需重复下载
    if (region.packInfo.isDefaultInstalled) {
      if (typeof onProgress === 'function') onProgress(100);
      return;
    }

    const withGallery = Boolean(options.withGallery);
    const baseEndPct = withGallery ? 50 : 100;

    if (typeof onProgress === 'function') onProgress(5);

    // 1. 下载基础离线包
    const filename = region.packInfo.filename;
    const arrayBuffer = await this._downloadZipArrayBuffer(filename, regionId);
    if (typeof onProgress === 'function') onProgress(withGallery ? 25 : 50);

    // 校验 SHA-256 完整性
    if (region.packInfo.sha256) {
      if (typeof onProgress === 'function') onProgress(withGallery ? 30 : 60);
      const computedHash = await computeSha256(arrayBuffer);
      if (computedHash.toLowerCase() !== region.packInfo.sha256.toLowerCase()) {
        throw new Error(
          `离线包 SHA-256 完整性校验失败: 预期 ${region.packInfo.sha256}, 实际 ${computedHash}`
        );
      }
    }

    // 解压基础包
    await this._extractZipEntries(
      arrayBuffer,
      `${PACKS_DIR}/${regionId}`,
      onProgress,
      withGallery ? 35 : 70,
      withGallery ? 48 : 95
    );

    // 记录基础安装状态
    this._setStorageItem(`${PACK_STORAGE_PREFIX}${regionId}`, 'true');
    this._setStorageItem(
      `${PACK_STORAGE_META_PREFIX}${regionId}`,
      JSON.stringify({
        version: region.packInfo.version || '1.0.0',
        sizeBytes: region.packInfo.sizeBytes || arrayBuffer.byteLength,
        installedAt: Date.now()
      })
    );

    // 2. 若选择附带画册，接着下载画册扩展包
    if (withGallery && region.packInfo.galleryPack) {
      await this.downloadAndInstallGallery(regionId, (pct) => {
        // 将画册进度映射到 50% - 100%
        const mapped = 50 + Math.round(pct * 0.5);
        if (typeof onProgress === 'function') onProgress(mapped);
      });
    }

    if (typeof onProgress === 'function') onProgress(100);
  }

  /**
   * 增量下载并安装指定地域的高清风光画册包
   * @param {string} regionId 地域唯一标识
   * @param {Function} [onProgress] 进度回调函数 (0 - 100)
   * @returns {Promise<void>}
   */
  async downloadAndInstallGallery(regionId, onProgress) {
    const region = regionsData.find((r) => r.id === regionId);
    if (!region?.packInfo?.galleryPack) {
      // 若未单独配置画册包则静默完成
      if (typeof onProgress === 'function') onProgress(100);
      return;
    }

    if (typeof onProgress === 'function') onProgress(5);

    const galleryFilename = region.packInfo.galleryPack.filename;
    let arrayBuffer = null;
    try {
      arrayBuffer = await this._downloadZipArrayBuffer(galleryFilename, regionId);
    } catch (err) {
      // 若画册包尚未上传至远端，降级为就地初始化占位目录，严禁阻塞核心使用
      console.warn(`[ResourcePack] 画册包下载未就绪，使用轻量模式:`, err);
      this._setStorageItem(`${PACK_GALLERY_STORAGE_PREFIX}${regionId}`, 'true');
      if (typeof onProgress === 'function') onProgress(100);
      return;
    }

    if (typeof onProgress === 'function') onProgress(40);

    // 解压画册包至 gallery 子目录
    await this._extractZipEntries(
      arrayBuffer,
      `${PACKS_DIR}/${regionId}/gallery`,
      onProgress,
      50,
      95
    );

    this._setStorageItem(`${PACK_GALLERY_STORAGE_PREFIX}${regionId}`, 'true');
    await this.refreshGalleryBaseUris();
    if (typeof onProgress === 'function') onProgress(100);
  }

  /**
   * 仅卸载画册图片，释放空间并保留基础路线轨迹
   * @param {string} regionId
   * @returns {Promise<void>}
   */
  async uninstallGallery(regionId) {
    if (this.isNativePlatform()) {
      try {
        await this._filesystem.rmdir({
          path: `${PACKS_DIR}/${regionId}/gallery`,
          directory: Directory.Data,
          recursive: true
        });
      } catch (_) {}
    }
    this._removeStorageItem(`${PACK_GALLERY_STORAGE_PREFIX}${regionId}`);
    await this.refreshGalleryBaseUris();
  }

  /**
   * 卸载指定地域离线资源包并释放本地磁盘空间（包含画册）
   * 默认内置地域受保护，不可卸载
   * @param {string} regionId 地域唯一标识
   * @returns {Promise<void>}
   */
  async uninstallPack(regionId) {
    const region = regionsData.find((r) => r.id === regionId);
    if (region?.packInfo?.isDefaultInstalled) {
      // 默认内置地域不可卸载
      return;
    }

    if (this.isNativePlatform()) {
      try {
        await this._filesystem.rmdir({
          path: `${PACKS_DIR}/${regionId}`,
          directory: Directory.Data,
          recursive: true
        });
      } catch (err) {
        // 若目录已不存在则静默处理
      }
    }

    this._removeStorageItem(`${PACK_STORAGE_PREFIX}${regionId}`);
    this._removeStorageItem(`${PACK_STORAGE_META_PREFIX}${regionId}`);
    this._removeStorageItem(`${PACK_GALLERY_STORAGE_PREFIX}${regionId}`);
  }

  /**
   * 统计各地域离线包磁盘空间占用
   * @returns {Promise<{ [regionId: string]: number, totalBytes: number }>}
   */
  async getStorageUsage() {
    const usage = { totalBytes: 0 };
    if (!this.isNativePlatform()) {
      return usage;
    }

    for (const region of regionsData) {
      if (region.packInfo?.isDefaultInstalled) {
        continue;
      }

      const isInstalled = await this.isPackInstalled(region.id);
      if (isInstalled) {
        let size = 0;
        try {
          const stat = await this._filesystem.stat({
            path: `${PACKS_DIR}/${region.id}/mountains.json`,
            directory: Directory.Data
          });
          size = stat?.size || region.packInfo?.sizeBytes || 0;
        } catch {
          size = region.packInfo?.sizeBytes || 0;
        }
        usage[region.id] = size;
        usage.totalBytes += size;
      }
    }

    return usage;
  }
}

export const resourcePackService = new ResourcePackService();
