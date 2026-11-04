import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const sourceDir = path.resolve(__dirname, '../assets/mountains');
const targetDirs = [
  path.resolve(__dirname, '../dist/assets/mountains'),
  path.resolve(__dirname, '../android/app/src/main/assets/public/assets/mountains'),
];

if (!fs.existsSync(sourceDir)) {
  console.error(`[copy_assets] FATAL: Source directory not found: ${sourceDir}`);
  process.exit(1);
}

for (const targetDir of targetDirs) {
  fs.mkdirSync(targetDir, { recursive: true });
}

const files = fs.readdirSync(sourceDir);
let copiedCount = 0;
let totalBytes = 0;

for (const file of files) {
  if (file.toLowerCase().endsWith('.jpg') || file.toLowerCase().endsWith('.jpeg') || file.toLowerCase().endsWith('.png') || file.toLowerCase().endsWith('.webp')) {
    const srcFile = path.join(sourceDir, file);
    const fileSize = fs.statSync(srcFile).size;
    for (const targetDir of targetDirs) {
      const destFile = path.join(targetDir, file);
      fs.copyFileSync(srcFile, destFile);
    }
    copiedCount++;
    totalBytes += fileSize;
  }
}

if (copiedCount === 0 || totalBytes < 10 * 1024 * 1024) {
  console.error(`[copy_assets] FATAL: Expected at least 10MB assets, but copied ${copiedCount} files (${(totalBytes / (1024 * 1024)).toFixed(2)} MB). Aborting build.`);
  process.exit(1);
}

console.log(`[copy_assets] Successfully synced ${copiedCount} assets (${(totalBytes / (1024 * 1024)).toFixed(2)} MB) to both dist/ and android assets!`);
