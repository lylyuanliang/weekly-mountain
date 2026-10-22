<template>
  <div class="explore-view relative w-full h-screen overflow-hidden bg-background text-on-surface select-none font-body-md">
    <!-- ================= TOP APP BAR (Stitch Shared Header) ================= -->
    <header class="fixed top-0 inset-x-0 z-50 bg-surface/80 dark:bg-surface/80 backdrop-blur-md shadow-sm border-b border-outline-variant/20">
      <div class="flex justify-between items-center w-full px-margin h-16 max-w-md mx-auto">
        <div class="flex items-center gap-space-sm text-primary dark:text-primary">
          <!-- Region Switcher Pill -->
          <button
            aria-label="切换徒步省市与区域"
            @click="isRegionSheetOpen = true"
            class="flex items-center gap-1.5 px-3 py-1.5 rounded-full frost-glass border border-outline-variant/40 hover:border-primary/60 active:scale-95 transition-all text-on-surface"
          >
            <span class="w-2 h-2 rounded-full bg-primary glow-primary animate-pulse flex-shrink-0"></span>
            <span class="text-body-md font-bold tracking-tight text-primary">
              {{ regionStore.currentRegion.name }}
            </span>
            <span class="material-symbols-outlined text-primary text-[18px]">expand_more</span>
          </button>
        </div>
        <div class="flex items-center gap-2">
          <span class="hidden sm:inline-block px-2 py-0.5 rounded-full bg-surface-container-high text-label-data-sm font-label-data-sm text-primary">
            GPS ACTIVE
          </span>
          <button
            aria-label="选择区域与城市"
            @click="isRegionSheetOpen = true"
            class="w-10 h-10 rounded-full flex items-center justify-center bg-surface-container-low text-on-surface-variant dark:text-on-surface-variant hover:text-primary dark:hover:text-primary transition-colors duration-200 active:scale-95 shadow-inner"
          >
            <span class="material-symbols-outlined text-[22px]">tune</span>
          </button>
        </div>
      </div>
    </header>

    <!-- ================= FLOATING SEARCH & CHIP FILTERS ================= -->
    <TopSearchBar
      @focus="onSearchFocus"
    />

    <!-- ================= FULLSCREEN INTERACTIVE TOPO MAP CANVAS ================= -->
    <AppMap
      ref="mapRef"
      @mountain-select="onMountainSelected"
      @map-click="onMapClick"
      @map-pan="onMapPan"
    />

    <!-- ================= BOTTOM SHEET DRAWER ================= -->
    <BottomSheet
      ref="bottomSheetRef"
      @mountain-select="onMountainSelected"
      @mountain-detail="openMountainDetail"
      @mountain-weather="openMountainWeather"
    />

    <!-- ================= MOUNTAIN DETAIL DRAWER SHEET ================= -->
    <MountainDetailSheet
      v-model="isDetailOpen"
      :mountain="selectedDetailMountain"
      @checkin="onDetailCheckin"
      @add-plan="onDetailAddPlan"
      @probe-waypoint="onDetailProbeWaypoint"
      @clear-probe="onDetailClearProbe"
    />

    <!-- ================= LIVE WEATHER MODAL ================= -->
    <MountainWeatherModal
      v-model="isWeatherModalOpen"
      :mountain="selectedWeatherMountain"
      @view-detail="openMountainDetail"
    />

    <!-- ================= REGION PICKER SHEET ================= -->
    <RegionPickerSheet
      v-model="isRegionSheetOpen"
      @region-change="onRegionChanged"
      @toast="showToast"
    />

    <!-- Micro Toast Reaction -->
    <div
      v-if="toastMessage"
      class="fixed top-24 left-1/2 -translate-x-1/2 z-50 px-4 py-2 rounded-xl frost-glass-highlight text-primary text-body-sm font-semibold shadow-2xl flex items-center gap-2 transition-all duration-300"
    >
      <span class="material-symbols-outlined text-[18px]">info</span>
      <span>{{ toastMessage }}</span>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue';
