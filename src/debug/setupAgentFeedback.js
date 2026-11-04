/**
 * 初始化 @agent-feedback/client 容器与全局事件监听
 * v1.3.0 原生承载受限安全门禁 (Lockout Shield)、穿透通信持久化配置 (Settings Tab) 与宿主 GitHub 引导
 * 并注册每周一山定制的「📦 本地包」业务扩展插件
 */
export function initAgentFeedbackExtensions(piniaInstance) {
  if (typeof window === 'undefined') return;

  const doRegister = async () => {
    try {
      const [
        { registerExtensionTab, openFeedbackModal },
        { alpineDevApkTab }
      ] = await Promise.all([
        import('@lylyuanliang/agent-feedback-client'),
        import('./alpineDevApkPlugin.js')
      ]);

      // 注册业务定制插件：开发机本地构建 APK 直连下载与联调面板
      registerExtensionTab(alpineDevApkTab);

      // 监听全局呼出反馈事件 (供个人中心或业务组件一键调起对应 Tab)
      window.addEventListener('wm-open-feedback', async (e) => {
        const tab = e.detail?.tab || 'submit';
        try {
          openFeedbackModal(tab);
        } catch (err) {
          console.warn('[Alpine Debug] Failed to open feedback modal:', err);
        }
      });

      console.log('[Alpine Debug] Native @agent-feedback/client v1.3.0 with AlpineDevApkExtension initialized.');
    } catch (err) {
      console.warn('[Alpine Debug] Failed to register agent feedback extensions:', err);
    }
  };

  if (document.readyState === 'loading') {
    window.addEventListener('DOMContentLoaded', doRegister);
  } else {
    doRegister();
  }
}
