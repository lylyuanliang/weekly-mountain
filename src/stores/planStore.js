import { defineStore } from 'pinia';
import { ref } from 'vue';

export const PLANS_STORAGE_KEY = 'weekly_mountain_plans';

export const REC_PRESETS = [
  {
    id: "autumn8",
    name: "秋季彩林云海 · 8 周",
    desc: "9-11 月正当季：红叶、云海、观景平台一条龙，由近及远排开，强度缓升。",
    weeks: [
      "jiufengshan",
      "bipenggou",
      "songpinggou",
      "liangtaigou",
      "dawagengzha",
      "niubeishan",
      "jiaodingshan",
      "jiguanshan-liuliba"
    ]
  },
  {
    id: "starter6",
    name: "入门阶梯 · 6 周",
    desc: "从城市绿心到名山古道，难度 L1→L2 缓慢爬坡，适合和女朋友从零起步。",
    weeks: [
      "longquanshan",
      "yulei-songmao",
      "hongkou-gaoyuan",
      "qingcheng-houshan",
      "tiantai-qionglai",
      "mengdingshan"
    ]
  },
  {
    id: "seacloud4",
    name: "云海观景台 · 4 连",
    desc: "成都周边四大观景平台连打，注意提前订房、看天气窗口再出发。",
    weeks: [
      "niubeishan",
      "dawagengzha",
      "jiaodingshan",
      "xiling-xueshan"
    ]
  },
  {
    id: "snow3",
    name: "雪山近观 · 3 连",
    desc: "索道+自驾观景看雪山，冬季路线，出发前查防滑链与封路信息。",
    weeks: [
      "xiling-xueshan",
      "balangshan",
      "dawagengzha"
    ]
  }
];

export function createWeek(weekNum, items = []) {
  const list = Array.isArray(items) ? [...items] : [];
  return {
    week: weekNum,
    t: `第${weekNum}周`,
    items: list,
    get mountainIds() {
      return this.items;
    },
    set mountainIds(val) {
      this.items = val;
    }
  };
}

function getPlansFromStorage() {
  try {
    if (typeof localStorage !== 'undefined') {
      const raw = localStorage.getItem(PLANS_STORAGE_KEY);
      if (raw) {
        const parsed = JSON.parse(raw);
        if (Array.isArray(parsed)) {
          return parsed.map((w, i) =>
            createWeek(w.week || i + 1, w.items || w.mountainIds || (Array.isArray(w) ? w : []))
          );
        }
      }
    }
  } catch (e) {
    console.warn('Failed to parse plans from localStorage', e);
  }
  return [];
}

function savePlansToStorage(plans) {
  try {
    if (typeof localStorage !== 'undefined') {
      localStorage.setItem(PLANS_STORAGE_KEY, JSON.stringify(plans));
    }
  } catch (e) {
    console.warn('Failed to save plans to localStorage', e);
  }
}

export const usePlanStore = defineStore('plan', () => {
  const plans = ref(getPlansFromStorage());

  function addToPlan(mid, week) {
    let targetWeekNum = typeof week === 'number' ? week : null;

    if (targetWeekNum === null) {
      if (plans.value.length === 0) {
        targetWeekNum = 1;
      } else {
        targetWeekNum = plans.value.length;
      }
    } else if (targetWeekNum <= 0) {
      targetWeekNum = 1;
    }

    // 确保已有指定周
    while (plans.value.length < targetWeekNum) {
      const nextNum = plans.value.length + 1;
      plans.value.push(createWeek(nextNum));
    }

    const targetWeek = plans.value[targetWeekNum - 1];
    if (targetWeek && !targetWeek.items.includes(mid)) {
      targetWeek.items.push(mid);
    }

    savePlansToStorage(plans.value);
  }

  function removeFromPlan(mid, week) {
    if (typeof week === 'number' && week > 0 && week <= plans.value.length) {
      const targetWeek = plans.value[week - 1];
      if (targetWeek) {
        targetWeek.items = targetWeek.items.filter((id) => id !== mid);
      }
    } else {
      plans.value.forEach((w) => {
        w.items = w.items.filter((id) => id !== mid);
      });
    }

    savePlansToStorage(plans.value);
  }

  function applyPreset(presetKey, mode = 'replace') {
    let preset = REC_PRESETS.find((p) => p.id === presetKey);
    if (!preset) {
      preset = REC_PRESETS.find(
        (p) =>
          p.name.includes(presetKey) ||
          p.desc.includes(presetKey) ||
          (presetKey === '川西日出云海线' && p.id === 'seacloud4') ||
          (presetKey === 'sunrise_clouds' && p.id === 'seacloud4')
      );
    }
    if (!preset) {
      console.warn(`Preset ${presetKey} not found`);
      return false;
    }

    const newWeeks = preset.weeks.map((mid, i) => createWeek(i + 1, [mid]));

    if (mode === 'append') {
      const base = plans.value.length;
      newWeeks.forEach((w, i) => {
        plans.value.push(createWeek(base + i + 1, w.items));
      });
    } else {
      plans.value = newWeeks;
    }

    savePlansToStorage(plans.value);
    return true;
  }

  function addNewWeek() {
    const nextWeekNum = plans.value.length + 1;
    const newWeek = createWeek(nextWeekNum, []);
    plans.value.push(newWeek);
    savePlansToStorage(plans.value);
    return newWeek;
  }

  function removeWeek(weekNum) {
    const idx = plans.value.findIndex((w) => w.week === weekNum);
    if (idx !== -1) {
      plans.value.splice(idx, 1);
      // 重新连续编号
      plans.value.forEach((w, i) => {
        w.week = i + 1;
        w.t = `第${i + 1}周`;
      });
      savePlansToStorage(plans.value);
    }
  }

  function clearPlans() {
    plans.value = [];
    savePlansToStorage(plans.value);
  }

  return {
    plans,
    addToPlan,
    removeFromPlan,
    addNewWeek,
    removeWeek,
    applyPreset,
    clearPlans
  };
});
