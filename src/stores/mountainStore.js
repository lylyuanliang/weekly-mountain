import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import mountainsData from '../data/mountains.json' with { type: 'json' };
import waypointsData from '../data/waypoints.json' with { type: 'json' };
import regionsData from '../data/regions.json' with { type: 'json' };
import { resourcePackService } from '../services/resourcePackService.js';
import { useRegionStore } from './regionStore.js';

export const GROUP_META = {
  A: { label: "云海日出", icon: "☁️" },
  B: { label: "雪山远眺", icon: "🏔️" },
  C: { label: "森林瀑布", icon: "🌲" },
  D: { label: "红叶彩林", icon: "🍁" },
  E: { label: "古道人文", icon: "⛩️" },
  F: { label: "草甸花海", icon: "🌸" },
  G: { label: "进阶野线", icon: "🧗" },
  H: { label: "远线王牌", icon: "👑" }
};

export const DIFF_LABEL = {
  L1: "轻松",
  L2: "休闲",
  L3: "进阶",
  L4: "挑战",
  L5: "硬核"
};

export const DIFF_COLOR = {
  L1: "#4ade80",
  L2: "#34d399",
  L3: "#fbbf24",
  L4: "#fb923c",
  L5: "#f87171"
};

export const SEASON_OF_MONTH = {
  12: "冬", 1: "冬", 2: "冬",
  3: "春", 4: "春", 5: "春",
  6: "夏", 7: "夏", 8: "夏",
  9: "秋", 10: "秋", 11: "秋"
};

export function seasonNow() {
  const m = new Date().getMonth() + 1;
  return SEASON_OF_MONTH[m] || "春";
}

