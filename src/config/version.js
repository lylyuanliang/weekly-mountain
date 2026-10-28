/**
 * 应用版本与构建时间元数据
 * 规范：前三位为发布版本 (0.0.1)，第 4 位为内部调试/内测递增号 (001, 002...)
 * 供主页、详情抽屉、全屏大图、导航弹窗及个人中心统一展示
 */
export const APP_VERSION = '0.0.1.202610281816';
export const RELEASE_VERSION = '0.0.1';
export const BUILD_DATE = '2026-10-28';
export const BUILD_TIME = '18:16';
export const BUILD_TIMESTAMP = '2026-10-28 18:16';
export const BUILD_CODE = 1793182577;

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
 * 远程穿透与联调服务器地址（用于 App 内真机反馈与在线 OTA 更新）
 * 仅在调试/内测构建 (IS_DEBUG_BUILD = true) 时读取配置，Release 纯净版强制置空并由构建期死代码消除 (DCE) 彻底剔除，杜绝逆向泄露
 */
export const DEFAULT_CPOLAR_TUNNEL = IS_DEBUG_BUILD ? (import.meta.env.VITE_TUNNEL_URL || '') : '';
