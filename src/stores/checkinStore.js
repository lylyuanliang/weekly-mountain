import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import mountainsData from '../data/mountains.json' with { type: 'json' };
import { usePlanStore } from './planStore.js';
import { useThemeStore } from './themeStore.js';

export const CHECKED_STORAGE_KEY = 'weekly_mountain_checked';
export const CHECKIN_RECORDS_STORAGE_KEY = 'weekly_mountain_checkin_records';

/**
 * 将图片文件压缩为 Base64 格式（优先 WebP，降级 JPEG）
 * 限制最大尺寸与质量，防止 LocalStorage 配额超限
 * @param {File|Blob} file 原始图片文件
 * @param {number} maxDimension 最大边长像素
 * @param {number} quality 压缩质量 (0.1 ~ 1.0)
 * @returns {Promise<string>} Base64 Data URL
 */
export async function compressImageToBase64(file, maxDimension = 960, quality = 0.75) {
  return new Promise((resolve, reject) => {
    if (!file) {
      return reject(new Error('未提供有效图片'));
    }
    if (typeof FileReader === 'undefined' || typeof Image === 'undefined') {
      return reject(new Error('当前运行环境不支持图片处理'));
    }

    const reader = new FileReader();
    reader.onerror = () => reject(new Error('读取图片文件失败'));
    reader.onload = (e) => {
      const img = new Image();
      img.onerror = () => reject(new Error('解析图片资源失败'));
      img.onload = () => {
        let width = img.width;
        let height = img.height;

        if (width > maxDimension || height > maxDimension) {
          if (width > height) {
            height = Math.round((height * maxDimension) / width);
            width = maxDimension;
          } else {
            width = Math.round((width * maxDimension) / height);
            height = maxDimension;
          }
        }

        const canvas = document.createElement('canvas');
        canvas.width = width;
        canvas.height = height;
        const ctx = canvas.getContext('2d');
        if (!ctx) {
          return resolve(e.target.result);
        }

        ctx.drawImage(img, 0, 0, width, height);

        let dataUrl = '';
        try {
          dataUrl = canvas.toDataURL('image/webp', quality);
          if (!dataUrl.startsWith('data:image/webp')) {
            dataUrl = canvas.toDataURL('image/jpeg', quality);
          }
        } catch (err) {
          dataUrl = canvas.toDataURL('image/jpeg', quality);
        }

        resolve(dataUrl);
      };
      img.src = e.target.result;
    };
    reader.readAsDataURL(file);
  });
}

export function numOr(v) {
  if (v == null) return "";
  if (typeof v === "number") return isFinite(v) ? v : "";
  const m = String(v).match(/-?\d+(\.\d+)?/);
  return m ? Number(m[0]) : "";
}

/**
 * 顶层数值缺失时，从 routes / route_detail 推导，避免数据失真
 */
export function derivedNums(m) {
  if (!m) return { alt: 0, dist: 0, asc: 0, dur: 0 };
  const out = {
    alt: numOr(m.altitude_m) || 0,
    dist: numOr(m.distance_km) || 0,
    asc: numOr(m.ascent_m) || 0,
    dur: numOr(m.duration_h) || 0
  };
  const r0 = (Array.isArray(m.routes) && m.routes[0]) || {};
  if (!out.dist) out.dist = numOr(r0.dist_km) || 0;
  if (!out.asc) out.asc = numOr(r0.ascent_m) || 0;
  if (!out.dur) out.dur = numOr(r0.time_h) || 0;
  const rds = Array.isArray(m.route_detail) ? m.route_detail : [];

  // 选「常规一日主徒步线」：排除景区观光车线与多日穿越线，取里程最长者
  let best = null, bestKm = 0;
  for (const r of rds) {
    if (!Array.isArray(r.segments)) continue;
    const label = String(r.name || "") + String(r.terrain || "") + String(r.difficulty_note || "");
    if (/观光车|景区车|中转车|索道|骑马/.test(label)) continue;
    if (/穿越|多日|2天|两天|3天|三天|天露营|大环线/.test(label)) continue;
    const km = r.segments.reduce((s, x) => s + (numOr(x.km) || 0), 0);
    if (km > bestKm) { bestKm = km; best = r; }
  }
  if (!best) {
    for (const r of rds) {
      if (!Array.isArray(r.segments)) continue;
      const km = r.segments.reduce((s, x) => s + (numOr(x.km) || 0), 0);
      if (km > bestKm) { bestKm = km; best = r; }
    }
  }
  if (best) {
    let topAlt = 0, lowAlt = 0;
    best.segments.forEach((s, i) => {
      const a = numOr(s.alt_m) || 0;
      if (a > topAlt) topAlt = a;
      if (i === 0 && a) lowAlt = a;
    });
    if (!out.alt && topAlt) out.alt = topAlt;
    if (!out.dist) out.dist = Math.round(best.segments.reduce((s, x) => s + (numOr(x.km) || 0), 0) * 10) / 10;
    if (!out.asc && topAlt && lowAlt && topAlt > lowAlt) out.asc = topAlt - lowAlt;
  }
  return out;
}

