<template>
  <Teleport to="body">
    <Transition name="fade">
      <div
        v-if="modelValue"
        class="fixed inset-0 z-[1060] flex items-end sm:items-center justify-center p-0 sm:p-4 bg-black/80 backdrop-blur-md modal-backdrop-scroll-contain select-none"
        @click.self="close"
        @touchmove.self.prevent
      >
        <div
          class="w-full max-w-lg rounded-t-3xl sm:rounded-3xl bg-surface-container-low border border-outline-variant/30 shadow-2xl overflow-hidden flex flex-col text-on-surface animate-modal-in max-h-[90vh] sm:max-h-[85vh]"
          role="dialog"
          aria-modal="true"
        >
          <!-- Header -->
          <div class="relative p-4 sm:p-5 pb-3 bg-gradient-to-b from-primary/15 via-surface-container/60 to-transparent border-b border-outline-variant/20 flex items-start justify-between">
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 rounded-2xl flex items-center justify-center bg-primary/20 border border-primary/30 text-primary flex-shrink-0">
                <span class="material-symbols-outlined text-[24px]">layers</span>
              </div>
              <div>
                <h3 class="font-headline-md text-base sm:text-lg font-bold text-on-surface flex items-center gap-1.5">
                  选择【{{ region?.name || '离线资源' }}】规格
                </h3>
                <p class="text-[11px] sm:text-xs text-on-surface-variant mt-0.5">
                  双层搭积木架构 · 支持后续随时双向无缝切换
                </p>
              </div>
            </div>

            <button
              type="button"
              @click="close"
              aria-label="关闭规格选择"
              class="w-8 h-8 rounded-full flex items-center justify-center bg-surface-container-high hover:bg-surface-bright text-on-surface-variant hover:text-on-surface border border-outline-variant/30 transition-colors"
            >
              <span class="material-symbols-outlined text-[18px]">close</span>
            </button>
          </div>

          <!-- Body -->
          <div
            class="p-4 sm:p-5 flex-1 flex flex-col gap-3.5 overflow-y-auto no-scrollbar overscroll-contain"
            style="overscroll-behavior: contain; -webkit-overflow-scrolling: touch;"
          >
            <!-- Spec Option 1: 极速基础包 -->
            <div
              @click="selectedSpec = 'base'"
              class="p-3.5 rounded-2xl border transition-all cursor-pointer flex flex-col gap-2 relative group"
              :class="selectedSpec === 'base'
                ? 'bg-primary/10 border-primary glow-primary shadow-lg ring-1 ring-primary/40'
                : 'frost-glass border-outline-variant/30 hover:border-outline-variant/60'"
            >
              <div class="flex items-center justify-between">
                <div class="flex items-center gap-2">
                  <span class="text-xs font-bold px-2 py-0.5 rounded-md bg-primary/20 text-primary border border-primary/30 flex items-center gap-1">
                    <span class="material-symbols-outlined text-[13px]">bolt</span>
                    推荐 · 极速就绪
                  </span>
                  <span class="text-sm font-bold text-on-surface">极速基础包</span>
                </div>
                <div class="flex items-center gap-1.5">
                  <span class="text-xs font-mono font-bold text-primary">{{ formatSize(region?.packInfo?.sizeBytes || 87364) }}</span>
                  <span class="material-symbols-outlined text-[20px]" :class="selectedSpec === 'base' ? 'text-primary' : 'text-outline/40'">
                    {{ selectedSpec === 'base' ? 'radio_button_checked' : 'radio_button_unchecked' }}
                  </span>
                </div>
              </div>

              <div class="text-[12px] text-on-surface-variant leading-relaxed">
                包含 {{ region?.mountainsCount || 36 }} 座山峰等高线、GPS轨迹、车程海拔、路书及防坑避险决策数据。
              </div>

              <div class="grid grid-cols-2 gap-1.5 text-[11px] text-on-surface-variant/90 pt-1 border-t border-outline-variant/20">
                <div class="flex items-center gap-1 text-emerald-400">
                  <span class="material-symbols-outlined text-[13px]">check</span>
                  <span>零流量秒速完成 (约 87KB)</span>
                </div>
                <div class="flex items-center gap-1 text-emerald-400">
                  <span class="material-symbols-outlined text-[13px]">check</span>
                  <span>100% 完整离线路线与轨迹</span>
                </div>
                <div class="flex items-center gap-1 text-emerald-400">
                  <span class="material-symbols-outlined text-[13px]">check</span>
                  <span>全量路况下撤与防坑指南</span>
                </div>
                <div class="flex items-center gap-1 text-amber-300">
                  <span class="material-symbols-outlined text-[13px]">swap_horiz</span>
                  <span>随时一键增量补全画册</span>
                </div>
              </div>
            </div>

            <!-- Spec Option 2: 完整风光包 -->
            <div
              @click="selectedSpec = 'full'"
              class="p-3.5 rounded-2xl border transition-all cursor-pointer flex flex-col gap-2 relative group"
              :class="selectedSpec === 'full'
                ? 'bg-secondary/10 border-secondary glow-secondary shadow-lg ring-1 ring-secondary/40'
                : 'frost-glass border-outline-variant/30 hover:border-outline-variant/60'"
            >
              <div class="flex items-center justify-between">
                <div class="flex items-center gap-2">
                  <span class="text-xs font-bold px-2 py-0.5 rounded-md bg-secondary/20 text-secondary border border-secondary/30 flex items-center gap-1">
                    <span class="material-symbols-outlined text-[13px]">photo_library</span>
                    沉浸视觉 · 完整版
                  </span>
                  <span class="text-sm font-bold text-on-surface">完整风光包</span>
                </div>
                <div class="flex items-center gap-1.5">
                  <span class="text-xs font-mono font-bold text-secondary">{{ formatTotalSize() }}</span>
                  <span class="material-symbols-outlined text-[20px]" :class="selectedSpec === 'full' ? 'text-secondary' : 'text-outline/40'">
                    {{ selectedSpec === 'full' ? 'radio_button_checked' : 'radio_button_unchecked' }}
                  </span>
                </div>
              </div>

              <div class="text-[12px] text-on-surface-variant leading-relaxed">
                包含基础包全部离线路线轨迹，并增配 {{ region?.mountainsCount || 36 }} 座名山高清全景实拍画册图集。
              </div>

              <div class="grid grid-cols-2 gap-1.5 text-[11px] text-on-surface-variant/90 pt-1 border-t border-outline-variant/20">
                <div class="flex items-center gap-1 text-emerald-400">
                  <span class="material-symbols-outlined text-[13px]">check</span>
                  <span>包含基础包全部路线数据</span>
                </div>
                <div class="flex items-center gap-1 text-secondary">
                  <span class="material-symbols-outlined text-[13px]">photo_camera</span>
                  <span>高清名山实拍图集身临其境</span>
                </div>
                <div class="flex items-center gap-1 text-secondary">
                  <span class="material-symbols-outlined text-[13px]">wifi</span>
                  <span>推荐在 Wi-Fi 环境下预载</span>
                </div>
                <div class="flex items-center gap-1 text-amber-300">
                  <span class="material-symbols-outlined text-[13px]">cleaning_services</span>
                  <span>空间紧张可一键释放图片</span>
                </div>
              </div>
            </div>

            <!-- Tips Panel (生动简略的区别与切换说明) -->
            <div class="p-3.5 rounded-2xl bg-surface-container/70 border border-outline-variant/20 flex flex-col gap-2">
              <div class="flex items-center gap-1.5 text-xs font-bold text-primary">
                <span class="material-symbols-outlined text-[16px]">help_outline</span>
                <span>离线规格选择与切换指南 (Tips)</span>
              </div>
              <ul class="text-[11px] text-on-surface-variant leading-relaxed space-y-1 pl-1">
                <li class="flex items-start gap-1.5">
                  <span class="text-primary font-bold">Q1:</span>
                  <span><strong class="text-on-surface">先下了基础包，以后还能看照片吗？</strong> 可以！后续在面板点击「+ 补全画册」仅增量下载图片压缩包，无需重新下载路线数据。</span>
                </li>
                <li class="flex items-start gap-1.5">
                  <span class="text-secondary font-bold">Q2:</span>
                  <span><strong class="text-on-surface">下了风光包，手机存储不够怎么办？</strong> 随时在面板点击「释放画册图片」，秒级腾出约 15.8MB 空间，且所有离线路线轨迹完好保留。</span>
                </li>
                <li class="flex items-start gap-1.5">
                  <span class="text-amber-400 font-bold">Q3:</span>
                  <span><strong class="text-on-surface">户外无网徒步选哪个？</strong> 两者离线导航、轨迹与等高线决策能力 100% 一致。临近出发或手机存储敏感推荐选择极速基础包。</span>
                </li>
              </ul>
            </div>
          </div>

          <!-- Footer Actions -->
          <div class="p-4 sm:p-5 pt-3 bg-surface-container-high/40 border-t border-outline-variant/20 flex items-center justify-end gap-3">
            <button
              type="button"
              @click="close"
              class="px-4 py-2 rounded-xl text-xs font-semibold text-on-surface-variant hover:text-on-surface active:scale-95 transition-all"
            >
              稍后决定
            </button>
            <button
              type="button"
              @click="confirmSelection"
              class="px-5 py-2.5 rounded-xl text-xs font-bold flex items-center gap-1.5 shadow-lg active:scale-95 transition-all"
              :class="selectedSpec === 'base'
                ? 'bg-primary text-on-primary hover:bg-primary/90 glow-primary'
                : 'bg-secondary text-on-secondary hover:bg-secondary/90 glow-secondary'"
            >
              <span class="material-symbols-outlined text-[16px]">cloud_download</span>
              <span>
                {{ selectedSpec === 'base' ? '下载极速基础包 (约 87KB)' : '下载完整风光包 (约 15.8MB)' }}
              </span>
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref } from 'vue';
import { useScrollLock } from '@/composables/useScrollLock.js';

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  region: {
    type: Object,
    default: null
  }
});

const emit = defineEmits(['update:modelValue', 'confirm']);

const selectedSpec = ref('base');

useScrollLock(() => props.modelValue);

function close() {
  emit('update:modelValue', false);
}

function confirmSelection() {
  emit('confirm', {
    withGallery: selectedSpec.value === 'full'
  });
  close();
}

function formatSize(bytes) {
  if (!bytes) return '';
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `约 ${Math.round(bytes / 1000)}KB`;
  return `约 ${(bytes / (1024 * 1024)).toFixed(1)}MB`;
}

function formatTotalSize() {
  const baseBytes = props.region?.packInfo?.sizeBytes || 87364;
  const galleryBytes = props.region?.packInfo?.galleryPack?.sizeBytes || 15840000;
  return formatSize(baseBytes + galleryBytes);
}
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

@keyframes modal-in {
  from {
    opacity: 0;
    transform: scale(0.96) translateY(12px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

.animate-modal-in {
  animation: modal-in 0.22s cubic-bezier(0.16, 1, 0.3, 1) both;
}

.glow-primary {
  box-shadow: 0 0 15px rgba(16, 185, 129, 0.2);
}

.glow-secondary {
  box-shadow: 0 0 15px rgba(6, 182, 212, 0.2);
}
</style>
