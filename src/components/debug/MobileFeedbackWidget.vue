<template>
  <!-- Only displayed in dev environment, cpolar tunnels, or when ?debug=1 is present -->
  <aside v-if="isEnabled" class="mobile-feedback-container pointer-events-auto">
    <!-- Floating Trigger Pill on Mobile Screen (Draggable, default above bottom sheet) -->
    <button
      v-if="!isOpen"
      ref="triggerBtnRef"
      type="button"
      @click="handleBtnClick"
      @touchstart.passive="onBtnTouchStart"
      @touchmove.passive="onBtnTouchMove"
      @touchend="onBtnTouchEnd"
      :style="btnPos.x !== null ? { left: `${btnPos.x}px`, top: `${btnPos.y}px`, right: 'auto', bottom: 'auto' } : {}"
      :class="{ 'opacity-0 pointer-events-none scale-75': isSuppressedBySheet }"
      class="btn-feedback-trigger fixed right-3 bottom-[432px] z-[999] flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-[#262a34] text-primary border border-primary/50 shadow-2xl active:scale-95 transition-all duration-300 group select-none cursor-grab whitespace-nowrap flex-nowrap shrink-0 max-w-fit"
      :title="hasActiveFeedback ? '有正在处理中的反馈，点击查看进度' : '真机调试反馈给 AI (支持拖拽移动)'"
      aria-label="真机调试反馈给 AI"
    >
      <span
        class="w-2 h-2 rounded-full flex-shrink-0"
        :class="hasActiveFeedback ? 'bg-amber-400 shadow-[0_0_8px_#f59e0b]' : 'bg-primary shadow-[0_0_8px_#4edea3]'"
      ></span>
      <span
        class="material-symbols-outlined text-[17px] flex-shrink-0"
        :class="hasActiveFeedback ? 'text-amber-400' : 'text-primary'"
      >
        {{ hasActiveFeedback ? 'hourglass_top' : 'chat_bubble' }}
      </span>
      <span class="text-caption font-bold tracking-tight text-on-surface whitespace-nowrap flex-shrink-0">
        {{ hasActiveFeedback ? (activeCount > 1 ? `处理中 (${activeCount}排队)` : '处理中...') : '反馈给 AI' }}
      </span>
      <span
        v-if="feedbackHistory.length > 0 && !hasActiveFeedback"
        class="px-1.5 py-0.2 rounded-full bg-surface-container-lowest text-primary text-[10px] font-mono border border-primary/30 flex-shrink-0"
      >
        {{ feedbackHistory.length }}
      </span>
    </button>

    <!-- Feedback Modal / Bottom Sheet (Teleported to body to avoid clipping by app container) -->
    <Teleport to="body">
      <div
        v-if="isOpen"
        v-show="!isModalHiddenForCapture"
        class="mobile-feedback-modal fixed inset-0 z-[1000] flex items-end sm:items-center justify-center p-0 sm:p-4 bg-black/80 backdrop-blur-sm animate-fade-in select-none"
        @click.self="closeModal"
      >
        <div
          class="w-full max-w-md bg-[#1c1f29] rounded-t-3xl sm:rounded-2xl border-t sm:border border-outline-variant/40 shadow-2xl flex flex-col h-[80vh] max-h-[88dvh] min-h-[440px] overflow-hidden"
          role="dialog"
          aria-modal="true"
          aria-label="真机调试即时反馈"
        >
          <!-- Fixed Top Header & Tab Switcher (flex-shrink-0, 保证在任何视口下永不被压缩或截断) -->
          <div class="p-4 sm:p-5 pb-3 flex-shrink-0 space-y-3 border-b border-outline-variant/20 bg-[#1c1f29]">
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-2">
                <span class="material-symbols-outlined text-primary text-[22px]">devices</span>
                <div>
                  <div class="flex items-center gap-1.5">
                    <h3 class="text-headline-md font-bold text-on-surface text-[16px]">
                      手机端即时反馈
                    </h3>
                    <span class="px-1.5 py-0.2 rounded bg-primary/20 text-primary font-mono text-[10px] font-bold border border-primary/40">v{{ APP_VERSION }}</span>
                  </div>
                  <p class="text-[11px] text-on-surface-variant font-mono">
                    直连 AI 哨兵 · 实时追踪 · 多截图与模态支持
                  </p>
                </div>
              </div>
              <button
                type="button"
                @click="closeModal"
                class="w-8 h-8 rounded-full bg-surface-container-high flex items-center justify-center text-on-surface-variant hover:text-on-surface border border-outline-variant/30 active:scale-95 transition-all"
                aria-label="关闭反馈窗口"
              >
                <span class="material-symbols-outlined text-[18px]">close</span>
              </button>
            </div>

            <!-- Segmented Tab Switcher: [ ✍️ 提新反馈 ] | [ 📋 进度与历史 (N) ] -->
            <div class="flex items-center p-1 rounded-xl bg-surface-container-low border border-outline-variant/30 gap-1 select-none">
              <button
                type="button"
                data-tab="create"
                @click="activeTab = 'create'"
                class="flex-1 py-1.5 px-3 rounded-lg text-caption font-semibold flex items-center justify-center gap-1.5 transition-all"
                :class="activeTab === 'create' ? 'bg-surface-container-high text-primary shadow-sm' : 'text-on-surface-variant hover:text-on-surface'"
              >
                <span class="material-symbols-outlined text-[16px]">edit_note</span>
                <span>提新反馈</span>
              </button>
              <button
                type="button"
                data-tab="history"
                @click="switchTab('history')"
                class="flex-1 py-1.5 px-3 rounded-lg text-caption font-semibold flex items-center justify-center gap-1.5 transition-all relative"
                :class="activeTab === 'history' ? 'bg-surface-container-high text-primary shadow-sm' : 'text-on-surface-variant hover:text-on-surface'"
              >
                <span class="material-symbols-outlined text-[16px]">history</span>
                <span>进度与历史</span>
                <span
                  v-if="hasActiveFeedback"
                  class="w-2 h-2 rounded-full bg-amber-400 animate-pulse ml-0.5"
                  title="有处理中的反馈"
                ></span>
                <span
                  v-else-if="feedbackHistory.length > 0"
                  class="px-1.5 py-0.2 rounded-full bg-primary/20 text-primary text-[10px] font-mono"
                >
                  {{ feedbackHistory.length }}
                </span>
              </button>
            </div>
          </div>

          <!-- Dedicated Scrollable Body (flex-1 overflow-y-auto overscroll-contain) -->
          <div class="flex-1 overflow-y-auto px-4 sm:px-5 py-3.5 space-y-3.5 no-scrollbar overscroll-contain">
            <!-- TAB 1: CREATE NEW FEEDBACK -->
        <div v-if="activeTab === 'create'" class="space-y-3.5 animate-fade-in">
          <!-- Active Feedback Notice -->
          <div
            v-if="hasActiveFeedback"
            class="p-2.5 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-300 text-[11px] flex items-center gap-2 animate-fade-in"
          >
            <span class="material-symbols-outlined text-[16px] animate-pulse flex-shrink-0">hourglass_top</span>
            <span class="leading-tight">
              当前有 <strong>{{ activeCount }} 条</strong> 反馈正在排队处理中。你可随时继续提交，新反馈将自动加入待处理队列，AI 将按序连贯处理。
            </span>
          </div>

          <!-- Auto-Captured Device Diagnostics Summary -->
          <div class="p-2.5 rounded-xl bg-surface-container-low/90 border border-outline-variant/30 space-y-1.5 text-caption font-mono text-[11px]">
            <div class="flex items-center justify-between text-on-surface-variant">
              <span>📱 视口尺寸 (CSS):</span>
              <strong class="text-primary font-bold">{{ deviceInfo.viewport }} (DPR: {{ deviceInfo.dpr }})</strong>
            </div>
            <div class="flex items-center justify-between text-on-surface-variant">
              <span>🧭 当前路由 / 山峰:</span>
              <span class="text-secondary truncate max-w-[200px]">
                {{ currentRouteText }}
              </span>
            </div>
            <div class="flex items-center justify-between text-on-surface-variant">
              <span>⚡ 控制台 JS 异常:</span>
              <span :class="consoleErrors.length > 0 ? 'text-error font-bold' : 'text-primary'">
                {{ consoleErrors.length > 0 ? `${consoleErrors.length} 条报错` : '0 报错 (运行正常)' }}
              </span>
            </div>
          </div>

          <!-- Quick Tags -->
          <div class="space-y-1.5">
            <p class="text-[11px] text-on-surface-variant font-medium">快速选择预设问题标签：</p>
            <div class="flex flex-wrap gap-1.5">
              <button
                v-for="tag in quickTags"
                :key="tag"
                type="button"
                @click="addQuickTag(tag)"
                class="px-2.5 py-1 rounded-lg bg-surface-container-high border border-outline-variant/30 text-caption text-on-surface hover:border-primary/50 active:scale-95 transition-all text-[11px]"
              >
                {{ tag }}
              </button>
            </div>
          </div>

          <!-- Feedback Content Input with Paste Support -->
          <div class="space-y-1">
            <label for="mobile-feedback-text" class="text-[11px] text-on-surface-variant font-medium flex items-center justify-between">
              <span>具体现象与修改建议：</span>
              <span class="text-[10px] text-primary" v-if="feedbackText.length > 0">{{ feedbackText.length }} 字</span>
            </label>
            <textarea
              id="mobile-feedback-text"
              v-model="feedbackText"
              @paste="handlePaste"
              rows="3"
              placeholder="例：在小米15上滑动地图感觉有阻尼；或者山峰卡片底部的按钮依然有一点点偏下... (支持直接粘贴截图)"
              class="w-full p-2.5 rounded-xl bg-surface-container-lowest border border-outline-variant/40 text-on-surface text-body-sm focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary/40 resize-none font-sans"
            ></textarea>
          </div>

          <!-- Screenshot Attachment Section -->
          <div class="space-y-2">
            <!-- Checkbox Toggle Card (Stitch Alpine Custom Checkbox) -->
            <div
              @click="toggleAutoCapture"
              class="feedback-checkbox-card p-2.5 rounded-xl bg-surface-container-high/60 border border-outline-variant/30 hover:border-outline-variant/60 flex items-center justify-between cursor-pointer transition-all active:scale-[0.99] select-none group"
            >
              <div class="flex items-center gap-2.5">
                <!-- Custom Stitch Alpine Checkbox -->
                <div
                  class="w-5 h-5 rounded-md border flex items-center justify-center transition-all duration-200 flex-shrink-0"
                  :class="autoCaptureCurrentPage
                    ? 'bg-primary border-primary text-[#0a0e17] shadow-[0_0_10px_rgba(78,222,163,0.35)]'
                    : 'bg-[#10141e] border-outline-variant/60 group-hover:border-primary/50 text-transparent'"
                >
                  <span class="material-symbols-outlined text-[15px] font-black leading-none">check</span>
                </div>
                <input
                  type="checkbox"
                  :checked="autoCaptureCurrentPage"
                  class="sr-only"
                  aria-label="自动截图当前页面"
                />
                <span class="text-caption font-medium text-on-surface flex items-center gap-1.5">
                  <span class="material-symbols-outlined text-[17px] text-secondary">photo_camera</span>
                  <span>自动截图当前页面</span>
                </span>
              </div>
              <span
                class="text-[10px] font-mono transition-colors"
                :class="autoCaptureCurrentPage ? 'text-primary font-semibold' : 'text-on-surface-variant'"
              >
                {{ autoCaptureCurrentPage ? (isCapturing ? '截屏中...' : '已开启') : '默认未勾选' }}
              </span>
            </div>

            <!-- Invisible Native File Input for Album / Camera (支持多图选择) -->
            <input
              ref="fileInputRef"
              type="file"
              accept="image/*"
              multiple
              class="hidden"
              @change="handleFileChange"
            />

            <!-- Screenshots Section (多截图管理与相册选择) -->
            <div class="space-y-2">
              <div class="flex items-center justify-between px-1">
                <button
                  v-if="screenshotList.length < MAX_SCREENSHOTS"
                  type="button"
                  @click="triggerFileInput"
                  class="text-[11px] text-primary hover:text-primary-fixed flex items-center gap-1 active:scale-95 transition-all font-mono"
                >
                  <span class="material-symbols-outlined text-[15px]">add_photo_alternate</span>
                  <span>{{ screenshotList.length === 0 ? '从手机相册选取截屏/拍照 (可多选)' : `继续添加 (${screenshotList.length}/${MAX_SCREENSHOTS})` }}</span>
                </button>
                <span v-else class="text-[10px] text-on-surface-variant font-mono">已满 5 张截图</span>

                <div class="flex items-center gap-2">
                  <span v-if="screenshotList.length === 0" class="text-[10px] text-on-surface-variant font-mono opacity-70">支持直接粘贴</span>
                  <button
                    v-else
                    type="button"
                    @click="clearAllScreenshots"
                    class="text-[10px] text-error/80 hover:text-error active:scale-95 transition-all font-mono"
                  >
                    清空全部
                  </button>
                </div>
              </div>

              <!-- Multi-Screenshot Preview Grid -->
              <div
                v-if="screenshotList.length > 0"
                class="p-2.5 rounded-xl bg-surface-container-low/90 border border-primary/30 space-y-2 animate-fade-in"
              >
                <div class="flex items-center justify-between text-[11px] font-mono text-on-surface-variant px-0.5">
                  <span class="text-primary font-bold flex items-center gap-1">
                    <span class="material-symbols-outlined text-[14px]">photo_library</span>
                    已附带 {{ screenshotList.length }} 张截图凭证
                  </span>
                  <span class="text-[10px] opacity-75">点击缩略图查看大图</span>
                </div>

                <div class="flex items-center gap-2.5 overflow-x-auto no-scrollbar py-1">
                  <!-- Thumbnail Items -->
                  <div
                    v-for="(item, idx) in screenshotList"
                    :key="item.id || idx"
                    class="relative w-16 h-16 rounded-lg overflow-hidden bg-black/40 border border-outline-variant/40 flex-shrink-0 cursor-pointer group shadow"
                  >
                    <img
                      :src="item.data"
                      :alt="'截图 ' + (idx + 1)"
                      class="w-full h-full object-cover group-hover:scale-105 transition-transform"
                      @click="openLightbox(item.data, `${item.source} (${idx + 1}/${screenshotList.length})`)"
                      title="点击全屏查看"
                    />
                    <!-- Overlay Remove Button -->
                    <button
                      type="button"
                      @click.stop="removeScreenshotItem(idx)"
                      class="absolute top-0.5 right-0.5 w-4 h-4 rounded-full bg-black/80 hover:bg-error text-white flex items-center justify-center text-[10px] transition-colors"
                      title="移除此图"
                      aria-label="移除截图"
                    >
                      ✕
                    </button>
                    <!-- Bottom Source Chip -->
                    <div class="absolute inset-x-0 bottom-0 bg-black/75 text-[8px] font-mono text-center text-on-surface-variant truncate px-0.5 py-0.2">
                      {{ item.source === '自动截图当前页面' ? '当前页' : '相册' }}
                    </div>
                  </div>

                  <!-- Add More Tile (if < MAX_SCREENSHOTS) -->
                  <button
                    v-if="screenshotList.length < MAX_SCREENSHOTS"
                    type="button"
                    @click="triggerFileInput"
                    class="w-16 h-16 rounded-lg border border-dashed border-outline-variant/60 hover:border-primary flex flex-col items-center justify-center text-on-surface-variant hover:text-primary active:scale-95 transition-all flex-shrink-0 bg-surface-container/20 group"
                    title="添加更多截图"
                  >
                    <span class="material-symbols-outlined text-[20px] group-hover:scale-110 transition-transform">add</span>
                    <span class="text-[9px] font-mono">添加</span>
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- Success or Error Status Notice -->
          <div
            v-if="submitStatus.message"
            class="p-2.5 rounded-xl border flex items-center gap-2 text-caption animate-fade-in"
            :class="submitStatus.success ? 'bg-primary-container/20 border-primary/40 text-primary' : 'bg-error-container/20 border-error/40 text-error'"
          >
            <span class="material-symbols-outlined text-[18px] flex-shrink-0">
              {{ submitStatus.success ? 'check_circle' : 'error' }}
            </span>
            <span class="leading-tight">{{ submitStatus.message }}</span>
          </div>

          <!-- Action Buttons -->
          <div class="pt-1 flex items-center gap-2.5">
            <button
              type="button"
              @click="handleSubmit"
              :disabled="isSubmitting"
              class="flex-1 py-2.5 px-3 rounded-xl bg-gradient-to-r from-primary-container to-secondary-container text-surface-container-lowest font-bold text-body-sm flex items-center justify-center gap-1.5 glow-primary active:scale-95 transition-all disabled:opacity-50"
            >
              <span
                class="material-symbols-outlined text-[18px]"
                :class="{ 'animate-spin': isSubmitting }"
              >
                {{ isSubmitting ? 'progress_activity' : 'send' }}
              </span>
              <span>{{ isSubmitting ? '正在传输...' : (screenshotList.length > 0 ? `🚀 携带 ${screenshotList.length} 张截图发送给 AI` : '🚀 发送给 AI 助手') }}</span>
            </button>

            <button
              type="button"
              @click="copyDiagnostics"
              class="py-2.5 px-3 rounded-xl bg-surface-container-high border border-outline-variant/30 text-on-surface text-caption font-semibold flex items-center gap-1 active:scale-95 hover:border-primary/40 transition-all flex-shrink-0"
              title="复制设备与报错报告到剪贴板"
            >
              <span class="material-symbols-outlined text-[16px]">content_copy</span>
              <span>{{ copied ? '已复制' : '复制报告' }}</span>
            </button>
          </div>
        </div>

        <!-- TAB 2: PROGRESS & HISTORY LIST -->
        <div v-else-if="activeTab === 'history'" class="space-y-3 animate-fade-in" data-testid="feedback-history-list">
          <!-- History Subheader with Refresh -->
          <div class="flex items-center justify-between px-1">
            <span class="text-[12px] font-bold text-on-surface flex items-center gap-1.5">
              <span class="material-symbols-outlined text-[16px] text-primary">view_timeline</span>
              <span>调试反馈追踪列表</span>
            </span>
            <button
              type="button"
              @click="fetchHistory(false)"
              :disabled="isFetchingHistory"
              class="text-[11px] text-primary hover:text-primary-fixed flex items-center gap-1 active:scale-95 transition-all disabled:opacity-50 py-1 px-2 rounded-lg bg-surface-container-high/60 border border-outline-variant/20"
            >
              <span class="material-symbols-outlined text-[14px]" :class="{ 'animate-spin': isFetchingHistory }">refresh</span>
              <span>{{ isFetchingHistory ? '刷新中...' : '刷新' }}</span>
            </button>
          </div>

          <!-- Loading State -->
          <div v-if="isFetchingHistory && feedbackHistory.length === 0" class="py-12 text-center text-on-surface-variant text-[12px] space-y-2">
            <span class="material-symbols-outlined animate-spin text-[28px] text-primary">progress_activity</span>
            <p class="font-mono text-caption">正在同步反馈进度...</p>
          </div>

          <!-- Empty State -->
          <div v-else-if="feedbackHistory.length === 0" class="p-8 rounded-2xl bg-surface-container-low/50 border border-outline-variant/20 text-center space-y-2">
            <span class="material-symbols-outlined text-[36px] text-on-surface-variant opacity-40">inbox</span>
            <p class="text-caption text-on-surface-variant">暂无历史反馈记录</p>
            <button
              type="button"
              @click="activeTab = 'create'"
              class="text-[11px] text-primary hover:underline font-semibold"
            >
              点击去提交第一条反馈
            </button>
          </div>

          <!-- History Item Cards List -->
          <div v-else class="space-y-2.5 max-h-[58vh] overflow-y-auto pr-1">
            <div
              v-for="item in feedbackHistory"
              :key="item.id || item.timestamp"
              class="p-3.5 rounded-2xl bg-surface-container-low border border-outline-variant/30 space-y-2.5 hover:border-primary/40 transition-colors shadow-sm"
              :class="{ 'border-amber-500/40 bg-amber-500/5': item.status === 'pending' || item.status === 'processing' }"
            >
              <!-- Card Header: Status Badge + Mountain + Time -->
              <div class="flex items-center justify-between gap-2">
                <div class="flex items-center gap-1.5 flex-wrap">
                  <!-- Pending Status -->
                  <span
                    v-if="item.status === 'pending'"
                    class="px-2 py-0.5 rounded-full bg-amber-500/15 text-amber-300 border border-amber-500/30 text-[10px] font-bold flex items-center gap-1"
                  >
                    <span class="w-1.5 h-1.5 rounded-full bg-amber-400 animate-ping"></span>
                    <span>排队待处理 {{ getQueueBadge(item.id || item.timestamp) }}</span>
                  </span>
                  <!-- Processing Status -->
                  <span
                    v-else-if="item.status === 'processing'"
                    class="px-2 py-0.5 rounded-full bg-blue-500/15 text-blue-300 border border-blue-500/30 text-[10px] font-bold flex items-center gap-1"
                  >
                    <span class="material-symbols-outlined text-[12px] animate-spin">sync</span>
                    <span>AI 正在排查修复</span>
                  </span>
                  <!-- Answered / Explanation Status -->
                  <span
                    v-else-if="item.status === 'answered' || item.status === 'explained' || item.status === 'rejected'"
                    class="px-2 py-0.5 rounded-full bg-purple-500/15 text-purple-300 border border-purple-500/30 text-[10px] font-bold flex items-center gap-1"
                  >
                    <span class="material-symbols-outlined text-[12px]">help_outline</span>
                    <span>方案答复 / 说明</span>
                  </span>
                  <!-- Completed Status -->
                  <span
                    v-else
                    class="px-2 py-0.5 rounded-full bg-emerald-500/15 text-emerald-300 border border-emerald-500/30 text-[10px] font-bold flex items-center gap-1"
                  >
                    <span class="material-symbols-outlined text-[12px]">check_circle</span>
                    <span>已完成并验证</span>
                  </span>

                  <!-- Context tag: Mountain Name -->
                  <span v-if="item.state?.mountain" class="px-1.5 py-0.5 rounded bg-surface-container-high text-[10px] text-secondary font-mono">
                    {{ item.state.mountain }}
                  </span>
                </div>

                <!-- Timestamp -->
                <span class="text-[10px] text-on-surface-variant font-mono flex-shrink-0">
                  {{ formatTime(item.timestamp) }}
                </span>
              </div>

              <!-- Feedback Content Quote -->
              <p class="text-[12px] text-on-surface leading-relaxed break-words pl-2.5 border-l-2 border-primary/50 font-sans">
                {{ item.content }}
              </p>

              <!-- Attached Screenshots Thumbnails (支持多图与历史单图平滑兼容) -->
              <div v-if="item.screenshots && item.screenshots.length > 0" class="space-y-1.5">
                <span class="text-[10px] font-mono text-on-surface-variant flex items-center gap-1">
                  <span class="material-symbols-outlined text-[13px] text-primary">photo_library</span>
                  附带 {{ item.screenshots.length }} 张截图凭证：
                </span>
                <div class="flex items-center gap-2 overflow-x-auto no-scrollbar py-0.5">
                  <div
                    v-for="(sShot, sIdx) in item.screenshots"
                    :key="sShot.filename || sIdx"
                    class="relative w-12 h-12 rounded-lg overflow-hidden bg-black/40 border border-outline-variant/30 flex-shrink-0 cursor-pointer group hover:border-primary transition-all"
                    @click="openLightbox('/api/feedback/screenshot/' + sShot.filename, `${item.content} (图 ${sIdx + 1})`)"
                  >
                    <img
                      :src="'/api/feedback/screenshot/' + sShot.filename"
                      alt="反馈截图缩略图"
                      class="w-full h-full object-cover group-hover:scale-105 transition-transform"
                      loading="lazy"
                    />
                    <div class="absolute inset-0 bg-black/30 opacity-0 group-hover:opacity-100 flex items-center justify-center transition-opacity">
                      <span class="material-symbols-outlined text-[14px] text-white">zoom_in</span>
                    </div>
                  </div>
                </div>
              </div>
              <div
                v-else-if="item.screenshotFilename"
                class="flex items-center gap-2.5 p-2 rounded-xl bg-surface-container-high/60 border border-outline-variant/30 cursor-pointer hover:border-primary/50 active:scale-[0.98] transition-all"
                @click="openLightbox('/api/feedback/screenshot/' + item.screenshotFilename, item.content || '反馈截图')"
              >
                <img
                  :src="'/api/feedback/screenshot/' + item.screenshotFilename"
                  alt="反馈截图缩略图"
                  class="w-11 h-11 object-cover rounded-lg bg-black/40 border border-outline-variant/30 flex-shrink-0"
                  loading="lazy"
                />
                <div class="flex-1 min-w-0 text-[10px] font-mono text-on-surface-variant space-y-0.5">
                  <div class="text-on-surface font-semibold flex items-center gap-1 text-[11px]">
                    <span class="material-symbols-outlined text-[13px] text-primary">image</span>
                    <span>查看提交时截图凭证</span>
                  </div>
                  <span class="truncate block text-on-surface-variant/80">
                    {{ item.screenshotMeta?.dimensions || '' }} · {{ item.screenshotMeta?.sizeText || '' }}
                  </span>
                </div>
                <span class="material-symbols-outlined text-[18px] text-on-surface-variant mr-1">zoom_in</span>
              </div>

              <!-- AI Reply & Solution Explanation Callout -->
              <div class="p-2.5 rounded-xl bg-surface-container-high/90 border border-primary/30 space-y-1">
                <div class="flex items-center justify-between text-[11px]">
                  <span class="font-bold text-primary flex items-center gap-1">
                    <span class="material-symbols-outlined text-[15px]">smart_toy</span>
                    <span>AI 进度与处理答复：</span>
                  </span>
                  <span v-if="item.updatedAt" class="text-[9px] text-on-surface-variant font-mono">
                    更新于 {{ formatTime(item.updatedAt) }}
                  </span>
                </div>
                <p class="text-[11px] text-on-surface-variant leading-relaxed">
                  {{ item.reply || (item.status === 'completed' ? '已排查并完成代码修复与验证。' : 'AI 正在排查定位中，请稍候刷新...') }}
                </p>
              </div>
            </div>
          </div>
        </div>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- Full-screen Lightbox Preview for Screenshot (Teleported to body) -->
    <Teleport to="body">
      <div
        v-if="lightboxOpen && lightboxSrc"
        class="fixed inset-0 z-[1010] bg-black/95 backdrop-blur-md flex flex-col items-center justify-center p-4 select-none animate-fade-in"
        @click.self="lightboxOpen = false"
      >
        <div class="w-full max-w-md flex items-center justify-between pb-3 text-white">
          <span class="text-caption font-mono truncate max-w-[280px]">{{ lightboxTitle || '截图放大预览' }}</span>
          <button
            type="button"
            @click="lightboxOpen = false"
            class="p-1.5 rounded-full bg-white/10 hover:bg-white/20 text-white"
          >
            <span class="material-symbols-outlined text-[20px]">close</span>
          </button>
        </div>
        <div class="max-w-full max-h-[80vh] overflow-auto rounded-xl border border-white/20">
          <img :src="lightboxSrc" alt="截图放大预览" class="max-w-full max-h-[75vh] object-contain rounded-lg" />
        </div>
      </div>
    </Teleport>
  </aside>
