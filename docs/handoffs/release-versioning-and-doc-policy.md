# 主题：Release 版本发布标题纯净规范与文档结构优化

- 当前状态：已完成 (completed)
- 最后更新时间：2026-11-05
- 恢复入口：`scripts/sync_version.py`

## 1. 目标与背景
用户反馈在 GitHub Releases 侧边栏与列表中，多版本 Release 标题拼接长句导致排版冗余堆砌。
要求：
- 从下一个版本开始，GitHub Release 标题统一仅保留纯净版本号（如 `v0.3.0.202611051117` 或 `v0.3.0`）；
- 详细说明与特性分类统一在正文更新日志（Changelog）中完整呈现；
- 更新版本元数据同步脚本 `scripts/sync_version.py`、项目协作规则 `AGENTS.md`、`GEMINI.md` 以及版本记录文档 `docs/releases/RELEASE-v0.3.0.md`。

## 2. 关键决策与实施内容
1. **构建脚本改造 (`scripts/sync_version.py`)**：
   - 默认生成 Release 标题逻辑调整为仅保留 `version_tag`（例如 `v0.3.0.202611051117`），不再自动在标题后拼接长描述；
   - 仍保留 `--title` 命令行参数支持，如无显式指定则严格使用纯净版本号。
2. **规约文档同步 (`AGENTS.md`, `GEMINI.md`)**：
   - 更新第 6.3 节第 5 条为「Release 标题纯净版本号原则」：明确从当前及后续版本起，Release 标题（Title）统一仅保留版本号，严禁长描述后缀，侧边栏保持极简；
   - 更新示例元数据块。
3. **版本文档调整 (`docs/releases/RELEASE-v0.3.0.md`)**：
   - 将元数据块中 `title` 修正为 `"v0.3.0"`，保持纯净；
4. **元数据文件更新 (`public/version.json`)**：
   - 将 `title` 字段更新为 `"v0.3.0.202611051117"`。

## 3. 修改文件清单
- `scripts/sync_version.py`: 改造 `final_title` 默认生成逻辑为仅保留版本号；
- `AGENTS.md`: 更新第 6.3 节发版规约第 5 条为纯净版本号原则；
- `GEMINI.md`: 同步更新第 6.3 节规约；
- `docs/releases/RELEASE-v0.3.0.md`: 更新元数据块 `title`；
- `public/version.json`: 更新 `title` 字段为纯净版本号；
- `docs/handoffs/release-versioning-and-doc-policy.md`: 本次交接记录。

## 4. 验证与自测结果
- 运行 `python scripts/sync_version.py 0.3.0.202611051117`：
  - 成功生成 `public/version.json`，验证 `title` 为 `"v0.3.0.202611051117"`；
- 运行 `git diff --check`：无语法或空白符错误；
- 检查 GitHub Actions 流水线配置：`generate_notes.cjs` 直接读取 `versionInfo.title` 作为 Release 标题，将输出纯净版本号。

## 5. 恢复与后续步骤
下次发版时直接按规约在 `docs/releases/RELEASE-vX.Y.Z.md` 中维护 `changelog`，运行 `python scripts/sync_version.py` 即可自动生成仅含版本号的标题与结构化日志。
