<template>
  <div class="plan-view w-full min-h-screen bg-background text-on-surface pb-28 pt-3 px-space-lg max-w-md mx-auto space-y-space-xl select-none font-body-md">
    <!-- ================= TOP APP BAR ================= -->
    <header class="flex justify-between items-center w-full py-1">
      <div class="flex items-center gap-space-sm">
        <router-link
          to="/explore"
          aria-label="返回探索"
          class="w-8 h-8 rounded-full flex items-center justify-center text-on-surface-variant hover:text-primary active:scale-95 transition-all"
        >
          <span class="material-symbols-outlined text-[20px]">arrow_back</span>
        </router-link>
        <div class="flex flex-col">
          <span class="font-headline-md text-[16px] leading-[22px] font-bold tracking-tight text-on-surface">周计划 · 2025</span>
          <span class="font-label-data-sm text-[10px] text-primary tracking-wider uppercase">Weekly Mountain Season</span>
        </div>
      </div>
      <div class="flex items-center gap-1">
        <button
          @click="handleClearPlans"
          class="p-1.5 rounded-full flex items-center justify-center text-on-surface-variant hover:text-error active:scale-95 transition-colors"
          title="清空周计划"
        >
          <span class="material-symbols-outlined text-[19px]">delete_sweep</span>
        </button>
        <button
          @click="showNotification('周计划已自动保存至本地存储')"
          class="p-1.5 rounded-full flex items-center justify-center text-on-surface-variant hover:text-primary active:scale-95 transition-colors"
          title="数据同步状态"
        >
          <span class="material-symbols-outlined text-[19px]">cloud_done</span>
        </button>
      </div>
    </header>

    <!-- ================= SECTION 1: 2025 赛季计划概览 Banner (Bento Glass Card) ================= -->
    <section class="relative rounded-3xl bg-surface-container/70 border border-white/10 p-space-lg backdrop-blur-xl overflow-hidden glow-primary">
      <!-- Ambient radial background glow -->
      <div class="absolute -top-12 -right-12 w-44 h-44 bg-primary/15 rounded-full blur-3xl pointer-events-none"></div>
      <div class="absolute -bottom-10 -left-10 w-36 h-36 bg-secondary/15 rounded-full blur-2xl pointer-events-none"></div>

      <div class="relative z-10 space-y-4">
        <!-- Top Badge & Season Title -->
        <div class="flex items-start justify-between">
          <div>
            <div class="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-primary/10 border border-primary/20 text-primary font-label-data-sm text-[10px] mb-1.5">
              <span class="material-symbols-outlined text-[13px] fill" style="font-variation-settings: 'FILL' 1;">stars</span>
              2025 {{ regionStore.currentRegion.shortName }}山岳远征季
            </div>
            <h2 class="font-headline-lg text-[22px] leading-tight font-bold text-on-surface tracking-tight">
              年度已完成 <span class="text-primary font-label-data-lg text-[28px] font-bold">{{ checkinStore.stats.doneCount }}</span><span class="text-on-surface-variant text-[15px]">/{{ currentRegionMountainsCount }} 座</span>
            </h2>
          </div>

          <!-- Circular Progress Mini Widget -->
          <div class="relative w-14 h-14 flex items-center justify-center shrink-0">
            <svg class="w-14 h-14 transform -rotate-90" viewBox="0 0 48 48">
              <circle cx="24" cy="24" fill="none" r="19" stroke="rgba(255,255,255,0.08)" stroke-width="3.5"></circle>
              <circle
                class="drop-shadow-[0_0_6px_rgba(16,185,129,0.7)] transition-all duration-700 ease-out"
                cx="24"
                cy="24"
                fill="none"
                r="19"
                stroke="#10b981"
                stroke-dasharray="120"
                :stroke-dashoffset="120 - (120 * checkinStore.stats.completionRate) / 100"
                stroke-linecap="round"
                stroke-width="3.5"
              ></circle>
            </svg>
            <div class="absolute flex flex-col items-center">
              <span class="font-label-data-sm text-[11px] font-bold text-primary">{{ checkinStore.stats.completionRate }}%</span>
            </div>
          </div>
        </div>

        <!-- Metric Strip -->
        <div class="grid grid-cols-3 gap-2 p-2.5 rounded-xl bg-surface-container-lowest/60 border border-white/5 backdrop-blur-md">
          <div class="flex flex-col">
            <span class="font-label-data-sm text-[10px] text-on-surface-variant flex items-center gap-0.5">
              <span class="material-symbols-outlined text-[12px] text-primary">altitude</span> 累计爬升
            </span>
            <span class="font-label-data-lg text-[16px] font-bold text-on-surface mt-0.5 truncate">
              +{{ checkinStore.stats.totalAscent.toLocaleString() }}<span class="text-[10px] text-on-surface-variant ml-0.5 font-normal">m</span>
            </span>
          </div>

          <div class="flex flex-col border-x border-white/5 px-2">
            <span class="font-label-data-sm text-[10px] text-on-surface-variant flex items-center gap-0.5">
              <span class="material-symbols-outlined text-[12px] text-secondary">distance</span> 徒步里程
            </span>
            <span class="font-label-data-lg text-[16px] font-bold text-on-surface mt-0.5 truncate">
              {{ checkinStore.stats.totalDistance }}<span class="text-[10px] text-on-surface-variant ml-0.5 font-normal">km</span>
            </span>
          </div>

          <div class="flex flex-col pl-1">
            <span class="font-label-data-sm text-[10px] text-on-surface-variant flex items-center gap-0.5">
              <span class="material-symbols-outlined text-[12px] text-tertiary">calendar_month</span> 排期周数
            </span>
            <span class="font-label-data-lg text-[16px] font-bold text-on-surface mt-0.5 truncate">
              {{ planStore.plans.length }}<span class="text-[10px] text-on-surface-variant ml-0.5 font-normal">周</span>
            </span>
          </div>
        </div>

        <!-- Quick Action Buttons -->
        <div class="grid grid-cols-2 gap-2 pt-1">
          <button
            @click="handleAddNewWeek"
            class="btn-add-week flex items-center justify-center gap-1.5 py-2.5 px-3 rounded-xl bg-gradient-to-r from-primary-container to-secondary text-surface-container-lowest font-body-md text-[13px] font-bold active:scale-95 transition-all shadow-[0_0_18px_rgba(16,185,129,0.35)]"
          >
            <span class="material-symbols-outlined text-[18px]">add</span>
            新建周计划
          </button>
          <button
            @click="scrollToPresets"
            class="flex items-center justify-center gap-1.5 py-2.5 px-3 rounded-xl bg-surface-container-high/60 border border-white/10 text-on-surface font-body-md text-[13px] font-medium hover:border-primary/40 active:scale-95 transition-all"
          >
            <span class="material-symbols-outlined text-[17px] text-secondary">auto_awesome</span>
            套用精选路线
          </button>
        </div>
      </div>
    </section>

    <!-- ================= SECTION 2: 周计划时间轴看板 (Weekly Timeline) ================= -->
    <section class="space-y-space-md plan-timeline">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-2">
          <span class="w-1.5 h-4 rounded-full bg-primary"></span>
          <h3 class="font-headline-md text-[18px] font-bold text-on-surface">时间轴排期看板</h3>
        </div>
        <span class="font-label-data-sm text-[11px] text-primary flex items-center gap-0.5">
          共 {{ planStore.plans.length }} 周计划 <span class="material-symbols-outlined text-[14px]">local_fire_department</span>
        </span>
      </div>

      <!-- Empty State -->
      <div
        v-if="planStore.plans.length === 0"
        class="rounded-2xl bg-surface-container/60 border border-white/10 p-6 backdrop-blur-xl text-center space-y-3"
      >
        <span class="material-symbols-outlined text-[44px] text-outline">calendar_month</span>
        <h4 class="font-headline-md text-[15px] font-bold text-on-surface">当前暂无周计划排期</h4>
        <p class="font-body-sm text-[12px] text-on-surface-variant max-w-xs mx-auto">
          可直接套用下方资深领队精选路线，或在「探索」地图中将心仪山峰加入周计划。
        </p>
        <button
          @click="scrollToPresets"
          class="inline-flex items-center gap-1 px-4 py-2 rounded-xl bg-primary text-on-primary font-body-md text-[12px] font-bold active:scale-95 transition-all shadow-sm"
        >
          <span class="material-symbols-outlined text-[16px]">auto_awesome</span>
          查看精选路线
        </button>
      </div>

      <!-- Timeline Container -->
      <div
        v-else
        class="relative pl-3 space-y-space-lg before:content-[''] before:absolute before:left-[11px] before:top-3 before:bottom-3 before:w-[1.5px] before:bg-gradient-to-b before:from-primary before:via-secondary before:to-outline-variant/40"
      >
        <!-- Cards -->
        <div
          v-for="week in planStore.plans"
          :key="week.week"
          class="timeline-week-card relative pl-6"
        >
          <!-- Timeline Node Indicator -->
          <div
            v-if="isWeekCompleted(week)"
            class="absolute -left-[5px] top-4 w-5 h-5 rounded-full bg-surface-container-lowest border-2 border-primary flex items-center justify-center shadow-[0_0_8px_rgba(16,185,129,0.8)] z-10"
            title="本周已完成"
          >
            <span class="material-symbols-outlined text-[12px] text-primary font-bold">check</span>
          </div>
          <div
            v-else-if="week.week === currentActiveWeekNum"
            class="absolute -left-[5px] top-4 w-5 h-5 rounded-full bg-secondary-container border-2 border-secondary flex items-center justify-center glow-secondary z-10 animate-pulse"
            title="进行中"
          >
            <span class="w-2 h-2 rounded-full bg-on-secondary"></span>
          </div>
          <div
            v-else
            class="absolute -left-[5px] top-4 w-5 h-5 rounded-full bg-surface-container-lowest border-2 border-tertiary flex items-center justify-center glow-tertiary z-10"
            title="预定规划中"
          >
            <span class="w-1.5 h-1.5 rounded-full bg-tertiary"></span>
          </div>

          <!-- Card Body -->
          <div class="rounded-2xl bg-surface-container/60 border border-white/10 p-3.5 backdrop-blur-xl space-y-3">
            <!-- Header -->
            <div class="flex items-center justify-between">
              <span class="font-label-data-sm text-[11px] font-semibold text-on-surface-variant">
                第 {{ week.week }} 周 · {{ getWeekTitle(week) }}
              </span>
              <div class="flex items-center gap-2">
                <span
                  v-if="isWeekCompleted(week)"
                  class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-primary/10 border border-primary/25 text-primary font-label-data-sm text-[10px]"
                >
                  <span class="w-1.5 h-1.5 rounded-full bg-primary"></span> 已完成
                </span>
                <span
                  v-else
                  class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-secondary/15 border border-secondary/30 text-secondary font-label-data-sm text-[10px]"
                >
                  待出征 · 进行中
                </span>
                <button
                  @click="handleDeleteWeek(week.week)"
                  class="btn-delete-week text-on-surface-variant hover:text-error transition-colors p-0.5"
                  title="删除本周计划"
                >
                  <span class="material-symbols-outlined text-[15px]">close</span>
                </button>
              </div>
            </div>

            <!-- Mountains in Week -->
            <div v-if="getWeekMountains(week).length === 0" class="py-3 text-center text-on-surface-variant text-[12px]">
              本周尚未添加目标山峰
            </div>

            <div
              v-for="m in getWeekMountains(week)"
              :key="m.id"
              class="flex gap-3 items-center pt-1"
            >
              <!-- Thumbnail -->
              <div class="w-16 h-16 rounded-xl overflow-hidden shrink-0 relative border border-white/10 bg-surface-container-low">
                <img
                  v-if="m.cover_image || m.id"
                  :src="m.cover_image || `assets/mountains/${m.id}.jpg`"
                  :alt="m.name"
                  class="w-full h-full object-cover"
                  loading="lazy"
                />
                <div v-else class="w-full h-full flex items-center justify-center bg-surface-container-high text-outline">
                  <span class="material-symbols-outlined text-[24px]">terrain</span>
                </div>
                <div class="absolute bottom-0 inset-x-0 bg-surface-container-lowest/80 text-center font-label-data-sm text-[9px] text-on-surface py-0.5">
                  {{ m.altitude_m || derivedNums(m).alt }}m
                </div>
              </div>

              <!-- Main Info -->
              <div class="flex-1 min-w-0">
                <div class="flex items-center justify-between">
                  <h4 class="font-headline-md text-[14px] font-bold text-on-surface truncate">{{ m.name }}</h4>
                  <span class="px-1.5 py-0.5 rounded bg-primary/10 text-primary font-label-data-sm text-[9px] shrink-0">
                    {{ m.difficulty || 'L2' }}
                  </span>
                </div>
                <p class="font-body-sm text-[11px] text-on-surface-variant truncate mt-0.5">
                  {{ m.subtitle || m.tags?.[0] || `${regionStore.currentRegion.name}名山` }}
                </p>
                <div class="flex items-center gap-2 mt-1 text-on-surface-variant font-label-data-sm text-[10px]">
                  <span class="flex items-center gap-0.5 text-primary">
                    <span class="material-symbols-outlined text-[11px]">trending_up</span>
                    +{{ derivedNums(m).asc }}m
                  </span>
                  <span>·</span>
                  <span class="flex items-center gap-0.5 text-secondary">
                    <span class="material-symbols-outlined text-[11px]">directions_car</span>
                    {{ m.drive_hours || m.car_time_h || 2 }}h
                  </span>
                  <span>·</span>
                  <span>{{ derivedNums(m).dist }}km</span>
                </div>
              </div>
            </div>

            <!-- Card Action Footer -->
            <div class="pt-2 border-t border-white/5 flex items-center justify-between text-on-surface-variant font-label-data-sm text-[10px]">
              <div
                v-for="m in getWeekMountains(week)"
                :key="'act-' + m.id"
                class="w-full flex items-center justify-between gap-2"
              >
                <button
                  @click="checkinStore.toggleCheckin(m.id)"
                  class="flex items-center gap-1.5 py-1 px-2.5 rounded-lg text-[11px] transition-all"
                  :class="checkinStore.isDone(m.id)
                    ? 'bg-primary/20 text-primary border border-primary/40 font-semibold'
                    : 'bg-surface-container-high/80 text-on-surface hover:text-primary border border-white/10'"
                >
                  <span class="material-symbols-outlined text-[14px]" :class="{ fill: checkinStore.isDone(m.id) }">
                    {{ checkinStore.isDone(m.id) ? 'verified' : 'check_circle' }}
                  </span>
                  <span>{{ checkinStore.isDone(m.id) ? '已打卡' : '打卡确认' }}</span>
                </button>

                <button
                  @click="planStore.removeFromPlan(m.id, week.week)"
                  class="text-on-surface-variant hover:text-error p-1 text-[11px] flex items-center gap-0.5"
                  title="从周计划移除"
                >
                  <span class="material-symbols-outlined text-[14px]">remove_circle_outline</span>
                  <span>移除</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ================= SECTION 3: 精选推荐路线 (Recommended Presets) ================= -->
    <section id="official-presets" class="space-y-space-md official-presets">
      <div class="flex items-center justify-between">
        <div>
          <div class="flex items-center gap-2">
            <span class="w-1.5 h-4 rounded-full bg-secondary"></span>
            <h3 class="font-headline-md text-[18px] font-bold text-on-surface">精选推荐周计划</h3>
          </div>
          <p class="font-body-sm text-[11px] text-on-surface-variant mt-0.5">资深领队调优难度梯度，循序渐进</p>
        </div>
        <span class="font-label-data-sm text-[11px] text-primary flex items-center gap-0.5">
          共 4 套方案
        </span>
      </div>

      <!-- Presets Stack -->
      <div class="space-y-3">
        <div
          v-for="preset in presetsWithMeta"
          :key="preset.id"
          class="preset-card p-3.5 rounded-2xl bg-surface-container/60 border border-white/10 backdrop-blur-xl flex items-center justify-between gap-3 hover:border-primary/30 transition-all"
        >
          <div class="space-y-1.5 flex-1 min-w-0">
            <div class="flex items-center gap-2">
              <h4 class="font-headline-md text-[14px] font-bold text-on-surface truncate">{{ preset.name }}</h4>
              <span class="px-2 py-0.5 rounded-full bg-primary/10 border border-primary/20 text-primary font-label-data-sm text-[9px] shrink-0">
                {{ preset.weeks.length }} 周推荐
              </span>
            </div>
            <p class="font-body-sm text-[11px] text-on-surface-variant line-clamp-1">
              {{ preset.desc }}
            </p>
            <div class="flex items-center gap-1 text-[10px] font-label-data-sm text-outline truncate">
              <span>包含: {{ preset.mountainNames }}</span>
            </div>
          </div>

          <div class="flex flex-col gap-1.5 shrink-0">
            <button
              @click="applyPreset(preset.id, 'replace')"
              class="btn-apply-preset px-3 py-1.5 rounded-xl bg-primary text-on-primary font-body-md text-[12px] font-bold active:scale-95 transition-all shadow-sm text-center"
            >
              套用
            </button>
            <button
              @click="applyPreset(preset.id, 'append')"
              class="px-2.5 py-1 rounded-xl bg-surface-container-high/80 border border-white/10 text-on-surface hover:text-primary font-body-md text-[10px] font-medium active:scale-95 transition-all text-center"
              title="追加到现有周计划末尾"
            >
              追加
            </button>
          </div>
        </div>
      </div>
    </section>

    <!-- Toast Feedback -->
    <div
      v-if="toastMessage"
      class="fixed top-16 left-1/2 -translate-x-1/2 z-50 px-4 py-2 rounded-xl frost-glass-highlight text-primary text-body-sm font-semibold shadow-2xl flex items-center gap-2 transition-all duration-300"
    >
      <span class="material-symbols-outlined text-[18px]">info</span>
      <span>{{ toastMessage }}</span>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { usePlanStore, REC_PRESETS } from '@/stores/planStore.js';
