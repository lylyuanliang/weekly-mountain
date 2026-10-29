<template>
  <article
    :id="`mountain-card-${mountain.id}`"
    @click="$emit('select', mountain.id)"
    class="hero-mountain-card flex-shrink-0 w-[84vw] max-w-[340px] snap-center rounded-2xl bg-[#1c202c] border overflow-hidden shadow-2xl relative group"
    :class="isActive ? 'border-primary ring-2 ring-primary/40 glow-primary scale-[1.01]' : 'border-outline-variant/40 hover:border-outline-variant/70'"
  >
    <!-- Mountain Hero Image -->
    <div class="relative h-36 w-full overflow-hidden bg-surface-container-lowest">
      <img
        :src="currentImgSrc"
        @error="handleImgError"
        :alt="mountain.name"
        decoding="async"
        class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
      />
      <!-- Gradient Shade -->
      <div class="absolute inset-0 bg-gradient-to-t from-[#1c202c] via-[#1c202c]/40 to-transparent"></div>

      <!-- Badges on Top-Left of Hero Image -->
      <div class="absolute top-2 left-2 flex items-center gap-1.5 z-10">
        <!-- Altitude Badge -->
        <span class="px-2 py-0.5 rounded-full bg-[#0a0e17]/90 text-label-data-sm font-label-data-sm text-primary border border-primary/30 flex items-center gap-1">
          <span class="w-1.5 h-1.5 rounded-full bg-primary shadow-[0_0_4px_#4edea3]"></span>
          {{ nums.alt }}m
        </span>

        <!-- Difficulty Badge -->
        <span
          class="px-2 py-0.5 rounded-full bg-[#0a0e17]/90 text-label-data-sm font-label-data-sm border"
          :class="diffBadgeClass"
        >
          {{ mountain.difficulty || 'L2' }} {{ diffLabel }}
        </span>

        <!-- Search Match Badge -->
        <span
          v-if="isSearchMatched"
          class="px-2 py-0.5 rounded-full bg-primary/25 text-label-data-sm font-label-data-sm text-primary border border-primary/50 flex items-center gap-1 shadow-[0_0_8px_rgba(78,222,163,0.3)] animate-pulse"
        >
          <span class="material-symbols-outlined text-[12px]">search</span>
          <span>搜索匹配</span>
        </span>
      </div>

      <!-- Live Condition / Weather Chip on Top-Right -->
      <div class="absolute top-2 right-2 z-10 flex items-center gap-1 max-w-[145px]">
        <!-- Summit / Check-in Badge -->
        <span
          v-if="isChecked"
          class="px-2 py-0.5 rounded-full bg-[#0a0e17]/90 text-label-data-sm font-label-data-sm text-primary border border-primary/40 flex items-center gap-1 flex-shrink-0 shadow-md backdrop-blur-sm"
          title="您已登顶此山峰"
        >
          <span class="material-symbols-outlined text-[13px] fill text-primary">verified</span>
          <span class="font-bold">已登顶</span>
        </span>
        <button
          type="button"
          @click.stop="handleWeatherClick"
          class="px-2 py-0.5 rounded-full bg-[#0a0e17]/90 text-label-data-sm font-label-data-sm text-secondary-fixed border border-secondary/40 hover:border-secondary flex items-center gap-1 truncate active:scale-95 transition-all shadow-md group/wx"
          title="点击查看未来 7 天实况天气"
        >
          <span class="material-symbols-outlined text-[14px] text-secondary flex-shrink-0 group-hover/wx:animate-pulse">{{ weatherIcon }}</span>
          <span class="truncate">{{ weatherText }}</span>
        </button>
      </div>

      <!-- Mountain Title over Image gradient -->
      <div class="absolute bottom-2 left-3 right-3 z-10">
        <div class="flex items-baseline justify-between gap-1.5">
          <h3 class="text-headline-md font-headline-md text-on-surface font-extrabold tracking-tight truncate">
            {{ mountain.name }}
          </h3>
          <span
            v-if="mountain.distToCenterKm !== undefined"
            class="px-1.5 py-0.5 rounded text-[10px] font-mono font-semibold bg-[#0a0e17]/85 text-primary border border-primary/30 shrink-0"
            :title="`距${regionStore.currentRegion.driveCenter || '市中心'}直线距离 ${mountain.distToCenterKm}km`"
          >
            距中心 {{ mountain.distToCenterKm }}km
          </span>
        </div>
        <p class="text-caption font-caption text-on-surface-variant flex items-center gap-1 mt-0.5">
          <span class="material-symbols-outlined text-[13px] text-primary">location_on</span>
          <span class="truncate">{{ locationText }}</span>
        </p>
      </div>
    </div>

    <!-- Hiking Telemetry Grid (4-column Equal Grid) -->
    <div class="px-2 py-1.5 grid grid-cols-4 gap-0.5 border-y border-outline-variant/20 bg-[#161922] text-center">
      <div class="flex flex-col">
        <span class="text-[9.5px] font-caption text-on-surface-variant uppercase tracking-wider">最高海拔</span>
        <span class="text-label-data-sm font-label-data-sm text-primary font-bold mt-0.5">{{ nums.alt }}m</span>
      </div>
      <div class="flex flex-col border-l border-outline-variant/20">
        <span class="text-[9.5px] font-caption text-on-surface-variant uppercase tracking-wider">累计爬升</span>
        <span class="text-label-data-sm font-label-data-sm text-primary font-semibold mt-0.5">+{{ nums.asc }}m</span>
      </div>
      <div class="flex flex-col border-l border-outline-variant/20">
        <span class="text-[9.5px] font-caption text-on-surface-variant uppercase tracking-wider">往返里程</span>
        <span class="text-label-data-sm font-label-data-sm text-on-surface font-semibold mt-0.5">{{ nums.dist }}km</span>
      </div>
      <div class="flex flex-col border-l border-outline-variant/20">
        <span class="text-[9.5px] font-caption text-on-surface-variant uppercase tracking-wider">距中心/车程</span>
        <span
          class="telemetry-dist-drive text-label-data-sm font-label-data-sm text-secondary font-semibold mt-0.5 truncate"
          :title="`距${regionStore.currentRegion.driveCenter || '市中心'}直线距离约 ${mountain.distToCenterKm || 0}km · 单程车程约 ${driveText}`"
        >
          {{ mountain.distToCenterKm ? Math.round(mountain.distToCenterKm) + 'km · ' : '' }}{{ driveText }}
        </span>
      </div>
    </div>

    <!-- Action Buttons Footer -->
    <div class="px-2.5 py-2 flex items-center gap-2">
      <!-- Elevation / Detail Secondary Button -->
      <button
        type="button"
        @click.stop="$emit('detail', mountain)"
        class="flex-1 py-1.5 px-2 rounded-xl bg-[#161d2d] border border-secondary/40 text-secondary text-body-sm font-semibold flex items-center justify-center gap-1 active:scale-95 hover:border-secondary transition-all"
      >
        <span class="material-symbols-outlined text-[17px]">explore</span>
        <span>路线详情</span>
      </button>

      <!-- Add to Plan Primary Action Button -->
      <button
        type="button"
        @click.stop="handleAddToPlan"
        class="flex-1 py-1.5 px-2.5 rounded-xl bg-gradient-to-r from-primary-container to-secondary-container text-surface-container-lowest font-headline-md text-body-sm font-bold flex items-center justify-center gap-1 glow-primary active:scale-95 transition-all"
      >
        <span class="material-symbols-outlined text-[17px]">{{ isPlanned ? 'check' : 'add_circle' }}</span>
        <span>{{ isPlanned ? '已在计划' : '加入周计划' }}</span>
      </button>
    </div>
  </article>
