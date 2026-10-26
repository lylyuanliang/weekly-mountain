<template>
  <main
    ref="mapContainerRef"
    class="explore-map-container relative w-full h-screen overflow-hidden bg-surface-container-lowest select-none touch-none"
    @mousedown="onMouseDown"
    @mousemove="onMouseMove"
    @mouseup="onMouseUp"
    @mouseleave="onMouseUp"
    @touchstart.passive="onTouchStart"
    @touchmove.passive="onTouchMove"
    @touchend="onTouchEnd"
    @wheel.prevent="onWheel"
    @click="handleMapClick"
  >
    <!-- Map World Plane (Holds Tiles & Markers with 3D & Zoom Transform) -->
    <div
      class="absolute inset-0 z-0 origin-center"
      :class="isInteracting ? '' : 'transition-transform duration-200 ease-out'"
      :style="worldTransformStyle"
    >
      <!-- Base Layer 0: Slippy Map Tiles Grid -->
      <div
        class="absolute inset-0 z-0 pointer-events-none will-change-transform"
        :class="layerMode === 0 ? 'map-tile-dark' : ''"
        style="transform: translateZ(0);"
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
          <!-- Base Map Tile Image -->
          <img
            :src="tile.url"
            alt="map tile"
            decoding="async"
            class="w-full h-full object-cover select-none pointer-events-none"
            @error="onTileError"
          />
          <!-- Optional Road/Label Overlay for Satellite Layer -->
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

      <!-- Map Dynamic Mountain Markers Layer -->
      <div class="absolute inset-0 z-20 pointer-events-auto">
        <!-- Mountain Markers for Current Region -->
        <div
          v-for="m in mountainPositions"
          :key="m.id"
          v-show="isMountainVisible(m.id)"
          :data-mountain-id="m.id"
          class="mountain-marker absolute cursor-pointer group will-change-transform"
          :class="[
            m.id === mountainStore.selectedMountainId ? 'is-active selected z-30' : 'z-20',
            isInteracting ? 'is-interacting' : ''
          ]"
          :style="getMarkerStyle(m)"
          @click.stop="handleMarkerClick(m.id)"
        >
          <!-- Active / Selected Marker Design -->
          <template v-if="m.id === mountainStore.selectedMountainId">
            <!-- Macro/Medium View (lodMode === 'compact', Z < 9.8): Sleek, Compact Highlighted Pill -->
            <template v-if="lodMode === 'compact'">
              <!-- Subtle Beacon Ring -->
              <div class="absolute -inset-1 rounded-full bg-primary/20  pointer-events-none"></div>

              <!-- Interactive Pin Pill -->
              <div
                class="relative flex items-center gap-1.5 px-2 py-0.5 rounded-full frost-glass-highlight glow-primary border border-primary/70 shadow-xl transition-all duration-200 active:scale-95 select-none"
              >
                <!-- Concentric Pulsing Aurora Dot (100% Coaxial Center, 0 Offset) -->
                <span class="relative flex items-center justify-center flex-shrink-0 w-2 h-2">

                  <span class="relative w-2 h-2 rounded-full bg-primary shadow-[0_0_8px_#4edea3]"></span>
                </span>
                <span class="text-[10.5px] font-bold text-on-surface tracking-tight whitespace-nowrap">{{ m.name }}</span>
                <span class="text-[9px] font-label-data-sm text-primary tracking-tight whitespace-nowrap">{{ m.alt }}m</span>
              </div>

              <!-- Drop Line to Ground Topo Anchor -->
              <div class="w-0.5 h-2 bg-gradient-to-b from-primary/90 to-transparent mx-auto"></div>
            </template>

            <!-- Detailed Close-up View (lodMode === 'detailed', Z >= 9.8): Compact Elegant Card (Capped) -->
            <template v-else>
              <!-- Subtle Beacon Outer Ring (Gentle Aurora Glow, No Drift Ping) -->
              <div class="absolute -inset-1.5 rounded-full bg-primary/20  pointer-events-none"></div>

              <!-- Interactive Pin Card (Capped Max Width, Refined Typography) -->
              <div
                class="relative flex items-center gap-1.5 px-2.5 py-1 rounded-full frost-glass-highlight glow-primary border border-primary/70 shadow-xl transition-all duration-200 select-none max-w-[145px]"
              >
                <!-- Concentric Pulsing Aurora Dot (100% Coaxial Center, 0 Offset) -->
                <span class="relative flex items-center justify-center flex-shrink-0 w-2 h-2">

                  <span class="relative w-2 h-2 rounded-full bg-primary shadow-[0_0_8px_#4edea3]"></span>
                </span>
                <div class="flex flex-col min-w-0">
                  <div class="flex items-center gap-1 min-w-0">
                    <span class="text-[12px] font-bold text-on-surface tracking-tight truncate leading-tight">{{ m.name }}</span>
                    <span class="px-1 py-0.2 text-[8.5px] font-label-data-sm bg-primary/20 text-primary rounded font-semibold flex-shrink-0">
                      {{ m.difficulty || 'L2' }}
                    </span>
                  </div>
                  <span class="text-[9.5px] font-label-data-sm text-primary tracking-wider leading-none mt-0.5">
                    {{ m.alt }}m
                  </span>
                </div>
              </div>

              <!-- Drop Line to Ground Topo Anchor -->
              <div class="w-0.5 h-2.5 bg-gradient-to-b from-primary/90 to-transparent mx-auto"></div>
            </template>
          </template>

          <!-- Normal / Unselected Marker Design (Adaptive Scaling Based on Zoom) -->
          <template v-else>
            <!-- Macro/Medium View (lodMode === 'compact', Z < 9.8): Compact Single-Line Name Chip -->
            <template v-if="lodMode === 'compact'">
              <div
                class="relative flex items-center gap-1 px-2 py-0.5 rounded-full frost-glass border shadow-md transition-all duration-200 group-hover:scale-105 group-hover:border-primary/50 active:scale-95 select-none"
                :class="m.isDone ? 'border-primary/50 bg-surface-container-high/90 glow-primary' : 'border-outline-variant/40 bg-surface-container-lowest/85'"
              >
                <!-- Pin status dot -->
                <span
                  class="w-1.5 h-1.5 rounded-full flex-shrink-0"
                  :class="m.isDone ? 'bg-primary' : (m.difficulty === 'L4' || m.difficulty === 'L5' ? 'bg-secondary' : 'bg-primary/80')"
                ></span>
                <span class="text-[10px] font-bold text-on-surface tracking-tight leading-tight whitespace-nowrap">
                  {{ m.name }}
                </span>
              </div>
              <div class="w-0.5 h-1.5 bg-gradient-to-b from-outline-variant/40 to-transparent mx-auto"></div>
            </template>

            <!-- Detailed Close-up View (lodMode === 'detailed', Z >= 9.8): Two-Line Chip with Altitude -->
            <template v-else>
              <div
                class="relative flex items-center gap-1.5 px-2.5 py-1 rounded-full frost-glass border shadow-lg transition-all duration-200 group-hover:scale-110 group-hover:border-primary/50 active:scale-95 select-none"
                :class="m.isDone ? 'border-primary/50 bg-surface-container-high/90 glow-primary' : 'border-outline-variant/50 bg-surface-container-lowest/80'"
              >
                <!-- Pin status dot -->
                <span
                  class="w-2 h-2 rounded-full flex-shrink-0"
                  :class="m.isDone ? 'bg-primary' : (m.difficulty === 'L4' || m.difficulty === 'L5' ? 'bg-secondary' : 'bg-primary/80')"
                ></span>
                <div class="flex flex-col">
                  <span class="text-[11px] font-bold text-on-surface tracking-tight leading-tight whitespace-nowrap">
                    {{ m.name }}
                  </span>
                  <span
                    class="text-[9px] font-label-data-sm leading-none whitespace-nowrap"
                    :class="m.isDone ? 'text-primary' : 'text-on-surface-variant'"
                  >
                    {{ m.alt }}m
                  </span>
                </div>
              </div>
              <div class="w-0.5 h-2.5 bg-gradient-to-b from-outline-variant/60 to-transparent mx-auto"></div>
            </template>
          </template>
        </div>

        <!-- Interactive Probe Beacon Marker -->
        <div
          v-if="probeScreenPos"
          class="probe-beacon-marker absolute pointer-events-none z-40 will-change-transform"
          :style="{
            left: `${probeScreenPos.x}px`,
            top: `${probeScreenPos.y}px`,
            transform: 'translate(-50%, -50%)',
          }"
        >
          <!-- Ground Target Radar Anchor centered at (x, y) -->
          <div class="relative w-4 h-4 flex items-center justify-center">
            <span class="absolute -inset-2 rounded-full border border-primary/60 shadow-[0_0_10px_#4edea3]"></span>
            <span class="absolute -inset-6 rounded-full border border-primary/40 "></span>
            <span class="w-3.5 h-3.5 rounded-full bg-primary shadow-[0_0_14px_#4edea3]"></span>

            <!-- Dropline and Tooltip Capsule extending upward -->
            <div class="absolute bottom-4 left-1/2 -translate-x-1/2 flex flex-col items-center pointer-events-none mb-1">
              <div class="px-2.5 py-1.5 rounded-xl frost-glass-highlight border border-primary text-on-surface shadow-[0_0_24px_rgba(78,222,163,0.5)] flex items-center gap-2 select-none pointer-events-auto">
                <span class="px-1.5 py-0.5 rounded bg-primary text-[#0a0e17] text-[10px] font-mono font-black">
                  #{{ probeScreenPos.seq || 1 }}
                </span>
                <div class="flex flex-col text-left">
                  <span class="text-[12px] font-bold text-on-surface tracking-tight whitespace-nowrap">
                    {{ probeScreenPos.name }}
                  </span>
                  <span class="text-[10px] font-mono text-primary font-bold whitespace-nowrap">
                    {{ probeScreenPos.alt_m }}m 路 璺濊捣鐐?{{ probeScreenPos.km }}km
                  </span>
                </div>
                <span
                  class="px-1 py-0.5 rounded text-[9px] font-mono border whitespace-nowrap"
                  :class="probeScreenPos.unc ? 'bg-amber-500/20 text-amber-300 border-amber-500/40' : 'bg-primary/20 text-primary border-primary/40'"
                >
                  {{ probeScreenPos.unc ? '浼扮畻' : 'GPS' }}
                </span>
              </div>
              <div class="w-0.5 h-5 bg-gradient-to-t from-primary/90 to-primary/40"></div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Floating Top-Left Minimal View Coordinates HUD -->
    <div class="absolute left-margin top-44 z-30 pointer-events-none flex flex-col gap-1">
      <div class="px-2.5 py-1 rounded-md bg-surface-container-lowest/85 backdrop-blur-md border border-outline-variant/30 inline-flex items-center gap-2 shadow-lg">
        <span class="w-1.5 h-1.5 rounded-full bg-primary shadow-[0_0_6px_#4edea3]"></span>
        <span class="text-label-data-sm font-label-data-sm text-on-surface-variant tracking-wider">
          {{ selectedHudCoordinate }}
        </span>
      </div>
      <!-- Layer Badge -->
      <div class="px-2 py-0.5 rounded bg-surface-container-lowest/70 backdrop-blur-sm border border-outline-variant/20 inline-flex items-center gap-1.5 self-start shadow">
        <span class="text-[10px] text-primary">馃椇锔?{{ currentLayerMeta.name }}</span>
        <span class="text-[9px] font-label-data-sm text-outline">Z{{ mapZoom.toFixed(1) }}</span>
      </div>
    </div>

    <!-- Floating Right Instrument Controls (Stitch 99% High Fidelity) -->
    <div class="absolute right-margin top-44 z-30 flex flex-col gap-space-sm items-center">
      <!-- 3D Topo Toggle Button -->
      <button
        @click="toggle3D"
        class="w-9.5 h-9.5 rounded-full frost-glass flex flex-col items-center justify-center text-on-surface hover:text-primary active:scale-95 shadow-xl transition-all border border-outline-variant/30 group"
        :class="is3D ? 'border-secondary glow-secondary text-secondary' : ''"
        title="鍒囨崲 3D 鎷撴墤瑙嗚"
      >
        <span class="material-symbols-outlined text-[20px]" :class="is3D ? 'text-primary' : 'text-secondary'">view_in_ar</span>
        <span class="text-[9px] font-label-data-sm font-bold text-on-surface-variant group-hover:text-primary leading-tight">3D</span>
      </button>

      <!-- Layer Switcher Button -->
      <button
        @click="cycleLayer"
        class="w-9.5 h-9.5 rounded-full frost-glass flex items-center justify-center text-on-surface hover:text-primary active:scale-95 shadow-xl transition-all border border-outline-variant/30"
        :title="`鍒囨崲搴曞浘: ${currentLayerMeta.name}`"
      >
        <span class="material-symbols-outlined text-[22px] text-primary">{{ currentLayerMeta.icon }}</span>
      </button>

      <!-- Zoom In (+) -->
      <button
        @click="zoomIn"
        class="w-9.5 h-9.5 rounded-full frost-glass flex items-center justify-center text-on-surface hover:text-primary active:scale-95 shadow-xl transition-all border border-outline-variant/30"
        title="鏀惧ぇ鍦板浘"
      >
        <span class="material-symbols-outlined text-[20px]">add</span>
      </button>

      <!-- Zoom Out (-) -->
      <button
        @click="zoomOut"
        class="w-9.5 h-9.5 rounded-full frost-glass flex items-center justify-center text-on-surface hover:text-primary active:scale-95 shadow-xl transition-all border border-outline-variant/30"
        title="缂╁皬鍦板浘"
      >
        <span class="material-symbols-outlined text-[20px]">remove</span>
      </button>

      <!-- Compass with Elevation Dial -->
      <div
        @click="resetNorth"
        class="w-11 h-16 rounded-full frost-glass flex flex-col items-center justify-between py-1.5 shadow-xl border border-outline-variant/30 cursor-pointer active:scale-95 transition-all"
        title="鎸囧寳閽?/ 鏍囬珮 / 閲嶇疆涓績"
      >
        <span class="text-[10px] font-label-data-sm font-bold text-error tracking-tighter">N</span>
        <span class="material-symbols-outlined text-[18px] text-primary rotate-45">navigation</span>
        <span class="text-[8px] font-label-data-sm text-on-surface-variant">{{ selectedElevationDial }}</span>
      </div>

      <!-- GPS Recenter Button -->
      <button
        @click="recenterLocation"
        class="w-9.5 h-9.5 rounded-full frost-glass flex items-center justify-center text-primary active:scale-95 shadow-xl transition-all border border-primary/30 glow-primary"
        title="閲嶇疆瑙嗚 / 瀹氫綅涓績"
      >
        <span class="material-symbols-outlined text-[20px]">my_location</span>
      </button>
    </div>
  </main>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue';
