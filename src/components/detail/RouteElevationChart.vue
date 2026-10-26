<template>
  <div class="route-elevation-chart w-full flex flex-col gap-4 select-none">
    <!-- Top Telemetry Ribbon (4 Metrics Bento) -->
    <div class="grid grid-cols-4 gap-2 p-3 rounded-2xl bg-surface-container/70 border border-outline-variant/30 text-center">
      <div class="flex flex-col">
        <span class="text-[10px] font-caption text-on-surface-variant uppercase tracking-wider">起点海拔</span>
        <span class="text-label-data-sm font-label-data-sm text-on-surface font-bold mt-0.5">
          {{ startAlt }}m
        </span>
      </div>
      <div class="flex flex-col border-l border-outline-variant/20">
        <span class="text-[10px] font-caption text-on-surface-variant uppercase tracking-wider">峰顶最高</span>
        <span class="text-label-data-sm font-label-data-sm text-primary font-bold mt-0.5">
          {{ peakAlt }}m
        </span>
      </div>
      <div class="flex flex-col border-l border-outline-variant/20">
        <span class="text-[10px] font-caption text-on-surface-variant uppercase tracking-wider">垂直落差</span>
        <span class="text-label-data-sm font-label-data-sm text-primary font-bold mt-0.5">
          +{{ elevationGain }}m
        </span>
      </div>
      <div class="flex flex-col border-l border-outline-variant/20">
        <span class="text-[10px] font-caption text-on-surface-variant uppercase tracking-wider">单程/往返</span>
        <span class="text-label-data-sm font-label-data-sm text-secondary font-bold mt-0.5">
          {{ totalKm }}km
        </span>
      </div>
    </div>

    <!-- Interactive SVG Elevation Profile Chart -->
    <div class="relative w-full rounded-2xl bg-surface-container/90 border border-outline-variant/30 p-3 overflow-hidden shadow-inner">
      <div class="flex items-center justify-between mb-2 px-1">
        <div class="flex items-center gap-1.5">
          <span class="material-symbols-outlined text-[18px] text-primary">show_chart</span>
          <span class="text-body-sm font-semibold text-on-surface">路线高程走势剖面</span>
        </div>
        <div class="flex items-center gap-2 text-[11px] font-caption text-on-surface-variant">
          <span class="flex items-center gap-1">
            <span class="w-2 h-2 rounded-full bg-primary inline-block"></span>
            已核准
          </span>
          <span class="flex items-center gap-1">
            <span class="w-2 h-2 rounded-full bg-tertiary-fixed-dim inline-block"></span>
            估算点
          </span>
        </div>
      </div>

      <!-- SVG Drawing -->
      <div class="relative w-full aspect-[2.4/1] min-h-[160px]">
        <svg
          ref="svgRef"
          class="w-full h-full overflow-visible touch-none cursor-crosshair"
          :viewBox="`0 0 ${svgWidth} ${svgHeight}`"
          preserveAspectRatio="none"
          @mousemove="handleChartPointerMove"
          @mouseleave="handleChartPointerLeave"
          @touchstart.passive="handleChartPointerStart"
          @touchmove.passive="handleChartPointerMove"
        >
          <defs>
            <!-- Elevation Gradient Fill -->
            <linearGradient id="elevationGrad" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stop-color="var(--acc-aurora, #4edea3)" stop-opacity="0.38" />
              <stop offset="60%" stop-color="var(--acc-aurora, #4edea3)" stop-opacity="0.10" />
              <stop offset="100%" stop-color="var(--acc-aurora, #4edea3)" stop-opacity="0.0" />
            </linearGradient>

            <!-- Glow Filter -->
            <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
              <feGaussianBlur stdDeviation="3" result="blur" />
              <feMerge>
                <feMergeNode in="blur" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
          </defs>

          <!-- Horizontal Grid Lines & Labels -->
          <g class="grid-lines" opacity="0.3">
            <line
              v-for="(grid, idx) in gridYLines"
              :key="'grid-line-' + idx"
              :x1="padding.left"
              :y1="grid.y"
              :x2="svgWidth - padding.right"
              :y2="grid.y"
              stroke="rgba(255,255,255,0.18)"
              stroke-dasharray="3,3"
              stroke-width="1"
            />
          </g>

          <g class="grid-labels">
            <text
              v-for="(grid, idx) in gridYLines"
              :key="'grid-lbl-' + idx"
              :x="padding.left - 6"
              :y="grid.y + 3.5"
              fill="rgba(187, 202, 191, 0.7)"
              font-family="var(--font-data, monospace)"
              font-size="9"
              text-anchor="end"
            >
              {{ grid.alt }}m
            </text>
          </g>

          <!-- Elevation Area Fill -->
          <path
            v-if="chartPoints.length > 1"
            :d="areaPath"
            fill="url(#elevationGrad)"
          />

          <!-- Elevation Main Line -->
          <path
            v-if="chartPoints.length > 1"
            :d="linePath"
            fill="none"
            stroke="var(--acc-aurora, #4edea3)"
            stroke-width="2.5"
            stroke-linecap="round"
            stroke-linejoin="round"
            filter="url(#glow)"
          />

          <!-- Active Probe Vertical Guideline -->
          <line
            v-if="activeChartPoint"
            :x1="activeChartPoint.x"
            :y1="padding.top"
            :x2="activeChartPoint.x"
            :y2="svgHeight - padding.bottom"
            stroke="var(--acc-aurora, #4edea3)"
            stroke-width="1.2"
            stroke-dasharray="2,2"
            opacity="0.8"
          />

          <!-- Waypoint Marker Nodes -->
          <g
            v-for="(pt, idx) in chartPoints"
            :key="`node-${idx}`"
            class="cursor-pointer group"
            @click.stop="selectWaypoint(idx)"
          >
            <!-- Outer Glow / Hit Area -->
            <circle
              :cx="pt.x"
              :cy="pt.y"
              r="14"
              fill="transparent"
            />
            <!-- Outer Halo Ring -->
            <circle
              :cx="pt.x"
              :cy="pt.y"
              :r="activeWaypointIndex === idx ? 7 : 4.5"
              :fill="pt.unc ? '#1c1f29' : '#0f131c'"
              :stroke="pt.unc ? 'var(--acc-gold, #ffb95f)' : 'var(--acc-aurora, #4edea3)'"
              :stroke-width="activeWaypointIndex === idx ? 2.5 : 1.8"
              class="transition-all duration-200"
            />
            <!-- Inner Center Dot -->
            <circle
              :cx="pt.x"
              :cy="pt.y"
              :r="activeWaypointIndex === idx ? 3.5 : 2"
              :fill="pt.unc ? 'var(--acc-gold, #ffb95f)' : 'var(--acc-aurora, #4edea3)'"
            />

            <!-- Active Waypoint Beacon Ring (Static Crisp Vector, 0 CPU / 0 Battery / 0 Heat) -->
            <circle
              v-if="activeWaypointIndex === idx"
              :cx="pt.x"
              :cy="pt.y"
              r="9"
              fill="none"
              :stroke="pt.unc ? 'var(--acc-gold, #ffb95f)' : 'var(--acc-aurora, #4edea3)'"
              stroke-width="1.8"
              opacity="0.85"
              stroke-dasharray="2,2"
              class="pointer-events-none"
            />

            <!-- Top Seq Badge on Peak or Key Nodes -->
            <text
              v-if="idx === 0 || idx === chartPoints.length - 1 || pt.alt_m === peakAlt || activeWaypointIndex === idx"
              :x="pt.x"
              :y="pt.y - 9"
              fill="var(--text-primary, #dfe2ef)"
              font-family="var(--font-data, monospace)"
              font-size="8.5"
              font-weight="bold"
              text-anchor="middle"
            >
              #{{ pt.seq }}
            </text>
          </g>
        </svg>

        <!-- Active Waypoint Popup Tooltip -->
        <div
          v-if="activeWaypoint"
          class="absolute top-2 right-2 px-2.5 py-1.5 rounded-lg frost-glass-highlight border border-primary/40 shadow-lg text-left pointer-events-none max-w-[210px] z-10"
        >
          <div class="flex items-center gap-1.5">
            <span class="w-1.5 h-1.5 rounded-full bg-primary"></span>
            <span class="text-caption font-semibold text-primary truncate">#{{ activeWaypoint.seq }} {{ activeWaypoint.name }}</span>
          </div>
          <div class="text-[10px] font-caption text-on-surface-variant mt-0.5 font-mono">
            海拔 {{ activeWaypoint.alt_m }}m · 累计 {{ activeWaypoint.km }}km
          </div>
        </div>
      </div>
    </div>

    <!-- Waypoint Sequence Detailed Cards (Timeline List) -->
    <div class="waypoints-container flex flex-col gap-2.5">
      <div class="flex items-center justify-between px-1">
        <h4 class="text-body-md font-bold text-on-surface flex items-center gap-1.5">
          <span class="material-symbols-outlined text-[18px] text-secondary">alt_route</span>
          <span>全线 GPS 打卡地标序列 ({{ mountainWaypoints.length }} 处)</span>
        </h4>
        <span class="text-caption text-on-surface-variant font-mono">
          {{ verifiedCount }} 已核准 / {{ unverifiedCount }} 估算
        </span>
      </div>

      <div class="space-y-2">
        <div
          v-for="(wp, index) in mountainWaypoints"
          :key="`wp-${index}`"
          :id="`waypoint-${index}`"
          class="waypoint-item relative p-3 rounded-2xl border transition-all duration-200 cursor-pointer"
          :class="activeWaypointIndex === index
            ? 'bg-surface-container-high border-primary/60 glow-primary'
            : 'bg-surface-container/60 border-outline-variant/30 hover:border-outline-variant/60'"
          @click="selectWaypoint(index)"
        >
          <div class="flex items-start justify-between gap-2">
            <!-- Left: Seq Pill & Name -->
            <div class="flex items-center gap-2">
              <span
                class="w-6 h-6 rounded-full flex items-center justify-center text-[11px] font-bold font-mono border"
                :class="wp.unc
                  ? 'bg-tertiary-fixed-dim/20 text-tertiary-fixed-dim border-tertiary/40'
                  : 'bg-primary/20 text-primary border-primary/40'"
              >
                {{ wp.seq || index + 1 }}
              </span>
              <div>
                <h5 class="text-body-sm font-bold text-on-surface leading-tight">
                  {{ wp.name }}
                </h5>
                <span v-if="wp.route_name" class="text-[10px] text-on-surface-variant">
                  {{ wp.route_name }}
                </span>
              </div>
            </div>

            <!-- Right: Altitude & Verification Badge -->
            <div class="flex flex-col items-end gap-1 flex-shrink-0">
              <span class="text-label-data-sm font-label-data-sm text-primary font-bold">
                {{ wp.alt_m }}m
              </span>
              <span
                class="px-1.5 py-0.5 rounded text-[10px] font-mono border"
                :class="wp.unc
                  ? 'bg-amber-500/10 text-amber-300 border-amber-500/30'
                  : 'bg-emerald-500/10 text-emerald-300 border-emerald-500/30'"
              >
                {{ wp.unc ? '⚠ 区间估算' : '✓ 已核准 GPS' }}
              </span>
            </div>
          </div>

          <!-- Mid Info: Telemetry Details -->
          <div class="mt-2 pt-2 border-t border-outline-variant/20 flex flex-wrap items-center gap-x-4 gap-y-1 text-[11px] font-mono text-on-surface-variant">
            <span class="flex items-center gap-1">
              <span class="material-symbols-outlined text-[13px] text-secondary">straighten</span>
              距离起点: {{ wp.km }}km
            </span>
            <span class="flex items-center gap-1">
              <span class="material-symbols-outlined text-[13px] text-primary">my_location</span>
              {{ formatCoord(wp.lat) }}, {{ formatCoord(wp.lng) }}
            </span>
          </div>

          <!-- Note Content -->
          <p v-if="wp.note" class="mt-1.5 text-body-sm text-on-surface-variant leading-relaxed bg-surface-container-low/50 p-2 rounded-xl border border-outline-variant/15 text-[12px]">
            {{ wp.note }}
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onUnmounted } from 'vue';
import waypointsData from '@/data/waypoints.json' with { type: 'json' };

