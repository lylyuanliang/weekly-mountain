<template>
  <Teleport to="body">
    <Transition name="fade">
      <div
        v-if="visible"
        class="alpine-poster-modal fixed inset-0 z-50 bg-black/85 backdrop-blur-md flex flex-col items-center justify-start overflow-y-auto px-3 pt-[calc(14px+max(env(safe-area-inset-top,0px),34px))] pb-[calc(14px+max(env(safe-area-inset-bottom,0px),16px))] sm:p-6"
        @click.self="handleClose"
      >
        <!-- 弹窗顶栏控制区 -->
        <div class="w-full max-w-[390px] flex items-center justify-between pb-3 px-1 text-on-surface">
          <div class="flex items-center gap-2">
            <span class="w-2 h-2 rounded-full bg-primary animate-pulse"></span>
            <span class="font-headline-md text-[16px] font-bold tracking-tight text-white">Alpine Explorer 成就长图</span>
          </div>
          <button
            @click="handleClose"
            class="w-8 h-8 rounded-full bg-surface-container-high/80 border border-white/10 hover:border-primary/40 flex items-center justify-center text-on-surface-variant hover:text-on-surface active:scale-95 transition-all"
            aria-label="关闭海报弹窗"
          >
            <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <!-- 海报生成与导出定制控制卡片 -->
        <div class="w-full max-w-[390px] mb-3 p-3.5 rounded-2xl bg-surface-container/90 border border-white/10 space-y-3 select-none shadow-xl">
          <div class="flex items-center justify-between border-b border-white/10 pb-2">
            <span class="text-[12px] font-bold text-white flex items-center gap-1.5">
              <svg class="w-4 h-4 text-emerald-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="3" />
                <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z" />
              </svg>
              <span>海报导出参数定制</span>
            </span>
            <span class="text-[10px] text-gray-400 font-mono">实时渲染 · 灵活勾选</span>
          </div>

          <!-- 选项 1: 是否包含打卡照片 (开关) -->
          <div class="flex items-center justify-between">
            <div class="flex flex-col">
              <span class="text-[12px] font-medium text-white flex items-center gap-1.5">
                <span>包含登顶实拍照片</span>
                <span
                  class="text-[9px] px-1.5 py-0.2 rounded font-mono"
                  :class="includePhotos ? 'bg-emerald-400/20 text-emerald-300' : 'bg-white/10 text-gray-400'"
                >
                  {{ includePhotos ? '开启实拍海报' : '纯净拓扑勋章' }}
                </span>
              </span>
              <span class="text-[10px] text-gray-400">关闭后仅呈现等高线名山徽章，节省画幅更纯粹</span>
            </div>
            <button
              type="button"
              @click="includePhotos = !includePhotos"
              class="w-11 h-6 rounded-full transition-colors relative flex items-center p-0.5"
              :class="includePhotos ? 'bg-emerald-500' : 'bg-surface-container-high border border-white/20'"
              role="switch"
              :aria-checked="includePhotos"
              aria-label="切换海报是否包含照片"
            >
              <div
                class="w-5 h-5 rounded-full bg-white transition-transform shadow-md"
                :class="includePhotos ? 'translate-x-5' : 'translate-x-0'"
              ></div>
            </button>
          </div>

          <!-- 选项 2: 勾选特定打卡山峰导出 -->
          <div v-if="allCheckedMountains.length > 0" class="space-y-1.5 pt-2 border-t border-white/5">
            <div class="flex items-center justify-between text-[11px]">
              <span class="text-gray-300 font-medium">
                勾选展示名山 ({{ selectedMountainIds.length }}/{{ allCheckedMountains.length }})
              </span>
              <div class="flex items-center gap-2">
                <button
                  type="button"
                  @click="selectAllMountains"
                  class="text-[10px] text-emerald-400 hover:underline active:scale-95 transition-transform"
                >
                  全选
                </button>
                <span class="text-white/20">|</span>
                <button
                  type="button"
                  @click="clearAllMountains"
                  class="text-[10px] text-gray-400 hover:text-white active:scale-95 transition-transform"
                >
                  清空
                </button>
              </div>
            </div>

            <!-- 可水平滚动/折行的名山胶囊选择器 -->
            <div class="flex flex-wrap gap-1.5 max-h-24 overflow-y-auto pr-1">
              <button
                v-for="m in allCheckedMountains"
                :key="m.id"
                type="button"
                @click="toggleMountainSelection(m.id)"
                class="px-2 py-1 rounded-lg text-[10px] font-medium border transition-all flex items-center gap-1 active:scale-95"
                :class="selectedMountainIds.includes(m.id)
                  ? 'bg-emerald-500/20 border-emerald-400/50 text-emerald-300'
                  : 'bg-surface-container-high/60 border-white/10 text-gray-400 hover:text-gray-200'"
              >
                <span class="w-1.5 h-1.5 rounded-full" :class="selectedMountainIds.includes(m.id) ? 'bg-emerald-400' : 'bg-gray-600'"></span>
                <span>{{ m.name }}</span>
                <span v-if="m.photos?.length > 0" class="text-[9px] text-emerald-400/80">📷</span>
              </button>
            </div>
          </div>
        </div>

        <!-- 海报渲染容器 (用于 html2canvas 精准抓取) -->
        <div
          ref="posterRef"
          class="alpine-poster-canvas w-full max-w-[390px] rounded-3xl overflow-hidden shadow-2xl relative select-none"
          style="background: linear-gradient(180deg, #090d16 0%, #0d1320 50%, #090d16 100%); border: 1px solid rgba(255, 255, 255, 0.12);"
        >
          <!-- 背景拓扑微光与等高线纹理 -->
          <div class="absolute inset-0 pointer-events-none overflow-hidden opacity-35">
            <svg class="w-full h-full" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 800" preserveAspectRatio="none">
              <defs>
                <linearGradient id="topo-grad" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stop-color="#4edea3" stop-opacity="0.25" />
                  <stop offset="50%" stop-color="#4cd7f6" stop-opacity="0.1" />
                  <stop offset="100%" stop-color="#ffb95f" stop-opacity="0.05" />
                </linearGradient>
              </defs>
              <path d="M-50,120 Q100,80 200,140 T450,110" fill="none" stroke="url(#topo-grad)" stroke-width="1.2" stroke-dasharray="4,4" />
              <path d="M-50,220 Q150,160 250,240 T450,190" fill="none" stroke="url(#topo-grad)" stroke-width="1" />
              <path d="M-50,380 Q120,320 220,410 T450,350" fill="none" stroke="url(#topo-grad)" stroke-width="1.2" stroke-dasharray="6,4" />
              <path d="M-50,540 Q180,480 280,560 T450,510" fill="none" stroke="url(#topo-grad)" stroke-width="1" />
              <path d="M-50,680 Q140,620 240,710 T450,650" fill="none" stroke="url(#topo-grad)" stroke-width="1.2" />
            </svg>
          </div>

          <!-- 海报顶部 Ambient Glow -->
          <div class="absolute -top-16 -right-16 w-48 h-48 rounded-full pointer-events-none" style="background: radial-gradient(circle, rgba(78, 222, 163, 0.28) 0%, transparent 70%);"></div>
          <div class="absolute top-48 -left-16 w-40 h-40 rounded-full pointer-events-none" style="background: radial-gradient(circle, rgba(76, 215, 246, 0.2) 0%, transparent 70%);"></div>

          <!-- ================= 海报内容主体 ================= -->
          <div class="relative z-10 p-5 space-y-4 text-white">
            <!-- 1. 品牌徽标与官方认证标识 -->
            <div class="flex items-center justify-between border-b border-white/10 pb-3">
              <div class="flex items-center gap-2.5">
                <div class="w-8 h-8 rounded-xl bg-gradient-to-br from-emerald-400/30 to-cyan-400/20 border border-emerald-400/40 flex items-center justify-center shadow-[0_0_12px_rgba(78,222,163,0.3)]">
                  <!-- 高山 Vector 徽标 -->
                  <svg class="w-5 h-5 text-emerald-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M3 20h18L15 6l-4 7-3-4-5 11z" />
                  </svg>
                </div>
                <div class="flex flex-col">
                  <span class="font-bold text-[14px] tracking-wider text-white flex items-center gap-1">
                    ALPINE EXPLORER
                    <span class="text-[9px] px-1 py-0.2 rounded bg-emerald-400/20 text-emerald-300 font-mono">PRO</span>
                  </span>
                  <span class="text-[9px] text-gray-400 tracking-widest uppercase font-mono">成都市周边名山巡礼 · 50座</span>
                </div>
              </div>
              <div class="text-right">
                <span class="text-[9px] font-mono text-cyan-400 tracking-wider">OFFICIAL TOPO</span>
                <div class="text-[10px] text-gray-300 font-medium">探索者里程档案</div>
              </div>
            </div>

            <!-- 2. 用户军衔徽章与圆环进度 Bento -->
            <div class="p-3.5 rounded-2xl border border-white/10 relative overflow-hidden" style="background: rgba(28, 31, 41, 0.75);">
              <div class="flex items-center justify-between">
                <div class="space-y-1">
                  <div class="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-emerald-500/15 border border-emerald-400/30 text-emerald-300 text-[10px] font-mono">
                    <svg class="w-3 h-3 text-emerald-400" viewBox="0 0 24 24" fill="currentColor">
                      <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
                    </svg>
                    <span>{{ checkinStore.stats.rank.level }} · {{ checkinStore.stats.rank.title }}</span>
                  </div>
                  <div class="text-[20px] font-bold text-white tracking-tight flex items-baseline gap-1">
                    <span>已征服</span>
                    <span class="text-[26px] font-bold text-emerald-400 font-mono">{{ checkinStore.stats.doneCount }}</span>
                    <span class="text-[13px] text-gray-400 font-normal">/ {{ totalMountainsCount }} 座名山</span>
                  </div>
                  <div class="text-[10px] text-gray-400">
                    四川西部山原高山拓扑峰线完成度
                  </div>
                </div>

                <!-- 进度环 -->
                <div class="relative w-16 h-16 flex items-center justify-center shrink-0">
                  <svg class="w-16 h-16 transform -rotate-90" viewBox="0 0 64 64">
                    <circle cx="32" cy="32" fill="none" r="26" stroke="rgba(255,255,255,0.08)" stroke-width="4.5" />
                    <circle
                      cx="32"
                      cy="32"
                      fill="none"
                      r="26"
                      stroke="#4edea3"
                      stroke-dasharray="163"
                      :stroke-dashoffset="163 - (163 * checkinStore.stats.completionRate) / 100"
                      stroke-linecap="round"
                      stroke-width="4.5"
                    />
                  </svg>
                  <div class="absolute flex flex-col items-center">
                    <span class="text-[12px] font-bold text-emerald-400 font-mono">{{ checkinStore.stats.completionRate }}%</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- 3. 三列核心遥测指标 -->
            <div class="grid grid-cols-3 gap-2 p-3 rounded-2xl border border-white/10" style="background: rgba(15, 19, 28, 0.85);">
              <div class="flex flex-col">
                <span class="text-[10px] text-gray-400 flex items-center gap-1 font-mono">
                  <svg class="w-3 h-3 text-emerald-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                  </svg>
                  累计爬升
                </span>
                <span class="text-[15px] font-bold text-white font-mono mt-1 truncate">
                  +{{ checkinStore.stats.totalAscent.toLocaleString() }}<span class="text-[9px] text-gray-400 ml-0.5 font-normal">m</span>
                </span>
              </div>

              <div class="flex flex-col border-x border-white/10 px-2">
                <span class="text-[10px] text-gray-400 flex items-center gap-1 font-mono">
                  <svg class="w-3 h-3 text-cyan-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z" />
                    <circle cx="12" cy="9" r="2.5" />
                  </svg>
                  徒步里程
                </span>
                <span class="text-[15px] font-bold text-white font-mono mt-1 truncate">
                  {{ checkinStore.stats.totalDistance }}<span class="text-[9px] text-gray-400 ml-0.5 font-normal">km</span>
                </span>
              </div>

              <div class="flex flex-col pl-1">
                <span class="text-[10px] text-gray-400 flex items-center gap-1 font-mono">
                  <svg class="w-3 h-3 text-amber-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M12 8v13m0-13V3m0 5l-4-4m4 4l4-4M5 21h14" />
                  </svg>
                  解锁勋章
                </span>
                <span class="text-[15px] font-bold text-white font-mono mt-1 truncate">
                  {{ unlockedBadgesCount }}<span class="text-[9px] text-gray-400 ml-0.5 font-normal">/4 枚</span>
                </span>
              </div>
            </div>

            <!-- 4. 打卡纪实与精选实景照片卡片 -->
            <div class="space-y-2.5 pt-1">
              <div class="flex items-center justify-between text-[11px] font-mono text-gray-400">
                <span class="flex items-center gap-1 text-emerald-400 font-semibold tracking-wider">
                  <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
                    <circle cx="8.5" cy="8.5" r="1.5" />
                    <polyline points="21 15 16 10 5 21" />
                  </svg>
                  SUMMIT ARCHIVES · 峰线足迹
                </span>
                <span class="text-gray-400 text-[10px]">{{ featuredMountains.length }} 座选定纪实</span>
              </div>

              <!-- 4.1 用户有打卡且开启照片显示时的实景卡片 -->
              <div v-if="displayMountainsWithPhotos.length > 0" class="space-y-3">
                <div
                  v-for="item in displayMountainsWithPhotos.slice(0, 3)"
                  :key="item.id"
                  class="rounded-2xl border border-white/12 p-3 space-y-2 overflow-hidden shadow-lg"
                  style="background: rgba(28, 31, 41, 0.85);"
                >
                  <!-- 实景照片容器 -->
                  <div class="relative w-full h-44 rounded-xl overflow-hidden bg-black/50 border border-white/10">
                    <img
                      :src="item.photos?.[0] || item.record.photoUrl"
                      :alt="item.name"
                      class="w-full h-full object-cover"
                      crossorigin="anonymous"
                    />
                    <div class="absolute bottom-2 left-2 px-2 py-0.5 rounded-md bg-black/70 backdrop-blur-md border border-white/10 text-[10px] font-mono text-white flex items-center gap-1">
                      <span class="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
                      <span>海拔 {{ item.altitude_m || item.alt }}m</span>
                    </div>
                    <div class="absolute top-2 right-2 px-2 py-0.5 rounded-md bg-black/70 backdrop-blur-md text-[9px] font-mono text-gray-300">
                      {{ formatCheckinDate(item.record.checkedAt) }}
                    </div>
                    <!-- 多图数量角标 -->
                    <div
                      v-if="item.photos?.length > 1"
                      class="absolute top-2 left-2 px-1.5 py-0.5 rounded-md bg-black/70 backdrop-blur-md border border-white/10 text-[9px] font-mono text-emerald-300 flex items-center gap-1"
                    >
                      <svg class="w-2.5 h-2.5" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M4 4h3l2-2h6l2 2h3a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2z" />
                      </svg>
                      <span>{{ item.photos.length }} 张实景</span>
                    </div>
                  </div>

                  <!-- 如果有 2 张或更多照片，展示次要微缩照片行 -->
                  <div v-if="item.photos?.length > 1" class="grid grid-cols-3 gap-1.5 pt-0.5">
                    <div
                      v-for="(subPhoto, sIdx) in item.photos.slice(1, 4)"
                      :key="sIdx"
                      class="h-14 rounded-lg overflow-hidden border border-white/10 bg-black/40"
                    >
                      <img :src="subPhoto" :alt="`${item.name} 实景 ${sIdx + 2}`" class="w-full h-full object-cover" crossorigin="anonymous" />
                    </div>
                  </div>

                  <!-- 山峰名称与心得 -->
                  <div class="space-y-1">
                    <div class="flex items-center justify-between">
                      <span class="text-[14px] font-bold text-white">{{ item.name }}</span>
                      <span class="text-[10px] px-2 py-0.5 rounded-full bg-cyan-400/10 border border-cyan-400/20 text-cyan-300 font-mono">
                        {{ item.difficulty || 'L1' }} 级峰线
                      </span>
                    </div>
                    <p v-if="item.record.note" class="text-[11px] text-gray-300 italic border-l-2 border-emerald-400/60 pl-2 py-0.5 line-clamp-2">
                      “{{ item.record.note }}”
                    </p>
                    <p v-else class="text-[10px] text-gray-400 line-clamp-1">
                      {{ item.county || '成都周边名山' }}
                    </p>
                  </div>
                </div>
              </div>

              <!-- 4.2 若关闭了照片，或者部分名山无照片，展示精细拓扑勋章网格 -->
              <div v-if="displayMountainsWithoutPhotos.length > 0" class="grid grid-cols-2 gap-2">
                <div
                  v-for="item in displayMountainsWithoutPhotos.slice(0, 8)"
                  :key="item.id"
                  class="p-2.5 rounded-xl border border-white/10 flex items-center justify-between space-x-2 shadow-sm"
                  style="background: rgba(28, 31, 41, 0.65);"
                >
                  <div class="truncate">
                    <div class="text-[12px] font-semibold text-white truncate">{{ item.name }}</div>
                    <div class="text-[9px] text-gray-400 font-mono flex items-center gap-1">
                      <span>{{ item.altitude_m || item.alt }}m</span>
                      <span class="text-emerald-400/60">·</span>
                      <span>{{ item.difficulty || 'L1' }}</span>
                    </div>
                  </div>
                  <span class="w-5 h-5 rounded-full bg-emerald-500/20 border border-emerald-400/30 text-emerald-400 flex items-center justify-center shrink-0">
                    <svg class="w-3 h-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                      <polyline points="20 6 9 17 4 12" />
                    </svg>
                  </span>
                </div>
              </div>

              <!-- 4.3 零打卡或未选择任何名山时的探索启程手记 -->
              <div
                v-if="featuredMountains.length === 0"
                class="p-4 rounded-2xl border border-white/10 text-center space-y-2"
                style="background: rgba(28, 31, 41, 0.65);"
              >
                <div class="w-10 h-10 mx-auto rounded-full bg-emerald-400/10 border border-emerald-400/20 flex items-center justify-center text-emerald-400">
                  <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="12" cy="12" r="10" />
                    <polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76" />
                  </svg>
                </div>
                <div class="text-[13px] font-bold text-white">探索者首征集结令</div>
                <p class="text-[11px] text-gray-400 max-w-xs mx-auto leading-relaxed">
                  成都市周边 50 座名山拓扑峰线已就绪。踏出征程，在山脊与云海间点亮属于你的第一枚高山勋章！
                </p>
              </div>
            </div>

            <!-- 5. 底部防伪水印、时间戳与官方数字编号 -->
            <div class="pt-3 border-t border-white/10 space-y-2">
              <div class="flex items-center justify-between text-[9px] font-mono text-gray-400">
                <div class="flex items-center gap-1.5">
                  <span class="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
                  <span class="text-gray-300">防伪序列码: {{ securitySerial }}</span>
                </div>
                <span>{{ currentDateStr }}</span>
              </div>

              <div class="flex items-center justify-between pt-1">
                <div class="flex flex-col">
                  <span class="text-[10px] font-bold text-white tracking-wider">CHENGDU ALPINE EXPLORER</span>
                  <span class="text-[8px] text-gray-400 tracking-wider">暗黑高山拓扑架构 · 官方认证数字档案</span>
                </div>

                <!-- 认证印章微缩 SVG -->
                <div class="w-10 h-10 rounded-full border border-emerald-400/40 p-1 flex items-center justify-center text-emerald-300/80 rotate-12">
                  <svg class="w-full h-full" viewBox="0 0 40 40">
                    <circle cx="20" cy="20" r="18" fill="none" stroke="currentColor" stroke-width="1.2" stroke-dasharray="3,2" />
                    <text x="20" y="16" font-size="5" fill="currentColor" text-anchor="middle" font-family="monospace">ALPINE</text>
                    <text x="20" y="24" font-size="5" fill="currentColor" text-anchor="middle" font-family="monospace">VERIFIED</text>
                  </svg>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 弹窗底部操作按钮组 -->
        <div class="w-full max-w-[390px] pt-4 pb-2 space-y-2.5">
          <button
            @click="handleSavePoster"
            :disabled="isGenerating"
            class="btn-save-poster w-full py-3.5 px-4 rounded-2xl bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 hover:to-teal-400 text-slate-950 font-bold text-[14px] flex items-center justify-center gap-2 shadow-[0_0_20px_rgba(78,222,163,0.4)] active:scale-[0.98] transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <svg v-if="!isGenerating" class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
            </svg>
            <svg v-else class="w-4 h-4 animate-spin" viewBox="0 0 24 24" fill="none">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <span>{{ isGenerating ? '正在渲染视网膜高清海报...' : '📥 一键生成并保存海报到相册' }}</span>
          </button>

          <!-- 提示文本 -->
          <p class="text-center text-[11px] text-gray-400">
            支持一键直接存入系统相册 · 包含防伪认证编码 · 自动适配所选峰线
          </p>
        </div>

        <!-- 生成成功后的图片就绪快捷入口条 -->
        <div
          v-if="generatedImageUrl"
          class="w-full max-w-[390px] mt-2 p-3 rounded-2xl border border-emerald-400/30 bg-surface-container/90 text-center space-y-2 cursor-pointer active:scale-98 transition-transform"
          @click="isPosterReadyModalOpen = true"
        >
          <div class="text-[12px] text-emerald-400 font-semibold flex items-center justify-center gap-1.5">
            <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="20 6 9 17 4 12" />
            </svg>
            <span>海报已就绪！点击展开全屏查看并管理</span>
          </div>
          <div class="h-28 overflow-hidden rounded-xl border border-white/10 relative">
            <img :src="generatedImageUrl" alt="成就海报缩略图" class="w-full h-full object-cover object-top" />
            <div class="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent flex items-end justify-center pb-1 text-[10px] text-gray-300">
              点击全屏放大查看
            </div>
          </div>
        </div>
      </div>
    </Transition>

    <!-- 海报生成成功后专属全屏查看与相册保存弹窗 (最高层级 z-[60]) -->
    <Transition name="fade">
      <div
        v-if="isPosterReadyModalOpen"
        class="fixed inset-0 z-[60] bg-black/95 backdrop-blur-lg flex flex-col justify-between pt-[calc(14px+max(env(safe-area-inset-top,0px),34px))] pb-[calc(14px+max(env(safe-area-inset-bottom,0px),16px))] px-3 sm:px-6 select-none"
        @click.self="isPosterReadyModalOpen = false"
      >
        <!-- 弹窗顶栏 -->
        <div class="w-full max-w-md mx-auto flex items-center justify-between pb-2 text-white">
          <div class="flex items-center gap-2">
            <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            <span class="font-bold text-[15px]">🎉 成就海报已就绪</span>
          </div>
          <button
            @click="isPosterReadyModalOpen = false"
            class="w-8 h-8 rounded-full bg-white/10 hover:bg-white/20 flex items-center justify-center text-white active:scale-95 transition-all"
            aria-label="关闭预览"
          >
            <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <!-- 核心图片展示区 -->
        <div class="relative flex-1 flex flex-col items-center justify-center min-h-0 py-1 overflow-y-auto">
          <div class="max-w-[360px] w-full rounded-2xl overflow-hidden border border-emerald-400/30 shadow-[0_0_30px_rgba(78,222,163,0.25)] bg-black/50">
            <img
              :src="generatedImageUrl"
              alt="Alpine Explorer 成就长图海报"
              class="w-full h-auto block max-h-[60vh] object-contain mx-auto select-auto"
            />
          </div>

          <!-- 保存状态反馈气泡 -->
          <div
            v-if="isNativeApp"
            class="mt-2.5 px-3 py-1.5 rounded-full bg-emerald-500/20 border border-emerald-400/40 text-emerald-300 text-[11px] font-mono flex items-center gap-1.5 shadow-sm"
          >
            <svg class="w-3.5 h-3.5 shrink-0 text-emerald-400" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
            </svg>
            <span>海报已直存手机系统相册！亦可点击下方按钮重复保存或分享</span>
          </div>
          <div
            v-else
            class="mt-2.5 px-3 py-1.5 rounded-full bg-emerald-500/20 border border-emerald-400/40 text-emerald-300 text-[11px] font-mono flex items-center gap-1.5 shadow-sm"
          >
            <svg class="w-3.5 h-3.5 shrink-0 text-emerald-400" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z"/>
            </svg>
            <span>点击下方按钮即可一键保存图片到本地相册或下载</span>
          </div>
        </div>

        <!-- 底部快捷动作栏 (物理按钮一键操作，无需长按) -->
        <div class="w-full max-w-md mx-auto pt-2 space-y-2">
          <div class="grid grid-cols-2 gap-2">
            <button
              @click="saveToGalleryDirectly()"
              class="py-3 px-3 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-500 text-slate-950 font-bold text-[13px] flex items-center justify-center gap-1.5 active:scale-95 transition-all shadow-md"
            >
              <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
              <span>💾 一键保存到相册</span>
            </button>
            <button
              @click="handleSystemShare"
              class="py-3 px-3 rounded-xl bg-surface-container-high/90 hover:bg-surface-container-highest border border-white/10 text-white font-medium text-[12px] flex items-center justify-center gap-1.5 active:scale-95 transition-all"
            >
              <svg class="w-4 h-4 text-cyan-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
              </svg>
              <span>📤 系统分享 / 另存</span>
            </button>
          </div>
          <button
            @click="isPosterReadyModalOpen = false"
            class="w-full py-1.5 text-[12px] text-gray-400 hover:text-white transition-colors text-center"
          >
            返回长图海报
          </button>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, computed, watch } from 'vue';
