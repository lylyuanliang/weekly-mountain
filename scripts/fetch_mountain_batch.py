# -*- coding: utf-8 -*-
"""
Alpine Explorer 山峰标志性风景图多源抓取与高清清洗脚本
支持按批次 (Batch 1-4) 或指定 ID 并发执行
"""

import os
import sys
import json
import time
import re
import urllib.request
import urllib.parse
from PIL import Image

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from mountain_queries import MOUNTAIN_CONFIG

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8'
}

# 商业图库/水印素材站过滤黑名单
WATERMARK_DOMAINS = [
    'vjshi', 'vcg', 'quanjing', 'shutterstock', 'getty', '588ku',
    'nipic', 'ibaotu', '699pic', 'veer', 'visualchina', 'photophoto',
    'huitu', 'tukuppt', '135editor', '58pic', 'sogou.com/pic'
]

BAD_KEYWORDS = [
    'logo', 'icon', 'avatar', 'poster', 'banner', 'vector', 'clipart',
    'badge', 'emoji', 'watermark', 'sample', 'thumb', 'carton', 'drawing',
    'illustration', 'chart', 'map', 'floorplan'
]

def is_clean_url(url):
    u = url.lower()
    for domain in WATERMARK_DOMAINS:
        if domain in u:
            return False
    for bad in BAD_KEYWORDS:
        if bad in u:
            return False
    return True

def search_bing_images(query, limit=8):
    encoded = urllib.parse.quote(query)
    url = f"https://cn.bing.com/images/async?q={encoded}&first=1&count={limit*3}&scenario=ImageBasicHover&datsrc=N_I&layout=RowBased&mmasync=1"
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
            matches = re.findall(r'murl&quot;:&quot;(https?://[^&"]+)', html)
            urls = []
            for m in matches:
                # unescape if needed
                m_clean = m.replace('\\/', '/').replace('&amp;', '&')
                if is_clean_url(m_clean):
                    urls.append(m_clean)
            return urls[:limit]
    except Exception as e:
        print(f"    [-] Bing search warning for '{query}': {e}")
        return []

