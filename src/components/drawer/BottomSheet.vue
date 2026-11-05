<template>
  <section
    class="bottom-sheet fixed inset-x-0 max-w-md mx-auto pointer-events-auto select-none"
    :class="snapState === 'expanded' ? 'z-[56]' : 'z-40'"
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
      style="overscroll-behavior: none; -webkit-overflow-scrolling: touch;"
      :class="[
        'h-full rounded-t-3xl bg-[#171b26] border-t border-outline-variant/30 shadow-[0_-12px_40px_rgba(0,0,0,0.7)] pt-2 px-margin flex flex-col gap-1.5 overflow-hidden',
        snapState === 'expanded' ? 'pb-[72px]' : 'pb-2'
      ]"
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
          class="flex items-center gap-1 px-3.5 py-1.5 rounded-full bg-primary/20 hover:bg-primary/30 text-primary text-body-sm font-bold border border-primary/40 active:scale-95 transition-all flex-shrink-0 shadow-sm cursor-pointer"
          title="展开山峰卡片"
        >
          <span>展开</span>
          <span class="material-symbols-outlined text-[16px]">expand_less</span>
        </button>
      </div>

      <!-- ================= HALF & EXPANDED STATES ================= -->
      <template v-else>
        <!-- Section Header: Peaks Count & Action Buttons (Visual Anchor) -->
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

            <!-- Action Buttons for Snap State Cycling -->
            <template v-if="snapState === 'half'">
              <!-- Collapse to Minimal Peek Bar -->
              <button
                @click.stop="collapse"
                aria-label="收起卡片以查看大地图"
                class="flex items-center gap-0.5 px-2.5 py-1 rounded-full bg-surface-container-low text-on-surface-variant hover:text-primary active:scale-95 transition-all border border-outline-variant/30 text-caption font-semibold cursor-pointer"
                title="降到最低以查看大地图"
              >
                <span>收起大图</span>
                <span class="material-symbols-outlined text-[16px]">expand_more</span>
              </button>

              <!-- Expand to Fullscreen Compact List -->
              <button
                @click.stop="expandToFull"
                aria-label="展开全屏高密度列表"
                class="flex items-center gap-0.5 px-2.5 py-1 rounded-full bg-primary/15 hover:bg-primary/25 text-primary active:scale-95 transition-all border border-primary/35 text-caption font-semibold cursor-pointer shadow-sm"
                title="展开全屏高密度列表"
              >
                <span>展开全屏</span>
                <span class="material-symbols-outlined text-[16px]">expand_less</span>
              </button>
            </template>

            <template v-else-if="snapState === 'expanded'">
              <!-- Retract back to Half Screen Carousel -->
              <button
                @click.stop="expandToHalf"
                aria-label="收回半屏大图轮播"
                class="flex items-center gap-0.5 px-2.5 py-1 rounded-full bg-surface-container-low text-on-surface-variant hover:text-primary active:scale-95 transition-all border border-outline-variant/30 text-caption font-semibold cursor-pointer"
                title="收回半屏大图轮播"
              >
                <span>收回半屏</span>
                <span class="material-symbols-outlined text-[16px]">expand_more</span>
              </button>
            </template>
          </div>
        </div>

        <!-- Weather Bulletin Banner (In Half State when not search active) -->
        <div
          v-if="snapState === 'half' && !isSearchActive"
          class="w-full px-3 py-1.5 rounded-xl bg-surface-container-low/90 border border-outline-variant/30 flex items-center gap-2.5 flex-shrink-0 transition-opacity duration-200"
        >
          <span class="material-symbols-outlined text-tertiary-fixed-dim text-[18px] flex-shrink-0">warning</span>
          <p class="text-caption font-caption text-on-surface-variant truncate">
            <strong class="text-on-surface font-semibold">Balang Pass:</strong> 实时路况 · 巴朗山及 3800m+ 积雪路段需防滑链
          </p>
        </div>

        <!-- Mode Transition Container (Zero-tear Crossfade) -->
        <Transition name="drawer-content-fade" mode="out-in">
          <!-- EXPANDED STATE: VERTICAL COMPACT LIST -->
          <div
            v-if="snapState === 'expanded'"
            key="expanded-list"
            ref="compactListRef"
            class="compact-list-container flex-1 overflow-y-auto overscroll-contain pr-0.5 flex flex-col gap-2 pt-1 pb-4"
            style="-webkit-overflow-scrolling: touch;"
          >
            <CompactMountainCard
              v-for="mountain in mountainStore.filteredMountains"
              :key="mountain.id"
              :mountain="mountain"
              :is-active="mountain.id === mountainStore.selectedMountainId"
              @select="handleCardSelect"
              @detail="handleCardDetail"
              @weather="handleCardWeather"
            />

            <!-- Empty State -->
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

          <!-- HALF STATE: HORIZONTAL HERO CAROUSEL -->
          <div
            v-else
            key="half-carousel"
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

            <!-- Empty State -->
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
        </Transition>
      </template>
    </div>
  </section>
