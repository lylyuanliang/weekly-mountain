# 交接文档：DSH 智能体联调与多 Agent 维度文档重构 (DSH Agent Testing & Docs Refactor)

## 任务背景与目标
- **背景**：针对真机工单外部调度问题，在本地开展 DeepSeek DSH 命令行智能体联测与状态流转分析。发现 DSH 真实命令行仅支持 `dsh headless "<prompt>"` 子进程拉起独立修复会话，且原配置在 Windows 环境变量展开与错误直出方面存在优化空间。同时对开源仓库 `agent-feedback` 文档体系进行多 Agent 维度重构。
- **目标**：
  1. 在 `weekly-mountain` 的 `vite.config.js` 中配置 DSH 实机联测命令（使用 `call` 规避引号剥离，采用 `%FEEDBACK_IDS%` 宏占位符）；
  2. 修复 `agent-feedback` 内核调度异常直出报错信息、支持跨平台命令宏替换与 ESM 动态加载兼容；
  3. 将 `agent-feedback` 文档全面重构为以 Agent 为维度的独立专属接入教程体系，明确标注实测状态（Antigravity 🟢 已全流程验证，DSH 🟡 实机联测进行中，其余 ⏳ 待实测）；
  4. 分批次完成原子提交并推送到 GitHub 远端。

## 当前执行状态
- **状态**：已完成 (Completed)
- **已修改与同步文件**：
  - `weekly-mountain/vite.config.js`：配置适配当前版本的 DSH headless 联调命令；
  - `weekly-mountain/node_modules/@lylyuanliang/agent-feedback-sentinel/dist/index.js`：同步最新的内核构建产物；
  - `agent-feedback`：完成 3 个原子批次提交并成功推送至 GitHub `main` 分支。

## 恢复与后续测试入口
- 本地启动测试：在 `weekly-mountain` 运行 `npm run dev`；
- 手机端提交工单后，哨兵防抖 10 秒后将调用 `dsh headless` 执行自动化排查与修复；
- 手机端历史面板可实时查看处理状态或真实报错日志。
