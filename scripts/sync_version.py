#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
版本同步与时间戳版本升级脚本 (scripts/sync_version.py)
用于自动将应用版本号第四位更新为当前时间戳 (YYYYMMDDHHmm)，并同步对齐：
1. package.json
2. src/config/version.js
3. public/version.json
4. android/app/build.gradle (versionName & versionCode)
"""

import os
import re
import sys
import json
import time
from datetime import datetime

# 确保 Windows 控制台字符编码为 UTF-8
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def generate_timestamp_version(base_version="0.3.0"):
    now = datetime.now()
    timestamp_str = now.strftime("%Y%m%d%H%M")
    unix_seconds = int(time.time())
    app_version = f"{base_version}.{timestamp_str}"
    return app_version, timestamp_str, unix_seconds, now

def sync_all(explicit_version=None):
    if explicit_version:
        parts = explicit_version.replace("v", "").split(".")
        if len(parts) >= 4:
            base_version = ".".join(parts[:3])
            timestamp_str = parts[3]
        else:
            base_version = explicit_version
            timestamp_str = datetime.now().strftime("%Y%m%d%H%M")
        now = datetime.now()
        unix_seconds = int(time.time())
        app_version = f"{base_version}.{timestamp_str}" if len(parts) < 4 else explicit_version.replace("v", "")
    else:
        base_version = "0.3.0"
        app_version, timestamp_str, unix_seconds, now = generate_timestamp_version(base_version)

    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M")
    build_timestamp = f"{date_str} {time_str}"
    version_tag = f"v{app_version}"

    print(f"[*] 正在同步时间戳版本: {app_version} (Tag: {version_tag}, Code: {unix_seconds})...")

    # 1. 更新 package.json
    pkg_path = os.path.join(PROJECT_ROOT, "package.json")
    if os.path.exists(pkg_path):
        with open(pkg_path, "r", encoding="utf-8") as f:
            pkg_data = json.load(f)
        pkg_data["version"] = app_version
        with open(pkg_path, "w", encoding="utf-8") as f:
            json.dump(pkg_data, f, ensure_ascii=False, indent=2)
            f.write("\n")
        print(f"  [✓] package.json -> {app_version}")

    # 2. 更新 src/config/version.js
    version_js_path = os.path.join(PROJECT_ROOT, "src", "config", "version.js")
    if os.path.exists(version_js_path):
        with open(version_js_path, "r", encoding="utf-8") as f:
            v_content = f.read()

        v_content = re.sub(r"export const APP_VERSION = '[^']+';", f"export const APP_VERSION = '{app_version}';", v_content)
        v_content = re.sub(r"export const RELEASE_VERSION = '[^']+';", f"export const RELEASE_VERSION = '{base_version}';", v_content)
        v_content = re.sub(r"export const BUILD_DATE = '[^']+';", f"export const BUILD_DATE = '{date_str}';", v_content)
        v_content = re.sub(r"export const BUILD_TIME = '[^']+';", f"export const BUILD_TIME = '{time_str}';", v_content)
        v_content = re.sub(r"export const BUILD_TIMESTAMP = '[^']+';", f"export const BUILD_TIMESTAMP = '{build_timestamp}';", v_content)
        v_content = re.sub(r"export const BUILD_CODE = \d+;", f"export const BUILD_CODE = {unix_seconds};", v_content)

        with open(version_js_path, "w", encoding="utf-8") as f:
            f.write(v_content)
        print(f"  [✓] src/config/version.js -> {app_version} ({build_timestamp})")

    # 3. 更新 public/version.json
    public_dir = os.path.join(PROJECT_ROOT, "public")
    os.makedirs(public_dir, exist_ok=True)
    version_json_path = os.path.join(public_dir, "version.json")

    release_apk_name = f"weekly-mountain-{version_tag}-release.apk"
    debug_apk_name = f"weekly-mountain-{version_tag}-debug.apk"
    release_download_url = f"https://github.com/lylyuanliang/weekly-mountain/releases/download/{version_tag}/{release_apk_name}"
    debug_download_url = f"https://github.com/lylyuanliang/weekly-mountain/releases/download/{version_tag}/{debug_apk_name}"

    version_json_data = {
        "version": app_version,
        "versionTag": version_tag,
        "title": f"{version_tag} 签名一致性对齐、CI双包体积硬门禁与微信导航引导优化",
        "publishedAt": date_str,
        "changelog": (
            "1. 【签名对齐】固化 Android 原生 debug.keystore 签名配置，根治跨环境覆盖安装签名不一致 (INSTALL_FAILED_UPDATE_INCOMPATIBLE)；\n"
            "2. 【状态机修复】修复安装中断或取消后更新弹窗卡死在「您正在使用最新版本」的状态停滞，增设「安装包已就绪」直接安装入口；\n"
            "3. 【流水线硬门禁】修复 GitHub CI 归档残缺中间 APK 导致 3.94MB 的严重缺陷，锁定 canonical outputs 产物并增设 20MB 体积门禁；\n"
            "4. 【静态资源断言】硬化 scripts/copy_assets.js，防范缺失资源时静默退出 0，确保 153 座山峰全景高清大图 100% 完整打包；\n"
            "5. 【微信导航引导】Web 版微信内置浏览器增设系统浏览器打开引导卡片，主动提示右上角在浏览器打开直达高德/百度/腾讯地图导航；\n"
            "6. 【本地联调包】真机反馈面板无缝打通开发机本地刚构建 APK 直连极速下载，免除远端流水线漫长等待。"
        ),
        "assetName": release_apk_name,
        "assetSizeText": "约 29 MB",
        "downloadUrl": release_download_url,
        "debugDownloadUrl": debug_download_url,
        "releaseDownloadUrl": release_download_url
    }
    with open(version_json_path, "w", encoding="utf-8") as f:
        json.dump(version_json_data, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"  [✓] public/version.json -> {version_tag}")

    # 4. 更新 android/app/build.gradle
    build_gradle_path = os.path.join(PROJECT_ROOT, "android", "app", "build.gradle")
    if os.path.exists(build_gradle_path):
        with open(build_gradle_path, "r", encoding="utf-8") as f:
            gradle_content = f.read()

        gradle_content = re.sub(r'versionCode\s+\d+', f'versionCode {unix_seconds}', gradle_content)
        gradle_content = re.sub(r'versionName\s+"[^"]+"', f'versionName "{app_version}"', gradle_content)

        with open(build_gradle_path, "w", encoding="utf-8") as f:
            f.write(gradle_content)
        print(f"  [✓] android/app/build.gradle -> versionCode {unix_seconds}, versionName {app_version}")

    print(f"\n[SUCCESS] 全部工程版本元数据已统一升版至: {app_version}\n")
    return app_version

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else None
    sync_all(target)