// 计算两点间的 Haversine 地理直线距离（公里）
export function getDistanceKm(lat1, lon1, lat2, lon2) {
  if (typeof lat1 !== 'number' || typeof lon1 !== 'number' || typeof lat2 !== 'number' || typeof lon2 !== 'number') {
    return 0;
  }
  const R = 6371; // 地球平均半径 (km)
  const dLat = ((lat2 - lat1) * Math.PI) / 180;
  const dLon = ((lon2 - lon1) * Math.PI) / 180;
  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos((lat1 * Math.PI) / 180) * Math.cos((lat2 * Math.PI) / 180) *
    Math.sin(dLon / 2) * Math.sin(dLon / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return Math.round(R * c * 10) / 10;
}

// 提取山峰代表性地理坐标（优先最高海拔打卡点）
export function getMountainCoordinate(mountain, waypointsMap = waypointsData) {
  if (!mountain) return { lat: 30.65, lng: 103.35 };

  // 1. 优先从全局打卡点字典匹配
  const wps = (waypointsMap && waypointsMap[mountain.id]) || [];
  let bestWp = null;
  let maxAlt = -1;

  for (const w of wps) {
    if (typeof w.lat === 'number' && typeof w.lng === 'number') {
      const alt = w.alt_m || 0;
      if (alt > maxAlt) {
        maxAlt = alt;
        bestWp = w;
      }
    }
  }

  if (!bestWp && wps.length > 0) {
    bestWp = wps[0];
  }

  // 2. 尝试从山峰自身所包含的航迹点路由 (wp_routes) 提取
  if (!bestWp && Array.isArray(mountain.wp_routes)) {
    for (const r of mountain.wp_routes) {
      if (Array.isArray(r.waypoints)) {
        for (const w of r.waypoints) {
          if (typeof w.lat === 'number' && typeof w.lng === 'number') {
            const alt = w.alt_m || 0;
            if (alt > maxAlt) {
              maxAlt = alt;
              bestWp = w;
            }
          }
        }
      }
    }
  }

  if (bestWp) {
    return {
      lat: bestWp.lat,
      lng: bestWp.lng
    };
  }

  // 3. 尝试直接坐标字段
  if (typeof mountain.lat === 'number' && typeof mountain.lng === 'number') {
    return { lat: mountain.lat, lng: mountain.lng };
  }
  if (mountain.coord && typeof mountain.coord.lat === 'number' && typeof mountain.coord.lng === 'number') {
    return { lat: mountain.coord.lat, lng: mountain.coord.lng };
  }

  // 4. 根据山峰所属地域配置获取中心坐标基准
  if (mountain.region_id) {
    const reg = regionsData.find((r) => r.id === mountain.region_id);
    if (reg?.center) {
      return { lat: reg.center.lat, lng: reg.center.lng };
    }
  }

  return {
    lat: 30.65,
    lng: 103.35
  };
}

const defaultFilters = () => ({
  difficulty: 'all',
  region: 'all',
  maxDrive: 0,
  scenarios: []
});

export const useMountainStore = defineStore('mountain', () => {
  const mountains = ref(mountainsData);
  const waypoints = ref(waypointsData);
  const isLoading = ref(false);
  const searchQuery = ref('');
  const activeFilters = ref(defaultFilters());
  const selectedMountainId = ref(mountainsData[0]?.id || null);

  const selectedMountain = computed(() => {
    const regionStore = useRegionStore();
    const curCenter = regionStore.currentRegion?.center || { lng: 104.066, lat: 30.657 };

    // 优先从已计算好距离的 filteredMountains 中获取
    const sel = filteredMountains.value.find((m) => m.id === selectedMountainId.value);
    if (sel) {
      return sel;
    }

    const rawSel = mountains.value.find((m) => m.id === selectedMountainId.value);
    if (rawSel) {
      const coord = getMountainCoordinate(rawSel, waypoints.value);
      return {
        ...rawSel,
        distToCenterKm: getDistanceKm(curCenter.lat, curCenter.lng, coord.lat, coord.lng)
      };
    }
    return filteredMountains.value[0] || null;
  });

  const regions = computed(() => {
    const map = {};
    const regionStore = useRegionStore();
    const curRegionId = regionStore.currentRegionId;

    mountains.value.forEach((m) => {
      if (m.region_id && curRegionId && m.region_id !== curRegionId) {
        const allSameRegion = mountains.value.every((item) => item.region_id === m.region_id);
        if (!allSameRegion) return;
      }
      const r = m.region || '其他';
      map[r] = (map[r] || 0) + 1;
    });
    return Object.keys(map)
      .sort((a, b) => map[b] - map[a])
      .map((r) => ({ region: r, count: map[r] }));
  });

  const filteredMountains = computed(() => {
    const q = (searchQuery.value || '').trim().toLowerCase();
    const season = seasonNow();
    const { difficulty, region, maxDrive, scenarios } = activeFilters.value;
    const regionStore = useRegionStore();
    const curRegionId = regionStore.currentRegionId;
    const curCenter = regionStore.currentRegion?.center || { lng: 104.066, lat: 30.657 };

    const results = mountains.value.filter((m) => {
      // 0. City / Region match (e.g. chengdu / chongqing)
      if (m.region_id && curRegionId && m.region_id !== curRegionId) {
        // 若当前数据集全部属于降级默认地域，仍确保展示
        const allSameRegion = mountains.value.every((item) => item.region_id === m.region_id);
        if (!allSameRegion) {
          return false;
        }
      }

      // 1. Keyword search (name, region, county, tags, group)
      if (q) {
        const hay = (
          (m.name || '') + ' ' +
          (m.county || '') + ' ' +
          (m.county_short || '') + ' ' +
          (m.region || '') + ' ' +
          (Array.isArray(m.tags) ? m.tags.join(' ') : '') + ' ' +
          (m.group || '') + ' ' +
          (GROUP_META[m.group]?.label || '')
        ).toLowerCase();
        if (!hay.includes(q)) return false;
      }

      // 2. Difficulty filter
      if (difficulty && difficulty !== 'all') {
        if (m.difficulty !== difficulty) return false;
      }

      // 3. Region filter
      if (region && region !== 'all') {
        const reg = m.region || '其他';
        if (reg !== region && !(m.county || '').includes(region)) {
          return false;
        }
      }

      // 4. Maximum driving hours filter
      if (typeof maxDrive === 'number' && maxDrive > 0 && maxDrive < 100) {
        if ((m.drive_hours || 0) > maxDrive) return false;
      }

      // 5. Scenarios / Tags filter
      if (Array.isArray(scenarios) && scenarios.length > 0) {
        for (const s of scenarios) {
          if (s === 'free') {
            if (!m.free) return false;
          } else if (s === 'overnight') {
            if (!m.overnight) return false;
          } else if (s === 'season') {
            const sb = Array.isArray(m.season_best) ? m.season_best.join(';') : String(m.season_best || '');
            if (!sb.includes(season)) return false;
          } else {
            const matchTag = Array.isArray(m.tags) && m.tags.some((t) => t.includes(s));
            const matchGroup = m.group === s || GROUP_META[m.group]?.label === s;
            if (!matchTag && !matchGroup) return false;
          }
        }
      }

      return true;
    });

    // 注入距当前市中心的精确直线距离（公里）
    const withDistance = results.map((m) => {
      const coord = getMountainCoordinate(m, waypoints.value);
      const dist = getDistanceKm(curCenter.lat, curCenter.lng, coord.lat, coord.lng);
      return {
        ...m,
        distToCenterKm: dist
      };
    });

    if (q) {
      return withDistance.sort((a, b) => {
        const aHas = (a.name || '').toLowerCase().includes(q);
        const bHas = (b.name || '').toLowerCase().includes(q);
        if (aHas && !bHas) return -1;
        if (!aHas && bHas) return 1;
        return (a.distToCenterKm || 0) - (b.distToCenterKm || 0);
      });
    }

    // 核心需求：卡片按照距市中心距离「由近到远」排序
    return withDistance.sort((a, b) => (a.distToCenterKm || 0) - (b.distToCenterKm || 0));
  });

  // 异步载入并响应式热挂载指定地域山峰数据集
  async function loadActiveRegion(regionId) {
    isLoading.value = true;
    try {
      const data = await resourcePackService.loadRegionMountains(regionId);
      const safeData = Array.isArray(data) && data.length > 0 ? data : mountainsData;
      mountains.value = safeData;

      // 自动定位首座标杆名山
      if (safeData.length > 0) {
        selectedMountainId.value = safeData[0].id;
      }

      // 同步保持 regionStore 选中状态一致
      const regionStore = useRegionStore();
      if (regionStore.currentRegionId !== regionId && regionStore.regions.some((r) => r.id === regionId)) {
        regionStore.currentRegionId = regionId;
        if (typeof window !== 'undefined' && window.localStorage) {
          window.localStorage.setItem('weekly_mountain_region', regionId);
        } else if (typeof globalThis !== 'undefined' && globalThis.localStorage) {
          globalThis.localStorage.setItem('weekly_mountain_region', regionId);
        }
      }

      return safeData;
    } catch (err) {
      console.warn(`[mountainStore] 加载地域 [${regionId}] 山峰异常，安全降级至默认数据集:`, err);
      mountains.value = mountainsData;
      if (mountainsData.length > 0) {
        selectedMountainId.value = mountainsData[0].id;
      }
      return mountainsData;
    } finally {
      isLoading.value = false;
    }
  }

  function setSearch(q) {
    searchQuery.value = q || '';
  }

  function setFilter(key, val) {
    if (typeof key === 'object' && key !== null) {
      Object.assign(activeFilters.value, key);
    } else {
      activeFilters.value[key] = val;
    }
  }

  function resetFilters() {
    searchQuery.value = '';
    activeFilters.value = defaultFilters();
  }

  function selectMountain(id) {
    selectedMountainId.value = id;
  }

  function getMountainById(id) {
    const m = mountains.value.find((item) => item.id === id);
    if (!m) return null;
    const regionStore = useRegionStore();
    const curCenter = regionStore.currentRegion?.center || { lng: 104.066, lat: 30.657 };
    const coord = getMountainCoordinate(m, waypoints.value);
    return {
      ...m,
      distToCenterKm: getDistanceKm(curCenter.lat, curCenter.lng, coord.lat, coord.lng)
    };
  }

  return {
    mountains,
    waypoints,
    isLoading,
    searchQuery,
    activeFilters,
    selectedMountainId,
    selectedMountain,
    regions,
    filteredMountains,
    setSearch,
    setFilter,
    resetFilters,
    selectMountain,
    getMountainById,
    loadActiveRegion
  };
});
