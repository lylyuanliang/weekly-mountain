<template>
  <Teleport to="body" :disabled="!isFullscreen">
    <div
      :class="isFullscreen
        ? 'route-trajectory-fullscreen fixed inset-0 z-[9995] bg-[#0c1218] flex flex-col w-screen h-screen select-none overscroll-contain animate-fade-in'
        : 'route-trajectory-card rounded-2xl overflow-hidden bg-surface-container-high/90 border border-outline-variant/30 flex flex-col shadow-lg'"
    >
      <!-- ================= Header Bar ================= -->
      <!-- Mode A: Fullscreen Header -->
      <div
        v-if="isFullscreen"
        class="flex flex-col bg-[#121822] border-b border-outline-variant/20 flex-shrink-0 z-30 pt-[max(env(safe-area-inset-top,0px),12px)] shadow-md"
      >
        <!-- Top Row: Back button, Title, Right Actions -->
        <div class="px-3 py-2 flex items-center justify-between gap-2">
          <!-- Exit Fullscreen Back Button & Title -->
          <div class="flex items-center gap-2 min-w-0">
            <button
              type="button"
              class="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-surface-container-high hover:bg-surface-bright text-on-surface text-caption font-bold border border-outline-variant/30 active:scale-95 transition-all cursor-pointer flex-shrink-0"
              @click="closeFullscreen"
            >
              <span class="material-symbols-outlined text-[18px]">arrow_back</span>
              <span>退出全屏</span>
            </button>

            <div class="flex items-center gap-1.5 min-w-0">
              <span class="text-body-sm font-bold text-on-surface truncate">{{ mountain.name }} · 路线轨迹全景</span>
              <span class="px-2 py-0.5 rounded text-[10px] font-mono bg-surface-container text-secondary border border-secondary/30 flex-shrink-0">
                {{ tracks.length }} 条路线
              </span>
            </div>
          </div>

          <!-- Quick Action Buttons -->
          <div class="flex items-center gap-1.5 flex-shrink-0">
            <!-- Toggle Map Layer -->
            <button
              type="button"
              class="w-8 h-8 rounded-lg bg-surface-container-low hover:bg-surface-container-highest/80 text-on-surface flex items-center justify-center border border-outline-variant/20 text-[13px] cursor-pointer transition-colors"
              :title="layerMode === 0 ? '切换至遥感卫星底图' : '切换至黑曜夜间底图'"
              @click="toggleLayerMode"
            >
              <span class="material-symbols-outlined text-[17px]">
                {{ layerMode === 0 ? 'satellite_alt' : 'dark_mode' }}
              </span>
            </button>

            <!-- Recenter -->
            <button
              type="button"
              class="w-8 h-8 rounded-lg bg-surface-container-low hover:bg-surface-container-highest/80 text-on-surface flex items-center justify-center border border-outline-variant/20 text-[13px] cursor-pointer transition-colors"
              title="复位视口居中"
              @click="fitViewToCurrent"
            >
              <span class="material-symbols-outlined text-[17px]">filter_center_focus</span>
            </button>

            <!-- Exit Fullscreen Icon Button -->
            <button
              type="button"
              class="w-8 h-8 rounded-lg bg-surface-container-low hover:bg-surface-container-highest/80 text-on-surface flex items-center justify-center border border-outline-variant/20 text-[13px] cursor-pointer transition-colors"
              title="退出全屏"
              @click="closeFullscreen"
            >
              <span class="material-symbols-outlined text-[18px]">fullscreen_exit</span>
            </button>
          </div>
        </div>

        <!-- Sub Row: Route Selection Tabs -->
        <div class="px-3 pb-2 flex items-center gap-1.5 overflow-x-auto scrollbar-none">
          <!-- All Routes Compare Tab -->
          <button
            type="button"
            class="flex items-center gap-1 px-3 py-1 rounded-full text-caption font-semibold transition-all flex-shrink-0 cursor-pointer"
            :class="selectedRouteIndex === null
              ? 'bg-secondary text-on-secondary shadow-sm ring-1 ring-secondary/50 font-bold'
              : 'bg-surface-container-low text-on-surface-variant hover:text-on-surface'"
            @click="selectRoute(null)"
          >
            <span class="material-symbols-outlined text-[14px]">compare_arrows</span>
            <span>全景对比 ({{ tracks.length }})</span>
          </button>

          <!-- Individual Route Tabs -->
          <button
            v-for="(t, idx) in tracks"
            :key="`fs-track-tab-${idx}`"
            type="button"
            class="flex items-center gap-1.5 px-3 py-1 rounded-full text-caption font-semibold transition-all flex-shrink-0 cursor-pointer"
            :class="selectedRouteIndex === idx
              ? 'text-white shadow-sm ring-1'
              : 'bg-surface-container-low text-on-surface-variant hover:text-on-surface'"
            :style="selectedRouteIndex === idx ? { backgroundColor: t.color, ringColor: t.color } : {}"
            @click="selectRoute(idx)"
          >
            <span
              v-if="selectedRouteIndex !== idx"
              class="w-2 h-2 rounded-full flex-shrink-0"
              :style="{ backgroundColor: t.color }"
            ></span>
            <span class="truncate max-w-[120px]">{{ t.route_name.split('（')[0] }}</span>
          </button>
        </div>
      </div>

      <!-- Mode B: Inline Card Header -->
      <div
        v-else
        class="px-3 py-2 bg-surface-container/90 border-b border-outline-variant/20 flex items-center justify-between gap-2 flex-shrink-0"
      >
        <div class="flex items-center gap-1.5 overflow-x-auto scrollbar-none py-0.5 max-w-full">
          <!-- All Routes Compare Tab -->
          <button
            type="button"
            class="flex items-center gap-1 px-2.5 py-1 rounded-full text-caption font-semibold transition-all flex-shrink-0 cursor-pointer"
            :class="selectedRouteIndex === null
              ? 'bg-secondary text-on-secondary shadow-sm ring-1 ring-secondary/50 font-bold'
              : 'bg-surface-container-low text-on-surface-variant hover:text-on-surface hover:bg-surface-container-highest/60'"
            @click="selectRoute(null)"
          >
            <span class="material-symbols-outlined text-[14px]">compare_arrows</span>
            <span>全景对比 ({{ tracks.length }})</span>
          </button>

          <!-- Individual Route Tabs -->
          <button
            v-for="(t, idx) in tracks"
            :key="`track-tab-${idx}`"
            type="button"
            class="flex items-center gap-1.5 px-2.5 py-1 rounded-full text-caption font-semibold transition-all flex-shrink-0 cursor-pointer"
            :class="selectedRouteIndex === idx
              ? 'text-white shadow-sm ring-1'
              : 'bg-surface-container-low text-on-surface-variant hover:text-on-surface'"
            :style="selectedRouteIndex === idx ? { backgroundColor: t.color, ringColor: t.color } : {}"
            @click="selectRoute(idx)"
          >
            <span
              v-if="selectedRouteIndex !== idx"
              class="w-2 h-2 rounded-full flex-shrink-0"
              :style="{ backgroundColor: t.color }"
            ></span>
            <span class="truncate max-w-[90px]">{{ t.route_name.split('（')[0] }}</span>
          </button>
        </div>

        <!-- Quick Switchers: Layer, Reset & Fullscreen -->
        <div class="flex items-center gap-1 flex-shrink-0">
          <button
            type="button"
            class="w-7 h-7 rounded-lg bg-surface-container-low hover:bg-surface-container-highest/80 text-on-surface flex items-center justify-center border border-outline-variant/20 text-[12px] cursor-pointer transition-colors"
            :title="layerMode === 0 ? '切换至遥感卫星底图' : '切换至黑曜夜间底图'"
            @click="toggleLayerMode"
          >
            <span class="material-symbols-outlined text-[15px]">
              {{ layerMode === 0 ? 'satellite_alt' : 'dark_mode' }}
            </span>
          </button>
          <button
            type="button"
            class="w-7 h-7 rounded-lg bg-surface-container-low hover:bg-surface-container-highest/80 text-on-surface flex items-center justify-center border border-outline-variant/20 text-[12px] cursor-pointer transition-colors"
            title="复位视口居中"
            @click="fitViewToCurrent"
          >
            <span class="material-symbols-outlined text-[15px]">filter_center_focus</span>
          </button>
          <button
            type="button"
            class="w-7 h-7 rounded-lg bg-secondary/20 hover:bg-secondary/35 text-secondary flex items-center justify-center border border-secondary/30 text-[12px] cursor-pointer transition-all active:scale-95"
            title="全屏查看轨迹"
            @click="openFullscreen"
          >
            <span class="material-symbols-outlined text-[16px]">fullscreen</span>
          </button>
        </div>
      </div>

      <!-- ================= Map Viewport Canvas ================= -->
      <div
        ref="mapContainerRef"
        :class="isFullscreen ? 'relative flex-1 w-full min-h-0' : 'relative w-full h-[280px] sm:h-[320px]'"
        class="overflow-hidden bg-[#0c1218] select-none touch-none cursor-grab active:cursor-grabbing"
        @mousedown="handleMouseDown"
        @mousemove="handleMouseMove"
        @mouseup="handleMouseUp"
        @mouseleave="handleMouseUp"
        @wheel.prevent="handleWheel"
        @touchstart.passive="handleTouchStart"
        @touchmove.passive="handleTouchMove"
        @touchend="handleTouchEnd"
      >
        <!-- Map World Plane (Standard 2D Transform: Strictly NO preserve-3d to respect overflow:hidden) -->
        <div
          class="absolute inset-0 z-0 origin-center pointer-events-none"
          :class="isInteracting ? '' : 'transition-transform duration-200 ease-out'"
          :style="worldTransformStyle"
        >
          <!-- Base Slippy Map Tiles Layer -->
          <div
            class="absolute inset-0 pointer-events-none"
            :class="layerMode === 0 ? 'map-tile-dark' : ''"
          >
            <div
              v-for="tile in visibleTiles"
              :key="tile.key"
              class="absolute w-[256px] h-[256px] overflow-hidden"
              :style="{
                left: `${tile.left}px`,
                top: `${tile.top}px`
              }"
            >
              <img
                :src="tile.url"
                alt="amap tile"
                decoding="async"
                class="w-full h-full object-cover select-none pointer-events-none"
                @error="onTileError"
              />
              <img
                v-if="tile.subUrl"
                :src="tile.subUrl"
                alt="road overlay"
                decoding="async"
                class="absolute inset-0 w-full h-full object-cover pointer-events-none opacity-85 select-none"
                @error="onTileError"
              />
            </div>
          </div>

          <!-- Vector SVG Trajectory Paths & Waypoint Pins -->
          <svg
            class="absolute inset-0 w-full h-full pointer-events-auto"
            :viewBox="`0 0 ${containerWidth} ${containerHeight}`"
          >
            <!-- Route Paths Layer -->
            <g v-for="(route, rIdx) in tracks" :key="`route-svg-${rIdx}`">
              <!-- Background Outline Stroke for High Contrast against terrain -->
              <path
                :d="getRoutePathD(route)"
                fill="none"
                stroke="#050a0e"
                :stroke-width="isRouteActive(rIdx) ? 7 : 4"
                stroke-linecap="round"
                stroke-linejoin="round"
                :opacity="isRouteActive(rIdx) ? 0.85 : 0.35"
              />

              <!-- Active Route Glow Underlay (Pure Vector Aura, 0 GPU offscreen buffer bug) -->
              <path
                v-if="isRouteActive(rIdx)"
                :d="getRoutePathD(route)"
                fill="none"
                :stroke="route.color"
                :stroke-width="8"
                stroke-linecap="round"
                stroke-linejoin="round"
                opacity="0.3"
              />

              <!-- Colored Core Route Polyline (No transition on d to eliminate frame lag) -->
              <path
                :d="getRoutePathD(route)"
                fill="none"
                :stroke="route.color"
                :stroke-width="isRouteActive(rIdx) ? 3.5 : 2"
                stroke-linecap="round"
                stroke-linejoin="round"
                :opacity="isRouteActive(rIdx) ? 1 : 0.4"
                :class="{ 'route-polyline-animated': isRouteActive(rIdx) }"
                class="cursor-pointer"
                @click.stop="selectRoute(rIdx)"
              />
            </g>

            <!-- Waypoint Markers Layer (Counter-scaled by 1/zoomScale to maintain constant size) -->
            <g v-for="(wp, wIdx) in visibleWaypoints" :key="`wp-${wIdx}`">
              <g
                class="cursor-pointer"
                :transform="`translate(${wp.pixelX}, ${wp.pixelY}) scale(${1 / zoomScale})`"
                @click.stop="openWaypoint(wp)"
              >
                <!-- Pin Outer Glow -->
                <circle
                  r="10"
                  :fill="getWaypointColor(wp.type)"
                  fill-opacity="0.25"
                />
                <!-- Pin Circle Body -->
                <circle
                  r="6.5"
                  :fill="getWaypointColor(wp.type)"
                  stroke="#0a0f14"
                  stroke-width="2"
                />
                <!-- Inner Center Dot -->
                <circle
                  r="2.5"
                  fill="#ffffff"
                />
                <!-- Waypoint Label Tag -->
                <text
                  v-if="selectedRouteIndex !== null || wp.type === 'start' || wp.type === 'summit' || wp.type === 'end'"
                  y="18"
                  text-anchor="middle"
                  class="text-[10px] font-sans font-bold fill-white select-none pointer-events-none"
                  style="paint-order: stroke; stroke: #080d12; stroke-width: 2.5px; stroke-linejoin: round;"
                >
                  {{ wp.name.length > 6 ? wp.name.slice(0, 5) + '..' : wp.name }}
                </text>
              </g>
            </g>
          </svg>
        </div>

        <!-- Active Waypoint Tooltip Popup (Solid Obsidian Background, 0 Backdrop-Blur) -->
        <transition name="fade">
          <div
            v-if="activeWaypoint"
            class="absolute z-20 p-2.5 rounded-xl bg-[#18202c] border border-outline-variant/40 shadow-2xl text-on-surface max-w-[210px] space-y-1"
            :style="waypointTooltipStyle"
            @click.stop
          >
            <div class="flex items-center justify-between gap-1">
              <span class="text-caption font-bold text-on-surface flex items-center gap-1 truncate">
                <span class="w-2 h-2 rounded-full" :style="{ backgroundColor: getWaypointColor(activeWaypoint.type) }"></span>
                {{ activeWaypoint.name }}
              </span>
              <button
                type="button"
                class="w-4 h-4 rounded text-on-surface-variant hover:text-on-surface flex items-center justify-center text-[12px] cursor-pointer"
                @click="activeWaypoint = null"
              >
                ✕
              </button>
            </div>
            <div class="flex items-center gap-2 text-[10px] text-secondary font-mono">
              <span v-if="activeWaypoint.alt_m">海拔: {{ activeWaypoint.alt_m }}m</span>
              <span>{{ getWaypointTypeName(activeWaypoint.type) }}</span>
            </div>
            <p v-if="activeWaypoint.desc" class="text-[11px] text-on-surface-variant leading-tight">
              {{ activeWaypoint.desc }}
            </p>
          </div>
        </transition>

        <!-- Floating Zoom Controls -->
        <div class="absolute right-3 bottom-12 flex flex-col gap-1.5 z-10">
          <button
            type="button"
            class="w-8 h-8 rounded-lg bg-surface-container-high/95 hover:bg-surface-container-highest text-on-surface border border-outline-variant/30 flex items-center justify-center font-bold text-[16px] shadow-lg cursor-pointer transition-colors active:scale-95"
            title="放大"
            @click="zoomIn"
          >
            +
          </button>
          <button
            type="button"
            class="w-8 h-8 rounded-lg bg-surface-container-high/95 hover:bg-surface-container-highest text-on-surface border border-outline-variant/30 flex items-center justify-center font-bold text-[16px] shadow-lg cursor-pointer transition-colors active:scale-95"
            title="缩小"
            @click="zoomOut"
          >
            −
          </button>
        </div>

        <!-- Watermark / Attribution -->
        <div class="absolute left-3 bottom-1 text-[9px] text-on-surface-variant/60 font-mono pointer-events-none select-none z-10">
          {{ layerMode === 0 ? '© 高德地图 · 矢量暗夜' : '© 高德地图 · 遥感卫星' }}
        </div>
      </div>

      <!-- ================= Bottom Metrics Strip ================= -->
      <div
        :class="isFullscreen ? 'p-3.5 bg-[#121822] border-t border-outline-variant/20 pb-[max(env(safe-area-inset-bottom,0px),14px)] flex-shrink-0' : 'p-3 bg-surface-container-low/90 border-t border-outline-variant/20 flex flex-col gap-2 flex-shrink-0'"
      >
        <!-- Active Route Single Details -->
        <div v-if="currentSelectedRoute" class="flex items-center justify-between gap-2 flex-wrap">
          <div class="flex items-center gap-1.5">
            <span class="w-2.5 h-2.5 rounded-full flex-shrink-0" :style="{ backgroundColor: currentSelectedRoute.color }"></span>
            <span class="text-body-sm font-bold text-on-surface">{{ currentSelectedRoute.route_name }}</span>
            <span v-if="currentSelectedRoute.difficulty" class="px-1.5 py-0.5 rounded text-[10px] font-mono bg-surface-container text-secondary border border-secondary/30">
              {{ currentSelectedRoute.difficulty }}
            </span>
          </div>

          <div class="flex items-center gap-3 text-caption font-mono text-on-surface-variant">
            <span v-if="currentSelectedRoute.distance_km">里程: <strong class="text-on-surface">{{ currentSelectedRoute.distance_km }}km</strong></span>
            <span v-if="currentSelectedRoute.elevation_gain_m">爬升: <strong class="text-on-surface">+{{ currentSelectedRoute.elevation_gain_m }}m</strong></span>
            <span v-if="currentSelectedRoute.estimated_hours">预计: <strong class="text-on-surface">{{ currentSelectedRoute.estimated_hours }}</strong></span>
          </div>
        </div>

        <!-- Comparative Summary when "All" selected -->
        <div v-else class="flex items-center gap-2 text-caption text-on-surface-variant">
          <span class="material-symbols-outlined text-[16px] text-secondary flex-shrink-0">alt_route</span>
          <span class="flex-1 leading-snug">
            已并在同一地图呈现 <strong class="text-secondary font-mono">{{ tracks.length }}</strong> 条路线走向，点击单条路线可聚焦航点与高差
          </span>
          <span class="text-[11px] font-mono text-secondary px-2 py-0.5 rounded bg-surface-container flex-shrink-0 border border-secondary/20">
            全景对比
          </span>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue';
