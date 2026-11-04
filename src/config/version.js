/**
 * 应用版本与构建时间元数据
 * 规范：前三位为发布版本 (0.0.1)，第 4 位为内部调试/内测递增号 (001, 002...)
 * 供主页、详情抽屉、全屏大图、导航弹窗及个人中心统一展示
 */
import { isNativeApp } from '@/utils/platform.js';

export const APP_VERSION = '0.3.0.202611041718';
export const RELEASE_VERSION = '0.3.0';
export const BUILD_DATE = '2026-11-04';
export const BUILD_TIME = '17:18';
export const BUILD_TIMESTAMP = '2026-11-04 17:18';
export const BUILD_CODE = 1793783884;

/**
 * 开发者调试与 AI 移动端反馈入口开关
 * 默认模式为调试内测开启 (true)；纯净发布/外部内测变体 (VITE_ENABLE_DEBUG=false) 自动剥离
 */
export const IS_DEBUG_BUILD = import.meta.env.VITE_ENABLE_DEBUG !== 'false';
export const BUILD_VARIANT = IS_DEBUG_BUILD ? 'debug' : 'release';
export const VERSION_LABEL = IS_DEBUG_BUILD
  ? `v${APP_VERSION} (${BUILD_TIMESTAMP})`
  : `v${APP_VERSION} (内测体验版)`;

/**
 * 平台感知动态版本标签
 * 原生 App 环境：展示原生构建版本（内测/调试版）
 * 网页 Web 环境：展示 Web 版专属标识，消除更新安装概念困惑
 */
export function getVersionLabel() {
  if (!isNativeApp()) {
    return IS_DEBUG_BUILD
      ? `v${APP_VERSION} (Web Dev)`
      : `v${RELEASE_VERSION} (Web版)`;
  }
  return VERSION_LABEL;
}

/**
 * 远程穿透与联调服务器地址（用于 App 内真机反馈与在线 OTA 更新）
 * 仅在调试/内测构建 (IS_DEBUG_BUILD = true) 时读取配置，Release 纯净版强制置空并由构建期死代码消除 (DCE) 彻底剔除，杜绝逆向泄露
 */
export const DEFAULT_CPOLAR_TUNNEL = IS_DEBUG_BUILD ? (import.meta.env.VITE_TUNNEL_URL || '') : '';
