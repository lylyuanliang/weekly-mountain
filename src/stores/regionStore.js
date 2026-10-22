import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import regionsData from '../data/regions.json' with { type: 'json' };

export const useRegionStore = defineStore('region', () => {
  const regions = ref(regionsData);
  const currentRegionId = ref(
    typeof window !== 'undefined'
      ? localStorage.getItem('weekly_mountain_region') || 'chengdu'
      : 'chengdu'
  );
  const isRegionSheetOpen = ref(false);

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

  // 切换目标区域
  function setRegion(regionId) {
    const target = regions.value.find((r) => r.id === regionId);
    if (!target) return;

    currentRegionId.value = regionId;
    if (typeof window !== 'undefined') {
      localStorage.setItem('weekly_mountain_region', regionId);
    }
  }

  function openRegionSheet() {
    isRegionSheetOpen.value = true;
  }

  function closeRegionSheet() {
    isRegionSheetOpen.value = false;
  }

  return {
    regions,
    currentRegionId,
    currentRegion,
    activeRegions,
    plannedRegions,
    isRegionSheetOpen,
    setRegion,
    openRegionSheet,
    closeRegionSheet
  };
});