import { lonToX, latToY, xToLon, yToLat, projectPoint } from '@/utils/mapProjection';
import { getMountainTracks, getTracksFitBounds } from '@/utils/trackService';
import { useScrollLock } from '@/composables/useScrollLock';

const props = defineProps({
  mountain: {
    type: Object,
    required: true
  },
  modelValue: {
    type: Number,
    default: null
  }
});

const emit = defineEmits(['update:modelValue', 'select-waypoint']);

// Fullscreen State
const isFullscreen = ref(false);
useScrollLock(isFullscreen);

function openFullscreen() {
  isFullscreen.value = true;
  nextTick(() => {
    updateContainerDimensions();
    fitViewToCurrent();
  });
}

function closeFullscreen() {
  isFullscreen.value = false;
  nextTick(() => {
    updateContainerDimensions();
    fitViewToCurrent();
  });
}

function toggleFullscreen() {
  if (isFullscreen.value) {
    closeFullscreen();
  } else {
    openFullscreen();
  }
}

// Map Viewport Container Ref & Dimensions
const mapContainerRef = ref(null);
const containerWidth = ref(360);
const containerHeight = ref(300);

// Layer Mode: 0 = Dark Night, 1 = Satellite
const layerMode = ref(0);

// Viewport States
const centerLng = ref(104.06);
const centerLat = ref(30.67);
const zoom = ref(12);