import { useMountainStore, getMountainCoordinate } from '@/stores/mountainStore.js';
import { useCheckinStore, derivedNums } from '@/stores/checkinStore.js';
import { useRegionStore } from '@/stores/regionStore.js';
import waypointsData from '@/data/waypoints.json' with { type: 'json' };

const emit = defineEmits(['mountain-select', 'map-click', 'map-pan']);

const mountainStore = useMountainStore();
const checkinStore = useCheckinStore();
const regionStore = useRegionStore();
const mapContainerRef = ref(null);

// ================= Web Mercator Core Projection =================
function lonToX(lon, z) {
  return ((lon + 180) / 360) * Math.pow(2, z) * 256;
}

function latToY(lat, z) {
  const s = Math.sin((lat * Math.PI) / 180);
  return (0.5 - Math.log((1 + s) / (1 - s)) / (4 * Math.PI)) * Math.pow(2, z) * 256;
}

function xToLon(x, z) {
  return (x / (Math.pow(2, z) * 256)) * 360 - 180;
}

function yToLat(y, z) {
  const n = Math.PI - (2 * Math.PI * y) / (Math.pow(2, z) * 256);
  return (180 / Math.PI) * Math.atan(0.5 * (Math.exp(n) - Math.exp(-n)));
}

// ================= Map Layer Sources =================
const TILE_LAYERS = [
  {
    id: 'amap-night',
    name: '鏋佸厜榛戞洔鐭虫殫澶?,
    icon: 'dark_mode',
    url: (z, x, y) =>
      `https://webrd0${1 + ((x + y) % 4)}.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=8&x=${x}&y=${y}&z=${z}`,
    subUrl: null,
    attrib: '漏 楂樺痉鍦板浘 路 鐭㈤噺鏆楀'
  },
  {
    id: 'amap-sat',
    name: '楂樻竻閬ユ劅鍗槦',
    icon: 'satellite_alt',
    url: (z, x, y) =>
      `https://webst0${1 + ((x + y) % 4)}.is.autonavi.com/appmaptile?style=6&x=${x}&y=${y}&z=${z}`,
    subUrl: (z, x, y) =>
      `https://wprd0${1 + ((x + y) % 4)}.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=8&x=${x}&y=${y}&z=${z}`,
    attrib: '漏 楂樺痉鍦板浘 路 鍗槦褰卞儚'
  }
];

