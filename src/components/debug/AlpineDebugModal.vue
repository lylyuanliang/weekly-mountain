<template>

  <!-- Debug Modal / Bottom Sheet -->

  <Teleport to="body">

    <aside

      v-if="modelValue"

      class="alpine-debug-modal fixed inset-0 z-[1000] flex items-end sm:items-center justify-center p-0 sm:p-4 bg-black/80 backdrop-blur-md animate-fade-in select-none modal-backdrop-scroll-contain"

      @click.self="close"

      @touchmove.self.prevent

    >

    <div

      class="w-full sm:max-w-lg max-h-[92vh] flex flex-col rounded-t-3xl sm:rounded-3xl bg-[#13161c] border border-white/10 shadow-2xl overflow-hidden"

    >

      <!-- Header -->

      <header class="px-5 py-4 border-b border-white/10 flex items-center justify-between bg-surface-container-high/40">

        <div class="flex items-center gap-2.5">

          <div class="w-8 h-8 rounded-xl bg-primary/20 text-primary flex items-center justify-center">

            <span class="material-symbols-outlined text-[18px]">build_circle</span>

          </div>

          <div>

            <div class="flex items-center gap-2">

              <h3 class="font-headline-md text-[15px] font-bold text-on-surface">真机联调与内测服务</h3>

              <span class="px-1.5 py-0.2 rounded-full bg-primary/20 text-primary font-mono text-[9px] font-bold border border-primary/40">

                DEBUG

              </span>

            </div>

            <p class="font-label-data-sm text-[10px] text-on-surface-variant">内网穿透通道 · 在线 OTA 更新 · 真机实时反馈</p>

          </div>

        </div>



        <button

          type="button"

          @click="close"

          class="w-8 h-8 rounded-full bg-white/5 hover:bg-white/10 text-on-surface-variant hover:text-on-surface flex items-center justify-center active:scale-95 transition-all"

        >

          <span class="material-symbols-outlined text-[18px]">close</span>

        </button>

      </header>



      <!-- Scrollable Body -->

      <div class="flex-1 overflow-y-auto p-4 sm:p-5 space-y-4 overscroll-contain" style="overscroll-behavior: contain; -webkit-overflow-scrolling: touch;">

        <!-- 1. 穿透服务连通性与诊断 -->

        <section class="p-3.5 rounded-2xl bg-surface-container/60 border border-white/5 space-y-2.5">

          <div class="flex items-center justify-between">

            <span class="font-headline-md text-[13px] font-bold text-on-surface flex items-center gap-1.5">

              <span class="material-symbols-outlined text-[16px] text-primary">lan</span>

              穿透与通信诊断

            </span>

            <span

              class="px-2 py-0.5 rounded-full text-[10px] font-mono border"

              :class="debugStore.isCapacitorNative ? 'bg-secondary/15 text-secondary border-secondary/30' : 'bg-white/5 text-on-surface-variant border-white/10'"

            >

              {{ debugStore.isCapacitorNative ? 'Android 原生容器' : 'Web 移动端' }}

            </span>

          </div>



          <!-- 穿透地址配置 -->

          <div class="space-y-1">

            <label class="text-[11px] text-on-surface-variant flex items-center justify-between">

              <span>穿透通信基地址</span>

              <button

                type="button"

                @click="resetTunnelUrl"

                class="text-[10px] text-primary hover:underline active:scale-95"

              >

                重置默认

              </button>

            </label>

            <div class="flex items-center gap-2">

              <input

                v-model="inputTunnelUrl"

                type="text"

                class="flex-1 px-3 py-1.5 rounded-xl bg-black/40 border border-white/10 text-[11px] font-mono text-on-surface focus:outline-none focus:border-primary/60"

                placeholder="https://your-tunnel-domain.cpolar.top"

              />

              <button

                type="button"

                @click="handleSaveAndTestTunnel"

                :disabled="debugStore.tunnelStatus.checking"

                class="px-3 py-1.5 rounded-xl bg-surface-container-high hover:bg-surface-container text-primary text-[11px] font-semibold border border-primary/30 flex items-center gap-1 active:scale-95 transition-all"

              >

                <span class="material-symbols-outlined text-[14px]" :class="{ 'animate-spin': debugStore.tunnelStatus.checking }">

                  {{ debugStore.tunnelStatus.checking ? 'refresh' : 'network_check' }}

                </span>

                <span>测试</span>

              </button>

            </div>

            <!-- 测试状态提示 -->

            <div v-if="debugStore.tunnelStatus.msg" class="text-[11px] flex items-center gap-1.5 pt-0.5" :class="debugStore.tunnelStatus.healthy ? 'text-primary' : 'text-amber-400'">

              <span class="material-symbols-outlined text-[13px]">

                {{ debugStore.tunnelStatus.healthy ? 'check_circle' : 'warning' }}

              </span>

              <span>{{ debugStore.tunnelStatus.msg }}</span>

            </div>

          </div>

        </section>



        <!-- 2. 在线更新 (OTA Online Update) -->

        <section class="p-3.5 rounded-2xl bg-surface-container/60 border border-white/5 space-y-3">

          <div class="flex items-center justify-between">

            <div class="flex items-center gap-1.5">

              <span class="material-symbols-outlined text-[16px] text-secondary">system_update</span>

              <span class="font-headline-md text-[13px] font-bold text-on-surface">在线更新与版本管理</span>

            </div>

            <span class="text-[10px] text-on-surface-variant font-mono">

              当前: v{{ APP_VERSION }}

            </span>

          </div>



          <!-- 检查更新与状态 -->

          <div class="flex items-center gap-2">

            <button

              type="button"

              @click="handleCheckUpdate"

              :disabled="debugStore.isCheckingUpdate"

              class="flex-1 py-2 px-3 rounded-xl bg-primary text-on-primary font-body-sm text-[12px] font-bold flex items-center justify-center gap-1.5 active:scale-95 transition-all shadow-md"

            >

              <span class="material-symbols-outlined text-[16px]" :class="{ 'animate-spin': debugStore.isCheckingUpdate }">

                sync

              </span>

              <span>{{ debugStore.isCheckingUpdate ? '正在检测远端产物...' : '检查在线更新' }}</span>

            </button>

          </div>



          <!-- 更新错误提示 -->

          <div v-if="debugStore.updateError" class="p-2.5 rounded-xl bg-amber-500/10 border border-amber-500/30 text-[11px] text-amber-300 flex items-center gap-2">

            <span class="material-symbols-outlined text-[15px] flex-shrink-0">error</span>

            <span>{{ debugStore.updateError }}</span>

          </div>



          <!-- 检测到新版本卡片 -->

          <div

            v-if="debugStore.updateInfo"

            class="p-3 rounded-xl bg-black/40 border border-white/10 space-y-2 animate-fade-in"

          >

            <div class="flex items-center justify-between">

              <div class="flex items-center gap-1.5">

                <span class="w-2 h-2 rounded-full" :class="hasNewVersion ? 'bg-amber-400 animate-ping' : 'bg-primary'"></span>

                <span class="text-[12px] font-bold text-on-surface">

                  {{ hasNewVersion ? `发现新构建: v${debugStore.updateInfo.latestVersion}` : '已是最新构建版本' }}

                </span>

              </div>

              <span class="text-[10px] text-on-surface-variant font-mono">

                大小: {{ debugStore.updateInfo.fileSize }}

              </span>

            </div>



            <!-- 更新日志 -->

            <ul v-if="debugStore.updateInfo.changelog?.length" class="text-[11px] text-on-surface-variant list-disc pl-4 space-y-0.5">

              <li v-for="(log, idx) in debugStore.updateInfo.changelog" :key="idx">{{ log }}</li>

            </ul>



            <!-- 下载进行中展示原生流式进度 -->

            <div v-if="debugStore.downloadStatus === 'downloading'" class="space-y-2 p-2.5 rounded-xl bg-surface-container-high/80 border border-primary/30">

              <div class="flex items-center justify-between text-[11px]">

                <span class="text-primary font-medium flex items-center gap-1">

                  <span class="material-symbols-outlined text-[14px] animate-spin">sync</span>

                  <span>正在应用内极速下载 APK...</span>

                </span>

                <span class="font-mono text-white font-bold">{{ debugStore.downloadProgress.percent }}%</span>

              </div>

              <div class="h-1.5 w-full rounded-full bg-surface-container-highest overflow-hidden">

                <div class="h-full bg-gradient-to-r from-emerald-500 to-teal-400 transition-all duration-150" :style="{ width: `${debugStore.downloadProgress.percent}%` }"></div>

              </div>

              <div class="flex items-center justify-between text-[10px] text-on-surface-variant font-mono">

                <span>{{ debugStore.downloadProgress.speed || '连接中...' }}</span>

                <button type="button" @click="debugStore.cancelDownloadApk" class="text-amber-400 hover:underline">取消下载</button>

              </div>

            </div>



            <div v-else-if="debugStore.downloadStatus === 'installing'" class="p-2.5 rounded-xl bg-emerald-500/10 border border-emerald-400/30 text-emerald-300 text-[11.5px] flex items-center justify-center gap-2">

              <span class="material-symbols-outlined text-[16px] animate-bounce">install_mobile</span>

              <span>下载完成，正在唤起手机系统安装界面...</span>

            </div>



            <!-- 一键在线下载安装（常态） -->

            <div v-else class="space-y-1">

              <button

                type="button"

                @click="handleDownloadApk"

                class="w-full py-2 px-3 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-600 text-white font-body-sm text-[12px] font-bold flex items-center justify-center gap-1.5 active:scale-95 transition-all shadow-lg"

              >

                <span class="material-symbols-outlined text-[16px]">download</span>

                <span>{{ hasNewVersion ? '一键在 App 内免跳转下载并升级' : '在 App 内重新下载当前最新 APK' }}</span>

              </button>

              <p class="text-[9.5px] text-outline text-center">

                原生流式下载至手机并直接唤起安装，免跳浏览器、免电脑与数据线

              </p>

            </div>

          </div>





        </section>



        <!-- 3. 真机反馈渠道 (In-App Feedback) -->

        <section class="p-3.5 rounded-2xl bg-surface-container/60 border border-white/5 space-y-3">

          <div class="flex items-center justify-between">

            <div class="flex items-center gap-1.5">

              <span class="material-symbols-outlined text-[16px] text-tertiary">rate_review</span>

              <span class="font-headline-md text-[13px] font-bold text-on-surface">App 内置真机反馈渠道</span>

            </div>

            <span class="text-[10px] text-primary font-mono">通道直连</span>

          </div>



          <p class="text-[11px] text-on-surface-variant">

            在 App 内可直接截屏并向 AI 提交 Bug 与优化建议，后台哨兵将实时捕获并分析。

          </p>



          <div class="grid grid-cols-2 gap-2">

            <button

              type="button"

              @click="openFeedbackCreate"

              class="py-2.5 px-3 rounded-xl bg-surface-container-high border border-primary/30 text-primary font-body-sm text-[12px] font-bold flex items-center justify-center gap-1.5 active:scale-95 transition-all shadow-sm"

            >

              <span class="material-symbols-outlined text-[16px]">edit_note</span>

              <span>提交真机反馈</span>

            </button>



            <button

              type="button"

              @click="openFeedbackHistory"

              class="py-2.5 px-3 rounded-xl bg-surface-container-high border border-white/10 text-on-surface font-body-sm text-[12px] font-semibold flex items-center justify-center gap-1.5 active:scale-95 transition-all shadow-sm"

            >

              <span class="material-symbols-outlined text-[16px] text-secondary">history</span>

              <span>查看处理进度</span>

            </button>

          </div>



          <!-- 浮动胶囊显示开关 -->

          <div class="pt-2 border-t border-white/5 flex items-center justify-between">

            <div class="flex flex-col">

              <span class="text-[12px] font-medium text-on-surface">屏幕常驻反馈悬浮小胶囊</span>

              <span class="text-[10px] text-on-surface-variant">屏幕右侧快捷按钮 (支持任意拖拽)</span>

            </div>



            <button

              type="button"

              @click="debugStore.toggleCapsuleVisibility()"

              class="w-11 h-6 rounded-full transition-colors relative"

              :class="debugStore.isCapsuleVisible ? 'bg-primary' : 'bg-surface-container-highest border border-white/10'"

            >

              <span

                class="absolute top-0.5 w-5 h-5 rounded-full bg-white transition-transform"

                :class="debugStore.isCapsuleVisible ? 'left-[22px]' : 'left-0.5'"

              ></span>

            </button>

          </div>

        </section>

      </div>



      <!-- Footer -->

      <footer class="p-3 border-t border-white/10 text-center bg-surface-container-lowest text-[10px] text-outline">

        成都周边50座山 · Alpine Explorer 开发者联调模式

      </footer>

    </div>

    </aside>

  </Teleport>

