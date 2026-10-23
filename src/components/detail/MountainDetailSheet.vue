<template>
  <!-- Detail Sheet Backdrop Overlay -->
  <Transition name="fade">
    <div
      v-if="modelValue && mountain"
      class="detail-sheet-backdrop fixed inset-0 z-[60] bg-black/75 backdrop-blur-md transition-opacity"
      @click="closeSheet"
    ></div>
  </Transition>

  <!-- Fullscreen Lightbox Modal (Teleported to body for true fullscreen viewing) -->
  <Teleport to="body">
    <Transition name="fade">
      <div
        v-if="isLightboxOpen && mountain"
        class="lightbox-overlay fixed inset-0 z-[120] bg-black/95 backdrop-blur-2xl flex flex-col justify-between p-4 sm:p-6 select-none"
        role="dialog"
        aria-modal="true"
        aria-label="高清大图全屏画廊预览"
        @click.self="closeLightbox"
        @touchstart.passive="onLightboxTouchStart"
        @touchmove.passive="onLightboxTouchMove"
        @touchend="onLightboxTouchEnd"
      >
        <!-- Top Toolbar -->
        <div class="flex items-center justify-between w-full max-w-4xl mx-auto py-2 px-1 z-20">
          <div class="flex items-center gap-2.5 min-w-0">
            <span class="material-symbols-outlined text-primary text-[24px] flex-shrink-0">photo_library</span>
            <div class="flex flex-col min-w-0">
              <span class="text-body-md font-bold text-white tracking-tight leading-snug truncate">
                {{ mountain.name }} · {{ activeLightboxImage.title }}
              </span>
              <span class="text-caption text-on-surface-variant font-mono truncate text-[11px]">
                {{ activeLightboxImage.desc }}
              </span>
            </div>
          </div>

          <div class="flex items-center gap-2.5 flex-shrink-0">
            <span
              v-if="galleryList.length > 1"
              class="px-2.5 py-1 rounded-full bg-surface-container-high/90 text-label-data-sm font-mono text-primary border border-primary/30"
            >
              {{ lightboxIndex + 1 }} / {{ galleryList.length }}
            </span>
            <span
              v-else
              class="px-2.5 py-1 rounded-full bg-surface-container-high/90 text-label-data-sm font-mono text-primary border border-primary/30"
            >
              高清实景
            </span>
            <button
              type="button"
              @click="closeLightbox"
              class="w-9 h-9 rounded-full flex items-center justify-center bg-surface-container-high hover:bg-surface-bright text-white border border-outline-variant/40 active:scale-95 transition-all"
              aria-label="关闭大图预览"
            >
              <span class="material-symbols-outlined text-[20px]">close</span>
            </button>
          </div>
        </div>

        <!-- Center Image Stage with Left / Right Arrows -->
        <div
          class="relative flex-1 flex items-center justify-center w-full max-w-5xl mx-auto my-2 overflow-hidden"
          @click.self="closeLightbox"
        >
          <!-- Prev Image Button -->
          <button
            v-if="galleryList.length > 1"
            type="button"
            @click.stop="prevLightboxImage"
            class="absolute left-2 sm:left-4 z-20 w-11 h-11 rounded-full frost-glass border border-outline-variant/40 flex items-center justify-center text-white hover:text-primary active:scale-90 transition-all shadow-2xl"
            aria-label="上一张图片"
          >
            <span class="material-symbols-outlined text-[24px]">chevron_left</span>
          </button>

          <!-- Large Centered Image -->
          <img
            :src="getSlideSrc(lightboxIndex)"
            :alt="activeLightboxImage.title || mountain.name"
            class="max-w-full max-h-[72vh] object-contain rounded-2xl shadow-[0_0_48px_rgba(0,0,0,0.95)] border border-outline-variant/30 select-none transition-all duration-300 pointer-events-auto"
            @click.stop
          />

          <!-- Next Image Button -->
          <button
            v-if="galleryList.length > 1"
            type="button"
            @click.stop="nextLightboxImage"
            class="absolute right-2 sm:right-4 z-20 w-11 h-11 rounded-full frost-glass border border-outline-variant/40 flex items-center justify-center text-white hover:text-primary active:scale-90 transition-all shadow-2xl"
            aria-label="下一张图片"
          >
            <span class="material-symbols-outlined text-[24px]">chevron_right</span>
          </button>
        </div>

        <!-- Bottom Controls & Dots -->
        <div class="flex flex-col items-center gap-2 py-2 max-w-md mx-auto w-full z-20">
          <!-- Indicator Dots -->
          <div v-if="galleryList.length > 1" class="flex items-center gap-2">
            <button
              v-for="(img, idx) in galleryList"
              :key="'lb-dot-' + idx"
              type="button"
              @click.stop="lightboxIndex = idx"
              class="h-2 rounded-full transition-all duration-300"
              :class="lightboxIndex === idx ? 'w-6 bg-primary glow-primary' : 'w-2 bg-white/40 hover:bg-white/80'"
              :aria-label="`切换大图至第 ${idx + 1} 张`"
            ></button>
          </div>
          <span class="text-caption text-on-surface-variant/80 text-[11px] font-mono">
            {{ galleryList.length > 1 ? '左右轻扫或按方向键切换 · 点击背景或按 ESC 退出' : '点击背景或按 ESC 退出' }}
          </span>
        </div>
      </div>
    </Transition>
  </Teleport>

  <!-- Navigation App Action Sheet / Modal -->
  <Teleport to="body">
    <Transition name="fade">
      <div
        v-if="isNavModalOpen && mountain"
        class="nav-picker-backdrop fixed inset-0 z-[110] bg-black/80 backdrop-blur-md flex items-end sm:items-center justify-center p-0 sm:p-4 select-none"
        @click.self="closeNavigationPicker"
        role="dialog"
        aria-modal="true"
      >
        <div
          class="nav-picker-panel w-full sm:max-w-md bg-surface-container rounded-t-3xl sm:rounded-3xl border border-outline-variant/30 shadow-[0_-12px_40px_rgba(0,0,0,0.8)] p-5 space-y-4 max-h-[85vh] overflow-y-auto"
        >
          <!-- Header -->
          <div class="flex items-center justify-between pb-2 border-b border-outline-variant/20">
            <div class="flex items-center gap-2">
              <span class="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center text-primary">
                <span class="material-symbols-outlined text-[18px]">navigation</span>
              </span>
              <div>
                <h3 class="text-body-md font-bold text-on-surface">选择手机导航 App</h3>
                <p class="text-[11px] font-mono text-on-surface-variant truncate max-w-[240px]">
                  目的地: {{ currentDestinationName }}
                </p>
              </div>
            </div>
            <button
              type="button"
              @click="closeNavigationPicker"
              class="w-7 h-7 rounded-full bg-surface-container-high hover:bg-surface-bright text-on-surface-variant flex items-center justify-center transition-colors"
            >
              <span class="material-symbols-outlined text-[16px]">close</span>
            </button>
          </div>

          <!-- Destination Info Card -->
          <div class="p-3 rounded-2xl bg-surface-container-low border border-outline-variant/25 text-body-sm space-y-1.5">
            <div class="flex items-center justify-between text-caption font-mono text-on-surface-variant">
              <span>GPS 坐标: {{ destinationCoord.lat.toFixed(4) }}°N, {{ destinationCoord.lng.toFixed(4) }}°E</span>
              <span class="text-primary font-bold">标高 {{ mountain.altitude_m }}m</span>
            </div>
            <p class="text-[12px] text-on-surface leading-snug">
              {{ mountain.nav_point || `${mountain.name} 推荐登山起点` }}
            </p>
          </div>

          <!-- Apps List -->
          <div class="space-y-2">
            <div
              v-for="app in availableNavApps"
              :key="app.id"
              @click="handleSelectNavApp(app)"
              class="nav-app-item group flex items-center justify-between p-3.5 rounded-2xl bg-surface-container-high/60 hover:bg-surface-container-high border border-outline-variant/25 hover:border-primary/40 cursor-pointer active:scale-[0.98] transition-all"
            >
              <div class="flex items-center gap-3">
                <div
                  class="w-10 h-10 rounded-2xl flex items-center justify-center flex-shrink-0"
                  :style="{ backgroundColor: app.color + '20', color: app.color }"
                >
                  <span class="material-symbols-outlined text-[22px]">{{ app.icon }}</span>
                </div>
                <div>
                  <div class="flex items-center gap-1.5">
                    <span class="text-body-md font-bold text-on-surface">{{ app.name }}</span>
                    <span
                      class="px-1.5 py-0.2 rounded text-[10px] font-bold font-mono"
                      :style="{ backgroundColor: app.color + '25', color: app.color }"
                    >
                      {{ app.badge }}
                    </span>
                  </div>
                  <p class="text-[11px] text-on-surface-variant mt-0.5">{{ app.desc }}</p>
                </div>
              </div>
              <span class="material-symbols-outlined text-[18px] text-on-surface-variant group-hover:text-primary transition-colors">
                chevron_right
              </span>
            </div>
          </div>

          <!-- Copy Destination Button -->
          <button
            type="button"
            @click="copyDestinationText"
            class="w-full py-2.5 rounded-xl bg-surface-container-high hover:bg-surface-bright border border-outline-variant/30 text-[12px] font-mono text-on-surface flex items-center justify-center gap-1.5 active:scale-95 transition-all"
          >
            <span class="material-symbols-outlined text-[15px]">content_copy</span>
            <span>复制终点信息（供其他车机或应用粘贴）</span>
          </button>
        </div>
      </div>
    </Transition>
  </Teleport>

  <!-- In-Sheet Toast Notification -->
  <Teleport to="body">
    <Transition name="fade">
      <div
        v-if="localToastMsg"
        class="fixed top-14 left-1/2 -translate-x-1/2 z-[140] px-4 py-2.5 rounded-2xl bg-surface-container-lowest/95 backdrop-blur-xl border border-primary/50 shadow-[0_8px_30px_rgba(78,222,163,0.35)] text-primary text-body-sm font-bold flex items-center gap-2 pointer-events-none"
      >
        <span class="material-symbols-outlined text-[18px]">check_circle</span>
        <span>{{ localToastMsg }}</span>
      </div>
    </Transition>
  </Teleport>

  <!-- Detail Sheet Slide-up Drawer -->
  <Transition name="slide-up">
    <aside
      v-if="modelValue && mountain"
      ref="sheetAsideRef"
      class="mountain-detail-sheet fixed inset-x-0 bottom-0 z-[70] max-w-md mx-auto h-[92vh] max-h-[92vh] flex flex-col rounded-t-3xl bg-surface-container/95 backdrop-blur-2xl border-t border-outline-variant/30 shadow-[0_-16px_48px_rgba(0,0,0,0.85)] select-none text-on-surface overflow-hidden"
      role="dialog"
      aria-modal="true"
      :aria-label="`${mountain.name} 详情`"
      @scroll.passive="preventAsideScroll"
    >
      <!-- Top Drag Handle -->
      <div
        class="w-12 h-1.5 rounded-full bg-outline-variant/60 mx-auto mt-2.5 mb-1 cursor-grab active:cursor-grabbing hover:bg-outline-variant transition-colors flex-shrink-0"
        @click="closeSheet"
        title="点击关闭"
      ></div>

      <!-- Sticky Top Header Bar -->
      <header class="flex items-center justify-between px-4 py-2 border-b border-outline-variant/20 bg-surface-container/90 backdrop-blur-md flex-shrink-0 z-20">
        <div class="flex items-center gap-2 min-w-0">
          <span class="material-symbols-outlined text-primary text-[22px] flex-shrink-0">terrain</span>
          <h2 class="text-headline-md font-bold text-on-surface tracking-tight truncate">
            {{ mountain.name }}
          </h2>
          <span class="px-2 py-0.5 rounded-md bg-primary/10 text-primary text-label-data-sm font-label-data-sm font-semibold border border-primary/20 flex-shrink-0">
            {{ nums.alt }}m
          </span>
          <span
            class="px-2 py-0.5 rounded-md text-label-data-sm font-label-data-sm font-medium border flex-shrink-0"
            :class="diffBadgeClass"
          >
            {{ mountain.difficulty || 'L2' }}
          </span>
        </div>

        <button
          type="button"
          aria-label="关闭详情"
          @click="closeSheet"
          class="btn-close-detail w-8 h-8 rounded-full flex items-center justify-center bg-surface-container-high hover:bg-surface-bright text-on-surface-variant hover:text-on-surface border border-outline-variant/30 transition-colors active:scale-95 flex-shrink-0 ml-2"
        >
          <span class="material-symbols-outlined text-[20px]">close</span>
        </button>
      </header>

      <!-- Scrollable Main Content Container -->
      <div
        ref="scrollContainerRef"
        class="flex-1 overflow-y-auto no-scrollbar scroll-smooth px-4 pb-6 space-y-4"
      >
        <!-- Hero Scenic Image Gallery Carousel Banner -->
        <div
          class="hero-gallery-banner relative w-full h-52 rounded-2xl overflow-hidden bg-surface-container-lowest border border-outline-variant/30 shadow-lg group select-none cursor-pointer mt-3"
          @touchstart.passive="onHeroTouchStart"
          @touchmove.passive="onHeroTouchMove"
          @touchend="onHeroTouchEnd"
          @click="openLightbox(currentImageIndex)"
          title="轻触查看高清全屏相册"
        >
          <!-- Current Active Gallery Image -->
          <img
            :src="getSlideSrc(currentImageIndex)"
            @error="handleImageError(currentImageIndex)"
            :alt="galleryList[currentImageIndex]?.title || mountain.name"
            class="w-full h-full object-cover transition-opacity duration-300"
            loading="lazy"
          />
          <div class="absolute inset-0 bg-gradient-to-t from-surface-container via-surface-container/35 to-transparent pointer-events-none"></div>

          <!-- Top Chips on Hero Image -->
          <div class="absolute top-3 left-3 right-3 flex items-center justify-between z-10 pointer-events-none">
            <span class="px-2.5 py-1 rounded-full bg-surface-container-lowest/80 backdrop-blur-md text-[11px] font-mono font-semibold text-secondary border border-secondary/30 flex items-center gap-1">
              <span class="material-symbols-outlined text-[14px]">explore</span>
              梯队 {{ mountain.group || 'A' }} 组 · {{ mountain.county_short || locationShort }}
            </span>

            <div class="flex items-center gap-1.5 pointer-events-auto">
              <!-- Gallery Photo Counter Chip -->
              <button
                type="button"
                @click.stop="openLightbox(currentImageIndex)"
                class="px-2 py-0.5 rounded-full bg-surface-container-lowest/80 backdrop-blur-md text-[11px] font-mono font-bold text-primary border border-primary/30 flex items-center gap-1 hover:bg-surface-container-high active:scale-95 transition-all shadow"
                title="轻触全屏放大画廊"
              >
                <span class="material-symbols-outlined text-[13px]">photo_library</span>
                {{ galleryList.length > 1 ? `${currentImageIndex + 1}/${galleryList.length}` : '实景全貌' }}
              </button>

              <!-- Weather Chip -->
              <span class="px-2 py-0.5 rounded-full bg-surface-container-lowest/80 backdrop-blur-md text-[11px] font-mono text-tertiary-fixed-dim border border-tertiary/30 flex items-center gap-1">
                <span class="material-symbols-outlined text-[13px] text-tertiary-fixed-dim">wb_sunny</span>
                {{ weatherCondition }}
              </span>
            </div>
          </div>

          <!-- Prev / Next Arrow Navigation Controls (Subtle Hover/Touch Arrows) -->
          <button
            v-if="galleryList.length > 1"
            type="button"
            @click.stop="prevImage"
            aria-label="查看上一张图片"
            class="gallery-arrow-btn absolute left-2 top-1/2 -translate-y-1/2 z-20 w-7 h-7 rounded-full frost-glass border border-outline-variant/30 flex items-center justify-center text-on-surface hover:text-primary active:scale-95 transition-all opacity-70 group-hover:opacity-100 shadow-md"
          >
            <span class="material-symbols-outlined text-[18px]">chevron_left</span>
          </button>
          <button
            v-if="galleryList.length > 1"
            type="button"
            @click.stop="nextImage"
            aria-label="查看下一张图片"
            class="gallery-arrow-btn absolute right-2 top-1/2 -translate-y-1/2 z-20 w-7 h-7 rounded-full frost-glass border border-outline-variant/30 flex items-center justify-center text-on-surface hover:text-primary active:scale-95 transition-all opacity-70 group-hover:opacity-100 shadow-md"
          >
            <span class="material-symbols-outlined text-[18px]">chevron_right</span>
          </button>

          <!-- Micro Indicator Dots -->
          <div
            v-if="galleryList.length > 1"
            class="gallery-dots absolute bottom-14 left-0 right-0 z-20 flex items-center justify-center gap-1.5 pointer-events-auto"
          >
            <button
              v-for="(img, idx) in galleryList"
              :key="'dot-' + idx"
              type="button"
              @click.stop="goToImage(idx)"
              class="h-1.5 rounded-full transition-all duration-300"
              :class="currentImageIndex === idx ? 'w-5 bg-primary glow-primary' : 'w-1.5 bg-white/40 hover:bg-white/70'"
              :aria-label="`切换至第 ${idx + 1} 张图片: ${img.title}`"
            ></button>
          </div>

          <!-- Bottom Title overlay on Hero Image -->
          <div class="absolute bottom-2.5 left-3 right-3 z-10 flex items-end justify-between pointer-events-none">
            <div>
              <p class="text-caption font-caption text-on-surface-variant flex items-center gap-1">
                <span>{{ galleryList[currentImageIndex]?.title || '四川川西山峰拓扑档案' }}</span>
                <span class="text-[10px] text-primary font-mono opacity-80">(轻触放大)</span>
              </p>
              <h3 class="text-headline-lg font-extrabold text-on-surface tracking-tight">
                {{ mountain.name }}
              </h3>
            </div>
            <div class="text-right">
              <span class="text-label-data-lg font-bold text-primary font-mono">{{ nums.alt }}</span>
              <span class="text-caption text-on-surface-variant ml-0.5">米海拔</span>
            </div>
          </div>
        </div>

        <!-- Quick Anchor Navigation Pills (Horizontal Scroller with Solid Obsidian Backing) -->
        <nav class="sticky top-0 z-20 -mx-4 px-4 py-2 bg-[#161d2d] border-b border-outline-variant/30 shadow-md flex gap-1.5 overflow-x-auto no-scrollbar">
          <button
            v-for="tab in anchorTabs"
            :key="tab.id"
            type="button"
            @click="scrollToAnchor(tab.id)"
            class="flex-shrink-0 px-2.5 py-1 rounded-lg text-body-sm font-medium transition-all"
            :class="activeAnchor === tab.id
              ? 'bg-primary/20 text-primary border border-primary/40'
              : 'bg-surface-container-high/60 text-on-surface-variant hover:text-on-surface border border-outline-variant/20'"
          >
            {{ tab.label }}
          </button>
        </nav>

        <!-- ================= MODULE 1: 概况 (Overview) ================= -->
        <section
          id="mod-overview"
          class="detail-module-card detail-module-overview p-4 rounded-2xl bg-surface-container-high/80 border border-outline-variant/30 space-y-3"
          data-module="overview"
        >
          <div class="flex items-center justify-between">
            <h4 class="text-body-lg font-bold text-on-surface flex items-center gap-2">
              <span class="material-symbols-outlined text-primary text-[20px]">info</span>
              <span>1. 山峰全景观况</span>
            </h4>
            <span class="px-2 py-0.5 rounded text-[11px] font-mono font-semibold" :class="mountain.free ? 'bg-primary/10 text-primary' : 'bg-tertiary/10 text-tertiary-fixed-dim'">
              {{ mountain.free ? '免费开放' : '收费景区' }}
            </span>
          </div>

          <!-- 4-Metrics Bento Grid -->
          <div class="grid grid-cols-4 gap-1.5 p-2.5 rounded-xl bg-surface-container-low/70 border border-outline-variant/20 text-center">
            <div class="flex flex-col">
              <span class="text-[10px] font-caption text-on-surface-variant uppercase">峰顶海拔</span>
              <span class="text-label-data-sm font-label-data-sm text-primary font-bold mt-0.5">{{ nums.alt }}m</span>
            </div>
            <div class="flex flex-col border-l border-outline-variant/20">
              <span class="text-[10px] font-caption text-on-surface-variant uppercase">累计爬升</span>
              <span class="text-label-data-sm font-label-data-sm text-primary font-bold mt-0.5">+{{ nums.asc }}m</span>
            </div>
            <div class="flex flex-col border-l border-outline-variant/20">
              <span class="text-[10px] font-caption text-on-surface-variant uppercase">往返里程</span>
              <span class="text-label-data-sm font-label-data-sm text-on-surface font-bold mt-0.5">{{ nums.dist }}km</span>
            </div>
            <div class="flex flex-col border-l border-outline-variant/20">
              <span class="text-[10px] font-caption text-on-surface-variant uppercase">预计用时</span>
              <span class="text-label-data-sm font-label-data-sm text-secondary font-bold mt-0.5">{{ durationText }}</span>
            </div>
          </div>

          <!-- Specs List -->
          <div class="space-y-1.5 text-body-sm text-on-surface-variant">
            <div class="flex items-start gap-2">
              <span class="w-18 flex-shrink-0 text-on-surface/80 font-medium">地理区划:</span>
              <span class="text-on-surface flex-1">{{ mountain.county || '四川省' }}</span>
            </div>
            <div class="flex items-start gap-2">
              <span class="w-18 flex-shrink-0 text-on-surface/80 font-medium">{{ regionStore.currentRegion.driveCenter }}车程:</span>
              <span class="text-on-surface flex-1">约 {{ mountain.drive_hours || '--' }} 小时直达</span>
            </div>
            <div class="flex items-start gap-2">
              <span class="w-18 flex-shrink-0 text-on-surface/80 font-medium">难度等级:</span>
              <span class="text-on-surface flex-1">{{ mountain.difficulty }} {{ diffLabel }} {{ mountain.difficulty_note ? `（${mountain.difficulty_note}）` : '' }}</span>
            </div>
            <div class="flex items-start gap-2">
              <span class="w-18 flex-shrink-0 text-on-surface/80 font-medium">过夜方案:</span>
              <span class="text-on-surface flex-1">{{ mountain.overnight ? '支持高山扎营/特色住宿' : '建议单日轻装往返，避免滞留' }}</span>
            </div>
            <div v-if="seasonBestText" class="flex items-start gap-2">
              <span class="w-18 flex-shrink-0 text-on-surface/80 font-medium">黄金季节:</span>
              <span class="text-on-surface flex-1">{{ seasonBestText }}</span>
            </div>
          </div>

          <!-- Reputation Box -->
          <div v-if="mountain.reputation" class="p-2.5 rounded-xl bg-surface-container-low/60 border border-outline-variant/20 text-body-sm text-on-surface-variant leading-relaxed">
            <div class="flex items-center gap-1.5 text-primary text-caption font-bold mb-1">
              <span class="material-symbols-outlined text-[16px]">reviews</span>
              <span>驴友综合口碑与红黑榜点评</span>
            </div>
            <p>{{ mountain.reputation }}</p>
          </div>
        </section>

        <!-- ================= MODULE 2: 路线 (Routes) ================= -->
        <section
          id="mod-routes"
          class="detail-module-card detail-module-routes p-4 rounded-2xl bg-surface-container-high/80 border border-outline-variant/30 space-y-3"
          data-module="routes"
        >
          <div class="flex items-center justify-between">
            <h4 class="text-body-lg font-bold text-on-surface flex items-center gap-2">
              <span class="material-symbols-outlined text-secondary text-[20px]">timeline</span>
              <span>2. 徒步与越野路线</span>
            </h4>
            <span class="text-caption text-secondary font-mono font-semibold">
              {{ (mountain.routes && mountain.routes.length) || 1 }} 条可选方案
            </span>
          </div>

          <div v-if="mountain.routes && mountain.routes.length" class="space-y-2.5">
            <div
              v-for="(r, idx) in mountain.routes"
              :key="`route-${idx}`"
              class="p-3 rounded-xl bg-surface-container-low/70 border border-outline-variant/20 space-y-1.5"
            >
              <div class="flex items-center justify-between">
                <span class="text-body-md font-bold text-on-surface flex items-center gap-1.5">
                  <span class="w-2 h-2 rounded-full bg-secondary"></span>
                  {{ r.name }}
                </span>
                <span v-if="r.difficulty" class="px-2 py-0.5 rounded text-[10px] font-mono bg-surface-container text-secondary border border-secondary/30">
                  {{ r.difficulty }}
                </span>
              </div>
              <div class="flex items-center gap-3 text-caption text-on-surface-variant font-mono">
                <span v-if="r.km">里程: {{ r.km }}km</span>
                <span v-if="r.hours">用时: {{ r.hours }}</span>
              </div>
              <p v-if="r.desc" class="text-body-sm text-on-surface-variant leading-relaxed">
                {{ r.desc }}
              </p>
              <div v-if="r.descent" class="pt-1.5 border-t border-outline-variant/15 text-caption text-on-surface-variant flex items-start gap-1">
                <span class="material-symbols-outlined text-[14px] text-tertiary-fixed-dim flex-shrink-0 mt-0.5">turn_sharp_left</span>
                <span><strong>下撤路径:</strong> {{ r.descent }}</span>
              </div>
            </div>
          </div>

          <!-- Route Detail Segments if present -->
          <div v-if="mountain.route_detail && mountain.route_detail.length" class="space-y-2">
            <h5 class="text-caption font-bold text-on-surface-variant uppercase tracking-wider flex items-center gap-1.5">
              <span class="material-symbols-outlined text-secondary text-[16px]">alt_route</span>
              <span>分段地形与补给明细</span>
            </h5>
            <div
              v-for="(rd, rdi) in mountain.route_detail"
              :key="`rd-${rdi}`"
              class="p-3.5 rounded-2xl bg-surface-container-low/80 border border-outline-variant/25 text-body-sm space-y-3"
            >
              <!-- Route Scheme Name (Full width header) -->
              <div class="space-y-2">
                <div class="flex items-center gap-2">
                  <span class="w-2.5 h-2.5 rounded-full bg-secondary flex-shrink-0"></span>
                  <h6 class="font-bold text-on-surface text-body-md leading-snug">
                    {{ rd.name || `路线方案 ${rdi + 1}` }}
                  </h6>
                </div>

                <!-- Terrain Chip (Full width pill if present) -->
                <div
                  v-if="rd.terrain"
                  class="flex items-start gap-1.5 px-2.5 py-1.5 rounded-xl bg-surface-container/80 text-[12px] text-secondary font-mono border border-secondary/25"
                >
                  <span class="font-bold flex-shrink-0">⛰️ 地形:</span>
                  <span class="leading-relaxed">{{ rd.terrain }}</span>
                </div>
              </div>

              <!-- Difficulty Note -->
              <div
                v-if="rd.difficulty_note"
                class="p-2.5 rounded-xl bg-surface-container/50 border border-outline-variant/20 text-caption text-on-surface-variant leading-relaxed flex items-start gap-1.5"
              >
                <span class="material-symbols-outlined text-[15px] text-tertiary-fixed-dim flex-shrink-0 mt-0.5">info</span>
                <span>{{ rd.difficulty_note }}</span>
              </div>

              <!-- Segments Timeline / List -->
              <div v-if="rd.segments && rd.segments.length" class="space-y-2.5 pt-1 border-t border-outline-variant/15">
                <div
                  v-for="(seg, si) in rd.segments"
                  :key="`seg-${si}`"
                  class="p-3 rounded-xl bg-surface-container/70 border border-outline-variant/25 space-y-2"
                >
                  <!-- Step Number + Route Nodes -->
                  <div class="flex items-start gap-2.5">
                    <span class="w-5 h-5 rounded-full bg-primary/20 text-primary flex items-center justify-center text-[11px] font-mono font-bold flex-shrink-0 mt-0.5">
                      {{ si + 1 }}
                    </span>
                    <div class="flex-1 min-w-0">
                      <!-- From -> To Points (Full width flow) -->
                      <div class="flex items-center flex-wrap gap-1.5 text-[13px] font-bold text-on-surface leading-snug">
                        <span>{{ seg.from || seg.name || `第 ${si + 1} 段` }}</span>
                        <span v-if="seg.to" class="text-primary font-mono font-bold">→</span>
                        <span v-if="seg.to" class="text-primary font-medium">{{ seg.to }}</span>
                      </div>

                      <!-- Metric Badges Row (Below route points, never squished!) -->
                      <div class="flex items-center flex-wrap gap-1.5 mt-2 text-[11px] font-mono">
                        <span v-if="seg.km" class="px-2 py-0.5 rounded-md bg-surface-container-lowest text-primary border border-primary/25 font-semibold">
                          📏 {{ seg.km }}km
                        </span>
                        <span v-if="seg.time_h" class="px-2 py-0.5 rounded-md bg-surface-container-lowest text-secondary border border-secondary/25 font-semibold">
                          ⏱️ 约{{ seg.time_h }}h
                        </span>
                        <span v-if="seg.alt_m" class="px-2 py-0.5 rounded-md bg-surface-container-lowest text-on-surface-variant border border-outline-variant/25">
                          ⛰️ 标高 {{ seg.alt_m }}m
                        </span>
                      </div>
                    </div>
                  </div>

                  <!-- Segment Note / Terrain Tips -->
                  <div v-if="seg.note" class="pl-7 pt-1.5 border-t border-outline-variant/10 text-[11px] text-on-surface-variant leading-relaxed">
                    {{ seg.note }}
                  </div>
                </div>
              </div>

              <!-- Water & Supply Tips -->
              <div v-if="rd.water || rd.supply" class="pt-2 border-t border-outline-variant/15 space-y-1.5 text-caption font-mono text-[11px]">
                <div v-if="rd.water" class="flex items-start gap-1.5 p-2 rounded-xl bg-surface-container-lowest/60 border border-secondary/20 text-on-surface-variant">
                  <span class="text-secondary font-bold flex-shrink-0">💧 水源情报:</span>
                  <span class="leading-relaxed">{{ rd.water }}</span>
                </div>
                <div v-if="rd.supply" class="flex items-start gap-1.5 p-2 rounded-xl bg-surface-container-lowest/60 border border-primary/20 text-on-surface-variant">
                  <span class="text-primary font-bold flex-shrink-0">🍱 沿途补给:</span>
                  <span class="leading-relaxed">{{ rd.supply }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Track Keywords (GPX search & App Deep Link) -->
          <div v-if="mountain.track_keywords && mountain.track_keywords.length" class="pt-3 border-t border-outline-variant/20 space-y-2.5">
            <div class="flex items-center justify-between">
              <div class="text-caption font-semibold text-on-surface flex items-center gap-1.5">
                <span class="material-symbols-outlined text-[17px] text-primary">download</span>
                <span class="font-bold">两步路 / 六只脚 GPX 户外轨迹</span>
              </div>
              <span class="text-[11px] font-mono text-primary/80">点击自动调起 App</span>
            </div>

            <!-- Quick Action: Launch 2bulu / Foottouch -->
            <div class="grid grid-cols-2 gap-2">
              <button
                type="button"
                @click="handleLaunchTwoBulu(mountain.name)"
                class="btn-launch-twobulu flex items-center justify-center gap-1.5 py-2 px-2.5 rounded-xl bg-emerald-500/15 hover:bg-emerald-500/25 border border-emerald-500/35 text-emerald-300 text-[12px] font-bold active:scale-95 transition-all shadow-sm"
              >
                <span class="material-symbols-outlined text-[17px]">hiking</span>
                <span>打开两步路 App</span>
              </button>
              <button
                type="button"
                @click="handleLaunchFootTouch(mountain.name)"
                class="btn-launch-foottouch flex items-center justify-center gap-1.5 py-2 px-2.5 rounded-xl bg-blue-500/15 hover:bg-blue-500/25 border border-blue-500/35 text-blue-300 text-[12px] font-bold active:scale-95 transition-all shadow-sm"
              >
                <span class="material-symbols-outlined text-[17px]">map</span>
                <span>打开六只脚 App</span>
              </button>
            </div>

            <!-- Track Keywords List with App Trigger -->
            <div class="space-y-1.5">
              <div
                v-for="(kw, kwi) in mountain.track_keywords"
                :key="`kw-${kwi}`"
                @click="handleLaunchTwoBulu(kw)"
                class="track-keyword-card group flex items-center justify-between p-2.5 rounded-xl bg-surface-container-low/90 hover:bg-surface-container border border-primary/20 hover:border-primary/45 cursor-pointer active:scale-[0.99] transition-all"
              >
                <div class="flex items-center gap-2 min-w-0 pr-2">
                  <span class="material-symbols-outlined text-primary text-[16px] flex-shrink-0 group-hover:scale-110 transition-transform">route</span>
                  <span class="text-[12px] font-mono text-on-surface truncate">{{ kw }}</span>
                </div>
                <div class="flex items-center gap-1.5 flex-shrink-0">
                  <span class="px-2 py-0.5 rounded-md bg-primary/15 group-hover:bg-primary/25 text-primary text-[10px] font-bold font-mono border border-primary/30 flex items-center gap-0.5">
                    <span>搜两步路</span>
                    <span class="material-symbols-outlined text-[11px]">open_in_new</span>
                  </span>
                  <button
                    type="button"
                    @click.stop="copyKeywordOnly(kw)"
                    class="p-1 rounded-md bg-surface-container hover:bg-surface-bright text-on-surface-variant hover:text-on-surface border border-outline-variant/30 transition-colors"
                    title="仅复制关键词"
                  >
                    <span class="material-symbols-outlined text-[13px]">content_copy</span>
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- Plan B Withdrawal Route -->
          <div v-if="mountain.plan_b" class="p-2.5 rounded-xl bg-amber-500/10 border border-amber-500/25 text-body-sm text-amber-200 leading-relaxed">
            <div class="flex items-center gap-1 font-bold text-amber-300 text-caption mb-0.5">
              <span class="material-symbols-outlined text-[16px]">alt_route</span>
              <span>恶劣天气备选撤退方案 (Plan B)</span>
            </div>
            <p class="text-[12px] text-amber-100/90">{{ mountain.plan_b }}</p>
          </div>
        </section>

        <!-- ================= MODULE 3: 高程打卡点 (Waypoints & Elevation) ================= -->
        <section
          id="mod-waypoints"
          class="detail-module-card detail-module-waypoints p-4 rounded-2xl bg-surface-container-high/80 border border-outline-variant/30 space-y-3"
          data-module="waypoints"
        >
          <div class="flex items-center justify-between">
            <h4 class="text-body-lg font-bold text-on-surface flex items-center gap-2">
              <span class="material-symbols-outlined text-primary text-[20px]">altitude</span>
              <span>3. 高程剖面与打卡点</span>
            </h4>
            <span class="text-caption text-primary font-mono font-semibold">
              GPS TOPOGRAPHY
            </span>
          </div>

          <!-- Embedded Route Elevation & Waypoints Component -->
          <RouteElevationChart
            :mountain="mountain"
            @probe-waypoint="(wp) => emit('probe-waypoint', wp)"
            @clear-probe="() => emit('clear-probe')"
          />
        </section>

        <!-- ================= MODULE 4: 亮点与机位 (Highlights & Spots) ================= -->
        <section
          id="mod-highlights"
          class="detail-module-card detail-module-highlights p-4 rounded-2xl bg-surface-container-high/80 border border-outline-variant/30 space-y-3"
          data-module="highlights"
        >
          <div class="flex items-center justify-between">
            <h4 class="text-body-lg font-bold text-on-surface flex items-center gap-2">
              <span class="material-symbols-outlined text-tertiary-fixed-dim text-[20px]">auto_awesome</span>
              <span>4. 核心亮点与机位</span>
            </h4>
            <span class="text-caption text-tertiary-fixed-dim font-mono font-semibold">HIGHLIGHTS</span>
          </div>

          <!-- Feature Tags -->
          <div v-if="mountain.tags && mountain.tags.length" class="flex flex-wrap gap-1.5">
            <span
              v-for="(tag, ti) in mountain.tags"
              :key="`tag-${ti}`"
              class="px-2.5 py-1 rounded-full bg-surface-container-low text-body-sm font-medium text-tertiary-fixed-dim border border-tertiary/30 flex items-center gap-1"
            >
              <span class="w-1.5 h-1.5 rounded-full bg-tertiary-fixed-dim"></span>
              {{ tag }}
            </span>
          </div>

          <!-- Photo Spots List -->
          <div v-if="mountain.photo_spots && mountain.photo_spots.length" class="space-y-2">
            <h5 class="text-caption font-bold text-on-surface-variant uppercase tracking-wider flex items-center gap-1">
              <span class="material-symbols-outlined text-[15px] text-primary">photo_camera</span>
              <span>经典摄影机位清单</span>
            </h5>
            <div class="space-y-1.5">
              <div
                v-for="(spot, si) in mountain.photo_spots"
                :key="`spot-${si}`"
                class="p-2.5 rounded-xl bg-surface-container-low/70 border border-outline-variant/20 flex items-start gap-2 text-body-sm"
              >
                <span class="text-primary font-mono font-bold text-[12px] mt-0.5">0{{ si + 1 }}</span>
                <span class="text-on-surface leading-snug">{{ spot }}</span>
              </div>
            </div>
          </div>

          <!-- Sunrise Sunset Reference -->
          <div v-if="mountain.sunrise_sunset_ref || mountain.sun_times" class="p-2.5 rounded-xl bg-surface-container-low/60 border border-outline-variant/20 text-body-sm space-y-1">
            <div class="flex items-center gap-1 text-tertiary-fixed-dim font-bold text-caption">
              <span class="material-symbols-outlined text-[16px]">wb_twilight</span>
              <span>日出日落与晨昏黄金时刻参考</span>
            </div>
            <p class="text-on-surface-variant text-[12px] leading-relaxed">
              {{ mountain.sunrise_sunset_ref || JSON.stringify(mountain.sun_times) }}
            </p>
          </div>
        </section>

        <!-- ================= MODULE 5: 路况驾驶 (Road & Navigation) ================= -->
        <section
          id="mod-road"
          class="detail-module-card detail-module-road p-4 rounded-2xl bg-surface-container-high/80 border border-outline-variant/30 space-y-3"
          data-module="road"
        >
          <div class="flex items-center justify-between">
            <h4 class="text-body-lg font-bold text-on-surface flex items-center gap-2">
              <span class="material-symbols-outlined text-secondary text-[20px]">directions_car</span>
              <span>5. 路况交通与驾驶指南</span>
            </h4>
            <span class="text-caption text-secondary font-mono font-semibold">NAVIGATION</span>
          </div>

          <!-- Nav Target Point & Map App Launcher -->
          <div v-if="mountain.nav_point" class="p-3.5 rounded-2xl bg-surface-container-low/90 border border-secondary/35 space-y-2.5">
            <div class="flex items-center justify-between">
              <span class="text-caption font-bold text-secondary flex items-center gap-1.5">
                <span class="material-symbols-outlined text-[17px]">navigation</span>
                <span>自驾与徒步导航终点</span>
              </span>
              <span class="px-2 py-0.5 rounded-full bg-secondary/15 text-secondary text-[10px] font-mono font-bold">
                一键调起地图
              </span>
            </div>
            <p class="text-body-sm text-on-surface leading-snug font-medium">
              {{ mountain.nav_point }}
            </p>
            <div class="flex items-center gap-2 pt-1">
              <button
                type="button"
                @click="openNavigationPicker"
                class="btn-open-nav-app flex-1 py-2 px-3 rounded-xl bg-primary hover:bg-primary-hover text-on-primary text-[12px] font-bold shadow-[0_4px_16px_rgba(78,222,163,0.3)] flex items-center justify-center gap-1.5 active:scale-95 transition-all"
              >
                <span class="material-symbols-outlined text-[17px]">explore</span>
                <span>打开手机地图 App 导航</span>
              </button>
              <button
                type="button"
                @click="copyDestinationText"
                class="py-2 px-3 rounded-xl bg-surface-container-high hover:bg-surface-bright text-on-surface text-[12px] font-mono border border-outline-variant/30 flex items-center justify-center gap-1 active:scale-95 transition-transform"
                title="复制终点文本"
              >
                <span class="material-symbols-outlined text-[14px]">content_copy</span>
                <span>复制</span>
              </button>
            </div>
          </div>

          <!-- Road Difficulty & Conditions -->
          <div v-if="mountain.road_difficulty" class="space-y-1">
            <h5 class="text-caption font-bold text-on-surface-variant uppercase tracking-wider">道路路况与通行条件</h5>
            <p class="text-body-sm text-on-surface-variant leading-relaxed bg-surface-container-low/60 p-2.5 rounded-xl border border-outline-variant/20">
              {{ mountain.road_difficulty }}
            </p>
          </div>

          <!-- Parking Info -->
          <div v-if="mountain.parking_fee || mountain.parking" class="flex items-start gap-2 text-body-sm text-on-surface-variant">
            <span class="material-symbols-outlined text-primary text-[18px] flex-shrink-0 mt-0.5">local_parking</span>
            <div>
              <strong class="text-on-surface">停车与收费:</strong>
              <p class="mt-0.5">{{ mountain.parking_fee || mountain.parking }}</p>
            </div>
          </div>

          <!-- Fuel & Charging -->
          <div v-if="mountain.fuel_charging" class="flex items-start gap-2 text-body-sm text-on-surface-variant">
            <span class="material-symbols-outlined text-secondary text-[18px] flex-shrink-0 mt-0.5">ev_station</span>
            <div>
              <strong class="text-on-surface">补能与充电桩:</strong>
              <p class="mt-0.5">{{ mountain.fuel_charging }}</p>
            </div>
          </div>

          <!-- Transit Info -->
          <div v-if="mountain.transit" class="flex items-start gap-2 text-body-sm text-on-surface-variant">
            <span class="material-symbols-outlined text-tertiary-fixed-dim text-[18px] flex-shrink-0 mt-0.5">directions_bus</span>
            <div>
              <strong class="text-on-surface">公共交通/景区直通车:</strong>
              <p class="mt-0.5">{{ mountain.transit }}</p>
            </div>
          </div>
        </section>

        <!-- ================= MODULE 6: 安全高反 (Safety & Altitude) ================= -->
        <section
          id="mod-safety"
          class="detail-module-card detail-module-safety p-4 rounded-2xl bg-surface-container-high/80 border border-outline-variant/30 space-y-3"
          data-module="safety"
        >
          <div class="flex items-center justify-between">
            <h4 class="text-body-lg font-bold text-on-surface flex items-center gap-2">
              <span class="material-symbols-outlined text-amber-400 text-[20px]">warning</span>
              <span>6. 安全警示与应急救援</span>
            </h4>
            <span class="text-caption text-amber-400 font-mono font-semibold">SAFETY FIRST</span>
          </div>

          <!-- Hazards List -->
          <div v-if="mountain.hazards && mountain.hazards.length" class="space-y-1.5">
            <div
              v-for="(hazard, hi) in mountain.hazards"
              :key="`hazard-${hi}`"
              class="p-2.5 rounded-xl bg-amber-500/10 border border-amber-500/25 flex items-start gap-2 text-body-sm text-amber-100"
            >
              <span class="material-symbols-outlined text-amber-400 text-[16px] flex-shrink-0 mt-0.5">error_outline</span>
              <span class="leading-relaxed">{{ hazard }}</span>
            </div>
          </div>

          <!-- Seasonal Risk -->
          <div v-if="mountain.season_risk" class="p-2.5 rounded-xl bg-surface-container-low/70 border border-outline-variant/20 text-body-sm text-on-surface-variant">
            <strong class="text-on-surface">季节性高危提示:</strong>
            <p class="mt-0.5 leading-relaxed">{{ mountain.season_risk }}</p>
          </div>

          <!-- Signal Coverage -->
          <div v-if="mountain.signal || mountain.signal_detail" class="flex items-start gap-2 text-body-sm text-on-surface-variant">
            <span class="material-symbols-outlined text-secondary text-[18px] flex-shrink-0 mt-0.5">cell_tower</span>
            <div>
              <strong class="text-on-surface">通信信号覆盖:</strong>
              <p class="mt-0.5 leading-relaxed">{{ mountain.signal || mountain.signal_detail }}</p>
            </div>
          </div>

          <!-- Rescue & Emergency -->
          <div v-if="mountain.rescue" class="p-2.5 rounded-xl bg-red-500/10 border border-red-500/25 text-body-sm text-red-200">
            <div class="flex items-center gap-1 font-bold text-red-300 text-caption mb-1">
              <span class="material-symbols-outlined text-[16px]">emergency</span>
              <span>紧急救援与属地医疗保障</span>
            </div>
            <p class="text-[12px] leading-relaxed text-red-100/90">{{ mountain.rescue }}</p>
          </div>

          <!-- Toilets / Sanitation -->
          <div v-if="mountain.toilets" class="flex items-start gap-2 text-body-sm text-on-surface-variant">
            <span class="material-symbols-outlined text-primary text-[18px] flex-shrink-0 mt-0.5">wc</span>
            <div>
              <strong class="text-on-surface">沿途公厕设施:</strong>
              <p class="mt-0.5">{{ mountain.toilets }}</p>
            </div>
          </div>
        </section>

        <!-- ================= MODULE 7: 装备清单 (Gear Checklist) ================= -->
        <section
          id="mod-gear"
          class="detail-module-card detail-module-gear p-4 rounded-2xl bg-surface-container-high/80 border border-outline-variant/30 space-y-3"
          data-module="gear"
        >
          <div class="flex items-center justify-between">
            <h4 class="text-body-lg font-bold text-on-surface flex items-center gap-2">
              <span class="material-symbols-outlined text-primary text-[20px]">backpack</span>
              <span>7. 装备清单与自查</span>
            </h4>
            <span class="text-caption text-primary font-mono font-semibold">
              {{ checkedGearCount }} / {{ totalGearCount }} 已备齐
            </span>
          </div>

          <!-- Day Hiking Gear Checklist -->
          <div v-if="mountain.gear_day && mountain.gear_day.length" class="space-y-1.5">
            <h5 class="text-caption font-bold text-on-surface-variant uppercase tracking-wider flex items-center gap-1">
              <span class="material-symbols-outlined text-[15px] text-primary">hiking</span>
              <span>单日冲顶必带装备</span>
            </h5>
            <div class="grid grid-cols-1 gap-1.5">
              <label
                v-for="(g, gi) in mountain.gear_day"
                :key="`g-day-${gi}`"
                class="flex items-center gap-2.5 p-2 rounded-xl bg-surface-container-low/70 border border-outline-variant/20 cursor-pointer hover:bg-surface-container-low transition-colors group select-none"
              >
                <!-- Custom Stitch Alpine Checkbox -->
                <div
                  class="w-4 h-4 rounded border flex items-center justify-center transition-all duration-200 flex-shrink-0"
                  :class="gearCheckedMap[`day-${gi}`]
                    ? 'bg-primary border-primary text-[#0a0e17] shadow-[0_0_8px_rgba(78,222,163,0.35)]'
                    : 'bg-surface-container-highest border-outline-variant/60 group-hover:border-primary/50 text-transparent'"
                >
                  <span class="material-symbols-outlined text-[13px] font-black leading-none">check</span>
                </div>
                <input
                  type="checkbox"
                  v-model="gearCheckedMap[`day-${gi}`]"
                  class="sr-only"
                />
                <span
                  class="text-body-sm transition-all"
                  :class="gearCheckedMap[`day-${gi}`] ? 'text-on-surface-variant line-through opacity-70' : 'text-on-surface font-medium'"
                >
                  {{ g }}
                </span>
              </label>
            </div>
          </div>

          <!-- Overnight Gear Checklist -->
          <div v-if="mountain.gear_night && mountain.gear_night.length" class="space-y-1.5 pt-2 border-t border-outline-variant/20">
            <h5 class="text-caption font-bold text-on-surface-variant uppercase tracking-wider flex items-center gap-1">
              <span class="material-symbols-outlined text-[15px] text-secondary">bed</span>
              <span>过夜 / 露营高山进阶装备</span>
            </h5>
            <div class="grid grid-cols-1 gap-1.5">
              <label
                v-for="(g, gi) in mountain.gear_night"
                :key="`g-night-${gi}`"
                class="flex items-center gap-2.5 p-2 rounded-xl bg-surface-container-low/70 border border-outline-variant/20 cursor-pointer hover:bg-surface-container-low transition-colors group select-none"
              >
                <!-- Custom Stitch Alpine Checkbox -->
                <div
                  class="w-4 h-4 rounded border flex items-center justify-center transition-all duration-200 flex-shrink-0"
                  :class="gearCheckedMap[`night-${gi}`]
                    ? 'bg-secondary border-secondary text-[#0a0e17] shadow-[0_0_8px_rgba(76,215,246,0.35)]'
                    : 'bg-surface-container-highest border-outline-variant/60 group-hover:border-secondary/50 text-transparent'"
                >
                  <span class="material-symbols-outlined text-[13px] font-black leading-none">check</span>
                </div>
                <input
                  type="checkbox"
                  v-model="gearCheckedMap[`night-${gi}`]"
                  class="sr-only"
                />
                <span
                  class="text-body-sm transition-all"
                  :class="gearCheckedMap[`night-${gi}`] ? 'text-on-surface-variant line-through opacity-70' : 'text-on-surface font-medium'"
                >
                  {{ g }}
                </span>
              </label>
            </div>
          </div>

          <div v-if="mountain.gear_detail" class="text-caption text-on-surface-variant p-2 rounded-lg bg-surface-container-low/50">
            <strong>专业装备建议:</strong> {{ mountain.gear_detail }}
          </div>
        </section>

        <!-- ================= MODULE 8: 餐饮住宿 (Food & Stay) ================= -->
        <section
          id="mod-food-stay"
          class="detail-module-card detail-module-food-stay p-4 rounded-2xl bg-surface-container-high/80 border border-outline-variant/30 space-y-3"
          data-module="food-stay"
        >
          <div class="flex items-center justify-between">
            <h4 class="text-body-lg font-bold text-on-surface flex items-center gap-2">
              <span class="material-symbols-outlined text-secondary text-[20px]">restaurant</span>
              <span>8. 餐饮补给与住宿营地</span>
            </h4>
            <span class="text-caption text-secondary font-mono font-semibold">FOOD & STAY</span>
          </div>

          <!-- Food Section -->
          <div v-if="mountain.food && mountain.food.length" class="space-y-1.5">
            <h5 class="text-caption font-bold text-on-surface-variant uppercase tracking-wider flex items-center gap-1">
              <span class="material-symbols-outlined text-[15px] text-primary">local_dining</span>
              <span>特色餐饮与路餐补给推荐</span>
            </h5>
            <div class="space-y-1">
              <p
                v-for="(f, fi) in mountain.food"
                :key="`food-${fi}`"
                class="p-2.5 rounded-xl bg-surface-container-low/70 border border-outline-variant/20 text-body-sm text-on-surface-variant leading-relaxed"
              >
                {{ f }}
              </p>
            </div>
          </div>

          <!-- Stay Section -->
          <div v-if="mountain.stay && mountain.stay.length" class="space-y-1.5 pt-2 border-t border-outline-variant/20">
            <h5 class="text-caption font-bold text-on-surface-variant uppercase tracking-wider flex items-center gap-1">
              <span class="material-symbols-outlined text-[15px] text-secondary">hotel</span>
              <span>住宿与扎营点推荐</span>
            </h5>
            <div class="space-y-1">
              <p
                v-for="(s, si) in mountain.stay"
                :key="`stay-${si}`"
                class="p-2.5 rounded-xl bg-surface-container-low/70 border border-outline-variant/20 text-body-sm text-on-surface-variant leading-relaxed"
              >
                {{ s }}
              </p>
            </div>
          </div>

          <!-- Overnight Plan -->
          <div v-if="mountain.overnight_plan && mountain.overnight_plan.length" class="p-2.5 rounded-xl bg-surface-container-low/60 border border-outline-variant/20 text-body-sm text-on-surface-variant space-y-1">
            <strong class="text-on-surface flex items-center gap-1 text-caption font-bold">
              <span class="material-symbols-outlined text-[16px] text-tertiary-fixed-dim">bedtime</span>
              日出与过夜方案
            </strong>
            <p v-for="(op, opi) in mountain.overnight_plan" :key="`op-${opi}`" class="text-[12px] leading-relaxed">
              {{ op }}
            </p>
          </div>
        </section>

        <!-- ================= MODULE 9: 门票费用 (Tickets & Budget) ================= -->
        <section
          id="mod-tickets"
          class="detail-module-card detail-module-tickets p-4 rounded-2xl bg-surface-container-high/80 border border-outline-variant/30 space-y-3"
          data-module="tickets"
        >
          <div class="flex items-center justify-between">
            <h4 class="text-body-lg font-bold text-on-surface flex items-center gap-2">
              <span class="material-symbols-outlined text-primary text-[20px]">confirmation_number</span>
              <span>9. 门票预约与预算参考</span>
            </h4>
            <span class="text-caption text-primary font-mono font-semibold">
              {{ mountain.free ? '免费山峰' : '收费景区' }}
            </span>
          </div>

          <!-- Ticket Policy -->
          <div v-if="mountain.ticket" class="p-3 rounded-xl bg-surface-container-low/70 border border-outline-variant/20 space-y-1 text-body-sm">
            <strong class="text-on-surface">门票与观光车政策:</strong>
            <p class="text-on-surface-variant leading-relaxed">{{ mountain.ticket }}</p>
          </div>

          <!-- Booking Required Info -->
          <div v-if="mountain.booking_required" class="p-2.5 rounded-xl bg-surface-container-low/60 border border-outline-variant/20 text-body-sm text-on-surface-variant space-y-0.5">
            <strong class="text-on-surface">预约要求与渠道:</strong>
            <p class="text-[12px] leading-relaxed">{{ mountain.booking_required }}</p>
          </div>

          <!-- Cableway Info -->
          <div v-if="mountain.cableway" class="flex items-start gap-2 text-body-sm text-on-surface-variant">
            <span class="material-symbols-outlined text-secondary text-[18px] flex-shrink-0 mt-0.5">cable</span>
            <div>
              <strong class="text-on-surface">索道/轨道交通:</strong>
              <p class="mt-0.5 leading-relaxed">{{ mountain.cableway }}</p>
            </div>
          </div>

          <!-- 2-Person Estimated Budget -->
          <div v-if="mountain.cost_2p || mountain.cost_per_person" class="p-3 rounded-xl bg-surface-container-low/80 border border-primary/25 space-y-1 text-body-sm">
            <div class="flex items-center gap-1.5 text-primary font-bold text-caption">
              <span class="material-symbols-outlined text-[16px]">account_balance_wallet</span>
              <span>自驾预算核算（双人/人均参考）</span>
            </div>
            <p class="text-on-surface leading-relaxed text-[12px]">
              {{ mountain.cost_2p || mountain.cost_per_person }}
            </p>
          </div>
        </section>

        <!-- ================= MODULE 10: 环保倡议 (Leave No Trace) ================= -->
        <section
          id="mod-eco"
          class="detail-module-card detail-module-eco p-4 rounded-2xl bg-surface-container-high/80 border border-outline-variant/30 space-y-3"
          data-module="eco"
        >
          <div class="flex items-center justify-between">
            <h4 class="text-body-lg font-bold text-on-surface flex items-center gap-2">
              <span class="material-symbols-outlined text-emerald-400 text-[20px]">eco</span>
              <span>10. 极光无痕山林倡议 (LNT)</span>
            </h4>
            <span class="text-caption text-emerald-400 font-mono font-semibold">LEAVE NO TRACE</span>
          </div>

          <!-- LNT 7 Principles Localized -->
          <div class="grid grid-cols-1 gap-2">
            <div class="p-2.5 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-body-sm text-emerald-100/90 space-y-1">
              <div class="flex items-center gap-2 font-bold text-emerald-300 text-caption">
                <span class="material-symbols-outlined text-[16px]">delete_forever</span>
                <span>全量带走垃圾，严禁遗弃残渣</span>
              </div>
              <p class="text-[12px] leading-relaxed">
                自备密封垃圾袋，将塑料瓶、包装袋、果皮纸巾及自热火锅/米饭残汤全量带下山处理。
              </p>
            </div>

            <div class="p-2.5 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-body-sm text-emerald-100/90 space-y-1">
              <div class="flex items-center gap-2 font-bold text-emerald-300 text-caption">
                <span class="material-symbols-outlined text-[16px]">local_fire_department</span>
                <span>严禁野外违规用火，杜绝火灾</span>
              </div>
              <p class="text-[12px] leading-relaxed">
                川西林区及高山草甸全年禁止野外篝火生火，遵守森林草原防灭火条例。
              </p>
            </div>

            <div class="p-2.5 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-body-sm text-emerald-100/90 space-y-1">
              <div class="flex items-center gap-2 font-bold text-emerald-300 text-caption">
                <span class="material-symbols-outlined text-[16px]">yard</span>
                <span>爱护珍稀植物，严禁踩踏采摘</span>
              </div>
              <p class="text-[12px] leading-relaxed">
                高山杜鹃、绿绒蒿、雪兔子生长极度缓慢，严禁采摘；只在既有路面上行走，不碾压脆弱草甸。
              </p>
            </div>
          </div>

          <!-- Local Community Tips -->
          <div v-if="mountain.local_tips" class="p-2.5 rounded-xl bg-surface-container-low/70 border border-outline-variant/20 text-body-sm text-on-surface-variant">
            <strong class="text-on-surface">属地民俗与环保要求:</strong>
            <p class="mt-0.5 leading-relaxed">{{ mountain.local_tips }}</p>
          </div>

          <div v-if="mountain.map_note" class="text-caption text-on-surface-variant p-2 rounded-lg bg-surface-container-low/50">
            <strong>生态保护区提示:</strong> {{ mountain.map_note }}
          </div>
        </section>

        <!-- ================= MODULE 11: 天气预报 (Weather Forecast) ================= -->
        <section
          id="mod-weather"
          class="detail-module-card detail-module-weather p-4 rounded-2xl bg-surface-container-high/80 border border-outline-variant/30 space-y-3"
          data-module="weather"
        >
          <div class="flex items-center justify-between">
            <h4 class="text-body-lg font-bold text-on-surface flex items-center gap-2">
              <span class="material-symbols-outlined text-secondary text-[20px]">cloud_sync</span>
              <span>11. 实时天气与气象观景窗口</span>
            </h4>
            <span class="text-caption text-secondary font-mono font-semibold">METEOROLOGY</span>
          </div>

          <!-- Live 7-Day Weather Forecast Component -->
          <MountainWeatherCard :mountain="mountain" :auto-load="true" />

          <!-- Weather Search Keywords (Default Collapsed Advanced Guide) -->
          <details
            v-if="mountain.weather_keywords && mountain.weather_keywords.length"
            class="group rounded-xl border border-outline-variant/30 bg-surface-container-low/60 overflow-hidden transition-all duration-200"
          >
            <summary class="px-3 py-2 cursor-pointer list-none flex items-center justify-between text-caption font-semibold text-on-surface-variant hover:text-on-surface select-none">
              <span class="flex items-center gap-1.5">
                <span class="material-symbols-outlined text-[16px] text-secondary">travel_explore</span>
                <span>进阶：第三方专业气象检索别名 (Windy / 墨迹)</span>
              </span>
              <span class="material-symbols-outlined text-[16px] text-on-surface-variant group-open:rotate-180 transition-transform duration-200">
                expand_more
              </span>
            </summary>
            <div class="px-3 pb-2.5 pt-1 space-y-1 border-t border-outline-variant/20">
              <p
                v-for="(wk, wki) in mountain.weather_keywords"
                :key="`wk-${wki}`"
                class="p-2 rounded-lg bg-surface-container/70 border border-outline-variant/20 text-body-sm text-on-surface-variant font-mono text-[11.5px]"
              >
                {{ wk }}
              </p>
            </div>
          </details>

          <!-- Four Seasons Breakdown -->
          <div v-if="mountain.season_best && mountain.season_best.length" class="space-y-1.5 pt-2 border-t border-outline-variant/20">
            <h5 class="text-caption font-bold text-on-surface-variant uppercase tracking-wider">四季观景特征解析</h5>
            <div class="space-y-1">
              <p
                v-for="(sb, sbi) in mountain.season_best"
                :key="`sb-${sbi}`"
                class="p-2 rounded-xl bg-surface-container-low/50 border border-outline-variant/15 text-body-sm text-on-surface-variant text-[12px] leading-relaxed"
              >
                {{ sb }}
              </p>
            </div>
          </div>

          <!-- Cloud Sea Window Rule -->
          <div class="p-2.5 rounded-xl bg-surface-container-low/70 border border-secondary/30 text-body-sm text-secondary space-y-1">
            <strong class="text-on-surface flex items-center gap-1 text-caption font-bold">
              <span class="material-symbols-outlined text-[16px] text-secondary">insights</span>
              云海与日照金山窗口定律
            </strong>
            <p class="text-[12px] leading-relaxed text-on-surface-variant">
              雨后初晴第 1-2 天清晨出现云海概率最高；风速需低于 3 级（低于 12km/h）；逆温层位于 2500-3200m 区间时呈现磅礴云海盛景。
            </p>
          </div>
        </section>

        <!-- ================= MODULE 12: 核验来源 (Sources & Audit) ================= -->
        <section
          id="mod-sources"
          class="detail-module-card detail-module-sources p-4 rounded-2xl bg-surface-container-high/80 border border-outline-variant/30 space-y-3"
          data-module="sources"
        >
          <div class="flex items-center justify-between">
            <h4 class="text-body-lg font-bold text-on-surface flex items-center gap-2">
              <span class="material-symbols-outlined text-primary text-[20px]">fact_check</span>
              <span>12. 数据核验与信源引用</span>
            </h4>
            <span class="text-caption text-primary font-mono font-semibold">VERIFICATION</span>
          </div>

          <!-- Source Citations List -->
          <div v-if="mountain.sources && mountain.sources.length" class="space-y-1.5">
            <h5 class="text-caption font-bold text-on-surface-variant uppercase tracking-wider">公开文献与媒体核实清单 ({{ mountain.sources.length }} 条)</h5>
            <div class="space-y-1">
              <a
                v-for="(src, srci) in mountain.sources"
                :key="`src-${srci}`"
                :href="src.url"
                target="_blank"
                rel="noopener noreferrer"
                class="p-2.5 rounded-xl bg-surface-container-low/70 border border-outline-variant/20 flex items-start justify-between gap-2 text-body-sm text-on-surface hover:border-primary/40 transition-colors group block"
              >
                <div class="flex items-start gap-1.5 min-w-0">
                  <span class="material-symbols-outlined text-primary text-[16px] flex-shrink-0 mt-0.5">link</span>
                  <span class="group-hover:text-primary transition-colors leading-snug line-clamp-2">{{ src.title }}</span>
                </div>
                <span v-if="src.date" class="text-[10px] font-mono text-on-surface-variant flex-shrink-0 ml-1">
                  {{ src.date }}
                </span>
              </a>
            </div>
          </div>

          <!-- Deepen vs Unverified Fields Tagging -->
          <div class="space-y-2 pt-2 border-t border-outline-variant/20 text-caption font-mono">
            <div v-if="mountain.deepen_fields && mountain.deepen_fields.length" class="text-on-surface-variant">
              <strong class="text-primary font-sans">多源交叉深度核验字段:</strong>
              <div class="flex flex-wrap gap-1 mt-1">
                <span
                  v-for="df in mountain.deepen_fields"
                  :key="df"
                  class="px-1.5 py-0.5 rounded bg-primary/10 text-primary border border-primary/20"
                >
                  {{ df }}
                </span>
              </div>
            </div>

            <div v-if="mountain.unverified_fields && mountain.unverified_fields.length" class="text-on-surface-variant">
              <strong class="text-tertiary-fixed-dim font-sans">待现场复核字段:</strong>
              <div class="flex flex-wrap gap-1 mt-1">
                <span
                  v-for="uf in mountain.unverified_fields"
                  :key="uf"
                  class="px-1.5 py-0.5 rounded bg-tertiary/10 text-tertiary-fixed-dim border border-tertiary/20"
                >
                  {{ uf }}
                </span>
              </div>
            </div>
          </div>

          <p class="text-[11px] text-on-surface-variant leading-relaxed p-2.5 rounded-xl bg-surface-container-low/40 border border-outline-variant/15">
            <strong>免责与更新说明:</strong> 本档案由四川户外志愿者与公开资讯整理，高山气候与景区运营政策变动频繁，出行前请务必向当地文旅与景区管理渠道复核最新路况与开放情况。
          </p>
        </section>
      </div>

      <!-- Sticky Bottom Action Bar -->
      <footer class="flex-shrink-0 p-3.5 bg-surface-container/95 backdrop-blur-2xl border-t border-outline-variant/30 flex items-center gap-2.5 z-30 shadow-[0_-8px_24px_rgba(0,0,0,0.6)]">
        <!-- Direct Navigation Button -->
        <button
          type="button"
          @click="openNavigationPicker"
          class="btn-bottom-nav py-3 px-3.5 rounded-2xl bg-secondary/15 hover:bg-secondary/25 border border-secondary/40 text-secondary text-body-sm font-bold flex items-center justify-center gap-1.5 active:scale-95 transition-all"
          title="打开手机地图导航"
        >
          <span class="material-symbols-outlined text-[19px]">navigation</span>
          <span class="whitespace-nowrap">导航</span>
        </button>

        <!-- Add to Plan Button -->
        <button
          type="button"
          @click="handleAddToPlan"
          class="flex-1 py-3 px-2 rounded-2xl frost-glass border border-secondary/40 text-secondary text-body-sm font-bold flex items-center justify-center gap-1.5 active:scale-95 hover:border-secondary transition-all"
        >
          <span class="material-symbols-outlined text-[19px]">
            {{ isInPlan ? 'event_available' : 'add_circle' }}
          </span>
          <span class="truncate">{{ isInPlan ? '已在计划' : '加入计划' }}</span>
        </button>

        <!-- Primary Summit Checkin Toggle Button -->
        <button
          type="button"
          @click="handleToggleCheckin"
          class="btn-checkin-toggle flex-1 py-3 px-2 rounded-2xl font-bold text-body-sm flex items-center justify-center gap-1.5 active:scale-95 transition-all shadow-lg"
          :class="isChecked
            ? 'bg-primary/20 text-primary border border-primary/60 glow-primary'
            : 'bg-primary text-on-primary hover:bg-primary-hover glow-primary'"
        >
          <span class="material-symbols-outlined text-[19px]">
            {{ isChecked ? 'check_circle' : 'flag' }}
          </span>
          <span class="truncate">{{ isChecked ? '✓ 已打卡' : '🏔️ 登顶打卡' }}</span>
        </button>
      </footer>
    </aside>
  </Transition>
</template>

<script setup>
import { ref, computed, watch, reactive, nextTick, onMounted, onUnmounted } from 'vue';
import { useCheckinStore, derivedNums } from '@/stores/checkinStore.js';
import { usePlanStore } from '@/stores/planStore.js';
import { useRegionStore } from '@/stores/regionStore.js';
import RouteElevationChart from '@/components/detail/RouteElevationChart.vue';
import MountainWeatherCard from '@/components/weather/MountainWeatherCard.vue';
import {
  isIos,
  launchTwoBulu,
  launchFootTouch,
  launchNavigation,
  NAVIGATION_APPS,
  cleanTrackKeyword,
  copyToClipboard
} from '@/utils/appLauncher.js';
import { getMountainCoordinate } from '@/stores/mountainStore.js';

const props = defineProps({
  mountain: {
    type: Object,
    default: null
  },
  modelValue: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits([
  'update:modelValue',
  'checkin',
  'add-plan',
  'probe-waypoint',
  'clear-probe',
  'toast'
]);

const checkinStore = useCheckinStore();
const planStore = usePlanStore();
const regionStore = useRegionStore();

const scrollContainerRef = ref(null);
const sheetAsideRef = ref(null);

function preventAsideScroll(e) {
  if (e.target && e.target.scrollTop !== 0) {
    e.target.scrollTop = 0;
  }
}
const activeAnchor = ref('overview');
const gearCheckedMap = reactive({});

// ================= 多图相册与全屏 Lightbox 画廊状态 =================
const currentImageIndex = ref(0);
const imageErrorMap = reactive({});
const isLightboxOpen = ref(false);
const lightboxIndex = ref(0);

const anchorTabs = [
  { id: 'overview', label: '🗺️ 概况' },
  { id: 'routes', label: '🥾 路线' },
  { id: 'waypoints', label: '📈 高程点' },
  { id: 'highlights', label: '✨ 亮点' },
  { id: 'road', label: '🚗 路况' },
  { id: 'safety', label: '🛡️ 安全' },
  { id: 'gear', label: '🎒 装备' },
  { id: 'food-stay', label: '⛺ 宿食' },
  { id: 'tickets', label: '🎫 门票' },
  { id: 'eco', label: '🌿 环保' },
  { id: 'weather', label: '☀️ 天气' },
  { id: 'sources', label: '🔍 来源' }
];

const nums = computed(() => {
  return derivedNums(props.mountain);
});

const isChecked = computed(() => {
  if (!props.mountain?.id) return false;
  return checkinStore.isDone(props.mountain.id);
});

const isInPlan = computed(() => {
  if (!props.mountain?.id) return false;
  return planStore.plans.some(w => w.items.includes(props.mountain.id));
});

const diffLabel = computed(() => {
  const d = props.mountain?.difficulty;
  if (d === 'L1') return '初级休闲';
  if (d === 'L2') return '进阶徒步';
  if (d === 'L3') return '中级高山';
  if (d === 'L4') return '挑战自虐';
  if (d === 'L5') return '极限探索';
  return '推荐路线';
});

const diffBadgeClass = computed(() => {
  const d = props.mountain?.difficulty;
  if (d === 'L1') return 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40';
  if (d === 'L2') return 'bg-sky-500/20 text-sky-300 border-sky-500/40';
  if (d === 'L3') return 'bg-amber-500/20 text-amber-300 border-amber-500/40';
  if (d === 'L4' || d === 'L5') return 'bg-rose-500/20 text-rose-300 border-rose-500/40';
  return 'bg-primary/20 text-primary border-primary/40';
});

const durationText = computed(() => {
  if (nums.value.dur) return `${nums.value.dur}h`;
  const r0 = props.mountain?.routes?.[0];
  if (r0?.hours) {
    const str = String(r0.hours);
    const m = str.match(/(\d+(?:-\d+)?\s*(?:小时|h))/);
    if (m) return m[1];
    if (str.includes('半日')) return '半日';
    if (str.length <= 8) return str;
    return '单日/半日';
  }
  return '半日/单日';
});

const locationShort = computed(() => {
  const c = props.mountain?.county || '';
  const match = c.match(/(?:四川省)?(?:([^市]+市|[^州]+州))?([^县区]+[县区])/);
  if (match) return `${match[1] || ''}${match[2] || ''}`;
  return '川西周边';
});

const weatherCondition = computed(() => {
  const alt = props.mountain?.altitude_m || 3000;
  if (alt > 4000) return '高海拔风雪';
  if (alt > 3000) return '高山云海';
  return '温带多云';
});

const seasonBestText = computed(() => {
  const raw = props.mountain?.season_best || props.mountain?.best_season;
  if (Array.isArray(raw) && raw.length) {
    return raw
      .map(s => {
        if (typeof s !== 'string') return '';
        return (s.split(/[：:]/)[0] || '').trim();
      })
      .filter(Boolean)
      .join(' · ');
  }
  if (typeof raw === 'string') return raw;
  return '春季 / 秋季晴好窗口';
});

const totalGearCount = computed(() => {
  const d = props.mountain?.gear_day?.length || 0;
  const n = props.mountain?.gear_night?.length || 0;
  return d + n;
});

const checkedGearCount = computed(() => {
  return Object.values(gearCheckedMap).filter(Boolean).length;
});

// ================= 高山暗黑黑曜石与极光绿图片加载兜底 =================
function heroFallbackSvg(name) {
  const title = encodeURIComponent(name || 'Alpine Peak');
  return `data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="600" height="300" viewBox="0 0 600 300"><defs><linearGradient id="g" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="%23181b25"/><stop offset="50%" stop-color="%23262a34"/><stop offset="100%" stop-color="%230f131c"/></linearGradient></defs><rect width="100%" height="100%" fill="url(%23g)"/><text x="50%" y="45%" dominant-baseline="middle" text-anchor="middle" fill="%2386948a" font-family="Plus Jakarta Sans, sans-serif" font-size="20" font-weight="bold">${title}</text><text x="50%" y="65%" dominant-baseline="middle" text-anchor="middle" fill="%234edea3" font-family="JetBrains Mono, monospace" font-size="14">ALPINE TOPO · 成都周边50座山</text></svg>`;
}

// ================= 画廊列表计算（严格仅限真实实拍风景照，绝不塞入折线示意图） =================
const galleryList = computed(() => {
  const m = props.mountain;
  if (!m) return [];

  // 若数据中配置了多张真实实拍风景照
  if (Array.isArray(m.gallery) && m.gallery.length > 0) {
    return m.gallery.map((item, i) => {
      const isObj = typeof item === 'object' && item !== null;
      return {
        src: isObj ? item.src : item,
        title: isObj ? item.title : `实景风光 0${i + 1}`,
        desc: isObj ? item.desc : `${m.name} · 真实高山全景实拍`
      };
    });
  }

  // 默认仅呈现 1 张真实的高清实拍风光照片，后续收录更多实景照后再动态扩展
  return [
    {
      src: `assets/mountains/${m.id}.jpg`,
      title: '主峰全貌实景',
      desc: `${m.name} · 标高 ${nums.value.alt}m 四川川西高山全貌实拍`
    }
  ];
});

const activeLightboxImage = computed(() => {
  if (galleryList.value.length === 0) return {};
  return galleryList.value[lightboxIndex.value] || galleryList.value[0] || {};
});

function getSlideSrc(idx) {
  if (imageErrorMap[idx]) {
    return heroFallbackSvg(props.mountain?.name);
  }
  return galleryList.value[idx]?.src || '';
}

function handleImageError(idx) {
  imageErrorMap[idx] = true;
}

function nextImage() {
  if (galleryList.value.length <= 1) return;
  currentImageIndex.value = (currentImageIndex.value + 1) % galleryList.value.length;
}

function prevImage() {
  if (galleryList.value.length <= 1) return;
  currentImageIndex.value = (currentImageIndex.value - 1 + galleryList.value.length) % galleryList.value.length;
}

function goToImage(idx) {
  currentImageIndex.value = idx;
}

function openLightbox(idx = 0) {
  lightboxIndex.value = idx;
  isLightboxOpen.value = true;
}

function closeLightbox() {
  isLightboxOpen.value = false;
  currentImageIndex.value = lightboxIndex.value;
}

function nextLightboxImage() {
  if (galleryList.value.length <= 1) return;
  lightboxIndex.value = (lightboxIndex.value + 1) % galleryList.value.length;
}

function prevLightboxImage() {
  if (galleryList.value.length <= 1) return;
  lightboxIndex.value = (lightboxIndex.value - 1 + galleryList.value.length) % galleryList.value.length;
}

// ================= 触控轻扫滑动手势交互 =================
let heroTouchStartX = 0;
let heroTouchStartY = 0;

function onHeroTouchStart(e) {
  if (e.touches && e.touches[0]) {
    heroTouchStartX = e.touches[0].clientX;
    heroTouchStartY = e.touches[0].clientY;
  }
}

function onHeroTouchMove() {
  // 保持被动滚动体验
}

function onHeroTouchEnd(e) {
  if (e.changedTouches && e.changedTouches[0]) {
    const dx = e.changedTouches[0].clientX - heroTouchStartX;
    const dy = e.changedTouches[0].clientY - heroTouchStartY;
    if (Math.abs(dx) > 36 && Math.abs(dx) > Math.abs(dy)) {
      if (dx < 0) {
        nextImage();
      } else {
        prevImage();
      }
    }
  }
}

let lightboxTouchStartX = 0;
let lightboxTouchStartY = 0;

function onLightboxTouchStart(e) {
  if (e.touches && e.touches[0]) {
    lightboxTouchStartX = e.touches[0].clientX;
    lightboxTouchStartY = e.touches[0].clientY;
  }
}

function onLightboxTouchMove() {
  // 保持被动滚动体验
}

function onLightboxTouchEnd(e) {
  if (e.changedTouches && e.changedTouches[0]) {
    const dx = e.changedTouches[0].clientX - lightboxTouchStartX;
    const dy = e.changedTouches[0].clientY - lightboxTouchStartY;
    if (Math.abs(dx) > 36 && Math.abs(dx) > Math.abs(dy)) {
      if (dx < 0) {
        nextLightboxImage();
      } else {
        prevLightboxImage();
      }
    }
  }
}

// ================= 全局键盘事件监听 (ESC/左右方向键) =================
function handleKeyDown(e) {
  if (!isLightboxOpen.value) return;
  if (e.key === 'Escape') {
    closeLightbox();
  } else if (e.key === 'ArrowRight') {
    nextLightboxImage();
  } else if (e.key === 'ArrowLeft') {
    prevLightboxImage();
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleKeyDown);
});

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeyDown);
});