</template>

<script setup>
import { ref, computed, watch, nextTick, onUnmounted } from 'vue';
import { useMountainStore } from '@/stores/mountainStore.js';
import HeroMountainCard from '@/components/card/HeroMountainCard.vue';
import CompactMountainCard from '@/components/card/CompactMountainCard.vue';

const emit = defineEmits(['mountain-select', 'mountain-detail', 'mountain-weather', 'snap-change']);

const mountainStore = useMountainStore();
const carouselRef = ref(null);
const compactListRef = ref(null);
const sheetContainerRef = ref(null);

// Snap states: 'collapsed' (66px) <-> 'half' (clamp 180px~364px) <-> 'expanded' (calc(100vh - 72px))
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
      bottom: snapState.value === 'expanded' ? '0px' : '66px',
      transition: 'none'
    };
  }

  let h = 'clamp(180px, min(364px, calc(100vh - 180px)), 364px)';
  let b = '66px';

  if (snapState.value === 'collapsed') {
    h = '66px';
    b = '66px';
  } else if (snapState.value === 'expanded') {
    h = 'calc(100vh - 72px)';
    b = '0px';
  }

  return {
    height: h,
    bottom: b,
    transition: 'height 0.28s cubic-bezier(0.16, 1, 0.3, 1), bottom 0.28s cubic-bezier(0.16, 1, 0.3, 1)'
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
  } else if (snapState.value === 'half') {
    expandToFull();
  } else {
    expandToHalf();
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
  snapState.value = 'expanded';
  emit('snap-change', 'expanded');
}

// Touch gesture & scroll chaining gate
let touchStartX = 0;
let touchStartY = 0;
let touchStartTime = 0;
let initialHeight = 0;
let touchDirection = null; // null | 'horizontal' | 'vertical' | 'list_scroll'
let isStartedOnHandle = false;
let isStartedInList = false;

function getCurrentPixelHeight() {
  if (sheetContainerRef.value) {
    const rect = sheetContainerRef.value.getBoundingClientRect();
    if (rect.height > 50) return rect.height;
  }
  const vh = window.innerHeight;
  if (snapState.value === 'collapsed') return 66;
  if (snapState.value === 'expanded') return vh - 72;
  return Math.max(180, Math.min(364, vh - 180));
}