const layerMode = ref(0);
const currentLayerMeta = computed(() => TILE_LAYERS[layerMode.value]);

// ================= Reactive Navigation States =================
const currentCenterLng = ref(regionStore.currentRegion.center.lng);
const currentCenterLat = ref(regionStore.currentRegion.center.lat);
const mapZoom = ref(regionStore.currentRegion.defaultZoom || 9);
const is3D = ref(false);

// Level of Detail (LOD) display mode based on mapZoom
// >= 9.8: 'detailed' (杩戞櫙鐗瑰啓锛氬湴鍚?+ 鏍囬珮 + 鍛煎惛鐐?+ 涓嬪瀭绾?
// < 9.8: 'compact' (涓繙鏅細绮捐嚧绱у噾鍗曡鍦板悕鑳跺泭锛屼紭闆呬笉鎶㈤暅)
const lodMode = computed(() => {
  if (mapZoom.value >= 9.8) return 'detailed';
  return 'compact';
});

// markerScale: 骞虫粦鑷€傚簲閫傚害缂╂斁绯绘暟锛屼弗鏍艰缃斁澶т笂闄愶紝闃叉鍦板浘鏀惧ぇ鏃舵爣璁扮偣鏃犺妭鍒惰啫鑳€
// 鍦?Z6.0 淇濇寔 0.80x锛屽湪 Z9.0 淇濇寔 0.90x锛屾渶楂樹弗鏍煎皝椤跺湪 0.95x
const markerScale = computed(() => {
  const z = mapZoom.value;
  const clampedZ = Math.max(6.0, Math.min(12.0, z));
  const s = 0.80 + (clampedZ - 6.0) * ((0.95 - 0.80) / (12.0 - 6.0));
  return Math.min(0.95, Math.round(s * 100) / 100);
});

