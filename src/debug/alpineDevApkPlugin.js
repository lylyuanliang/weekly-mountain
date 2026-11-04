/**
 * 每周一山业务定制插件：开发机本地构建 APK 直连下载与联调面板 (Dev APK Bridge)
 * 遵循 @agent-feedback/core 的 FeedbackExtensionTab 规范
 */
export const alpineDevApkTab = {
  id: 'alpine-dev-apk',
  label: '本地包',
  icon: '📦',
  async render(container) {
    const [{ createApp }, { default: AlpineDevApkExtensionView }] = await Promise.all([
      import('vue'),
      import('@/components/debug/AlpineDevApkExtensionView.vue')
    ]);
    const app = createApp(AlpineDevApkExtensionView);
    app.mount(container);
    return () => {
      app.unmount();
    };
  }
};