// ================= 监听与清理 =================
watch(
  () => props.mountain?.id,
  () => {
    currentImageIndex.value = 0;
    lightboxIndex.value = 0;
    Object.keys(imageErrorMap).forEach((k) => delete imageErrorMap[k]);
    Object.keys(gearCheckedMap).forEach((k) => delete gearCheckedMap[k]);
  }
);

watch(
  () => props.modelValue,
  (val) => {
    if (!val) {
      closeLightbox();
      emit('clear-probe');
      Object.keys(gearCheckedMap).forEach((k) => delete gearCheckedMap[k]);
    } else {
      nextTick(() => {
        if (sheetAsideRef.value) {
          sheetAsideRef.value.scrollTop = 0;
        }
      });
    }
  }
);

function closeSheet() {
  closeLightbox();
  emit('clear-probe');
  emit('update:modelValue', false);
}

function scrollToAnchor(id) {
  activeAnchor.value = id;
  const container = scrollContainerRef.value;
  if (!container) return;

  if (id === 'overview') {
    container.scrollTo({ top: 0, behavior: 'smooth' });
    return;
  }

  const target = document.getElementById(`mod-${id}`);
  if (target) {
    const containerRect = container.getBoundingClientRect();
    const targetRect = target.getBoundingClientRect();
    // 导航栏高度约 46px，加上顶部微距共保留 52px 吸顶缓冲
    const navStickyOffset = 52;
    const targetScrollTop = container.scrollTop + (targetRect.top - containerRect.top) - navStickyOffset;
    container.scrollTo({
      top: Math.max(0, targetScrollTop),
      behavior: 'smooth'
    });
  }
}