// Selection State
const selectedRouteIndex = ref(props.modelValue);
const activeWaypoint = ref(null);

// Continuous Zoom & World Plane Transform (Standard 2D Scale, 0 preserve-3d to respect overflow:hidden)
const intZoom = computed(() => Math.floor(zoom.value));
const zoomScale = computed(() => Math.pow(2, zoom.value - intZoom.value));

const worldTransformStyle = computed(() => ({
  transform: `scale(${zoomScale.value})`,
  transformOrigin: 'center center',
  willChange: isInteracting.value ? 'transform' : 'auto'
}));

// Drag & Pan States
const isDragging = ref(false);
const isPinching = ref(false);
const isInteracting = computed(() => isDragging.value || isPinching.value);

let isMapMoved = false;
let mouseDownX = 0;
let mouseDownY = 0;
let lastMouseX = 0;
let lastMouseY = 0;

let pendingDx = 0;
let pendingDy = 0;
let panRafId = null;

function applyPanDelta(dx, dy) {
  pendingDx += dx;
  pendingDy += dy;
  if (!panRafId) {
    panRafId = requestAnimationFrame(() => {
      panRafId = null;
      if (pendingDx === 0 && pendingDy === 0) return;
      const z = zoom.value;
      const cx = lonToX(centerLng.value, z) - pendingDx;
      const cy = latToY(centerLat.value, z) - pendingDy;
      pendingDx = 0;
      pendingDy = 0;
      centerLng.value = xToLon(cx, z);
      centerLat.value = yToLat(cy, z);
    });
  }
}