</template>

<script setup>
import { APP_VERSION } from '@/config/version.js';
import { ref, computed, watch, onMounted, onUnmounted } from 'vue';
import { useRoute } from 'vue-router';
import { useMountainStore } from '@/stores/mountainStore.js';

const route = useRoute();
const mountainStore = useMountainStore();


// 自动避让山峰详情页与全屏画廊，避免悬浮在右上角遮挡
const isSuppressedBySheet = ref(false);
let sheetObserver = null;

function setupSheetAutoSuppress() {
  const check = () => {
    const hasSheet = !!document.querySelector('.mountain-detail-sheet') || !!document.querySelector('.lightbox-overlay');
    isSuppressedBySheet.value = hasSheet;
  };
  sheetObserver = new MutationObserver(check);
  sheetObserver.observe(document.body, { childList: true, subtree: true });
  check();
}

const isEnabled = computed(() => {
  if (typeof window === 'undefined') return false;
  return (
    import.meta.env.DEV ||
    window.location.search.includes('debug=1') ||
    window.location.hostname.includes('cpolar') ||
    window.location.hostname.includes('192.168.') ||
    window.location.hostname.includes('10.')
  );
});

// Modal and View States
const isOpen = ref(false);
const isModalHiddenForCapture = ref(false);
const activeTab = ref('create'); // 'create' | 'history'
const feedbackHistory = ref([]);
const isFetchingHistory = ref(false);

