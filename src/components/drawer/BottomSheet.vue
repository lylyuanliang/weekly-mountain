<template>
  <section
    class="bottom-sheet fixed bottom-[66px] inset-x-0 z-40 max-w-md mx-auto pointer-events-auto select-none"
    :style="drawerStyle"
  >
    <!-- Drawer Container (Solid Dark Obsidian with 0% Blur GPU Penalty) -->
    <div
      ref="sheetContainerRef"
      @touchstart="onTouchStart"
      @touchmove="onTouchMove"
      @touchend="onTouchEnd"
      @touchcancel="onTouchEnd"
      @mousedown="onMouseDown"
      @mousemove="onMouseMove"
      @mouseup="onMouseUp"
      @mouseleave="onMouseUp"
      style="overscroll-behavior: none; -webkit-overflow-scrolling: touch;"
      class="h-full rounded-t-3xl bg-[#171b26] border-t border-outline-variant/30 shadow-[0_-12px_40px_rgba(0,0,0,0.7)] pt-2 pb-2 px-margin flex flex-col gap-1.5 overflow-hidden"
    >
      <!-- Drawer Drag Indicator Bar -->
      <div
        @click="cycleSnapState"
        class="drawer-handle w-12 h-1 rounded-full bg-outline-variant/60 mx-auto cursor-grab active:cursor-grabbing hover:bg-outline-variant transition-colors flex-shrink-0 mt-0.5 mb-0.5"
        title="轻扫、拖动或点击切换高度"
      ></div>

      <!-- ================= COLLAPSED STATE: MINIMAL PEEK BAR (Height ~66px) ================= -->
      <div
        v-if="snapState === 'collapsed'"
        @click="expandToHalf"
        class="flex items-center justify-between text-body-sm font-semibold text-on-surface py-0.5 px-0.5 cursor-pointer flex-1"
      >
        <div class="flex items-center gap-2 overflow-hidden">
          <span class="w-2.5 h-2.5 rounded-full bg-primary glow-primary shadow-[0_0_6px_#4edea3] flex-shrink-0"></span>
          <div class="flex items-baseline gap-1.5 overflow-hidden">
            <span class="text-on-surface text-body-sm font-bold truncate">
              {{ isSearchActive ? `搜索结果: 匹配 ${mountainStore.filteredMountains.length} 座` : (activeMountainName || `全景探索 ${mountainStore.filteredMountains.length} 座山峰`) }}
            </span>
            <span class="text-[11px] text-on-surface-variant font-normal hidden xs:inline truncate">
              轻触或上滑查看卡片
            </span>
          </div>
        </div>
        <button
          @click.stop="expandToHalf"
          class="flex items-center gap-1 px-3.5 py-1.5 rounded-full bg-primary/20 hover:bg-primary/30 text-primary text-body-sm font-bold border border-primary/40 active:scale-95 transition-all flex-shrink-0 shadow-sm"
          title="展开山峰卡片"
        >
          <span>展开</span>
          <span class="material-symbols-outlined text-[16px]">expand_less</span>
        </button>
      </div>

      <!-- ================= HALF & EXPANDED STATES ================= -->
      <template v-else>
        <!-- Section Header: Peaks Count & Quick Collapse Button -->
        <div class="flex items-center justify-between pt-0.5 flex-shrink-0">
          <div v-if="isSearchActive" class="flex items-center gap-2">
            <div class="w-6 h-6 rounded-lg bg-primary/20 border border-primary/30 flex items-center justify-center text-primary flex-shrink-0 shadow-sm">
              <span class="material-symbols-outlined text-[15px]">manage_search</span>
            </div>
            <div class="flex items-baseline gap-1.5">
              <h2 class="text-headline-md font-headline-md text-on-surface font-bold tracking-tight">搜索结果</h2>
              <span class="text-label-data-sm font-label-data-sm text-primary font-semibold px-2 py-0.5 rounded-md bg-primary/10 border border-primary/20">
                匹配 {{ mountainStore.filteredMountains.length }} 座
              </span>
            </div>
          </div>
          <div v-else class="flex items-baseline gap-2">
            <h2 class="text-headline-md font-headline-md text-on-surface font-bold tracking-tight">Active Peaks</h2>
            <span class="text-label-data-sm font-label-data-sm text-primary font-semibold px-2 py-0.5 rounded-md bg-primary/10">
              {{ mountainStore.filteredMountains.length }} TRACKS
            </span>
          </div>

          <div class="flex items-center gap-2">
            <!-- Quick Clear Search Button in Search Mode -->
            <button
              v-if="isSearchActive"
              type="button"
              @click="clearSearch"
              class="flex items-center gap-1 px-2.5 py-1 rounded-full bg-surface-container-high hover:bg-surface-bright text-primary active:scale-95 transition-all border border-primary/30 text-caption font-semibold cursor-pointer"
              title="清除搜索关键词"
            >
              <span class="material-symbols-outlined text-[14px]">close</span>
              <span>清除搜索</span>
            </button>
            <div v-else class="hidden xs:flex items-center gap-1.5 text-on-surface-variant text-caption">
              <span class="material-symbols-outlined text-secondary text-[16px]">filter_drama</span>
              <span>Live Radar</span>
            </div>

            <!-- Explicit Collapse Button to View Full Map -->
            <button
              @click.stop="collapse"
              aria-label="收起卡片以查看大地图"
              class="flex items-center gap-1 px-2.5 py-1 rounded-full bg-surface-container-low text-on-surface-variant hover:text-primary active:scale-95 transition-all border border-outline-variant/30 text-caption font-semibold"
              title="降到最低以查看大地图"
            >
              <span>收起大图</span>
              <span class="material-symbols-outlined text-[16px]">expand_more</span>
            </button>
          </div>
        </div>

        <!-- Weather Bulletin Banner (Hidden in Search Mode for Maximum Card Visibility) -->
        <div
          v-if="!isSearchActive"
          class="w-full px-3 py-2 rounded-xl bg-surface-container-low/90 border border-outline-variant/30 flex items-center gap-2.5 flex-shrink-0 transition-opacity duration-200"
        >
          <span class="material-symbols-outlined text-tertiary-fixed-dim text-[18px] flex-shrink-0">warning</span>
          <p class="text-caption font-caption text-on-surface-variant truncate">
            <strong class="text-on-surface font-semibold">Balang Pass:</strong> 实时路况 · 巴朗山及 3800m+ 积雪路段需防滑链
          </p>
        </div>

        <!-- Swipeable Hero Mountain Cards Carousel (Always Smooth Horizontal Stream) -->
        <div
          ref="carouselRef"
          class="flex gap-3.5 overflow-x-auto no-scrollbar -mx-margin px-margin pt-1 pb-2 snap-x snap-mandatory flex-1 items-start"
        >
          <HeroMountainCard
            v-for="mountain in mountainStore.filteredMountains"
            :key="mountain.id"
            :mountain="mountain"
            :is-active="mountain.id === mountainStore.selectedMountainId"
            @select="handleCardSelect"
            @detail="handleCardDetail"
            @weather="handleCardWeather"
          />

          <div
            v-if="mountainStore.filteredMountains.length === 0"
            class="w-full py-8 px-4 flex flex-col items-center justify-center text-center text-on-surface-variant gap-2 animate-fade-in"
          >
            <span class="material-symbols-outlined text-[36px] text-outline">{{ isSearchActive ? 'search_off' : 'terrain' }}</span>
            <p class="text-body-md font-bold text-on-surface">{{ isSearchActive ? '未搜索到匹配山峰' : '暂无匹配山峰' }}</p>
            <p class="text-caption text-on-surface-variant max-w-[280px] leading-relaxed">
              {{ isSearchActive ? `未找到与“${mountainStore.searchQuery}”相关的路线，建议尝试其他关键词。` : '当前收录以成都周边 0.5~4h 车程圈为主。如巴中光雾山等川北/川东远线名峰，可随时点击右下角反馈建议收录！' }}
            </p>
            <button
              @click="resetAllFilters"
              class="mt-1 px-4 py-1.5 rounded-full bg-surface-container-high text-primary text-body-sm font-semibold border border-primary/40 active:scale-95 shadow cursor-pointer"
            >
              {{ isSearchActive ? '清空搜索并查看全部' : '重置筛选条件' }}
            </button>
          </div>
        </div>
      </template>
    </div>
  </section>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue';
