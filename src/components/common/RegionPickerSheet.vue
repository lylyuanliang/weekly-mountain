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
        class="w-full max-w-md bg-surface-container-low border border-outline-variant/40 rounded-t-3xl sm:rounded-2xl shadow-2xl p-4 sm:p-5 flex flex-col gap-3.5 max-h-[85vh] overflow-y-auto no-scrollbar overscroll-contain"
        style="overscroll-behavior: contain; -webkit-overflow-scrolling: touch;"
        @click.stop
      >
        <!-- Header -->
        <div class="flex items-center justify-between border-b border-outline-variant/20 pb-2.5">
          <div class="flex items-center gap-2">
            <span class="material-symbols-outlined text-primary text-[20px]">explore</span>
            <h3 class="text-base font-bold text-on-surface">切换徒步区域</h3>
          </div>
          <button
            @click="close"
            class="w-7 h-7 rounded-full frost-glass flex items-center justify-center text-on-surface-variant hover:text-on-surface active:scale-95 transition-all"
            aria-label="关闭"
          >
            <span class="material-symbols-outlined text-[16px]">close</span>
          </button>
        </div>

        <!-- Section: Active Regions (已上线开放城市) -->
        <div class="flex flex-col gap-2">
          <div class="flex items-center justify-between text-[11px] text-on-surface-variant px-1 font-medium">
            <span>已收录开放区域</span>
            <span class="text-primary font-semibold">{{ isNative ? '离线可用' : '100% 在线即用' }}</span>
          </div>

          <div
            v-for="reg in regionStore.activeRegions"
            :key="reg.id"
            @click="handleRegionClick(reg)"
            class="p-3 rounded-2xl border transition-all cursor-pointer flex items-center justify-between gap-3"
            :class="reg.id === regionStore.currentRegionId
              ? 'bg-primary/10 border-primary glow-primary shadow-sm ring-1 ring-primary/30'
              : 'frost-glass border-outline-variant/25 hover:border-outline-variant/50'"
          >
            <!-- Left: Info -->
            <div class="flex items-center gap-2.5 min-w-0 flex-1">
              <div
                class="w-9 h-9 rounded-xl flex items-center justify-center text-[18px] shrink-0"
                :class="reg.id === regionStore.currentRegionId ? 'bg-primary/20 text-primary' : 'bg-surface-container text-on-surface-variant'"
              >
                🏔️
              </div>
              <div class="flex flex-col min-w-0">
                <div class="flex items-center gap-1.5">
                  <span class="text-sm font-bold text-on-surface truncate">{{ reg.name }}</span>
                  <span class="px-1.5 py-0.2 text-[9px] bg-white/10 text-on-surface-variant rounded font-semibold shrink-0">
                    {{ reg.mountainsCount }} 座名山
                  </span>
                </div>
                <span class="text-[11px] text-on-surface-variant/80 truncate mt-0.5">
                  {{ reg.province }} · {{ reg.driveCenter }}中心辐射
                </span>
              </div>
            </div>

            <!-- Right: Action / Status -->
            <div class="flex items-center gap-2 shrink-0">
              <!-- Web Mode -->
              <template v-if="!isNative">
                <span
                  v-if="reg.id === regionStore.currentRegionId"
                  class="px-2 py-0.5 text-[11px] font-semibold text-primary bg-primary/15 border border-primary/30 rounded-lg flex items-center gap-1"
                >
                  <span class="material-symbols-outlined text-[14px]">check</span>
                  当前所在
                </span>
                <span v-else class="text-[11px] text-on-surface-variant font-medium">点击切换</span>
              </template>

              <!-- Native Mode -->
              <template v-else>
                <!-- Downloading State -->
                <span
                  v-if="isDownloading(reg.id)"
                  class="px-2 py-0.5 text-[10px] font-semibold bg-secondary/15 text-secondary border border-secondary/25 rounded-lg flex items-center gap-1"
                >
                  <span class="material-symbols-outlined text-[13px] animate-spin">sync</span>
                  {{ getProgress(reg.id) }}%
                </span>

                <!-- Already Ready -->
                <template v-else-if="isRegionReady(reg.id)">
                  <div class="flex items-center gap-1.5">
                    <!-- + 补全画册快捷入口 (仅基础版且未下载画册时显示) -->
                    <button
                      v-if="!isGalleryReady(reg.id) && reg.packInfo?.galleryPack"
                      @click.stop="handleDownloadGallery(reg)"
                      class="px-1.5 py-0.5 text-[10px] bg-secondary/15 hover:bg-secondary/25 text-secondary border border-secondary/30 rounded-md font-semibold flex items-center gap-0.5 active:scale-95 transition-all"
                      title="增量补全高清实拍图集 (约 15.8MB)"
                    >
                      <span class="material-symbols-outlined text-[11px]">add_photo_alternate</span>
                      <span>+ 画册</span>
                    </button>

                    <!-- 当前选中状态 -->
                    <span
                      v-if="reg.id === regionStore.currentRegionId"
                      class="px-2 py-0.5 text-[11px] font-semibold text-primary bg-primary/15 border border-primary/30 rounded-lg flex items-center gap-1"
                    >
                      <span class="material-symbols-outlined text-[14px]">check</span>
                      当前所在
                    </span>
                    <!-- 未选中：显示切换提示 -->
                    <span
                      v-else
                      class="px-2 py-0.5 text-[11px] font-semibold text-on-surface-variant bg-surface-container rounded-lg"
                    >
                      点击切换
                    </span>
                  </div>
                </template>

                <!-- Not Installed: Download Button -->
                <template v-else>
                  <button
                    @click.stop="handleDownloadClick(reg)"
                    class="px-2.5 py-1 text-[11px] font-bold bg-primary text-on-primary rounded-xl flex items-center gap-1 shadow-sm active:scale-95 transition-all"
                  >
                    <span class="material-symbols-outlined text-[13px]">cloud_download</span>
                    <span>下载离线包</span>
                  </button>
                </template>
              </template>
            </div>
          </div>
        </div>

        <!-- Section: Planned Regions (轻量紧凑网格，杜绝大卡片堆叠造成的视觉疲劳) -->
        <div class="flex flex-col gap-2 pt-1 border-t border-outline-variant/15">
          <div class="flex items-center justify-between text-[11px] text-on-surface-variant px-1 font-medium">
            <span>路线勘测规划中</span>
            <span class="text-secondary text-[10px]">陆续上线</span>
          </div>

          <div class="grid grid-cols-2 sm:grid-cols-3 gap-2">
            <div
              v-for="reg in regionStore.plannedRegions"
              :key="reg.id"
              @click="handlePlannedClick(reg)"
              class="px-2.5 py-2 rounded-xl frost-glass border border-outline-variant/20 hover:border-outline-variant/40 transition-all cursor-pointer flex items-center gap-2 group active:scale-95"
            >
              <span class="text-[14px] opacity-70 group-hover:scale-110 transition-transform">🧭</span>
              <div class="flex flex-col min-w-0">
                <span class="text-xs font-semibold text-on-surface truncate group-hover:text-secondary transition-colors">
                  {{ reg.name }}
                </span>
                <span class="text-[9px] text-on-surface-variant/70">
                  {{ reg.badge }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Footer Hint -->
        <div class="text-[10px] text-on-surface-variant/50 text-center py-0.5">
          💡 存储空间与画册管理可在「我的 ➔ 离线地域资源管理」中随时调配
        </div>
      </div>
    </div>

    <!-- 离线包多规格（基础包 vs 完整画册包）选择弹窗 -->
    <PackSpecSelectModal
      v-model="showSpecModal"
      :region="pendingDownloadRegion"
      @confirm="handleConfirmSpec"
    />
  </Teleport>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useRegionStore } from '@/stores/regionStore.js';