function getMarkerStyle(m) {
  const isSelected = m.id === mountainStore.selectedMountainId;
  // 涓ユ牸涓婇檺姝婚攣锛氶€変腑鐘舵€佹渶楂樺皝椤跺湪 1.0x锛堢粷涓嶆棤闄愯啫鑳€锛侊級锛屾湭閫変腑鐘舵€佹渶楂?0.95x
  const currentScale = isSelected ? Math.min(1.0, markerScale.value) : markerScale.value;
  return {
    left: `${m.x}px`,
    top: `${m.y}px`,
    transform: `translate(-50%, -50%) scale(${currentScale})`,
    transformOrigin: '50% 65%',
  };
}

// Container dimensions
const containerWidth = ref(window.innerWidth || 390);
const containerHeight = ref(window.innerHeight || 844);

function updateDimensions() {
  if (mapContainerRef.value) {
    containerWidth.value = mapContainerRef.value.clientWidth || window.innerWidth || 390;
    containerHeight.value = mapContainerRef.value.clientHeight || window.innerHeight || 844;
  }
}

// Watch region change to update map center
watch(
  () => regionStore.currentRegionId,
  () => {
    const r = regionStore.currentRegion;
    if (r) {
      currentCenterLng.value = r.center.lng;
      currentCenterLat.value = r.center.lat;
      mapZoom.value = r.defaultZoom || 9;
    }
  }
);