function handleToggleCheckin() {
  if (!props.mountain?.id) return;
  checkinStore.toggleCheckin(props.mountain.id);
  emit('checkin', props.mountain.id);
}

function handleAddToPlan() {
  if (!props.mountain?.id) return;
  planStore.addToPlan(props.mountain.id);
  emit('add-plan', props.mountain.id);
}

// ================= 手机原生导航与两步路户外 App 联动 =================
const isNavModalOpen = ref(false);
const localToastMsg = ref('');
let localToastTimer = null;

function showSheetToast(msg) {
  localToastMsg.value = msg;
  emit('toast', msg);
  if (localToastTimer) clearTimeout(localToastTimer);
  localToastTimer = setTimeout(() => {
    localToastMsg.value = '';
  }, 2600);
}

const destinationCoord = computed(() => {
  if (!props.mountain) return { lat: 30.65, lng: 104.06 };
  return getMountainCoordinate(props.mountain);
});

const currentDestinationName = computed(() => {
  if (!props.mountain) return '';
  return props.mountain.name + (props.mountain.nav_point ? ` · ${props.mountain.nav_point.split(/[,，;；]/)[0]}` : '');
});

const availableNavApps = computed(() => {
  const isAppleDevice = isIos();
  return NAVIGATION_APPS.filter((app) => {
    if (app.showOnlyIos && !isAppleDevice) return false;
    return true;
  });
});

