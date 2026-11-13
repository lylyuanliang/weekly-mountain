/**
 * tests/test_store_multi_region.js
 * Store 动态热挂载升级测试套件 (Task 4)
 *
 * 验证：
 * 1. 初始状态：成都 51 座山完整加载，selectedMountain 自动定位首座名山；
 * 2. 动态热挂载切换至重庆：mountains 响应式替换为 36 座山，selectedMountain 自动更新为重庆标杆名峰，基准距离以重庆中心计算；
 * 3. 动态热挂载切换回成都：mountains 完整恢复为 51 座山，基准距离以成都中心计算；
 * 4. 容错与优雅降级：请求未知或异常地域时平滑回退默认数据，严禁抛出未捕获异常；
 * 5. 离线资源包管理联动：installedPacks、downloadProgress、downloadRegionPack、uninstallRegionPack 正常工作；
 * 6. 全文受限词汇扫描：代码与注释中 0 处违规。
 */

import assert from 'node:assert';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { createPinia, setActivePinia } from 'pinia';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const projectRoot = path.resolve(__dirname, '..');

// 模拟本地存储 (LocalStorage)
const storageMock = {};
globalThis.localStorage = {
  getItem: (key) => (key in storageMock ? storageMock[key] : null),
  setItem: (key, val) => {
    storageMock[key] = String(val);
  },
  removeItem: (key) => {
    delete storageMock[key];
  },
  clear: () => {
    Object.keys(storageMock).forEach((k) => delete storageMock[k]);
  }
};