function flushPanDelta() {
  if (panRafId) {
    cancelAnimationFrame(panRafId);
    panRafId = null;
  }
  if (pendingDx !== 0 || pendingDy !== 0) {
    const z = zoom.value;
    const cx = lonToX(centerLng.value, z) - pendingDx;
    const cy = latToY(centerLat.value, z) - pendingDy;
    pendingDx = 0;
    pendingDy = 0;
    centerLng.value = xToLon(cx, z);
    centerLat.value = yToLat(cy, z);
  }
}

// Extract Tracks
const tracks = computed(() => getMountainTracks(props.mountain));

const currentSelectedRoute = computed(() => {
  if (selectedRouteIndex.value === null || selectedRouteIndex.value === undefined) return null;
  return tracks.value[selectedRouteIndex.value] || null;
});

function isRouteActive(rIdx) {
  if (selectedRouteIndex.value === null) return true;
  return selectedRouteIndex.value === rIdx;
}

// ================= Map Tiles Calculation =================
const visibleTiles = computed(() => {
  const z = intZoom.value;
  const maxTile = Math.pow(2, z) - 1;
  const cx = lonToX(centerLng.value, z);
  const cy = latToY(centerLat.value, z);

  const w = containerWidth.value;
  const h = containerHeight.value;

  const left = cx - w / 2;
  const top = cy - h / 2;

  // 1-tile padding on all edges prevents seams when zooming & panning
  const x0 = Math.floor(left / 256) - 1;
  const x1 = Math.floor((left + w) / 256) + 1;
  const y0 = Math.floor(top / 256) - 1;
  const y1 = Math.floor((top + h) / 256) + 1;

  const tiles = [];
  for (let ty = y0; ty <= y1; ty++) {
    if (ty < 0 || ty > maxTile) continue;
    for (let tx = x0; tx <= x1; tx++) {
      const wx = ((tx % (maxTile + 1)) + (maxTile + 1)) % (maxTile + 1);
      const subIdx = 1 + ((wx + ty) % 4);

      let url = '';
      let subUrl = null;

      if (layerMode.value === 0) {
        url = `https://webrd0${subIdx}.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=8&x=${wx}&y=${ty}&z=${z}`;
      } else {
        url = `https://webst0${subIdx}.is.autonavi.com/appmaptile?style=6&x=${wx}&y=${ty}&z=${z}`;
        subUrl = `https://wprd0${subIdx}.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=8&x=${wx}&y=${ty}&z=${z}`;
      }

      tiles.push({
        key: `tile-${layerMode.value}-${z}-${wx}-${ty}`,
        url,
        subUrl,
        left: Math.round(tx * 256 - left),
        top: Math.round(ty * 256 - top)
      });
    }
  }
  return tiles;
});

