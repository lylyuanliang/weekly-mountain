/**
 * 平台环境与运行形态感知工具库 (Platform Detector)
 * 精确识别当前运行环境为 Capacitor 原生移动 App (Android/iOS) 还是纯 Web 浏览器 (Cloudflare Pages/移动Web/微信等)
 */
import { Capacitor } from '@capacitor/core';

/**
 * 判断当前运行环境是否为原生 App (Capacitor Android / iOS)
 * 采用多层防御检测：
 * 1. URL 调试开关或 localStorage 模拟标记 (?native=1 / wm_force_native=true)
 * 2. Capacitor.isNativePlatform() 官方 API 检测
 * 3. 协议判断 (capacitor: / ionic:)
 * 4. Android 原生宿主 WebView 注入对象 (window.AlpineNative)
 * @returns {boolean}
 */
export function isNativeApp() {
  if (typeof window === 'undefined') return false;

  // 允许通过 URL 参数或 localStorage 在浏览器端便捷模拟原生容器形态
  if (
    window.location.search.includes('native=1') ||
    window.location.hash.includes('native=1') ||
    window.localStorage.getItem('wm_force_native') === 'true'
  ) {
    return true;
  }

  try {
    if (Capacitor && typeof Capacitor.isNativePlatform === 'function' && Capacitor.isNativePlatform()) {
      return true;
    }
  } catch {}

  if (window.Capacitor && typeof window.Capacitor.isNativePlatform === 'function') {
    if (window.Capacitor.isNativePlatform()) return true;
  }

  return (
    window.location.protocol === 'capacitor:' ||
    window.location.protocol === 'ionic:' ||
    Boolean(window.AlpineNative)
  );
}

/**
 * 判断当前运行环境是否为 Web 浏览器端 (包含桌面浏览器、手机浏览器、微信/QQ内置浏览器等)
 * @returns {boolean}
 */
export function isWebPlatform() {
  return !isNativeApp();
}

/**
 * 获取当前运行平台标识
 * @returns {'android' | 'ios' | 'web'}
 */
export function getPlatform() {
  if (isNativeApp()) {
    try {
      if (Capacitor && typeof Capacitor.getPlatform === 'function') {
        const p = Capacitor.getPlatform();
        if (p === 'android' || p === 'ios') return p;
      }
    } catch {}

    if (typeof navigator !== 'undefined') {
      if (/Android/i.test(navigator.userAgent)) return 'android';
      if (/(iPhone|iPad|iPod)/i.test(navigator.userAgent)) return 'ios';
    }
    return 'android';
  }
  return 'web';
}