</template>



<script setup>

import { ref, computed, watch, onMounted } from 'vue';

import { useDebugStore } from '@/stores/debugStore.js';

import { useScrollLock } from '@/composables/useScrollLock.js';

import { APP_VERSION, BUILD_CODE, DEFAULT_CPOLAR_TUNNEL } from '@/config/version.js';



const props = defineProps({

  modelValue: {

    type: Boolean,

    default: false

  }

});



const emit = defineEmits(['update:modelValue']);



const debugStore = useDebugStore();

const inputTunnelUrl = ref(debugStore.tunnelUrl);



// 彻底杜绝底层页面背景滚动穿透

useScrollLock(() => props.modelValue);



watch(

  () => debugStore.tunnelUrl,

  (val) => {

    inputTunnelUrl.value = val;

  }

);



const hasNewVersion = computed(() => {

  if (!debugStore.updateInfo) return false;

  const remoteCode = debugStore.updateInfo.buildCode || 0;

  return remoteCode > BUILD_CODE || debugStore.updateInfo.latestVersion !== APP_VERSION;

});



function close() {

  emit('update:modelValue', false);

}



function resetTunnelUrl() {

  inputTunnelUrl.value = DEFAULT_CPOLAR_TUNNEL;

  debugStore.setTunnelUrl(DEFAULT_CPOLAR_TUNNEL);

}



async function handleSaveAndTestTunnel() {

  debugStore.setTunnelUrl(inputTunnelUrl.value);

  await debugStore.testTunnelHealth();

}



async function handleCheckUpdate() {

  debugStore.setTunnelUrl(inputTunnelUrl.value);

  await debugStore.checkUpdate();

}



async function handleDownloadApk() {

  await debugStore.downloadAndInstallApk();

}



function openFeedbackCreate() {

  close();

  setTimeout(() => {

    window.dispatchEvent(new CustomEvent('wm-open-feedback', { detail: { tab: 'create' } }));

  }, 150);

}



function openFeedbackHistory() {

  close();

  setTimeout(() => {

    window.dispatchEvent(new CustomEvent('wm-open-feedback', { detail: { tab: 'history' } }));

  }, 150);

}



onMounted(() => {

  if (props.modelValue) {

    debugStore.testTunnelHealth();

  }

});



watch(

  () => props.modelValue,

  (val) => {

    if (val) {

      debugStore.testTunnelHealth();

      debugStore.checkUpdate();

    }

  }

);

</script>
