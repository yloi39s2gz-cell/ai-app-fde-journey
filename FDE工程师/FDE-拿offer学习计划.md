# FDE 工程师（Forward Deployed Engineer）学习计划

> 对齐 OpenAI / Anthropic / Palantir / Databricks / Salesforce / 字节 / 腾讯 等 20+ 家真实 JD。
> 岗位本质：**驻场把 AI 系统在客户环境跑通的生产工程师**，不是售前、不是纯研发。

---

## ⚠️ 个人化适配（2026-09-22 更新，以本节为准）

**我的情况**：Python 偏弱、过往 AI 项目多为 AI 辅助完成；目标**国内市场**（大中小厂都投）；每天可投入 **1–2 小时**。

**裁剪结论**：

| 项 | 原计划 | 个人版 |
|---|---|---|
| 总时长 | 6 个月（按每天 3–4h） | **约 8 个月**（每天 1.5h × 7 ≈ 10h/周） |
| 第一目标 | 直接冲头部 FDE | **先够初级 FDE / AI应用开发岗（12–25k）**，第 6 个月起再冲大厂 |
| 已有基础 | 从零 | AI应用开发 stage0–4 已完成 → **跳过** LLM 心智模型/RAG/Agent 入门 |
| 最大短板 | - | **独立编码能力**（弱）→ 每天 20 分钟无 AI 手写；不能全靠 Copilot |

### 8 个月分档目标

| 阶段 | 时间 | 目标 | 对应投递 |
|---|---|---|---|
| **A 补地基** | M1–M2 | 无 AI 能写对 Python 小程序；会读他人代码；SQL/HTTP/Git 过关 | 不投，纯练 |
| **B FDE 核心** | M3–M5 | MCP + 企业级 RAG + 生产化三件套；1 个可演示项目 | **初级 FDE / AI应用开发（12–25k）** 开始投 |
| **C 作品+驻场特质** | M6–M7 | 模拟客户交付 case + 沟通练习；第 2 个项目 | 中级 FDE / 大厂初级（20–40k） |
| **D 冲刺** | M8 | 面试题库 + 内推 | 按 B/C 表现定：字节/腾讯/蚂蚁等 |

### 每周节奏（10h 固定分配）

| 时段 | 时长 | 内容 |
|---|---|---|
| 工作日晚 ×5 | 各 1h | 当周主任务（概念 20min + 动手 35min + 笔记 5min） |
| 周末 ×2 | 各 2.5h | 连续项目块：调试 / 部署 / 复盘 |
| 每天雷打不动 | 20min | **无 AI 手写**：默写昨天写过的函数/改 bug，写完才准开 Copilot |

### 国内投递关键词（B 阶段起用）

- P0：`FDE` `前线部署工程师` `AI前线部署工程师` `Agent开发` `大模型应用开发`
- P1：`AI应用开发工程师` `RAG` `解决方案工程师（AI）` `驻场工程师`
- 渠道：Boss / 猎聘 / 内推（woshifde.com 看情报）

### 当前进度

- [ ] FDE stage0（MCP）← **进行中**
- [ ] FDE stage1（企业级 RAG·权限）
- [ ] FDE stage2（生产化）
- [ ] FDE stage3（模拟客户交付）
- [ ] A 地基清单（见下）
- [ ] 第一个可演示项目上线
- [ ] 投出第一份简历

---

## 0. 岗位认知

### 0.1 FDE 是什么

- Palantir 发明（内部叫 "Delta"），现被 OpenAI、Anthropic、Databricks、腾讯、字节等大规模复制
- 过去 2 年岗位需求增长 42 倍（LinkedIn 数据）
- 薪资：海外头部 $170K–$500K+；国内 20–80k·15薪，高端年包 40w–100w+
- 本质 = 软件工程师 + 解决方案架构师 + 咨询顾问，对**上线结果**负责，不是对交付里程碑负责

### 0.2 与相邻岗位边界（面试必问）