function onTouchStart(e) {
  if (e.touches.length !== 1) return;
  const target = e.target;
  if (target.closest('button')) return;

  isStartedOnHandle = Boolean(target.closest('.drawer-handle'));
  const listEl = compactListRef.value;
  isStartedInList = Boolean(listEl && (listEl === target || listEl.contains(target)));

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
      if (dx > dy && snapState.value === 'half') {
        touchDirection = 'horizontal';
        return; // 放行半屏横滑轮播
      }

      if (snapState.value === 'expanded') {
        if (isStartedOnHandle) {
          touchDirection = 'vertical';
          wasDragged = true;
          isDragging.value = true;
        } else if (isStartedInList) {
          const currentScrollTop = compactListRef.value?.scrollTop ?? 0;
          // 若列表未在最顶，原生纵向滚动放行，禁止触发抽屉拖拽
          if (currentScrollTop > 0) {
            touchDirection = 'list_scroll';
            return;
          }
          // 若已在最顶（scrollTop <= 0）且手势向下拉动（currentY - touchStartY > 10），接力给抽屉下拉
          if (currentY - touchStartY > 10) {
            touchDirection = 'vertical';
            wasDragged = true;
            isDragging.value = true;
          } else {
            touchDirection = 'list_scroll';
            return;
          }
        } else {
          touchDirection = 'vertical';
          wasDragged = true;
          isDragging.value = true;
        }
      } else {
        // 'half' 或 'collapsed' 模式
        touchDirection = 'vertical';
        wasDragged = true;
        isDragging.value = true;
      }
    } else {
      return;
    }
  }

  if (touchDirection === 'vertical') {
    // 阻止移动端整页橡皮筋下拉穿透
    if (e.cancelable) {
      e.preventDefault();
    }
    wasDragged = true;
    const deltaY = touchStartY - currentY; // 向下拉为负，向上拉为正
    const newHeight = initialHeight + deltaY;
    const minH = 66;
    const maxH = Math.max(window.innerHeight - 72, 364);
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
  const deltaY = touchStartY - touchEndY; // > 0 向上推，< 0 向下拉
  const duration = Math.max(1, Date.now() - touchStartTime);
  const velocityY = (touchEndY - touchStartY) / duration; // > 0 向下拉，< 0 向上推

  const vh = window.innerHeight;
  const collapsedPx = 66;
  const halfPx = Math.max(180, Math.min(364, vh - 180));
  const expandedPx = vh - 72;

  // 快速轻扫 (Flick) 判定
  const isFlickUp = deltaY > 20 || velocityY < -0.15;
  const isFlickDown = deltaY < -20 || velocityY > 0.15;

  if (isFlickUp) {
    if (snapState.value === 'collapsed') {
      expandToHalf();
    } else {
      expandToFull();
    }
  } else if (isFlickDown) {
    if (snapState.value === 'expanded') {
      expandToHalf();
    } else {
      collapse();
    }
  } else if (h !== null) {
    // 无强动力轻扫时，依据当前拉动释放高度就近吸附
    const threshCollapseHalf = (collapsedPx + halfPx) / 2;
    const threshHalfExpanded = (halfPx + expandedPx) / 2;

    if (h < threshCollapseHalf) {
      collapse();
    } else if (h < threshHalfExpanded) {
      expandToHalf();
    } else {
      expandToFull();
    }
  }

  setTimeout(() => {
    wasDragged = false;
  }, 200);
}

// Mouse drag support for Desktop / Automated Testing
let isMouseDown = false;
let mouseStartX = 0;
let mouseStartY = 0;
let mouseStartTime = 0;
let isMouseStartedOnHandle = false;
let isMouseStartedInList = false;
let mouseDirection = null;

function onMouseDown(e) {
  const target = e.target;
  if (target.closest('button')) return;

  isMouseDown = true;
  wasDragged = false;
  mouseStartX = e.clientX;
  mouseStartY = e.clientY;
  mouseStartTime = Date.now();
  initialHeight = getCurrentPixelHeight();
  mouseDirection = null;

  isMouseStartedOnHandle = Boolean(target.closest('.drawer-handle'));
  const listEl = compactListRef.value;
  isMouseStartedInList = Boolean(listEl && (listEl === target || listEl.contains(target)));

  window.addEventListener('mousemove', onMouseMove);
  window.addEventListener('mouseup', onMouseUp);
}

