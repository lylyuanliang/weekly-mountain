import { createApp, watch } from 'vue';
import AlpineDebugExtensionView from '@/components/debug/AlpineDebugExtensionView.vue';
import { useDebugStore } from '@/stores/debugStore.js';

/**
 * 注册每周一山定制的「真机联调与更新」扩展 Tab 至 @agent-feedback/client 容器
 * 遵循通用插件架构，不污染 @agent-feedback/core 核心包
 */
export function initAgentFeedbackExtensions(piniaInstance) {
  if (typeof window === 'undefined') return;

  const doRegister = async () => {
    try {
      const { registerExtensionTab, setApiBase } = await import('@agent-feedback/client');

      // 绑定 DebugStore 的动态 API 基地址 (支持 Android 原生离线包走穿透服务)
      if (piniaInstance) {
        const debugStore = useDebugStore(piniaInstance);
        if (debugStore.apiBase) {
          setApiBase(debugStore.apiBase);
        }
        watch(
          () => debugStore.apiBase,
          (newBase) => {
            setApiBase(newBase);
          }
        );
      }

      registerExtensionTab({
        id: 'alpine-debug',
        label: '🛠️ 联调与更新',
        render(container) {
          const extApp = createApp(AlpineDebugExtensionView);
          if (piniaInstance) {
            extApp.use(piniaInstance);
          }
          extApp.mount(container);
          return () => {
            extApp.unmount();
          };
        }
      });

      // 监听全局呼出反馈事件 (供个人中心或 AlpineDebugModal 中的“提交真机反馈”/“查看处理进度”一键调起)
      window.addEventListener('wm-open-feedback', (e) => {
        const tab = e.detail?.tab === 'history' ? 'history' : 'submit';
        const widget = document.querySelector('agent-feedback-widget');
        if (widget) {
          if (typeof widget.toggleModal === 'function') widget.toggleModal(true);
          if (typeof widget.setTab === 'function') widget.setTab(tab);
        }
      });

      console.log('[Alpine Debug] Custom extension tab registered to @agent-feedback/client.');
    } catch (e) {
      console.warn('[Alpine Debug] Failed to register agent-feedback extension tab:', e);
    }
  };

  if (document.readyState === 'loading') {
    window.addEventListener('DOMContentLoaded', doRegister);
  } else {
    doRegister();
  }
}