import { useMountainStore } from '@/stores/mountainStore.js';
import HeroMountainCard from '@/components/card/HeroMountainCard.vue';

const emit = defineEmits(['mountain-select', 'mountain-detail', 'mountain-weather', 'snap-change']);

const mountainStore = useMountainStore();
const carouselRef = ref(null);
const sheetContainerRef = ref(null);

// Snap states: 'collapsed' (54px minimal bar for full map) <-> 'half' (clamp 400px~460px for card carousel)
const snapState = ref('half');
const customHeight = ref(null);
const isDragging = ref(false);

const isSearchActive = computed(() => {
  return Boolean(mountainStore.searchQuery && mountainStore.searchQuery.trim().length > 0);
});

function clearSearch() {
  mountainStore.setSearch('');
}

function resetAllFilters() {
  mountainStore.setSearch('');
  mountainStore.resetFilters();
}

const activeMountainName = computed(() => {
  const m = mountainStore.selectedMountain;
  return m ? `${m.name} · ${m.altitude_m || ''}m` : null;
});

const drawerStyle = computed(() => {
  if (isDragging.value && customHeight.value !== null) {
    return {
      height: `${customHeight.value}px`,
      transition: 'none'
    };
  }

  // 智能自适应高度：全屏时最高 364px；软键盘弹出或视口高度变小（<520px）时，预留至少 180px 给顶栏与搜索框，避免顶到顶部
  const h =
    snapState.value === 'collapsed'
      ? '66px'
      : 'clamp(180px, min(364px, calc(100vh - 180px)), 364px)';

  return {
    height: h,
    transition: 'height 0.28s cubic-bezier(0.16, 1, 0.3, 1)'
  };
});

