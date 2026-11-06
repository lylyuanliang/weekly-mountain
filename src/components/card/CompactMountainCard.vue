<template>
  <article
    :id="`compact-mountain-card-${mountain.id}`"
    @click="handleClick"
    class="compact-mountain-card group flex items-center gap-3 p-2 h-[84px] min-h-[84px] max-h-[84px] rounded-[14px] bg-[#1c202c] border select-none cursor-pointer overflow-hidden relative"
    :class="isActive ? 'is-active border-primary glow-primary bg-[#1f2432]' : 'border-outline-variant/30 hover:border-outline-variant/60'"
  >
    <!-- Left: 68x68 Rounded Thumbnail with Fallback & Difficulty Badge -->
    <div class="relative w-[68px] h-[68px] rounded-xl overflow-hidden bg-surface-container-lowest flex-shrink-0">
      <img
        :src="currentImgSrc"
        @error="handleImgError"
        :alt="mountain.name"
        decoding="async"
        class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
      />
      <!-- Gradient overlay for text readability -->
      <div class="absolute inset-0 bg-gradient-to-t from-[#0a0e17]/80 via-transparent to-transparent"></div>

      <!-- Verified / Checked Badge (Top-Left) -->
      <span
        v-if="isChecked"
        class="absolute top-1 left-1 w-4 h-4 rounded-full bg-[#0a0e17]/90 text-primary border border-primary/50 flex items-center justify-center shadow-md"
        title="您已登顶此山峰"
      >
        <span class="material-symbols-outlined text-[11px]">verified</span>
      </span>

      <!-- Difficulty Badge (Bottom-Left) -->
      <span
        class="absolute bottom-1 left-1 px-1.5 py-0.2 rounded bg-[#0a0e17]/85 text-[10px] font-mono font-bold border backdrop-blur-sm shadow-sm"
        :class="diffBadgeClass"
      >
        {{ mountain.difficulty || 'L2' }}
      </span>
    </div>

    <!-- Center: 3-Row Telemetry & Metadata -->
    <div class="flex-1 min-w-0 flex flex-col justify-between h-[68px] py-0.5">
      <!-- Line 1: Mountain Name & Altitude -->
      <div class="flex items-center justify-between gap-1.5 leading-tight">
        <div class="flex items-center gap-1.5 min-w-0">
          <h3 class="text-[15px] font-bold text-on-surface truncate tracking-tight group-hover:text-primary transition-colors">
            {{ mountain.name }}
          </h3>
          <span
            v-if="isSearchMatched"
            class="px-1 py-0.2 rounded text-[9px] bg-primary/20 text-primary border border-primary/40 flex-shrink-0 animate-pulse font-sans"
          >
            匹配
          </span>
        </div>
        <div class="flex items-baseline gap-0.5 text-primary font-label-data-sm font-bold flex-shrink-0">
          <span>{{ nums.alt }}</span>
          <span class="text-[10px] font-normal text-primary/80">m</span>
        </div>
      </div>

      <!-- Line 2: County & Center Distance / Drive -->
      <p class="text-[11px] text-on-surface-variant flex items-center gap-1 truncate leading-tight">
        <span class="material-symbols-outlined text-[13px] text-primary/70 flex-shrink-0">location_on</span>
        <span class="truncate">{{ locationDistText }}</span>
      </p>

      <!-- Line 3: Feature Indicator Capsules -->
      <div class="flex items-center gap-1.5 overflow-hidden text-[10px]">
        <!-- Cumulative Ascent -->
        <span
          class="px-1.5 py-0.5 rounded bg-[#161d2d] text-primary border border-primary/25 font-mono flex items-center gap-0.5 flex-shrink-0"
          :title="`累计爬升 +${nums.asc}m`"
        >
          <span class="text-primary/70 text-[9px] font-sans">爬升</span>
          <span>+{{ nums.asc }}m</span>
        </span>

        <!-- Round-trip Distance -->
        <span
          class="px-1.5 py-0.5 rounded bg-[#161d2d] text-on-surface-variant border border-outline-variant/30 font-mono flex items-center gap-0.5 flex-shrink-0"
          :title="`往返里程 ${nums.dist}km`"
        >
          <span class="text-on-surface-variant/70 text-[9px] font-sans">里程</span>
          <span>{{ nums.dist }}km</span>
        </span>

        <!-- Live Weather Capsule -->
        <button
          type="button"
          @click.stop="handleWeatherClick"
          class="px-1.5 py-0.5 rounded bg-[#161d2d] text-secondary border border-secondary/30 hover:border-secondary flex items-center gap-0.5 truncate active:scale-95 transition-all flex-shrink-0 group/wx cursor-pointer"
          :title="`查看天气: ${weatherText}`"
        >
          <span class="material-symbols-outlined text-[12px] text-secondary flex-shrink-0 group-hover/wx:animate-pulse">{{ weatherIcon }}</span>
          <span class="truncate max-w-[64px]">{{ weatherText }}</span>
        </button>

        <!-- Feature Tag (e.g. 和缓步道 / 云海日出) -->
        <span
          v-if="featureTag"
          class="px-1.5 py-0.5 rounded bg-surface-container-high/60 text-on-surface-variant border border-outline-variant/20 truncate max-w-[65px] hidden xs:inline"
          :title="featureTag"
        >
          {{ featureTag }}
        </span>
      </div>
    </div>

    <!-- Right: Detail / Explore Indicator Chevron -->
    <button
      type="button"
      @click.stop="handleDetailClick"
      class="flex-shrink-0 pl-0.5 pr-1 flex items-center justify-center text-on-surface-variant/40 group-hover:text-primary active:scale-90 transition-all cursor-pointer"
      title="查看路线详情"
      aria-label="查看路线详情"
    >
      <span class="material-symbols-outlined text-[20px]">chevron_right</span>
    </button>
  </article>