import { useCheckinStore, derivedNums } from '@/stores/checkinStore.js';
import { useMountainStore } from '@/stores/mountainStore.js';

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  isOpen: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits(['update:modelValue', 'close']);

const visible = computed({
  get() {
    return props.modelValue || props.isOpen;
  },
  set(val) {
    emit('update:modelValue', val);
    if (!val) {
      emit('close');
    }
  }
});

const checkinStore = useCheckinStore();
const mountainStore = useMountainStore();

const posterRef = ref(null);
const isGenerating = ref(false);
const generatedImageUrl = ref('');
const generatedBlob = ref(null);
const isPosterReadyModalOpen = ref(false);

// 定制选项 1：是否包含照片
const includePhotos = ref(true);

// 定制选项 2：勾选导出的山峰 ID 列表
const selectedMountainIds = ref([]);

// 判断是否运行在 Android 原生 Native 环境
const isNativeApp = computed(() => {
  return typeof window !== 'undefined' && Boolean(window.AlpineNative && typeof window.AlpineNative.saveImageToGallery === 'function');
});

const totalMountainsCount = computed(() => {
  return mountainStore.mountains?.length || 50;
});

// 所有打卡名山列表
const allCheckedMountains = computed(() => {
  const ids = checkinStore.checkedIds || [];
  return ids
    .map((id) => {
      const m = mountainStore.getMountainById(id);
      if (!m) return null;
      const dn = derivedNums(m);
      const rec = checkinStore.getCheckinRecord(id) || {};
      const photos = Array.isArray(rec.photos) && rec.photos.length
        ? rec.photos
        : (rec.photoUrl ? [rec.photoUrl] : []);
      return {
        ...m,
        ...dn,
        record: rec,
        photos,
        photoUrl: photos[0] || rec.photoUrl || ''
      };
    })
    .filter(Boolean);
});