import { useCheckinStore, derivedNums } from '@/stores/checkinStore.js';
import { useMountainStore } from '@/stores/mountainStore.js';
import { useRegionStore } from '@/stores/regionStore.js';

const planStore = usePlanStore();
const checkinStore = useCheckinStore();
const mountainStore = useMountainStore();
const regionStore = useRegionStore();

const currentRegionMountainsCount = computed(() => {
  const regId = regionStore.currentRegionId;
  return mountainStore.mountains.filter((m) => !m.region_id || m.region_id === regId).length;
});

const toastMessage = ref('');
let toastTimer = null;

function showNotification(msg) {
  toastMessage.value = msg;
  if (toastTimer) clearTimeout(toastTimer);
  toastTimer = setTimeout(() => {
    toastMessage.value = '';
  }, 2200);
}

// 路线精选强化展示：显示包含的山峰名称与别名匹配
const presetsWithMeta = computed(() => {
  return REC_PRESETS.map((p) => {
    const names = p.weeks.map((mid) => {
      const m = mountainStore.getMountainById(mid);
      return m ? m.name : mid;
    }).join(' / ');

    // 增加别名属性，确保包含「川西日出云海线」
    let displayName = p.name;
    if (p.id === 'seacloud4') {
      displayName = '川西日出云海线 (云海观景台 · 4 连)';
    }

    return {
      ...p,
      name: displayName,
      mountainNames: names
    };
  });
});

