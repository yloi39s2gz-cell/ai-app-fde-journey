# stage0 启动包（2026-10-03）

> 这一份不是新知识，是**把已经写出来的东西真正跑通、真正搞懂**。
> 时间预算：今晚 60~90 分钟。做完你会有三个之前没有的东西：
> ① 一个能自己跑通的 MCP 调试客户端 ② 一份填完的自测答案 ③ 一个干净的 git 提交。

## 0. 事实核查（先看这一行）

我把你仓库里的东西全部检查了一遍，结论如下：

| 检查项 | 结果 |
| --- | --- |
| `mcp` SDK 版本 | **2.2.0**（v2 新 API，`FastMCP` 已改名 `MCPServer`） |
| `server.py` 能不能 import | ✅ 可以（`from mcp.server.mcpserver import MCPServer`） |
| `server.py` 能不能被客户端拉起 | ✅ 可以，4 个 tool 全部正常响应 |
| `@mcp.tool()` 装饰器 | ✅ 在 v2 里依然可用 |
| README 里写的 tool 数量 | ⚠️ 写了 3 个，**代码里有 4 个**（多了 `resolve_ticket`） |
| `notes.md` / `questions.md` | ⚠️ 全空，一个字没写 |
| git | 之前 0 commit，现在已有基线提交 |

**你这个 stage 的真实状态：代码是好的，文档是空的，验证是缺的。**
所以今晚不写新功能，先把"验证"这块补上 —— 这也是 FDE 和"会写 demo 的人"的区别：
交付物必须**自己能被验证**，不能等客户来告诉你能不能跑。

## 1. 今天的任务（按顺序做，每步都有验收）

### 任务 1：读代码，回答 3 个问题（10 分钟，不许看 AI）

打开 [server.py](learning/fde/stage0/server.py)，只看，不写。然后回答：

1. `list_tickets(status=None)` 和不传参数时，返回值有什么不同？为什么？
2. `create_ticket` 用了 `global _NEXT_ID`。**能不能不用 global？** 想想替代写法。
   （追问：如果 priority 传了 "urgent"，这个函数会不会报错？该在哪里拦住？）
3. `get_ticket(999)` 返回 `{"error": ...}` 而不是抛异常。为什么工具函数更适合返回值而不是抛异常？
   （提示：想想模型看到的是 JSON 还是 Python traceback）

> 把答案写在 `notes.md` 的「1. 架构题」下面。写你的话，不要抄定义。

### 任务 2：手写一个 MCP 调试客户端（40 分钟，核心任务）

**为什么做这个**：FDE 驻场第一天最尴尬的事，是工具写完了却只能等客户开 Claude Desktop 才发现跑不起来。
你需要能**独立验证自己的交付物**。MCP Server 是 stdio 子进程，能拉起它的只有 MCP Client ——
所以你要自己写一个。

打开 [client_demo.py](learning/fde/stage0/client_demo.py)，里面是骨架 + 5 个 TODO。
**先把 5 个 TODO 填完，再看 `client_demo_reference.py` 对答案。**

验收标准（全部满足才算过）：

- [ ] `python client_demo.py` 能打印出 4 个 tool 的名字
- [ ] `list_tickets()` 不传参时拿到 3 条（101/102/103）
- [ ] `list_tickets(status="open")` 拿到 1 条，且**你能说出它的返回形状和上一次有什么不同**
- [ ] 能新建一个工单并拿到它的 id（应该从 104 开始）
- [ ] 查询不存在的 id（999）时，程序**不崩**，而是打印出 error 字段
- [ ] 你能说出：为什么这时 `res.is_error` 还是 False

> 第 2、3、6 条是故意分开写的。**同一个工具返回不同形状**这件事，
> 是这一课最值钱的发现（见下方「坑 4」）。

### 任务 3：填完 `notes.md` 和 `questions.md`（20 分钟）

- [questions.md](learning/fde/stage0/questions.md) 有 6 道自测题，**先自己答，再点开参考答案**。
  答不上来的题，把"我卡在哪"也写下来 —— 那才是你的真实进度。
- [notes.md](learning/fde/stage0/notes.md) 最后一题（FDE 场景题：客户 12 个内部系统怎么交付）
  是本阶段**最像面试的一题**，至少写 5 行。

### 任务 4：提交（5 分钟）

```powershell
cd C:\Users\admin\Desktop\学习
git add -A
git commit -m "feat(fde/stage0): 补 MCP 调试客户端与自测答案"
```

## 2. 四个坑，我替你踩过了（省你两小时）

1. **`Start-Process` 在这台机器上报 `已添加项。字典中的关键字:"NO_PROXY"`**。
   是 PowerShell 5.1 的已知问题（环境变量里有大小写重名的 NO_PROXY/no_proxy）。
   结论：**别用 Start-Process 去拉 Server**，直接让客户端用 `stdio_client` 拉。
2. **stdio Server 不能"手动运行看输出"**。直接 `python server.py` 会看起来像卡住 ——
   它在等 stdin 上的 JSON-RPC 消息。这不是 bug，是 stdio 传输的本性。
3. **`from mcp.server.fastmcp import FastMCP` 在 mcp 2.x 会报错**，
   错误信息里明写了 "FastMCP was renamed to MCPServer"。
   你如果从旧教程抄代码，就会撞上这个。**版本迁移是驻场日常的一部分**，记下来。
4. **同一个 MCP 工具，返回值形状会变**（我写参考实现时才发现的）：
   `list_tickets()` 给回 **3 个** text block（一张工单一个 block），
   而 `list_tickets(status="open")` 只给回 **1 个** block（内容是单个 dict）。
   所以如果你写 `res.content[0].text`，第二条会"看起来正常"、第一条会**静默丢数据**。
   正确姿势是遍历 `res.content` 收齐再判断 `len(blobs)`。
   第二个观察：`create_ticket(priority="urgent")` 不会被拦，照样写进库 ——
   MCP 只按类型注解生成 schema，**取值合法性得你自己校验**。

   > 这两个观察都不是查文档得来的，是**自己写客户端时撞出来的**。
   > 这就是我让你手写 `client_demo.py` 而不是给你一个能跑的文件的原因。

## 3. 做完这一份之后，下一站是什么

见 [30天启动表](learning/fde/stage0/../../START_HERE.md)（我同步写的路线总表）。
一句话：**MCP 从"能跑"升级到"能交付"** —— 加 human-in-the-loop 确认、审计日志、
接进你自己的 Agent（stage4 那套），然后写一个 30 秒能讲完的交付故事。