// 当弹窗打开时，若尚未初始化所选山峰，默认全选所有打卡山峰
watch(
  () => visible.value,
  (isOpen) => {
    if (isOpen) {
      if (selectedMountainIds.value.length === 0 && checkinStore.checkedIds.length > 0) {
        selectedMountainIds.value = [...checkinStore.checkedIds];
      }
    }
  },
  { immediate: true }
);

function selectAllMountains() {
  selectedMountainIds.value = allCheckedMountains.value.map((m) => m.id);
}

function clearAllMountains() {
  selectedMountainIds.value = [];
}

function toggleMountainSelection(id) {
  const idx = selectedMountainIds.value.indexOf(id);
  if (idx >= 0) {
    selectedMountainIds.value.splice(idx, 1);
  } else {
    selectedMountainIds.value.push(id);
  }
}

// 解锁勋章数量
const unlockedBadgesCount = computed(() => {
  let count = 0;
  if (checkinStore.stats.doneCount >= 1) count++;
  const hasHighAlt = checkinStore.checkedIds.some((id) => {
    const m = mountainStore.getMountainById(id);
    return m && m.altitude_m >= 4000;
  });
  if (hasHighAlt) count++;
  const hasCloud = checkinStore.checkedIds.some((id) => {
    const m = mountainStore.getMountainById(id);
    return m && (m.group === 'A' || m.highlights?.some((h) => h.includes('云海')));
  });
  if (hasCloud) count++;
  if (checkinStore.stats.doneCount >= 5) count++;
  return count;
});

