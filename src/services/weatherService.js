/**
 * 实时天气数据服务 (Open-Meteo 高精度气象模型)
 * 免 API Key，基于经纬度网格预报未来 7 天高海拔天气
 */
import waypointsData from '@/data/waypoints.json';

// WMO 天气代码标准映射表
export const WMO_MAP = {
  0: { icon: '☀️', text: '晴朗', code: 0 },
  1: { icon: '🌤', text: '多云间晴', code: 1 },
  2: { icon: '⛅', text: '多云', code: 2 },
  3: { icon: '☁️', text: '阴天', code: 3 },
  45: { icon: '🌫', text: '山间大雾', code: 45 },
  48: { icon: '🌫', text: '雾凇覆冰', code: 48 },
  51: { icon: '🌦', text: '小毛毛雨', code: 51 },
  53: { icon: '🌦', text: '毛毛雨', code: 53 },
  55: { icon: '🌧', text: '大毛毛雨', code: 55 },
  61: { icon: '🌦', text: '小雨', code: 61 },
  63: { icon: '🌧', text: '中雨', code: 63 },
  65: { icon: '🌧', text: '大雨', code: 65 },
  66: { icon: '🌧', text: '冻雨', code: 66 },
  67: { icon: '🌧', text: '强冻雨', code: 67 },
  71: { icon: '🌨', text: '小雪', code: 71 },
  73: { icon: '🌨', text: '中雪', code: 73 },
  75: { icon: '❄️', text: '大雪', code: 75 },
  77: { icon: '🌨', text: '米雪', code: 77 },
  80: { icon: '🌦', text: '阵雨', code: 80 },
  81: { icon: '🌧', text: '强阵雨', code: 81 },
  82: { icon: '⛈', text: '短时暴雨', code: 82 },
  85: { icon: '🌨', text: '高山阵雪', code: 85 },
  86: { icon: '❄️', text: '强阵雪', code: 86 },
  95: { icon: '⛈', text: '雷阵雨', code: 95 },
  96: { icon: '⛈', text: '雷雨伴冰雹', code: 96 },
  99: { icon: '⛈', text: '强雷暴冰雹', code: 99 }
};

const WEEKDAYS = ['周日', '周一', '周二', '周三', '周四', '周五', '周六'];
const CACHE_STORAGE_KEY = 'weekly_mountain_weather_cache';
const CACHE_TTL_MS = 3 * 3600 * 1000; // 3小时本地缓存有效期

/**
 * 获取山峰最核心气象基准坐标点（优先选择最高打卡点/观景台）
 */
export function getMountainWeatherPoint(mountain) {
  if (!mountain) return null;
  const wps = waypointsData[mountain.id] || [];
  let bestPoint = null;
  let maxAlt = -1;

  for (const wp of wps) {
    if (typeof wp.lat === 'number' && typeof wp.lng === 'number') {
      const alt = wp.alt_m || 0;
      if (alt > maxAlt) {
        maxAlt = alt;
        bestPoint = wp;
      }
    }
  }

  if (bestPoint) {
    return {
      lat: bestPoint.lat,
      lng: bestPoint.lng,
      name: bestPoint.name || mountain.name,
      alt: bestPoint.alt_m || mountain.altitude_m || null
    };
  }

  // 兜底坐标（成都周边默认）
  return {
    lat: 30.65,
    lng: 103.35,
    name: mountain.name,
    alt: mountain.altitude_m || 2000
  };
}

/**
 * 从本地存储读取天气缓存
 */
export function getWeatherCache(mountainId) {
  try {
    const raw = localStorage.getItem(CACHE_STORAGE_KEY);
    if (!raw) return null;
    const store = JSON.parse(raw);
    const item = store[mountainId];
    if (!item || !item.time || !item.data) return null;
    if (Date.now() - item.time > CACHE_TTL_MS) {
      return null; // 已过期
    }
    return item;
  } catch (e) {
    console.warn('[WeatherService] 读取天气缓存失败:', e);
    return null;
  }
}

/**
 * 写入本地天气缓存
 */
function setWeatherCache(mountainId, data, point) {
  try {
    const raw = localStorage.getItem(CACHE_STORAGE_KEY);
    const store = raw ? JSON.parse(raw) : {};
    store[mountainId] = {
      time: Date.now(),
      data,
      point
    };
    localStorage.setItem(CACHE_STORAGE_KEY, JSON.stringify(store));
  } catch (e) {
    console.warn('[WeatherService] 保存天气缓存失败:', e);
  }
}

/**
 * 清除指定山峰天气缓存（用于强制刷新）
 */
export function clearWeatherCache(mountainId) {
  try {
    const raw = localStorage.getItem(CACHE_STORAGE_KEY);
    if (!raw) return;
    const store = JSON.parse(raw);
    delete store[mountainId];
    localStorage.setItem(CACHE_STORAGE_KEY, JSON.stringify(store));
  } catch (e) {
    console.warn('[WeatherService] 清理天气缓存失败:', e);
  }
}

/**
 * 解析并生成结构化天气报告
 */
