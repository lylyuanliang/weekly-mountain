<template>
  <div class="top-search-bar fixed top-[72px] inset-x-0 z-[55] px-margin flex flex-col gap-2.5 max-w-md mx-auto pointer-events-auto">
    <!-- Search Bar -->
    <div class="w-full h-12 rounded-xl frost-glass flex items-center px-3.5 gap-2.5 shadow-2xl border border-outline-variant/40 focus-within:border-primary/70 focus-within:glow-primary transition-all">
      <span class="material-symbols-outlined text-primary text-[22px] flex-shrink-0">search</span>
      <input
        ref="searchInputRef"
        :value="mountainStore.searchQuery"
        @input="onSearchInput"
        @focus="onFocus"
        @blur="onBlur"
        class="w-full bg-transparent border-0 p-0 text-on-surface placeholder:text-outline text-body-md focus:ring-0 focus:outline-none"
        :placeholder="`搜索${regionStore.currentRegion.shortName}周边山峰、路线、县域、标签...`"
        type="text"
      />
      <button
        v-if="mountainStore.searchQuery"
        @click="clearSearch"
        aria-label="Clear Search"
        class="p-1 rounded-lg text-on-surface-variant hover:text-primary active:scale-95 transition-transform"
      >
        <span class="material-symbols-outlined text-[18px]">close</span>
      </button>
      <button
        v-else
        aria-label="Voice Search"
        class="p-1.5 rounded-lg text-on-surface-variant hover:text-primary active:scale-95 transition-transform"
      >
        <span class="material-symbols-outlined text-[20px]">mic</span>
      </button>
    </div>

    <!-- Horizontal Scrollable Filter Chips -->
    <div class="flex items-center gap-2 overflow-x-auto no-scrollbar py-0.5 -mx-margin px-margin">
      <!-- Active / All Peaks Filter -->
      <button
        @click="selectAll"
        class="filter-chip flex-shrink-0 flex items-center gap-1.5 px-3 py-1.5 rounded-full font-body-sm transition-all active:scale-95"
        :class="isAllActive
          ? 'bg-surface-container-high border border-primary text-primary glow-primary font-semibold'
          : 'frost-glass border border-outline-variant/30 text-on-surface-variant hover:text-on-surface'"
      >
        <span class="w-1.5 h-1.5 rounded-full bg-primary"></span>
        <span>全部 ({{ currentRegionMountainsCount }})</span>
      </button>

      <!-- L1 Leisure -->
      <button
        @click="toggleDifficulty('L1')"
        class="filter-chip flex-shrink-0 flex items-center gap-1.5 px-3 py-1.5 rounded-full font-body-sm transition-all active:scale-95"
        :class="mountainStore.activeFilters.difficulty === 'L1'
          ? 'bg-surface-container-high border border-primary text-primary glow-primary font-semibold'
          : 'frost-glass border border-outline-variant/30 text-on-surface-variant hover:text-on-surface'"
      >
        <span class="w-1.5 h-1.5 rounded-full bg-primary-container"></span>
        <span>L1 轻松 (&lt;5km)</span>
      </button>

      <!-- L2 Intermediate -->
      <button
        @click="toggleDifficulty('L2')"
        class="filter-chip flex-shrink-0 flex items-center gap-1.5 px-3 py-1.5 rounded-full font-body-sm transition-all active:scale-95"
        :class="mountainStore.activeFilters.difficulty === 'L2'
          ? 'bg-surface-container-high border border-secondary text-secondary glow-secondary font-semibold'
          : 'frost-glass border border-outline-variant/30 text-on-surface-variant hover:text-on-surface'"
      >
        <span class="w-1.5 h-1.5 rounded-full bg-secondary"></span>
        <span>L2 进阶 (5-15km)</span>
      </button>

      <!-- L3 Summit Challenge -->
      <button
        @click="toggleDifficulty('L3')"
        class="filter-chip flex-shrink-0 flex items-center gap-1.5 px-3 py-1.5 rounded-full font-body-sm transition-all active:scale-95"
        :class="mountainStore.activeFilters.difficulty === 'L3'
          ? 'bg-surface-container-high border border-tertiary text-tertiary glow-gold font-semibold'
          : 'frost-glass border border-outline-variant/30 text-on-surface-variant hover:text-on-surface'"
      >
        <span class="w-1.5 h-1.5 rounded-full bg-tertiary"></span>
        <span>L3 挑战</span>
      </button>

      <!-- L4/L5 Hardcore -->
      <button
        @click="toggleDifficulty('L4')"
        class="filter-chip flex-shrink-0 flex items-center gap-1.5 px-3 py-1.5 rounded-full font-body-sm transition-all active:scale-95"
        :class="mountainStore.activeFilters.difficulty === 'L4'
          ? 'bg-surface-container-high border border-error text-error font-semibold'
          : 'frost-glass border border-outline-variant/30 text-on-surface-variant hover:text-on-surface'"
      >
        <span class="w-1.5 h-1.5 rounded-full bg-error"></span>
        <span>L4 硬核</span>
      </button>

      <!-- Drive 2-4h -->
      <button
        @click="toggleDriveHours(4)"
        class="filter-chip flex-shrink-0 flex items-center gap-1 px-3 py-1.5 rounded-full font-body-sm transition-all active:scale-95"
        :class="mountainStore.activeFilters.maxDrive === 4
          ? 'bg-surface-container-high border border-primary text-primary glow-primary font-semibold'
          : 'frost-glass border border-outline-variant/30 text-on-surface-variant hover:text-on-surface'"
      >
        <span class="material-symbols-outlined text-[16px]">directions_car</span>
        <span>车程 2-4h</span>
      </button>

      <!-- Sea of Clouds -->
      <button
        @click="toggleScenario('云海')"
        class="filter-chip flex-shrink-0 flex items-center gap-1 px-3 py-1.5 rounded-full font-body-sm transition-all active:scale-95"
        :class="isScenarioActive('云海')
          ? 'bg-surface-container-high border border-secondary text-secondary glow-secondary font-semibold'
          : 'frost-glass border border-outline-variant/30 text-on-surface-variant hover:text-on-surface'"
      >
        <span class="material-symbols-outlined text-[16px] text-secondary">cloud</span>
        <span>日出云海</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useMountainStore } from '@/stores/mountainStore.js';
