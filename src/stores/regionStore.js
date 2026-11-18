import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import regionsData from '../data/regions.json' with { type: 'json' };
import { resourcePackService } from '../services/resourcePackService.js';
import { useMountainStore } from './mountainStore.js';

export const useRegionStore = defineStore('region', () => {
  const regions = ref(regionsData);
  const currentRegionId = ref(
    typeof window !== 'undefined' && window.localStorage
      ? window.localStorage.getItem('weekly_mountain_region') || 'chengdu'
      : typeof globalThis !== 'undefined' && globalThis.localStorage
        ? globalThis.localStorage.getItem('weekly_mountain_region') || 'chengdu'
        : 'chengdu'
  );
  const isRegionSheetOpen = ref(false);

  // 已安装离线包集合与下载进度字典
  const installedPacks = ref(['chengdu']);
  const installedGalleries = ref(['chengdu']);
  const downloadProgress = ref({});

  // 当前选中的区域详细对象
  const currentRegion = computed(() => {
    return regions.value.find((r) => r.id === currentRegionId.value) || regions.value[0];
  });

  // 已开通上线的城市列表
  const activeRegions = computed(() => {
    return regions.value.filter((r) => r.status === 'active');
  });

  // 路线勘测与规划中的城市列表
  const plannedRegions = computed(() => {
    return regions.value.filter((r) => r.status === 'planned');
  });

  // 刷新已安装资源包列表
  async function refreshInstalledPacks() {
    try {
      const list = await resourcePackService.getInstalledPacks();
      const arr = Array.isArray(list) ? [...list] : ['chengdu'];
      arr.has = (id) => arr.includes(id);
      Object.defineProperty(arr, 'size', {
        get() {
          return this.length;
        },
        configurable: true
      });
      installedPacks.value = arr;

      // 同步画册安装状态
      const galleryList = ['chengdu'];
      for (const reg of regions.value) {
        if (reg.id !== 'chengdu' && (await resourcePackService.isGalleryInstalled(reg.id))) {
          galleryList.push(reg.id);
        }
      }
      installedGalleries.value = galleryList;
      await resourcePackService.refreshGalleryBaseUris();

      // 原生端防护：如果当前选中的地域不在已安装列表中，且不是默认内置地域，自动重置回退至默认成都
      if (resourcePackService.isNativePlatform() && currentRegionId.value !== 'chengdu' && !installedPacks.value.includes(currentRegionId.value)) {
        console.warn(`[regionStore] 当前地域 [${currentRegionId.value}] 离线包已被卸载/未就绪，自动重置回退至默认成都`);
        await setRegion('chengdu');
      } else {
        // 确保已挂载的山峰数据与当前生效的地域严格一致
        try {
          const mountainStore = useMountainStore();
          if (mountainStore.mountains.length === 0 || (mountainStore.mountains[0]?.region_id && mountainStore.mountains[0].region_id !== currentRegionId.value)) {
            await mountainStore.loadActiveRegion(currentRegionId.value);
          }
        } catch (_) {}
      }

      return installedPacks.value;
    } catch (err) {
      console.warn('[regionStore] 刷新已安装离线包列表失败:', err);
      return installedPacks.value;
    }
  }

  // 检查指定区域资源包是否就绪可用
  function isPackInstalled(regionId) {
    if (installedPacks.value && typeof installedPacks.value.has === 'function') {
      return installedPacks.value.has(regionId);
    }
    return Array.isArray(installedPacks.value) && installedPacks.value.includes(regionId);
  }

  // 检查指定区域画册是否已就绪
  function isGalleryInstalled(regionId) {
    if (regionId === 'chengdu') return true;
    return installedGalleries.value.includes(regionId);
  }

  // 下载并安装指定地域离线资源包（支持指定规格）
  async function downloadRegionPack(regionId, options = {}) {
    downloadProgress.value = { ...downloadProgress.value, [regionId]: 0 };
    try {
      await resourcePackService.downloadAndInstallPack(
        regionId,
        (pct) => {
          downloadProgress.value = { ...downloadProgress.value, [regionId]: pct };
        },
        options
      );
      await refreshInstalledPacks();
      return true;
    } catch (err) {
      console.error(`[regionStore] 下载离线包 [${regionId}] 失败:`, err);
      throw err;
    }
  }

  // 增量补全指定地域的高清风光画册包
  async function downloadRegionGallery(regionId) {
    downloadProgress.value = { ...downloadProgress.value, [regionId]: 0 };
    try {
      await resourcePackService.downloadAndInstallGallery(regionId, (pct) => {
        downloadProgress.value = { ...downloadProgress.value, [regionId]: pct };
      });
      await refreshInstalledPacks();
      return true;
    } catch (err) {
      console.error(`[regionStore] 补全画册包 [${regionId}] 失败:`, err);
      throw err;
    }
  }

  // 仅卸载画册图片，释放空间并保留基础路线轨迹
  async function uninstallRegionGallery(regionId) {
    try {
      await resourcePackService.uninstallGallery(regionId);
      await refreshInstalledPacks();
      return true;
    } catch (err) {
      console.error(`[regionStore] 释放画册图片 [${regionId}] 失败:`, err);
      throw err;
    }
  }

  // 卸载指定地域离线资源包并释放本地存储
  async function uninstallRegionPack(regionId) {
    try {
      await resourcePackService.uninstallPack(regionId);
      const nextProgress = { ...downloadProgress.value };
      delete nextProgress[regionId];
      downloadProgress.value = nextProgress;
      await refreshInstalledPacks();

      // 核心闭环：若卸载的正是当前正在浏览的区域，立即强制切回默认成都并重新载入成都山峰！
      if (currentRegionId.value === regionId) {
        console.info(`[regionStore] 当前地域 [${regionId}] 已被卸载，自动切回默认基线地域 [chengdu]`);
        await setRegion('chengdu');
      }

      return true;
    } catch (err) {
      console.error(`[regionStore] 卸载离线包 [${regionId}] 失败:`, err);
      throw err;
    }
  }

  // 切换目标区域，并联动 mountainStore 热挂载目标地域山峰数据
  async function setRegion(regionId) {
    let targetId = regionId;
    let target = regions.value.find((r) => r.id === targetId);

    // 原生移动端防线：若非内置默认地域且离线包未就绪，严禁切换至该地域，安全阻断并回退至默认成都
    if (target && resourcePackService.isNativePlatform() && !target.packInfo?.isDefaultInstalled) {
      const isReady = await resourcePackService.isPackInstalled(targetId);
      if (!isReady) {
        console.warn(`[regionStore] 目标地域 [${targetId}] 离线包未安装，安全阻断并回退至默认成都`);
        targetId = 'chengdu';
        target = regions.value.find((r) => r.id === 'chengdu');
      }
    }

    if (!target) {
      console.warn(`[regionStore] 目标地域 [${regionId}] 未收录，安全降级回退至默认成都`);
      targetId = 'chengdu';
      target = regions.value.find((r) => r.id === 'chengdu');
    }

    currentRegionId.value = targetId;
    if (typeof window !== 'undefined' && window.localStorage) {
      window.localStorage.setItem('weekly_mountain_region', targetId);
    } else if (typeof globalThis !== 'undefined' && globalThis.localStorage) {
      globalThis.localStorage.setItem('weekly_mountain_region', targetId);
    }

    try {
      const mountainStore = useMountainStore();
      await mountainStore.loadActiveRegion(targetId);
    } catch (err) {
      console.warn(`[regionStore] 联动挂载地域 [${targetId}] 山峰异常:`, err);
    }

    return currentRegion.value;
  }

  function openRegionSheet() {
    isRegionSheetOpen.value = true;
  }

  function closeRegionSheet() {
    isRegionSheetOpen.value = false;
  }

  // 初始化尝试静默同步已安装离线包状态
  refreshInstalledPacks().catch(() => {});

  return {
    regions,
    currentRegionId,
    currentRegion,
    activeRegions,
    plannedRegions,
    installedPacks,
    installedGalleries,
    downloadProgress,
    isRegionSheetOpen,
    isPackInstalled,
    isGalleryInstalled,
    refreshInstalledPacks,
    downloadRegionPack,
    downloadRegionGallery,
    uninstallRegionGallery,
    uninstallRegionPack,
    setRegion,
    openRegionSheet,
    closeRegionSheet
  };
});