const props = defineProps({
  mountain: {
    type: Object,
    required: true
  },
  waypoints: {
    type: Array,
    default: null
  }
});

const emit = defineEmits(['probe-waypoint', 'clear-probe']);

const svgRef = ref(null);
const activeWaypointIndex = ref(0);

const mountainWaypoints = computed(() => {
  if (Array.isArray(props.waypoints) && props.waypoints.length > 0) {
    return props.waypoints;
  }
  if (props.mountain?.id && waypointsData[props.mountain.id]) {
    return waypointsData[props.mountain.id];
  }
  return [];
});

const activeWaypoint = computed(() => {
  if (mountainWaypoints.value.length === 0) return null;
  return mountainWaypoints.value[activeWaypointIndex.value] || mountainWaypoints.value[0];
});

const verifiedCount = computed(() => {
  return mountainWaypoints.value.filter(w => !w.unc).length;
});

const unverifiedCount = computed(() => {
  return mountainWaypoints.value.filter(w => !!w.unc).length;
});

const startAlt = computed(() => {
  if (mountainWaypoints.value.length === 0) return props.mountain?.altitude_m || 0;
  return mountainWaypoints.value[0].alt_m || props.mountain?.altitude_m || 0;
});

const peakAlt = computed(() => {
  if (mountainWaypoints.value.length === 0) return props.mountain?.altitude_m || 0;
  return Math.max(...mountainWaypoints.value.map(w => w.alt_m || 0), props.mountain?.altitude_m || 0);
});

