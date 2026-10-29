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

      <!-- First-Launch Mandatory Safety & Legal Disclaimer Modal -->
      <LegalDisclaimerModal v-model="isDisclaimerOpen" :mandatory="true" />

      <!-- Official In-App Online Update Modal -->
      <AppUpdateModal />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import ExploreView from '@/views/ExploreView.vue';
import PlanView from '@/views/PlanView.vue';
import ProfileView from '@/views/ProfileView.vue';
import BottomNav from '@/components/common/BottomNav.vue';
import LegalDisclaimerModal from '@/components/common/LegalDisclaimerModal.vue';
import AppUpdateModal from '@/components/common/AppUpdateModal.vue';
import { useUpdateStore } from '@/stores/updateStore.js';
import { IS_DEBUG_BUILD } from '@/config/version.js';

// 首次启动强制法律免责协议弹窗检测
const isDisclaimerOpen = ref(false);
const updateStore = useUpdateStore();

onMounted(async () => {
  try {
    const agreed = localStorage.getItem('alpine_disclaimer_agreed');
    if (agreed !== 'true') {
      isDisclaimerOpen.value = true;
    }
  } catch (e) {
    isDisclaimerOpen.value = true;
  }

  // 启动 2 秒后在后台静默检测是否有新版本发布
  setTimeout(() => {
    updateStore.checkForUpdate(true);
  }, 2000);

  // 在离线 Debug APK 或非 dev 模式下，按需加载 @agent-feedback/client 确保真机常驻悬浮胶囊
  if (!import.meta.env.DEV && IS_DEBUG_BUILD) {
    try {
      await import('@lylyuanliang/agent-feedback-client');
    } catch {}
  }
});

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
