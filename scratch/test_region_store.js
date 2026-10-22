import assert from 'node:assert';
import { setActivePinia, createPinia } from 'pinia';
import { useRegionStore } from '../src/stores/regionStore.js';
import { useMountainStore } from '../src/stores/mountainStore.js';

// Setup mock global localStorage
globalThis.localStorage = {
  _data: {},
  getItem(k) { return this._data[k] || null; },
  setItem(k, v) { this._data[k] = String(v); },
  removeItem(k) { delete this._data[k]; },
  clear() { this._data = {}; }
};

setActivePinia(createPinia());

const regionStore = useRegionStore();
const mountainStore = useMountainStore();

console.log('--- Testing Region Store and Mountain Store Integration ---');

// Test 1: Check initial region
assert.strictEqual(regionStore.currentRegionId, 'chengdu', 'Default region should be chengdu');
assert.strictEqual(regionStore.currentRegion.name, '成都周边', 'Current region name should be 成都周边');
assert.strictEqual(regionStore.currentRegion.mountainsCount, 51, 'Chengdu has 51 mountains');
console.log('✔ Test 1 Passed: Default region is chengdu with 51 mountains');

// Test 2: Filtered mountains for Chengdu
assert.strictEqual(mountainStore.filteredMountains.length, 51, 'All 51 mountains match chengdu');
assert.ok(mountainStore.selectedMountain, 'Selected mountain exists');
console.log('✔ Test 2 Passed: All 51 mountains filtered for chengdu');

// Test 3: Switch to planned region
regionStore.setRegion('chongqing');
assert.strictEqual(regionStore.currentRegionId, 'chongqing');
assert.strictEqual(regionStore.currentRegion.name, '重庆周边');
assert.strictEqual(mountainStore.filteredMountains.length, 0, 'Chongqing currently has 0 mountains');
console.log('✔ Test 3 Passed: Switching to chongqing updates currentRegion and filteredMountains');

// Test 4: Switch back to chengdu
regionStore.setRegion('chengdu');
assert.strictEqual(mountainStore.filteredMountains.length, 51);
console.log('✔ Test 4 Passed: Switching back to chengdu restores 51 mountains');

// Test 5: Regions list
assert.ok(regionStore.activeRegions.length >= 1, 'At least 1 active region');
assert.ok(regionStore.plannedRegions.length >= 4, 'At least 4 planned regions (Chongqing, Xi\'an, Kunming, Beijing)');
console.log('✔ Test 5 Passed: Active and planned regions properly categorized');

console.log('====================================================');
console.log('All Region Store Integration Tests Passed!');
console.log('====================================================');
