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

  // 下载并安装指定地域离线资源包
  async function downloadRegionPack(regionId) {
    downloadProgress.value = { ...downloadProgress.value, [regionId]: 0 };
    try {
      await resourcePackService.downloadAndInstallPack(regionId, (pct) => {
        downloadProgress.value = { ...downloadProgress.value, [regionId]: pct };
      });
      await refreshInstalledPacks();
      return true;
    } catch (err) {
      console.error(`[regionStore] 下载离线包 [${regionId}] 失败:`, err);
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
      return true;
    } catch (err) {
      console.error(`[regionStore] 卸载离线包 [${regionId}] 失败:`, err);
      throw err;
    }
  }

  // 切换目标区域，并联动 mountainStore 热挂载目标地域山峰数据
  async function setRegion(regionId) {
    const target = regions.value.find((r) => r.id === regionId);
    if (!target) {
      console.warn(`[regionStore] 目标地域 [${regionId}] 未收录，安全降级回退至默认成都`);
      currentRegionId.value = 'chengdu';
      if (typeof window !== 'undefined' && window.localStorage) {
        window.localStorage.setItem('weekly_mountain_region', 'chengdu');
      } else if (typeof globalThis !== 'undefined' && globalThis.localStorage) {
        globalThis.localStorage.setItem('weekly_mountain_region', 'chengdu');
      }
      try {
        const mountainStore = useMountainStore();
        await mountainStore.loadActiveRegion('chengdu');
      } catch (err) {
        console.warn('[regionStore] 降级载入默认地域异常:', err);
      }
      return currentRegion.value;
    }

    currentRegionId.value = regionId;
    if (typeof window !== 'undefined' && window.localStorage) {
      window.localStorage.setItem('weekly_mountain_region', regionId);
    } else if (typeof globalThis !== 'undefined' && globalThis.localStorage) {
      globalThis.localStorage.setItem('weekly_mountain_region', regionId);
    }

    try {
      const mountainStore = useMountainStore();
      await mountainStore.loadActiveRegion(regionId);
    } catch (err) {
      console.warn(`[regionStore] 联动挂载地域 [${regionId}] 山峰异常:`, err);
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
    downloadProgress,
    isRegionSheetOpen,
    isPackInstalled,
    refreshInstalledPacks,
    downloadRegionPack,
    uninstallRegionPack,
    setRegion,
    openRegionSheet,
    closeRegionSheet
  };
});
