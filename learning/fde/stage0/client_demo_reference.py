"""MCP 调试客户端（参考实现 —— 先自己写完再看）。

用到的 v2 API（三个）：
    mcp.StdioServerParameters        —— 描述"怎么启动这个 server"
    mcp.client.stdio.stdio_client    —— 把 server.py 当子进程拉起来，接上 stdin/stdout
    mcp.ClientSession                —— 协议会话：initialize / list_tools / call_tool

★ 下面第 2 条是我在写这份参考实现时才发现的，专门去协议层做了实验才搞明白 ——
  这正是"你自己写一遍客户端"的价值：不写客户端，你永远不会知道自己的 server
  返回给外面到底是什么形状。

三个必须知道的坑：

1) 字段名是 snake_case：CallToolResult 上只有 is_error / structured_content，
   没有 isError。pydantic v2 访问不存在的字段会直接抛 AttributeError。

2) **同一个工具，返回值形状会变**（这是最容易踩的一个）：
     list_tickets()                   -> 3 个 text block，每个是一张工单
     list_tickets(status="open")      -> 1 个 text block，内容是一张工单 dict
   也就是说 MCP 把"列表"摊成了多个 block，而"单项"还是一个 block。
   结果就是 len(blobs) 时 1 时 3，你不能假设它永远是个 list。
   所以 payload() 要同时处理这两种情况（见下面函数）。

3) 业务错误不是协议错误：
   get_ticket(999) 返回 {"error": ...}，但 is_error 仍然是 False。
   这是**有意设计** —— 让模型读到错误、自己决定下一步，
   而不是把异常抛到协议层让整个调用失败。

顺便记录一个观察：这个 server 不校验 priority 的取值，
create_ticket(priority="urgent") 照样写进库了。
MCP 只负责把参数传进来（由类型注解生成 schema），
**"这个值合不合法"必须由你自己在函数里校验**。
"""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


def payload(res):
    """把 CallToolResult 收成一个 Python 对象。

    返回 dict（单条）或 list[dict]（多条），调用方按 len(blobs) 判断。
    """
    blobs = [json.loads(c.text) for c in res.content if c.type == "text"]
    return blobs[0] if len(blobs) == 1 else blobs


async def main() -> None:
    # 用 sys.executable：客户机器上的 python 不一定是你这台，
    # 用当前解释器能保证 server.py 依赖的包一定装了。
    server_path = Path(__file__).resolve().parent / "server.py"
    params = StdioServerParameters(command=sys.executable, args=[str(server_path)])

    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()
            print(f"共 {len(tools.tools)} 个 tool：")
            for tool in tools.tools:
                first_line = (tool.description or "").splitlines()[0]
                print(f"  - {tool.name}: {first_line}")

            print("\n[1] list_tickets() —— 不传参")
            res = await session.call_tool("list_tickets", {})
            print(f"    content blocks = {len(res.content)}")
            all_tickets = payload(res)
            print(f"    拿到 {len(all_tickets)} 条：{[t['id'] for t in all_tickets]}")

            print("\n[2] list_tickets(status='open') —— 同一个工具，形状变了")
            res = await session.call_tool("list_tickets", {"status": "open"})
            just_one = payload(res)
            print(f"    content blocks = {len(res.content)}  -> 结果是 "
                  f"{type(just_one).__name__}：{just_one}")

            print("\n[3] create_ticket(...) 拿新 id")
            res = await session.call_tool(
                "create_ticket", {"title": "VPN 断线", "priority": "high"}
            )
            created = payload(res)
            new_id = created["id"]
            print(f"    新建 id={new_id} status={created['status']}")

            print("\n[4] get_ticket(999) —— 不存在的 id，验证程序不崩")
            res = await session.call_tool("get_ticket", {"ticket_id": 999})
            print(f"    error={payload(res).get('error')}")
            print(f"    is_error={res.is_error}  <- 业务错误不是协议错误")

            print(f"\n[5] 回查刚建的 {new_id}")
            res = await session.call_tool("get_ticket", {"ticket_id": new_id})
            print(f"    {payload(res)}")


if __name__ == "__main__":
    asyncio.run(main())