function onTileError(e) {
  if (e?.target) {
    e.target.style.opacity = '0.08';
  }
}

// ================= Path & Waypoint Projections =================
function getRoutePathD(route) {
  if (!route.coordinates || route.coordinates.length < 2) return '';
  const z = intZoom.value;
  const w = containerWidth.value;
  const h = containerHeight.value;

  const points = route.coordinates.map(c => {
    const p = projectPoint(c[0], c[1], centerLng.value, centerLat.value, z, w, h);
    return `${p.x.toFixed(1)},${p.y.toFixed(1)}`;
  });

  return `M ${points.join(' L ')}`;
}

const visibleWaypoints = computed(() => {
  const z = intZoom.value;
  const w = containerWidth.value;
  const h = containerHeight.value;

  let targetWaypoints = [];
  if (selectedRouteIndex.value !== null && tracks.value[selectedRouteIndex.value]) {
    targetWaypoints = tracks.value[selectedRouteIndex.value].key_waypoints || [];
  } else {
    for (const t of tracks.value) {
      if (t.key_waypoints) {
        for (const wp of t.key_waypoints) {
          if (wp.type === 'start' || wp.type === 'end' || wp.type === 'summit') {
            targetWaypoints.push(wp);
          }
        }
      }
    }
  }

  return targetWaypoints.map(wp => {
    const pos = projectPoint(wp.lng, wp.lat, centerLng.value, centerLat.value, z, w, h);
    return {
      ...wp,
      pixelX: Math.round(pos.x),
      pixelY: Math.round(pos.y)
    };
  });
});