// PC / Handle toggle cycle
let wasDragged = false;

function cycleSnapState() {
  if (wasDragged) {
    wasDragged = false;
    return;
  }
  if (snapState.value === 'collapsed') {
    expandToHalf();
  } else {
    collapse();
  }
}

function collapse() {
  snapState.value = 'collapsed';
  emit('snap-change', 'collapsed');
}

function expandToHalf() {
  snapState.value = 'half';
  emit('snap-change', 'half');
}

function expandToFull() {
  // Alias to expandToHalf to prevent full screen layout breaks
  expandToHalf();
}

// Touch gesture tracking
let touchStartX = 0;
let touchStartY = 0;
let touchStartTime = 0;
let initialHeight = 0;
let touchDirection = null; // null | 'horizontal' | 'vertical'

function getCurrentPixelHeight() {
  if (sheetContainerRef.value) {
    const rect = sheetContainerRef.value.getBoundingClientRect();
    if (rect.height > 60) return rect.height;
  }
  const vh = window.innerHeight;
  if (snapState.value === 'collapsed') return 54;
  return Math.max(320, Math.min(430, vh - 128));
}

function onTouchStart(e) {
  if (e.touches.length !== 1) return;
  wasDragged = false;
  touchStartX = e.touches[0].clientX;
  touchStartY = e.touches[0].clientY;
  touchStartTime = Date.now();
  initialHeight = getCurrentPixelHeight();
  touchDirection = null;
}

function onTouchMove(e) {
  if (e.touches.length !== 1) return;

  const currentX = e.touches[0].clientX;
  const currentY = e.touches[0].clientY;
  const dx = Math.abs(currentX - touchStartX);
  const dy = Math.abs(currentY - touchStartY);

  if (touchDirection === null) {
    if (dx > 6 || dy > 6) {
      if (dx > dy && snapState.value !== 'collapsed') {
        touchDirection = 'horizontal';
        return; // 不阻断卡片横向平滑滚动
      } else {
        touchDirection = 'vertical';
        wasDragged = true;
        isDragging.value = true;
      }
    } else {
      return;
    }
  }

  if (touchDirection === 'vertical') {
    // 关键：彻底阻止移动端（尤其微信内置浏览器）整页橡皮筋下拉穿透！
    if (e.cancelable) {
      e.preventDefault();
    }
    wasDragged = true;
    const deltaY = touchStartY - currentY; // 向下滑动时 deltaY < 0
    const newHeight = initialHeight + deltaY;
    const minH = 54;
    // 确保拖拽最大高度不低于初始高度，避免小屏视口误截断卡死
    const maxH = Math.max(initialHeight + 40, 520);
    customHeight.value = Math.max(minH, Math.min(maxH, newHeight));
  }
}