const feedbackText = ref('');
const isSubmitting = ref(false);
const copied = ref(false);
const submitStatus = ref({ success: false, message: '' });
const consoleErrors = ref([]);

// Floating pill draggable position
const triggerBtnRef = ref(null);
const btnPos = ref({ x: null, y: null });
let isBtnDragging = false;
let btnTouchStartX = 0;
let btnTouchStartY = 0;
let btnInitialX = 0;
let btnInitialY = 0;
let btnWidth = 145;
let btnHeight = 36;
let hasBtnMoved = false;

function onBtnTouchStart(e) {
  isBtnDragging = true;
  hasBtnMoved = false;
  const touch = e.touches[0];
  btnTouchStartX = touch.clientX;
  btnTouchStartY = touch.clientY;
  const rect = e.currentTarget.getBoundingClientRect();
  btnInitialX = rect.left;
  btnInitialY = rect.top;
  btnWidth = rect.width || 145;
  btnHeight = rect.height || 36;
}

function onBtnTouchMove(e) {
  if (!isBtnDragging) return;
  const touch = e.touches[0];
  const dx = touch.clientX - btnTouchStartX;
  const dy = touch.clientY - btnTouchStartY;
  if (Math.hypot(dx, dy) > 6) {
    hasBtnMoved = true;
  }
  const screenW = typeof window !== 'undefined' ? window.innerWidth : 390;
  const screenH = typeof window !== 'undefined' ? window.innerHeight : 844;
  const maxX = Math.max(10, screenW - btnWidth - 12);
  const maxY = Math.max(60, screenH - btnHeight - 80);
  const newX = Math.max(10, Math.min(maxX, btnInitialX + dx));
  const newY = Math.max(60, Math.min(maxY, btnInitialY + dy));
  btnPos.value = { x: newX, y: newY };
}

