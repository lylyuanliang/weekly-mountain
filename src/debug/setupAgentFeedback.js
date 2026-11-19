import { initAgentFeedback, registerExtensionTab, openFeedbackModal } from '@lylyuanliang/agent-feedback-client';
import { alpineDevApkTab } from './alpineDevApkPlugin.js';

/**
 * 初始化 @agent-feedback/client 官方原生容器与全局事件监听
 * 遵循官方标准 API，0 补丁侵入、0 样板代码
 */
export function initAgentFeedbackExtensions() {
  if (typeof window === 'undefined') return;

  // 1. 调用官方推荐标准入口：自动注入选项、开启联调设置、装配安全门禁与处理 DOM 守候
  initAgentFeedback({
    appName: '每周一山',
    primaryColor: '#4edea3',
    hostChannel: {
      name: 'GitHub Issues',
      url: 'https://github.com/lylyuanliang/weekly-mountain/issues',
      description: '未持有内测密钥时，请前往 GitHub 提交建议与问题反馈'
    }
  });

  // 2. 注册业务定制扩展槽：开发机本地构建 APK 直连下载与联调面板
  registerExtensionTab(alpineDevApkTab);

  // 3. 监听全局呼出反馈事件 (供个人中心或业务调试面板一键唤起对应 Tab)
  window.addEventListener('wm-open-feedback', (e) => {
    const tab = e.detail?.tab || 'submit';
    try {
      openFeedbackModal(tab);
    } catch (err) {
      console.warn('[Alpine Debug] Failed to open feedback modal:', err);
    }
  });

  console.log('[Alpine Debug] Native @agent-feedback/client initialized with official clean API.');
}
