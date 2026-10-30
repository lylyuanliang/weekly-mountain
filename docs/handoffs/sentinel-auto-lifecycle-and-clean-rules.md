# 主题：sentinel-auto-lifecycle-and-clean-rules (哨兵生命周期自动托管与提示词解绑)

- 当前状态：已完成 (Completed)
- 最后更新时间：2026-10-29 20:14
- 恢复入口：`docs/handoffs/sentinel-auto-lifecycle-and-clean-rules.md`

---

## 1. 目标与背景
1. 在 `@lylyuanliang/agent-feedback` 开源库中实现哨兵全自动生命周期管理：
   - `packages/sentinel`: 改造 `once` 语义，支持 `--daemon` / `--no-once` 持续常驻监听；适配器矩阵支持 Antigravity、Webhook、MCP 及多轮守护；
   - `packages/vite-plugin`: 原生支持 `sentinel` 选项（`autoStart: true`），在 Vite `npm run dev` 启动时自动运行，随 DevServer 关闭（`httpServer.on('close')` / `SIGINT` / `SIGTERM`）自动清理退出，彻底实现同生共死与 0 心智负担；
   - 彻底攻克外部终端启动（用户手动 `npm run dev`）时缺少 `ANTIGRAVITY_CONVERSATION_ID` 环境变量导致的适配器降级为 `webhook` 且无法唤醒的痛点，支持基于本地数据库 `conversation_summaries.db` 的零配置工作区智能感知自动绑定；
   - 编写完整的自动化单元测试与新项目接入场景模拟测试。
2. 在《每周一山》宿主项目中解除人工提示词绑定：
   - 清除 `GEMINI.md` 与 `AGENTS.md` 中第 1.3 节的“处理完毕后必须重新启动哨兵”软约束提示词；
   - 升级引入改造后的 `agent-feedback` 闭环，进行真实新项目接入模式的真机回归测试。

---

## 2. 落地实施记录

### 2.1 外部终端无感自动感知与唤醒架构攻坚
- **问题本质分析（源于用户真机终端截图）**：
  - 截图中清晰可见：第 5 行显示 `[*] Agent Feedback 哨兵已启动 (适配器: webhook)...`，防抖聚合完毕后没有唤醒智能体；
  - 根因：智能体内部子进程拥有私有环境变量 `ANTIGRAVITY_CONVERSATION_ID`，但用户在宿主机外部独立终端（如 VS Code 终端、PowerShell、CMD）运行 `npm run dev` 时，环境变量中并不存在该字段，导致插件回退至 `webhook`，且在未配 `webhookCommand` 时仅执行了数据持久化，未触发外部通知。
- **开源库架构级升级**：
  - `packages/sentinel`:
    - 新增 `detectAntigravityConversation(cwd)`：利用 Node.js 原生内置 `node:sqlite` 引擎零依赖查询 `~/.gemini/antigravity/conversation_summaries.db`，按当前工作区根目录模糊匹配未退出的活跃会话 ID；
    - 新增 `getAgentApiExecutable()`：兼容绝对路径 `~/.gemini/antigravity/bin/agentapi.bat`（Windows）与 `agentapi`（POSIX），消除 PATH 丢失风险；
    - 当适配器未指定时，若检测到本地活跃会话，自动无感提升为 `antigravity` 适配器并绑定该会话；
    - 在 Webhook 模式下未配下游时增加友好诊断提示。
  - `packages/vite-plugin`:
    - 引入 `detectAntigravityConversation`，在 `configureServer` 中实现真正的零配置跨终端自动感知；
    - 日志输出直接带上检测到的活跃会话前缀：`[@agent-feedback/vite-plugin] 哨兵已伴随 DevServer 自动启动 (适配器: antigravity (会话: 66cdabf9...), 常驻守护)`。