function onBtnTouchEnd() {
  isBtnDragging = false;
  if (hasBtnMoved && btnPos.value.x !== null) {
    const screenW = typeof window !== 'undefined' ? window.innerWidth : 390;
    // 自动吸附左侧或右侧安全留白 (12px)，严格以自身真实宽度计算，杜绝文字挤压折行
    const snapRightX = Math.max(10, screenW - btnWidth - 12);
    btnPos.value.x = (btnPos.value.x + btnWidth / 2) > screenW / 2 ? snapRightX : 10;
  }
}

function handleBtnClick() {
  if (hasBtnMoved) {
    hasBtnMoved = false;
    return;
  }
  openModal();
}

// Screenshot states
const fileInputRef = ref(null);
const autoCaptureCurrentPage = ref(false); // 默认不选中
const MAX_SCREENSHOTS = 5;
const screenshotList = ref([]); // 支持多张截图 [{ id, data, width, height, sizeText, source, name }]
const screenshotData = computed(() => screenshotList.value[0]?.data || null);
const screenshotMeta = computed(() => screenshotList.value[0] ? {
  dimensions: `${screenshotList.value[0].width} × ${screenshotList.value[0].height}`,
  sizeText: screenshotList.value[0].sizeText,
  source: screenshotList.value[0].source
} : { dimensions: '', sizeText: '', source: '' });
const isCapturing = ref(false);