const waypointTooltipStyle = computed(() => {
  if (!activeWaypoint.value) return {};
  const z = intZoom.value;
  const w = containerWidth.value;
  const h = containerHeight.value;
  const pos = projectPoint(
    activeWaypoint.value.lng,
    activeWaypoint.value.lat,
    centerLng.value,
    centerLat.value,
    z,
    w,
    h
  );
  const cx = w / 2;
  const cy = h / 2;
  const sx = cx + (pos.x - cx) * zoomScale.value;
  const sy = cy + (pos.y - cy) * zoomScale.value;

  const left = Math.min(Math.max(sx - 105, 8), w - 218);
  const top = Math.max(sy - 95, 8);

  return {
    left: `${left}px`,
    top: `${top}px`
  };
});

function getWaypointColor(type) {
  switch (type) {
    case 'start': return '#10b981';
    case 'end': return '#f43f5e';
    case 'summit': return '#eab308';
    case 'viewpoint': return '#06b6d4';
    case 'supply': return '#3b82f6';
    default: return '#a855f7';
  }
}

function getWaypointTypeName(type) {
  switch (type) {
    case 'start': return '🚩 起点';
    case 'end': return '🏁 终点';
    case 'summit': return '⛰️ 极顶';
    case 'viewpoint': return '👁️ 观景点';
    case 'supply': return '💧 补给站';
    default: return '📍 地标点';
  }
}