</template>

<script setup>
import { ref, computed } from 'vue';
import { DIFF_LABEL, useMountainStore } from '@/stores/mountainStore.js';
import { useCheckinStore, derivedNums } from '@/stores/checkinStore.js';
import { usePlanStore } from '@/stores/planStore.js';
import { useRegionStore } from '@/stores/regionStore.js';
import { getWeatherCache } from '@/services/weatherService.js';

const props = defineProps({
  mountain: {
    type: Object,
    required: true
  },
  isActive: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits(['select', 'detail', 'weather']);

const checkinStore = useCheckinStore();
const planStore = usePlanStore();
const regionStore = useRegionStore();
const mountainStore = useMountainStore();

const isSearchMatched = computed(() => {
  return Boolean(mountainStore.searchQuery && mountainStore.searchQuery.trim().length > 0);
});

const nums = computed(() => derivedNums(props.mountain));

const isChecked = computed(() => checkinStore.isDone(props.mountain.id));

const isPlanned = computed(() => {
  return planStore.plans.some((w) => (w.items || []).includes(props.mountain.id));
});

const diffLabel = computed(() => {
  return DIFF_LABEL[props.mountain.difficulty] || '';
});

const diffBadgeClass = computed(() => {
  const d = props.mountain.difficulty;
  if (d === 'L1') return 'text-primary border-primary/30';
  if (d === 'L2') return 'text-secondary border-secondary/30';
  if (d === 'L3') return 'text-tertiary border-tertiary/30';
  return 'text-error border-error/30';
});

const driveText = computed(() => {
  const h = props.mountain.drive_hours;
  if (h) return `${h}h`;
  return '2.5h';
});

const locationText = computed(() => {
  const m = props.mountain;
  if (m.county && m.region) return `${m.region} · ${m.county}`;
  return m.county || m.region || '四川西部';
});

// Weather / Condition preview with live cache check
const cachedWeather = computed(() => {
  return getWeatherCache(props.mountain?.id);
});

const weatherIcon = computed(() => {
  if (cachedWeather.value?.data?.weather_code?.[0] !== undefined) {
    const code = cachedWeather.value.data.weather_code[0];
    if (code >= 71 && code <= 86) return 'ac_unit';
    if (code >= 51 && code <= 67) return 'rainy';
    if (code >= 95) return 'thunderstorm';
    if (code >= 1 && code <= 3) return 'cloud';
    if (code === 45 || code === 48) return 'foggy';
    return 'sunny';
  }

  const w = String(props.mountain.weather_keywords || props.mountain.tags || '');
  if (w.includes('雪') || w.includes('冰')) return 'ac_unit';
  if (w.includes('云海') || w.includes('雾')) return 'cloud';
  if (w.includes('雨')) return 'rainy';
  return 'sunny';
});

const weatherText = computed(() => {
  if (cachedWeather.value?.data?.temperature_2m_max?.[0] !== undefined) {
    const max = Math.round(cachedWeather.value.data.temperature_2m_max[0]);
    const min = Math.round(cachedWeather.value.data.temperature_2m_min[0]);
    return `${max}°/${min}° 实况`;
  }

  const kw = props.mountain.weather_keywords;
  if (Array.isArray(kw) && kw.length > 0) {
    for (const item of kw) {
      const str = String(item).trim();
      if (str.length > 0 && str.length <= 6) return str;
      const match = str.match(/(晴天|多云|阴天|雨雪|积雪|大风|云海|星空|日照金山)/);
      if (match) return match[0];
    }
  }
  if (props.mountain.altitude_m > 4000) return '高山晴冷';
  if (props.mountain.altitude_m > 3000) return '高海拔';
  return '适宜徒步';
});

function handleWeatherClick() {
  emit('weather', props.mountain);
}

// Image fallback handling
const fallbackSvg = computed(() => {
  const title = encodeURIComponent(props.mountain.name || 'Alpine Peak');
  return `data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="400" height="220" viewBox="0 0 400 220"><defs><linearGradient id="g" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="%23181b25"/><stop offset="50%" stop-color="%23262a34"/><stop offset="100%" stop-color="%230f131c"/></linearGradient></defs><rect width="100%" height="100%" fill="url(%23g)"/><path d="M-20 220 L120 70 L220 180 L310 90 L420 220 Z" fill="%234edea3" opacity="0.15"/><path d="M60 220 L210 110 L340 220 Z" fill="%234cd7f6" opacity="0.2"/><text x="50%" y="45%" dominant-baseline="middle" text-anchor="middle" fill="%2386948a" font-family="Plus Jakarta Sans, sans-serif" font-size="16" font-weight="bold">${title}</text><text x="50%" y="65%" dominant-baseline="middle" text-anchor="middle" fill="%234edea3" font-family="JetBrains Mono, monospace" font-size="12">ALPINE TOPO · ${nums.value.alt}M</text></svg>`;
});

const currentImgSrc = ref(
  props.mountain.photo_spots?.[0]?.url ||
  `assets/mountains/${props.mountain.id}.jpg`
);

function handleImgError() {
  currentImgSrc.value = fallbackSvg.value;
}

function handleAddToPlan() {
  if (isPlanned.value) {
    planStore.removeFromPlan(props.mountain.id);
  } else {
    planStore.addToPlan(props.mountain.id);
  }
}
</script>
