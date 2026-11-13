import { createApp } from 'vue';
import AlpineDevApkExtensionView from '@/components/debug/AlpineDevApkExtensionView.vue';

/**
 * 每周一山业务定制插件：开发机本地构建 APK 直连下载与联调面板 (Dev APK Bridge)
 * 遵循 @agent-feedback/core 的 FeedbackExtensionTab 规范
 * 原生同步快速挂载，消除动态 chunk 导入延迟引起的布局抖动
 */
export const alpineDevApkTab = {
  id: 'alpine-dev-apk',
  label: '本地包',
  icon: '📦',
  render(container) {
    const app = createApp(AlpineDevApkExtensionView);
    app.mount(container);
    return () => {
      app.unmount();
    };
  }
};
