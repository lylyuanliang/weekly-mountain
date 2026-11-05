import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const rootDir = path.resolve(__dirname, '..');
const distDir = path.resolve(rootDir, 'dist');
const androidAssetsDir = path.resolve(rootDir, 'android/app/src/main/assets');
const androidPublicDir = path.resolve(androidAssetsDir, 'public');

console.log('[sync_android_assets] Starting web asset synchronization to Android...');

// 1. Verify dist directory exists and has index.html
const indexHtmlPath = path.resolve(distDir, 'index.html');
if (!fs.existsSync(indexHtmlPath)) {
  console.error(`[sync_android_assets] FATAL: dist/index.html not found at ${indexHtmlPath}. Run vite build first!`);
  process.exit(1);
}

// 2. Recursive copy helper
function copyDirRecursive(src, dest) {
  fs.mkdirSync(dest, { recursive: true });
  const entries = fs.readdirSync(src, { withFileTypes: true });

  for (const entry of entries) {
    const srcPath = path.join(src, entry.name);
    const destPath = path.join(dest, entry.name);

    if (entry.isDirectory()) {
      copyDirRecursive(srcPath, destPath);
    } else {
      fs.copyFileSync(srcPath, destPath);
    }
  }
}

// 3. Copy dist to android/app/src/main/assets/public
console.log(`[sync_android_assets] Copying ${distDir} -> ${androidPublicDir}`);
copyDirRecursive(distDir, androidPublicDir);

// 4. Ensure capacitor.config.json exists in android/app/src/main/assets
const rootCapConfig = path.resolve(rootDir, 'capacitor.config.json');
const androidCapConfig = path.resolve(androidAssetsDir, 'capacitor.config.json');
if (fs.existsSync(rootCapConfig)) {
  fs.copyFileSync(rootCapConfig, androidCapConfig);
  console.log(`[sync_android_assets] Synced capacitor.config.json to ${androidCapConfig}`);
} else {
  console.error(`[sync_android_assets] Warning: Root capacitor.config.json not found!`);
}

// 5. Ensure capacitor.plugins.json exists
const androidPluginsJson = path.resolve(androidAssetsDir, 'capacitor.plugins.json');
if (!fs.existsSync(androidPluginsJson)) {
  const defaultPlugins = [
    {
      pkg: '@capacitor/app-launcher',
      classpath: 'com.capacitorjs.plugins.applauncher.AppLauncherPlugin'
    }
  ];
  fs.writeFileSync(androidPluginsJson, JSON.stringify(defaultPlugins, null, 2), 'utf-8');
  console.log(`[sync_android_assets] Created fallback capacitor.plugins.json`);
}

// 6. Verification assertions
const targetIndexHtml = path.resolve(androidPublicDir, 'index.html');
if (!fs.existsSync(targetIndexHtml) || fs.statSync(targetIndexHtml).size < 100) {
  console.error(`[sync_android_assets] FATAL: target index.html missing or too small!`);
  process.exit(1);
}

const targetMountainsDir = path.resolve(androidPublicDir, 'assets/mountains');
if (!fs.existsSync(targetMountainsDir)) {
  console.error(`[sync_android_assets] FATAL: target assets/mountains missing!`);
  process.exit(1);
}

const mountainFiles = fs.readdirSync(targetMountainsDir);
if (mountainFiles.length < 50) {
  console.error(`[sync_android_assets] FATAL: only ${mountainFiles.length} mountain assets found in target (expected >= 50)!`);
  process.exit(1);
}

console.log(`[sync_android_assets] SUCCESS: Android assets synced and verified!`);
console.log(`  - public/index.html: ${fs.statSync(targetIndexHtml).size} bytes`);
console.log(`  - public/assets/mountains: ${mountainFiles.length} files`);
console.log(`  - capacitor.config.json: ${fs.existsSync(androidCapConfig) ? 'OK' : 'MISSING'}`);
console.log(`  - capacitor.plugins.json: ${fs.existsSync(androidPluginsJson) ? 'OK' : 'MISSING'}`);
