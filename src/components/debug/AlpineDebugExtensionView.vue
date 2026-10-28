<template>
  <div class="alpine-ext-root">
    <component is="style">
      .alpine-ext-root {
        display: flex;
        flex-direction: column;
        gap: 14px;
        font-family: inherit;
        color: var(--af-text-main, #f3f4f6);
        box-sizing: border-box;
      }
      .alpine-ext-root * {
        box-sizing: border-box;
      }
      .ext-card {
        background: var(--af-bg-surface, #181f2a);
        border: 1px solid var(--af-border, rgba(255, 255, 255, 0.08));
        border-radius: var(--af-radius, 12px);
        padding: 14px;
        display: flex;
        flex-direction: column;
        gap: 12px;
      }
      .card-title-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
      }
      .card-title {
        font-size: 13px;
        font-weight: 700;
        display: flex;
        align-items: center;
        gap: 6px;
        color: var(--af-text-main, #fff);
      }
      .dot-indicator {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: var(--af-primary, #4edea3);
        box-shadow: 0 0 8px var(--af-primary, #4edea3);
        display: inline-block;
      }
      .platform-chip, .version-chip {
        font-size: 10px;
        font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
        padding: 2px 8px;
        border-radius: 9999px;
        background: rgba(78, 222, 163, 0.12);
        color: var(--af-primary, #4edea3);
        border: 1px solid rgba(78, 222, 163, 0.3);
      }
      .field-group {
        display: flex;
        flex-direction: column;
        gap: 8px;
      }
      .field-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 11px;
        color: var(--af-text-muted, #9ca3af);
      }
      .btn-link {
        background: none;
        border: none;
        color: var(--af-primary, #4edea3);
        font-size: 11px;
        cursor: pointer;
        padding: 0;
      }
      .btn-link:hover {
        text-decoration: underline;
      }
      .input-with-action {
        display: flex;
        gap: 8px;
      }
      .ext-input {
        flex: 1;
        background: var(--af-bg-base, #11141b);
        border: 1px solid var(--af-border, rgba(255, 255, 255, 0.1));
        border-radius: 8px;
        padding: 8px 12px;
        font-size: 12px;
        font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
        color: var(--af-text-main, #fff);
        outline: none;
      }
      .ext-input:focus {
        border-color: var(--af-primary, #4edea3);
      }
      .btn-action {
        background: var(--af-bg-surface, #1e2430);
        border: 1px solid rgba(78, 222, 163, 0.3);
        color: var(--af-primary, #4edea3);
        border-radius: 8px;
        padding: 0 14px;
        font-size: 12px;
        font-weight: 600;
        cursor: pointer;
      }
      .status-msg {
        font-size: 11px;
        color: #f59e0b;
      }
      .status-msg.status-ok {
        color: var(--af-primary, #4edea3);
      }
      .btn-primary {
        width: 100%;
        background: var(--af-primary, #4edea3);
        color: #0b0e14;
        border: none;
        border-radius: 8px;
        padding: 10px 14px;
        font-size: 13px;
        font-weight: 700;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 6px;
        transition: opacity 0.15s;
      }
      .btn-primary:disabled {
        opacity: 0.6;
        cursor: not-allowed;
      }
      .error-msg {
        padding: 8px 12px;
        background: rgba(239, 68, 68, 0.15);
        border: 1px solid rgba(239, 68, 68, 0.3);
        color: #f87171;
        border-radius: 8px;
        font-size: 11px;
      }
      .update-card {
        background: var(--af-bg-base, #11141b);
        border: 1px solid var(--af-border, rgba(255, 255, 255, 0.08));
        border-radius: 10px;
        padding: 12px;
        display: flex;
        flex-direction: column;
        gap: 10px;
      }
      .update-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
      }
      .update-version {
        font-size: 12px;
        font-weight: 700;
        color: var(--af-text-main, #fff);
      }
      .update-size {
        font-size: 11px;
        color: var(--af-text-muted, #9ca3af);
        font-family: monospace;
      }
      .changelog-list {
        padding-left: 18px;
        margin: 0;
        font-size: 11px;
        color: var(--af-text-muted, #9ca3af);
        line-height: 1.6;
      }
      .btn-download {
        width: 100%;
        background: linear-gradient(135deg, #10b981, #0d9488);
        color: #fff;
        border: none;
        border-radius: 8px;
        padding: 10px;
        font-size: 12px;
        font-weight: 700;
        cursor: pointer;
      }
      .download-tip {
        font-size: 10px;
        color: var(--af-text-muted, #6b7280);
        text-align: center;
        margin: 4px 0 0 0;
      }
      .progress-box {
        background: rgba(78, 222, 163, 0.08);
        border: 1px solid rgba(78, 222, 163, 0.25);
        border-radius: 8px;
        padding: 10px;
        display: flex;
        flex-direction: column;
        gap: 6px;
      }
      .progress-header, .progress-footer {
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 11px;
      }
      .progress-percent {
        font-weight: 700;
        color: var(--af-primary, #4edea3);
        font-family: monospace;
      }
      .progress-track {
        height: 6px;
        width: 100%;
        background: rgba(0, 0, 0, 0.4);
        border-radius: 9999px;
        overflow: hidden;
      }
      .progress-bar {
        height: 100%;
        background: var(--af-primary, #4edea3);
        border-radius: 9999px;
        transition: width 0.15s ease;
      }
      .btn-cancel {
        background: none;
        border: none;
        color: #f59e0b;
        font-size: 10px;
        cursor: pointer;
        padding: 0;
      }
      .install-ready {
        padding: 10px;
        background: rgba(16, 185, 129, 0.15);
        border: 1px solid rgba(16, 185, 129, 0.3);
        color: #34d399;
        font-size: 12px;
        border-radius: 8px;
        text-align: center;
      }
      .ext-footer {
        text-align: center;
        font-size: 10px;
        color: var(--af-text-muted, #6b7280);
        padding-top: 4px;
      }
    </component>

    <!-- 1. 穿透通信诊断 -->
    <section class="ext-card">
      <div class="card-title-row">
        <span class="card-title">
          <span class="dot-indicator"></span>
          穿透与通信诊断
        </span>
        <span class="platform-chip">
          {{ debugStore.isCapacitorNative ? 'Android 原生容器' : 'Web 移动端' }}
        </span>
      </div>

      <div class="field-group">
        <div class="field-header">
          <span>穿透通信基地址</span>
          <button type="button" @click="resetTunnelUrl" class="btn-link">重置默认</button>
        </div>
        <div class="input-with-action">
          <input
            v-model="inputTunnelUrl"
            type="text"
            class="ext-input"
            placeholder="https://your-tunnel-domain.cpolar.top"
          />
          <button
            type="button"
            @click="handleSaveAndTestTunnel"
            :disabled="debugStore.tunnelStatus.checking"
            class="btn-action"
          >
            {{ debugStore.tunnelStatus.checking ? '测试中...' : '测试' }}
          </button>
        </div>

        <div v-if="debugStore.tunnelStatus.msg" class="status-msg" :class="{ 'status-ok': debugStore.tunnelStatus.healthy }">
          {{ debugStore.tunnelStatus.healthy ? '● 穿透通道连通正常' : '▲ ' + debugStore.tunnelStatus.msg }}
        </div>
      </div>
    </section>

    <!-- 2. 内测更新与构建管理 -->
    <section class="ext-card">
      <div class="card-title-row">
        <span class="card-title">
          <span class="dot-indicator"></span>
          内测更新与构建管理
        </span>
        <span class="version-chip">v{{ APP_VERSION }}</span>
      </div>

      <div class="field-group">
        <button
          type="button"
          @click="handleCheckUpdate"
          :disabled="debugStore.isCheckingUpdate"
          class="btn-primary"
        >
          {{ debugStore.isCheckingUpdate ? '正在检测远端构建产物...' : '⚡ 检查在线更新' }}
        </button>

        <div v-if="debugStore.updateError" class="error-msg">
          {{ debugStore.updateError }}
        </div>

        <!-- 发现新构建卡片 -->
        <div v-if="debugStore.updateInfo" class="update-card">
          <div class="update-header">
            <span class="update-version">
              {{ hasNewVersion ? `发现新构建: v${debugStore.updateInfo.latestVersion}` : '已是最新构建版本' }}
            </span>
            <span class="update-size">{{ debugStore.updateInfo.fileSize }}</span>
          </div>

          <ul v-if="debugStore.updateInfo.changelog?.length" class="changelog-list">
            <li v-for="(log, idx) in debugStore.updateInfo.changelog" :key="idx">{{ log }}</li>
          </ul>

          <!-- 原生流式下载进度条 -->
          <div v-if="debugStore.downloadStatus === 'downloading'" class="progress-box">
            <div class="progress-header">
              <span>正在应用内极速下载 APK...</span>
              <span class="progress-percent">{{ debugStore.downloadProgress.percent }}%</span>
            </div>
            <div class="progress-track">
              <div class="progress-bar" :style="{ width: `${debugStore.downloadProgress.percent}%` }"></div>
            </div>
            <div class="progress-footer">
              <span>{{ debugStore.downloadProgress.speed || '连接中...' }}</span>
              <button type="button" @click="debugStore.cancelDownloadApk" class="btn-cancel">取消下载</button>
            </div>
          </div>

          <div v-else-if="debugStore.downloadStatus === 'installing'" class="install-ready">
            <span>🚀 下载完成，正在唤起手机系统安装界面...</span>
          </div>

          <!-- 一键在线下载升级按钮 -->
          <div v-else class="action-box">
            <div v-if="debugStore.downloadStatus === 'error'" style="margin-bottom: 8px; font-size: 11px; color: #fbbf24; text-align: center;">
              ⚠️ {{ debugStore.downloadProgress.message || '网络连接中断' }}
            </div>
            <button type="button" @click="handleDownloadApk" class="btn-download">
              {{
                debugStore.downloadProgress.percent > 0 && debugStore.downloadProgress.percent < 100
                  ? `📥 继续断点续传下载 (${debugStore.downloadProgress.percent}%)`
                  : (hasNewVersion ? '📥 一键在 App 内免跳转下载并升级' : '🔄 重新下载当前最新 APK')
              }}
            </button>
            <p class="download-tip">原生流式下载至手机并直接唤起安装，支持锁屏与切屏断点续传</p>
          </div>
        </div>
      </div>
    </section>

    <footer class="ext-footer">
      成都周边50座山 · Alpine Explorer 内测联调模式
    </footer>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue';
import { useDebugStore } from '@/stores/debugStore.js';
import { APP_VERSION, BUILD_CODE, DEFAULT_CPOLAR_TUNNEL } from '@/config/version.js';

const debugStore = useDebugStore();
const inputTunnelUrl = ref(debugStore.tunnelUrl);

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

onMounted(() => {
  debugStore.testTunnelHealth();
  debugStore.checkUpdate();
});
</script>