function onTouchEnd(e) {
  if (touchDirection !== 'vertical') {
    touchDirection = null;
    isDragging.value = false;
    return;
  }

  isDragging.value = false;
  touchDirection = null;

  const h = customHeight.value;
  customHeight.value = null;

  const touchEndY = e.changedTouches[0]?.clientY ?? touchStartY;
  const deltaY = touchStartY - touchEndY; // < 0 表示向下滑动，> 0 表示向上滑动
  const duration = Math.max(1, Date.now() - touchStartTime);
  const velocityY = (touchEndY - touchStartY) / duration; // px/ms, > 0 表示向下滑动速度

  // 灵敏自然的向下滑动手势判定：
  // 1. 向下滑动距离超过 15px
  // 2. 向下滑动瞬时速度 > 0.12 px/ms
  // 3. 当前高度已被拉低至初始高度的 80% 以下
  const isSwipeDown = deltaY < -15 || velocityY > 0.12 || (h !== null && h < initialHeight * 0.8);
  const isSwipeUp = deltaY > 15 || velocityY < -0.12 || (h !== null && h > initialHeight * 1.15);

  if (isSwipeDown) {
    collapse();
  } else if (isSwipeUp) {
    expandToHalf();
  } else if (h !== null) {
    if (h < (initialHeight + 54) / 2) {
      collapse();
    } else {
      expandToHalf();
    }
  }

  setTimeout(() => {
    wasDragged = false;
  }, 200);
}

// Mouse drag support for Desktop / Testing
let isMouseDown = false;
let mouseStartX = 0;
let mouseStartY = 0;
let mouseStartTime = 0;

function onMouseDown(e) {
  if (e.target.closest('button')) return;
  isMouseDown = true;
  wasDragged = false;
  mouseStartX = e.clientX;
  mouseStartY = e.clientY;
  mouseStartTime = Date.now();
  initialHeight = getCurrentPixelHeight();
}

function onMouseMove(e) {
  if (!isMouseDown) return;
  const currentY = e.clientY;
  const deltaY = mouseStartY - currentY;
  if (Math.abs(deltaY) > 6) {
    wasDragged = true;
    isDragging.value = true;
    const newHeight = initialHeight + deltaY;
    const minH = 54;
    const maxH = Math.max(initialHeight + 40, 520);
    customHeight.value = Math.max(minH, Math.min(maxH, newHeight));
  }
}

function onMouseUp(e) {
  if (!isMouseDown) return;
  isMouseDown = false;
  isDragging.value = false;
  const currentY = e.clientY;
  const deltaY = mouseStartY - currentY;
  const duration = Math.max(1, Date.now() - mouseStartTime);
  const velocityY = (currentY - mouseStartY) / duration;
  const h = customHeight.value;
  customHeight.value = null;

  const isSwipeDown = deltaY < -15 || velocityY > 0.12 || (h !== null && h < initialHeight * 0.8);
  const isSwipeUp = deltaY > 15 || velocityY < -0.12 || (h !== null && h > initialHeight * 1.15);

  if (isSwipeDown) {
    collapse();
  } else if (isSwipeUp) {
    expandToHalf();
  } else if (h !== null) {
    if (h < (initialHeight + 54) / 2) {
      collapse();
    } else {
      expandToHalf();
    }
  }

  setTimeout(() => {
    wasDragged = false;
  }, 200);
}

function handleCardSelect(id) {
  mountainStore.selectMountain(id);
  emit('mountain-select', id);
}

function handleCardDetail(m) {
  emit('mountain-detail', m);
}

function handleCardWeather(m) {
  emit('mountain-weather', m);
}

// Auto-scroll carousel when selected mountain changes
watch(
  () => mountainStore.selectedMountainId,
  (newId) => {
    if (!newId) return;
    expandToHalf();
    nextTick(() => {
      const cardEl = document.getElementById(`mountain-card-${newId}`);
      if (cardEl && carouselRef.value) {
        cardEl.scrollIntoView({
          behavior: 'smooth',
          inline: 'center',
          block: 'nearest'
        });
      }
    });
  }
);

defineExpose({
  collapse,
  expandToHalf,
  expandToFull,
  snapState
});
</script>
