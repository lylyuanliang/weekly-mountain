import { createApp } from 'vue';
import AlpineDebugExtensionView from '@/components/debug/AlpineDebugExtensionView.vue';

/**
 * 注册每周一山定制的「真机联调与更新」扩展 Tab 至 @agent-feedback/client 容器
 * 遵循通用插件架构，不污染 @agent-feedback/core 核心包
 */
export function initAgentFeedbackExtensions(piniaInstance) {
  if (typeof window === 'undefined') return;

  const doRegister = async () => {
    try {
      const { registerExtensionTab } = await import('@agent-feedback/client');
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