export function getRank(doneCount) {
  if (doneCount >= 25) return { level: 'LV.5', title: '传奇巅峰' };
  if (doneCount >= 15) return { level: 'LV.4', title: '巅峰行者' };
  if (doneCount >= 8) return { level: 'LV.3', title: '进阶高山' };
  if (doneCount >= 3) return { level: 'LV.2', title: '荒野探索' };
  return { level: 'LV.1', title: '初探山岳' };
}

function getCheckedFromStorage() {
  try {
    if (typeof localStorage !== 'undefined') {
      const raw = localStorage.getItem(CHECKED_STORAGE_KEY);
      if (raw) {
        const parsed = JSON.parse(raw);
        if (Array.isArray(parsed)) return parsed;
        if (typeof parsed === 'object' && parsed !== null) return Object.keys(parsed);
      }
    }
  } catch (e) {
    console.warn('Failed to parse checked mountains from localStorage', e);
  }
  return [];
}

function saveCheckedToStorage(ids) {
  try {
    if (typeof localStorage !== 'undefined') {
      localStorage.setItem(CHECKED_STORAGE_KEY, JSON.stringify(ids));
    }
  } catch (e) {
    console.warn('Failed to save checked mountains to localStorage', e);
  }
}

function getRecordsFromStorage() {
  try {
    if (typeof localStorage !== 'undefined') {
      const raw = localStorage.getItem(CHECKIN_RECORDS_STORAGE_KEY);
      if (raw) {
        const parsed = JSON.parse(raw);
        if (parsed && typeof parsed === 'object' && !Array.isArray(parsed)) {
          return parsed;
        }
      }
    }
  } catch (e) {
    console.warn('Failed to parse checkin records from localStorage', e);
  }
  return {};
}

function saveRecordsToStorage(records) {
  try {
    if (typeof localStorage !== 'undefined') {
      localStorage.setItem(CHECKIN_RECORDS_STORAGE_KEY, JSON.stringify(records));
    }
  } catch (e) {
    console.warn('Failed to save checkin records to localStorage', e);
  }
}