function getWeekMountains(week) {
  const items = week.items || week.mountainIds || [];
  return items
    .map((id) => mountainStore.getMountainById(id))
    .filter(Boolean);
}

function getWeekTitle(week) {
  const mountains = getWeekMountains(week);
  if (mountains.length > 0) {
    return mountains[0].name;
  }
  return week.t || `第${week.week}周`;
}

function isWeekCompleted(week) {
  const mountains = getWeekMountains(week);
  if (mountains.length === 0) return false;
  return mountains.every((m) => checkinStore.isDone(m.id));
}

const currentActiveWeekNum = computed(() => {
  for (const w of planStore.plans) {
    if (!isWeekCompleted(w)) return w.week;
  }
  return planStore.plans.length > 0 ? planStore.plans[0].week : 1;
});

function handleAddNewWeek() {
  planStore.addNewWeek();
  showNotification('已新增排期周计划');
}

function handleDeleteWeek(weekNum) {
  planStore.removeWeek(weekNum);
  showNotification(`已删除第 ${weekNum} 周计划`);
}

function handleClearPlans() {
  if (confirm('确认清空所有周计划排期吗？')) {
    planStore.clearPlans();
    showNotification('周计划已清空');
  }
}

function applyPreset(presetId, mode = 'replace') {
  const ok = planStore.applyPreset(presetId, mode);
  if (ok) {
    showNotification(mode === 'append' ? '已成功追加路线方案' : '已成功套用精选推荐周计划！');
  }
}

function scrollToPresets() {
  const el = document.getElementById('official-presets');
  if (el) {
    el.scrollIntoView({ behavior: 'smooth' });
  }
}
</script>

<style scoped>
.frost-glass-highlight {
  background: rgba(28, 31, 41, 0.92);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(78, 222, 163, 0.3);
}
</style>
