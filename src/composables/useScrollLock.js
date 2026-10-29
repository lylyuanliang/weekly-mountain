import { watch, onBeforeUnmount, isRef } from 'vue';

let lockCount = 0;
let originalBodyOverflow = '';
let originalHtmlOverflow = '';
let originalPaddingRight = '';

/**
 * 锁定底层 document.body 及 document.documentElement 滚动
 * 支持引用计数：多个弹窗层叠打开时，仅在所有弹窗均关闭后恢复滚动
 */
export function lockScroll() {
  if (typeof document === 'undefined') return;

  if (lockCount === 0) {
    originalBodyOverflow = document.body.style.overflow || '';
    originalHtmlOverflow = document.documentElement.style.overflow || '';
    originalPaddingRight = document.body.style.paddingRight || '';

    // 若有垂直滚动条，补充 padding-right 防止 PC/桌面端页面布局跳动
    const scrollBarWidth = window.innerWidth - document.documentElement.clientWidth;
    if (scrollBarWidth > 0) {
      document.body.style.paddingRight = `${scrollBarWidth}px`;
    }

    document.documentElement.style.overflow = 'hidden';
    document.body.style.overflow = 'hidden';
    document.documentElement.classList.add('body-scroll-locked');
    document.body.classList.add('body-scroll-locked');
  }

  lockCount++;
}

/**
 * 解锁底层 document.body 滚动
 */
export function unlockScroll() {
  if (typeof document === 'undefined') return;

  lockCount = Math.max(0, lockCount - 1);

  if (lockCount === 0) {
    document.documentElement.style.overflow = originalHtmlOverflow;
    document.body.style.overflow = originalBodyOverflow;
    document.body.style.paddingRight = originalPaddingRight;
    document.documentElement.classList.remove('body-scroll-locked');
    document.body.classList.remove('body-scroll-locked');
  }
}

/**
 * 响应式滚动锁 Composable
 * @param {import('vue').Ref<boolean> | (() => boolean)} trigger 响应式布尔值或计算属性
 */
export function useScrollLock(trigger) {
  let isLocallyLocked = false;

  function applyLock(val) {
    if (val && !isLocallyLocked) {
      lockScroll();
      isLocallyLocked = true;
    } else if (!val && isLocallyLocked) {
      unlockScroll();
      isLocallyLocked = false;
    }
  }

  if (isRef(trigger) || typeof trigger === 'function') {
    watch(
      typeof trigger === 'function' ? trigger : () => trigger.value,
      (newVal) => applyLock(Boolean(newVal)),
      { immediate: true }
    );
  }

  onBeforeUnmount(() => {
    if (isLocallyLocked) {
      unlockScroll();
      isLocallyLocked = false;
    }
  });

  return {
    lock: () => applyLock(true),
    unlock: () => applyLock(false)
  };
}