// ================= Interactivity & Gestures =================
function selectRoute(idx) {
  if (isMapMoved) return;
  selectedRouteIndex.value = idx;
  activeWaypoint.value = null;
  emit('update:modelValue', idx);
  fitViewToCurrent();
}

function toggleLayerMode() {
  layerMode.value = (layerMode.value + 1) % 2;
}

function fitViewToCurrent() {
  const bounds = getTracksFitBounds(
    tracks.value,
    selectedRouteIndex.value,
    containerWidth.value,
    containerHeight.value
  );
  centerLng.value = bounds.centerLng;
  centerLat.value = bounds.centerLat;
  zoom.value = Math.min(Math.max(bounds.zoom, 10), 16);
}

function zoomIn() {
  zoom.value = Math.min(17, Math.round((zoom.value + 1.0) * 10) / 10);
}

function zoomOut() {
  zoom.value = Math.max(9, Math.round((zoom.value - 1.0) * 10) / 10);
}

function openWaypoint(wp) {
  if (isMapMoved) return;
  activeWaypoint.value = wp;
  emit('select-waypoint', wp);
}

// Mouse Gestures
function handleMouseDown(e) {
  if (e.button !== 0) return;
  isDragging.value = true;
  isMapMoved = false;
  mouseDownX = e.clientX;
  mouseDownY = e.clientY;
  lastMouseX = e.clientX;
  lastMouseY = e.clientY;
}

function handleMouseMove(e) {
  if (!isDragging.value) return;
  const dx = e.clientX - lastMouseX;
  const dy = e.clientY - lastMouseY;
  if (!isMapMoved && Math.hypot(e.clientX - mouseDownX, e.clientY - mouseDownY) > 5) {
    isMapMoved = true;
  }
  lastMouseX = e.clientX;
  lastMouseY = e.clientY;
  applyPanDelta(dx, dy);
}

function handleMouseUp() {
  flushPanDelta();
  isDragging.value = false;
  if (isMapMoved) {
    setTimeout(() => {
      isMapMoved = false;
    }, 60);
  }
}

function handleWheel(e) {
  const delta = e.deltaY > 0 ? -0.25 : 0.25;
  zoom.value = Math.min(Math.max(zoom.value + delta, 9), 17);
}

// Touch Gestures
let lastTouchX = 0;
let lastTouchY = 0;
let mapTouchStartX = 0;
let mapTouchStartY = 0;
let initialPinchDist = 0;
let initialPinchZoom = 12;
let pinchRafId = null;
let pendingPinchZoom = null;