| 岗位 | 职责 | 边界 |
|---|---|---|
| **FDE** | 客户环境里写代码、做集成，对结果负责 | 写生产代码，能扩展产品能力 |
| Solutions Architect | 售前方案与演示 | 成单即交接 |
| Customer Success Engineer | 配置与使用指导 | 限于产品已有功能 |
| Implementation Consultant | 项目管理与排期 | 技术问题上交研发 |
| Software Engineer | 按路线图做产品 | 基本不进客户环境 |

> 面试官问"你和 SA 有什么区别"，想听的是**边界**：谁写生产代码、谁对上线结果负责。

### 0.3 投递关键词

| 优先级 | 搜索词 |
|---|---|
| P0 | Forward Deployed Engineer / FDE / 前线部署工程师 / 前置部署工程师 |
| P0 | AI前线部署工程师 / Agent FDE |
| P1 | 解决方案工程师（AI方向）/ 驻场工程师 / 应用工程师 |
| P1 | Applied AI Engineer / Customer Engineer / Deployment Engineer |
| P2 | 技术咨询顾问（带 AI 交付）/ Professional Services Engineer |

国内渠道：Boss / 猎聘 / 智联搜以上词；情报站：woshifde.com、fdejobboard.com
海外：公司官网 careers 页优先，FDE 岗内推通过率远高于海投

---

## 1. JD 共性提炼（20+ 家）

### 1.1 硬技能出现频率

1. **🥇 Python（必须）+ JS/TS（几乎必须）** — 全栈生产级代码
2. **🥈 LLM 应用四件套**：Prompt Engineering / RAG / Agent / **Evals（评估）**
3. **🥉 MCP + Agent 编排** — 2026 高频词（Anthropic、Salesforce、中软国际点名）
4. **云平台**（AWS/Azure/GCP 至少一家）+ Docker/K8s + CI/CD
5. **数据能力**：SQL、数据管道、ETL、权限/脱敏
6. **集成能力**：REST API、企业系统（SAP/Oracle/Salesforce）、身份认证（OAuth/SAML）
7. **AI 编码工具**：Cursor、Claude Code（Disney 明确写进 JD）

### 1.2 软实力（几乎所有 JD 强调）

- ✅ 客户沟通：能对 CTO 讲架构，也能和一线开发蹲着 debug
- ✅ 模糊容忍度："客户也不知道自己要什么"是日常
- ✅ 主人翁意识（Ownership）：对上线结果负责
- ✅ 沉淀能力：把一次性方案固化成 playbook / 可复用资产
- ✅ 出差意愿 25–50%（纯远程 FDE 几乎不存在）
- ✅ 商业语言：ROI、token 成本、延迟、幻觉率 → 翻译给 CFO 听

### 1.3 经验门槛

- 大多数岗位 **3–5 年+** 工程经验，不是应届生岗位
- 最看重：**1 段完整的"从 0 到生产上线"经历** + **1 段客户/跨团队交付经历**

### 1.4 代表 JD 摘录

| 公司 | 经验 | 核心要求 |
|---|---|---|
| OpenAI | 5年+ | Python/JS 全栈；LLM 系统落地；原型→生产端到端；出差50% |
| Anthropic | 4年+ | MCP servers、sub-agents、agent skills；高级Prompt/Agent/Evals；出差25% |
| Palantir | 3年+ | Python/TS 生产代码；数据工程 ETL；Foundry/AIP；模糊环境独立交付 |
| Databricks | 6-7年+ | Spark；RAG、多Agent、Text2SQL、Fine-tuning；LangChain/DSPy |
| Disney | 3年+ | Prompt/Agent/RAG/Evals；日常用 Cursor、Claude Code |
| Salesforce | - | SQL/Python；RAG、向量库、MCP、agent-to-agent；OAuth/SAML |
| 字节（豆包） | - | Python/Java 全栈；大模型原理、效果评估、Post-Training |
| 腾讯 | - | AI前线部署工程师，北京/上海/杭州，20-60k×15 |
| 中软国际 | 3年+ | Python+TS/Java；MCP/sub-agents/skills；企业IT架构；Vibe Coding |

---

## 2. 六个月路线（4 阶段 Gate 制）

