<template>
  <div class="dev-apk-root">
    <component is="style">
      .dev-apk-root {
        display: flex;
        flex-direction: column;
        gap: 12px;
        font-family: inherit;
        color: var(--af-text-main, #f3f4f6);
        padding: 4px 0 24px 0;
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
        flex-wrap: wrap;
        gap: 6px;
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
      .chip-badge, .chip-version, .chip-auth {
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
      .chip-auth {
        background: rgba(78, 222, 163, 0.15);
        color: var(--af-primary, #4edea3);
        border-color: rgba(78, 222, 163, 0.35);
      }
      .tunnel-row {
        display: flex;
        flex-direction: column;
        gap: 6px;
        font-size: 11px;
      }
      .tunnel-header-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
      }
      .field-label {
        color: var(--af-text-muted, #9ca3af);
        font-weight: 600;
      }
      .tunnel-val-wrapper {
        display: flex;
        align-items: center;
        justify-content: space-between;
        background: rgba(0, 0, 0, 0.25);
        padding: 6px 10px;
        border-radius: 6px;
        border: 1px solid rgba(255, 255, 255, 0.06);
        gap: 8px;
      }
      .tunnel-val {
        color: var(--af-text-main, #e5e7eb);
        word-break: break-all;
        font-size: 11px;
        flex: 1;
      }
      .tunnel-val.empty {
        color: #f59e0b;
        font-style: italic;
      }
      .btn-tunnel-edit {
        background: rgba(78, 222, 163, 0.1);
        border: 1px solid rgba(78, 222, 163, 0.3);
        color: var(--af-primary, #4edea3);
        font-size: 11px;
        padding: 2px 8px;
        border-radius: 4px;
        cursor: pointer;
        flex-shrink: 0;
      }
      .btn-tunnel-edit:hover {
        background: rgba(78, 222, 163, 0.2);
      }
      .tunnel-edit-box {
        display: flex;
        flex-direction: column;
        gap: 6px;
      }
      .tunnel-input {
        background: rgba(0, 0, 0, 0.35);
        border: 1px solid var(--af-primary, #4edea3);
        border-radius: 6px;
        color: #fff;
        padding: 8px 10px;
        font-size: 12px;
        outline: none;
        width: 100%;
      }
      .tunnel-actions {
        display: flex;
        justify-content: flex-end;
        gap: 8px;
      }
      .btn-tunnel-save {
        background: var(--af-primary, #4edea3);
        color: #0d1117;
        font-size: 11px;
        font-weight: 700;
        padding: 4px 12px;
        border-radius: 4px;
        border: none;
        cursor: pointer;
      }
      .btn-tunnel-cancel {
        background: rgba(255, 255, 255, 0.08);
        color: #9ca3af;
        font-size: 11px;
        padding: 4px 10px;
        border-radius: 4px;
        border: none;
        cursor: pointer;
      }
      .tunnel-hint {
        font-size: 10px;
        color: #f59e0b;
        line-height: 1.4;
        background: rgba(245, 158, 11, 0.08);
        border: 1px solid rgba(245, 158, 11, 0.2);
        padding: 6px 8px;
        border-radius: 6px;
      }
      .success-tip {
        font-size: 10px;
        color: var(--af-primary, #4edea3);
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
        will-change: transform;
        transform: translateZ(0);
      }
      @keyframes af-spin {
        to { transform: rotate(360deg) translateZ(0); }
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
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 10px 12px;
        background: rgba(0, 0, 0, 0.25);
        padding: 12px;
        border-radius: 8px;
        border: 1px solid rgba(255, 255, 255, 0.05);
      }
      .meta-item {
        display: flex;
        flex-direction: column;
        gap: 4px;
        min-width: 0;
        overflow: hidden;
      }
      .meta-item.full-width {
        grid-column: span 2;
      }
      .meta-label {
        font-size: 10px;
        color: var(--af-text-muted, #9ca3af);
        white-space: nowrap;
      }
      .meta-value {
        font-size: 12px;
        font-weight: 600;
        color: var(--af-text-main, #f3f4f6);
        min-width: 0;
      }
      .meta-value.highlight-size {
        color: var(--af-primary, #4edea3);
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
        padding: 20px 16px;
        gap: 12px;
      }
      .lock-icon {
        font-size: 28px;
      }
      .lock-title {
        font-size: 14px;
        font-weight: 700;
        color: var(--af-text-main, #fff);
      }
      .lock-desc {
        font-size: 11px;
        color: var(--af-text-muted, #9ca3af);
        line-height: 1.5;
        max-width: 320px;
      }
      .unlock-form {
        display: flex;
        flex-direction: column;
        gap: 8px;
        width: 100%;
        max-width: 320px;
        margin-top: 4px;
      }
      .auth-input {
        background: rgba(0, 0, 0, 0.35);
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 8px;
        color: #fff;
        padding: 9px 12px;
        font-size: 13px;
        outline: none;
        width: 100%;
        text-align: center;
      }
      .auth-input:focus {
        border-color: var(--af-primary, #4edea3);
      }
      .unlock-btns {
        display: flex;
        gap: 8px;
      }
      .btn-action {
        background: var(--af-primary, #4edea3);
        color: #0d1117;
        border: none;
        border-radius: 8px;
        padding: 8px 14px;
        font-size: 12px;
        font-weight: 700;
        cursor: pointer;
        flex: 1;
      }
      .btn-subaction {
        background: rgba(255, 255, 255, 0.08);
        border: 1px solid rgba(255, 255, 255, 0.15);
        color: var(--af-text-main, #fff);
        border-radius: 8px;
        padding: 8px 12px;
        font-size: 11px;
        cursor: pointer;
      }
      .auth-error-msg {
        color: #f87171;
        font-size: 11px;
      }
      .secret-hint {
        font-size: 10px;
        color: var(--af-text-muted, #9ca3af);
        line-height: 1.5;
        background: rgba(0, 0, 0, 0.2);
        padding: 6px 10px;
        border-radius: 6px;
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
      .btn-unbind {
        background: none;
        border: none;
        color: #9ca3af;
        font-size: 10px;
        cursor: pointer;
        text-decoration: underline;
        padding: 0;
      }
      .badge-tag {
        font-size: 9px;
        background: rgba(0, 0, 0, 0.4);
        color: var(--af-primary, #4edea3);
        padding: 1px 6px;
        border-radius: 9999px;
        font-weight: 600;
        margin-left: 4px;
        border: 1px solid rgba(78, 222, 163, 0.3);
      }
      .download-progress-box {
        background: rgba(0, 0, 0, 0.35);
        border: 1px solid var(--af-border, rgba(255, 255, 255, 0.12));
        border-radius: 8px;
        padding: 12px;
        display: flex;
        flex-direction: column;
        gap: 8px;
      }
      .progress-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
      }
      .progress-title {
        font-size: 12px;
        font-weight: 700;
        color: var(--af-text-main, #f3f4f6);
        display: flex;
        align-items: center;
        gap: 6px;
      }
      .pulse-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: var(--af-primary, #4edea3);
        box-shadow: 0 0 8px var(--af-primary, #4edea3);
        animation: pulse-ring 1.4s infinite;
      }
      .progress-percent {
        font-size: 13px;
        font-weight: 800;
        color: var(--af-primary, #4edea3);
      }
      .progress-track {
        width: 100%;
        height: 8px;
        background: rgba(255, 255, 255, 0.08);
        border-radius: 9999px;
        overflow: hidden;
      }
      .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, #10b981, var(--af-primary, #4edea3));
        border-radius: 9999px;
        transition: width 0.15s ease-out;
      }
      .progress-fill.pulse-animated {
        background: linear-gradient(90deg, #10b981, var(--af-primary, #4edea3), #38bdf8);
        background-size: 200% 100%;
        animation: progress-shimmer 2s linear infinite;
      }
      @keyframes progress-shimmer {
        0% { background-position: 200% 0; }
        100% { background-position: -200% 0; }
      }
      .progress-meta {
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 10px;
        color: var(--af-text-muted, #9ca3af);
      }
      .progress-msg {
        text-align: right;
        max-width: 60%;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }
      .progress-action-row {
        margin-top: 4px;
      }
      .btn-progress-action {
        width: 100%;
        padding: 8px 12px;
        border-radius: 6px;
        font-size: 11px;
        font-weight: 700;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 6px;
        border: none;
      }
      .btn-permission {
        background: #f59e0b;
        color: #0d1117;
      }
      .btn-install {
        background: var(--af-primary, #4edea3);
        color: #0d1117;
      }
      .btn-retry {
        background: #ef4444;
        color: #fff;
      }
      .progress-footer-actions {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-top: 2px;
        padding-top: 6px;
        border-top: 1px dashed rgba(255, 255, 255, 0.08);
      }
      .btn-sub-action {
        background: none;
        border: none;
        font-size: 10px;
        color: var(--af-text-muted, #9ca3af);
        cursor: pointer;
        padding: 2px 4px;
      }
      .btn-sub-action:hover {
        color: #fff;
      }
    </component>

    <!-- 1. 未授权状态防护卡片 (支持就地输入秘钥配对或跳转设置) -->
    <div v-if="!authorized" class="dev-card locked-card">
      <div class="lock-icon">🔒</div>
      <div class="lock-title">开发机本地联调受限</div>
      <div class="lock-desc">
        本地构建 APK 直连下载专为开发者与内部测试设计。请输入开发机配对密钥以解锁访问。
      </div>

      <div class="unlock-form">
        <input
          v-model="pairingSecretInput"
          type="password"
          class="auth-input text-mono"
          placeholder="输入开发机配对密钥 (wm-...)"
          @keyup.enter="handleUnlock"
        />
        <div class="unlock-btns">
          <button type="button" @click="handleUnlock" :disabled="authSubmitting" class="btn-action">
            {{ authSubmitting ? '验证中...' : '立即配对解锁' }}
          </button>
          <button type="button" @click="goToSettings" class="btn-subaction">
            ⚙️ 联调设置
          </button>
        </div>
        <div v-if="authError" class="auth-error-msg">⚠️ {{ authError }}</div>
      </div>

      <div class="secret-hint">
        💡 密钥生成并存放于电脑端开发机项目根目录：<br/>
        <code>scratch/.agent-feedback-secret</code>
      </div>
    </div>

    <!-- 2. 已授权状态：开发机联调包分发与直连穿透通道 -->
    <template v-else>
      <!-- 开发机穿透与连接状态 -->
      <section class="dev-card">
        <div class="card-header">
          <div class="card-title">
            <span class="dot-indicator" :class="{ 'dot-active': isConnected }"></span>
            <span>开发机直连通道</span>
          </div>
          <div style="display: flex; gap: 6px; align-items: center;">
            <span class="chip-auth">🟢 已配对</span>
            <span class="chip-badge">{{ isNativeApp ? 'Android 原生' : 'Web 环境' }}</span>
          </div>
        </div>

        <!-- 穿透基地址：支持就地修改与保存 -->
        <div class="tunnel-row">
          <div class="tunnel-header-row">
            <span class="field-label">当前穿透基地址：</span>
            <button
              v-if="!isEditingTunnel"
              type="button"
              @click="startEditTunnel"
              class="btn-tunnel-edit"
            >
              {{ devServerUrl ? '✏️ 修改地址' : '➕ 配置穿透' }}
            </button>
          </div>

          <!-- 编辑状态 -->
          <div v-if="isEditingTunnel" class="tunnel-edit-box">
            <input
              v-model="inputTunnelUrl"
              type="url"
              class="tunnel-input text-mono"
              placeholder="例如 https://xxxx.cpolar.top 或 http://192.168.1.xxx:5173"
              @keyup.enter="saveTunnelUrl"
            />
            <div class="tunnel-actions">
              <button type="button" @click="cancelEditTunnel" class="btn-tunnel-cancel">取消</button>
              <button type="button" @click="saveTunnelUrl" class="btn-tunnel-save">保存并应用</button>
            </div>
          </div>

          <!-- 展示状态 -->
          <div v-else class="tunnel-val-wrapper">
            <span class="tunnel-val text-mono" :class="{ empty: !devServerUrl }">
              {{ devServerUrl || '未配置穿透地址（手机真机无法直连 localhost）' }}
            </span>
          </div>

          <!-- 提示条 -->
          <div v-if="isNativeApp && (!devServerUrl || devServerUrl.includes('localhost'))" class="tunnel-hint">
            💡 手机真机无法访问开发机 localhost。请点击右上角「{{ devServerUrl ? '✏️ 修改地址' : '➕ 配置穿透' }}」填入内网穿透域名（如 cpolar/ngrok）或同一 WiFi 下的电脑局域网 IP（如 http://192.168.1.100:5173）。
          </div>
          <div v-if="saveSuccess" class="success-tip">✅ 穿透基地址已保存并同步至系统全局配置</div>
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
          <div class="error-tip">
            请确认：① 电脑端 `npm run dev` 正常运行；② 穿透地址已连通且端口正确。
          </div>
        </div>

        <div style="display: flex; justify-content: flex-end; margin-top: 2px;">
          <button type="button" @click="handleUnbind" class="btn-unbind">解除当前设备密钥配对</button>
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
          <div class="meta-item full-width">
            <span class="meta-label">产物包名</span>
            <span class="meta-value text-mono text-truncate" :title="artifactInfo.apkName">
              {{ artifactInfo.apkName || 'app-debug.apk' }}
            </span>
          </div>
          <div class="meta-item">
            <span class="meta-label">文件体积</span>
            <span class="meta-value text-mono highlight-size">{{ artifactInfo.fileSize || '未知' }}</span>
          </div>
          <div class="meta-item">
            <span class="meta-label">最后编译时间</span>
            <span class="meta-value text-mono">{{ artifactInfo.updateTime || '刚刚' }}</span>
          </div>
        </div>

        <!-- 下载操作区：未在下载中时展示下载按钮 -->
        <div v-if="downloadState.status === 'idle'" class="action-buttons">
          <button
            type="button"
            @click="downloadApk('debug')"
            class="btn-download primary"
          >
            <span>⬇️ 下载本地 Debug APK</span>
            <span v-if="isNativeApp" class="badge-tag">应用内续传</span>
          </button>
          <button
            type="button"
            @click="downloadApk('release')"
            class="btn-download secondary"
          >
            <span>⬇️ 下载本地 Release APK</span>
          </button>
        </div>

        <!-- 应用内实时下载进度与状态控制卡片 -->
        <div v-else class="download-progress-box">
          <div class="progress-header">
            <div class="progress-title">
              <span class="pulse-dot"></span>
              <span v-if="downloadState.status === 'downloading'">
                应用内下载中 ({{ downloadState.variant === 'release' ? 'Release' : 'Debug' }})
              </span>
              <span v-else-if="downloadState.status === 'installing'">
                正在调起系统安装器...
              </span>
              <span v-else-if="downloadState.status === 'permission_required'">
                待授予未知应用安装权限
              </span>
              <span v-else-if="downloadState.status === 'completed'">
                安装包下载完成
              </span>
              <span v-else-if="downloadState.status === 'error'">
                下载中断
              </span>
            </div>
            <span class="progress-percent text-mono">{{ downloadState.percent }}%</span>
          </div>

          <!-- 进度条轨道 -->
          <div class="progress-track">
            <div
              class="progress-fill"
              :style="{ width: `${Math.max(2, Math.min(100, downloadState.percent))}%` }"
              :class="{ 'pulse-animated': downloadState.status === 'downloading' }"
            ></div>
          </div>

          <!-- 统计信息与状态消息 -->
          <div class="progress-meta">
            <span class="progress-bytes text-mono">
              {{ formatBytes(downloadState.receivedBytes) }} / {{ formatBytes(downloadState.totalBytes) }}
            </span>
            <span class="progress-msg">{{ downloadState.message || '支持断点续传与切屏后台保持' }}</span>
          </div>

          <!-- 异常与权限引导操作 -->
          <div v-if="downloadState.status === 'permission_required'" class="progress-action-row">
            <button type="button" @click="openPermissionSettings" class="btn-progress-action btn-permission">
              👉 前往设置开启未知应用安装权限
            </button>
          </div>

          <div v-else-if="downloadState.status === 'installing'" class="progress-action-row">
            <button type="button" @click="triggerManualInstall" class="btn-progress-action btn-install">
              📲 重新调起系统安装器
            </button>
          </div>

          <div v-else-if="downloadState.status === 'error'" class="progress-action-row">
            <button type="button" @click="downloadApk(downloadState.variant)" class="btn-progress-action btn-retry">
              🔄 恢复/重试下载
            </button>
          </div>

          <!-- 辅助控制：取消与浏览器降级 -->
          <div class="progress-footer-actions">
            <button type="button" @click="cancelDownload" class="btn-sub-action">
              ✕ 取消下载
            </button>
            <button type="button" @click="fallbackToExternalBrowser" class="btn-sub-action text-primary">
              🌐 切换为外部浏览器下载 ↗
            </button>
          </div>
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
import { ref, onMounted, onUnmounted } from 'vue';
import {
  getApiBase,
  setApiBase,
  isAuthorized,
  authorize,
  deauthorize,
  openFeedbackModal
} from '@lylyuanliang/agent-feedback-client';
import { openExternalUrl } from '@/utils/appLauncher.js';
import { formatBytes } from '@/services/updateService.js';

const authorized = ref(false);
const isConnected = ref(false);
const loading = ref(false);
const fetchError = ref('');
const devServerUrl = ref('');
const inputTunnelUrl = ref('');
const isEditingTunnel = ref(false);
const saveSuccess = ref(false);

const pairingSecretInput = ref('');
const authSubmitting = ref(false);
const authError = ref('');

const artifactInfo = ref(null);
const copied = ref(false);
const isNativeApp = ref(typeof window !== 'undefined' && !!(window.Capacitor?.isNativePlatform?.() || window.AlpineNative));

const downloadState = ref({
  status: 'idle', // 'idle' | 'downloading' | 'installing' | 'permission_required' | 'completed' | 'error'
  percent: 0,
  receivedBytes: 0,
  totalBytes: 0,
  message: '',
  variant: 'debug'
});

function onDownloadProgress(event) {
  const data = event?.detail || event;
  if (!data) return;

  if (data.status) {
    downloadState.value.status = data.status;
  }
  if (data.percent !== undefined) {
    downloadState.value.percent = Number(data.percent) || 0;
  }
  if (data.receivedBytes !== undefined) {
    downloadState.value.receivedBytes = Number(data.receivedBytes) || 0;
  }
  if (data.totalBytes !== undefined) {
    downloadState.value.totalBytes = Number(data.totalBytes) || 0;
  }
  if (data.message !== undefined) {
    downloadState.value.message = data.message;
  }
}

onMounted(() => {
  checkAuthAndLoad();
  if (typeof window !== 'undefined') {
    const prevProgress = window.onAlpineDownloadProgress;
    window.onAlpineDownloadProgress = (data) => {
      if (typeof prevProgress === 'function') {
        try { prevProgress(data); } catch (_) {}
      }
      window.dispatchEvent(new CustomEvent('alpine-download-progress', { detail: data }));
    };
    window.addEventListener('alpine-download-progress', onDownloadProgress);
  }
});

onUnmounted(() => {
  if (typeof window !== 'undefined') {
    window.removeEventListener('alpine-download-progress', onDownloadProgress);
  }
});

function checkAuthAndLoad() {
  authorized.value = isAuthorized();
  initTunnelUrl();
  if (authorized.value) {
    checkDevArtifacts();
  }
}

function initTunnelUrl() {
  const savedBase = getApiBase();
  if (savedBase) {
    devServerUrl.value = savedBase;
    inputTunnelUrl.value = savedBase;
  } else if (!isNativeApp.value) {
    devServerUrl.value = window.location.origin;
    inputTunnelUrl.value = window.location.origin;
  } else {
    devServerUrl.value = '';
    inputTunnelUrl.value = '';
  }
}

function startEditTunnel() {
  inputTunnelUrl.value = devServerUrl.value;
  isEditingTunnel.value = true;
}

function cancelEditTunnel() {
  isEditingTunnel.value = false;
  inputTunnelUrl.value = devServerUrl.value;
}

function saveTunnelUrl() {
  let clean = (inputTunnelUrl.value || '').trim().replace(/\/+$/, '');
  if (clean && !/^https?:\/\//i.test(clean)) {
    clean = 'http://' + clean;
  }

  devServerUrl.value = clean;
  inputTunnelUrl.value = clean;
  setApiBase(clean);
  try {
    localStorage.setItem('af_api_base', clean);
  } catch {}

  isEditingTunnel.value = false;
  saveSuccess.value = true;
  setTimeout(() => { saveSuccess.value = false; }, 2500);

  if (authorized.value && clean) {
    checkDevArtifacts();
  }
}

async function handleUnlock() {
  const key = pairingSecretInput.value.trim();
  if (!key) {
    authError.value = '请输入配对密钥';
    return;
  }
  authSubmitting.value = true;
  authError.value = '';

  try {
    const ok = await authorize(key);
    if (ok) {
      authorized.value = true;
      pairingSecretInput.value = '';
      checkDevArtifacts();
    } else {
      authError.value = '配对密钥不匹配，请查看开发机 scratch/.agent-feedback-secret';
    }
  } catch (err) {
    authError.value = err.message || '验证失败';
  } finally {
    authSubmitting.value = false;
  }
}

function handleUnbind() {
  deauthorize();
  authorized.value = false;
  artifactInfo.value = null;
  isConnected.value = false;
}

function goToSettings() {
  openFeedbackModal('settings');
}

async function checkDevArtifacts() {
  loading.value = true;
  fetchError.value = '';

  let targetBase = (devServerUrl.value || '').trim().replace(/\/+$/, '');
  if (!targetBase && !isNativeApp.value) {
    targetBase = window.location.origin;
  }

  if (!targetBase || (isNativeApp.value && targetBase.includes('localhost'))) {
    loading.value = false;
    isConnected.value = false;
    fetchError.value = isNativeApp.value
      ? '手机真机无法直连开发机 localhost。请点击上方「配置穿透」填入开发机内网穿透域名或局域网 IP（例如 http://192.168.1.xxx:5173）。'
      : '尚未配置开发机地址，请确认开发机已启动。';
    return;
  }

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

    const text = await res.text();
    if (text.trim().startsWith('<') || text.toLowerCase().includes('<!doctype')) {
      throw new Error('开发机返回了 HTML 页面而非 API 数据。请检查穿透端口是否正确填入 5173，且开发机已启动 npm run dev。');
    }

    const data = JSON.parse(text);
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

  // 1. 若处于原生 Android 环境且支持 AlpineNative 原生下载桥，执行应用内断点续传下载
  if (isNativeApp.value && typeof window !== 'undefined' && window.AlpineNative) {
    downloadState.value = {
      status: 'downloading',
      percent: 0,
      receivedBytes: 0,
      totalBytes: artifactInfo.value?.fileSizeBytes || 0,
      message: '正在连接开发机高速下载 (支持断点续传)...',
      variant: variant
    };

    const targetVersion = `dev-${variant}-${artifactInfo.value?.buildCode || Date.now()}`;
    if (typeof window.AlpineNative.downloadAndInstallApkWithSha256 === 'function') {
      window.AlpineNative.downloadAndInstallApkWithSha256(downloadUrl, targetVersion, null);
    } else if (typeof window.AlpineNative.downloadAndInstallApk === 'function') {
      window.AlpineNative.downloadAndInstallApk(downloadUrl, targetVersion, null);
    } else {
      openExternalUrl(downloadUrl);
    }
    return;
  }

  // 2. 网页端环境：标准浏览器文件直接下载
  const a = document.createElement('a');
  a.href = downloadUrl;
  a.download = `weekly-mountain-dev-${variant}.apk`;
  a.target = '_blank';
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
}

function cancelDownload() {
  if (typeof window !== 'undefined' && window.AlpineNative?.cancelDownload) {
    window.AlpineNative.cancelDownload();
  }
  downloadState.value.status = 'idle';
  downloadState.value.percent = 0;
  downloadState.value.receivedBytes = 0;
  downloadState.value.totalBytes = 0;
  downloadState.value.message = '';
}

function triggerManualInstall() {
  if (typeof window !== 'undefined' && window.AlpineNative?.installDownloadedApk) {
    window.AlpineNative.installDownloadedApk();
  }
}

function openPermissionSettings() {
  if (typeof window !== 'undefined' && window.AlpineNative?.openInstallPermissionSettings) {
    window.AlpineNative.openInstallPermissionSettings();
  }
}

function fallbackToExternalBrowser() {
  const targetBase = (devServerUrl.value || window.location.origin).replace(/\/+$/, '');
  const variant = downloadState.value.variant || 'debug';
  const apkPath = variant === 'release' ? '/releases/weekly-mountain-latest-release.apk' : '/releases/weekly-mountain-latest-debug.apk';
  const downloadUrl = `${targetBase}${apkPath}`;
  cancelDownload();
  openExternalUrl(downloadUrl);
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