export function parseDailyWeather(daily, point, timestamp = Date.now()) {
  if (!daily || !Array.isArray(daily.time)) return null;

  const days = daily.time.map((timeStr, idx) => {
    const code = daily.weather_code ? daily.weather_code[idx] : 0;
    const wmo = WMO_MAP[code] || { icon: '🌤', text: '多云', code };
    const maxTemp = daily.temperature_2m_max ? Math.round(daily.temperature_2m_max[idx]) : null;
    const minTemp = daily.temperature_2m_min ? Math.round(daily.temperature_2m_min[idx]) : null;
    const precipProb = daily.precipitation_probability_max ? daily.precipitation_probability_max[idx] : 0;
    const precipSum = daily.precipitation_sum ? Math.round(daily.precipitation_sum[idx] * 10) / 10 : 0;
    const windSpeed = daily.wind_speed_10m_max ? Math.round(daily.wind_speed_10m_max[idx]) : 0;

    const dateObj = new Date(timeStr + 'T00:00:00');
    const weekday = WEEKDAYS[dateObj.getDay()];
    const monthDay = timeStr.slice(5); // '10-19'

    // 恶劣天气判定：降水概率 ≥ 50% 或 降水量 ≥ 3mm
    const isBad = precipProb >= 50 || precipSum >= 3;
    const isCold = minTemp !== null && minTemp <= 0;
    const isWindy = windSpeed >= 35;

    return {
      date: timeStr,
      weekday,
      monthDay,
      code,
      icon: wmo.icon,
      text: wmo.text,
      maxTemp,
      minTemp,
      precipProb,
      precipSum,
      windSpeed,
      isBad,
      isCold,
      isWindy
    };
  });

  // 安全与徒步窗口智能分析
  const badDays = days.filter((d) => d.isBad);
  const coldDays = days.filter((d) => d.isCold);
  const maxWind = Math.max(0, ...days.map((d) => d.windSpeed));

  const warnings = [];
  if (badDays.length > 0) {
    const dates = badDays.map((d) => d.monthDay).join('、');
    const maxP = Math.max(...badDays.map((d) => d.precipProb));
    warnings.push({
      type: 'danger',
      icon: 'water_drop',
      text: `${dates} 有降水过程（最大概率 ${maxP}%），高海拔徒步建议避开或备齐防水硬壳。`
    });
  } else {
    warnings.push({
      type: 'success',
      icon: 'verified',
      text: '未来 7 天降水概率低，天气晴好稳定，非常适宜登高与观景！'
    });
  }

  if (coldDays.length > 0) {
    warnings.push({
      type: 'ice',
      icon: 'ac_unit',
      text: `有 ${coldDays.length} 天最低温 ≤0℃，山脊可能结暗冰并有风寒效应，注意加带保暖抓绒与冰爪。`
    });
  }

  if (maxWind >= 35) {
    warnings.push({
      type: 'wind',
      icon: 'air',
      text: `局部时段最大风速可达 ${maxWind} km/h，垭口与山脊风力强劲，注意防风与重心稳定。`
    });
  }

  return {
    point,
    updateTime: timestamp,
    updateTimeStr: new Date(timestamp).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }),
    days,
    badDays,
    coldDays,
    maxWind,
    warnings,
    source: 'Open-Meteo 高海拔高精数值预报'
  };
}

/**
 * 获取山峰未来 7 天实况天气
 * @param {Object} mountain 山峰对象
 * @param {Boolean} forceRefresh 是否强制联网拉取
 */
export async function fetchMountainWeather(mountain, forceRefresh = false) {
  if (!mountain || !mountain.id) {
    throw new Error('无效的山峰信息');
  }

  const point = getMountainWeatherPoint(mountain);
  if (!point || typeof point.lat !== 'number' || typeof point.lng !== 'number') {
    throw new Error('缺少山峰坐标数据');
  }

  // 1. 如果不强制刷新，优先读取 3 小时本地缓存
  if (!forceRefresh) {
    const cached = getWeatherCache(mountain.id);
    if (cached) {
      const parsed = parseDailyWeather(cached.data, cached.point || point, cached.time);
      if (parsed) return parsed;
    }
  }

  // 2. 联网请求 Open-Meteo 免费气象 API
  const url = `https://api.open-meteo.com/v1/forecast?latitude=${point.lat.toFixed(4)}&longitude=${point.lng.toFixed(4)}&daily=weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max,wind_speed_10m_max&timezone=Asia%2FShanghai&forecast_days=7`;

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 8000); // 8秒超时

  try {
    const response = await fetch(url, {
      signal: controller.signal
    });
    clearTimeout(timeoutId);

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const json = await response.json();
    if (!json || !json.daily) {
      throw new Error('气象服务器返回数据异常');
    }

    const now = Date.now();
    // 写入缓存
    setWeatherCache(mountain.id, json.daily, point);

    // 解析格式化
    return parseDailyWeather(json.daily, point, now);
  } catch (err) {
    clearTimeout(timeoutId);
    // 网络异常时，尝试降级读取任何现有旧缓存（即使已过3小时）
    try {
      const raw = localStorage.getItem(CACHE_STORAGE_KEY);
      if (raw) {
        const store = JSON.parse(raw);
        const item = store[mountain.id];
        if (item && item.data) {
          const parsed = parseDailyWeather(item.data, item.point || point, item.time);
          if (parsed) {
            parsed.isStale = true;
            parsed.warnings.unshift({
              type: 'warn',
              icon: 'cloud_off',
              text: '当前处于离线状态，展示为之前缓存的气象数据。'
            });
            return parsed;
          }
        }
      }
    } catch (e) {
      // ignore
    }

    throw new Error(err.name === 'AbortError' ? '网络请求超时，请检查网络后重试' : (err.message || '获取天气失败'));
  }
}