// Full-screen Lightbox
const lightboxOpen = ref(false);
const lightboxSrc = ref('');
const lightboxTitle = ref('');

function openLightbox(src, title = '截图放大预览') {
  lightboxSrc.value = src;
  lightboxTitle.value = title;
  lightboxOpen.value = true;
}

const quickTags = [
  '按钮位置偏下',
  '地图滑动迟钝',
  '向下滑动卡片不顺',
  '抽屉拉动受阻',
  '字体间距偏小',
  '样式错位',
  '真机操作流畅'
];

// Capture device info
const deviceInfo = ref({
  viewport: '',
  dpr: 1,
  ua: '',
  screen: ''
});

function refreshDeviceInfo() {
  if (typeof window === 'undefined') return;
  deviceInfo.value = {
    viewport: `${window.innerWidth} × ${window.innerHeight}`,
    dpr: window.devicePixelRatio || 1,
    screen: `${window.screen?.width || 0} × ${window.screen?.height || 0}`,
    ua: navigator.userAgent
  };
}

const currentRouteText = computed(() => {
  const p = route?.fullPath || '#/explore';
  const m = mountainStore.selectedMountain;
  if (m) return `${p} (${m.name})`;
  return p;
});

// Intercept runtime JS errors
if (typeof window !== 'undefined') {
  const origError = console.error;
  console.error = (...args) => {
    origError.apply(console, args);
    const msg = args.map(a => (typeof a === 'object' ? JSON.stringify(a) : String(a))).join(' ');
    consoleErrors.value.unshift(msg.slice(0, 160));
    if (consoleErrors.value.length > 5) consoleErrors.value.pop();
  };

  window.addEventListener('error', (event) => {
    const errText = `${event.message} (${event.filename ? event.filename.split('/').pop() : ''}:${event.lineno})`;
    consoleErrors.value.unshift(errText);
    if (consoleErrors.value.length > 5) consoleErrors.value.pop();
  });
}

