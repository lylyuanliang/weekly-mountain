#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每周一山 (Weekly Mountain) 自动化生产打包与静态资源审计脚本
1. 执行 npm run build 生成 dist/（自动同步 assets/mountains/ 风景图）
2. 将 dist/ 打包为自包含静态部署包 weekly-mountain-deploy.zip
3. 统计审计文件清单、解压体积、文件总数、压缩包体积
4. 自动解压验证部署包完整性（index.html 及风景图资源）
"""

import os
import sys
import zipfile
import tempfile
import subprocess
import shutil

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

WORKSPACE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST_DIR = os.path.join(WORKSPACE_DIR, "dist")
OUTPUT_ZIP = os.path.join(WORKSPACE_DIR, "weekly-mountain-deploy.zip")


def run_build():
    print(f"[1/4] Running npm run build in {WORKSPACE_DIR}...")
    npm_cmd = "npm.cmd" if sys.platform == "win32" else "npm"
    result = subprocess.run(
        [npm_cmd, "run", "build"],
        cwd=WORKSPACE_DIR,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace"
    )
    if result.returncode != 0:
        print("Build failed with stderr:")
        print(result.stderr)
        print("Stdout:")
        print(result.stdout)
        raise RuntimeError(f"npm run build failed with code {result.returncode}")
    print(result.stdout.strip())
    print("[OK] Build completed successfully.")


def package_dist():
    print(f"\n[2/4] Packaging dist/ into {os.path.basename(OUTPUT_ZIP)}...")
    if not os.path.exists(DIST_DIR):
        raise FileNotFoundError(f"dist directory not found at {DIST_DIR}")

    file_list = []
    for root, _, files in os.walk(DIST_DIR):
        for f in files:
            full_path = os.path.join(root, f)
            rel_path = os.path.relpath(full_path, DIST_DIR).replace("\\", "/")
            file_list.append((full_path, rel_path))

    with zipfile.ZipFile(OUTPUT_ZIP, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for full_path, rel_path in file_list:
            zf.write(full_path, arcname=rel_path)

    print(f"[OK] Archived {len(file_list)} files into {OUTPUT_ZIP}")
    return file_list


def audit_and_assert_metrics(file_list):
    print("\n[3/4] Auditing package metrics...")

    total_uncompressed_bytes = sum(os.path.getsize(f[0]) for f in file_list)
    total_uncompressed_mb = total_uncompressed_bytes / (1024 * 1024)
    file_count = len(file_list)
    zip_bytes = os.path.getsize(OUTPUT_ZIP)
    zip_mb = zip_bytes / (1024 * 1024)

    # 分类汇总统计
    html_files = [f for f in file_list if f[1].endswith('.html')]
    js_files = [f for f in file_list if f[1].endswith('.js')]
    css_files = [f for f in file_list if f[1].endswith('.css')]
    img_files = [f for f in file_list if f[1].startswith('assets/mountains/')]

    print("--------------------------------------------------------------------------------")
    print(f" {'Category':<30} | {'Count':<8} | {'Total Size':<15}")
    print("--------------------------------------------------------------------------------")
    print(f" {'HTML Entry':<30} | {len(html_files):<8} | {sum(os.path.getsize(x[0]) for x in html_files)/1024:,.2f} KB")
    print(f" {'JavaScript Bundle':<30} | {len(js_files):<8} | {sum(os.path.getsize(x[0]) for x in js_files)/1024:,.2f} KB")
    print(f" {'CSS Stylesheet':<30} | {len(css_files):<8} | {sum(os.path.getsize(x[0]) for x in css_files)/1024:,.2f} KB")
    print(f" {'Mountain Scenic Images':<30} | {len(img_files):<8} | {sum(os.path.getsize(x[0]) for x in img_files)/(1024*1024):,.2f} MB")
    print("--------------------------------------------------------------------------------")
    print(f" Total Uncompressed Size : {total_uncompressed_mb:.3f} MB ({total_uncompressed_bytes:,} bytes)")
    print(f" Total File Count        : {file_count} files")
    print(f" Compressed Zip Size     : {zip_mb:.3f} MB ({zip_bytes:,} bytes)")
    print("--------------------------------------------------------------------------------")
    print("[INFO] Package size limit restriction has been relaxed according to user instruction.")
    print(f"[INFO] Current uncompressed package size: {total_uncompressed_mb:.2f} MB, {file_count} files.")


def verify_unzip():
    print(f"\n[4/4] Verifying zip extraction and artifact integrity...")
    with tempfile.TemporaryDirectory() as temp_dir:
        with zipfile.ZipFile(OUTPUT_ZIP, 'r') as zf:
            zf.extractall(temp_dir)

        index_html = os.path.join(temp_dir, "index.html")
        assert os.path.exists(index_html), "Assertion Failed: index.html missing in unzipped output!"
        assert os.path.getsize(index_html) > 1000, "Assertion Failed: index.html is suspiciously small!"

        mountain_imgs_dir = os.path.join(temp_dir, "assets", "mountains")
        assert os.path.exists(mountain_imgs_dir), "Assertion Failed: assets/mountains missing in unzipped output!"
        img_count = len([f for f in os.listdir(mountain_imgs_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))])
        assert img_count == 51, f"Assertion Failed: Expected 51 mountain images, got {img_count}"

        print(f"[PASS] Unzip verified: index.html ({os.path.getsize(index_html)} bytes) + {img_count} mountain scenic photos present and valid.")


if __name__ == "__main__":
    run_build()
    files = package_dist()
    audit_and_assert_metrics(files)
    verify_unzip()
    print("\n=======================================================")
    print(" 🎉 PACKAGING & DEPLOYMENT VERIFICATION COMPLETE! 🎉")
    print("=======================================================")