function getPinchDist(e) {
  const t1 = e.touches[0];
  const t2 = e.touches[1];
  return Math.hypot(t1.clientX - t2.clientX, t1.clientY - t2.clientY);
}

function handleTouchStart(e) {
  if (e.touches.length === 2) {
    isDragging.value = false;
    isPinching.value = true;
    isMapMoved = true;
    initialPinchDist = getPinchDist(e);
    initialPinchZoom = zoom.value;
  } else if (e.touches.length === 1) {
    isPinching.value = false;
    isDragging.value = true;
    isMapMoved = false;
    mapTouchStartX = e.touches[0].clientX;
    mapTouchStartY = e.touches[0].clientY;
    lastTouchX = e.touches[0].clientX;
    lastTouchY = e.touches[0].clientY;
  }
}

function handleTouchMove(e) {
  if (e.touches.length === 1 && isDragging.value) {
    const dx = e.touches[0].clientX - lastTouchX;
    const dy = e.touches[0].clientY - lastTouchY;
    if (!isMapMoved && Math.hypot(e.touches[0].clientX - mapTouchStartX, e.touches[0].clientY - mapTouchStartY) > 5) {
      isMapMoved = true;
    }
    lastTouchX = e.touches[0].clientX;
    lastTouchY = e.touches[0].clientY;
    applyPanDelta(dx, dy);
  } else if (e.touches.length === 2 && initialPinchDist > 0) {
    const dist = getPinchDist(e);
    const newZoom = initialPinchZoom + Math.log2(dist / initialPinchDist);
    pendingPinchZoom = Math.max(9, Math.min(17, newZoom));

    if (!pinchRafId) {
      pinchRafId = requestAnimationFrame(() => {
        pinchRafId = null;
        if (pendingPinchZoom !== null) {
          zoom.value = pendingPinchZoom;
          pendingPinchZoom = null;
        }
      });
    }
  }
}

function handleTouchEnd(e) {
  flushPanDelta();
  if (pinchRafId) {
    cancelAnimationFrame(pinchRafId);
    pinchRafId = null;
  }
  if (pendingPinchZoom !== null) {
    zoom.value = pendingPinchZoom;
    pendingPinchZoom = null;
  }
  isDragging.value = false;
  if (isMapMoved) {
    setTimeout(() => {
      isMapMoved = false;
    }, 60);
  }
  if (!e?.touches || e.touches.length < 2) {
    isPinching.value = false;
    initialPinchDist = 0;
  }
}

// Lifecycle & Resize
function updateContainerDimensions() {
  if (mapContainerRef.value) {
    containerWidth.value = mapContainerRef.value.clientWidth || (isFullscreen.value ? window.innerWidth : 360);
    containerHeight.value = mapContainerRef.value.clientHeight || (isFullscreen.value ? window.innerHeight - 120 : 300);
  }
}

let resizeObserver = null;
onMounted(() => {
  updateContainerDimensions();
  fitViewToCurrent();

  if (window.ResizeObserver && mapContainerRef.value) {
    resizeObserver = new ResizeObserver(() => {
      updateContainerDimensions();
    });
    resizeObserver.observe(mapContainerRef.value);
  }
});

onUnmounted(() => {
  if (isFullscreen.value) {
    closeFullscreen();
  }
  if (resizeObserver) {
    resizeObserver.disconnect();
  }
  if (panRafId) {
    cancelAnimationFrame(panRafId);
  }
  if (pinchRafId) {
    cancelAnimationFrame(pinchRafId);
  }
});

watch(() => props.mountain, () => {
  if (isFullscreen.value) {
    closeFullscreen();
  }
  selectedRouteIndex.value = null;
  activeWaypoint.value = null;
  fitViewToCurrent();
}, { deep: true });

watch(() => props.modelValue, (newVal) => {
  if (newVal !== selectedRouteIndex.value) {
    selectedRouteIndex.value = newVal;
    fitViewToCurrent();
  }
});
</script>

<style scoped>
.map-tile-dark {
  filter: invert(92%) hue-rotate(180deg) brightness(88%) contrast(125%) saturate(75%);
}

.route-polyline-animated {
  stroke-dasharray: 6 3;
  animation: routeDashFlow 24s linear infinite;
}

@keyframes routeDashFlow {
  to {
    stroke-dashoffset: -360;
  }
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: scale(0.95);
}
</style>