> 每阶段有明确里程碑（Gate），不过关不进入下一阶段。

### Phase 1：工程地基（第 1–4 周）

**目标**：能独立写出并部署一个全栈应用。

| 周 | 内容 | 产出 |
|---|---|---|
| W1 | Python 进阶：类型标注、asyncio、pytest、包管理（uv/poetry） | 带测试的 CLI/API 小项目 |
| W2 | 全栈：FastAPI + React/Next.js，REST 设计、JWT/OAuth 鉴权 | 全栈应用 |
| W3 | 云 + Docker：AWS 或阿里云，ECS/Lambda + S3/RDS，Dockerfile，GitHub Actions CI/CD | 公网可访问的部署 |
| W4 | Git 协作 + SQL 深化（窗口函数、执行计划）+ Linux/网络基础 | 笔记补弱项 |

**🎯 Gate 1**：一个部署在公网、有测试、有 CI/CD 的全栈项目，能现场演示。

- [ ] W1 完成
- [ ] W2 完成
- [ ] W3 完成
- [ ] W4 完成 + Gate 1 验收

### Phase 2：LLM 应用核心（第 5–10 周）⭐ 最重要

**目标**：掌握 Prompt / RAG / Agent / Evals 四件套，能从 0 搭生产级 LLM 应用。

| 周 | 内容 | 产出 |
|---|---|---|
| W5 | LLM API 精通：OpenAI + Claude 双 API；streaming、function calling、structured output、成本/延迟计算 | 结构化数据提取工具 |
| W6 | Prompt & Context Engineering：系统提示词、few-shot、CoT、上下文压缩 | prompt 模板库 |
| W7 | RAG 深水区：chunking、embedding 选型、混合检索（BM25+向量）、rerank、**权限过滤**、引用溯源 | 带权限的企业知识库问答 |
| W8 | Agent 工程：tool schema、plan-act-observe、状态管理、重试/降级、human-in-the-loop；LangGraph 或原生 Agent SDK | 多步自动化 Agent |
| W9 | MCP 协议：手写一个 MCP Server，接入 Claude Desktop / Claude Code | 开源 MCP Server |
| W10 | Evals：golden dataset、LLM-as-judge、回归测试；Promptfoo 或 Braintrust | 为 W7/W8 建评估集 |

**🎯 Gate 2**：一个 RAG + Agent + 评估集的完整项目，评估分数可复现。

- [ ] W5 完成
- [ ] W6 完成
- [ ] W7 完成
- [ ] W8 完成
- [ ] W9 完成
- [ ] W10 完成 + Gate 2 验收

### Phase 3：生产化与企业环境（第 11–16 周）

**目标**：把 demo 变成客户敢用的生产系统——FDE 与 AI 玩家的核心分水岭。

| 周 | 内容 | 产出 |
|---|---|---|
| W11 | 可观测性：Langfuse/LangSmith 追踪、token/成本/延迟监控 | 全链路追踪接入 |
| W12 | 安全：OWASP LLM Top 10、prompt injection、PII 脱敏、secrets、guardrails | 安全自查清单 + 防注入测试 |
| W13 | 数据工程：ETL 管道、向量库运维（pgvector/Qdrant）、schema、数据质量 | 数据层重构 |
| W14 | 企业集成：REST/SSO（OAuth/SAML）、私有化/混合云、Docker Compose → K8s 基础 | 私有化部署版本 |
| W15 | 可靠性：超时/坏 JSON/幻觉/超长文档、fallback、限流、成本预算 | 故障手册 Runbook |
| W16 | AI 编码工具流：Cursor / Claude Code 高级用法（CLAUDE.md、MCP 集成、spec-driven） | 自己的 AI 开发工作流 |

**🎯 Gate 3**：Phase 2 项目升级为有监控、有护栏、可私有化部署、有 Runbook 的"能交付给客户的系统"+ 一篇复盘。

- [ ] W11 完成
- [ ] W12 完成
- [ ] W13 完成
- [ ] W14 完成
- [ ] W15 完成
- [ ] W16 完成 + Gate 3 验收

