# MCP 理论课（D1 无实操版）

> 今天不写代码，只读懂下面的代码和文字。读完能回答文末 4 个问题就算过关。

---

## 一、先建立心智模型：三种「让 LLM 用工具」的方式

### 1. Function Calling（函数调用）—— 焊死在应用里

```python
# tools 定义写死在你自己的应用代码中
tools = [{
    "name": "get_weather",
    "description": "查询某城市天气",
    "parameters": {
        "type": "object",
        "properties": {"city": {"type": "string"}},
        "required": ["city"],
    },
}]

def get_weather(city: str) -> str:   # ← 函数本体也在这个文件里
    return f"{city}: 晴, 25°C"

# 模型说「我要调 get_weather」→ 你的代码自己执行 get_weather()
```

**问题**：工具和 Agent 焊死在一起。换个客户、换套系统，要改你的代码。

---

### 2. MCP（Model Context Protocol）—— 工具做成独立服务器

```
┌─────────────┐  JSON-RPC/stdio   ┌──────────────────┐
│  Claude/    │ ◄───────────────► │  MCP Server       │
│  你的Agent   │   list_tools /    │  (独立进程/独立仓库) │
│             │   call_tool       │  暴露 tickets 等工具│
└─────────────┘                   └──────────────────┘
```

**MCP = 给 LLM 应用设计的「USB-C 接口」标准。**
- Server 想接谁就接谁，应用想用哪个 Server 就挂哪个，双方不互相改代码。

---

### 3. 静态硬编码 —— 最原始

```python
if user_input == "查工单":
    result = my_db.query(...)   # 写死的 if-else，模型根本没有「选工具」的自由
```

FDE 场景几乎不用这种，知道区别即可。

---

## 二、一张表看懂区别（面试必背）

| 维度 | Function Calling | MCP |
|------|------------------|-----|
| 工具放哪 | 焊在 Agent 代码里 | 独立 Server 进程/仓库 |
| 换个 LLM 应用 | 要复制一份工具代码 | 改一行配置即可挂上 |
| 多个客户复用 | 每个客户 fork 一份 | 同一个 Server 分发给多家 |
| FDE 交付物 | 交 Agent 源码（耦合） | 交 Server（可插拔）★ |
| 协议 | 各家厂商 API 私有格式 | 开放标准（JSON-RPC） |

**一句话**：FC 是「把工具焊进汽车」，MCP 是「给汽车装一个标准 USB 口，U 盘（工具）随插随用」。

---

## 三、MCP 三方架构（必考）

```
  Host（宿主，如 Claude Code / 你的Agent App）
        │  管理连接、用户权限
        ▼
  Client（客户端，Host 内部每条连接一个）
        │  JSON-RPC 会话
        ▼
  Server（工具真正所在，如我们写的 ticket_server.py）
```

- **Host**：用户直接面对的程序（Claude Desktop、Claude Code、Cursor…）
- **Client**：Host 和某一个 Server 之间的一对一连接
- **Server**：声明「我有哪些 tool / resource / prompt」，被调用时执行逻辑

---

## 四、一个 MCP Server 长什么样（读代码即可）

```python
from mcp.server.mcpserver import MCPServer   # 注意：新版叫 MCPServer，旧教程写 FastMCP

server = MCPServer("ticket-server")           # ① 起个名字

@server.tool()                                 # ② 用装饰器登记工具
def list_tickets(status: str = "open") -> str:
    """列出工单。status: open/resolved。返回JSON字符串。"""
    # ③ 真正的业务逻辑：查内存字典 / 查数据库都行
    return json.dumps([...], ensure_ascii=False)

if __name__ == "__main__":
    server.run(transport="stdio")              # ④ 用 stdio 管道和宿主通信
```

**逐行翻译成人话：**
1. `MCPServer(...)`：我是一个 MCP 服务器，名叫 ticket-server。
2. `@server.tool()`：把下面这个函数注册成模型可调用的「工具」。函数名+docstring+type hint 会一起被发给模型，模型靠这些决定什么时候调、传什么参数。
3. 函数体：普通 Python，和 LLM 无关——**这才是 FDE 写的「真活」**（对接客户数据库、权限、审计日志等都在这层）。
4. `run(transport="stdio")`：通过标准输入输出和宿主对话（还有 sse、streamable-http 等远程传输方式，进阶再学）。

---

## 五、调用时序（脑内过一遍）

```
1. Host 启动，拉起 ticket_server.py
2. Server 告诉 Host：我有 list_tickets / get_ticket / create_ticket / resolve_ticket
3. 用户对 LLM 说：「帮我看看未关闭的工单」
4. LLM 决定调 list_tickets(status="open")
5. Host → Client → Server：JSON-RPC call_tool
6. Server 执行 Python 函数，把字符串结果返回
7. LLM 拿到结果，组织自然语言回复用户
```

**关键点**：第 4 步是模型在「决策」，第 6 步是你的代码在「干活」。FDE 调试时要分清：是模型选错工具（改 prompt/描述），还是工具执行报错（改 Server 代码）——这是两类完全不同的 bug。

---

## 六、FDE 视角：为什么客户非要 MCP

1. **不锁定**：今天接 Claude，明天接内部自研模型，Server 不用重写。
2. **权限边界清晰**：Server 是独立进程，可以在它这一层做客户要求的鉴权/审计/脱敏，而不是散落在各处 Agent 代码里。
3. **交付即插件**：你给客户交付的是一个「标准插头」，他们现有的 MCP 宿主（Claude Code、内部平台）直接挂上就能用。
4. **写操作必须加护栏**：create_ticket / resolve_ticket 这类写操作，在真实交付里要加 human-in-the-loop 确认，不能让模型静默改客户数据。面试提到「写操作」一定要主动说这一句。

---

## 七、和 Function Calling 的对比题（面试原题级）

> 「你写过 Function Calling，为什么还要 MCP？」

参考答案骨架：
- FC 能用，但工具定义和执行逻辑与单一应用耦合，多客户/多宿主场景要复制粘贴。
- MCP 提供标准协议，工具侧独立演进、可被任意合规宿主挂载。
- 对 FDE 来说，交付物从「改客户的 Agent 代码」变成「交付一个可插拔 Server」，边界更干净，出问题好定位（模型决策 vs 工具执行分层）。

---

## 八、今日自测（不用写代码，口头回答）

1. Function Calling 的工具定义存在哪里？MCP 的工具定义存在哪里？
2. MCP 三方架构是哪三方，各自职责一句话。
3. `@server.tool()` 装饰的函数里，哪部分是「模型决策」，哪部分是「你的真活」？
4. 如果客户说「我们的写操作不能让 AI 自动执行」，你在 MCP 架构里怎么回应？

（答案见同目录 questions.md，先自己答再看。）