def search_wikimedia_images(query, limit=6):
    encoded = urllib.parse.quote(query)
    url = f"https://commons.wikimedia.org/w/api.php?action=query&generator=search&gsrnamespace=6&gsrsearch={encoded}&gsrlimit={limit*2}&prop=imageinfo&iiprop=url|size&format=json"
    req = urllib.request.Request(url, headers={'User-Agent': 'WeeklyMountainApp/1.0'})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            pages = data.get('query', {}).get('pages', {})
            urls = []
            for pid, p in pages.items():
                ii = p.get('imageinfo', [{}])[0]
                u = ii.get('url')
                if u and is_clean_url(u) and any(u.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.webp']):
                    urls.append(u)
            return urls[:limit]
    except Exception as e:
        return []

def download_and_process(url, out_path, min_w=400, min_h=280, max_dim=(1200, 800)):
    req = urllib.request.Request(url, headers=HEADERS)
    tmp_path = out_path + '.download.tmp'
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = resp.read()
        if len(data) < 15 * 1024:  # too small (< 15KB is likely placeholder or icon)
            return False
        with open(tmp_path, 'wb') as f:
            f.write(data)
        with Image.open(tmp_path) as im:
            im = im.convert('RGB')
            w, h = im.size
            if w < min_w or h < min_h:
                if os.path.exists(tmp_path): os.remove(tmp_path)
                return False
            aspect = w / float(h)
            if aspect < 0.65 or aspect > 2.8: # extreme aspect ratio
                if os.path.exists(tmp_path): os.remove(tmp_path)
                return False

            im.thumbnail(max_dim, Image.Resampling.LANCZOS)
            im.save(out_path, format='JPEG', quality=82, optimize=True)

        if os.path.exists(tmp_path):
            os.remove(tmp_path)

        kb = os.path.getsize(out_path) / 1024
        print(f"    [OK] Downloaded & normalized: {os.path.basename(out_path)} ({kb:.1f} KB, {im.size[0]}x{im.size[1]})")
        return True
    except Exception as e:
        if os.path.exists(tmp_path):
            try: os.remove(tmp_path)
            except Exception: pass
        return False

def make_fallback_photo(source_main_jpg, out_path, mode="photo2"):
    """
    If web search completely fails for a niche mountain, generate a photographic scenic crop
    derived from the authentic main photo so there is never an image 404 or broken icon.
    """
    if not os.path.exists(source_main_jpg):
        return False
    try:
        with Image.open(source_main_jpg) as im:
            im = im.convert('RGB')
            w, h = im.size
            if mode == "photo2":
                # crop upper 75% for panoramic sky/peak view
                crop_box = (0, 0, w, int(h * 0.85))
            else:
                # crop center-lower for trail/detail
                crop_box = (int(w * 0.1), int(h * 0.15), int(w * 0.95), h)
            cropped = im.crop(crop_box)
            cropped.thumbnail((1200, 800), Image.Resampling.LANCZOS)
            cropped.save(out_path, format='JPEG', quality=80, optimize=True)
        print(f"    [FALLBACK-CROP] Created scenic crop for {os.path.basename(out_path)}")
        return True
    except Exception as e:
        print(f"    [ERROR] Fallback crop failed: {e}")
        return False

def fetch_single_mountain(mountain_id, mountain_data, assets_dir="assets/mountains"):
    cfg = MOUNTAIN_CONFIG.get(mountain_id, {})
    m_name = mountain_data.get('name', mountain_id)
    alt = mountain_data.get('altitude_m', 2000)

    main_jpg = os.path.join(assets_dir, f"{mountain_id}.jpg")
    photo2_jpg = os.path.join(assets_dir, f"{mountain_id}-2.jpg")
    photo3_jpg = os.path.join(assets_dir, f"{mountain_id}-3.jpg")

    p2_cfg = cfg.get('photo2', {})
    p3_cfg = cfg.get('photo3', {})
    main_cfg = cfg.get('main', {
        "title": f"{m_name}标志风光",
        "desc": f"海拔{alt}m 四川川西高山全貌实拍"
    })

    print(f"\n>>> Processing [{mountain_id}] {m_name} ...")

    # Target 2
    if not os.path.exists(photo2_jpg) or os.path.getsize(photo2_jpg) < 1000:
        q2 = p2_cfg.get('query', f"{m_name} 风景 实拍")
        print(f"  Searching Photo 2: '{q2}'")
        urls = search_bing_images(q2, limit=8)
        if not urls:
            urls = search_wikimedia_images(q2, limit=6)

        success = False
        for u in urls:
            if download_and_process(u, photo2_jpg):
                success = True
                break
            time.sleep(0.3)

        if not success:
            # retry with broader search
            retry_q = f"{m_name} 旅游 风景"
            print(f"  Retrying Photo 2: '{retry_q}'")
            r_urls = search_bing_images(retry_q, limit=6)
            for u in r_urls:
                if download_and_process(u, photo2_jpg):
                    success = True
                    break
                time.sleep(0.3)

        if not success:
            make_fallback_photo(main_jpg, photo2_jpg, mode="photo2")
    else:
        print(f"  [EXISTS] {os.path.basename(photo2_jpg)}")

    time.sleep(0.5)

    # Target 3
    if not os.path.exists(photo3_jpg) or os.path.getsize(photo3_jpg) < 1000:
        q3 = p3_cfg.get('query', f"{m_name} 观景台 远眺")
        print(f"  Searching Photo 3: '{q3}'")
        urls = search_bing_images(q3, limit=8)
        if not urls:
            urls = search_wikimedia_images(q3, limit=6)

        success = False
        for u in urls:
            if download_and_process(u, photo3_jpg):
                success = True
                break
            time.sleep(0.3)

        if not success:
            # retry with broader search
            retry_q = f"{m_name} 登山 徒步 摄影"
            print(f"  Retrying Photo 3: '{retry_q}'")
            r_urls = search_bing_images(retry_q, limit=6)
            for u in r_urls:
                if download_and_process(u, photo3_jpg):
                    success = True
                    break
                time.sleep(0.3)

        if not success:
            make_fallback_photo(main_jpg, photo3_jpg, mode="photo3")
    else:
        print(f"  [EXISTS] {os.path.basename(photo3_jpg)}")

    # Return structured gallery items
    gallery_items = [
        {
            "src": f"assets/mountains/{mountain_id}.jpg",
            "title": main_cfg.get('title', f"{m_name}标志风光"),
            "desc": main_cfg.get('desc', f"海拔{alt}m 四川川西高山全貌实拍")
        },
        {
            "src": f"assets/mountains/{mountain_id}-2.jpg",
            "title": p2_cfg.get('title', f"{m_name}壮丽全景"),
            "desc": p2_cfg.get('desc', f"高山晨曦与巍峨雪峰壮丽自然风光")
        },
        {
            "src": f"assets/mountains/{mountain_id}-3.jpg",
            "title": p3_cfg.get('title', f"{m_name}秘境风情"),
            "desc": p3_cfg.get('desc', f"高山原始林海与徒步探险风貌")
        }
    ]
    return gallery_items

def run_batch(batch_idx):
    with open('src/data/mountains.json', 'r', encoding='utf-8') as f:
        mountains = json.load(f)

    total = len(mountains)
    # 4 Batches:
    # 1: 0..12 (13)
    # 2: 13..25 (13)
    # 3: 26..38 (13)
    # 4: 39..50 (12)
    slices = [
        (0, 13),
        (13, 26),
        (26, 39),
        (39, 51)
    ]

    start_idx, end_idx = slices[batch_idx - 1]
    batch_mountains = mountains[start_idx:end_idx]

    print(f"==================================================")
    print(f"  STARTING BATCH {batch_idx}: Mountains {start_idx+1} to {end_idx} (Total {len(batch_mountains)})")
    print(f"==================================================")

    os.makedirs('assets/mountains', exist_ok=True)
    os.makedirs('scratch', exist_ok=True)

    results = {}
    for m in batch_mountains:
        mid = m['id']
        items = fetch_single_mountain(mid, m)
        results[mid] = items

    out_json = f"scratch/gallery_batch{batch_idx}.json"
    with open(out_json, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n[DONE] Batch {batch_idx} completed! Saved {len(results)} mountains gallery config to {out_json}")

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="Fetch mountain images batch")
    parser.add_argument('--batch', type=int, choices=[1, 2, 3, 4], help="Batch index 1, 2, 3, or 4")
    parser.add_argument('--ids', type=str, help="Comma separated mountain ids")
    args = parser.parse_args()

    if args.batch:
        run_batch(args.batch)
    elif args.ids:
        ids = [x.strip() for x in args.ids.split(',') if x.strip()]
        with open('src/data/mountains.json', 'r', encoding='utf-8') as f:
            mountains = json.load(f)
        m_map = {m['id']: m for m in mountains}
        results = {}
        for mid in ids:
            if mid in m_map:
                results[mid] = fetch_single_mountain(mid, m_map[mid])
        with open("scratch/gallery_custom.json", "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
    else:
        print("Usage: python scripts/fetch_mountain_batch.py --batch [1|2|3|4]")
