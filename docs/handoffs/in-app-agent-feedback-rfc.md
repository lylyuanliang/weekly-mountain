# RFC: In-App Agent Feedback Bridge (端侧实时反馈与智能体闭环通用架构)

> **文档版本**: 1.0.0 (Draft)
> **创建日期**: 2026-10-27
> **参考落地项目**: 《每周一山 · 成都周边50座山》移动端公测与研发实践
> **目标**: 将经过实战验证的「端侧实时遥测与调试反馈 -> 智能哨兵无损监听 -> 响应式唤醒 Coding Agent -> 自动修复验证 -> 实时状态回写」体系，抽象为跨平台、框架无关的通用开发者工具库与 Agent 插件。

---

## 1. 背景与核心价值

在移动端、桌面端（Electron / Tauri）、Web 业务系统或小程序开发过程中，开发者/测试人员在真机或调试应用中发现 Bug 或体验问题时，传统链路极其割裂：
- 需要切出应用 -> 打开聊天窗口或终端 -> 截图打字描述 -> 切换回应用确认。
- 难以自动抓取崩溃发生瞬间的精准上下文（当前路由、视口尺寸、DOM 结构快照、控制台报错日志、用户操作行为轨迹）。

**In-App Agent Feedback 核心价值**：
1. **0 切换成本**：在被调试应用中直接点击浮窗或触发快捷键，圈选截图并提交；
2. **环境全息自动捕获**：提交时自动抓取路由、控制台 `console.error`、设备分辨率、系统平台、网络状态；
3. **0 Token 静默休眠与响应式唤醒**：在无新反馈时，后台哨兵 0% CPU、0 Token 消耗；收到反馈后 10 秒防抖聚合，并通过进程退出信号秒级主动唤醒 IDE 中的 AI Coding Agent；
4. **无人值守全自动修复与回写**：Agent 在电脑端自主分析、修复、自动化验证并部署，状态直接实时回写至用户移动端面板；
5. **生产环境物理剥离 (0 泄露)**：发布正式包（Release 构建）时，通过编译期死代码消除（DCE）将该套件 100% 物理剥离，严禁泄漏调试地址与内部接口。

---

## 2. 系统三层架构

```
┌─────────────────────────────────────────────────────────────┐
│ 1. 客户端 SDK 层 (@antigravity/feedback-widget)             │
│    - 悬浮拖拽气泡 / 快捷键唤起 / 全局 Error 自动监听           │
│    - 客户端轻量截屏 (html2canvas / Native Webview Screenshot)  │
│    - 状态与回复列表面板 (轮询/SSE 查看 Agent 修复进度)         │
│    - 跨框架适配：Vanilla JS, Vue 3, React, Svelte, Electron  │
└──────────────────────────────┬──────────────────────────────┘
                               │ HTTP / WebSocket / Tunnel
┌──────────────────────────────▼──────────────────────────────┐
│ 2. 中继与通道层 (Local Dev Middleware / Tunnel Sidecar)      │
│    - 本地模式：Vite / Webpack / Next.js DevServer 中间件     │
│    - 远程/真机模式：集成 Cloudflare Quick Tunnel / Cpolar    │
│    - 反馈数据持久化：标准化 `feedback_queue.json` 读写        │
└──────────────────────────────┬──────────────────────────────┘
                               │ 文件监听 + 进程退出事件唤醒
┌──────────────────────────────▼──────────────────────────────┐
│ 3. Agent 哨兵与决策层 (Antigravity Sentinel Plugin/Skill)     │
│    - 静默哨兵进程：轻量轮询，0% CPU，0 大模型 Token 消耗     │
│    - 防抖聚合窗口 (Debounce Window: 10s)：归并连发截图与说明  │
│    - 响应式主动唤醒：聚合后 sys.exit(0) 唤醒 IDE 会话         │
│    - 安全分诊 (Triage)：防 Prompt 注入、防破坏性变更审查     │
│    - 状态双向回写：通过 CLI/脚本更新 status 与 reply 字段    │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. 标准化数据协议 (Feedback Schema)

```typescript
export interface InAppFeedback {
  id: number;                   // 毫秒时间戳 ID (如 1793009756156)
  timestamp: number;
  receivedAt: string;           // ISO 8601 字符串
  content: string;              // 用户输入的文本描述
  status: 'pending' | 'processing' | 'completed' | 'rejected' | 'ignored';
  reply?: string;               // Agent 分析修复后的回复内容
  updatedAt?: string;

