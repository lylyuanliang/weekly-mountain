#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据层自动化提取与解耦脚本
从 index.html 中精确提取原生山峰数据集与路线打卡点 GPS 坐标，
生成纯静态 JSON 产物：
- src/data/mountains.json（50 座山峰完整结构化对象）
- src/data/waypoints.json（按山峰 id 索引的 GPS 打卡点字典）
"""

import os
import re
import json


def num_or(v):
    if v is None:
        return 0
    if isinstance(v, (int, float)):
        return v
    m = re.search(r'[-+]?\d*\.?\d+', str(v))
    return float(m.group(0)) if m else 0


def derived_nums(m):
    """
    当山峰顶层缺失数值时，从 routes / route_detail / wp_routes 推导海拔、里程、爬升
    """
    out = {
        'alt': num_or(m.get('altitude_m')),
        'dist': num_or(m.get('distance_km')),
        'asc': num_or(m.get('ascent_m')),
        'dur': num_or(m.get('duration_h'))
    }
    r0 = (m.get('routes') and m['routes'][0]) or {}
    if not out['dist']:
        out['dist'] = num_or(r0.get('dist_km') or r0.get('distance_km'))
    if not out['asc']:
        out['asc'] = num_or(r0.get('ascent_m'))
    if not out['dur']:
        out['dur'] = num_or(r0.get('time_h') or r0.get('duration_h') or r0.get('hours'))

    rds = m.get('route_detail') or []
    best = None
    best_km = 0
    for r in rds:
        if not isinstance(r.get('segments'), list):
            continue
        label = str(r.get('name') or '') + str(r.get('terrain') or '') + str(r.get('difficulty_note') or '')
        if re.search(r'观光车|景区车|中转车|索道|骑马', label):
            continue
        if re.search(r'穿越|多日|2天|两天|3天|三天|天露营|大环线', label):
            continue
        km = sum(num_or(x.get('km')) for x in r['segments'])
        if km > best_km:
            best_km = km
            best = r

    if not best:
        for r in rds:
            if not isinstance(r.get('segments'), list):
                continue
            km = sum(num_or(x.get('km')) for x in r['segments'])
            if km > best_km:
                best_km = km
                best = r

    if best:
        top_alt = 0
        low_alt = 0
        for i, s_item in enumerate(best['segments']):
            a = num_or(s_item.get('alt_m'))
            if a > top_alt:
                top_alt = a
            if i == 0 and a:
                low_alt = a
        if not out['alt'] and top_alt:
            out['alt'] = top_alt
        if not out['dist']:
            out['dist'] = round(sum(num_or(x.get('km')) for x in best['segments']), 1)
        if not out['asc'] and top_alt and low_alt and top_alt > low_alt:
            out['asc'] = top_alt - low_alt

    # 顶层 alt 仍未推导出时，从打卡点中取最高海拔
    if not out['alt']:
        wps = [
            num_or(w.get('alt_m'))
            for r in m.get('wp_routes', [])
            for w in r.get('waypoints', [])
            if num_or(w.get('alt_m'))
        ]
        if wps:
            out['alt'] = max(wps)

    return out


def wp_uncertain(m, w):
    """
    判断打卡点坐标是否为估算/待核
    """
    nm = re.sub(r'[（(].*$', '', str(w.get('name', ''))).strip()
    if not nm or len(nm) < 2:
        return False
    if re.search(r'估算|待核|近似|内插|不可用', str(w.get('coord_note', ''))):
        return True
    unverified_list = m.get('wp_unverified', [])
    if not isinstance(unverified_list, list):
        return False
    for t in unverified_list:
        s_val = str(t).strip()
        if '坐标' not in s_val:
            continue
        if s_val.startswith(nm):
            return True
    return False


def extract_data():
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    html_path = os.path.join(project_root, "index.html")
    out_dir = os.path.join(project_root, "src", "data")
    os.makedirs(out_dir, exist_ok=True)

    print(f"Reading index.html from: {html_path}")
    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    # 优先匹配 const MOUNTAINS = [ ... ]; 或 const DATA = [ ... ];
    match = re.search(r'const\s+(?:MOUNTAINS|DATA)\s*=\s*(\[\s*\{.*?\}\s*\]);', html_content, re.DOTALL)
    if not match:
        # 行级精确定位降级
        lines = html_content.splitlines()
        start_line = None
        end_line = None
        for i, line in enumerate(lines):
            if 'const MOUNTAINS =' in line or 'const DATA =' in line:
                start_line = i
            elif start_line is not None and line.strip() == '];':
                end_line = i
                break
        if start_line is None or end_line is None:
            raise RuntimeError("Could not find MOUNTAINS or DATA array in index.html")
        json_slice = (
            lines[start_line].split('=', 1)[1].strip() +
            "\n" +
            "\n".join(lines[start_line + 1:end_line]) +
            "\n]"
        )
        mountains = json.loads(json_slice)
    else:
        mountains = json.loads(match.group(1))

    print(f"Parsed {len(mountains)} mountains from index.html")
    if len(mountains) != 50:
        raise ValueError(f"Expected 50 mountains, but got {len(mountains)}")

    waypoints = {}
    for m in mountains:
        mid = m["id"]

        # 确保 altitude_m 数值完整
        derived = derived_nums(m)
        if not m.get("altitude_m"):
            m["altitude_m"] = int(derived["alt"]) if derived["alt"] else None
        else:
            try:
                m["altitude_m"] = int(m["altitude_m"])
            except (ValueError, TypeError):
                pass

        # 确保 season_best 与 best_season 双向对齐
        if mid == "shuangqiaogou" and not m.get("season_best"):
            m["season_best"] = ["四季皆宜：春赏雪山杜鹃，夏避暑清凉，秋看彩林红叶，冬观冰瀑攀冰（12-2月）"]
        m["best_season"] = m.get("season_best") or m.get("best_season") or ["四季皆宜"]

        # 提取全部路线中的打卡点
        pts = []
        wp_routes = m.get("wp_routes", [])
        for route_idx, route in enumerate(wp_routes):
            r_name = route.get("name", f"路线{route_idx + 1}")
            for w in route.get("waypoints", []):
                pt = {
                    "seq": w.get("seq"),
                    "name": w.get("name"),
                    "lat": w.get("lat"),
                    "lng": w.get("lng"),
                    "alt_m": w.get("alt_m"),
                    "km": w.get("km"),
                    "note": w.get("note"),
                    "unc": wp_uncertain(m, w),
                    "route_index": route_idx,
                    "route_name": r_name,
                }
                pts.append(pt)
        waypoints[mid] = pts

    # 输出 src/data/mountains.json
    m_path = os.path.join(out_dir, "mountains.json")
    with open(m_path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(mountains, f, ensure_ascii=False, indent=2)
    print(f"Wrote {len(mountains)} mountains to {m_path}")

    # 输出 src/data/waypoints.json
    wp_path = os.path.join(out_dir, "waypoints.json")
    with open(wp_path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(waypoints, f, ensure_ascii=False, indent=2)
    total_wps = sum(len(v) for v in waypoints.values())
    print(f"Wrote {len(waypoints)} waypoint sets ({total_wps} total points) to {wp_path}")

    print("Data extraction completed successfully!")


if __name__ == "__main__":
    extract_data()