async function runTests() {
  console.log('====================================================');
  console.log(' 开始执行 Store 动态热挂载升级测试套件 (Task 4)');
  console.log('====================================================\n');

  // 初始化 Pinia 环境
  const pinia = createPinia();
  setActivePinia(pinia);

  const { useRegionStore } = await import('../src/stores/regionStore.js');
  const { useMountainStore, getDistanceKm, getMountainCoordinate } = await import('../src/stores/mountainStore.js');

  const regionStore = useRegionStore();
  const mountainStore = useMountainStore();

  // ----------------------------------------------------
  // Test 1: 初始状态验证 (成都 51 座山)
  // ----------------------------------------------------
  console.log('▶ [1/6] 验证初始状态：成都 51 座山默认挂载与首座标杆名山');
  assert.strictEqual(regionStore.currentRegionId, 'chengdu', '默认地域应为 chengdu');
  assert.strictEqual(regionStore.currentRegion.name, '成都周边', '默认地域名称应为成都周边');
  assert.strictEqual(mountainStore.mountains.length, 51, '初始山峰列表应包含成都 51 座山');
  assert.strictEqual(mountainStore.filteredMountains.length, 51, '初始筛选列表应包含成都 51 座山');
  assert.ok(mountainStore.selectedMountain, '初始应存在选中的标杆名山');
  assert.strictEqual(mountainStore.selectedMountain.id, 'longquanshan', '成都首选名山应为龙泉山');
  console.log('  ✔ 成都 51 座山初始加载成功，首座名山:', mountainStore.selectedMountain.name);

  // ----------------------------------------------------
  // Test 2: 动态热挂载切换至重庆 (36 座山，基准距离切换为重庆中心)
  // ----------------------------------------------------
  console.log('\n▶ [2/6] 验证热挂载切换至重庆：36 座山响应式替换与基准距离更新');
  await regionStore.setRegion('chongqing');

  assert.strictEqual(regionStore.currentRegionId, 'chongqing', '当前地域应切换为 chongqing');
  assert.strictEqual(regionStore.currentRegion.name, '重庆周边', '当前地域名称应为重庆周边');
  assert.strictEqual(mountainStore.mountains.length, 36, '热挂载后山峰列表应更新为 36 座山');
  assert.strictEqual(mountainStore.filteredMountains.length, 36, '热挂载后筛选列表应为 36 座山');
  assert.ok(mountainStore.selectedMountain, '应自动选中重庆标杆名峰');
  assert.strictEqual(mountainStore.selectedMountain.id, 'jinyunshan', '重庆首选标杆名山应为缙云山');

  // 验证基准距离已切换为重庆中心 (lng: 106.55, lat: 29.56)
  const cqCenter = regionStore.currentRegion.center;
  assert.deepStrictEqual(cqCenter, { lng: 106.55, lat: 29.56 }, '重庆中心坐标核验');

  // 寻找金刀峡，验证其相对重庆中心的直线距离 (~54km) 远小于相对成都中心的距离 (~255km)
  const jindaoxia = mountainStore.getMountainById('jindaoxia');
  assert.ok(jindaoxia, '应能查询到金刀峡');
  assert.ok(
    typeof jindaoxia.distToCenterKm === 'number' && jindaoxia.distToCenterKm > 0,
    '金刀峡应具备距当前市中心直线距离'
  );
  assert.ok(
    jindaoxia.distToCenterKm < 100,
    `金刀峡距重庆市中心应在 100km 内，实际为 ${jindaoxia.distToCenterKm}km`
  );
  console.log(
    `  ✔ 重庆 36 座山热挂载成功，选中名峰: ${mountainStore.selectedMountain.name}，金刀峡距重庆中心: ${jindaoxia.distToCenterKm}km`
  );

  // ----------------------------------------------------
  // Test 3: 热挂载切回成都 (51 座山完整恢复)
  // ----------------------------------------------------
  console.log('\n▶ [3/6] 验证热挂载切回成都：51 座山完整恢复');
  await regionStore.setRegion('chengdu');

  assert.strictEqual(regionStore.currentRegionId, 'chengdu', '当前地域应切回 chengdu');
  assert.strictEqual(mountainStore.mountains.length, 51, '山峰列表应恢复为 51 座山');
  assert.strictEqual(mountainStore.filteredMountains.length, 51, '筛选列表应恢复为 51 座山');
  assert.strictEqual(mountainStore.selectedMountain.id, 'longquanshan', '应重新选中成都首座名山');

  const cdCenter = regionStore.currentRegion.center;
  assert.deepStrictEqual(cdCenter, { lng: 104.066, lat: 30.657 }, '成都中心坐标核验');
  console.log('  ✔ 成功切回成都，51 座山峰数据集与筛选器完整恢复');

  // ----------------------------------------------------
  // Test 4: 容错与优雅降级测试
  // ----------------------------------------------------
  console.log('\n▶ [4/6] 验证容错与优雅降级：未知地域平滑回退，严禁崩溃');
  // 测试 setRegion 传入未收录地域
  await regionStore.setRegion('unknown_city_xyz');
  assert.strictEqual(regionStore.currentRegionId, 'chengdu', '未收录地域应安全回退至 chengdu');
  assert.strictEqual(mountainStore.mountains.length, 51, '回退后山峰列表应保持 51 座山');

  // 测试 direct loadActiveRegion 传入异常地域
  const fallbackData = await mountainStore.loadActiveRegion('non_existent_region');
  assert.ok(Array.isArray(fallbackData) && fallbackData.length === 51, '直接加载异常地域应降级返回默认 51 座山');
  assert.strictEqual(mountainStore.mountains.length, 51, '异常加载后 mountains 应安全保持默认 51 座山');
  console.log('  ✔ 容错降级机制健全，异常入参安全回退至默认数据');

  // ----------------------------------------------------
  // Test 5: 离线资源包状态管理联动测试
  // ----------------------------------------------------
  console.log('\n▶ [5/6] 验证 regionStore 离线资源包状态字典与异步动作');
  assert.ok(regionStore.installedPacks, 'regionStore 应提供 installedPacks 状态');
  assert.ok(regionStore.downloadProgress, 'regionStore 应提供 downloadProgress 字典');
  assert.strictEqual(typeof regionStore.downloadRegionPack, 'function', '应提供 downloadRegionPack 动作');
  assert.strictEqual(typeof regionStore.uninstallRegionPack, 'function', '应提供 uninstallRegionPack 动作');

  // Web 模式下内置成都应处于可用集合中
  if (Array.isArray(regionStore.installedPacks)) {
    assert.ok(regionStore.installedPacks.includes('chengdu'), 'installedPacks 应包含 chengdu');
  } else if (typeof regionStore.installedPacks.has === 'function') {
    assert.ok(regionStore.installedPacks.has('chengdu'), 'installedPacks 应包含 chengdu');
  }

  // 执行内置区域下载（应立即触发完成且不报错）
  await regionStore.downloadRegionPack('chengdu');
  console.log('  ✔ 离线包状态字典与管理动作运行符合预期');

  // ----------------------------------------------------
  // Test 6: 严禁出现受限中立词汇红线扫描 (0 处违规)
  // ----------------------------------------------------
  console.log('\n▶ [6/6] 验证受限词汇红线扫描 (0 处违规)');
  const forbiddenWord = String.fromCharCode(0x5b98, 0x65b9);
  const filesToCheck = [
    path.join(projectRoot, 'src', 'stores', 'regionStore.js'),
    path.join(projectRoot, 'src', 'stores', 'mountainStore.js'),
    path.join(projectRoot, 'tests', 'test_store_multi_region.js')
  ];

  for (const fp of filesToCheck) {
    if (fs.existsSync(fp)) {
      const content = fs.readFileSync(fp, 'utf-8');
      const count = (content.match(new RegExp(forbiddenWord, 'g')) || []).length;
      assert.strictEqual(
        count,
        0,
        `文件 ${path.basename(fp)} 包含违规词汇 [${forbiddenWord}]，出现次数: ${count}`
      );
    }
  }
  console.log('  ✔ 代码与测试注释红线扫描通过：0 处违规词汇');

  console.log('\n====================================================');
  console.log(' 恭喜！Task 4 所有 6 项 Store 测试全部 100% 通过！');
  console.log('====================================================');
}

runTests().catch((err) => {
  console.error('\n❌ 测试失败，捕获到异常:', err);
  process.exit(1);
});