function openNavigationPicker() {
  isNavModalOpen.value = true;
}

function closeNavigationPicker() {
  isNavModalOpen.value = false;
}

function handleSelectNavApp(app) {
  const dest = {
    lat: destinationCoord.value.lat,
    lng: destinationCoord.value.lng,
    name: currentDestinationName.value
  };
  launchNavigation(app.id, dest);
  showSheetToast(`正在为你打开 ${app.name}...`);
  setTimeout(() => {
    isNavModalOpen.value = false;
  }, 400);
}

async function copyDestinationText() {
  const text = `${currentDestinationName.value} (GPS: ${destinationCoord.value.lat.toFixed(4)}, ${destinationCoord.value.lng.toFixed(4)})`;
  const ok = await copyToClipboard(text);
  if (ok) {
    showSheetToast('已复制目的地与 GPS 坐标！');
  }
}

async function handleLaunchTwoBulu(rawKw) {
  const res = await launchTwoBulu(rawKw);
  showSheetToast(`已复制「${res.keyword}」，正在调起两步路 App...`);
}

async function handleLaunchFootTouch(rawKw) {
  const res = await launchFootTouch(rawKw);
  showSheetToast(`已复制「${res.keyword}」，正在调起六只脚 App...`);
}

async function copyKeywordOnly(rawKw) {
  const clean = cleanTrackKeyword(rawKw);
  const ok = await copyToClipboard(clean);
  if (ok) {
    showSheetToast(`已复制搜索词：「${clean}」`);
  }
}

async function copyText(str) {
  if (!str) return;
  const ok = await copyToClipboard(str);
  if (ok) {
    showSheetToast(`已复制到剪贴板！`);
  }
}
</script>

<style scoped>
.detail-module-card {
  scroll-margin-top: 64px;
}

.slide-up-enter-active,
.slide-up-leave-active {
  transition: transform 0.32s cubic-bezier(0.16, 1, 0.3, 1), opacity 0.28s ease;
}

.slide-up-enter-from,
.slide-up-leave-to {
  transform: translateY(100%);
  opacity: 0.8;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.25s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