### 2.2 `agent-feedback` 开源库基础改造与测试
- **多智能体接入生态指南落地**：
  - 新增 [`docs/multi-agent-integration-guide.md`](file:///d:/file_save/workspace/github/agent-feedback/docs/multi-agent-integration-guide.md)；
  - 在 [`README.md`](file:///d:/file_save/workspace/github/agent-feedback/README.md) 中添加专项文档索引。
- **全量回归验证**：
  - 运行 `pnpm test`：5 个包全部绿灯，84/84 项测试全部通过（0 fail, 0 hang）；
  - 模拟纯外部终端（`delete process.env.ANTIGRAVITY_CONVERSATION_ID`）测试：成功自动推断解析出 `66cdabf9-ca17-464c-957c-28b829d5bc91`，适配器成功自适应升级为 `antigravity`；
  - 运行 `pnpm build`：TypeScript 编译与 Rollup/Vite 构建全量通过。

### 2.2 `weekly-mountain` 宿主项目改造
- **解除人工提示词绑定**：
  - 修改 [`GEMINI.md`](file:///d:/file_save/workspace/github/weekly-mountain/GEMINI.md) 与 [`AGENTS.md`](file:///d:/file_save/workspace/github/weekly-mountain/AGENTS.md)；
  - 彻底删除第 1.3 节“处理完毕后必须重新启动哨兵”；
  - 明确哨兵由 Vite 插件伴生自动托管，智能体严禁依赖提示词手动干预。
- **接入最新 Vite 插件托管配置**：
  - 更新 [`vite.config.js`](file:///d:/file_save/workspace/github/weekly-mountain/vite.config.js)，配置 `sentinel: { autoStart: true, debounceSeconds: 10 }`；
  - 安装最新构建的 `.tgz` 包并启动 DevServer，控制台清晰输出：
    `[@agent-feedback/vite-plugin] 哨兵已伴随 DevServer 自动启动 (适配器: webhook, 常驻守护)`；
  - 发送真实时间戳工单测试，验证哨兵自动捕获、10 秒防抖聚合、自动将状态转为 `processing`、并通过 CLI `npx agent-feedback update-status` 顺利闭环为 `completed`。

---

## 3. 修改文件清单

### `agent-feedback` 仓库
- `docs/multi-agent-integration-guide.md`
- `README.md`
- `packages/client/src/index.ts`
- `packages/sentinel/src/index.ts`
- `packages/sentinel/bin/cli.js`
- `packages/sentinel/tests/sentinel.test.ts`
- `packages/vite-plugin/package.json`
- `packages/vite-plugin/src/index.ts`
- `packages/vite-plugin/tests/plugin.test.ts`

### `weekly-mountain` 仓库
- `GEMINI.md`
- `AGENTS.md`
- `vite.config.js`
- `docs/handoffs/sentinel-auto-lifecycle-and-clean-rules.md`

---

## 4. 自测验证与发版清洗记录
- **agent-feedback 状态**：
  - 去除文档中所有“工业级”字样，标题修正为“完整参考项目”，手势优化为“原生触控手势工程”；
  - 提交 f8f4045 并同步更新 GitHub 远端 main 分支与 v1.1.0 标签；
  - 84 项全单测 100% 绿灯，发布安装包（Core / Client / Sentinel / Vite-Plugin）纯净就绪；
- **weekly-mountain 历史非规范 Tag 清洗**：
  - 本地与 GitHub 远端彻底清理废弃的历史非规范标签（v0.0.1.004、v0.0.1.005、v1.2.3、v1.2.4、v2.0.0、v2.0.7）；
  - 目前规范保留用户正式发布的 2 个历史与里程碑标签：v0.0.1.005 与 v0.2.0，v0.0.1.005 时间戳已对齐真实历史（10月27日），GitHub Releases 完美按 v0.2.0 (Latest 顶部) -> v0.0.1.005 (历史 底部) 排序；
- **README.md 样式与 GFM 语法修复**：
  - 修复 License 与 Platform 徽标（Shields.io 格式规范化，去除 .svg 后缀与特殊编码，升级 Version 为 v0.2.0）；
  - 修复波浪号 GFM 删除线误解析（L1~L2 与 L3~L5 中间文本被误当成 ~~del~~ 渲染删除线，替换为全角标准中文波浪号 L1～L2、L3～L5）；
- **功能端到端全链路验证**：
  - DevServer 伴生哨兵常驻自动托管；
  - 移动端打卡、相册、OTA 在线更新全链路通过。
