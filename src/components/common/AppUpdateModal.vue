<template>
  <Teleport to="body">
    <Transition name="fade">
      <div
        v-if="updateStore.isModalOpen"
        class="fixed inset-0 z-[1050] flex items-center justify-center p-4 bg-black/80 backdrop-blur-md modal-backdrop-scroll-contain select-none"
        @click.self="onBackdropClick"
        @touchmove.self.prevent
      >
        <div
          class="w-full max-w-sm rounded-3xl bg-surface-container-low border border-outline-variant/30 shadow-2xl overflow-hidden flex flex-col text-on-surface animate-modal-in"
          role="dialog"
          aria-modal="true"
        >
          <!-- Modal Header (Alpine Peak Styling) -->
          <div class="relative p-5 pb-4 bg-gradient-to-b from-primary/15 via-surface-container/60 to-transparent border-b border-outline-variant/20">
            <div class="flex items-start justify-between">
              <div class="flex items-center gap-3">
                <div
                  class="w-10 h-10 rounded-2xl flex items-center justify-center shadow-sm flex-shrink-0"
                  :class="updateStore.versionDiffStatus === 'ahead_of_release' ? 'bg-cyan-500/20 border border-cyan-500/40 text-cyan-400' : 'bg-primary/20 border border-primary/30 text-primary'"
                >
                  <span class="material-symbols-outlined text-[24px]">
                    {{ updateStore.errorMessage ? 'info' : (updateStore.hasUpdate ? 'system_update' : (updateStore.versionDiffStatus === 'ahead_of_release' ? 'rocket_launch' : 'verified')) }}
                  </span>
                </div>
                <div>
                  <h3 class="font-headline-md text-base font-bold text-on-surface flex items-center gap-1.5">
                    {{ updateStore.errorMessage ? '更新检测提示' : (updateStore.hasUpdate ? '发现新版本' : (updateStore.versionDiffStatus === 'ahead_of_release' ? '当前为先行内测版' : '当前已是最新版')) }}
                  </h3>
                  <div class="flex items-center gap-2 mt-0.5 text-[11px] text-on-surface-variant">
                    <span>当前: v{{ currentVersion }}</span>
                    <span v-if="!updateStore.errorMessage && updateStore.hasUpdate && updateStore.latestRelease" class="text-primary font-semibold">
                      ➔ v{{ updateStore.latestRelease.version }}
                    </span>
                    <span v-else-if="!updateStore.errorMessage && updateStore.versionDiffStatus === 'ahead_of_release' && updateStore.latestRelease" class="text-cyan-400 font-semibold">
                      (领先官方 v{{ updateStore.latestRelease.version }})
                    </span>
                  </div>
                </div>
              </div>

              <!-- Close button (disabled during active downloading) -->
              <button
                v-if="updateStore.downloadStatus !== 'downloading'"
                type="button"
                @click="updateStore.closeModal"
                aria-label="关闭更新弹窗"
                class="w-8 h-8 rounded-full flex items-center justify-center bg-surface-container-high hover:bg-surface-bright text-on-surface-variant hover:text-on-surface border border-outline-variant/30 transition-colors"
              >
                <span class="material-symbols-outlined text-[18px]">close</span>
              </button>
            </div>
          </div>

          <!-- Modal Body Content -->
          <div class="p-5 flex-1 flex flex-col space-y-4 max-h-[60vh] overflow-y-auto overscroll-contain" style="overscroll-behavior: contain; -webkit-overflow-scrolling: touch;">
            <!-- 状态 A: 存在新版本，准备升级 -->
            <div v-if="updateStore.hasUpdate && updateStore.downloadStatus === 'idle'" class="space-y-3.5">
              <!-- Version metadata chips -->
              <div class="flex items-center justify-between text-xs px-3 py-2 rounded-xl bg-surface-container/60 border border-outline-variant/20">
                <span class="text-on-surface-variant flex items-center gap-1">
                  <span class="material-symbols-outlined text-[14px]">calendar_today</span>
                  {{ updateStore.latestRelease?.publishedAt || '今日更新' }}
                </span>
                <span class="text-primary font-mono font-medium">
                  {{ updateStore.latestRelease?.assetSizeText || '约 28 MB' }}
                </span>
              </div>

              <!-- Changelog Section -->
              <div>
                <h4 class="text-[11px] font-bold text-on-surface-variant tracking-wider uppercase mb-1.5 flex items-center gap-1">
                  <span class="material-symbols-outlined text-[13px] text-primary">auto_awesome</span>
                  更新亮点与优化日志
                </h4>
                <div class="p-3 rounded-2xl bg-surface-container-lowest/80 border border-outline-variant/15 text-xs text-on-surface-variant/90 leading-relaxed max-h-36 overflow-y-auto whitespace-pre-wrap font-sans">
                  {{ updateStore.latestRelease?.changelog }}
                </div>
              </div>
            </div>

            <!-- 状态 B: 正在高速下载中 -->
            <div v-else-if="updateStore.downloadStatus === 'downloading'" class="py-3 space-y-4">
              <div class="flex items-center justify-between">
                <span class="text-xs text-on-surface font-medium flex items-center gap-1.5">
                  <span class="w-2 h-2 rounded-full bg-primary animate-pulse"></span>
                  高速通道下载中...
                </span>
                <span class="text-sm font-mono font-bold text-primary">
                  {{ updateStore.downloadProgress.percent }}%
                </span>
              </div>

              <!-- Glowing Progress Bar -->
              <div class="w-full h-3 rounded-full bg-surface-container overflow-hidden p-0.5 border border-outline-variant/20">
                <div
                  class="h-full rounded-full bg-gradient-to-r from-teal-400 via-primary to-emerald-400 transition-all duration-200 shadow-sm shadow-primary/50"
                  :style="{ width: `${updateStore.downloadProgress.percent}%` }"
                ></div>
              </div>

              <!-- Progress Metadata -->
              <div class="flex items-center justify-between text-[11px] font-mono text-on-surface-variant">
                <span>{{ formatBytes(updateStore.downloadProgress.receivedBytes) }} / {{ formatBytes(updateStore.downloadProgress.totalBytes) }}</span>
                <span class="text-emerald-400 font-semibold">{{ updateStore.downloadProgress.message || '高速下载中' }}</span>
              </div>
            </div>

            <!-- 状态 C: 正在唤起系统安装 -->
            <div v-else-if="updateStore.downloadStatus === 'installing'" class="py-6 flex flex-col items-center justify-center text-center space-y-3">
              <div class="w-12 h-12 rounded-full border-2 border-primary border-t-transparent animate-spin flex items-center justify-center">
                <span class="material-symbols-outlined text-[20px] text-primary">install_mobile</span>
              </div>
              <h4 class="text-sm font-bold text-on-surface">安装包准备就绪</h4>
              <p class="text-xs text-on-surface-variant leading-relaxed max-w-[240px]">
                正在唤起系统安装器，请在稍后弹出的系统界面中点击「更新」确认安装。
              </p>
            </div>

            <!-- 状态 D: 等待授予未知应用安装权限 -->
            <div v-else-if="updateStore.downloadStatus === 'permission_required'" class="py-4 space-y-3">
              <div class="p-3 rounded-2xl bg-amber-500/10 border border-amber-500/20 text-xs text-amber-200 flex items-start gap-2">
                <span class="material-symbols-outlined text-[16px] text-amber-400 shrink-0 mt-0.5">security</span>
                <span>Android 系统安全保护：请在系统设置中允许本应用安装新版本，授予后即可自动安装。</span>
              </div>
            </div>

            <!-- 状态 E: 下载或网络异常 -->
            <div v-else-if="updateStore.downloadStatus === 'error' || updateStore.errorMessage" class="py-3 space-y-3">
              <div class="p-3 rounded-2xl bg-red-500/10 border border-red-500/20 text-xs text-red-200 flex items-start gap-2">
                <span class="material-symbols-outlined text-[16px] text-red-400 shrink-0 mt-0.5">error</span>
                <span>{{ updateStore.errorMessage || '下载过程出现异常，请稍后重试' }}</span>
              </div>
            </div>

            <!-- 状态 F1: 当前版本高于远端稳定发布版 (先行内测版 / 防降级保护) -->
            <div v-else-if="updateStore.versionDiffStatus === 'ahead_of_release'" class="py-4 space-y-3">
              <div class="flex flex-col items-center justify-center text-center space-y-2">
                <div class="w-12 h-12 rounded-full bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-400 mb-1 shadow-[0_0_15px_rgba(6,182,212,0.2)]">
                  <span class="material-symbols-outlined text-[26px]">rocket_launch</span>
                </div>
                <h4 class="text-sm font-bold text-on-surface">您正在体验先行内测版本</h4>
                <p class="text-xs text-on-surface-variant leading-relaxed">
                  当前安装版本 <span class="font-mono text-cyan-400 font-semibold">v{{ currentVersion }}</span> 领先于官方稳定发布版 <span class="font-mono text-on-surface font-semibold">v{{ updateStore.latestRelease?.version }}</span>。
                </p>
              </div>

              <div class="p-3.5 rounded-2xl bg-surface-container/60 border border-outline-variant/20 space-y-2.5 text-xs">
                <div class="flex items-start gap-2.5 text-on-surface-variant">
                  <span class="material-symbols-outlined text-[16px] text-amber-400 shrink-0 mt-0.5">verified_user</span>
                  <span class="leading-relaxed"><strong>防降级保护机制：</strong>系统已自动拦截降级。根据 Android 系统规范，无法向低版本覆盖安装，无需也不可降级。</span>
                </div>
                <div class="flex items-start gap-2.5 text-on-surface-variant">
                  <span class="material-symbols-outlined text-[16px] text-cyan-400 shrink-0 mt-0.5">bug_report</span>
                  <span class="leading-relaxed"><strong>内网测试更新：</strong>若需安装本地最新构建的测试包，可通过右侧「真机反馈」浮层一键下载最新 APK。</span>
                </div>
              </div>
            </div>

            <!-- 状态 F2: 当前已是最新版本 -->
            <div v-else class="py-6 flex flex-col items-center justify-center text-center space-y-2">
              <div class="w-12 h-12 rounded-full bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400 mb-1">
                <span class="material-symbols-outlined text-[26px]">check_circle</span>
              </div>
              <h4 class="text-sm font-bold text-on-surface">您正在使用最新版本</h4>
              <p class="text-xs text-on-surface-variant">
                当前版本 v{{ currentVersion }} 为最新发布版本，暂无可用更新。
              </p>
            </div>
          </div>

          <!-- Modal Footer Actions -->
          <div class="p-4 pt-3 bg-surface-container/40 border-t border-outline-variant/20 flex flex-col gap-2">
            <!-- 状态 A 动作按钮：立即在线更新 -->
            <template v-if="updateStore.hasUpdate && updateStore.downloadStatus === 'idle'">
              <button
                type="button"
                @click="updateStore.startDownloadAndInstall"
                class="w-full py-3 rounded-2xl bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-400 hover:to-teal-500 text-white font-medium text-sm flex items-center justify-center gap-2 shadow-lg shadow-emerald-900/30 active:scale-[0.98] transition-all"
              >
                <span class="material-symbols-outlined text-[18px]">download</span>
                <span>立即在线升级 (免跳转)</span>
              </button>
              <button
                type="button"
                @click="updateStore.closeModal"
                class="w-full py-2.5 rounded-2xl bg-surface-container-high hover:bg-surface-bright text-on-surface-variant text-xs font-medium transition-colors"
              >
                稍后再说
              </button>
            </template>

            <!-- 状态 B 动作按钮：下载中支持取消 -->
            <template v-else-if="updateStore.downloadStatus === 'downloading'">
              <button
                type="button"
                @click="updateStore.cancelDownload"
                class="w-full py-2.5 rounded-2xl bg-surface-container-high hover:bg-surface-bright text-on-surface-variant text-xs font-medium transition-colors"
              >
                取消下载
              </button>
            </template>

            <!-- 状态 D 动作按钮：去授权权限 -->
            <template v-else-if="updateStore.downloadStatus === 'permission_required'">
              <div class="space-y-2 w-full">
                <button
                  type="button"
                  @click="updateStore.openInstallPermissionSettings"
                  class="w-full py-3 rounded-2xl bg-amber-600 hover:bg-amber-500 text-white font-medium text-sm flex items-center justify-center gap-2 shadow-md active:scale-[0.98] transition-all"
                >
                  <span class="material-symbols-outlined text-[18px]">settings</span>
                  <span>前往系统开启安装权限</span>
                </button>
                <button
                  type="button"
                  @click="updateStore.startDownloadAndInstall"
                  class="w-full py-2.5 rounded-2xl bg-surface-container-high hover:bg-surface-bright text-primary font-medium text-xs flex items-center justify-center gap-1.5 border border-primary/30 transition-all active:scale-[0.98]"
                >
                  <span class="material-symbols-outlined text-[15px]">verified</span>
                  <span>我已开启权限，立即调起安装</span>
                </button>
              </div>
            </template>

            <!-- 状态 E 动作按钮：重试或浏览器下载 -->
            <template v-else-if="updateStore.downloadStatus === 'error' || updateStore.errorMessage">
              <button
                type="button"
                @click="updateStore.startDownloadAndInstall"
                class="w-full py-3 rounded-2xl bg-primary hover:bg-primary-hover text-on-primary font-medium text-sm flex items-center justify-center gap-2 shadow-md active:scale-[0.98] transition-all"
              >
                <span class="material-symbols-outlined text-[18px]">refresh</span>
                <span>重新尝试下载</span>
              </button>
              <button
                type="button"
                @click="fallbackToBrowser"
                class="w-full py-2 rounded-2xl bg-surface-container-high hover:bg-surface-bright text-on-surface-variant text-xs transition-colors flex items-center justify-center gap-1"
              >
                <span class="material-symbols-outlined text-[14px]">open_in_browser</span>
                <span>在外部浏览器中下载</span>
              </button>
            </template>

            <!-- 状态 F1 动作按钮：先行版确认 -->
            <template v-else-if="updateStore.versionDiffStatus === 'ahead_of_release'">
              <button
                type="button"
                @click="updateStore.closeModal"
                class="w-full py-3 rounded-2xl bg-gradient-to-r from-cyan-600 to-teal-600 hover:from-cyan-500 hover:to-teal-500 text-white font-medium text-sm flex items-center justify-center gap-1.5 shadow-md active:scale-[0.98] transition-all"
              >
                <span class="material-symbols-outlined text-[18px]">verified</span>
                <span>我知道了 (继续体验先行版)</span>
              </button>
            </template>

            <!-- 状态 F2 动作按钮：最新稳定版关闭 -->
            <template v-else>
              <button
                type="button"
                @click="updateStore.closeModal"
                class="w-full py-3 rounded-2xl bg-surface-container-high hover:bg-surface-bright text-on-surface font-medium text-sm transition-colors active:scale-[0.98]"
              >
                我知道了
              </button>
            </template>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { computed } from 'vue';
import { useUpdateStore } from '@/stores/updateStore.js';
import { useScrollLock } from '@/composables/useScrollLock.js';
import { APP_VERSION } from '@/config/version.js';
import { formatBytes } from '@/services/updateService.js';
import { openExternalUrl } from '@/utils/appLauncher.js';

const updateStore = useUpdateStore();

// 彻底杜绝底层页面背景滚动穿透
useScrollLock(() => updateStore.isModalOpen);
const currentVersion = computed(() => APP_VERSION);

function onBackdropClick() {
  if (updateStore.downloadStatus !== 'downloading') {
    updateStore.closeModal();
  }
}

function fallbackToBrowser() {
  const url = updateStore.latestRelease?.rawDownloadUrl || updateStore.latestRelease?.htmlUrl;
  if (url) {
    openExternalUrl(url);
  }
  updateStore.closeModal();
}
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.25s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

@keyframes modalIn {
  from {
    opacity: 0;
    transform: scale(0.95) translateY(8px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

.animate-modal-in {
  animation: modalIn 0.22s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}
</style>
