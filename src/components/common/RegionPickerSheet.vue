<template>
  <Teleport to="body">
    <!-- Backdrop Overlay -->
    <div
      v-if="modelValue"
      class="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm transition-opacity duration-300 flex items-end sm:items-center justify-center p-0 sm:p-4 modal-backdrop-scroll-contain select-none"
      @click="close"
      @touchmove.self.prevent
    >
      <!-- Sheet Modal Container -->
      <div
        class="w-full max-w-md bg-surface-container-low border border-outline-variant/40 rounded-t-3xl sm:rounded-2xl shadow-2xl p-5 flex flex-col gap-4 max-h-[85vh] overflow-y-auto no-scrollbar overscroll-contain"
        style="overscroll-behavior: contain; -webkit-overflow-scrolling: touch;"
        @click.stop
      >
        <!-- Header -->
        <div class="flex items-center justify-between border-b border-outline-variant/20 pb-3">
          <div class="flex items-center gap-2">
            <span class="material-symbols-outlined text-primary text-[22px]">location_on</span>
            <h3 class="text-title-md font-bold text-on-surface">选择徒步省市与区域</h3>
          </div>
          <button
            @click="close"
            class="w-8 h-8 rounded-full frost-glass flex items-center justify-center text-on-surface-variant hover:text-on-surface active:scale-95"
            aria-label="关闭"
          >
            <span class="material-symbols-outlined text-[18px]">close</span>
          </button>
        </div>

        <!-- Section: Active Regions (已上线城市) -->
        <div class="flex flex-col gap-2">
          <div class="flex items-center justify-between text-label-data-sm text-on-surface-variant px-1 font-semibold">
            <span>已收录开放区域</span>
            <span class="text-primary font-bold">{{ isNative ? '离线可用' : '100% 在线即用' }}</span>
          </div>

          <div
            v-for="reg in regionStore.activeRegions"
            :key="reg.id"
            @click="handleRegionClick(reg)"
            class="p-3.5 rounded-xl border transition-all cursor-pointer flex flex-col gap-2"
            :class="reg.id === regionStore.currentRegionId
              ? 'bg-surface-container-high border-primary glow-primary shadow-lg'
              : 'frost-glass border-outline-variant/30 hover:border-outline-variant/60'"
          >
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-3 min-w-0">
                <div
                  class="w-10 h-10 rounded-xl flex items-center justify-center text-[18px] shrink-0"
                  :class="reg.id === regionStore.currentRegionId ? 'bg-primary/20 text-primary' : 'bg-surface-container text-on-surface-variant'"
                >
                  🏔️
                </div>
                <div class="flex flex-col min-w-0">
                  <div class="flex items-center gap-2">
                    <span class="text-body-md font-bold text-on-surface truncate">{{ reg.name }}</span>
                    <span class="px-1.5 py-0.5 text-[10px] font-label-data-sm bg-primary/20 text-primary rounded font-semibold shrink-0">
                      {{ reg.badge }}
                    </span>
                  </div>
                  <span class="text-[12px] text-on-surface-variant line-clamp-1 mt-0.5">
                    {{ reg.description }}
                  </span>
                </div>
              </div>

              <!-- Status Badge / Action Right Column -->
              <div class="flex items-center gap-1.5 shrink-0 ml-2">
                <!-- Web Mode: 在线即用 -->
                <template v-if="!isNative">
                  <span class="px-2 py-0.5 text-[10px] font-label-data-sm bg-primary/10 text-primary border border-primary/20 rounded font-semibold flex items-center gap-1">
                    <span class="w-1.5 h-1.5 rounded-full bg-primary animate-pulse"></span>
                    在线即用
                  </span>
                  <span
                    v-if="reg.id === regionStore.currentRegionId"
                    class="material-symbols-outlined text-primary text-[20px] flex-shrink-0"
                  >
                    check_circle
                  </span>
                </template>

                <!-- Native Mode -->
                <template v-else>
                  <!-- Downloading State -->
                  <span
                    v-if="isDownloading(reg.id)"
                    class="px-2 py-0.5 text-[10px] font-label-data-sm bg-secondary/15 text-secondary border border-secondary/25 rounded font-semibold flex items-center gap-1"
                  >
                    <span class="material-symbols-outlined text-[13px] animate-spin">sync</span>
                    下载中 {{ getProgress(reg.id) }}%
                  </span>

                  <!-- Installed / Baseline Ready -->
                  <template v-else-if="isRegionReady(reg.id)">
                    <span class="px-2 py-0.5 text-[10px] font-label-data-sm bg-primary/10 text-primary border border-primary/20 rounded font-semibold flex items-center gap-1">
                      <span class="material-symbols-outlined text-[13px]">cloud_done</span>
                      已就绪
                    </span>
                    <span
                      v-if="reg.id === regionStore.currentRegionId"
                      class="material-symbols-outlined text-primary text-[20px] flex-shrink-0"
                    >
                      check_circle
                    </span>
                  </template>

                  <!-- Not Installed: Download Button -->
                  <template v-else>
                    <button
                      @click.stop="handleDownloadClick(reg)"
                      class="btn-download-pack px-2.5 py-1 text-[11px] font-label-data-sm bg-primary text-on-primary rounded-lg font-semibold flex items-center gap-1 shadow-sm active:scale-95 transition-all"
                    >
                      <span class="material-symbols-outlined text-[14px]">cloud_download</span>
                      <span>下载离线包 ({{ formatPackSize(reg.packInfo?.sizeBytes) }})</span>
                    </button>
                  </template>
                </template>
              </div>
            </div>

            <!-- Native Downloading Progress Bar -->
            <div v-if="isNative && isDownloading(reg.id)" class="w-full pt-1">
              <div class="w-full bg-surface-container rounded-full h-1.5 overflow-hidden">
                <div
                  class="bg-primary h-full transition-all duration-200"
                  :style="{ width: `${getProgress(reg.id)}%` }"
                ></div>
              </div>
            </div>
          </div>
        </div>

        <!-- Section: Planned Regions (筹备与勘测中) -->
        <div class="flex flex-col gap-2 pt-2">
          <div class="flex items-center justify-between text-label-data-sm text-on-surface-variant px-1 font-semibold">
            <span>筹备规划中的省市周边</span>
            <span class="text-secondary text-[11px]">敬请期待</span>
          </div>

          <div class="grid grid-cols-1 gap-2">
            <div
              v-for="reg in regionStore.plannedRegions"
              :key="reg.id"
              @click="handlePlannedClick(reg)"
              class="p-3 rounded-xl frost-glass border border-outline-variant/20 hover:border-outline-variant/40 transition-all cursor-pointer flex items-center justify-between group"
            >
              <div class="flex items-center gap-2.5">
                <div class="w-8 h-8 rounded-lg bg-surface-container flex items-center justify-center text-[14px] opacity-75">
                  🧭
                </div>
                <div class="flex flex-col">
                  <div class="flex items-center gap-2">
                    <span class="text-body-sm font-semibold text-on-surface group-hover:text-secondary transition-colors">
                      {{ reg.name }}
                    </span>
                    <span class="px-1.5 py-0.2 text-[9px] font-label-data-sm bg-secondary/15 text-secondary rounded">
                      {{ reg.badge }}
                    </span>
                  </div>
                  <span class="text-[11px] text-on-surface-variant/80 line-clamp-1">
                    {{ reg.description }}
                  </span>
                </div>
              </div>

              <span class="material-symbols-outlined text-outline text-[18px] group-hover:text-secondary transition-colors">
                chevron_right
              </span>
            </div>
          </div>
        </div>

        <!-- Footer Tip -->
        <div class="text-[11px] text-outline text-center py-1 border-t border-outline-variant/20 mt-1">
          💡 后续将陆续上线秦岭、滇中、京郊等周边山峰与 GPS 路线
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { computed } from 'vue';
import { useRegionStore } from '@/stores/regionStore.js';
import { useScrollLock } from '@/composables/useScrollLock.js';
import { isNativeApp } from '@/utils/platform.js';

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits(['update:modelValue', 'region-change', 'toast']);