function onMouseMove(e) {
  if (!isMouseDown) return;
  const currentY = e.clientY;
  const currentX = e.clientX;
  const dx = Math.abs(currentX - mouseStartX);
  const dy = Math.abs(currentY - mouseStartY);

  if (mouseDirection === null) {
    if (dx > 6 || dy > 6) {
      if (dx > dy && snapState.value === 'half') {
        mouseDirection = 'horizontal';
        return;
      }

      if (snapState.value === 'expanded') {
        if (isMouseStartedOnHandle) {
          mouseDirection = 'vertical';
          wasDragged = true;
          isDragging.value = true;
        } else if (isMouseStartedInList) {
          const currentScrollTop = compactListRef.value?.scrollTop ?? 0;
          if (currentScrollTop > 0) {
            mouseDirection = 'list_scroll';
            return;
          }
          if (currentY - mouseStartY > 10) {
            mouseDirection = 'vertical';
            wasDragged = true;
            isDragging.value = true;
          } else {
            mouseDirection = 'list_scroll';
            return;
          }
        } else {
          mouseDirection = 'vertical';
          wasDragged = true;
          isDragging.value = true;
        }
      } else {
        mouseDirection = 'vertical';
        wasDragged = true;
        isDragging.value = true;
      }
    } else {
      return;
    }
  }

  if (mouseDirection === 'vertical') {
    wasDragged = true;
    const deltaY = mouseStartY - currentY;
    const newHeight = initialHeight + deltaY;
    const minH = 66;
    const maxH = Math.max(window.innerHeight - 72, 364);
    customHeight.value = Math.max(minH, Math.min(maxH, newHeight));
  }
}

function onMouseUp(e) {
  if (!isMouseDown) return;
  isMouseDown = false;
  window.removeEventListener('mousemove', onMouseMove);
  window.removeEventListener('mouseup', onMouseUp);

  if (mouseDirection !== 'vertical') {
    mouseDirection = null;
    isDragging.value = false;
    return;
  }

  isDragging.value = false;
  mouseDirection = null;

  const currentY = e.clientY;
  const deltaY = mouseStartY - currentY;
  const duration = Math.max(1, Date.now() - mouseStartTime);
  const velocityY = (currentY - mouseStartY) / duration;
  const h = customHeight.value;
  customHeight.value = null;

  const vh = window.innerHeight;
  const collapsedPx = 66;
  const halfPx = Math.max(180, Math.min(364, vh - 180));
  const expandedPx = vh - 72;

  const isFlickUp = deltaY > 20 || velocityY < -0.15;
  const isFlickDown = deltaY < -20 || velocityY > 0.15;

  if (isFlickUp) {
    if (snapState.value === 'collapsed') {
      expandToHalf();
    } else {
      expandToFull();
    }
  } else if (isFlickDown) {
    if (snapState.value === 'expanded') {
      expandToHalf();
    } else {
      collapse();
    }
  } else if (h !== null) {
    const threshCollapseHalf = (collapsedPx + halfPx) / 2;
    const threshHalfExpanded = (halfPx + expandedPx) / 2;

    if (h < threshCollapseHalf) {
      collapse();
    } else if (h < threshHalfExpanded) {
      expandToHalf();
    } else {
      expandToFull();
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

// Auto-scroll carousel or compact list when selected mountain changes
watch(
  () => mountainStore.selectedMountainId,
  (newId) => {
    if (!newId) return;
    if (snapState.value === 'collapsed') {
      expandToHalf();
    }
    nextTick(() => {
      if (snapState.value === 'expanded') {
        const cardEl = document.getElementById(`compact-mountain-card-${newId}`);
        if (cardEl && compactListRef.value) {
          cardEl.scrollIntoView({
            behavior: 'smooth',
            block: 'nearest'
          });
        }
      } else {
        const cardEl = document.getElementById(`mountain-card-${newId}`);
        if (cardEl && carouselRef.value) {
          cardEl.scrollIntoView({
            behavior: 'smooth',
            inline: 'center',
            block: 'nearest'
          });
        }
      }
    });
  }
);

onUnmounted(() => {
  window.removeEventListener('mousemove', onMouseMove);
  window.removeEventListener('mouseup', onMouseUp);
});

defineExpose({
  collapse,
  expandToHalf,
  expandToFull,
  cycleSnapState,
  snapState
});
</script>

<style scoped>
.bottom-sheet {
  box-sizing: border-box;
}

/* 零撕裂交叉淡入淡出及微位移动效 */
.drawer-content-fade-enter-active {
  transition: opacity 0.18s cubic-bezier(0.16, 1, 0.3, 1), transform 0.18s cubic-bezier(0.16, 1, 0.3, 1);
}

.drawer-content-fade-leave-active {
  transition: opacity 0.15s ease-in, transform 0.15s ease-in;
}

.drawer-content-fade-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

.drawer-content-fade-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}
</style>
