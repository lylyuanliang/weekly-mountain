<template>
  <div id="mountain-app" class="app-root w-full min-h-screen bg-surface-lowest text-on-surface flex justify-center selection:bg-primary-container selection:text-on-primary">
    <!-- Viewport Container (max-w-[480px] on desktop, 100% on mobile) -->
    <div class="w-full max-w-[480px] min-h-screen relative flex flex-col bg-background border-x border-white/5 overflow-x-hidden">
      <!-- Main view hosts (Native Tab Stacking Architecture, 0ms switch, absolute 0 flicker) -->
      <main class="flex-1 w-full relative">
        <ExploreView v-show="activeTab === 'explore'" />
        <PlanView v-show="activeTab === 'plan'" />
        <ProfileView v-show="activeTab === 'profile'" />
      </main>

      <!-- Global 3-Tab Bottom Navigation -->
      <BottomNav />

      <!-- Mobile In-App Feedback Widget (Dev / Cpolar Tunnel only) -->
      <MobileFeedbackWidget />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useRoute } from 'vue-router';
import ExploreView from '@/views/ExploreView.vue';
import PlanView from '@/views/PlanView.vue';
import ProfileView from '@/views/ProfileView.vue';
import BottomNav from '@/components/common/BottomNav.vue';
import MobileFeedbackWidget from '@/components/debug/MobileFeedbackWidget.vue';

const route = useRoute();

const activeTab = computed(() => {
  if (route.path.startsWith('/plan')) return 'plan';
  if (route.path.startsWith('/profile')) return 'profile';
  return 'explore';
});
</script>

<style>
/* 基础全局重置与视口设定，彻底禁止移动端橡皮筋下拉穿透 */
html,
body {
  margin: 0;
  padding: 0;
  width: 100%;
  min-height: 100%;
  background-color: #0a0e17;
  color: #dfe2ef;
  font-family: 'Plus Jakarta Sans', system-ui, -apple-system, sans-serif;
  -webkit-font-smoothing: antialiased;
  overscroll-behavior: none;
  overscroll-behavior-y: none;
  -webkit-overflow-scrolling: touch;
}

#app,
#mountain-app {
  width: 100%;
  min-height: 100vh;
  position: relative;
  overscroll-behavior: none;
  overscroll-behavior-y: none;
}

/* Material Symbols font settings */
.material-symbols-outlined {
  font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;
  display: inline-block;
  vertical-align: middle;
  line-height: 1;
}

.material-symbols-outlined.fill {
  font-variation-settings: 'FILL' 1;
}
</style>