### Phase 4：FDE 特质 + 求职（第 17–24 周）

**目标**：补上"客户那半边"，形成面试武器库。

#### 模拟客户交付项目（3 周）⭐ 核心

选一个**真实行业场景**（不是 todo app），例如：
- 物流公司 PDF 单据自动录入 → 结构化入库
- 金融研报知识库 + 合规问答（带权限隔离）
- 制造业工单分类 + 自动派单 Agent

**要求**：2 周内从业务访谈 → 需求拆解 → MVP → 生产级交付，全程写文档。
- 第 1 周：业务调研（找真实从业者聊）、discovery 文档、定义 ROI 指标
- 第 2 周：冲刺交付 + evals + 部署

#### 软技能刻意练习（并行）

- 把技术讲给非技术人："这个系统怎么帮你们公司省钱"
- 客户 role-play 练习（FDE 面试必有：模糊需求现场拆解）
- 准备万能问题："你和 Solutions Architect 有什么区别？"

#### 作品集与投递（最后 3 周）

- GitHub 放 2–3 个端到端项目（README、架构图、评估结果、复盘）
- 写 1–2 篇技术博客（沉淀 = JD 里的 "codify patterns"）
- 研究目标公司：国内（腾讯/字节/蚂蚁/智谱/中软国际）或海外
- 走**内推**优先

**🎯 Gate 4**：1 个"模拟客户交付"完整 case + 30 分钟讲清 ROI + 通过 mock interview。

- [ ] 模拟交付项目完成
- [ ] role-play / 系统设计练习完成
- [ ] 作品集上线
- [ ] Gate 4 验收（mock interview）

---

## 3. 推荐资源

| 类型 | 资源 |
|---|---|
| 路线图 | roadmap.sh/forward-deployed-engineer；GitHub: lunar-arun/Forward-Deployed-Engineer、thecoder8890/forward-deployed-engineer-roadmap |
| 方法论 | Palantir FDE 文化（Shyam Sankar 演讲）、Anthropic Engineering Blog、OpenAI Agents Guide |
| 书 | 《AI Engineering》— Chip Huyen |
| 工具链 | Langfuse（观测）、Promptfoo（评估）、pgvector/Qdrant（向量）、Cursor/Claude Code（编码） |
| 社区 | forwarddeployedhq.com、fdejobboard.com、woshifde.com |
| 参考 JD | openai.com/careers、anthropic.com/careers、palantir.com/careers |

---

## 4. 常见误区

1. ❌ 把 FDE 当"会讲 PPT 的工程师" → ✅ 核心是**生产交付**，指标是"客户下月还在用"
2. ❌ 只刷工程，不练沟通 → ✅ 面试有客户 role-play，过不了就出局
3. ❌ 拒绝出差要全远程 → ✅ 驻场是价值来源，纯远程 FDE 岗几乎不存在
4. ❌ 等客户给明确需求 → ✅ 客户也不知道要什么，你用原型帮他想清楚
5. ❌ 把 demo 当生产代码交 → ✅ 分清 hack 模式和生产模式
6. ❌ 死磕 Transformer 数学 → ✅ 除非研究岗，不需要论文级深度

---

## 5. 与 AI 应用开发岗的差异（本仓库两条线）

| | AI应用开发（`../AI应用开发/`） | FDE（本文件夹） |
|---|---|---|
| 面向 | 产品公司内部研发岗 | 驻场客户交付岗 |
| 面试 | 八股 + 项目 + 算法中等 | 系统设计 + 客户 role-play + 模糊需求拆解 |
| 核心产出 | 产品功能 | 客户环境里能跑、能维护的系统 |
| 额外要求 | 深度（RAG/Agent 精调） | 广度 + 沟通 + 商业语言 + 出差 |
| 共用基础 | Python / LLM API / RAG / Agent / Evals **完全共用** | 同左，另加生产化、企业集成、客户交付 |

> 建议：两条线共享 Phase 1–2 基础；若主攻 FDE，Phase 3 起按本计划走。
