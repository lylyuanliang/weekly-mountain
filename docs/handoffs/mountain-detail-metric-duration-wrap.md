# 主题：山峰详情核心概况「预计耗时」移动端防换行与多方案适配优化

- 当前状态：已完成 (completed)
- 关联反馈：`#1794280517773`
- 移动端视口：369 x 821, DPR 3.25 (Android 原生客户端, Xiaomi 15)
- 恢复入口：`src/components/detail/MountainDetailSheet.vue`

## 1. 目标与背景
真机反馈 `#1794280517773` 指出：在 369px 宽度的移动设备上，山峰详情页「核心概况」三列网格中的「预计耗时」卡片，当值为「半日/单日」时发生折行（第一行“半日/单”、第二行“日”），不仅破坏了界面数字指标的整齐排版，也与同行的「徒步里程（5 km）」和「成都车程（0.5 h）」形成了割裂。用户提议：“灵活点，或者不用中文汉字，有没有其他方案”。

## 2. 根因剖析与方案设计

### 2.1 根因
1. **容器净宽受限**：在 369px 屏幕上，三列网格（`col-span-2`）每张卡片总宽约 107px，扣除 `p-2.5`（20px）后内部有效内容宽度仅 87px；
2. **大字号汉字溢出**：原本预计耗时直接将长达 5 个全角字符的字符串（如“半日/单日”）填入 `text-lg font-black`（18px 粗体）容器中，字符总宽约 85-90px，必然触发行末强制折行；
3. **视觉韵律不一致**：左侧卡片为大数字+小单位（`5 km`），右侧为大数字+小单位（`0.5 h`），中间卡片原本却塞入了中文长短语。

### 2.2 解决方案：高山拓扑标准「数值 + 单位」与防折行体系
1. **数据解析器深度升级 (`durationInfo`)**：
   - 智能解析山峰主记录及路线中所有时间字段（`duration_h`, `time_h`, `hours`, `time`, `duration`）；
   - 按国际户外与高山拓扑规范，将耗时拆分为结构化的 `{ value, unit, sublabel }`：
     - 半天/半日 ➔ `value: '0.5'`, `unit: 'd'`, `sublabel: '半日往返'`；
     - 单日/半日区间 ➔ `value: '0.5-1'`, `unit: 'd'`, `sublabel: '单日/半日'`；
     - 小时区间（如 4-5小时、12小时） ➔ `value: '4-5'`, `unit: 'h'`, `sublabel: '配速参考'`；
     - 分钟短线（如 10-15分钟） ➔ `value: '10-15'`, `unit: 'min'`, `sublabel: '单程登顶'`；
     - 多日行程（如 2天） ➔ `value: '2'`, `unit: 'd'`, `sublabel: '多日行程'`。
2. **排版对齐与视觉一致性**：
   - 耗时卡片与里程、车程完全统一，采用 `<span class="font-black text-secondary font-mono leading-none">{{ durationInfo.value }}</span>` + `<span class="text-[10px] font-bold text-on-surface-variant ml-0.5">{{ durationInfo.unit }}</span>`；
   - 补充 10px 紧凑副标展示中文语境（如“半日往返”、“单日全天”）；
3. **样式防溢出防御**：
   - 增加 `overflow-hidden`、`whitespace-nowrap`、`truncate`；
   - 当数值字符较长（> 5）时自适应降级字号（`:class="durationInfo.value.length > 5 ? 'text-base' : 'text-lg'"`），确保在任何极限窄屏设备上都不可能断行。

## 3. 修改文件清单
- `src/components/detail/MountainDetailSheet.vue`：
  - Template：Bento 3、Bento 4、Bento 5 统一部署 `overflow-hidden` 与 `whitespace-nowrap flex items-baseline`；
  - Script：新增 `durationInfo` 响应式推导函数，保持 `durationText` 向后兼容。

## 4. 自测与端到端验证
1. **Playwright 真机视口验证 (369 x 821, DPR 3.0, Android 16)**：
   - 针对反馈来源山峰「龙泉山」，验证渲染为 `0.5 d`（数值 0.5，单位 d，副标 半日往返）；
   - 3 张卡片并列：`5 km` | `0.5 d` | `0.5 h`，视觉韵律极度协调，单行完全容纳（占用仅约 45px，余量超 40px），0 处换行；
   - 实测截图保存至：`C:\Users\lylyu\.gemini\antigravity\brain\f10cae1d-876c-4402-a407-84287f540050\mountain_detail_duration_fixed.png`；
2. **构建验证**：
   - `npm run build`：0 错误，0 警告，静态资源成功编译并同步至 Android assets；
   - `git diff --check`：0 空格与换行告警；
   - `git grep -n "官方" src/`：0 处命中，合规红线稳固。
3. **反馈闭环**：
   - 已通过 CLI `npx agent-feedback update-status --id 1794280517773 --status completed` 将处理状态与修复说明写入队列。
