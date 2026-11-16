/**
 * tests/test_weather_and_gallery_resilience.js
 * 验证天气多级容灾高可用性、地域名山精准坐标与离线画册图片解析链路
 */

import assert from 'node:assert';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

import {
  getMountainWeatherPoint,
  generateClimatologicalWeather,
  fetchMountainWeather
} from '../src/services/weatherService.js';
import { ResourcePackService } from '../src/services/resourcePackService.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const projectRoot = path.dirname(__dirname);

console.log('====================================================');
console.log(' 开始执行天气服务与画册解析韧性测试套件');
console.log('====================================================');

async function run() {
  const cqDataPath = path.join(projectRoot, 'src', 'data', 'regions', 'chongqing', 'mountains.json');
  const cqMountains = JSON.parse(fs.readFileSync(cqDataPath, 'utf8'));

  // 1. 验证 36 座重庆名山均包含真实经纬度坐标与 3 张画册条目
  console.log('\n▶ [1/5] 验证重庆 36 座山地理坐标与画册图集完整性');
  assert.strictEqual(cqMountains.length, 36, '重庆名山总数应为 36 座');
  for (const m of cqMountains) {
    assert.ok(m.coord && typeof m.coord.lat === 'number' && typeof m.coord.lng === 'number', `山峰 ${m.name} 缺少合法 coord 经纬度`);
    assert.ok(m.lat && m.lng, `山峰 ${m.name} 缺少平级 lat/lng 属性`);
    assert.ok(Array.isArray(m.gallery) && m.gallery.length === 3, `山峰 ${m.name} 应具备 3 张画册条目`);
    for (const g of m.gallery) {
      assert.ok(g.src && g.src.includes('assets/mountains/'), `画册条目 ${g.title} 缺少合法 src`);
      assert.ok(g.title && g.title.length > 0, `画册条目缺少标题`);
      assert.ok(g.desc && g.desc.length > 0, `画册条目缺少描述`);
    }
  }
  console.log('  ✔ 重庆 36 座名山全部具备精准地理坐标与 3 张精修画册元数据');

  // 2. 验证气象坐标提取
  console.log('\n▶ [2/5] 验证气象基准坐标提取');
  const jinyun = cqMountains.find((m) => m.id === 'jinyunshan');
  const pt = getMountainWeatherPoint(jinyun);
  assert.strictEqual(pt.name, '缙云山');
  assert.ok(Math.abs(pt.lat - 29.8356) < 0.01, '缙云山纬度应为 29.83° 附近');
  assert.ok(Math.abs(pt.lng - 106.3951) < 0.01, '缙云山经度应为 106.39° 附近');
  console.log(`  ✔ 缙云山气象坐标提取正确: [${pt.lat}, ${pt.lng}], 海拔: ${pt.alt}m`);

  // 3. 验证离线高山气候模型生成 (零失败容灾)
  console.log('\n▶ [3/5] 验证离线高山气候模型 (零崩溃容灾)');
  const estWeather = generateClimatologicalWeather(jinyun, pt);
  assert.strictEqual(estWeather.days.length, 7, '应生成完整 7 天预报');
  assert.strictEqual(estWeather.isEstimated, true, '应标记为估算模型');
  assert.ok(estWeather.source.includes('离线高山气象模型'), '数据源标识应标明模型');
  assert.ok(estWeather.days[0].maxTemp !== null, '每日应包含最高温度');
  assert.ok(estWeather.days[0].minTemp !== null, '每日应包含最低温度');
  assert.ok(estWeather.warnings.length > 0, '应包含安全徒步气象建议');
  console.log(`  ✔ 离线气候模型正常输出: ${estWeather.days[0].date} ${estWeather.days[0].text} ${estWeather.days[0].maxTemp}°/${estWeather.days[0].minTemp}°`);

  // 4. 验证 fetchMountainWeather 网络容灾与智能回退
  console.log('\n▶ [4/5] 验证 fetchMountainWeather 容灾拉取');
  const liveWeather = await fetchMountainWeather(jinyun, true);
  assert.ok(liveWeather && liveWeather.days.length === 7, '气象服务应返回 7 天数据');
  assert.ok(liveWeather.source, '应具备数据源标识');
  console.log(`  ✔ 气象服务拉取成功，生效源: [${liveWeather.source}]`);

  // 5. 验证资源包服务画册图片解析 (resolveMountainImageUrl)
  console.log('\n▶ [5/5] 验证 ResourcePackService 图片解析逻辑');
  const service = new ResourcePackService({ isNative: true });
  service.setNativePlatformForTesting(true);

  // 内置成都：始终返回 assets 路径
  const cdMountain = { id: 'longquanshan', name: '龙泉山', region_id: 'chengdu' };
  const cdUrl = service.resolveMountainImageUrl(cdMountain, 0);
  assert.strictEqual(cdUrl, 'assets/mountains/longquanshan.jpg', '成都名山应直接返回 assets 路径');

  // 未安装画册的重庆名山：返回 null 触发 Alpine Topo 矢量徽章
  const cqUninstalledUrl = service.resolveMountainImageUrl(jinyun, 0);
  assert.strictEqual(cqUninstalledUrl, null, '未安装画册时应返回 null 优雅降级');

  // 安装画册标记后：返回合法图片路径
  service._setStorageItem('weekly_mountain_pack_gallery_chongqing', 'true');
  const cqInstalledUrl = service.resolveMountainImageUrl(jinyun, 0);
  assert.ok(cqInstalledUrl && cqInstalledUrl.includes('jinyunshan.jpg'), '安装画册后应解析出合法图片路径');
  console.log(`  ✔ 画册分级解析符合预期: 未安装 -> ${cqUninstalledUrl}, 安装后 -> ${cqInstalledUrl}`);

  console.log('\n====================================================');
  console.log(' 恭喜！天气服务与画册解析所有 5 项测试全部 100% 通过！');
  console.log('====================================================');
}

run().catch((err) => {
  console.error('\n❌ 测试失败:', err);
  process.exit(1);
});
