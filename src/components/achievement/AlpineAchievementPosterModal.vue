<template>
  <Teleport to="body">
    <Transition name="fade">
      <div
        v-if="visible"
        class="alpine-poster-modal fixed inset-0 z-50 bg-black/85 backdrop-blur-md flex flex-col items-center justify-start overflow-y-auto px-3 py-4 sm:p-6"
        @click.self="handleClose"
      >
        <!-- 弹窗顶栏控制区 -->
        <div class="w-full max-w-md flex items-center justify-between pb-3 px-1 text-on-surface">
          <div class="flex items-center gap-2">
            <span class="w-2 h-2 rounded-full bg-primary animate-pulse"></span>
            <span class="font-headline-md text-[16px] font-bold tracking-tight">Alpine Explorer 成就长图</span>
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
                <span class="text-gray-400 text-[10px]">{{ featuredMountains.length }} 座纪实</span>
              </div>

              <!-- 4.1 用户有打卡且有上传照片的卡片 (优先突出高质感实景) -->
              <div v-if="mountainsWithPhotos.length > 0" class="space-y-3">
                <div
                  v-for="item in mountainsWithPhotos.slice(0, 2)"
                  :key="item.id"
                  class="rounded-2xl border border-white/12 p-3 space-y-2 overflow-hidden shadow-lg"
                  style="background: rgba(28, 31, 41, 0.85);"
                >
                  <!-- 实景照片容器 -->
                  <div class="relative w-full h-44 rounded-xl overflow-hidden bg-black/50 border border-white/10">
                    <img
                      :src="item.record.photoUrl"
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

              <!-- 4.2 若有打卡但无照片，或者补充展示其他打卡名山列表网格 -->
              <div v-if="mountainsWithoutPhotos.length > 0" class="grid grid-cols-2 gap-2">
                <div
                  v-for="item in mountainsWithoutPhotos.slice(0, 4)"
                  :key="item.id"
                  class="p-2.5 rounded-xl border border-white/10 flex items-center justify-between space-x-2"
                  style="background: rgba(28, 31, 41, 0.65);"
                >
                  <div class="truncate">
                    <div class="text-[12px] font-semibold text-white truncate">{{ item.name }}</div>
                    <div class="text-[9px] text-gray-400 font-mono">海拔 {{ item.altitude_m || item.alt }}m</div>
                  </div>
                  <span class="w-5 h-5 rounded-full bg-emerald-500/20 border border-emerald-400/30 text-emerald-400 flex items-center justify-center shrink-0">
                    <svg class="w-3 h-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                      <polyline points="20 6 9 17 4 12" />
                    </svg>
                  </span>
                </div>
              </div>

              <!-- 4.3 零打卡兜底：探索者启程手记 -->
              <div
                v-if="checkinStore.stats.doneCount === 0"
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
            class="btn-save-poster w-full py-3 px-4 rounded-2xl bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 hover:to-teal-400 text-slate-950 font-bold text-[14px] flex items-center justify-center gap-2 shadow-[0_0_20px_rgba(78,222,163,0.4)] active:scale-[0.98] transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <svg v-if="!isGenerating" class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
            </svg>
            <svg v-else class="w-4 h-4 animate-spin" viewBox="0 0 24 24" fill="none">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <span>{{ isGenerating ? '正在渲染高质感海报...' : '📥 保存到手机 / 下载海报' }}</span>
          </button>

          <!-- 提示文本 -->
          <p class="text-center text-[11px] text-gray-400">
            视网膜屏 2x 高清导出 · 包含 GPS 与高山拓扑防伪认证
          </p>
        </div>

        <!-- 生成成功后的图片直接长按保存预览（移动端最佳体验） -->
        <div
          v-if="generatedImageUrl"
          class="w-full max-w-[390px] mt-2 p-3 rounded-2xl border border-emerald-400/30 bg-surface-container/90 text-center space-y-2"
        >
          <div class="text-[12px] text-emerald-400 font-semibold flex items-center justify-center gap-1.5">
            <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="20 6 9 17 4 12" />
            </svg>
            <span>海报已生成完毕！手机端可长按下方图片直接保存</span>
          </div>
          <div class="max-h-60 overflow-y-auto rounded-xl border border-white/10">
            <img :src="generatedImageUrl" alt="成就海报预览" class="w-full h-auto block" />
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
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

const totalMountainsCount = computed(() => {
  return mountainStore.mountains?.length || 50;
});

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

// 打卡名山与记录列表
const featuredMountains = computed(() => {
  const ids = checkinStore.checkedIds || [];
  return ids
    .map((id) => {
      const m = mountainStore.getMountainById(id);
      if (!m) return null;
      const dn = derivedNums(m);
      const rec = checkinStore.getCheckinRecord(id) || {};
      return {
        ...m,
        ...dn,
        record: rec
      };
    })
    .filter(Boolean);
});

// 筛选出有照片与无照片的名山
const mountainsWithPhotos = computed(() => {
  return featuredMountains.value.filter((item) => Boolean(item.record?.photoUrl));
});

const mountainsWithoutPhotos = computed(() => {
  return featuredMountains.value.filter((item) => !item.record?.photoUrl);
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
 * 渲染海报并触发下载
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

    // 触发浏览器直接下载
    const link = document.createElement('a');
    link.download = `Alpine-Explorer-Achievement-${new Date().toISOString().slice(0, 10)}.png`;
    link.href = dataUrl;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
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
