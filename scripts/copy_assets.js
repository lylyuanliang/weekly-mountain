import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const rootDir = path.resolve(__dirname, '..');
const baselineDir = path.resolve(rootDir, 'assets/mountains');
const distMountainsDir = path.resolve(rootDir, 'dist/assets/mountains');
const androidMountainsDir = path.resolve(rootDir, 'android/app/src/main/assets/public/assets/mountains');

if (!fs.existsSync(baselineDir)) {
  console.error(`[copy_assets] FATAL: Baseline source directory not found: ${baselineDir}`);
  process.exit(1);
}

// 确保目标目录存在
fs.mkdirSync(distMountainsDir, { recursive: true });
fs.mkdirSync(androidMountainsDir, { recursive: true });

// 1. 同步基线成都图片至 Web (dist) 与 Android 原生工程
const baselineFiles = fs.readdirSync(baselineDir);
const baselineSet = new Set(baselineFiles);

let baselineCopied = 0;
let baselineBytes = 0;

for (const file of baselineFiles) {
  if (/\.(jpg|jpeg|png|webp)$/i.test(file)) {
    const srcFile = path.join(baselineDir, file);
    const stat = fs.statSync(srcFile);

    fs.copyFileSync(srcFile, path.join(distMountainsDir, file));
    fs.copyFileSync(srcFile, path.join(androidMountainsDir, file));

    baselineCopied++;
    baselineBytes += stat.size;
  }
}

// 2. 清理 Android assets 中多余的扩展画册（保持安装包极致轻量，画册仅按需下载）
const androidFiles = fs.readdirSync(androidMountainsDir);
let androidPruned = 0;
for (const af of androidFiles) {
  if (!baselineSet.has(af) && /\.(jpg|jpeg|png|webp)$/i.test(af)) {
    fs.unlinkSync(path.join(androidMountainsDir, af));
    androidPruned++;
  }
}

// 3. 扫描并同步各扩展地域画册图片至 Web 生产目录 (dist)，保障 Web 端免下载零摩擦全量畅享
const regionsDir = path.resolve(rootDir, 'src/data/regions');
let galleryCopied = 0;
let galleryBytes = 0;

if (fs.existsSync(regionsDir)) {
  const regions = fs.readdirSync(regionsDir);
  for (const reg of regions) {
    const gDir = path.join(regionsDir, reg, 'gallery');
    if (fs.existsSync(gDir)) {
      const gFiles = fs.readdirSync(gDir);
      for (const gf of gFiles) {
        if (/\.(jpg|jpeg|png|webp)$/i.test(gf)) {
          const gSrc = path.join(gDir, gf);
          const stat = fs.statSync(gSrc);
          fs.copyFileSync(gSrc, path.join(distMountainsDir, gf));
          galleryCopied++;
          galleryBytes += stat.size;
        }
      }
    }
  }
}

console.log(`[copy_assets] 资产分发与边界隔离完成：`);
console.log(`  - 基线成都名山: ${baselineCopied} 张 (${(baselineBytes / 1024 / 1024).toFixed(2)} MB)`);
console.log(`  - 扩展地域画册 (仅Web端): ${galleryCopied} 张 (${(galleryBytes / 1024 / 1024).toFixed(2)} MB)`);
console.log(`  - Web 生产目录 (dist): 共 ${baselineCopied + galleryCopied} 张图片`);
console.log(`  - Android 安装包目录: 精准保留 ${baselineCopied} 张基线底图 (清理冗余: ${androidPruned} 张)`);
