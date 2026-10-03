"""MCP Server：模拟客户工单系统（FDE stage0 教学用）。

基于 MCP Python SDK v2（FastMCP 已更名为 MCPServer）。

运行方式（stdio，给 MCP 客户端拉起）:
    python server.py

可视化调试:
    uvx @modelcontextprotocol/inspector python server.py
"""

from __future__ import annotations

from mcp.server.mcpserver import MCPServer
from pydantic import BaseModel, Field

mcp = MCPServer(name="ticket-system", instructions="模拟客户工单系统，供 FDE stage0 教学演示。")


class Ticket(BaseModel):
    id: int
    title: str
    status: str = Field(description="open | in_progress | resolved")
    priority: str = Field(description="low | medium | high")


# 模拟客户数据库（进程内存；重启即丢——故意的，让你观察状态）
_DB: dict[int, Ticket] = {
    101: Ticket(id=101, title="打印机卡纸", status="open", priority="medium"),
    102: Ticket(id=102, title="VPN 连不上", status="in_progress", priority="high"),
    103: Ticket(id=103, title="申请数据分析权限", status="resolved", priority="low"),
}
_NEXT_ID = 104


@mcp.tool()
def list_tickets(status: str | None = None) -> list[dict]:
    """查询工单列表。

    Args:
        status: 可选，按状态过滤：open / in_progress / resolved。不传则返回全部。
    """
    tickets = list(_DB.values())
    if status:
        tickets = [t for t in tickets if t.status == status]
    return [t.model_dump() for t in tickets]


@mcp.tool()
def get_ticket(ticket_id: int) -> dict:
    """按 ID 查询单个工单详情。

    Args:
        ticket_id: 工单 ID，例如 101
    """
    if ticket_id not in _DB:
        return {"error": f"ticket {ticket_id} not found"}
    return _DB[ticket_id].model_dump()


@mcp.tool()
def create_ticket(title: str, priority: str = "medium") -> dict:
    """新建工单（写操作，会改变系统状态）。

    Args:
        title: 工单标题，用一句话描述问题
        priority: 优先级 low / medium / high，默认 medium
    """
    global _NEXT_ID
    ticket = Ticket(id=_NEXT_ID, title=title, status="open", priority=priority)
    _DB[_NEXT_ID] = ticket
    _NEXT_ID += 1
    return ticket.model_dump()


@mcp.tool()
def resolve_ticket(ticket_id: int) -> dict:
    """将工单标记为已解决。

    Args:
        ticket_id: 要关闭的工单 ID
    """
    if ticket_id not in _DB:
        return {"error": f"ticket {ticket_id} not found"}
    _DB[ticket_id].status = "resolved"
    return _DB[ticket_id].model_dump()


if __name__ == "__main__":
    # stdio 传输：由 MCP 客户端作为子进程拉起
    mcp.run(transport="stdio")