import { useMountainStore } from '@/stores/mountainStore.js';
import { useRegionStore } from '@/stores/regionStore.js';
import TopSearchBar from '@/components/common/TopSearchBar.vue';
import AppMap from '@/components/map/AppMap.vue';
import BottomSheet from '@/components/drawer/BottomSheet.vue';
import MountainDetailSheet from '@/components/detail/MountainDetailSheet.vue';
import RegionPickerSheet from '@/components/common/RegionPickerSheet.vue';
import MountainWeatherModal from '@/components/weather/MountainWeatherModal.vue';

const mountainStore = useMountainStore();
const regionStore = useRegionStore();
const mapRef = ref(null);
const bottomSheetRef = ref(null);
const toastMessage = ref('');
let toastTimer = null;

const isRegionSheetOpen = ref(false);
const isDetailOpen = ref(false);
const selectedDetailMountain = ref(null);
const isWeatherModalOpen = ref(false);
const selectedWeatherMountain = ref(null);

function showToast(msg) {
  toastMessage.value = msg;
  if (toastTimer) clearTimeout(toastTimer);
  toastTimer = setTimeout(() => {
    toastMessage.value = '';
  }, 2400);
}

function onMapClick() {
  bottomSheetRef.value?.collapse?.();
}

function onSearchFocus() {
  // 当用户点击搜索框唤起移动端虚拟键盘时，自动将卡片抽屉收拢至 54px 极简折叠栏，彻底杜绝遮挡
  bottomSheetRef.value?.collapse?.();
}

function onMapPan() {
  bottomSheetRef.value?.collapse?.();
}

function onRegionChanged(reg) {
  mountainStore.resetFilters();
  if (mapRef.value?.panToLocation) {
    mapRef.value.panToLocation(reg.center.lng, reg.center.lat, reg.defaultZoom, 380, 50);
  }
  showToast(`已切换至【${reg.name}】（${reg.badge}）`);
}

function handleCompassClick() {
  if (mapRef.value?.recenterLocation) {
    mapRef.value.recenterLocation();
  }
  showToast('已重置回成都及周边全景视野');
}

function handleFilterClick() {
  showToast('当前已载入全部 50 座川西山峰拓扑数据');
}

function onMountainSelected(id) {
  if (bottomSheetRef.value?.expandToHalf) {
    bottomSheetRef.value.expandToHalf();
  }
  if (mapRef.value?.panToMountain) {
    mapRef.value.panToMountain(id);
  }
  const m = mountainStore.getMountainById(id);
  if (m) {
    showToast(`聚焦山峰：${m.name} · ${m.altitude_m || ''}m`);
  }
}

function openMountainDetail(mountain) {
  selectedDetailMountain.value = mountain;
  isDetailOpen.value = true;
}

function openMountainWeather(mountain) {
  selectedWeatherMountain.value = mountain;
  isWeatherModalOpen.value = true;
}

function onDetailCheckin(id) {
  const m = mountainStore.getMountainById(id);
  const name = m?.name || '山峰';
  showToast(`已切换【${name}】登顶打卡状态`);
}

function onDetailAddPlan(id) {
  const m = mountainStore.getMountainById(id);
  const name = m?.name || '山峰';
  showToast(`已将【${name}】加入本周徒步计划`);
}

function onDetailProbeWaypoint(waypoint) {
  if (mapRef.value?.setProbeMarker) {
    mapRef.value.setProbeMarker(waypoint);
  }
}

function onDetailClearProbe() {
  if (mapRef.value?.clearProbe) {
    mapRef.value.clearProbe();
  }
}

// 抽屉关闭时联动清除地图探针信标
watch(isDetailOpen, (open) => {
  if (!open) {
    mapRef.value?.clearProbe?.();
  }
});
</script>
