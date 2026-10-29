# 主题：sentinel-auto-lifecycle-and-clean-rules (哨兵生命周期自动托管与提示词解绑)

- 当前状态：已完成 (Completed)
- 最后更新时间：2026-10-29 17:50
- 恢复入口：`docs/handoffs/sentinel-auto-lifecycle-and-clean-rules.md`

---

## 1. 目标与背景
1. 在 `@lylyuanliang/agent-feedback` 开源库中实现哨兵全自动生命周期管理：
   - `packages/sentinel`: 改造 `once` 语义，支持 `--daemon` / `--no-once` 持续常驻监听；适配器矩阵支持 Antigravity、Webhook、MCP 及多轮守护；
   - `packages/vite-plugin`: 原生支持 `sentinel` 选项（`autoStart: true`），在 Vite `npm run dev` 启动时自动运行，随 DevServer 关闭（`httpServer.on('close')` / `SIGINT` / `SIGTERM`）自动清理退出，彻底实现同生共死与 0 心智负担；
   - 编写完整的自动化单元测试与新项目接入场景模拟测试（覆盖模拟全新项目接入 `vite-plugin` 后的自动启动、多轮持续常驻守护、关闭清理）。
2. 在《每周一山》宿主项目中解除人工提示词绑定：
   - 清除 `GEMINI.md` 与 `AGENTS.md` 中第 1.3 节的“处理完毕后必须重新启动哨兵”软约束提示词；
   - 升级引入改造后的 `agent-feedback` 闭环，进行真实新项目接入模式的真机回归测试。

---

## 2. 落地实施记录

### 2.1 `agent-feedback` 开源库改造
- **多智能体接入生态指南落地**：
  - 新增 [`docs/multi-agent-integration-guide.md`](file:///d:/file_save/workspace/github/agent-feedback/docs/multi-agent-integration-guide.md)，系统剖析 Antigravity、Claude Code、Codex、DSH、ZCode、Cursor 等全智能体的生命周期机制与命令驱动方案；
  - 在 [`README.md`](file:///d:/file_save/workspace/github/agent-feedback/README.md) 中添加专项文档索引。
- **`packages/sentinel` 改造**：
  - 在 `WatcherOptions` 中明确 `once` 语义，CLI 支持 `--daemon` / `--no-once` 持续常驻监听；
  - 增加常驻守护模式测试用例，18/18 单元测试全部通过。
- **`packages/vite-plugin` 改造**：
  - 依赖 `@lylyuanliang/agent-feedback-sentinel`；
  - 导出 `SentinelPluginOptions`，在 `configureServer` 中实现 DevServer 伴生自动启动与退出清理；
  - 在 `tests/plugin.test.ts` 中实现全新的新项目接入场景模拟测试套件，23/23 单元测试全部通过。
- **`packages/client` 健壮性优化**：
  - 为历史和状态轮询定时器添加 `unref()`，彻底消除 Node.js 虚拟 DOM 测试环境下的悬挂。
- **全量回归验证**：
  - 运行 `pnpm test`：5 个包全部绿灯，83/83 项测试全部通过（0 fail, 0 hang）；
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

## 4. 自测验证结果
- `agent-feedback` 全量 Monorepo 测试：83 项测试全部通过 (0 failed, 0 hanging)；
- `weekly-mountain` DevServer 启动测试：哨兵伴随 Vite 自动启动，持续守护，无需人工命令；
- 端到端反馈提交流程：工单自动流转 `pending` -> `processing` -> `completed`，全生命周期无断点；
- Antigravity 原生主动唤醒验证：接入 `agentapi send-message $ANTIGRAVITY_CONVERSATION_ID`，实测在 DevServer 常驻守护前提下，端侧反馈防抖后毫秒级主动唤醒会话；
- 用户反馈修复（工单 ID: 1793267885431）：山峰卡片「已登」升级为暗黑深色基底「已登顶」认证勋章；
- 移动端 App 打包验证：成功打出最新时间戳测试包 `weekly-mountain-v0.2.0.202610291809-debug.apk` (28.08 MB)，HTTP 下载服务与在线更新验证通过。
