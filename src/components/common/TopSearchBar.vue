<template>
  <div class="top-search-bar fixed top-[calc(68px+max(env(safe-area-inset-top,0px),16px))] inset-x-0 z-[55] px-margin flex flex-col gap-2.5 max-w-md mx-auto pointer-events-auto">
    <!-- Search Bar with Floating Suggestions Anchor -->
    <div class="relative w-full">
      <div class="w-full h-10 rounded-xl frost-glass flex items-center px-3 gap-2 shadow-xl border border-outline-variant/40 focus-within:border-primary/70 focus-within:glow-primary transition-all">
        <span class="material-symbols-outlined text-primary text-[19px] flex-shrink-0">search</span>
        <input
          ref="searchInputRef"
          :value="mountainStore.searchQuery"
          @input="onSearchInput"
          @focus="onFocus"
          @blur="onBlur"
          class="w-full bg-transparent border-0 p-0 text-on-surface placeholder:text-outline/80 text-[13px] focus:ring-0 focus:outline-none"
          :placeholder="`搜索${regionStore.currentRegion.shortName}周边山峰、路线、县域、标签...`"
          type="text"
        />
        <button
          v-if="mountainStore.searchQuery"
          @mousedown.prevent
          @click="clearSearch"
          aria-label="Clear Search"
          class="p-1 rounded-lg text-on-surface-variant hover:text-primary active:scale-95 transition-transform cursor-pointer"
        >
          <span class="material-symbols-outlined text-[17px]">close</span>
        </button>
        <button
          v-else
          aria-label="Voice Search"
          class="p-1 rounded-lg text-on-surface-variant hover:text-primary active:scale-95 transition-transform"
        >
          <span class="material-symbols-outlined text-[18px]">mic</span>
        </button>
      </div>

      <!-- Search Suggestions Dropdown Overlay (Stitch Alpine Dark Obsidian) -->
      <div
        v-if="isDropdownOpen && mountainStore.searchQuery.trim().length > 0"
        @mousedown.prevent
        class="search-suggestions-dropdown absolute left-0 right-0 top-12 z-[80] rounded-2xl bg-[#171b26]/95 backdrop-blur-xl border border-outline-variant/40 shadow-2xl overflow-hidden flex flex-col max-h-[58vh] animate-fade-in"
      >
        <!-- Dropdown Header -->
        <div class="p-3 pb-2 border-b border-outline-variant/20 flex items-center justify-between bg-surface-container-low/80">
          <div class="flex items-center gap-1.5 text-xs text-on-surface-variant">
            <span class="material-symbols-outlined text-[15px] text-primary">manage_search</span>
            <span>匹配到 <strong class="text-primary font-bold font-mono">{{ matchingSuggestions.length }}</strong> 座山峰</span>
          </div>
          <button
            type="button"
            @click="clearSearch"
            class="text-[11px] text-on-surface-variant hover:text-primary transition-colors flex items-center gap-0.5 cursor-pointer"
          >
            <span class="material-symbols-outlined text-[13px]">delete_sweep</span>
            <span>清空</span>
          </button>
        </div>

        <!-- Matching List -->
        <div v-if="matchingSuggestions.length > 0" class="overflow-y-auto divide-y divide-outline-variant/10 py-1">
          <div
            v-for="m in matchingSuggestions"
            :key="m.id"
            @click="onSelectSuggestion(m)"
            class="suggestion-item p-2.5 px-3 hover:bg-surface-container-high/60 active:bg-surface-container-high flex items-center gap-3 cursor-pointer transition-colors"
          >
            <!-- Thumbnail Photo -->
            <div class="w-11 h-11 rounded-xl overflow-hidden bg-surface-container flex-shrink-0 border border-outline-variant/20 relative">
              <img
                :src="`/assets/mountains/${m.id}.jpg`"
                @error="onImgError"
                :alt="m.name"
                class="w-full h-full object-cover"
                loading="lazy"
              />
            </div>

            <!-- Content -->
            <div class="flex-1 min-w-0">
              <div class="flex items-center justify-between gap-1">
                <h4 class="text-xs font-bold text-on-surface truncate">
                  <template v-for="(seg, idx) in highlightMatch(m.name, mountainStore.searchQuery)" :key="idx">
                    <span v-if="seg.match" class="text-primary font-bold bg-primary/25 px-0.5 rounded shadow-sm">{{ seg.text }}</span>
                    <span v-else>{{ seg.text }}</span>
                  </template>
                </h4>
                <!-- Difficulty chip -->
                <span
                  class="text-[10px] px-1.5 py-0.2 rounded-full font-mono font-medium border shrink-0"
                  :style="{ borderColor: `${getDiffColor(m.difficulty)}60`, color: getDiffColor(m.difficulty), backgroundColor: `${getDiffColor(m.difficulty)}15` }"
                >
                  {{ m.difficulty }} {{ getDiffLabel(m.difficulty) }}
                </span>
              </div>

              <!-- Subtitle details -->
              <div class="flex items-center gap-2 mt-1 text-[11px] text-on-surface-variant font-mono truncate">
                <span class="text-on-surface-variant truncate">{{ m.county_short || m.county || m.region || '成都' }}</span>
                <span>·</span>
                <span class="text-primary font-medium">{{ m.altitude_m || m.altitude }}m</span>
                <span v-if="m.distToCenterKm">·</span>
                <span v-if="m.distToCenterKm" class="text-outline">距市中心 {{ m.distToCenterKm }}km</span>
              </div>
            </div>

            <!-- Arrow -->
            <span class="material-symbols-outlined text-[16px] text-outline-variant flex-shrink-0">chevron_right</span>
          </div>
        </div>

        <!-- Empty state when no matches -->
        <div v-else class="p-6 text-center space-y-3">
          <div class="w-10 h-10 rounded-full bg-surface-container-high flex items-center justify-center text-outline mx-auto">
            <span class="material-symbols-outlined text-[20px]">search_off</span>
          </div>
          <div class="space-y-1">
            <h5 class="text-xs font-bold text-on-surface">未找到与“{{ mountainStore.searchQuery }}”匹配的山峰</h5>
            <p class="text-[11px] text-on-surface-variant">可尝试搜索山峰全名、县域名称或常用徒步标签</p>
          </div>
          <!-- Quick recommendations -->
          <div class="pt-2">
            <div class="text-[10px] text-outline mb-1.5">热门搜索推荐：</div>
            <div class="flex flex-wrap gap-1.5 justify-center">
              <button
                v-for="word in hotSearchWords"
                :key="word"
                type="button"
                @click="onQuickSearch(word)"
                class="px-2.5 py-0.5 rounded-full bg-surface-container border border-outline-variant/30 text-[10px] text-on-surface hover:text-primary hover:border-primary/40 active:scale-95 transition-all cursor-pointer"
              >
                {{ word }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Horizontal Scrollable Filter Chips -->
    <div class="flex items-center gap-2 overflow-x-auto no-scrollbar py-0.5 -mx-margin px-margin">
      <!-- Active / All Peaks Filter -->
      <button
        @click="selectAll"
        class="filter-chip flex-shrink-0 flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[12px] font-medium transition-all active:scale-95"
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
        class="filter-chip flex-shrink-0 flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[12px] font-medium transition-all active:scale-95"
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
        class="filter-chip flex-shrink-0 flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[12px] font-medium transition-all active:scale-95"
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
        class="filter-chip flex-shrink-0 flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[12px] font-medium transition-all active:scale-95"
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
        class="filter-chip flex-shrink-0 flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[12px] font-medium transition-all active:scale-95"
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
        class="filter-chip flex-shrink-0 flex items-center gap-1 px-2.5 py-1 rounded-full text-[12px] font-medium transition-all active:scale-95"
        :class="mountainStore.activeFilters.maxDrive === 4
          ? 'bg-surface-container-high border border-primary text-primary glow-primary font-semibold'
          : 'frost-glass border border-outline-variant/30 text-on-surface-variant hover:text-on-surface'"
      >
        <span class="material-symbols-outlined text-[14px]">directions_car</span>
        <span>车程 2-4h</span>
      </button>

      <!-- Sea of Clouds -->
      <button
        @click="toggleScenario('云海')"
        class="filter-chip flex-shrink-0 flex items-center gap-1 px-2.5 py-1 rounded-full text-[12px] font-medium transition-all active:scale-95"
        :class="isScenarioActive('云海')
          ? 'bg-surface-container-high border border-secondary text-secondary glow-secondary font-semibold'
          : 'frost-glass border border-outline-variant/30 text-on-surface-variant hover:text-on-surface'"
      >
        <span class="material-symbols-outlined text-[14px] text-secondary">cloud</span>
        <span>日出云海</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useMountainStore, DIFF_LABEL, DIFF_COLOR } from '@/stores/mountainStore.js';
