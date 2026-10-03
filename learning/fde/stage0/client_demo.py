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

# TODO 1: 补 import。
#   需要：asyncio、sys、pathlib.Path
#   需要：from mcp import ClientSession, StdioServerParameters
#   需要：from mcp.client.stdio import stdio_client
#
# 提示：mcp 2.x 里 client 的入口就叫 mcp.client.stdio.stdio_client。


async def main() -> None:
    # TODO 2: 算出 server.py 的绝对路径。
    #   用 Path(__file__).resolve().parent / "server.py"
    #   为什么要绝对路径？因为 Server 会被当成**另一个进程**启动，
    #   它的工作目录不一定是当前目录。这是驻场最常见的"在我机器上能跑"来源。
    server_path = ...  # noqa: F841

    # TODO 3: 组装启动参数。
    #   StdioServerParameters(command=?, args=[?])
    #   command 用 sys.executable（当前解释器），不要写死 python
    #   —— 因为客户机器上的 python 可能不是你这台。
    params = ...

    # TODO 4: 建连接。整体结构是两层 async with 嵌套：
    #   async with stdio_client(params) as (read, write):
    #       async with ClientSession(read, write) as session:
    #           await session.initialize()
    #   然后在最里面做这几件事：
    #     1) tools = await session.list_tools()
    #        打印 [t.name for t in tools.tools]
    #     2) res = await session.call_tool("list_tickets", {})      -> 3 个 text block
    #        res = await session.call_tool("list_tickets", {"status": "open"}) -> 1 个 block
    #        ★ 陷阱：MCP 把"列表"摊成多个 block，把"单项"留在一个 block 里，
    #          所以 block 数量是 1 还是 N 会变，不能假设永远是个 list。
    #          正确写法是遍历 res.content 逐个 json.loads 收起来：
    #              blobs = [json.loads(c.text) for c in res.content if c.type == "text"]
    #          写 res.content[0].text 只会拿到第 1 条工单。
    #     3) 再 call_tool("create_ticket", {...}) 拿到新 id；
    #        再 call_tool("get_ticket", {"ticket_id": 999}) —— 这个必须不崩，
    #        只打印出 error 字段。注意：此时 res.is_error 仍然是 False。
    ...
    raise NotImplementedError("把 TODO 4 描述的两层 async with 写出来（写完删掉这一行）")


# TODO 5: 入口。
#   if __name__ == "__main__": asyncio.run(main())
