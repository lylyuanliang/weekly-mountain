/**
 * tests/test_resource_pack_service.js
 * 客户端资源包动态管理器单元与集成测试套件
 * 覆盖：
 * 1. Web 模式：全量在线可用性、零摩擦动态导入、降级容错
 * 2. 原生 Native 模式：内置默认区域识别、动态区域安装/卸载/状态检查/磁盘统计
 * 3. 损坏降级保护：文件损坏时优雅回退成都默认数据，防止崩溃
 * 4. SHA-256 完整性核验
 * 5. 受限中立词汇红线扫描（0 处违禁词）
 */

import assert from 'node:assert';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const projectRoot = path.resolve(__dirname, '..');

// 模拟本地存储（LocalStorage）
const storageMock = {};
globalThis.localStorage = {
  getItem: (key) => (key in storageMock ? storageMock[key] : null),
  setItem: (key, val) => { storageMock[key] = String(val); },
  removeItem: (key) => { delete storageMock[key]; },
  clear: () => { Object.keys(storageMock).forEach((k) => delete storageMock[k]); }
};

// 内存版 Filesystem 模拟器，兼容 Capacitor Filesystem 核心行为
class MemoryFilesystemAdapter {
  constructor() {
    this.files = new Map();
    this.dirs = new Set(['packs']);
  }

  _norm(p) {
    return p.replace(/\\/g, '/').replace(/^\/+/, '');
  }

  async writeFile({ path: filePath, data }) {
    const norm = this._norm(filePath);
    this.files.set(norm, data);
    // 自动记录父目录
    const segments = norm.split('/');
    for (let i = 1; i < segments.length; i++) {
      this.dirs.add(segments.slice(0, i).join('/'));
    }
    return { uri: `file:///${norm}` };
  }

  async readFile({ path: filePath }) {
    const norm = this._norm(filePath);
    if (!this.files.has(norm)) {
      throw new Error(`File not found: ${filePath}`);
    }
    return { data: this.files.get(norm) };
  }

  async stat({ path: filePath }) {
    const norm = this._norm(filePath);
    if (this.files.has(norm)) {
      const data = this.files.get(norm);
      const size = typeof data === 'string' ? Buffer.byteLength(data, 'utf8') : (data?.byteLength || 0);
      return { type: 'file', size, uri: `file:///${norm}` };
    }
    if (this.dirs.has(norm)) {
      return { type: 'directory', size: 0, uri: `file:///${norm}` };
    }
    throw new Error(`Entry does not exist: ${filePath}`);
  }

  async mkdir({ path: dirPath }) {
    const norm = this._norm(dirPath);
    this.dirs.add(norm);
    return;
  }

  async rmdir({ path: dirPath }) {
    const norm = this._norm(dirPath);
    // 递归删除该目录下所有文件及子目录
    for (const f of Array.from(this.files.keys())) {
      if (f === norm || f.startsWith(`${norm}/`)) {
        this.files.delete(f);
      }
    }
    for (const d of Array.from(this.dirs.keys())) {
      if (d === norm || d.startsWith(`${norm}/`)) {
        this.dirs.delete(d);
      }
    }
    return;
  }
}