const minAlt = computed(() => {
  if (mountainWaypoints.value.length === 0) return 0;
  return Math.min(...mountainWaypoints.value.map(w => w.alt_m || 0));
});

const elevationGain = computed(() => {
  const gain = peakAlt.value - startAlt.value;
  return gain > 0 ? gain : 0;
});

const totalKm = computed(() => {
  if (mountainWaypoints.value.length === 0) return props.mountain?.distance_km || 0;
  const last = mountainWaypoints.value[mountainWaypoints.value.length - 1];
  return last.km || props.mountain?.distance_km || 0;
});

// SVG Chart Geometry Specs
const svgWidth = 480;
const svgHeight = 160;
const padding = { top: 25, bottom: 25, left: 45, right: 25 };

const chartPoints = computed(() => {
  const pts = mountainWaypoints.value;
  if (!pts || pts.length === 0) return [];

  const innerW = svgWidth - padding.left - padding.right;
  const innerH = svgHeight - padding.top - padding.bottom;

  const low = Math.max(0, minAlt.value - 120);
  const high = peakAlt.value + 120;
  const altSpan = high - low || 1;

  const maxDistance = totalKm.value || (pts.length - 1) || 1;

  return pts.map((pt, idx) => {
    const kmVal = typeof pt.km === 'number' ? pt.km : idx;
    const progress = totalKm.value > 0 ? (kmVal / maxDistance) : (idx / (pts.length - 1 || 1));
    const clampedProgress = Math.max(0, Math.min(1, progress));

    const x = padding.left + clampedProgress * innerW;
    const alt = pt.alt_m || low;
    const y = padding.top + (1 - (alt - low) / altSpan) * innerH;

    return {
      ...pt,
      x: Math.round(x * 10) / 10,
      y: Math.round(y * 10) / 10
    };
  });
});

