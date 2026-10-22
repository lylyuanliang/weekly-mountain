<template>
  <Teleport to="body">
    <!-- Backdrop Overlay -->
    <div
      v-if="modelValue"
      class="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm transition-opacity duration-300 flex items-end sm:items-center justify-center p-0 sm:p-4"
      @click="close"
    >
      <!-- Sheet Modal Container -->
      <div
        class="w-full max-w-md bg-surface-container-low border border-outline-variant/40 rounded-t-3xl sm:rounded-2xl shadow-2xl p-5 flex flex-col gap-4 max-h-[85vh] overflow-y-auto no-scrollbar"
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
            <span class="text-primary font-bold">100% 离线可用</span>
          </div>

          <div
            v-for="reg in regionStore.activeRegions"
            :key="reg.id"
            @click="selectRegion(reg)"
            class="p-3.5 rounded-xl border transition-all cursor-pointer flex items-center justify-between"
            :class="reg.id === regionStore.currentRegionId
              ? 'bg-surface-container-high border-primary glow-primary shadow-lg'
              : 'frost-glass border-outline-variant/30 hover:border-outline-variant/60'"
          >
            <div class="flex items-center gap-3">
              <div
                class="w-10 h-10 rounded-xl flex items-center justify-center text-[18px]"
                :class="reg.id === regionStore.currentRegionId ? 'bg-primary/20 text-primary' : 'bg-surface-container text-on-surface-variant'"
              >
                🏔️
              </div>
              <div class="flex flex-col">
                <div class="flex items-center gap-2">
                  <span class="text-body-md font-bold text-on-surface">{{ reg.name }}</span>
                  <span class="px-1.5 py-0.5 text-[10px] font-label-data-sm bg-primary/20 text-primary rounded font-semibold">
                    {{ reg.badge }}
                  </span>
                </div>
                <span class="text-[12px] text-on-surface-variant line-clamp-1 mt-0.5">
                  {{ reg.description }}
                </span>
              </div>
            </div>

            <span
              v-if="reg.id === regionStore.currentRegionId"
              class="material-symbols-outlined text-primary text-[20px] flex-shrink-0"
            >
              check_circle
            </span>
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
          💡 后续将陆续上线重庆、秦岭、滇中、京郊等周边山峰与 GPS 路线
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { useRegionStore } from '@/stores/regionStore.js';

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits(['update:modelValue', 'region-change', 'toast']);

const regionStore = useRegionStore();

function close() {
  emit('update:modelValue', false);
}

function selectRegion(reg) {
  regionStore.setRegion(reg.id);
  emit('region-change', reg);
  close();
}

function handlePlannedClick(reg) {
  emit('toast', `【${reg.name}】正在实地勘测与整理 GPS 路线数据，敬请期待！`);
}
</script>
