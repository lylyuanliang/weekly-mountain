import { defineStore } from 'pinia';
import { ref } from 'vue';

export const THEME_STORAGE_KEY = 'weekly_mountain_theme';
export const AVAILABLE_THEMES = ['stitch', 'ink', 'camp'];

function getThemeFromStorage() {
  try {
    if (typeof localStorage !== 'undefined') {
      const val = localStorage.getItem(THEME_STORAGE_KEY);
      if (val) {
        const cleaned = val.replace(/^["']|["']$/g, '');
        if (AVAILABLE_THEMES.includes(cleaned)) return cleaned;
      }
    }
  } catch (e) {
    console.warn('Failed to parse theme from localStorage', e);
  }
  return 'stitch';
}

function updateDomTheme(themeName) {
  if (typeof document !== 'undefined' && document.documentElement) {
    document.documentElement.setAttribute('data-theme', themeName);
  }
}

export const useThemeStore = defineStore('theme', () => {
  const theme = ref(getThemeFromStorage());

  // 初始化设置 DOM data-theme
  updateDomTheme(theme.value);

  function setTheme(newTheme) {
    if (!AVAILABLE_THEMES.includes(newTheme)) {
      newTheme = 'stitch';
    }
    theme.value = newTheme;
    try {
      if (typeof localStorage !== 'undefined') {
        localStorage.setItem(THEME_STORAGE_KEY, newTheme);
      }
    } catch (e) {
      console.warn('Failed to save theme to localStorage', e);
    }
    updateDomTheme(newTheme);
  }

  function cycleTheme() {
    const idx = AVAILABLE_THEMES.indexOf(theme.value);
    const nextIdx = (idx + 1) % AVAILABLE_THEMES.length;
    setTheme(AVAILABLE_THEMES[nextIdx]);
  }

  return {
    theme,
    setTheme,
    cycleTheme
  };
});
