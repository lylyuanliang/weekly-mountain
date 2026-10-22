import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const sourceDir = path.resolve(__dirname, '../assets/mountains');
const targetDir = path.resolve(__dirname, '../dist/assets/mountains');

if (!fs.existsSync(sourceDir)) {
  console.warn(`[copy_assets] Source directory not found: ${sourceDir}`);
  process.exit(0);
}

fs.mkdirSync(targetDir, { recursive: true });

const files = fs.readdirSync(sourceDir);
let copiedCount = 0;
let totalBytes = 0;

for (const file of files) {
  if (file.toLowerCase().endsWith('.jpg') || file.toLowerCase().endsWith('.jpeg') || file.toLowerCase().endsWith('.png') || file.toLowerCase().endsWith('.webp')) {
    const srcFile = path.join(sourceDir, file);
    const destFile = path.join(targetDir, file);
    fs.copyFileSync(srcFile, destFile);
    copiedCount++;
    totalBytes += fs.statSync(destFile).size;
  }
}

console.log(`[copy_assets] Successfully synced ${copiedCount} assets (${(totalBytes / (1024 * 1024)).toFixed(2)} MB) to dist/assets/mountains/`);
