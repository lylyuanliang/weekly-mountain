#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
版本同步与时间戳版本升级脚本 (scripts/sync_version.py)
用于自动将应用版本号第四位更新为当前时间戳 (YYYYMMDDHHmm)，并同步对齐：
1. package.json
2. src/config/version.js
3. public/version.json (动态从 docs/releases/RELEASE-v*.md 或命令行入参提取标题与日志)
4. android/app/build.gradle (versionName & versionCode)
"""

import os
import re
import sys
import json
import time
import argparse
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

def extract_release_doc_meta(base_version):
    """
    从 docs/releases/ 目录下按规范提取对应版本的标题与更新日志
    优先读取 <!-- RELEASE_METADATA_START ... RELEASE_METADATA_END --> 结构化块
    """
    releases_dir = os.path.join(PROJECT_ROOT, "docs", "releases")
    target_file = os.path.join(releases_dir, f"RELEASE-v{base_version}.md")

    # 若不存在精确文件名，尝试在 docs/releases 下寻找最新的 RELEASE-*.md
    if not os.path.exists(target_file) and os.path.exists(releases_dir):
        all_files = sorted(
            [f for f in os.listdir(releases_dir) if f.startswith("RELEASE-v") and f.endswith(".md")],
            reverse=True
        )
        if all_files:
            target_file = os.path.join(releases_dir, all_files[0])

    if not os.path.exists(target_file):
        return None, None

    try:
        with open(target_file, "r", encoding="utf-8") as f:
            content = f.read()

        # 1. 结构化元数据块解析
        m = re.search(r"<!--\s*RELEASE_METADATA_START([\s\S]*?)RELEASE_METADATA_END\s*-->", content)
        if m:
            raw_meta = m.group(1).strip()
            lines = [l.strip() for l in raw_meta.splitlines() if l.strip()]
            title = ""
            changelog_items = []
            in_changelog = False
            for l in lines:
                if l.startswith("title:"):
                    title = l.split("title:", 1)[1].strip().strip("\"'")
                elif l.startswith("changelog:"):
                    in_changelog = True
                elif in_changelog and l.startswith("-"):
                    item = l.lstrip("-").strip().strip("\"'")
                    changelog_items.append(item)

            if title or changelog_items:
                formatted_changelog = "\n".join(
                    [f"{i}. {it}" if not re.match(r"^\d+\.", it) else it for i, it in enumerate(changelog_items, 1)]
                )
                return title, formatted_changelog

        # 2. 降级：从普通 Markdown 块中智能提取
        m_quote = re.search(r"> \*\*([^\*]+)\*\*", content)
        title = m_quote.group(1).strip() if m_quote else ""

        bullets = []
        for m_bullet in re.finditer(r"- \*\*([^*]+)\*\*[:：]\s*([^\r\n]+)", content):
            tag_name = m_bullet.group(1).split("(")[0].strip()
            desc = m_bullet.group(2).strip()
            bullets.append(f"【{tag_name}】{desc}")

        if bullets:
            formatted_changelog = "\n".join([f"{i}. {it}" for i, it in enumerate(bullets[:6], 1)])
            return title, formatted_changelog
    except Exception as e:
        print(f"  [!] 读取或解析版本文档 {target_file} 失败: {e}")

    return None, None

def sync_all(explicit_version=None, explicit_title=None, explicit_changelog=None):
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

    # 3. 动态解析并更新 public/version.json
    public_dir = os.path.join(PROJECT_ROOT, "public")
    os.makedirs(public_dir, exist_ok=True)
    version_json_path = os.path.join(public_dir, "version.json")

    # 从 docs/releases/RELEASE-v*.md 获取动态标题与更新日志
    doc_title, doc_changelog = extract_release_doc_meta(base_version)

    # 依据项目规范：从当前及后续版本起，Release 标题统一仅保留纯净版本号（如 v0.3.0.202611051117）
    # 严禁在标题后拼接长描述，避免 GitHub Release 侧边栏堆砌；详细说明全部在更新日志中展现
    if explicit_title:
        final_title = explicit_title if explicit_title.startswith(version_tag) else f"{version_tag} {explicit_title}".strip()
    else:
        final_title = version_tag

    final_changelog = explicit_changelog or doc_changelog or (
        "1. 【版本升级】应用架构优化与数据体验升级；\n"
        "2. 【体验调优】高精度山峰轨迹与离线瓦片加载优化。"
    )

    release_apk_name = f"weekly-mountain-{version_tag}-release.apk"
    debug_apk_name = f"weekly-mountain-{version_tag}-debug.apk"
    release_download_url = f"https://github.com/lylyuanliang/weekly-mountain/releases/download/{version_tag}/{release_apk_name}"
    debug_download_url = f"https://github.com/lylyuanliang/weekly-mountain/releases/download/{version_tag}/{debug_apk_name}"

    version_json_data = {
        "version": app_version,
        "versionTag": version_tag,
        "title": final_title,
        "publishedAt": date_str,
        "changelog": final_changelog,
        "assetName": release_apk_name,
        "assetSizeText": "约 29 MB",
        "downloadUrl": release_download_url,
        "debugDownloadUrl": debug_download_url,
        "releaseDownloadUrl": release_download_url
    }
    with open(version_json_path, "w", encoding="utf-8") as f:
        json.dump(version_json_data, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"  [✓] public/version.json -> {version_tag} (Title: '{final_title}')")

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
    parser = argparse.ArgumentParser(description="版本同步与时间戳版本升级工具")
    parser.add_argument("version", nargs="?", default=None, help="目标版本号或基线版本 (如 0.3.0 或 0.3.0.202611051055)")
    parser.add_argument("--title", default=None, help="自定义 Release 标题")
    parser.add_argument("--changelog", default=None, help="自定义 Release 更新日志")
    args = parser.parse_args()

    sync_all(args.version, explicit_title=args.title, explicit_changelog=args.changelog)
