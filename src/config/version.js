/**
 * 应用版本与构建时间元数据
 * 规范：前三位为发布版本 (0.0.1)，第 4 位为内部调试/内测递增号 (001, 002...)
 * 供主页、详情抽屉、全屏大图、导航弹窗及个人中心统一展示
 */
export const APP_VERSION = '0.0.1.005';
export const RELEASE_VERSION = '0.0.1';
export const BUILD_DATE = '2026-10-26';
export const BUILD_TIME = '19:15';
export const BUILD_TIMESTAMP = '2026-10-26 19:15';
export const BUILD_CODE = 5;

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
 * 动态读取环境变量 VITE_TUNNEL_URL (配置于 .env.local)，未配置时安全回退为空字符串，严禁硬编码敏感私有域名
 */
export const DEFAULT_CPOLAR_TUNNEL = import.meta.env.VITE_TUNNEL_URL || '';