import { useScrollLock } from '@/composables/useScrollLock.js';
import { isNativeApp } from '@/utils/platform.js';
import PackSpecSelectModal from './PackSpecSelectModal.vue';

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits(['update:modelValue', 'region-change', 'toast']);

const regionStore = useRegionStore();
const isNative = computed(() => isNativeApp());

// 规格选择弹窗控制
const showSpecModal = ref(false);
const pendingDownloadRegion = ref(null);

// 彻底杜绝底层页面背景滚动穿透
useScrollLock(() => props.modelValue);

function close() {
  emit('update:modelValue', false);
}

function isRegionReady(regionId) {
  const reg = regionStore.regions.find((r) => r.id === regionId);
  if (reg?.packInfo?.isDefaultInstalled) return true;
  return regionStore.isPackInstalled(regionId);
}

function isGalleryReady(regionId) {
  const reg = regionStore.regions.find((r) => r.id === regionId);
  if (reg?.packInfo?.isDefaultInstalled) return true;
  return regionStore.isGalleryInstalled(regionId);
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

  // 未安装：弹出规格选择弹窗
  handleDownloadClick(reg);
}

// 唤起离线包规格选择弹窗
function handleDownloadClick(reg) {
  if (isDownloading(reg.id)) return;
  pendingDownloadRegion.value = reg;
  showSpecModal.value = true;
}

// 确认规格并开始下载
async function handleConfirmSpec({ withGallery }) {
  const reg = pendingDownloadRegion.value;
  if (!reg) return;
  try {
    const specName = withGallery ? '完整风光包 (含实拍画册)' : '极速基础包';
    emit('toast', `开始下载【${reg.name}】${specName}...`);
    await regionStore.downloadRegionPack(reg.id, { withGallery });
    emit('toast', `【${reg.name}】${specName}已下载就绪！`);
  } catch (err) {
    emit('toast', `下载失败: ${err.message || '网络连接超时'}`);
  }
}

// 增量补全画册
async function handleDownloadGallery(reg) {
  if (isDownloading(reg.id)) return;
  try {
    emit('toast', `正在增量补全【${reg.name}】高清风光画册包...`);
    await regionStore.downloadRegionGallery(reg.id);
    emit('toast', `【${reg.name}】高清风光画册已补全就绪！`);
  } catch (err) {
    emit('toast', `画册补全失败: ${err.message || '网络连接超时'}`);
  }
}

function handlePlannedClick(reg) {
  emit('toast', `【${reg.name}】正在实地勘测与整理 GPS 路线数据，敬请期待！`);
}
</script>
