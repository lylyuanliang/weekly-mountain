/**
 * 初始化 @agent-feedback/client 容器与全局事件监听
 * v1.3.0 原生承载受限安全门禁 (Lockout Shield)、穿透通信持久化配置 (Settings Tab) 与宿主 GitHub 引导
 * 并注册每周一山定制的「📦 本地包」业务扩展插件
 */
export function initAgentFeedbackExtensions(piniaInstance) {
  if (typeof window === 'undefined') return;

  // 1. 提取构建期注入的安全门禁与宿主渠道配置
  const acConfig = typeof __WM_ACCESS_CONTROL_CONFIG__ !== 'undefined'
    ? __WM_ACCESS_CONTROL_CONFIG__
    : { enabled: true };

  const hostChannelConfig = {
    name: 'GitHub Issues',
    url: 'https://github.com/lylyuanliang/weekly-mountain/issues',
    description: '未持有内测密钥时，请前往 GitHub 提交建议与问题反馈'
  };

  // 2. 注入 window.__AGENT_FEEDBACK_OPTIONS__，确保离线 Debug APK 无论在 Web 还是原生容器下
  // 均能激活原生「⚙️ 联调设置」(Settings) Tab 与配对安全门禁
  if (!window.__AGENT_FEEDBACK_OPTIONS__) {
    window.__AGENT_FEEDBACK_OPTIONS__ = {
      showSettings: true,
      accessControl: acConfig,
      hostChannel: hostChannelConfig,
      sentinel: {
        autoStart: true,
        debounceSeconds: 10
      }
    };
  } else {
    window.__AGENT_FEEDBACK_OPTIONS__.showSettings = true;
    if (!window.__AGENT_FEEDBACK_OPTIONS__.accessControl) {
      window.__AGENT_FEEDBACK_OPTIONS__.accessControl = acConfig;
    }
    if (!window.__AGENT_FEEDBACK_OPTIONS__.hostChannel) {
      window.__AGENT_FEEDBACK_OPTIONS__.hostChannel = hostChannelConfig;
    }
  }

  const doRegister = async () => {
    try {
      const [
        client,
        { alpineDevApkTab }
      ] = await Promise.all([
        import('@lylyuanliang/agent-feedback-client'),
        import('./alpineDevApkPlugin.js')
      ]);

      // 3. 显式同步设置到客户端运行时
      if (client.setAccessControl) {
        client.setAccessControl(acConfig);
      }
      if (client.setHostChannel) {
        client.setHostChannel(hostChannelConfig);
      }

      // 【核心自愈】启动时若已配置穿透基地址且本地存在缓存秘钥，自动静默同步开发机最新门禁配置
      // 彻底根治本地秘钥已缓存但在重启或更新后显示未配对、必须手动点击“测试连通性”才能唤醒的体验 Bug
      if (typeof client.syncAccessControlFromServer === 'function') {
        try {
          const savedBase = (typeof localStorage !== 'undefined')
            ? (localStorage.getItem('af_api_base') || localStorage.getItem('wm_debug_tunnel_url') || '').trim()
            : '';
          if (savedBase) {
            client.syncAccessControlFromServer(savedBase).catch(() => {});
          }
        } catch (_) {}
      }

      // 4. 注册业务定制插件：开发机本地构建 APK 直连下载与联调面板
      client.registerExtensionTab(alpineDevApkTab);

      // 5. 监听全局呼出反馈事件 (供个人中心或业务组件一键调起对应 Tab)
      window.addEventListener('wm-open-feedback', async (e) => {
        const tab = e.detail?.tab || 'submit';
        try {
          client.openFeedbackModal(tab);
        } catch (err) {
          console.warn('[Alpine Debug] Failed to open feedback modal:', err);
        }
      });

      console.log('[Alpine Debug] Native @agent-feedback/client v1.3.0 initialized with Settings and DevApkExtension.');
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
