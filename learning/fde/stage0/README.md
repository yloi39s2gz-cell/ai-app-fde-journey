# FDE Stage 0：MCP — 给 Agent 插上"客户系统"的插座

> 对应 FDE 计划 Phase 2 W9。前置：已完成 AI应用开发 stage4（Agent 工具调用）。

## 你已会的 vs 今天要学的

| | stage4 的工具调用 | MCP |
|---|---|---|
| 工具定义在哪 | 写死在 `tools.py` | 独立进程的 Server 里 |
| 加一个工具 | 改 Agent 代码、重跑测试 | 写/装一个 Server，改配置 |
| 谁能用 | 只有你这个 Agent | Claude Desktop、Claude Code、任何 MCP 客户端 |
| FDE 交付物 | 定制代码（难复用） | **MCP Server（可插拔、可交接）** |

## 为什么 FDE JD 点名 MCP

驻场场景：客户说"让 AI 查我们的工单系统"。

- 没有 MCP：读客户 API 文档 → 改你的 Agent → 部署 → 客户换接口再来一遍
- 有 MCP：写一个 `ticket-mcp-server`，客户任何 MCP 客户端（Claude/Cursor/内部 Agent）都能接，**离开后客户自己还能用**（JD: "playbooks the client owns after you leave"）

## 核心概念（4 个）

1. **MCP Server**：一个独立程序，通过 stdio 或 HTTP 暴露 tools/resources/prompts
2. **Tool**：和 function calling 类似——name + JSON schema + handler，但跑在 Server 进程
3. **Client**：Claude Desktop / Claude Code / 你的 Agent，负责连接 Server 并把工具交给模型
4. **Transport**：本地用 `stdio`（子进程），远程用 `streamable HTTP`

## 本 stage 任务

```
stage0/
├── README.md          ← 本文
├── server.py          ← 你手写的 MCP Server（模拟客户工单系统）
├── notes.md           ← 实验后填写
└── questions.md       ← 自测题
```

### 任务 A：读懂并跑通 `server.py`

模拟一个"客户工单系统"，暴露 3 个 tool：
- `list_tickets(status)` — 查工单列表
- `get_ticket(id)` — 查详情
- `create_ticket(title, priority)` — 建工单（会改内存状态）

### 任务 B：用 MCP Inspector 可视化调用（不写一行客户端代码）

```bash
# 在 stage0 目录（已装 mcp>=2，FastMCP 已更名为 MCPServer）
uvx @modelcontextprotocol/inspector python server.py
```

浏览器会打开 Inspector，你能在界面上：
1. 看到 3 个 tools 的 schema
2. 手动填参数调用
3. 观察返回 JSON

**这是 FDE 演示神技**：驻场时给客户 CT0 5 分钟看到"你们的工单系统已经能被 AI 调用了"。

### 任务 C：接到 Claude Code（真实客户端）

在项目根或 `~/.claude.json` 的 mcpServers 配置：

```json
{
  "mcpServers": {
    "ticket-system": {
      "command": "uv",
      "args": ["run", "--directory", "FDE工程师/stage0", "server.py"]
    }
  }
}
```

或项目内 `.mcp.json`：

```json
{
  "mcpServers": {
    "ticket-system": {
      "command": "python",
      "args": ["FDE工程师/stage0/server.py"]
    }
  }
}
```

重启 Claude Code 后问：
- "帮我查所有 open 状态的工单"
- "新建一个标题为「打印机坏了」优先级 high 的工单"
- "再查一遍工单列表，确认建好了"

**验收**：模型通过 MCP 调了你的 Server，内存状态变化能被下一次查询观察到。

### 任务 D（进阶）：对比 function calling

用你 stage4 的写法，在本地写一个只有 `list_tickets` 的 function-calling Agent，对比：
- 加第 4 个 tool，两种方式各要改几处代码？
- 给"另一个团队的 Agent"复用，哪种能直接给？

## 过关标准（Gate）

- [ ] 能画出 MCP 三方架构（Client / Server / Model）
- [ ] Inspector 里成功调用 3 个 tool
- [ ] Claude Code 里用自然语言完成了建单→查询闭环
- [ ] 能向面试官讲清："MCP 和 function calling 差在哪？为什么 FDE 交付 MCP Server 而不是改客户代码？"

## 常见坑

1. **Server 不是 Web 服务**——stdio 模式是子进程，别去开端口
2. **Tool description 决定模型会不会用**——写清楚什么时候用、参数单位是什么（你 stage4 的 search_handbook 注释经验直接迁移）
3. **有副作用的 tool 要谨慎**——`create_ticket` 这类写操作，生产上要考虑确认机制（对应 FDE 的 human-in-the-loop）
4. **Windows 路径**——配置里用正斜杠或 `pathlib`，避免转义问题