// 用户选定的打卡名山列表（若未选则按全部已打卡）
const featuredMountains = computed(() => {
  const activeIds = selectedMountainIds.value.length > 0
    ? selectedMountainIds.value
    : checkinStore.checkedIds;
  return allCheckedMountains.value.filter((item) => activeIds.includes(item.id));
});

// 根据 includePhotos 和是否有照片筛选
const displayMountainsWithPhotos = computed(() => {
  if (!includePhotos.value) return [];
  return featuredMountains.value.filter((item) => (item.photos && item.photos.length > 0) || Boolean(item.record?.photoUrl));
});

const displayMountainsWithoutPhotos = computed(() => {
  if (!includePhotos.value) {
    // 关闭照片模式时，选中的山峰全部以拓扑勋章卡片展示
    return featuredMountains.value;
  }
  return featuredMountains.value.filter((item) => (!item.photos || item.photos.length === 0) && !item.record?.photoUrl);
});

// 当前日期
const currentDateStr = computed(() => {
  const d = new Date();
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${y}.${m}.${day}`;
});

// 防伪序列码 (根据完成数和时间哈希生成)
const securitySerial = computed(() => {
  const code = (checkinStore.stats.doneCount * 9973 + 104729)
    .toString(16)
    .toUpperCase()
    .slice(-4);
  return `ALP-2026-${code}F8`;
});

function formatCheckinDate(isoStr) {
  if (!isoStr) return '';
  try {
    const d = new Date(isoStr);
    const y = d.getFullYear();
    const m = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');
    return `${y}.${m}.${day} 登顶`;
  } catch (e) {
    return '';
  }
}

function handleClose() {
  visible.value = false;
}

/**
 * 核心保存方法：直接保存到手机系统相册 (如果是在 Android Native App 内)，否则降级到下载
 */
async function saveToGalleryDirectly(dataUrlToSave = null) {
  const dataUrl = dataUrlToSave || generatedImageUrl.value;
  if (!dataUrl) return false;

  const filename = `Alpine-Explorer-Achievement-${new Date().toISOString().slice(0, 10)}.png`;

  // 1. Android Native Bridge 优先：直接调用 MediaStore 写入相册
  if (typeof window !== 'undefined' && window.AlpineNative && typeof window.AlpineNative.saveImageToGallery === 'function') {
    try {
      const ok = window.AlpineNative.saveImageToGallery(dataUrl, filename);
      if (ok) {
        return true;
      }
    } catch (err) {
      console.warn('Native gallery save error:', err);
    }
  }

  // 2. 浏览器环境：调用 handleDirectDownload 触发下载
  handleDirectDownload();
  return true;
}

/**
 * 浏览器直接下载海报文件
 */
function handleDirectDownload() {
  if (!generatedImageUrl.value) return;
  try {
    const filename = `Alpine-Explorer-Achievement-${new Date().toISOString().slice(0, 10)}.png`;
    let url = generatedImageUrl.value;
    if (generatedBlob.value) {
      url = URL.createObjectURL(generatedBlob.value);
    }
    const link = document.createElement('a');
    link.download = filename;
    link.href = url;
    document.body.appendChild(link);
    link.click();
    setTimeout(() => {
      document.body.removeChild(link);
      if (generatedBlob.value) {
        URL.revokeObjectURL(url);
      }
    }, 1000);
  } catch (e) {
    console.warn('Direct download error:', e);
  }
}

/**
 * 调起系统分享面板（支持直接保存到手机系统相册或转发到微信）
 */
async function handleSystemShare() {
  if (!generatedBlob.value) {
    handleDirectDownload();
    return;
  }
  const filename = `Alpine-Explorer-Achievement-${new Date().toISOString().slice(0, 10)}.png`;
  const file = new File([generatedBlob.value], filename, { type: 'image/png' });
  if (navigator.canShare && navigator.canShare({ files: [file] })) {
    try {
      await navigator.share({
        title: '成都周边50座名山巡礼 · 成就海报',
        text: `我在 Alpine Explorer 已征服 ${checkinStore.stats.doneCount} 座名山！`,
        files: [file]
      });
    } catch (e) {
      console.log('Share dismissed:', e);
    }
  } else {
    // 降级使用相册直存
    saveToGalleryDirectly();
  }
}

/**
 * 渲染海报并直接触发保存到系统相册
 */
async function handleSavePoster() {
  if (isGenerating.value) return;
  if (!posterRef.value) return;

  isGenerating.value = true;
  try {
    // 动态按需加载 html2canvas
    const html2canvasModule = await import('html2canvas');
    const html2canvas = html2canvasModule.default || html2canvasModule;

    const canvas = await html2canvas(posterRef.value, {
      scale: 2,
      useCORS: true,
      allowTaint: true,
      backgroundColor: '#090d16',
      logging: false
    });

    const dataUrl = canvas.toDataURL('image/png');
    generatedImageUrl.value = dataUrl;

    const blob = await new Promise((resolve) => canvas.toBlob(resolve, 'image/png'));
    generatedBlob.value = blob;

    // 弹出专属全屏查看与相册保存弹窗
    isPosterReadyModalOpen.value = true;

    // 直接调用保存到系统相册
    await saveToGalleryDirectly(dataUrl);
  } catch (err) {
    console.error('Failed to generate poster:', err);
    alert('海报生成失败，请稍后重试');
  } finally {
    isGenerating.value = false;
  }
}
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.25s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
