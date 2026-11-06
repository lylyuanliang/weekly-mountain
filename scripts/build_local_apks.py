#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
本地开发机双 APK 构建与产物归档脚本 (scripts/build_local_apks.py)
用于在开发机器上完整构建「正式发布版 (Release)」与「内测调试版 (Debug)」原生 Android 安装包。
包含：
1. Web 资源对应编译 (build:release 与 build)
2. Android 原生编译 (assembleRelease 与 assembleDebug)
3. 安装包体积硬门禁 (>20MB) 与内部资源解压断言
4. 真实 SHA-256 计算与 SHA256SUMS.txt 本地归档
"""

import os
import sys
import json
import shutil
import hashlib
import zipfile
import subprocess

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def calculate_sha256(filepath):
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def get_file_size_mb(filepath):
    bytes_size = os.path.getsize(filepath)
    return f"{bytes_size / (1024 * 1024):.2f} MB", bytes_size

def run_cmd(cmd_list, cwd=PROJECT_ROOT):
    cmd_str = " ".join(cmd_list)
    print(f"\n[EXEC] {cmd_str} (cwd: {cwd})")
    shell_flag = sys.platform == "win32"
    res = subprocess.run(cmd_list, cwd=cwd, shell=shell_flag)
    if res.returncode != 0:
        print(f"[ERROR] 命令执行失败 (退出码 {res.returncode}): {cmd_str}")
        sys.exit(res.returncode)

def verify_apk(apk_path, label):
    print(f"\n[*] 正在校验 {label} 安装包完整性: {apk_path}")
    if not os.path.exists(apk_path):
        raise FileNotFoundError(f"未找到生成的安装包: {apk_path}")

    size_text, bytes_size = get_file_size_mb(apk_path)
    print(f"  - 文件体积: {size_text} ({bytes_size} 字节)")
    if bytes_size < 20 * 1024 * 1024:
        raise ValueError(f"安装包体积异常过小 ({size_text} < 20 MB)，可能缺失静态离线资源！")

    with zipfile.ZipFile(apk_path, "r") as z:
        names = set(z.namelist())
        if "assets/public/index.html" not in names:
            raise ValueError(f"安装包内部缺少关键资源: assets/public/index.html")
        mountain_count = sum(1 for n in names if n.startswith("assets/public/assets/mountains/"))
        print(f"  - 校验 assets/public/index.html: 存在")
        print(f"  - 校验离线高山资产: {mountain_count} 个文件")
        if mountain_count < 50:
            raise ValueError(f"安装包内高山静态资源不足 50 个: {mountain_count}")

    sha256 = calculate_sha256(apk_path)
    print(f"  - SHA-256 安全散列值: {sha256}")
    return sha256, size_text

def main():
    print("=" * 65)
    print("🏔️ 每周一山 · Alpine Explorer 开发机全量 APK 打包程序")
    print("=" * 65)

    version_json_path = os.path.join(PROJECT_ROOT, "public", "version.json")
    with open(version_json_path, "r", encoding="utf-8") as f:
        version_data = json.load(f)

    tag = version_data.get("versionTag") or f"v{version_data.get('version')}"
    print(f"[*] 当前打包目标版本: {tag}")

    gradlew_cmd = "gradlew.bat" if sys.platform == "win32" else "./gradlew"
    android_dir = os.path.join(PROJECT_ROOT, "android")

    # =========================================================================
    # 阶段 1：构建正式发布版 (Release - Zero-DCE 纯净精简构建)
    # =========================================================================
    print("\n" + "=" * 50)
    print("🚀 [阶段 1/2] 构建正式发布版 (Release)")
    print("=" * 50)
    run_cmd(["npm", "run", "build:release"])
    run_cmd([gradlew_cmd, "assembleRelease", "--no-daemon"], cwd=android_dir)

    raw_release_apk = os.path.join(android_dir, "app", "build", "outputs", "apk", "release", "app-release.apk")
    canonical_release_apk = os.path.join(PROJECT_ROOT, f"weekly-mountain-{tag}-release.apk")
    release_sha256, release_size = verify_apk(raw_release_apk, "正式发布版 (Release)")
    shutil.copyfile(raw_release_apk, canonical_release_apk)
    print(f"[✓] 已归档正式版至根目录: {canonical_release_apk}")

    # =========================================================================
    # 阶段 2：构建内测调试版 (Debug - 集成哨兵与诊断浮球)
    # =========================================================================
    print("\n" + "=" * 50)
    print("🛠️ [阶段 2/2] 构建内测调试版 (Debug)")
    print("=" * 50)
    run_cmd(["npm", "run", "build"])
    run_cmd([gradlew_cmd, "assembleDebug", "--no-daemon"], cwd=android_dir)

    raw_debug_apk = os.path.join(android_dir, "app", "build", "outputs", "apk", "debug", "app-debug.apk")
    canonical_debug_apk = os.path.join(PROJECT_ROOT, f"weekly-mountain-{tag}-debug.apk")
    debug_sha256, debug_size = verify_apk(raw_debug_apk, "内测调试版 (Debug)")
    shutil.copyfile(raw_debug_apk, canonical_debug_apk)
    print(f"[✓] 已归档调试版至根目录: {canonical_debug_apk}")

    # =========================================================================
    # 阶段 3：输出 SHA256SUMS.txt
    # =========================================================================
    sums_file = os.path.join(PROJECT_ROOT, "SHA256SUMS.txt")
    with open(sums_file, "w", encoding="utf-8") as f:
        f.write(f"{release_sha256}  weekly-mountain-{tag}-release.apk\n")
        f.write(f"{debug_sha256}  weekly-mountain-{tag}-debug.apk\n")
    print(f"\n[✓] 已生成哈希防篡改清单: {sums_file}")

    print("\n" + "=" * 65)
    print("🎉 本地开发机打包圆满完成！产物清单如下：")
    print("=" * 65)
    print(f"1. 🚀 正式发布版 (Release):")
    print(f"   - 文件路径: {canonical_release_apk}")
    print(f"   - 文件大小: {release_size}")
    print(f"   - SHA-256:  {release_sha256}")
    print(f"2. 🛠️ 内测调试版 (Debug):")
    print(f"   - 文件路径: {canonical_debug_apk}")
    print(f"   - 文件大小: {debug_size}")
    print(f"   - SHA-256:  {debug_sha256}")
    print("=" * 65)

if __name__ == "__main__":
    main()