</template>

<script setup>
import { ref, computed, watch } from 'vue';
import { DIFF_LABEL, useMountainStore, getMountainCoordinate, getDistanceKm } from '@/stores/mountainStore.js';
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

const isChecked = computed(() => checkinStore.isDone(props.mountain?.id));

const diffBadgeClass = computed(() => {
  const d = props.mountain?.difficulty;
  if (d === 'L1') return 'text-primary border-primary/30';
  if (d === 'L2') return 'text-secondary border-secondary/30';
  if (d === 'L3') return 'text-tertiary border-tertiary/30';
  return 'text-error border-error/30';
});

const shortCounty = computed(() => {
  const raw = props.mountain?.county || props.mountain?.region || '';
  let clean = raw.split(/[（(]/)[0].trim();
  clean = clean.replace(/^四川省?/, '');
  return clean || raw || '成都周边';
});

const driveText = computed(() => {
  const h = props.mountain?.drive_hours;
  if (h) return `${h}h`;
  return '2.5h';
});

const computedDistKm = computed(() => {
  if (props.mountain?.distToCenterKm !== undefined && props.mountain?.distToCenterKm !== null) {
    return Math.round(props.mountain.distToCenterKm);
  }
  const curCenter = regionStore.currentRegion?.center || { lng: 104.066, lat: 30.657 };
  const coord = getMountainCoordinate(props.mountain, mountainStore.waypoints);
  return Math.round(getDistanceKm(curCenter.lat, curCenter.lng, coord.lat, coord.lng));
});

const locationDistText = computed(() => {
  const parts = [shortCounty.value];
  if (computedDistKm.value) {
    parts.push(`距中心 ${computedDistKm.value}km (${driveText.value})`);
  } else {
    parts.push(driveText.value);
  }
  return parts.join(' · ');
});

const featureTag = computed(() => {
  const tags = props.mountain?.tags;
  if (Array.isArray(tags) && tags.length > 0) {
    const priority = ['和缓步道', '云海日出', '雪山远眺', '森林瀑布', '红叶彩林', '免费徒步', '近郊一日', '日出日落'];
    for (const p of priority) {
      if (tags.includes(p)) return p;
    }
    return tags[0];
  }
  return null;
});

// Weather / Live condition preview
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

  const w = String(props.mountain?.weather_keywords || props.mountain?.tags || '');
  if (w.includes('雪') || w.includes('冰')) return 'ac_unit';
  if (w.includes('云海') || w.includes('雾')) return 'cloud';
  if (w.includes('雨')) return 'rainy';
  return 'sunny';
});