// Active feedback detection
const hasActiveFeedback = computed(() => {
  return feedbackHistory.value.some(
    item => item.status === 'pending' || item.status === 'processing'
  );
});

const activeCount = computed(() => {
  return feedbackHistory.value.filter(
    item => item.status === 'pending' || item.status === 'processing'
  ).length;
});

function getQueueBadge(id) {
  const pendings = feedbackHistory.value.filter(item => item.status === 'pending').slice().reverse();
  const idx = pendings.findIndex(p => p.id === id || p.timestamp === id);
  if (idx !== -1 && pendings.length > 1) {
    return `(第 ${idx + 1} 位)`;
  }
  return '';
}

// History fetching & polling
let pollTimer = null;

async function fetchHistory(silent = false) {
  if (!silent) isFetchingHistory.value = true;
  try {
    const res = await fetch('/api/feedback');
    const data = await res.json();
    if (data && data.success && Array.isArray(data.history)) {
      feedbackHistory.value = data.history;
    }
  } catch (err) {
    consecutivePollErrors++;
    console.warn('Failed to fetch feedback history:', err);
  } finally {
    if (!silent) isFetchingHistory.value = false;
  }
}

function switchTab(tab) {
  activeTab.value = tab;
  if (tab === 'history') {
    fetchHistory(false);
  }
}

// 仅在弹窗打开时轻量按需轮询，弹窗关闭后彻底停止轮询，0 耗电 0 发热
let consecutivePollErrors = 0;

function checkAndSyncPolling() {
  if (pollTimer) {
    clearInterval(pollTimer);
    pollTimer = null;
  }

  // 严格仅在弹窗打开时轮询，弹窗关闭时坚决不轮询
  if (isOpen.value) {
    pollTimer = setInterval(async () => {
      if (typeof document !== 'undefined' && document.hidden) return;
      if (consecutivePollErrors >= 3) {
        // App 原生环境下若无本地 Mock 服务，连续失败3次后彻底停用轮询，保护电池与散热
        clearInterval(pollTimer);
        pollTimer = null;
        return;
      }
      try {
        await fetchHistory(true);
        consecutivePollErrors = 0;
      } catch (e) {
        consecutivePollErrors++;
      }
    }, 6000);
  }
}

