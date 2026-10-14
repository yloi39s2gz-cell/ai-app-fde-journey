"""MCP 调试客户端（骨架 —— 请把 5 个 TODO 填完）。

为什么要有这个文件：
    server.py 是个 stdio Server，它靠 stdin/stdout 收发 JSON-RPC，
    直接 python server.py 会看起来"卡住"。唯一能验证它的办法，
    是用一个 MCP Client 把它当子进程拉起来。

运行：
    python client_demo.py

做完对照：client_demo_reference.py
"""

from __future__ import annotations

import asyncio # TODO 1: 补 import。
import sys
import json
from pathlib import Path
from mcp import ClientSession,StdioServerParameters # TODO 2: 补 import。
from mcp.client.stdio import stdio_client # TODO 3: 补 import。


async def main() -> None:
    server_path=Path(__file__).resolve().parent / "server.py"
    params = StdioServerParameters(command=sys.executable, args=[str(server_path)])
    async with stdio_client(params) as (read,write):
         async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            print([t.name for t in tools.tools])

            res = await session.call_tool("list_tickets", {})
            blobs = [json.loads(c.text) for c in res.content if c.type == "text"]
            print(len(res.content), "块:", blobs)

            res = await session.call_tool("list_tickets", {"status": "open"})
            blobs = [json.loads(c.text) for c in res.content if c.type == "text"]
            print(len(res.content), "块:", blobs)

            res = await session.call_tool("create_ticket", {"title": "测试工单", "priority": "high"})
            blobs = [json.loads(c.text) for c in res.content if c.type == "text"]
            print("新建:", blobs)

            res = await session.call_tool("get_ticket", {"ticket_id": 999})
            blobs = [json.loads(c.text) for c in res.content if c.type == "text"]
            print("999:", blobs, "is_error:", res.is_error)



if __name__=="__main__":
    asyncio.run(main())