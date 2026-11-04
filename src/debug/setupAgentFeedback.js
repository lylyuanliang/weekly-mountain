/**
 * 初始化 @agent-feedback/client 容器与全局事件监听
 * v1.3.0 已原生承载受限安全门禁 (Lockout Shield)、穿透通信持久化配置 (Settings Tab) 与宿主 GitHub 引导
 */
export function initAgentFeedbackExtensions(piniaInstance) {
  if (typeof window === 'undefined') return;

  const doRegister = () => {
    // 监听全局呼出反馈事件 (供个人中心或业务组件一键调起对应 Tab)
    window.addEventListener('wm-open-feedback', async (e) => {
      const tab = e.detail?.tab === 'history' ? 'history' : (e.detail?.tab === 'settings' ? 'settings' : 'submit');
      try {
        const { openFeedbackModal } = await import('@lylyuanliang/agent-feedback-client');
        openFeedbackModal(tab);
      } catch (err) {
        console.warn('[Alpine Debug] Failed to open feedback modal:', err);
      }
    });

    console.log('[Alpine Debug] Native @agent-feedback/client v1.3.0 initialized.');
  };

  if (document.readyState === 'loading') {
    window.addEventListener('DOMContentLoaded', doRegister);
  } else {
    doRegister();
  }
}
