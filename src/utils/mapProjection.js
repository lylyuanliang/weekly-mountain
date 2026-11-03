/**
 * Web Mercator 墨卡托投影计算与自适应视口工具 (mapProjection.js)
 */

export function lonToX(lon, z) {
  return ((lon + 180) / 360) * Math.pow(2, z) * 256;
}

export function latToY(lat, z) {
  const s = Math.sin((lat * Math.PI) / 180);
  return (0.5 - Math.log((1 + s) / (1 - s)) / (4 * Math.PI)) * Math.pow(2, z) * 256;
}

export function xToLon(x, z) {
  return (x / (Math.pow(2, z) * 256)) * 360 - 180;
}

export function yToLat(y, z) {
  const n = Math.PI - (2 * Math.PI * y) / (Math.pow(2, z) * 256);
  return (180 / Math.PI) * Math.atan(0.5 * (Math.exp(n) - Math.exp(-n)));
}

/**
 * 根据多组经纬度航点，自动计算最佳居中经纬度与贴合缩放等级 (FitBounds)
 * @param {Array<{lat: number, lng: number}>} points 经纬度点集
 * @param {number} containerWidth 视口宽度
 * @param {number} containerHeight 视口高度
 * @param {number} padding 边距内衬 (px)
 * @returns {{ centerLng: number, centerLat: number, zoom: number }}
 */
export function computeFitBounds(points, containerWidth = 360, containerHeight = 240, padding = 48) {
  if (!points || points.length === 0) {
    return { centerLng: 104.06, centerLat: 30.67, zoom: 12 };
  }

  let minLng = Infinity;
  let maxLng = -Infinity;
  let minLat = Infinity;
  let maxLat = -Infinity;

  for (const pt of points) {
    const lng = typeof pt.lng === 'number' ? pt.lng : (Array.isArray(pt) ? pt[0] : 0);
    const lat = typeof pt.lat === 'number' ? pt.lat : (Array.isArray(pt) ? pt[1] : 0);
    if (!lng || !lat) continue;

    if (lng < minLng) minLng = lng;
    if (lng > maxLng) maxLng = lng;
    if (lat < minLat) minLat = lat;
    if (lat > maxLat) maxLat = lat;
  }

  if (minLng === Infinity || minLat === Infinity) {
    return { centerLng: 104.06, centerLat: 30.67, zoom: 12 };
  }

  const centerLng = (minLng + maxLng) / 2;
  const centerLat = (minLat + maxLat) / 2;

  // 如果只有一个点，返回默认聚焦等级
  if (minLng === maxLng && minLat === maxLat) {
    return { centerLng, centerLat, zoom: 14 };
  }

  const availW = Math.max(containerWidth - padding * 2, 80);
  const availH = Math.max(containerHeight - padding * 2, 80);

  let bestZoom = 11;
  for (let z = 16; z >= 9; z--) {
    const w = lonToX(maxLng, z) - lonToX(minLng, z);
    const h = Math.abs(latToY(maxLat, z) - latToY(minLat, z));
    if (w <= availW && h <= availH) {
      bestZoom = z;
      break;
    }
  }

  return {
    centerLng,
    centerLat,
    zoom: bestZoom
  };
}

/**
 * 将经纬度点投影为视口内的屏幕像素坐标 (x, y)
 */
export function projectPoint(lng, lat, centerLng, centerLat, zoom, width, height) {
  const cx = lonToX(centerLng, zoom);
  const cy = latToY(centerLat, zoom);
  const px = lonToX(lng, zoom) - cx + width / 2;
  const py = latToY(lat, zoom) - cy + height / 2;
  return { x: px, y: py };
}

/**
 * 屏幕像素坐标逆向投影为经纬度点
 */
export function unprojectPoint(x, y, centerLng, centerLat, zoom, width, height) {
  const cx = lonToX(centerLng, zoom);
  const cy = latToY(centerLat, zoom);
  const worldX = x - width / 2 + cx;
  const worldY = y - height / 2 + cy;
  return {
    lng: xToLon(worldX, zoom),
    lat: yToLat(worldY, zoom)
  };
}
