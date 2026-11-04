<template>
  <div class="dev-apk-root">
    <component is="style">
      .dev-apk-root {
        display: flex;
        flex-direction: column;
        gap: 12px;
        font-family: inherit;
        color: var(--af-text-main, #f3f4f6);
        padding: 4px 0;
        box-sizing: border-box;
      }
      .dev-apk-root * {
        box-sizing: border-box;
      }
      .dev-card {
        background: var(--af-bg-surface, #181f2a);
        border: 1px solid var(--af-border, rgba(255, 255, 255, 0.08));
        border-radius: var(--af-radius, 12px);
        padding: 14px;
        display: flex;
        flex-direction: column;
        gap: 10px;
      }
      .card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
      }
      .card-title {
        font-size: 13px;
        font-weight: 700;
        display: flex;
        align-items: center;
        gap: 8px;
        color: var(--af-text-main, #fff);
      }
      .dot-indicator {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #6b7280;
        display: inline-block;
        flex-shrink: 0;
      }
      .dot-indicator.dot-active {
        background: var(--af-primary, #4edea3);
        box-shadow: 0 0 8px var(--af-primary, #4edea3);
      }
      .chip-badge, .chip-version {
        font-size: 10px;
        font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
        padding: 2px 8px;
        border-radius: 9999px;
        background: rgba(255, 255, 255, 0.06);
        color: var(--af-text-muted, #9ca3af);
        border: 1px solid rgba(255, 255, 255, 0.1);
      }
      .chip-version {
        background: rgba(78, 222, 163, 0.12);
        color: var(--af-primary, #4edea3);
        border-color: rgba(78, 222, 163, 0.3);
      }
      .tunnel-row {
        display: flex;
        flex-direction: column;
        gap: 4px;
        font-size: 11px;
      }
      .field-label {
        color: var(--af-text-muted, #9ca3af);
      }
      .tunnel-val {
        color: var(--af-text-main, #e5e7eb);
        word-break: break-all;
        background: rgba(0, 0, 0, 0.25);
        padding: 6px 8px;
        border-radius: 6px;
        font-size: 11px;
      }
      .text-mono {
        font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
      }
      .text-truncate {
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }
      .btn-refresh {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid var(--af-border, rgba(255, 255, 255, 0.1));
        color: var(--af-text-main, #fff);
        border-radius: 8px;
        padding: 8px 12px;
        font-size: 12px;
        font-weight: 600;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 6px;
        transition: all 0.2s ease;
      }
      .btn-refresh:hover:not(:disabled) {
        background: rgba(255, 255, 255, 0.1);
        border-color: var(--af-primary, #4edea3);
      }
      .btn-refresh:disabled {
        opacity: 0.6;
        cursor: not-allowed;
      }
      .spinner {
        width: 12px;
        height: 12px;
        border: 2px solid rgba(255, 255, 255, 0.2);
        border-top-color: var(--af-primary, #4edea3);
        border-radius: 50%;
        animation: af-spin 0.8s linear infinite;
        display: inline-block;
      }
      @keyframes af-spin {
        to { transform: rotate(360deg); }
      }
      .error-banner {
        background: rgba(239, 68, 68, 0.1);
        border: 1px solid rgba(239, 68, 68, 0.25);
        color: #fca5a5;
        border-radius: 8px;
        padding: 8px 10px;
        font-size: 11px;
        line-height: 1.4;
      }
      .error-tip {
        color: #d1d5db;
        font-size: 10px;
        margin-top: 4px;
      }
      .artifact-card {
        border-color: rgba(78, 222, 163, 0.25);
      }
      .artifact-meta-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 8px;
        background: rgba(0, 0, 0, 0.2);
        padding: 10px;
        border-radius: 8px;
      }
      .meta-item {
        display: flex;
        flex-direction: column;
        gap: 2px;
      }
      .meta-item.full-width {
        grid-column: span 2;
      }
      .meta-label {
        font-size: 10px;
        color: var(--af-text-muted, #9ca3af);
      }
      .meta-value {
        font-size: 12px;
        font-weight: 600;
        color: var(--af-text-main, #f3f4f6);
      }
      .action-buttons {
        display: flex;
        flex-direction: column;
        gap: 8px;
        margin-top: 4px;
      }
      .btn-download {
        border-radius: 8px;
        padding: 10px;
        font-size: 12px;
        font-weight: 700;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 6px;
        border: 1px solid transparent;
        transition: all 0.2s ease;
      }
      .btn-download.primary {
        background: var(--af-primary, #4edea3);
        color: #0d1117;
      }
      .btn-download.primary:hover {
        filter: brightness(1.1);
      }
      .btn-download.secondary {
        background: rgba(255, 255, 255, 0.05);
        border-color: rgba(255, 255, 255, 0.15);
        color: var(--af-text-main, #f3f4f6);
      }
      .btn-download.secondary:hover {
        background: rgba(255, 255, 255, 0.1);
      }
      .btn-copy-link {
        background: none;
        border: none;
        color: var(--af-primary, #4edea3);
        font-size: 11px;
        cursor: pointer;
        padding: 4px 0;
        text-align: center;
      }
      .btn-copy-link:hover {
        text-decoration: underline;
      }
      .locked-card {
        text-align: center;
        align-items: center;
        padding: 24px 16px;
        gap: 12px;
      }
      .lock-icon {
        font-size: 32px;
      }
      .lock-title {
        font-size: 14px;
        font-weight: 700;
        color: var(--af-text-main, #fff);
      }
      .lock-desc {
        font-size: 12px;
        color: var(--af-text-muted, #9ca3af);
        line-height: 1.5;
        max-width: 280px;
      }
      .btn-action {
        background: var(--af-primary, #4edea3);
        color: #0d1117;
        border: none;
        border-radius: 8px;
        padding: 8px 18px;
        font-size: 12px;
        font-weight: 700;
        cursor: pointer;
      }
      .notice-card {
        background: rgba(255, 255, 255, 0.02);
        border: 1px dashed rgba(255, 255, 255, 0.1);
      }
      .notice-title {
        font-size: 11px;
        font-weight: 700;
        color: var(--af-text-muted, #9ca3af);
      }
      .notice-text {
        font-size: 10px;
        color: var(--af-text-muted, #9ca3af);
        line-height: 1.6;
      }
    </component>

    <!-- 1. 未授权状态防护 -->
    <div v-if="!authorized" class="dev-card locked-card">
      <div class="lock-icon">🔒</div>
      <div class="lock-title">开发机本地联调受限</div>
      <div class="lock-desc">
        本地构建 APK 直连下载专为开发者与内部测试设计。请先前往<strong>「⚙️ 设置」</strong>面板输入开发者配对密钥以解锁访问。
      </div>
      <button type="button" @click="goToSettings" class="btn-action">
        前往设置解锁
      </button>
    </div>

    <!-- 2. 已授权状态：开发机联调包分发 -->
    <template v-else>
      <!-- 开发机穿透与连接状态 -->
      <section class="dev-card">
        <div class="card-header">
          <div class="card-title">
            <span class="dot-indicator" :class="{ 'dot-active': isConnected }"></span>
            <span>开发机直连通道</span>
          </div>
          <span class="chip-badge">{{ isNativeApp ? 'Android 原生' : 'Web 环境' }}</span>
        </div>

        <div class="tunnel-row">
          <span class="field-label">当前穿透基地址：</span>
          <span class="tunnel-val text-mono">{{ devServerUrl || '未配置穿透地址' }}</span>
        </div>

        <button
          type="button"
          @click="checkDevArtifacts"
          :disabled="loading"
          class="btn-refresh"
        >
          <span v-if="loading" class="spinner"></span>
          <span>{{ loading ? '检测开发机产物中...' : '🔄 刷新开发机最新构建' }}</span>
        </button>

        <div v-if="fetchError" class="error-banner">
          ⚠️ 无法连接开发机：{{ fetchError }}
          <div class="error-tip">请确认开发机 `npm run dev` 正常运行且内网穿透已连通。</div>
        </div>
      </section>

      <!-- 本地构建产物详情卡片 -->
      <section v-if="artifactInfo" class="dev-card artifact-card">
        <div class="card-header">
          <div class="card-title">
            <span>📦 本地最新产物 (免发布)</span>
          </div>
          <span class="chip-version text-mono">v{{ artifactInfo.latestVersion || '0.3.0' }}</span>
        </div>

        <div class="artifact-meta-grid">
          <div class="meta-item">
            <span class="meta-label">产物名称</span>
            <span class="meta-value text-mono text-truncate">{{ artifactInfo.apkName || 'app-debug.apk' }}</span>
          </div>
          <div class="meta-item">
            <span class="meta-label">文件体积</span>
            <span class="meta-value">{{ artifactInfo.fileSize || '未知' }}</span>
          </div>
          <div class="meta-item full-width">
            <span class="meta-label">最后编译时间</span>
            <span class="meta-value text-mono">{{ artifactInfo.updateTime || '刚刚' }}</span>
          </div>
        </div>

        <div class="action-buttons">
          <button
            type="button"
            @click="downloadApk('debug')"
            class="btn-download primary"
          >
            <span>⬇️ 下载本地 Debug APK</span>
          </button>
          <button
            type="button"
            @click="downloadApk('release')"
            class="btn-download secondary"
          >
            <span>⬇️ 下载本地 Release APK</span>
          </button>
        </div>

        <button type="button" @click="copyDownloadLink" class="btn-copy-link">
          {{ copied ? '✅ 已复制下载链接到剪贴板' : '📋 复制开发机直连下载链接' }}
        </button>
      </section>

      <!-- 架构分流说明 -->
      <section class="dev-card notice-card">
        <div class="notice-title">💡 双层分发架构说明</div>
        <div class="notice-text">
          1. <strong>开发机直连 (当前)</strong>：直接读取本机 `android/app/build/outputs/apk/` 与 `releases/`，本地执行 `gradlew assembleDebug` 后手机秒级下载验证，无需 push 代码与等待 CI；<br/>
          2. <strong>正式发布更新</strong>：面向全网用户，统一经由 GitHub Releases 及 CDN 加速分发，请前往个人中心版本详情下载。
        </div>
      </section>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { getApiBase, isAuthorized, openFeedbackModal } from '@lylyuanliang/agent-feedback-client';
import { openExternalUrl } from '@/utils/appLauncher.js';

const authorized = ref(false);
const isConnected = ref(false);
const loading = ref(false);
const fetchError = ref('');
const devServerUrl = ref('');
const artifactInfo = ref(null);
const copied = ref(false);
const isNativeApp = ref(typeof window !== 'undefined' && !!(window.Capacitor?.isNativePlatform?.()));

onMounted(() => {
  checkAuthAndLoad();
});

function checkAuthAndLoad() {
  authorized.value = isAuthorized();
  devServerUrl.value = getApiBase() || window.location.origin;
  if (authorized.value) {
    checkDevArtifacts();
  }
}

function goToSettings() {
  openFeedbackModal('settings');
}

async function checkDevArtifacts() {
  loading.value = true;
  fetchError.value = '';
  devServerUrl.value = getApiBase() || window.location.origin;

  const targetBase = devServerUrl.value.replace(/\/+$/, '');
  const updateUrl = `${targetBase}/api/app-update?t=${Date.now()}`;

  try {
    const res = await fetch(updateUrl, {
      method: 'GET',
      headers: { 'Accept': 'application/json' },
      signal: AbortSignal.timeout(8000)
    });

    if (!res.ok) {
      throw new Error(`HTTP ${res.status}`);
    }

    const data = await res.json();
    artifactInfo.value = data;
    isConnected.value = true;
  } catch (err) {
    console.warn('[DevApk] Failed to fetch dev artifacts:', err);
    fetchError.value = err.message || '网络超时或服务不可达';
    isConnected.value = false;
  } finally {
    loading.value = false;
  }
}

function downloadApk(variant = 'debug') {
  const targetBase = (devServerUrl.value || window.location.origin).replace(/\/+$/, '');
  const apkPath = variant === 'release' ? '/releases/weekly-mountain-latest-release.apk' : '/releases/weekly-mountain-latest-debug.apk';
  const downloadUrl = `${targetBase}${apkPath}`;

  if (isNativeApp.value) {
    openExternalUrl(downloadUrl);
  } else {
    const a = document.createElement('a');
    a.href = downloadUrl;
    a.download = `weekly-mountain-dev-${variant}.apk`;
    a.target = '_blank';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  }
}

async function copyDownloadLink() {
  const targetBase = (devServerUrl.value || window.location.origin).replace(/\/+$/, '');
  const url = `${targetBase}/releases/weekly-mountain-latest-debug.apk`;
  try {
    if (navigator?.clipboard?.writeText) {
      await navigator.clipboard.writeText(url);
    } else {
      const input = document.createElement('input');
      input.value = url;
      document.body.appendChild(input);
      input.select();
      document.execCommand('copy');
      document.body.removeChild(input);
    }
    copied.value = true;
    setTimeout(() => { copied.value = false; }, 2500);
  } catch {
    copied.value = false;
  }
}
</script>