watch(isOpen, () => {
  if (isOpen.value) {
    consecutivePollErrors = 0;
  }
  checkAndSyncPolling();
});

function formatTime(ts) {
  if (!ts) return '';
  const num = typeof ts === 'string' ? new Date(ts).getTime() : ts;
  if (!num || isNaN(num)) return '';
  const now = Date.now();
  const diffSec = Math.floor((now - num) / 1000);
  if (diffSec < 60) return '刚刚';
  if (diffSec < 3600) return `${Math.floor(diffSec / 60)} 分钟前`;
  if (diffSec < 86400) return `${Math.floor(diffSec / 3600)} 小时前`;
  const d = new Date(num);
  return `${d.getMonth() + 1}/${d.getDate()} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`;
}

function openModal() {
  refreshDeviceInfo();
  submitStatus.value = { success: false, message: '' };
  autoCaptureCurrentPage.value = false; // 每次打开弹窗默认不选中
  if (hasActiveFeedback.value) {
    activeTab.value = 'history';
  } else {
    activeTab.value = 'create';
  }
  fetchHistory(true);
  isOpen.value = true;
  checkAndSyncPolling();
}

function closeModal() {
  isOpen.value = false;
  lightboxOpen.value = false;
  checkAndSyncPolling();
}

function addQuickTag(tag) {
  if (!feedbackText.value) {
    feedbackText.value = tag;
  } else if (!feedbackText.value.includes(tag)) {
    feedbackText.value = `${feedbackText.value}；${tag}`;
  }
}

// Compress image via offscreen Canvas
async function compressImage(source, maxWidth = 1280, quality = 0.85) {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.crossOrigin = 'anonymous';

    const handleLoad = () => {
      let { width, height } = img;
      if (width > maxWidth || height > maxWidth) {
        if (width > height) {
          height = Math.round((height * maxWidth) / width);
          width = maxWidth;
        } else {
          width = Math.round((width * maxWidth) / height);
          height = maxWidth;
        }
      }

      const canvas = document.createElement('canvas');
      canvas.width = width;
      canvas.height = height;
      const ctx = canvas.getContext('2d');
      if (!ctx) {
        reject(new Error('Canvas 2D context unavailable'));
        return;
      }

      ctx.fillStyle = '#0a0e17';
      ctx.fillRect(0, 0, width, height);
      ctx.drawImage(img, 0, 0, width, height);

      const base64 = canvas.toDataURL('image/jpeg', quality);
      const sizeBytes = Math.round((base64.length * 3) / 4);
      const sizeKb = Math.round(sizeBytes / 1024);

      resolve({
        base64,
        width,
        height,
        sizeBytes,
        sizeText: sizeKb > 1024 ? `${(sizeKb / 1024).toFixed(1)} MB` : `${sizeKb} KB`
      });
    };

    img.onload = handleLoad;
    img.onerror = () => reject(new Error('图片格式错误或读取失败'));

    if (typeof source === 'string') {
      img.src = source;
    } else if (source instanceof File || source instanceof Blob) {
      const reader = new FileReader();
      reader.onload = (e) => {
        img.src = e.target.result;
      };
      reader.onerror = () => reject(new Error('读取文件失败'));
      reader.readAsDataURL(source);
    } else {
      reject(new Error('无效的图片来源'));
    }
  });
}

function triggerFileInput() {
  if (fileInputRef.value) {
    fileInputRef.value.click();
  }
}

async function handleFileChange(event) {
  const files = Array.from(event.target?.files || []);
  if (!files.length) return;

  const availableSlots = MAX_SCREENSHOTS - screenshotList.value.length;
  if (availableSlots <= 0) {
    submitStatus.value = {
      success: false,
      message: `截图凭证已达上限 (${MAX_SCREENSHOTS} 张)，请先移除部分截图再添加。`
    };
    if (fileInputRef.value) fileInputRef.value.value = '';
    return;
  }

  const filesToProcess = files.slice(0, availableSlots);
  if (files.length > availableSlots) {
    submitStatus.value = {
      success: true,
      message: `最多支持 ${MAX_SCREENSHOTS} 张截图，已为您导入前 ${availableSlots} 张。`
    };
  } else {
    submitStatus.value = { success: false, message: '' };
  }

  for (const file of filesToProcess) {
    try {
      const res = await compressImage(file, 1280, 0.85);
      screenshotList.value.push({
        id: `img_${Date.now()}_${Math.random().toString(36).substring(2, 7)}`,
        data: res.base64,
        width: res.width,
        height: res.height,
        sizeText: res.sizeText,
        source: '手机相册 / 拍照',
        name: file.name || '相册截图'
      });
    } catch (err) {
      console.warn('Process image failed:', err);
    }
  }

  if (fileInputRef.value) fileInputRef.value.value = '';
}

function removeScreenshotItem(index) {
  const removed = screenshotList.value.splice(index, 1)[0];
  if (removed && removed.source === '自动截图当前页面') {
    autoCaptureCurrentPage.value = false;
  }
  if (fileInputRef.value) fileInputRef.value.value = '';
}

function clearAllScreenshots() {
  screenshotList.value = [];
  autoCaptureCurrentPage.value = false;
  if (fileInputRef.value) fileInputRef.value.value = '';
}

function removeScreenshot() {
  clearAllScreenshots();
}

function toggleAutoCapture() {
  autoCaptureCurrentPage.value = !autoCaptureCurrentPage.value;
  handleAutoCaptureToggle();
}

async function handleAutoCaptureToggle() {
  if (autoCaptureCurrentPage.value) {
    await handleAutoCapture();
  } else {
    // 移除自动截取的页面截图
    const autoIdx = screenshotList.value.findIndex((s) => s.source === '自动截图当前页面');
    if (autoIdx !== -1) {
      screenshotList.value.splice(autoIdx, 1);
    }
  }
}

