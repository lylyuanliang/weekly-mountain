# -*- coding: utf-8 -*-
"""
Alpine Explorer 山峰多图画廊原子合并脚本
读取 4 个 Batch 的 gallery_batch*.json，校验图片文件完整性，原子更新 src/data/mountains.json
"""

import os
import sys
import json
from PIL import Image

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

def merge_all_batches():
    batch_files = [f"scratch/gallery_batch{i}.json" for i in range(1, 5)]
    merged_galleries = {}

    missing_batches = []
    for bf in batch_files:
        if not os.path.exists(bf):
            missing_batches.append(bf)
        else:
            with open(bf, 'r', encoding='utf-8') as f:
                data = json.load(f)
                merged_galleries.update(data)

    if missing_batches:
        print(f"[WARN] Some batch files are still missing: {missing_batches}")
        print(f"       Currently loaded: {len(merged_galleries)} mountains")
    else:
        print(f"[OK] All 4 batch files found. Total mountains in galleries: {len(merged_galleries)}")

    mountains_path = "src/data/mountains.json"
    with open(mountains_path, 'r', encoding='utf-8') as f:
        mountains = json.load(f)

    updated_count = 0
    total_images_verified = 0

    for m in mountains:
        mid = m['id']
        if mid in merged_galleries:
            items = merged_galleries[mid]
            # Verify each image file physically exists and is readable
            verified_items = []
            for item in items:
                img_path = item['src']
                if os.path.exists(img_path) and os.path.getsize(img_path) > 10 * 1024:
                    try:
                        with Image.open(img_path) as im:
                            w, h = im.size
                            if w > 100 and h > 100:
                                verified_items.append(item)
                                total_images_verified += 1
                    except Exception as e:
                        print(f"  [WARN] Corrupt image {img_path}: {e}")
                else:
                    print(f"  [WARN] Image missing or too small: {img_path}")

            if len(verified_items) > 0:
                m['gallery'] = verified_items
                updated_count += 1
            else:
                print(f"  [ERROR] No verified gallery images for mountain: {mid}")
        else:
            print(f"  [MISSING] Mountain {mid} not in merged galleries!")

    # Atomic write to mountains.json
    tmp_path = mountains_path + ".tmp"
    with open(tmp_path, 'w', encoding='utf-8') as f:
        json.dump(mountains, f, ensure_ascii=False, indent=2)

    os.replace(tmp_path, mountains_path)

    print("--------------------------------------------------")
    print(f"  ATOMIC MERGE COMPLETE")
    print(f"  Total Mountains: {len(mountains)}")
    print(f"  Updated with Gallery: {updated_count}/{len(mountains)}")
    print(f"  Total Verified Photos in Gallery: {total_images_verified}")
    print("--------------------------------------------------")

if __name__ == '__main__':
    merge_all_batches()