import { useRegionStore } from '@/stores/regionStore.js';

const mountainStore = useMountainStore();
const regionStore = useRegionStore();
const emit = defineEmits(['focus', 'blur', 'mountain-select']);

const searchInputRef = ref(null);
const isDropdownOpen = ref(false);

const hotSearchWords = ['赵公山', '虹口', '青城后山', '九峰山', '巴朗山', '狮子王峰'];

const matchingSuggestions = computed(() => {
  return mountainStore.filteredMountains.slice(0, 8);
});

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

function getDiffLabel(diff) {
  return DIFF_LABEL[diff] || '轻松';
}

function getDiffColor(diff) {
  return DIFF_COLOR[diff] || '#4ade80';
}

function onImgError(e) {
  e.target.style.display = 'none';
}

function highlightMatch(text, query) {
  if (!text) return [];
  if (!query || !query.trim()) return [{ text: String(text), match: false }];
  const q = query.trim().toLowerCase();
  const t = String(text);
  const idx = t.toLowerCase().indexOf(q);
  if (idx === -1) return [{ text: t, match: false }];
  const res = [];
  if (idx > 0) res.push({ text: t.slice(0, idx), match: false });
  res.push({ text: t.slice(idx, idx + q.length), match: true });
  if (idx + q.length < t.length) res.push({ text: t.slice(idx + q.length), match: false });
  return res;
}

function onSearchInput(e) {
  mountainStore.setSearch(e.target.value);
  if (e.target.value.trim().length > 0) {
    isDropdownOpen.value = true;
  }
}

function onFocus(e) {
  if (mountainStore.searchQuery && mountainStore.searchQuery.trim().length > 0) {
    isDropdownOpen.value = true;
  }
  emit('focus', e);
}

function onBlur(e) {
  // 延迟 220ms 允许用户在手机上触发候选项的 click
  setTimeout(() => {
    isDropdownOpen.value = false;
  }, 220);
  emit('blur', e);
}

function clearSearch() {
  mountainStore.setSearch('');
  isDropdownOpen.value = false;
}

function onQuickSearch(word) {
  mountainStore.setSearch(word);
  isDropdownOpen.value = true;
}

function onSelectSuggestion(mountain) {
  mountainStore.setSearch(mountain.name);
  mountainStore.selectMountain(mountain.id);
  emit('mountain-select', mountain.id);
  isDropdownOpen.value = false;
  if (searchInputRef.value) {
    searchInputRef.value.blur();
  }
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
