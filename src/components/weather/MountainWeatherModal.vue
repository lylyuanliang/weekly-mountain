<template>
  <div
    v-if="modelValue && mountain"
    class="mountain-weather-modal-wrapper fixed inset-0 z-50 flex items-end sm:items-center justify-center p-0 sm:p-4 bg-black/70 backdrop-blur-sm animate-fade-in"
    @click.self="closeModal"
  >
    <div
      class="w-full max-w-md bg-surface-container rounded-t-3xl sm:rounded-2xl border-t sm:border border-outline-variant/30 shadow-2xl p-4 sm:p-5 space-y-4 max-h-[85vh] overflow-y-auto"
      role="dialog"
      aria-modal="true"
      :aria-label="`${mountain.name} 实时气象预报`"
    >
      <!-- Modal Header -->
      <div class="flex items-start justify-between">
        <div>
          <div class="flex items-center gap-2">
            <span class="w-2.5 h-2.5 rounded-full bg-primary glow-primary animate-pulse"></span>
            <h3 class="text-headline-md font-bold text-on-surface">
              {{ mountain.name }} · 实时天气
            </h3>
          </div>
          <p class="text-caption text-on-surface-variant mt-1">
            {{ mountain.region || '四川' }} · {{ mountain.county }} · 标高 {{ mountain.altitude_m }}m
          </p>
        </div>

        <button
          type="button"
          @click="closeModal"
          class="w-8 h-8 rounded-full bg-surface-container-high flex items-center justify-center text-on-surface-variant hover:text-on-surface border border-outline-variant/30 active:scale-95 transition-all"
          aria-label="关闭天气预报"
        >
          <span class="material-symbols-outlined text-[18px]">close</span>
        </button>
      </div>

      <!-- Live 7-Day Weather Component -->
      <MountainWeatherCard :mountain="mountain" :auto-load="true" />

      <!-- Footer Actions -->
      <div class="pt-2 flex items-center gap-3">
        <button
          type="button"
          @click="handleViewDetail"
          class="flex-1 py-2.5 px-3 rounded-xl bg-gradient-to-r from-primary-container to-secondary-container text-surface-container-lowest font-headline-md text-body-sm font-bold flex items-center justify-center gap-1 glow-primary active:scale-95 transition-all"
        >
          <span class="material-symbols-outlined text-[18px]">explore</span>
          <span>查看该山峰完整路线</span>
        </button>

        <button
          type="button"
          @click="closeModal"
          class="py-2.5 px-4 rounded-xl bg-surface-container-high border border-outline-variant/30 text-on-surface text-body-sm font-semibold active:scale-95 hover:border-outline-variant transition-all"
        >
          关闭
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import MountainWeatherCard from './MountainWeatherCard.vue';

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  mountain: {
    type: Object,
    default: null
  }
});

const emit = defineEmits(['update:modelValue', 'view-detail']);

function closeModal() {
  emit('update:modelValue', false);
}

function handleViewDetail() {
  closeModal();
  emit('view-detail', props.mountain);
}
</script>

<style scoped>
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
.animate-fade-in {
  animation: fadeIn 0.2s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}
</style>
