# 阶段 A｜编程地基（M1–M2，每天含在 1.5h 内）

> 原则：**能独立写 + 能读懂 + 能 debug**，不追求刷算法题。
> 背景：你会 Python 但过往靠 AI 辅助 → 两周内建立"先手写、后 AI"的习惯。

## 每天 20 分钟无 AI 手写（贯穿全程）

规则：
1. 关掉 Cursor / Copilot / Claude 的自动补全
2. 默写或改写**昨天亲手写过**的一个小函数（10–30 行）
3. 本地跑通才算完成；卡住先想 5 分钟，再允许看笔记，最后才准问 AI
4. 写完这 20 分钟，之后的时间可以正常用 AI 辅助提高效率

记录法：在本文件末尾「无AI手写打卡」表里打勾。

---

## M1 第 1–2 周：Python 能上生产线的写法

**每天主任务（40–50min）拆解**：概念 15min → 跟敲 25min → 改一个变体 10min

| 天 | 主任务 | 验收（能自己讲出来） |
|---|---|---|
| D1 | 类型标注 + 函数签名：给 3 个旧函数补全 type hint | 为什么 `list` 和 `list[str]` 对 FDE/面试都重要 |
| D2 | Pydantic：定义一个 Ticket 模型，校验非法 priority | LLM 输出为什么要过 Pydantic（衔接你 stage2） |
| D3 | 异常与重试：`try/except` + 最多 3 次重试 + 日志 | API 超时时你的代码会发生什么 |
| D4 | 字典/列表 comprehensions + `defaultdict` | 什么时候用它代替 for 循环 |
| D5 | 文件读写：JSON/CSV 各读写一次，处理坏行 | 客户丢来脏文件你怎么办 |
| D6 | 周末块1：不看教程，独立写 `word_count.py`（统计文本词频，支持从文件读） | 全程不开 AI |
| D7 | 周末块2：给 word_count 加测试（pytest 3 个 case） | `pytest` 能绿 |

## M1 第 3–4 周：HTTP + SQL + Git（FDE 集成三件套）

| 天 | 主任务 | 验收 |
|---|---|---|
| D8 | HTTP：用 `httpx` 调一个公开 API，处理非 200 | 状态码 401/403/404/429/500 含义 |
| D9 | 查询参数、headers、POST body 各写一例 | 能画出一次 REST 请求的 5 个组成 |
| D10 | SQL 基础回顾：SELECT/WHERE/JOIN/GROUP BY，本地用 sqlite 练 | 3 表 JOIN 手写不出就重练 |
| D11 | SQL 进阶：窗口函数 `ROW_NUMBER` / 聚合子查询 | 面试常问：每部门薪资 top3 |
| D12 | Git：`init / add / commit / branch / merge / diff`，故意制造一次冲突再解 | 会用 `git log --oneline` 和 `git diff` |
| D13 | 周末块：建一个 `practice` 仓库，把 M1 所有练习 commit 进去，写 README | 别人打开仓库能看懂你做了什么 |
| D14 | 复盘：默写 httpx 调用 + SQL JOIN + Git 三连，写进打卡表 | 三样都能无 AI 写出骨架 |

## M2 第 1–2 周：读代码 + debug（比写更重要）

驻场日常 = **读客户/同事的代码 + 修 bug**。

| 天 | 主任务 |
|---|---|
| D15 | 打开你 AI应用开发 `stage3/rag.py`（当时 AI 辅助写的），**逐行注释**它在干什么 |
| D16 | 给 stage3 加一个新功能：查询时返回 chunk 来源文件名（不问 AI，先自己试 30min） |
| D17 | 故意在 stage4 `agent.py` 里埋 3 个 bug（类型错/死循环/漏 await），再自己找出来 |
| D18 | 学会看 traceback：从最下一行往上读，定位到自己的文件行号 |
| D19 | 用 `print` / 断点式日志 debug 一个真实卡点（自己选） |
| D20 | 周末块：重构 stage3 里你觉得写得烂的一段，保持测试仍绿 |
| D21 | 休息 + 打卡表盘点 |

## M2 第 3–4 周：最小全栈 + 部署（国内 FDE/应用开发都看这个）

| 天 | 主任务 |
|---|---|
| D22 | FastAPI：3 个接口（GET 列表 / GET 详情 / POST 创建），内存存数据 |
| D23 | 给 FastAPI 写 2 个 pytest（用 `TestClient`） |
| D24 | 简单前端：一个 `index.html` + fetch 调上面的接口（不用框架也行） |
| D25 | Docker：写 Dockerfile，`docker run` 起来，浏览器能访问 |
| D26 | 部署到免费云（国内可用 阿里云/腾讯云试用，或 Railway/Render），拿到公网 URL |
| D27 | GitHub Actions：push 后自动跑 pytest（抄一个最简 yml） |
| D28 | 周末块：把 URL 写进 README，录 1 分钟演示（手机录屏即可） |

### ✅ 阶段 A 过关清单（M2 末自测，全勾才进 B）

- [ ] 无 AI 手写：带类型标注的函数 + Pydantic 校验 + 重试逻辑（30 分钟内）
- [ ] 无 AI 手写：httpx 调 API + sqlite 3 表 JOIN（各 15 分钟）
- [ ] 能读懂并解释自己 AI 辅助写的 stage3 任意一个文件
- [ ] 有一个「FastAPI + 测试 + Docker + 公网 URL」的小项目链接
- [ ] Git 提交历史清晰，有 README
- [ ] 打卡表 ≥ 40 天无 AI 手写

---

## 无AI手写打卡

| 日期 | 写了什么（≤5 字） | 独立完成? |
|---|---|---|
| | | |
| | | |
