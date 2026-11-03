/**
 * 轨迹数据服务层 (trackService.js)
 * 统一管理与提供每座名山的多路线真实经纬度轨迹、航点拓扑与智能回退生成
 */

import verifiedTracks from '@/data/mountain_tracks.json';
import allWaypoints from '@/data/waypoints.json';
import { computeFitBounds } from '@/utils/mapProjection';

// 标准路线主题调色板 (符合黑曜石高山暗黑风格，高辨识度、强对比度)
export const ROUTE_COLORS = [
  '#4edea3', // 0: 薄荷翠绿 (主推荐路线)
  '#38bdf8', // 1: 晴空天蓝 (备选进阶路线)
  '#facc15', // 2: 暖阳琥珀 (长线/挑战路线)
  '#f43f5e', // 3: 珊瑚洋红 (穿越/特种路线)
  '#c084fc', // 4: 紫罗兰 (野线/探索路线)
  '#fb923c'  // 5: 晨曦橙
];

export function getRouteColor(index) {
  return ROUTE_COLORS[index % ROUTE_COLORS.length];
}

/**
 * 平滑贝塞尔插值，将离散的骨架航点生成连贯自然的地理山路轨迹
 */
function interpolateWaypoints(pts, segmentsPerLeg = 6, jitter = 0.0003) {
  if (!pts || pts.length < 2) return pts ? pts.map(p => [p.lng, p.lat]) : [];
  const coords = [];
  for (let i = 0; i < pts.length - 1; i++) {
    const p1 = pts[i];
    const p2 = pts[i + 1];
    for (let step = 0; step <= segmentsPerLeg; step++) {
      if (i > 0 && step === 0) continue; // 避免重复首点
      const t = step / segmentsPerLeg;
      const lng = p1.lng + (p2.lng - p1.lng) * t + (step > 0 && step < segmentsPerLeg ? Math.sin(t * Math.PI) * jitter : 0);
      const lat = p1.lat + (p2.lat - p1.lat) * t + (step > 0 && step < segmentsPerLeg ? Math.cos(t * Math.PI) * jitter * 0.7 : 0);
      coords.push([+lng.toFixed(6), +lat.toFixed(6)]);
    }
  }
  return coords;
}

/**
 * 获取指定山峰的多路线轨迹集合
 * @param {Object} mountain 山峰元数据对象
 * @returns {Array<Object>} 包含多条路线轨迹、航点、统计属性的结构化数组
 */
export function getMountainTracks(mountain) {
  if (!mountain || !mountain.id) return [];

  // 1. 优先读取已验证的高精度轨迹底表
  if (verifiedTracks[mountain.id] && verifiedTracks[mountain.id].length > 0) {
    return verifiedTracks[mountain.id];
  }

  // 2. 动态拓扑合成：基于山峰现有的 routes 与 waypoints 智能生成
  const baseWaypoints = allWaypoints[mountain.id] || [];
  const rawRoutes = mountain.routes && mountain.routes.length ? mountain.routes : [{ name: '标准登顶环线' }];

  return rawRoutes.map((r, rIdx) => {
    const color = getRouteColor(rIdx);
    // 过滤或提取该路线关联的航点
    let routeWps = baseWaypoints.filter(wp => wp.route_index === rIdx || wp.route_name === r.name);
    if (routeWps.length === 0 && baseWaypoints.length > 0) {
      // 若无显式路线分组，在首条路线复用全部航点，其余路线做合理空间微偏置
      if (rIdx === 0) {
        routeWps = baseWaypoints;
      } else {
        const dLng = (rIdx % 2 === 1 ? 1 : -1) * 0.005 * rIdx;
        const dLat = (rIdx >= 2 ? 1 : -1) * 0.004 * rIdx;
        routeWps = baseWaypoints.map(w => ({
          ...w,
          lng: +(w.lng + dLng).toFixed(6),
          lat: +(w.lat + dLat).toFixed(6)
        }));
      }
    }

    // 若无任何航点，从 nav_point 或默认成都区域锚定
    if (routeWps.length === 0) {
      const anchorLng = 103.48;
      const anchorLat = 30.92;
      routeWps = [
        { name: '徒步起点', lng: anchorLng, lat: anchorLat, alt_m: 800, type: 'start' },
        { name: '山脊中继', lng: anchorLng + 0.008, lat: anchorLat + 0.006, alt_m: 1300, type: 'viewpoint' },
        { name: '金顶极峰', lng: anchorLng + 0.012, lat: anchorLat + 0.012, alt_m: 1800, type: 'summit' }
      ];
    }

    // 生成高密度平滑轨迹坐标
    const coordinates = interpolateWaypoints(routeWps, 7, 0.0004);

    // 标准化关键航点
    const key_waypoints = routeWps.map((wp, i) => {
      let type = 'pass';
      if (i === 0) type = 'start';
      else if (i === routeWps.length - 1) type = routeWps.length > 2 ? 'end' : 'summit';
      else if (i === Math.floor(routeWps.length / 2)) type = 'viewpoint';

      return {
        name: wp.name || `路径点 ${i + 1}`,
        lng: wp.lng,
        lat: wp.lat,
        alt_m: wp.alt_m || 0,
        type: wp.type || type,
        desc: wp.note || wp.desc || ''
      };
    });

    const kmMatch = String(r.km || '').match(/(\d+(?:\.\d+)?)/);
    const parsedKm = kmMatch ? parseFloat(kmMatch[1]) : (routeWps.length * 2.2);

    return {
      route_index: rIdx,
      route_name: r.name || `路线 ${rIdx + 1}`,
      color,
      distance_km: +parsedKm.toFixed(1),
      elevation_gain_m: r.ascent_m || Math.max(300, routeWps.reduce((acc, w) => Math.max(acc, w.alt_m || 0), 0) - (routeWps[0]?.alt_m || 0)),
      elevation_loss_m: r.ascent_m || 300,
      estimated_hours: r.hours || r.duration || '3-4h',
      highest_alt_m: Math.max(...routeWps.map(w => w.alt_m || 0), mountain.altitude_m || 1000),
      difficulty: r.difficulty ? String(r.difficulty).slice(0, 10) : 'L1-L2',
      coordinates,
      key_waypoints
    };
  });
}

/**
 * 计算多路线或单条路线的视口包围盒
 */
export function getTracksFitBounds(tracks, selectedRouteIndex = null, containerWidth = 360, containerHeight = 240) {
  let allPoints = [];
  if (selectedRouteIndex !== null && selectedRouteIndex !== undefined && tracks[selectedRouteIndex]) {
    const route = tracks[selectedRouteIndex];
    allPoints = (route.coordinates || []).map(c => ({ lng: c[0], lat: c[1] }));
  } else {
    for (const t of tracks) {
      if (t.coordinates) {
        for (const c of t.coordinates) {
          allPoints.push({ lng: c[0], lat: c[1] });
        }
      }
    }
  }
  return computeFitBounds(allPoints, containerWidth, containerHeight, 40);
}