async function handleAutoCapture() {
  if (isCapturing.value) return;
  isCapturing.value = true;
  isModalHiddenForCapture.value = true;

  try {
    await new Promise((resolve) => setTimeout(resolve, 160));

    const html2canvasModule = await import('html2canvas');
    const html2canvas = html2canvasModule.default || html2canvasModule;

    const canvas = await html2canvas(document.body, {
      useCORS: true,
      allowTaint: true,
      logging: false,
      scale: Math.min(window.devicePixelRatio || 1, 2)
    });

    const rawDataUrl = canvas.toDataURL('image/jpeg', 0.85);
    const res = await compressImage(rawDataUrl, 1280, 0.85);

    const autoItem = {
      id: `auto_${Date.now()}`,
      data: res.base64,
      width: res.width,
      height: res.height,
      sizeText: res.sizeText,
      source: '自动截图当前页面',
      name: '当前页面全貌'
    };

    const existingIdx = screenshotList.value.findIndex((s) => s.source === '自动截图当前页面');
    if (existingIdx !== -1) {
      screenshotList.value[existingIdx] = autoItem;
    } else {
      if (screenshotList.value.length >= MAX_SCREENSHOTS) {
        screenshotList.value.pop();
      }
      screenshotList.value.unshift(autoItem);
    }

    submitStatus.value = { success: false, message: '' };
  } catch (err) {
    console.warn('html2canvas capture warning:', err);
    autoCaptureCurrentPage.value = false;
    submitStatus.value = {
      success: false,
      message: '自动截屏受限（地图跨域保护），建议点击「从相册选取」上传系统截屏。'
    };
  } finally {
    isModalHiddenForCapture.value = false;
    isCapturing.value = false;
  }
}

async function handlePaste(event) {
  const items = event.clipboardData?.items;
  if (!items) return;

  for (let i = 0; i < items.length; i++) {
    const item = items[i];
    if (item.type.indexOf('image') !== -1) {
      const file = item.getAsFile();
      if (file) {
        try {
          if (screenshotList.value.length >= MAX_SCREENSHOTS) {
            submitStatus.value = {
              success: false,
              message: `截图凭证已达上限 (${MAX_SCREENSHOTS} 张)`
            };
            return;
          }
          const res = await compressImage(file, 1280, 0.85);
          screenshotList.value.push({
            id: `paste_${Date.now()}`,
            data: res.base64,
            width: res.width,
            height: res.height,
            sizeText: res.sizeText,
            source: '剪贴板粘贴',
            name: '剪贴板截图'
          });
          submitStatus.value = {
            success: true,
            message: `✅ 已成功从剪贴板添加截图 (当前共 ${screenshotList.value.length} 张)！`
          };
        } catch (err) {
          console.error('Failed to paste image:', err);
        }
        break;
      }
    }
  }
}

async function handleSubmit() {
  const text = feedbackText.value.trim();
  if (!text && screenshotList.value.length === 0) {
    submitStatus.value = { success: false, message: '请先输入反馈描述或附带截图' };
    return;
  }

  isSubmitting.value = true;
  submitStatus.value = { success: false, message: '' };

  refreshDeviceInfo();

  const payload = {
    content: text || '（未输入文字描述，已提供截图凭证）',
    timestamp: Date.now(),
    device: deviceInfo.value,
    state: {
      route: route?.fullPath || '#/explore',
      mountainId: mountainStore.selectedMountainId,
      mountain: mountainStore.selectedMountain?.name || null
    },
    screenshots: screenshotList.value.map((item) => ({
      data: item.data,
      meta: {
        dimensions: `${item.width} × ${item.height}`,
        sizeText: item.sizeText,
        source: item.source
      }
    })),
    screenshot: screenshotList.value[0]?.data || null,
    screenshotMeta: screenshotList.value[0] ? {
      dimensions: `${screenshotList.value[0].width} × ${screenshotList.value[0].height}`,
      sizeText: screenshotList.value[0].sizeText,
      source: screenshotList.value[0].source
    } : null,
    errors: consoleErrors.value
  };

  try {
    const res = await fetch('/api/feedback', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(payload)
    });

    const data = await res.json();
    if (data && data.success) {
      submitStatus.value = {
        success: true,
        message: '✅ 已送达！AI 哨兵已捕获并开始分析，已自动为您切到进度追踪。'
      };
      feedbackText.value = '';
      clearAllScreenshots();
      await fetchHistory(true);
      setTimeout(() => {
        activeTab.value = 'history';
      }, 800);
    } else {
      throw new Error(data?.error || '服务端响应异常');
    }
  } catch (err) {
    submitStatus.value = {
      success: false,
      message: `发送失败: ${err.message}。您可点击右下角「复制报告」发到对话框。`
    };
  } finally {
    isSubmitting.value = false;
  }
}

function copyDiagnostics() {
  refreshDeviceInfo();
  const report = [
    `【真机调试反馈】`,
    `设备视口: ${deviceInfo.value.viewport} (DPR: ${deviceInfo.value.dpr})`,
    `所在页面: ${currentRouteText.value}`,
    `反馈内容: ${feedbackText.value.trim() || '（未输入具体文字）'}`,
    screenshotData.value ? `截图凭证: 已附带 (${screenshotMeta.value.dimensions} · ${screenshotMeta.value.sizeText})` : `截图凭证: 无`,
    consoleErrors.value.length > 0 ? `异常日志:\n- ${consoleErrors.value.join('\n- ')}` : `控制台状态: 正常 0 报错`
  ].join('\n');

  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(report).then(() => {
      copied.value = true;
      setTimeout(() => {
        copied.value = false;
      }, 2000);
    });
  } else {
    const ta = document.createElement('textarea');
    ta.value = report;
    document.body.appendChild(ta);
    ta.select();
    document.execCommand('copy');
    document.body.removeChild(ta);
    copied.value = true;
    setTimeout(() => {
      copied.value = false;
    }, 2000);
  }
}

onMounted(() => {
  setupSheetAutoSuppress();
  refreshDeviceInfo();
  fetchHistory(true).then(() => {
    checkAndSyncPolling();
  });

  if (typeof document !== 'undefined') {
    document.addEventListener('visibilitychange', () => {
      if (!document.hidden) {
        fetchHistory(true).then(() => {
          checkAndSyncPolling();
        });
      }
    });
  }
});

onUnmounted(() => {
  if (sheetObserver) sheetObserver.disconnect();
  if (pollTimer) {
    clearInterval(pollTimer);
    pollTimer = null;
  }
});
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