const weatherText = computed(() => {
  if (cachedWeather.value?.data?.temperature_2m_max?.[0] !== undefined) {
    const max = Math.round(cachedWeather.value.data.temperature_2m_max[0]);
    const min = Math.round(cachedWeather.value.data.temperature_2m_min[0]);
    return `${max}°/${min}°`;
  }

  const kw = props.mountain?.weather_keywords;
  if (Array.isArray(kw) && kw.length > 0) {
    for (const item of kw) {
      const str = String(item).trim();
      if (str.length > 0 && str.length <= 4) return str;
      const match = str.match(/(晴天|多云|阴天|雨雪|积雪|大风|云海|星空|日照金山)/);
      if (match) return match[0];
    }
  }
  if (props.mountain?.altitude_m > 4000) return '高山晴冷';
  if (props.mountain?.altitude_m > 3000) return '高海拔';
  return '适宜徒步';
});

function handleWeatherClick() {
  emit('weather', props.mountain);
}

function handleClick() {
  emit('select', props.mountain?.id);
}

function handleDetailClick() {
  emit('detail', props.mountain);
}

// Fallback SVG
const fallbackSvg = computed(() => {
  const title = encodeURIComponent(props.mountain?.name || 'Alpine Peak');
  const alt = nums.value.alt || 0;
  return `data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="140" height="140" viewBox="0 0 140 140"><defs><linearGradient id="g" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="%23181b25"/><stop offset="50%" stop-color="%23262a34"/><stop offset="100%" stop-color="%230f131c"/></linearGradient></defs><rect width="100%" height="100%" fill="url(%23g)"/><path d="M-10 140 L45 50 L85 110 L115 65 L150 140 Z" fill="%234edea3" opacity="0.2"/><path d="M20 140 L75 75 L125 140 Z" fill="%234cd7f6" opacity="0.25"/><text x="50%" y="45%" dominant-baseline="middle" text-anchor="middle" fill="%23dfe2ef" font-family="Plus Jakarta Sans, sans-serif" font-size="12" font-weight="bold">${title}</text><text x="50%" y="65%" dominant-baseline="middle" text-anchor="middle" fill="%234edea3" font-family="JetBrains Mono, monospace" font-size="10">${alt}M</text></svg>`;
});

const currentImgSrc = ref(
  props.mountain?.photo_spots?.[0]?.url ||
  `assets/mountains/${props.mountain?.id}.jpg`
);

watch(
  () => props.mountain?.id,
  () => {
    currentImgSrc.value =
      props.mountain?.photo_spots?.[0]?.url ||
      `assets/mountains/${props.mountain?.id}.jpg`;
  }
);

function handleImgError() {
  currentImgSrc.value = fallbackSvg.value;
}
</script>

<style scoped>
.compact-mountain-card {
  box-sizing: border-box;
  transform: translateZ(0);
  transition: border-color 0.24s cubic-bezier(0.16, 1, 0.3, 1),
              background-color 0.24s cubic-bezier(0.16, 1, 0.3, 1),
              box-shadow 0.24s cubic-bezier(0.16, 1, 0.3, 1),
              transform 0.24s cubic-bezier(0.16, 1, 0.3, 1);
}

.compact-mountain-card.is-active {
  border-color: #4edea3 !important;
  background-color: #1f2533 !important;
  box-shadow: 0 0 0 1px rgba(78, 222, 163, 0.4), 0 4px 18px rgba(78, 222, 163, 0.18) !important;
}
</style>
