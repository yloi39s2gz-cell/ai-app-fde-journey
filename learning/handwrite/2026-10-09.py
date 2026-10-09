"""日常A · 2026-10-09

规则：20 分钟计时，AI 全关（包括那个对话）。卡住就在注释里写"我卡在哪"。
到点就停——写不完照样提交。

--------------------------------------------------------------------
今天的题（故意不是 server.py 里的那个函数，所以你抄不到）
--------------------------------------------------------------------

    find_tickets(tickets, keyword, status=None) -> list[dict]

    tickets 是 list[dict]，每条有 id / title / status / priority。
    找出 title 里**包含** keyword 的工单。

约束（五条，一条都不能少）：

    1. 不区分大小写：keyword 传 "vpn" 要能匹配 "VPN 连不上"
    2. keyword 传空字符串 "" 时，视为"全部"（不是"一个都匹配不上"）
    3. status 不为 None 时，状态还要匹配
    4. 结果按 id 升序排列
    5. 返回全新的 list[dict]，不许改动传进来的那个列表

第 2 条是这题的核心，不是凑数——想清楚"空字符串"和"没传"
在你脑子里是不是同一件事，以及**你打算怎么区分它们**。
"""

from __future__ import annotations


def find_tickets(
    tickets: list[dict],
    keyword: str,
    status: str | None = None,
) -> list[dict]:
    result=[]
    for t in tickets:
        if keyword.lower() in t["title"].lower():
            result.append(t)
    return result
    # 在这里写。先别往下看。
    #
    # 卡住的话，把"我卡在哪"写在这行下面，然后继续想。
    raise NotImplementedError


# ---------------------------------------------------------------------
# 自测（写完再跑，别提前看断言里的内容——那就是答案）
# ---------------------------------------------------------------------
if __name__ == "__main__":
    SAMPLE = [
        {"id": 103, "title": "申请数据分析权限", "status": "resolved", "priority": "low"},
        {"id": 101, "title": "打印机卡纸", "status": "open", "priority": "medium"},
        {"id": 102, "title": "VPN 连不上", "status": "in_progress", "priority": "high"},
    ]
    before = [dict(t) for t in SAMPLE]  # 快照，用来验约束 5

    # 约束 1 + 4：小写关键词也要能匹配，且结果按 id 升序
    ids = [t["id"] for t in find_tickets(SAMPLE, "vpn")]
    assert ids == [102], f"约束 1/4 没过，拿到 {ids}"

    # 约束 2：空关键词 = 全部（而不是空列表）
    assert len(find_tickets(SAMPLE, "")) == 3, "约束 2 没过：空关键词应该返回全部 3 条"

    # 约束 3：status 叠加过滤
    ids = [t["id"] for t in find_tickets(SAMPLE, "", status="open")]
    assert ids == [101], f"约束 3 没过，拿到 {ids}"

    # 约束 4：输入乱序也要输出有序
    assert [t["id"] for t in find_tickets(SAMPLE, "", status=None)] == [101, 102, 103], "约束 4 没过"

    # 约束 5：不许改原列表
    assert SAMPLE == before, "约束 5 没过：你把传进来的列表改了"

    print("五条约束全过 ✅")