const gridYLines = computed(() => {
  const low = Math.max(0, minAlt.value - 120);
  const high = peakAlt.value + 120;
  const altSpan = high - low || 1;
  const innerH = svgHeight - padding.top - padding.bottom;

  // 3 grid levels: low, mid, high
  const alts = [
    Math.round(minAlt.value),
    Math.round((minAlt.value + peakAlt.value) / 2),
    Math.round(peakAlt.value)
  ];

  return alts.map(alt => {
    const y = padding.top + (1 - (alt - low) / altSpan) * innerH;
    return {
      alt,
      y: Math.round(y * 10) / 10
    };
  });
});

const linePath = computed(() => {
  if (chartPoints.value.length === 0) return '';
  return chartPoints.value.reduce((acc, pt, i) => {
    return i === 0 ? `M ${pt.x} ${pt.y}` : `${acc} L ${pt.x} ${pt.y}`;
  }, '');
});

const areaPath = computed(() => {
  if (chartPoints.value.length === 0) return '';
  const first = chartPoints.value[0];
  const last = chartPoints.value[chartPoints.value.length - 1];
  const bottomY = svgHeight - padding.bottom;
  return `${linePath.value} L ${last.x} ${bottomY} L ${first.x} ${bottomY} Z`;
});

const activeChartPoint = computed(() => {
  return chartPoints.value[activeWaypointIndex.value] || null;
});

function selectWaypoint(idx) {
  if (idx < 0 || idx >= mountainWaypoints.value.length) return;
  activeWaypointIndex.value = idx;
  const wp = mountainWaypoints.value[idx];
  if (wp) {
    emit('probe-waypoint', wp);
  }
  const el = document.getElementById(`waypoint-${idx}`);
  if (el) {
    el.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }
}

function handleChartPointerStart(e) {
  handleChartPointerMove(e);
}

function handleChartPointerMove(e) {
  if (!svgRef.value || chartPoints.value.length === 0) return;
  const rect = svgRef.value.getBoundingClientRect();
  if (!rect.width) return;

  let clientX = e.clientX;
  if (e.touches && e.touches.length > 0) {
    clientX = e.touches[0].clientX;
  }
  if (typeof clientX !== 'number') return;

  const scaleX = svgWidth / rect.width;
  const currentX = (clientX - rect.left) * scaleX;

  let closestIdx = 0;
  let minDiff = Infinity;
  chartPoints.value.forEach((pt, i) => {
    const diff = Math.abs(pt.x - currentX);
    if (diff < minDiff) {
      minDiff = diff;
      closestIdx = i;
    }
  });

  if (closestIdx !== activeWaypointIndex.value) {
    activeWaypointIndex.value = closestIdx;
    const wp = mountainWaypoints.value[closestIdx];
    if (wp) {
      emit('probe-waypoint', wp);
    }
  }
}

function handleChartPointerLeave() {
  // 鼠标移出图表时，保留当前已探测的最后航点；关闭抽屉时统一清空探针
}

watch(
  () => props.mountain?.id,
  () => {
    activeWaypointIndex.value = 0;
    emit('clear-probe');
  }
);

onUnmounted(() => {
  emit('clear-probe');
});

function formatCoord(val) {
  if (typeof val === 'number') {
    return val.toFixed(4);
  }
  return String(val || '--');
}
</script>