// Integer tile zoom level & fractional scale (continuous scale without reverse jump)
const intZoom = computed(() => Math.floor(mapZoom.value));
const zoomScale = computed(() => Math.pow(2, mapZoom.value - intZoom.value));

// Compute visible tiles dynamically
const visibleTiles = computed(() => {
  const z = intZoom.value;
  const maxTile = Math.pow(2, z) - 1;
  const cx = lonToX(currentCenterLng.value, z);
  const cy = latToY(currentCenterLat.value, z);

  const w = containerWidth.value;
  const h = containerHeight.value;

  const left = cx - w / 2;
  const top = cy - h / 2;

  // Render with 1 tile padding to prevent seams
  const x0 = Math.floor(left / 256) - 1;
  const x1 = Math.floor((left + w) / 256) + 1;
  const y0 = Math.floor(top / 256) - 1;
  const y1 = Math.floor((top + h) / 256) + 1;

  const tiles = [];
  const layer = currentLayerMeta.value;

  for (let ty = y0; ty <= y1; ty++) {
    if (ty < 0 || ty > maxTile) continue;
    for (let tx = x0; tx <= x1; tx++) {
      const wx = ((tx % (maxTile + 1)) + (maxTile + 1)) % (maxTile + 1);
      tiles.push({
        key: `${layer.id}-${z}-${tx}-${ty}`,
        left: Math.round(tx * 256 - left),
        top: Math.round(ty * 256 - top),
        url: layer.url(z, wx, ty),
        subUrl: layer.subUrl ? layer.subUrl(z, wx, ty) : null
      });
    }
  }
  return tiles;
});

// Extract representative coordinates for all mountains
const mountainCoordinates = computed(() => {
  const map = {};
  mountainStore.mountains.forEach((m) => {
    const coord = getMountainCoordinate(m, waypointsData);
    const dn = derivedNums(m);

    map[m.id] = {
      id: m.id,
      name: m.name,
      lat: coord.lat,
      lng: coord.lng,
      alt: dn.alt || 2000,
      difficulty: m.difficulty
    };
  });
  return map;
});

// Calculate screen coordinates (x, y) for all mountains
const mountainPositions = computed(() => {
  const z = intZoom.value;
  const cx = lonToX(currentCenterLng.value, z);
  const cy = latToY(currentCenterLat.value, z);

  const left = cx - containerWidth.value / 2;
  const top = cy - containerHeight.value / 2;

  return mountainStore.mountains.map((m) => {
    const coord = mountainCoordinates.value[m.id] || {
      lat: 30.65,
      lng: 103.35,
      alt: 2000,
      difficulty: 'L2'
    };

    const px = lonToX(coord.lng, z) - left;
    const py = latToY(coord.lat, z) - top;

    return {
      id: m.id,
      name: m.name,
      x: Math.round(px),
      y: Math.round(py),
      alt: coord.alt,
      difficulty: coord.difficulty,
      isDone: checkinStore.isDone(m.id)
    };
  });
});

// Transform style for 3D and continuous pinch/scale
const worldTransformStyle = computed(() => {
  let transform = `scale(${zoomScale.value})`;
  if (is3D.value) {
    transform = `perspective(900px) rotateX(24deg) ${transform}`;
  }
  return {
    transform,
    transformOrigin: 'center center',
    transformStyle: 'preserve-3d',
    backfaceVisibility: 'hidden',
    WebkitBackfaceVisibility: 'hidden',
    willChange: 'transform'
  };
});

function isMountainVisible(mountainId) {
  return mountainStore.filteredMountains.some((m) => m.id === mountainId);
}

// HUD text
const selectedHudCoordinate = computed(() => {
  const m = mountainStore.selectedMountain;
  if (!m) {
    return `${regionStore.currentRegion.name.toUpperCase()} 路 TOPO 1:25,000`;
  }
  const c = mountainCoordinates.value[m.id];
  if (c && c.lat && c.lng) {
    const latStr = `${c.lat.toFixed(2)}掳N`;
    const lngStr = `${c.lng.toFixed(2)}掳E`;
    return `${m.name.toUpperCase()} 路 ${latStr} ${lngStr}`;
  }
  return `${regionStore.currentRegion.name.toUpperCase()} 路 TOPO 1:25,000`;
});

const selectedElevationDial = computed(() => {
  const m = mountainStore.selectedMountain;
  if (!m) return '3.1k';
  const dn = derivedNums(m);
  const alt = dn.alt || 3000;
  return `${(alt / 1000).toFixed(1)}k`;
});

// Marker Click
function handleMarkerClick(id) {
  if (isMapMoved) return; // 绉诲姩/缂╂斁鎵嬪娍鏈熼棿鎷︽埅璇Е鐐瑰嚮
  mountainStore.selectMountain(id);
  emit('mountain-select', id);
  panToMountain(id);
}

// ================= Gesture & Touch Handling =================
const isDragging = ref(false);
const isPinching = ref(false);
const isInteracting = computed(() => isDragging.value || isPinching.value);

let lastMouseX = 0;
let lastMouseY = 0;
let mouseDownX = 0;
let mouseDownY = 0;
let isMapMoved = false;

