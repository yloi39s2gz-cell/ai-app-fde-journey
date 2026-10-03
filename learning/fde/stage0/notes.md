# Stage 0 实验笔记（做完任务 A–D 再填）

## 1. 架构题

用你自己的话画/写清楚三方关系：Model、MCP Client、MCP Server。
今天哪个进程是 Server？谁拉起的它？

**你的回答：**


## 2. Inspector 观察（任务 B）

- `list_tickets` 不带 status 和带 `status=open`，返回有何不同？
- `create_ticket` 的 inputSchema 里，哪些字段是 required？`priority` 有默认值吗（看 schema 怎么写的）？

**你的回答：**


## 3. Claude Code 闭环（任务 C）

贴出你用自然语言让模型做的完整操作序列，以及模型实际调用的 tool 名和参数（从对话/日志里抄）。

**你的回答：**


## 4. 对比 function calling（任务 D）

| | function calling（stage4） | MCP（stage0） |
|---|---|---|
| 加一个 tool 要改哪里 | | |
| 给另一个团队复用怎么做 | | |
| 状态存在哪 | | |

**你的回答：**


## 5. FDE 场景题（面试向）

客户说："我们有 12 个内部系统，想让 AI 都能查。"
- 用 MCP 你会怎么交付？交付物清单是什么？
- 你离开后客户怎么继续用？

**你的回答：**