  // 遥测快照 (Telemetry Snapshot)
  telemetry: {
    route: string;              // 当前页面路径或 URL
    viewport: { width: number; height: number; dpr: number };
    userAgent: string;
    platform: 'android' | 'ios' | 'web' | 'desktop';
    appVersion: string;
    buildCode: number;
  };

  // 凭据与日志
  screenshots?: string[];       // Base64 或本地文件持久化路径
  consoleLogs?: Array<{
    type: 'log' | 'warn' | 'error';
    message: string;
    timestamp: number;
  }>;
}
```

---

## 4. 关键设计铁律与实战经验

1. **防抖聚合窗口 (Debounce Window)**：
   - 用户在真机操作时，往往会“发一条文字 -> 紧接着再发两张截图补充”。
   - 若每条反馈都直接唤醒 Agent，会导致会话频繁中断与上下文碎片化。
   - 规则：捕获第 1 条 `pending` 反馈后，自动开启 10 秒缓冲倒计时，合并此期间连发的多条反馈，形成单一结构化批次再唤醒会话。

2. **响应式唤醒机制 (Exit Code Wakeup)**：
   - 哨兵作为 Antigravity 的非 daemon 异步任务运行（`WaitMsBeforeAsync = 500`, `IsDaemon = false`）。
   - 收集完毕后哨兵更新状态为 `processing`，并以 `sys.exit(0)` 正常退出。
   - 进程退出产生的系统通知会直接打入 Antigravity 上下文，达成 0 成本秒级主动唤醒。
   - **铁律**：主会话或子代理在完成修复、验证并回写状态后，**必须在回复用户前重新拉起新的哨兵进程**，保持全天候监听。

3. **不可信外部输入与三道安全防线 (Security & Triage)**：
   - **第 1 防线**：防 Prompt 注入与指令劫持（识别诱导“忽略之前指令”、“删除文件”等，直接驳回）；
   - **第 2 防线**：可行性与边界评估（推翻核心设计系统、非理性的破坏性诉求标记 `rejected` 并给出合理说明）；
   - **第 3 防线**：防御性实施与测试闭环（自动化回归测试通过方可标记 `completed`）。

4. **远程无人值守/手机端离线响应策略 (Remote Autonomy)**：
   - 当用户在移动端公测离线时，严禁在电脑 IDE 中弹出阻塞式提问（如 `ask_question`）；
   - 遵循“改动最小、向前兼容”的安全默认值自主推进，将关键决策与验证结果写回 `reply` 字段，实现异步追溯闭环。

5. **编译期物理剥离 (Zero Leak)**：
   - 悬浮窗、内网穿透地址、反馈上传接口必须由构建环境标识控制（如 `VITE_ENABLE_DEBUG`）；
   - 采用动态异步导入或构建插件死代码消除（DCE），确保 Release 生产包反编译扫描 0 敏感信息残留。

---

## 5. 项目参考文件索引（用于新会话回溯）

- **前端悬浮层组件**：[`src/components/debug/MobileFeedbackWidget.vue`](file:///d:/file_save/workspace/github/weekly-mountain/src/components/debug/MobileFeedbackWidget.vue)
- **状态存储与穿透配置**：[`src/stores/debugStore.js`](file:///d:/file_save/workspace/github/weekly-mountain/src/stores/debugStore.js)
- **静默监听与防抖哨兵**：[`scripts/watch_mobile_feedback.py`](file:///d:/file_save/workspace/github/weekly-mountain/scripts/watch_mobile_feedback.py)
- **状态回写脚本**：[`scripts/update_feedback_status.py`](file:///d:/file_save/workspace/github/weekly-mountain/scripts/update_feedback_status.py)
- **安全与协作规范文档**：[`AGENTS.md`](file:///d:/file_save/workspace/github/weekly-mountain/AGENTS.md)