function onMouseDown(e) {
  if (e.target.closest('button')) return;
  cancelPanAnimation();
  isDragging.value = true;
  isMapMoved = false;
  mouseDownX = e.clientX;
  mouseDownY = e.clientY;
  lastMouseX = e.clientX;
  lastMouseY = e.clientY;
}

function onMouseMove(e) {
  if (!isDragging.value) return;
  const dx = e.clientX - lastMouseX;
  const dy = e.clientY - lastMouseY;
  if (!isMapMoved && Math.hypot(e.clientX - mouseDownX, e.clientY - mouseDownY) > 5) {
    isMapMoved = true;
    emit('map-pan');
  }
  lastMouseX = e.clientX;
  lastMouseY = e.clientY;

  applyPanDelta(dx, dy);
}

function onMouseUp(e) {
  flushPanDelta();
  if (isDragging.value && !isMapMoved) {
    emit('map-click');
  }
  isDragging.value = false;
  if (isMapMoved) {
    setTimeout(() => {
      isMapMoved = false;
    }, 60);
  }
}

function handleMapClick(e) {
  if (e.target.closest('button') || e.target.closest('.mountain-marker')) return;
  if (!isMapMoved) {
    emit('map-click');
  }
}

let lastTouchX = 0;
let lastTouchY = 0;
let mapTouchStartX = 0;
let mapTouchStartY = 0;
let initialPinchDist = 0;
let initialPinchZoom = 9;
let pinchRafId = null;
let pendingPinchZoom = null;

function getPinchDist(e) {
  const t1 = e.touches[0];
  const t2 = e.touches[1];
  return Math.hypot(t1.clientX - t2.clientX, t1.clientY - t2.clientY);
}

function onTouchStart(e) {
  if (e.target.closest('button')) return;
  cancelPanAnimation();

  if (e.touches.length === 2) {
    // 鍙屾寚瑙︽帶锛氫竴寰嬪紑鍚缉鏀炬ā寮忥紝缁濅笉鍙楁爣璁扮偣锛圡arker锛夐樆鏂紒
    isDragging.value = false;
    isPinching.value = true;
    isMapMoved = true;
    initialPinchDist = getPinchDist(e);
    initialPinchZoom = mapZoom.value;
  } else if (e.touches.length === 1) {
    // 鍗曟寚瑙︽帶锛氬嵆浣挎寜鍦ㄧ偣浣嶄笂涔熸甯歌褰曡捣鐐癸紙杞昏Е閫変腑锛屾嫋鍔ㄥ钩绉伙級
    isPinching.value = false;
    isDragging.value = true;
    isMapMoved = false;
    mapTouchStartX = e.touches[0].clientX;
    mapTouchStartY = e.touches[0].clientY;
    lastTouchX = e.touches[0].clientX;
    lastTouchY = e.touches[0].clientY;
  }
}

function onTouchMove(e) {
  if (e.touches.length === 1 && isDragging.value) {
    const dx = e.touches[0].clientX - lastTouchX;
    const dy = e.touches[0].clientY - lastTouchY;
    if (Math.hypot(e.touches[0].clientX - mapTouchStartX, e.touches[0].clientY - mapTouchStartY) > 8) {
      if (!isMapMoved) {
        isMapMoved = true;
        emit('map-pan');
      }
    }
    lastTouchX = e.touches[0].clientX;
    lastTouchY = e.touches[0].clientY;
    applyPanDelta(dx, dy);
  } else if (e.touches.length === 2 && initialPinchDist > 0) {
    const dist = getPinchDist(e);
    const newZoom = initialPinchZoom + Math.log2(dist / initialPinchDist);
    pendingPinchZoom = Math.max(6, Math.min(14, newZoom));

    if (!pinchRafId) {
      pinchRafId = requestAnimationFrame(() => {
        pinchRafId = null;
        if (pendingPinchZoom !== null) {
          mapZoom.value = pendingPinchZoom;
          pendingPinchZoom = null;
        }
      });
    }
  }
}