export const useCheckinStore = defineStore('checkin', () => {
  const checkedIds = ref(getCheckedFromStorage());
  const checkinRecords = ref(getRecordsFromStorage());

  function isDone(id) {
    return checkedIds.value.includes(id);
  }

  function toggleCheckin(id) {
    if (isDone(id)) {
      checkedIds.value = checkedIds.value.filter((x) => x !== id);
    } else {
      checkedIds.value = [...checkedIds.value, id];
      if (!checkinRecords.value[id]) {
        checkinRecords.value = {
          ...checkinRecords.value,
          [id]: {
            checkedAt: new Date().toISOString(),
            photoUrl: '',
            note: ''
          }
        };
        saveRecordsToStorage(checkinRecords.value);
      }
    }
    saveCheckedToStorage(checkedIds.value);
  }

  function setChecked(ids) {
    checkedIds.value = Array.isArray(ids) ? [...ids] : [];
    saveCheckedToStorage(checkedIds.value);
  }

  /**
   * 保存或更新某座山的打卡详情（包含实景照片 Base64 与探索心得随笔）
   * @param {string} mountainId 山峰 ID
   * @param {Object} detail 详情对象 { photoUrl, note, checkedAt }
   */
  function saveCheckinDetail(mountainId, detail = {}) {
    if (!mountainId) return null;

    if (!isDone(mountainId)) {
      checkedIds.value = [...checkedIds.value, mountainId];
      saveCheckedToStorage(checkedIds.value);
    }

    const prev = checkinRecords.value[mountainId] || {};
    const updated = {
      checkedAt: detail.checkedAt || prev.checkedAt || new Date().toISOString(),
      photoUrl: detail.photoUrl !== undefined ? detail.photoUrl : (prev.photoUrl || ''),
      note: detail.note !== undefined ? detail.note : (prev.note || '')
    };

    checkinRecords.value = {
      ...checkinRecords.value,
      [mountainId]: updated
    };
    saveRecordsToStorage(checkinRecords.value);
    return updated;
  }

  /**
   * 获取某座山的打卡详情记录
   * @param {string} mountainId 山峰 ID
   * @returns {Object|null}
   */
  function getCheckinRecord(mountainId) {
    if (!mountainId) return null;
    const record = checkinRecords.value[mountainId];
    if (record) return record;
    if (isDone(mountainId)) {
      return {
        checkedAt: new Date().toISOString(),
        photoUrl: '',
        note: ''
      };
    }
    return null;
  }

  /**
   * 删除某座山的打卡照片或重置打卡详情
   * @param {string} mountainId 山峰 ID
   */
  function removeCheckinPhoto(mountainId) {
    if (!mountainId || !checkinRecords.value[mountainId]) return;
    const prev = checkinRecords.value[mountainId];
    checkinRecords.value = {
      ...checkinRecords.value,
      [mountainId]: {
        ...prev,
        photoUrl: ''
      }
    };
    saveRecordsToStorage(checkinRecords.value);
  }

  const stats = computed(() => {
    let asc = 0;
    let dist = 0;
    const mountainMap = new Map(mountainsData.map((m) => [m.id, m]));

    checkedIds.value.forEach((id) => {
      const m = mountainMap.get(id);
      if (m) {
        const dn = derivedNums(m);
        asc += dn.asc || 0;
        dist += dn.dist || 0;
      }
    });

    const doneCount = checkedIds.value.length;
    const totalDistance = Math.round(dist * 10) / 10;
    const completionRate = mountainsData.length
      ? Math.round((doneCount / mountainsData.length) * 100)
      : 0;
    const rank = getRank(doneCount);

    return {
      doneCount,
      totalAscent: asc,
      totalDistance,
      completionRate,
      rank
    };
  });

  function exportBackup() {
    let plans = [];
    let theme = 'stitch';
    try {
      const planStore = usePlanStore();
      plans = planStore.plans;
    } catch (e) {}
    try {
      const themeStore = useThemeStore();
      theme = themeStore.theme;
    } catch (e) {}

    const payload = {
      version: 2,
      exported_at: new Date().toISOString().slice(0, 10),
      checked: [...checkedIds.value],
      checkinRecords: JSON.parse(JSON.stringify(checkinRecords.value)),
      plans: JSON.parse(JSON.stringify(plans)),
      theme
    };
    return JSON.stringify(payload, null, 2);
  }

  function importBackup(jsonStr) {
    try {
      const data = typeof jsonStr === 'string' ? JSON.parse(jsonStr) : jsonStr;
      if (!data || typeof data !== 'object') throw new Error('无效的备份数据');

      // 1. 兼容原版单页 JSON 结构 { state: { theme, done, plan } }
      if (data.state && typeof data.state === 'object') {
        const st = data.state;
        if (st.done && typeof st.done === 'object') {
          checkedIds.value = Object.keys(st.done);
          saveCheckedToStorage(checkedIds.value);
        }
        if (st.plan && Array.isArray(st.plan.weeks)) {
          try {
            const planStore = usePlanStore();
            planStore.plans = st.plan.weeks.map((w, i) => ({
              week: i + 1,
              t: w.t || `第${i + 1}周`,
              items: Array.isArray(w.items) ? [...w.items] : []
            }));
            if (typeof localStorage !== 'undefined') {
              localStorage.setItem('weekly_mountain_plans', JSON.stringify(planStore.plans));
            }
          } catch (e) {}
        }
        if (st.theme) {
          try {
            const themeStore = useThemeStore();
            themeStore.setTheme(st.theme);
          } catch (e) {}
        }
        return true;
      }

      // 2. 现代解耦备份结构
      if (Array.isArray(data.checked)) {
        checkedIds.value = [...data.checked];
      } else if (Array.isArray(data.checkedIds)) {
        checkedIds.value = [...data.checkedIds];
      }
      saveCheckedToStorage(checkedIds.value);

      if (data.checkinRecords && typeof data.checkinRecords === 'object') {
        checkinRecords.value = { ...data.checkinRecords };
        saveRecordsToStorage(checkinRecords.value);
      }

      if (Array.isArray(data.plans)) {
        try {
          const planStore = usePlanStore();
          planStore.plans = [...data.plans];
          if (typeof localStorage !== 'undefined') {
            localStorage.setItem('weekly_mountain_plans', JSON.stringify(planStore.plans));
          }
        } catch (e) {}
      }

      if (data.theme) {
        try {
          const themeStore = useThemeStore();
          themeStore.setTheme(data.theme);
        } catch (e) {}
      }

      return true;
    } catch (err) {
      console.error('importBackup failed:', err);
      return false;
    }
  }

  return {
    checkedIds,
    checkinRecords,
    isDone,
    toggleCheckin,
    setChecked,
    saveCheckinDetail,
    getCheckinRecord,
    removeCheckinPhoto,
    stats,
    exportBackup,
    importBackup
  };
});
