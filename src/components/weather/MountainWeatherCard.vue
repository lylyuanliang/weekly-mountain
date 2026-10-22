<template>
  <div class="mountain-weather-card rounded-2xl bg-surface-container-high/90 border border-outline-variant/30 p-3.5 space-y-3">
    <!-- Header with Point Info & Refresh Button -->
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-2 overflow-hidden">
        <span class="material-symbols-outlined text-secondary text-[20px] flex-shrink-0">routine</span>
        <div class="overflow-hidden">
          <div class="flex items-center gap-1.5 flex-wrap">
            <span class="text-body-sm font-bold text-on-surface truncate">
              {{ weatherData?.point?.name || mountain?.name }}
            </span>
            <span
              v-if="weatherData?.point?.alt"
              class="text-[11px] font-mono px-1.5 py-0.2 rounded bg-surface-container-lowest text-primary border border-primary/20"
            >
              {{ weatherData.point.alt }}m
            </span>
          </div>
          <p class="text-[10px] text-on-surface-variant font-mono mt-0.5">
            {{ weatherData ? `更新于 ${weatherData.updateTimeStr}` : '7 天数值气象预报' }}
          </p>
        </div>
      </div>

      <button
        type="button"
        @click="loadWeather(true)"
        :disabled="loading"
        class="flex items-center gap-1 px-2.5 py-1 rounded-full bg-surface-container text-body-sm text-secondary hover:text-primary active:scale-95 border border-secondary/30 transition-all flex-shrink-0 disabled:opacity-50"
        title="刷新实时气象"
      >
        <span
          class="material-symbols-outlined text-[15px]"
          :class="{ 'animate-spin': loading }"
        >
          refresh
        </span>
        <span class="text-[12px] font-medium">{{ loading ? '更新中' : '刷新' }}</span>
      </button>
    </div>

    <!-- Loading Skeleton -->
    <div v-if="loading && !weatherData" class="py-6 flex flex-col items-center justify-center gap-2 text-on-surface-variant">
      <span class="material-symbols-outlined text-[28px] text-primary animate-spin">progress_activity</span>
      <p class="text-caption font-mono animate-pulse">正在获取高精度未来 7 天气象数据…</p>
    </div>

    <!-- Error State with Retry -->
    <div v-else-if="error" class="p-3 rounded-xl bg-error-container/20 border border-error/30 text-on-error-container space-y-2">
      <div class="flex items-center gap-2">
        <span class="material-symbols-outlined text-error text-[18px]">wifi_off</span>
        <p class="text-body-sm text-error font-medium">{{ error }}</p>
      </div>
      <button
        type="button"
        @click="loadWeather(true)"
        class="px-3 py-1 rounded-lg bg-surface-container text-body-sm font-medium border border-outline-variant hover:border-primary active:scale-95 text-on-surface"
      >
        重试获取
      </button>
    </div>

    <!-- 7-Day Weather Stream -->
    <template v-else-if="weatherData">
      <div class="flex gap-2 overflow-x-auto no-scrollbar -mx-1 px-1 py-1">
        <div
          v-for="(day, idx) in weatherData.days"
          :key="day.date"
          class="flex-shrink-0 w-[78px] p-2 rounded-xl flex flex-col items-center text-center transition-all border"
          :class="[
            idx === 0 ? 'bg-surface-container-lowest/80 border-primary/40 ring-1 ring-primary/20' : 'bg-surface-container/60 border-outline-variant/20',
            day.isBad ? 'border-error/40 bg-error-container/10' : ''
          ]"
        >
          <!-- Day & Date -->
          <span class="text-[11px] font-semibold text-on-surface" :class="{ 'text-primary font-bold': idx === 0 }">
            {{ idx === 0 ? '今天' : day.weekday }}
          </span>
          <span class="text-[9.5px] font-mono text-on-surface-variant mb-1">
            {{ day.monthDay }}
          </span>

          <!-- Weather Icon -->
          <span class="text-[22px] my-0.5 select-none leading-none" :title="day.text">{{ day.icon }}</span>

          <!-- Weather Text -->
          <span class="text-[11px] font-medium text-on-surface truncate w-full mt-0.5">
            {{ day.text }}
          </span>

          <!-- Max / Min Temp -->
          <div class="text-[12px] font-mono font-bold text-primary mt-1">
            {{ day.maxTemp !== null ? `${day.maxTemp}°` : '—' }}
            <span class="text-on-surface-variant text-[10px] font-normal font-mono">
              / {{ day.minTemp !== null ? `${day.minTemp}°` : '—' }}
            </span>
          </div>

          <!-- Rain Probability -->
          <div
            v-if="day.precipProb !== null"
            class="mt-1 px-1 py-0.2 rounded text-[10px] font-mono flex items-center gap-0.5"
            :class="day.isBad ? 'bg-error-container/40 text-error font-bold' : 'bg-surface-container-high text-secondary'"
          >
            <span>💧</span>
            <span>{{ day.precipProb }}%</span>
          </div>
        </div>
      </div>

      <!-- Outdoor Safety & Hiking Advisory -->
      <div class="space-y-1.5 pt-1">
        <div
          v-for="(w, wi) in weatherData.warnings"
          :key="`warn-${wi}`"
          class="p-2 rounded-xl border flex items-start gap-2 text-caption leading-relaxed"
          :class="{
            'bg-error-container/20 border-error/40 text-error': w.type === 'danger',
            'bg-surface-container-low/80 border-secondary/30 text-secondary': w.type === 'ice',
            'bg-tertiary-container/20 border-tertiary/30 text-tertiary-fixed': w.type === 'wind',
            'bg-primary-container/20 border-primary/30 text-primary': w.type === 'success',
            'bg-surface-container border-outline-variant text-on-surface-variant': w.type === 'warn'
          }"
        >
          <span class="material-symbols-outlined text-[16px] flex-shrink-0 mt-0.5">{{ w.icon }}</span>
          <span>{{ w.text }}</span>
        </div>
      </div>

      <!-- Data Source Footnote -->
      <p class="text-[10px] text-on-surface-variant font-mono">
        {{ weatherData.source }} · 高海拔山顶体感气温通常较预报低 3~6℃
      </p>
    </template>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue';
import { fetchMountainWeather } from '@/services/weatherService.js';

const props = defineProps({
  mountain: {
    type: Object,
    required: true
  },
  autoLoad: {
    type: Boolean,
    default: true
  }
});

const loading = ref(false);
const error = ref(null);
const weatherData = ref(null);

async function loadWeather(force = false) {
  if (!props.mountain) return;
  loading.value = true;
  error.value = null;

  try {
    const data = await fetchMountainWeather(props.mountain, force);
    weatherData.value = data;
  } catch (err) {
    error.value = err.message || '获取天气预报失败';
  } finally {
    loading.value = false;
  }
}

watch(
  () => props.mountain?.id,
  (newId) => {
    if (newId && props.autoLoad) {
      loadWeather(false);
    }
  }
);

onMounted(() => {
  if (props.autoLoad) {
    loadWeather(false);
  }
});

defineExpose({
  loadWeather,
  weatherData
});
</script>

<style scoped>
.no-scrollbar::-webkit-scrollbar {
  display: none;
}
.no-scrollbar {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
</style>
