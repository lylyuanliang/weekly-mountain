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
   * 下载、校验并安装指定地域离线资源包
   * @param {string} regionId 地域唯一标识
   * @param {Function} [onProgress] 进度回调函数 (0 - 100)
   * @returns {Promise<void>}
   */
  async downloadAndInstallPack(regionId, onProgress) {
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

    if (typeof onProgress === 'function') onProgress(5);

    let arrayBuffer = null;

    // 测试模式优先使用注入的下载通道
    if (typeof this._downloadHandlerForTesting === 'function') {
      arrayBuffer = await this._downloadHandlerForTesting(regionId);
      if (typeof onProgress === 'function') onProgress(50);
    } else {
      // 生产环境多通道高可用下载
      const filename = region.packInfo.filename;
      const candidateUrls = [
        `${ACCELERATOR_PREFIX}https://github.com/${GITHUB_REPO}/releases/download/packs/${filename}`,
        `https://github.com/${GITHUB_REPO}/releases/download/packs/${filename}`,
        typeof window !== 'undefined' ? `/dist-packs/${filename}` : null
      ].filter(Boolean);

      let lastError = null;
      for (const url of candidateUrls) {
        try {
          const res = await fetch(url);
          if (res.ok) {
            arrayBuffer = await res.arrayBuffer();
            break;
          }
        } catch (e) {
          lastError = e;
        }
      }

      if (!arrayBuffer) {
        throw new Error(`下载离线包 [${regionId}] 失败: ${lastError?.message || '网络连接超时'}`);
      }
      if (typeof onProgress === 'function') onProgress(50);
    }

    // 校验 SHA-256 完整性
    if (region.packInfo.sha256) {
      if (typeof onProgress === 'function') onProgress(60);
      const computedHash = await computeSha256(arrayBuffer);
      if (computedHash.toLowerCase() !== region.packInfo.sha256.toLowerCase()) {
        throw new Error(
          `离线包 SHA-256 完整性校验失败: 预期 ${region.packInfo.sha256}, 实际 ${computedHash}`
        );
      }
    }

    if (typeof onProgress === 'function') onProgress(70);

    // 使用 JSZip 解压并写入文件系统
    const zip = await JSZip.loadAsync(arrayBuffer);
    const fileEntries = Object.keys(zip.files);
    const totalCount = fileEntries.length;
    let completedCount = 0;

    for (const relName of fileEntries) {
      const entry = zip.files[relName];
      const targetPath = `${PACKS_DIR}/${regionId}/${relName}`;

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
      const currentPct = 70 + Math.round((completedCount / totalCount) * 25);
      if (typeof onProgress === 'function') onProgress(Math.min(95, currentPct));
    }

    // 记录安装状态标记与元数据
    this._setStorageItem(`${PACK_STORAGE_PREFIX}${regionId}`, 'true');
    this._setStorageItem(
      `${PACK_STORAGE_META_PREFIX}${regionId}`,
      JSON.stringify({
        version: region.packInfo.version || '1.0.0',
        sizeBytes: region.packInfo.sizeBytes || arrayBuffer.byteLength,
        installedAt: Date.now()
      })
    );

    if (typeof onProgress === 'function') onProgress(100);
  }

  /**
   * 卸载指定地域离线资源包并释放本地磁盘空间
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
