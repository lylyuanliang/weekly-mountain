# 主题：每周一山升级 @lylyuanliang/agent-feedback 依赖至 1.5.1

- 当前状态：已完成 (completed)
- 涉及阶段：
  1. 依赖版本升级：
     - 将 `package.json` 中的 `@lylyuanliang/agent-feedback-*` 系列 4 个依赖升级为 `^1.5.1`：
       - `@lylyuanliang/agent-feedback-client`: `^1.5.1`
       - `@lylyuanliang/agent-feedback-core`: `^1.5.1`
       - `@lylyuanliang/agent-feedback-sentinel`: `^1.5.1`
       - `@lylyuanliang/agent-feedback-vite-plugin`: `^1.5.1`
     - 执行 `npm install` 成功更新 `package-lock.json` 与 `node_modules`，`npm list` 验证 4 个包均为 `1.5.1`；
  2. 验证与回归：
     - `tests/test_resource_pack_service.js`（11 项全绿）；
     - `tests/test_store_multi_region.js`（7 项全绿）；
     - `tests/test_weather_and_gallery_resilience.js`（5 项全绿）；
     - `python tests/test_region_datasets.py`（5 项全绿）；
     - `python tests/test_region_pack_builder.py`（5 项全绿）；
     - `npm run build`：生产环境打包成功，Android/Web 资产同步校验 100% 正常；
     - 确认无任何侵入式打补丁代码，代码库纯净标准接入。
- 恢复入口：
  - 配置文件：`package.json` 与 `package-lock.json`
  - 交接文档：`docs/handoffs/upgrade-agent-feedback-to-1-5-1.md`
