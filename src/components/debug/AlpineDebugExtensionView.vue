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
        flex-shrink: 0;
      }
      .dot-indicator.dot-locked {
        background: #ef4444;
        box-shadow: 0 0 8px #ef4444;
      }
      .platform-chip, .auth-chip {
        font-size: 10px;
        font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
        padding: 2px 8px;
        border-radius: 9999px;
      }
      .platform-chip {
        background: rgba(78, 222, 163, 0.12);
        color: var(--af-primary, #4edea3);
        border: 1px solid rgba(78, 222, 163, 0.3);
      }
      .auth-chip.chip-locked {
        background: rgba(239, 68, 68, 0.15);
        color: #f87171;
        border: 1px solid rgba(239, 68, 68, 0.3);
      }
      .auth-chip.chip-ok {
        background: rgba(16, 185, 129, 0.15);
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.3);
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
      .btn-link.danger {
        color: #f87171;
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
      .locked-warning-box {
        background: rgba(239, 68, 68, 0.1);
        border: 1px solid rgba(239, 68, 68, 0.25);
        border-radius: 10px;
        padding: 10px 12px;
        display: flex;
        flex-direction: column;
        gap: 8px;
      }
      .locked-title {
        font-size: 11px;
        font-weight: 700;
        color: #fca5a5;
        display: flex;
        align-items: center;
        gap: 4px;
      }
      .locked-desc {
        font-size: 11px;
        color: #e5e7eb;
        line-height: 1.5;
      }
      .btn-github-issue {
        width: 100%;
        background: #24292e;
        border: 1px solid rgba(255, 255, 255, 0.15);
        color: #fff;
        border-radius: 8px;
        padding: 8px 12px;
        font-size: 11px;
        font-weight: 600;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 6px;
      }
      .btn-github-issue:hover {
        background: #2f363d;
      }
      .info-notice {
        font-size: 10px;
        color: #9ca3af;
        line-height: 1.4;
        background: rgba(255, 255, 255, 0.03);
        border-radius: 8px;
        padding: 8px;
      }
    </component>

    <!-- 1. 开发者授权与访问控制 (解决 Point 3.1 & 3.2: 密钥输入 + 自动持久化 + 受限引导) -->
    <section class="ext-card">
      <div class="card-title-row">
        <span class="card-title">
          <span class="dot-indicator" :class="{ 'dot-locked': !debugStore.isAuthorized }"></span>
          开发者授权与访问控制
        </span>
        <span class="auth-chip" :class="debugStore.isAuthorized ? 'chip-ok' : 'chip-locked'">
          {{ debugStore.isAuthorized ? '● 已授权' : '▲ 未授权受限' }}
        </span>
      </div>

      <!-- 未授权锁定屏障提示 -->
      <div v-if="!debugStore.isAuthorized" class="locked-warning-box">
        <div class="locked-title">
          <span>🔒 核心联调通道受限保护</span>
        </div>
        <div class="locked-desc">
          当前通道直接与开发者本机的 AI 自愈哨兵实时通讯，仅供内部协同测试使用。普通用户如遇到体验缺陷或山峰数据建议，请前往官方 GitHub 提交反馈。
        </div>
        <button type="button" @click="openGitHubIssues" class="btn-github-issue">
          <svg class="w-3.5 h-3.5 fill-current" viewBox="0 0 24 24" width="14" height="14">
            <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/>
          </svg>
          <span>前往 GitHub Issues 提交问题</span>
        </button>
      </div>

      <!-- 口令输入与自动保存 (输入即刻存入当前设备 localStorage，下次免输) -->
      <div class="field-group">
        <div class="field-header">
          <span>开发者配对密钥 (输入自动持久化)</span>
          <button v-if="debugStore.isAuthorized" type="button" @click="handleClearAccessKey" class="btn-link danger">
            解除配对
          </button>
        </div>
        <input
          v-model="inputAccessKey"
          type="password"
          class="ext-input"
          placeholder="输入开发者专属密钥解锁联调通道"
          @input="handleAccessKeyInput"
        />
        <div class="info-notice">
          💡 密钥仅保存在当前设备，绝不上库或打包入包；开发机未配置时启动 DevServer 会在控制台打印临时配对码。
        </div>
      </div>
    </section>

    <!-- 2. 穿透与哨兵通信诊断 (仅配置通信与测试，彻底移除冗余的 APK 下载) -->
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
          <span>穿透通信基地址 (输入自动保存)</span>
          <button type="button" @click="resetTunnelUrl" class="btn-link">重置默认</button>
        </div>
        <div class="input-with-action">
          <input
            v-model="inputTunnelUrl"
            type="text"
            class="ext-input"
            placeholder="https://your-tunnel.cpolar.top"
            @input="handleTunnelUrlInput"
          />
          <button
            type="button"
            @click="handleTestTunnel"
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

    <!-- 3. 发布与架构原则公约说明 -->
    <section class="ext-card">
      <div class="card-title-row">
        <span class="card-title">
          <span class="dot-indicator"></span>
          分发架构与网络解耦说明
        </span>
      </div>
      <div class="info-notice">
        📌 <strong>网络流向解耦规范</strong>：<br/>
        1. <strong>安装包更新与下载</strong>：统一由主应用关于页/更新弹窗通过 GitHub Releases（及加速镜像）分发，本面板已彻底解耦 APK 下载；<br/>
        2. <strong>AI 反馈与实时哨兵</strong>：仅用于开发机实时排查，走上方配置的内网穿透通道。
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue';
import { useDebugStore } from '@/stores/debugStore.js';
import { DEFAULT_CPOLAR_TUNNEL } from '@/config/version.js';
import { openExternalUrl } from '@/utils/appLauncher.js';

const GITHUB_ISSUES_URL = 'https://github.com/lylyuanliang/weekly-mountain/issues';

const debugStore = useDebugStore();
const inputTunnelUrl = ref(debugStore.tunnelUrl);
const inputAccessKey = ref(debugStore.accessKey);

watch(
  () => debugStore.tunnelUrl,
  (val) => {
    inputTunnelUrl.value = val;
  }
);

watch(
  () => debugStore.accessKey,
  (val) => {
    inputAccessKey.value = val;
  }
);

function handleTunnelUrlInput() {
  debugStore.setTunnelUrl(inputTunnelUrl.value);
}

function handleAccessKeyInput() {
  debugStore.setAccessKey(inputAccessKey.value);
}

function handleClearAccessKey() {
  inputAccessKey.value = '';
  debugStore.clearAccessKey();
}

function resetTunnelUrl() {
  inputTunnelUrl.value = DEFAULT_CPOLAR_TUNNEL;
  debugStore.setTunnelUrl(DEFAULT_CPOLAR_TUNNEL);
}

async function handleTestTunnel() {
  debugStore.setTunnelUrl(inputTunnelUrl.value);
  await debugStore.testTunnelHealth();
}

function openGitHubIssues() {
  openExternalUrl(GITHUB_ISSUES_URL);
}
</script>