async function runTests() {
  console.log('====================================================');
  console.log(' 开始执行客户端资源包管理器单元测试 (ResourcePackService)');
  console.log('====================================================');

  // 1. 动态引入被测服务
  const { ResourcePackService, resourcePackService } = await import('../src/services/resourcePackService.js');

  assert.ok(ResourcePackService, 'ResourcePackService 类必须存在');
  assert.ok(resourcePackService, 'resourcePackService 单例实例必须存在');
  console.log('✔ [1/9] 类定义与单例导出检查通过');

  // 2. Web 模式行为测试
  const memFs = new MemoryFilesystemAdapter();
  const testService = new ResourcePackService({
    filesystem: memFs,
    isNative: false
  });

  assert.strictEqual(await testService.isPackInstalled('chengdu'), true, 'Web端默认已收录地域应判定就绪');
  assert.strictEqual(await testService.isPackInstalled('chongqing'), true, 'Web端重庆地域应判定就绪');
  assert.strictEqual(await testService.isPackInstalled('unknown_city'), false, '未录入的未知地域应返回 false');

  const webInstalled = await testService.getInstalledPacks();
  assert.deepStrictEqual(webInstalled, ['chengdu', 'chongqing'], 'Web端已收录活跃地域列表应完全返回');

  const chengduWebData = await testService.loadRegionMountains('chengdu');
  assert.strictEqual(Array.isArray(chengduWebData), true);
  assert.strictEqual(chengduWebData.length, 51, 'Web端成都山峰数量应为 51 座');

  const chongqingWebData = await testService.loadRegionMountains('chongqing');
  assert.strictEqual(Array.isArray(chongqingWebData), true);
  assert.strictEqual(chongqingWebData.length, 36, 'Web端重庆山峰数量应为 36 座');

  const fallbackWebData = await testService.loadRegionMountains('non_existing_region');
  assert.strictEqual(fallbackWebData.length, 51, 'Web端未知地域应优雅回退至默认成都数据');

  const webStorage = await testService.getStorageUsage();
  assert.strictEqual(webStorage.totalBytes, 0, 'Web端本地存储占用应为 0');
  console.log('✔ [2/9] Web 模式自适应动态加载与优雅降级通过');

  // 3. 原生 Native 模式：内置默认区域测试
  testService.setNativePlatformForTesting(true);

  assert.strictEqual(await testService.isPackInstalled('chengdu'), true, '原生端默认内置地域成都应直接为已就绪');
  const chengduNativeData = await testService.loadRegionMountains('chengdu');
  assert.strictEqual(chengduNativeData.length, 51, '原生端内置成都山峰应为 51 座');

  // 默认内置地域不允许卸载
  await testService.uninstallPack('chengdu');
  assert.strictEqual(await testService.isPackInstalled('chengdu'), true, '默认内置地域不可被卸载');
  console.log('✔ [3/9] 原生 Native 默认内置区域保护与加载通过');

  // 4. 原生 Native 模式：未安装动态区域状态与安全回退
  assert.strictEqual(await testService.isPackInstalled('chongqing'), false, '未安装前重庆区域应判定未就绪');
  const uninstalledFallback = await testService.loadRegionMountains('chongqing');
  assert.strictEqual(uninstalledFallback.length, 51, '未安装动态区域时应安全降级回退成都 51 峰，严禁抛错');
  console.log('✔ [4/9] 原生 Native 未安装动态包平滑降级通过');

  // 5. 原生 Native 模式：下载、校验与解压安装
  const distZipPath = path.join(projectRoot, 'dist-packs', 'pack-chongqing-v1.0.0.zip');
  assert.ok(fs.existsSync(distZipPath), 'dist-packs/pack-chongqing-v1.0.0.zip 必须存在用于测试');
  const zipBuffer = fs.readFileSync(distZipPath);

  // 注入模拟下载通道
  testService.setDownloadHandlerForTesting(async () => {
    return zipBuffer.buffer.slice(zipBuffer.byteOffset, zipBuffer.byteOffset + zipBuffer.byteLength);
  });

  const progressTicks = [];
  await testService.downloadAndInstallPack('chongqing', (pct) => {
    progressTicks.push(pct);
  });

  assert.ok(progressTicks.length > 0, '下载安装应有进度回调上报');
  assert.strictEqual(progressTicks[progressTicks.length - 1], 100, '最后进度必须达到 100%');
  for (let i = 1; i < progressTicks.length; i++) {
    assert.ok(progressTicks[i] >= progressTicks[i - 1], '进度百分比应单调递增');
  }

  assert.strictEqual(await testService.isPackInstalled('chongqing'), true, '安装后重庆应判定已就绪');
  const installedPacks = await testService.getInstalledPacks();
  assert.ok(installedPacks.includes('chengdu') && installedPacks.includes('chongqing'), '已安装列表应包含成都与重庆');

  const chongqingNativeData = await testService.loadRegionMountains('chongqing');
  assert.strictEqual(chongqingNativeData.length, 36, '安装后读取重庆山峰应为 36 座');
  assert.strictEqual(chongqingNativeData[0].name, '缙云山', '首座名峰应为缙云山');

  const storageUsage = await testService.getStorageUsage();
  assert.ok(storageUsage.chongqing > 0, '重庆离线包占用存储应大于 0');
  assert.strictEqual(storageUsage.totalBytes, storageUsage.chongqing, '总存储统计应准确');
  console.log(`✔ [5/9] 原生 Native 离线包下载、解压写入与存储统计通过 (占用: ${storageUsage.totalBytes} 字节)`);

  // 6. 原生 Native 模式：文件损坏与格式异常优雅降级容错
  await memFs.writeFile({
    path: 'packs/chongqing/mountains.json',
    data: 'CORRUPTED_NON_JSON_DATA'
  });
  const corruptFallback = await testService.loadRegionMountains('chongqing');
  assert.strictEqual(corruptFallback.length, 51, '离线文件内容损坏时必须优雅降级为成都 51 峰');
  console.log('✔ [6/9] 原生 Native 离线包文件损坏优雅降级通过');

  // 7. 原生 Native 模式：卸载离线包
  // 先重新安装回来
  await testService.downloadAndInstallPack('chongqing');
  assert.strictEqual(await testService.isPackInstalled('chongqing'), true);

  await testService.uninstallPack('chongqing');
  assert.strictEqual(await testService.isPackInstalled('chongqing'), false, '卸载后应恢复未就绪状态');
  const postUninstallStorage = await testService.getStorageUsage();
  assert.strictEqual(postUninstallStorage.totalBytes, 0, '卸载后存储空间应全部释放归零');
  console.log('✔ [7/9] 原生 Native 离线包卸载与存储空间安全释放通过');

  // 8. SHA-256 篡改校验测试
  const tamperedBuffer = Buffer.from(zipBuffer);
  tamperedBuffer[100] = (tamperedBuffer[100] + 1) % 256; // 随机翻转一个字节
  testService.setDownloadHandlerForTesting(async () => {
    return tamperedBuffer.buffer.slice(tamperedBuffer.byteOffset, tamperedBuffer.byteOffset + tamperedBuffer.byteLength);
  });

  let hashErrorCaught = false;
  try {
    await testService.downloadAndInstallPack('chongqing');
  } catch (err) {
    hashErrorCaught = true;
    assert.ok(err.message.includes('SHA-256'), '校验失败错误信息应明确标明哈希不匹配');
  }
  assert.strictEqual(hashErrorCaught, true, '数据包篡改时必须抛出校验异常拒绝安装');
  assert.strictEqual(await testService.isPackInstalled('chongqing'), false, '校验失败的包严禁标记为已安装');
  console.log('✔ [8/9] 离线包 SHA-256 完整性防篡改核验通过');

  // 9. 受限中立词汇红线扫描（0 处违规）
  const forbiddenWord = String.fromCharCode(0x5b98) + String.fromCharCode(0x65b9);
  const serviceFileContent = fs.readFileSync(path.join(projectRoot, 'src', 'services', 'resourcePackService.js'), 'utf8');
  const testFileContent = fs.readFileSync(__filename, 'utf8');

  assert.strictEqual(serviceFileContent.includes(forbiddenWord), false, `resourcePackService.js 包含受限词: ${forbiddenWord}`);
  assert.strictEqual(testFileContent.includes(forbiddenWord), false, `test_resource_pack_service.js 包含受限词: ${forbiddenWord}`);
  console.log('✔ [9/9] 全文受限用语扫描通过 (0 处违规)');

  console.log('====================================================');
  console.log(' 恭喜！ResourcePackService 所有 9 项测试全部 100% 通过！');
  console.log('====================================================');
}

runTests().catch((err) => {
  console.error('\n❌ 测试执行失败:', err);
  process.exit(1);
});