function onTouchEnd(e) {
  if (e.target?.closest?.('button')) {
    isDragging.value = false;
    isPinching.value = false;
    return;
  }
  flushPanDelta();
  if (pinchRafId) {
    cancelAnimationFrame(pinchRafId);
    pinchRafId = null;
  }
  if (pendingPinchZoom !== null) {
    mapZoom.value = pendingPinchZoom;
    pendingPinchZoom = null;
  }
  if (isDragging.value && !isMapMoved) {
    emit('map-click');
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

function onWheel(e) {
  const delta = e.deltaY > 0 ? -0.25 : 0.25;
  const newZoom = mapZoom.value + delta;
  mapZoom.value = Math.max(6, Math.min(14, newZoom));
}

let pendingDx = 0;
let pendingDy = 0;
let rafId = null;

function applyPanDelta(dx, dy) {
  pendingDx += dx;
  pendingDy += dy;
  if (!rafId) {
    rafId = requestAnimationFrame(() => {
      rafId = null;
      if (pendingDx === 0 && pendingDy === 0) return;
      const z = mapZoom.value;
      const cx = lonToX(currentCenterLng.value, z) - pendingDx;
      const cy = latToY(currentCenterLat.value, z) - pendingDy;
      pendingDx = 0;
      pendingDy = 0;
      currentCenterLng.value = xToLon(cx, z);
      currentCenterLat.value = yToLat(cy, z);
    });
  }
}

function flushPanDelta() {
  if (rafId) {
    cancelAnimationFrame(rafId);
    rafId = null;
  }
  if (pendingDx !== 0 || pendingDy !== 0) {
    const z = mapZoom.value;
    const cx = lonToX(currentCenterLng.value, z) - pendingDx;
    const cy = latToY(currentCenterLat.value, z) - pendingDy;
    pendingDx = 0;
    pendingDy = 0;
    currentCenterLng.value = xToLon(cx, z);
    currentCenterLat.value = yToLat(cy, z);
  }
}

function zoomIn() {
  mapZoom.value = Math.min(14, Math.round((mapZoom.value + 1.0) * 10) / 10);
}

function zoomOut() {
  mapZoom.value = Math.max(6, Math.round((mapZoom.value - 1.0) * 10) / 10);
}

function toggle3D() {
  is3D.value = !is3D.value;
}

function cycleLayer() {
  layerMode.value = (layerMode.value + 1) % TILE_LAYERS.length;
}

function resetNorth() {
  is3D.value = false;
  recenterLocation();
}

let panAnimationId = null;

function cancelPanAnimation() {
  if (panAnimationId) {
    cancelAnimationFrame(panAnimationId);
    panAnimationId = null;
  }
}

// 璁＄畻閬垮紑椤堕儴鎼滅储鏍忥紙绾?150px锛変笌搴曢儴鍗＄墖鎶藉眽锛堢害 430px锛夊悗鐨勩€屽紑闃斿ぉ闄呭彲瑙嗕腑蹇冦€嶅瀭鐩村亸绉婚噺
function getVisibleSkyOffsetY() {
  const h = containerHeight.value;
  // 椤堕儴鎼滅储鏍忎笌绛涢€夎兌鍥婂崰鐢ㄧ害 150px
  const topOccupied = 150;
  // 搴曢儴鎶藉眽鍦ㄥ崐灞曞紑鎬佷笅鍗犵敤楂樺害绾?364px锛屽惛搴?66px锛屽叡璁?430px
  const sheetHeight = Math.max(180, Math.min(364, h - 180));
  const bottomOccupied = 66 + sheetHeight;

  // 寮€闃斿尯鍩熶笂鐣屼笌涓嬬晫
  const visibleTop = topOccupied;
  const visibleBottom = Math.max(visibleTop + 80, h - bottomOccupied);
  const visibleCenter = (visibleTop + visibleBottom) / 2;

  // 鐩稿灞忓箷鐗╃悊涓績鐨勫悜涓婂亸绉婚噺
  const screenCenter = h / 2;
  const offsetY = Math.round(screenCenter - visibleCenter);
  // 瀹夊叏闄愬埗锛氭爣鍑嗙Щ鍔ㄧ绾︿负 135px ~ 140px锛屽眳涓偓娴簬寮€闃斿ぉ闄呬腑澶?
  return Math.max(0, Math.min(180, offsetY));
}

function recenterLocation() {
  cancelPanAnimation();
  const r = regionStore.currentRegion;
  // 閲嶇疆鍏ㄧ渷/鍏ㄦ櫙瑙嗚鏃讹紝鍚戜笂寰皟 50px锛岀‘淇濆崡閮ㄤ綆娴锋嫈灞卞嘲涓嶈创搴?
  panToLocation(r.center.lng, r.center.lat, r.defaultZoom || 9, 380, 50);
}

function panToLocation(targetLng, targetLat, targetZoom = null, duration = 380, offsetY = 0) {
  cancelPanAnimation();

  const startLng = currentCenterLng.value;
  const startLat = currentCenterLat.value;
  const startZoom = mapZoom.value;
  const endZoom = targetZoom || startZoom;

  // 鏍规嵁 WebMercator 鎶曞奖璁＄畻鍖呭惈鍙澶╅檯鍋忕Щ鐨勭洰鏍囩含搴︼紝纭繚鍔ㄧ敾缁堢偣鏍囪鐐圭簿鍑嗚惤浜庡紑闃旇閲庝腑蹇?
  const finalLat =
    offsetY !== 0
      ? yToLat(latToY(targetLat, endZoom) + offsetY, endZoom)
      : targetLat;

  const diffLng = targetLng - startLng;
  const diffLat = finalLat - startLat;
  const diffZoom = endZoom - startZoom;

  // Tiny delta check: if already at the target, finish immediately
  if (Math.abs(diffLng) < 0.00005 && Math.abs(diffLat) < 0.00005 && Math.abs(diffZoom) < 0.01) {
    currentCenterLng.value = targetLng;
    currentCenterLat.value = finalLat;
    if (targetZoom) mapZoom.value = targetZoom;
    return;
  }

  const startTime = performance.now();

  function step(now) {
    const elapsed = now - startTime;
    const progress = Math.min(1, elapsed / duration);
    // Cubic ease-out: 1 - pow(1 - progress, 3)
    const ease = 1 - Math.pow(1 - progress, 3);

    currentCenterLng.value = startLng + diffLng * ease;
    currentCenterLat.value = startLat + diffLat * ease;
    if (diffZoom !== 0) {
      mapZoom.value = startZoom + diffZoom * ease;
    }

    if (progress < 1) {
      panAnimationId = requestAnimationFrame(step);
    } else {
      currentCenterLng.value = targetLng;
      currentCenterLat.value = finalLat;
      if (targetZoom) mapZoom.value = targetZoom;
      panAnimationId = null;
    }
  }

  panAnimationId = requestAnimationFrame(step);
}

function panToMountain(id, targetZoom = null, customOffsetY = null) {
  const coord = mountainCoordinates.value[id];
  if (coord && typeof coord.lng === 'number' && typeof coord.lat === 'number') {
    const offsetY = customOffsetY !== null ? customOffsetY : getVisibleSkyOffsetY();
    panToLocation(coord.lng, coord.lat, targetZoom, 380, offsetY);
  }
}

// Watch selected mountain change to auto-pan
watch(
  () => mountainStore.selectedMountainId,
  (newId) => {
    if (!newId) return;
    panToMountain(newId);
  }
);

function onTileError(e) {
  // Gracefully fallback to dark tile placeholder
  if (e?.target) {
    e.target.style.opacity = '0.1';
  }
}

// ================= Interactive Probe Beacon State & Handlers =================
const probeWaypoint = ref(null);

const probeScreenPos = computed(() => {
  if (!probeWaypoint.value) return null;
  const rawLng = parseFloat(probeWaypoint.value.lng);
  const rawLat = parseFloat(probeWaypoint.value.lat);
  if (isNaN(rawLng) || isNaN(rawLat)) return null;

  const z = intZoom.value;
  const cx = lonToX(currentCenterLng.value, z);
  const cy = latToY(currentCenterLat.value, z);

  const left = cx - containerWidth.value / 2;
  const top = cy - containerHeight.value / 2;

  const px = lonToX(rawLng, z) - left;
  const py = latToY(rawLat, z) - top;

  return {
    x: Math.round(px),
    y: Math.round(py),
    name: probeWaypoint.value.name,
    alt_m: probeWaypoint.value.alt_m,
    km: probeWaypoint.value.km,
    seq: probeWaypoint.value.seq,
    unc: probeWaypoint.value.unc
  };
});

function setProbeMarker(waypoint) {
  if (!waypoint) {
    probeWaypoint.value = null;
    return;
  }
  probeWaypoint.value = waypoint;
  const rawLng = parseFloat(waypoint.lng);
  const rawLat = parseFloat(waypoint.lat);
  if (!isNaN(rawLng) && !isNaN(rawLat)) {
    // 骞虫粦灏嗗湴鍥捐鍙ｅ井璋冨眳涓紝鐣欏嚭涓婃柟澶╅檯寮€闃斿彲瑙嗗甫
    const offsetY = getVisibleSkyOffsetY();
    panToLocation(rawLng, rawLat, Math.max(mapZoom.value, 10.5), 320, offsetY);
  }
}

function clearProbe() {
  probeWaypoint.value = null;
}

onMounted(() => {
  updateDimensions();
  window.addEventListener('resize', updateDimensions);

  // Initial center on the default selected mountain (Longquanshan)
  const defaultId = mountainStore.selectedMountainId;
  if (defaultId && mountainCoordinates.value[defaultId]) {
    const c = mountainCoordinates.value[defaultId];
    currentCenterLng.value = c.lng;
    const z = mapZoom.value;
    const offsetY = getVisibleSkyOffsetY();
    currentCenterLat.value = yToLat(latToY(c.lat, z) + offsetY, z);
  }
});

onUnmounted(() => {
  cancelPanAnimation();
  window.removeEventListener('resize', updateDimensions);
});

defineExpose({
  recenterLocation,
  panToLocation,
  panToMountain,
  handleMarkerClick,
  cycleLayer,
  zoomIn,
  zoomOut,
  setProbeMarker,
  clearProbe
});
</script>

<style scoped>
.frost-glass {
  background: var(--frost-bg, rgba(16, 21, 33, 0.75));
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
}

.frost-glass-highlight {
  background: var(--frost-highlight-bg, rgba(23, 30, 48, 0.85));
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
}

.glow-primary {
  box-shadow: 0 0 20px -3px rgba(78, 222, 163, 0.35);
}

.glow-secondary {
  box-shadow: 0 0 20px -3px rgba(76, 215, 246, 0.35);
}

@keyframes beaconPulse {
  0% {
    transform: scale(0.95);
    opacity: 0.6;
  }
  50% {
    transform: scale(1.35);
    opacity: 0.15;
  }
  100% {
    transform: scale(0.95);
    opacity: 0.6;
  }
}

. {
  animation: beaconPulse 2.8s ease-in-out infinite;
}

.map-tile-dark {
  filter: invert(92%) hue-rotate(180deg) brightness(88%) contrast(125%) saturate(75%);
  will-change: transform;
  transform: translateZ(0);
}

.mountain-marker {
  transition: transform 0.18s cubic-bezier(0.2, 0, 0, 1);
  will-change: left, top;
}

.mountain-marker.is-interacting {
  transition: none !important;
}
</style>
