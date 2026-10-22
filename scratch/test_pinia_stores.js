/**
 * scratch/test_pinia_stores.js
 * Unit tests for Pinia Stores: mountainStore, checkinStore, planStore, themeStore.
 */

import assert from 'node:assert';
import { createPinia, setActivePinia } from 'pinia';

// Setup Mock LocalStorage & Mock DOM document for Node environment
const mockStorage = {};
globalThis.localStorage = {
  getItem: (key) => (key in mockStorage ? mockStorage[key] : null),
  setItem: (key, val) => { mockStorage[key] = String(val); },
  removeItem: (key) => { delete mockStorage[key]; },
  clear: () => { Object.keys(mockStorage).forEach((k) => delete mockStorage[k]); }
};

const domAttributes = {};
globalThis.document = {
  documentElement: {
    setAttribute: (attr, val) => { domAttributes[attr] = String(val); },
    getAttribute: (attr) => domAttributes[attr] || null
  }
};

async function runTests() {
  console.log('--- Starting Pinia Stores Unit Tests ---');

  // Step 1: Initialize Pinia
  const pinia = createPinia();
  setActivePinia(pinia);

  // Import stores
  const { useMountainStore } = await import('../src/stores/mountainStore.js');
  const { useCheckinStore } = await import('../src/stores/checkinStore.js');
  const { usePlanStore } = await import('../src/stores/planStore.js');
  const { useThemeStore } = await import('../src/stores/themeStore.js');

  const mountainStore = useMountainStore();
  const checkinStore = useCheckinStore();
  const planStore = usePlanStore();
  const themeStore = useThemeStore();

  // Test 1: mountainStore loaded 51 mountains (including Guangwushan), default filteredMountains.length === 51
  assert.strictEqual(mountainStore.mountains.length, 51, 'Mountain list must have 51 items');
  assert.strictEqual(mountainStore.filteredMountains.length, 51, 'Default filtered list must have 51 items');
  assert.ok(mountainStore.selectedMountainId, 'selectedMountainId should be initialized to first mountain');
  console.log('✔ Test 1 Passed: mountainStore loads 51 mountains');

  // Test 1b: Distance calculation and near-to-far sorting
  const first = mountainStore.filteredMountains[0];
  const last = mountainStore.filteredMountains[mountainStore.filteredMountains.length - 1];
  assert.strictEqual(first.id, 'longquanshan', 'First mountain must be Longquanshan (nearest)');
  assert.ok(first.distToCenterKm >= 30 && first.distToCenterKm <= 45, 'Longquanshan distToCenterKm should be ~37.8km');
  assert.strictEqual(last.id, 'guangwushan', 'Last mountain must be Guangwushan (furthest)');
  assert.ok(last.distToCenterKm >= 340, 'Guangwushan distToCenterKm should be ~347.9km');

  // Verify monotonic non-decreasing order of distance
  for (let i = 0; i < mountainStore.filteredMountains.length - 1; i++) {
    const cur = mountainStore.filteredMountains[i].distToCenterKm || 0;
    const next = mountainStore.filteredMountains[i + 1].distToCenterKm || 0;
    assert.ok(cur <= next, `Mountains must be sorted near to far: index ${i} (${cur}km) <= index ${i+1} (${next}km)`);
  }
  console.log('✔ Test 1b Passed: Distance sorting from near to far is strictly monotonic (Longquanshan 37.8km -> Guangwushan 347.9km)');

  // Test 2: Search "达瓦" precisely matches "达瓦更扎"
  mountainStore.setSearch('达瓦');
  assert.ok(mountainStore.filteredMountains.length >= 1, 'Search "达瓦" should return results');
  assert.strictEqual(mountainStore.filteredMountains[0].id, 'dawagengzha', 'First search result ID should be dawagengzha');
  mountainStore.setSearch('达瓦更扎');
  assert.strictEqual(mountainStore.filteredMountains[0].name, '达瓦更扎', 'Search "达瓦更扎" should return 达瓦更扎');
  mountainStore.setSearch('');
  assert.strictEqual(mountainStore.filteredMountains.length, 51, 'Clearing search restores 51 mountains');
  console.log('✔ Test 2 Passed: Search "达瓦" matches "达瓦更扎"');

  // Test 3: Difficulty filter "L3" correctly filters
  mountainStore.setFilter('difficulty', 'L3');
  const l3Count = mountainStore.filteredMountains.length;
  assert.ok(l3Count > 0 && l3Count < 51, 'L3 filter should return subset of mountains');
  assert.ok(mountainStore.filteredMountains.every((m) => m.difficulty === 'L3'), 'All filtered mountains must be L3');
  mountainStore.resetFilters();
  assert.strictEqual(mountainStore.filteredMountains.length, 51, 'Reset filters restores 51 mountains');
  console.log('✔ Test 3 Passed: Difficulty filter works');

  // Test 4: checkinStore check dawagengzha => ascent +866m, dist +13.9km, isDone === true
  mockStorage['weekly_mountain_checked'] = JSON.stringify([]);
  checkinStore.checkedIds = [];
  assert.strictEqual(checkinStore.isDone('dawagengzha'), false, 'dawagengzha initially not done');
  assert.strictEqual(checkinStore.stats.doneCount, 0, 'Initial doneCount is 0');
  assert.strictEqual(checkinStore.stats.totalAscent, 0, 'Initial totalAscent is 0');
  assert.strictEqual(checkinStore.stats.totalDistance, 0, 'Initial totalDistance is 0');

  checkinStore.toggleCheckin('dawagengzha');
  assert.strictEqual(checkinStore.isDone('dawagengzha'), true, 'dawagengzha should now be done');
  assert.strictEqual(checkinStore.stats.doneCount, 1, 'doneCount should be 1');
  assert.strictEqual(checkinStore.stats.totalAscent, 866, 'totalAscent for dawagengzha must be exactly 866m');
  assert.strictEqual(checkinStore.stats.totalDistance, 13.9, 'totalDistance for dawagengzha must be exactly 13.9km');
  assert.strictEqual(checkinStore.stats.rank.level, 'LV.1', 'Rank level should be LV.1');
  assert.strictEqual(checkinStore.stats.rank.title, '初探山岳', 'Rank title should be 初探山岳');
  assert.strictEqual(checkinStore.stats.completionRate, 2, 'Completion rate should be 2% (1/50)');

  // Verify LocalStorage persistence for checkedIds
  assert.ok(mockStorage['weekly_mountain_checked'].includes('dawagengzha'), 'checkedIds persisted in localStorage: weekly_mountain_checked');
  console.log('✔ Test 4 Passed: Checkin dawagengzha telemetry calculations & persistence accurate (866m, 13.9km)');

  // Test 5: themeStore cycles stitch -> ink -> camp -> stitch
  themeStore.setTheme('stitch');
  assert.strictEqual(themeStore.theme, 'stitch', 'Theme is stitch');
  assert.strictEqual(domAttributes['data-theme'], 'stitch', 'DOM data-theme is stitch');
  assert.strictEqual(mockStorage['weekly_mountain_theme'], 'stitch', 'LocalStorage weekly_mountain_theme is stitch');

  themeStore.cycleTheme();
  assert.strictEqual(themeStore.theme, 'ink', 'Theme cycled to ink');
  assert.strictEqual(domAttributes['data-theme'], 'ink', 'DOM data-theme updated to ink');
  assert.strictEqual(mockStorage['weekly_mountain_theme'], 'ink', 'LocalStorage updated to ink');

  themeStore.cycleTheme();
  assert.strictEqual(themeStore.theme, 'camp', 'Theme cycled to camp');
  assert.strictEqual(domAttributes['data-theme'], 'camp', 'DOM data-theme updated to camp');

  themeStore.cycleTheme();
  assert.strictEqual(themeStore.theme, 'stitch', 'Theme cycled back to stitch');
  assert.strictEqual(domAttributes['data-theme'], 'stitch', 'DOM data-theme updated to stitch');
  console.log('✔ Test 5 Passed: Theme cycling works (stitch -> ink -> camp -> stitch)');

  // Test 6: planStore adds, removes, applies preset
  planStore.clearPlans();
  planStore.addToPlan('dawagengzha', 1);
  assert.strictEqual(planStore.plans.length, 1, 'plans should have 1 week');
  assert.ok(planStore.plans[0].items.includes('dawagengzha'), 'Week 1 should contain dawagengzha');
  assert.ok(mockStorage['weekly_mountain_plans'].includes('dawagengzha'), 'plans persisted in localStorage: weekly_mountain_plans');

  planStore.removeFromPlan('dawagengzha', 1);
  assert.strictEqual(planStore.plans[0].items.includes('dawagengzha'), false, 'dawagengzha removed from week 1');

  // Apply preset
  planStore.applyPreset('autumn8');
  assert.strictEqual(planStore.plans.length, 8, 'autumn8 preset should create 8 weeks');
  assert.strictEqual(planStore.plans[0].items[0], 'jiufengshan', 'First mountain of autumn8 is jiufengshan');
  console.log('✔ Test 6 Passed: planStore add, remove, and preset apply work');

  // Test 7: checkinStore backup export and restore
  const backupJson = checkinStore.exportBackup();
  const parsedBackup = JSON.parse(backupJson);
  assert.ok(parsedBackup.checked, 'Backup must contain checked list');
  assert.ok(parsedBackup.plans, 'Backup must contain plans');
  assert.strictEqual(parsedBackup.theme, 'stitch', 'Backup must contain theme');

  // Reset and restore
  checkinStore.checkedIds = [];
  planStore.clearPlans();
  assert.strictEqual(checkinStore.checkedIds.length, 0);

  const importResult = checkinStore.importBackup(backupJson);
  assert.strictEqual(importResult, true, 'Import should succeed');
  assert.strictEqual(checkinStore.isDone('dawagengzha'), true, 'Restored checkin should contain dawagengzha');
  assert.strictEqual(planStore.plans.length, 8, 'Restored plans should contain 8 weeks');
  console.log('✔ Test 7 Passed: Backup export and import restore successfully');

  console.log('\n=======================================');
  console.log('All Pinia store tests passed!');
  console.log('=======================================');
}

runTests().catch((err) => {
  console.error('\n❌ Test execution failed:');
  console.error(err);
  process.exit(1);
});