const regionStore = useRegionStore();
const isNative = computed(() => isNativeApp());

// 彻底杜绝底层页面背景滚动穿透
useScrollLock(() => props.modelValue);

function close() {
  emit('update:modelValue', false);
}

function formatPackSize(bytes) {
  if (!bytes) return '';
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `约 ${Math.round(bytes / 1000)}KB`;
  return `约 ${(bytes / (1024 * 1024)).toFixed(1)}MB`;
}

function isRegionReady(regionId) {
  const reg = regionStore.regions.find((r) => r.id === regionId);
  if (reg?.packInfo?.isDefaultInstalled) return true;
  return regionStore.isPackInstalled(regionId);
}

function isDownloading(regionId) {
  const pct = regionStore.downloadProgress[regionId];
  return typeof pct === 'number' && pct >= 0 && pct < 100;
}

function getProgress(regionId) {
  return regionStore.downloadProgress[regionId] ?? 0;
}

async function selectRegion(reg) {
  await regionStore.setRegion(reg.id);
  emit('region-change', reg);
  close();
}

async function handleRegionClick(reg) {
  // Web 模式：全量在线即用，直接切换
  if (!isNative.value) {
    await selectRegion(reg);
    return;
  }

  // 原生移动模式：
  if (isDownloading(reg.id)) {
    emit('toast', `【${reg.name}】离线包正在下载中 (${getProgress(reg.id)}%)，请稍候...`);
    return;
  }

  if (isRegionReady(reg.id)) {
    await selectRegion(reg);
    return;
  }

  // 未安装：触发下载
  await handleDownloadClick(reg);
}

async function handleDownloadClick(reg) {
  if (isDownloading(reg.id)) return;
  try {
    emit('toast', `开始下载【${reg.name}】离线资源包...`);
    await regionStore.downloadRegionPack(reg.id);
    emit('toast', `【${reg.name}】离线资源包已下载就绪！`);
  } catch (err) {
    emit('toast', `下载失败: ${err.message || '网络连接超时'}`);
  }
}

function handlePlannedClick(reg) {
  emit('toast', `【${reg.name}】正在实地勘测与整理 GPS 路线数据，敬请期待！`);
}
</script>