import { useRegionStore } from '@/stores/regionStore.js';

const mountainStore = useMountainStore();
const regionStore = useRegionStore();
const emit = defineEmits(['focus', 'blur']);

const currentRegionMountainsCount = computed(() => {
  const regId = regionStore.currentRegionId;
  return mountainStore.mountains.filter((m) => !m.region_id || m.region_id === regId).length;
});

const isAllActive = computed(() => {
  const f = mountainStore.activeFilters;
  return (
    (!mountainStore.searchQuery || mountainStore.searchQuery.trim() === '') &&
    f.difficulty === 'all' &&
    f.region === 'all' &&
    (!f.maxDrive || f.maxDrive === 0) &&
    (!f.scenarios || f.scenarios.length === 0)
  );
});

function onSearchInput(e) {
  mountainStore.setSearch(e.target.value);
}

function onFocus(e) {
  emit('focus', e);
}

function onBlur(e) {
  emit('blur', e);
}

function clearSearch() {
  mountainStore.setSearch('');
}

function selectAll() {
  mountainStore.resetFilters();
}

function toggleDifficulty(diff) {
  if (mountainStore.activeFilters.difficulty === diff) {
    mountainStore.setFilter('difficulty', 'all');
  } else {
    mountainStore.setFilter('difficulty', diff);
  }
}

function toggleDriveHours(hours) {
  if (mountainStore.activeFilters.maxDrive === hours) {
    mountainStore.setFilter('maxDrive', 0);
  } else {
    mountainStore.setFilter('maxDrive', hours);
  }
}

function isScenarioActive(tag) {
  return (
    Array.isArray(mountainStore.activeFilters.scenarios) &&
    mountainStore.activeFilters.scenarios.includes(tag)
  );
}

function toggleScenario(tag) {
  const cur = Array.isArray(mountainStore.activeFilters.scenarios)
    ? [...mountainStore.activeFilters.scenarios]
    : [];
  const idx = cur.indexOf(tag);
  if (idx >= 0) {
    cur.splice(idx, 1);
  } else {
    cur.push(tag);
  }
  mountainStore.setFilter('scenarios', cur);
}
</script>
