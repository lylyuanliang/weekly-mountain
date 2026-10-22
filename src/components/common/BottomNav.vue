<template>
  <nav class="stitch-bottom-nav bottom-nav fixed bottom-0 left-0 right-0 max-w-md mx-auto w-full z-50 flex justify-around items-center px-space-md py-1.5 pb-2.5 bg-surface-container/95 dark:bg-surface-container/95 backdrop-blur-xl rounded-t-2xl shadow-2xl border-t border-outline-variant/30 select-none">
    <!-- Tab 1: 探索 (Explore) -->
    <router-link
      to="/explore"
      class="nav-tab nav-tab-explore flex flex-col items-center justify-center transition-all duration-150 active:scale-95 py-1 px-3.5"
      :class="isExploreActive ? activeClass : inactiveClass"
      aria-label="探索地图"
    >
      <div class="relative flex items-center justify-center">
        <span
          class="material-symbols-outlined text-[22px]"
          :class="{ fill: isExploreActive }"
          :style="isExploreActive ? { fontVariationSettings: `'FILL' 1` } : {}"
        >
          terrain
        </span>
        <span
          v-if="isExploreActive"
          class="absolute -bottom-1 w-1.5 h-1.5 rounded-full bg-primary glow-primary"
        ></span>
      </div>
      <span class="font-label-data-sm text-[11px] mt-0.5 font-medium">探索</span>
    </router-link>

    <!-- Tab 2: 周计划 (Plan) -->
    <router-link
      to="/plan"
      class="nav-tab nav-tab-plan flex flex-col items-center justify-center transition-all duration-150 active:scale-95 py-1 px-3.5"
      :class="isPlanActive ? activeClass : inactiveClass"
      aria-label="周计划看板"
    >
      <div class="relative flex items-center justify-center">
        <span
          class="material-symbols-outlined text-[22px]"
          :class="{ fill: isPlanActive }"
          :style="isPlanActive ? { fontVariationSettings: `'FILL' 1` } : {}"
        >
          calendar_today
        </span>
        <span
          v-if="isPlanActive"
          class="absolute -bottom-1 w-1.5 h-1.5 rounded-full bg-primary glow-primary"
        ></span>
      </div>
      <span class="font-label-data-sm text-[11px] mt-0.5 font-medium">周计划</span>
    </router-link>

    <!-- Tab 3: 我的成就与设置 (Profile) -->
    <router-link
      to="/profile"
      class="nav-tab nav-tab-profile flex flex-col items-center justify-center transition-all duration-150 active:scale-95 py-1 px-3.5"
      :class="isProfileActive ? activeClass : inactiveClass"
      aria-label="我的成就与设置"
    >
      <div class="relative flex items-center justify-center">
        <span
          class="material-symbols-outlined text-[22px]"
          :class="{ fill: isProfileActive }"
          :style="isProfileActive ? { fontVariationSettings: `'FILL' 1` } : {}"
        >
          military_tech
        </span>
        <span
          v-if="isProfileActive"
          class="absolute -bottom-1 w-1.5 h-1.5 rounded-full bg-primary glow-primary"
        ></span>
      </div>
      <span class="font-label-data-sm text-[11px] mt-0.5 font-medium">我的</span>
    </router-link>
  </nav>
</template>

<script setup>
import { computed } from 'vue';
import { useRoute } from 'vue-router';

const route = useRoute();

const isExploreActive = computed(() => {
  return route.path === '/' || route.path.startsWith('/explore');
});

const isPlanActive = computed(() => {
  return route.path.startsWith('/plan');
});

const isProfileActive = computed(() => {
  return route.path.startsWith('/profile');
});

const activeClass = 'text-primary font-bold rounded-full bg-primary/10 shadow-[0_0_12px_rgba(16,185,129,0.25)]';
const inactiveClass = 'text-on-surface-variant hover:text-primary';
</script>

<style scoped>
.glow-primary {
  box-shadow: 0 0 10px rgba(16, 185, 129, 0.6);
}
</style>
