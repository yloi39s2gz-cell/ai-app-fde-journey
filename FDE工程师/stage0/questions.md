# Stage 0 自测（不看 README 回答）

1. MCP 的全称？解决的核心问题是什么？

2. stdio 和 streamable HTTP 两种 transport 分别用在什么场景？

3. `create_ticket` 是读操作还是写操作？驻场交付时写操作 tool 通常要加什么机制？为什么？

4. Tool 的 description 写得好坏，会影响什么？举一个"写得很差的 description"的例子。

5. 面试题：「MCP 和 Function Calling 有什么区别？」——用 30 秒答完。

6. 面试题：「你为什么给客户交付 MCP Server，而不是直接把集成写进我们的产品？」——用 FDE 的 Ownership 视角答。

---

<details>
<summary>参考答案（做完再点开）</summary>

1. Model Context Protocol。让任意 MCP 客户端能以统一方式接入任意工具提供方，工具与 Agent 解耦，可插拔、可复用。

2. stdio：本地工具，客户端把 Server 当子进程拉起（Claude Desktop/Code 常用）。HTTP：远程共享 Server，多客户端连接，适合团队级部署。

3. 写操作。通常要 human-in-the-loop 确认、权限校验、审计日志——因为 Agent 可能误判，驻场环境写错会影响客户真实业务。

4. 影响模型选工具的准确率。差例子：`def search(q: str)` 注释写"搜索"——什么时候搜、搜什么范围全没说，模型宁可不用或乱用。好 description 要写：用途、何时用、参数含义与单位、边界情况。

5. Function calling：工具定义在应用代码里，绑死一个应用，换工具要改代码。MCP：工具在独立 Server 进程里，任何支持 MCP 的客户端都能接，换工具改配置不改代码。MCP 是"协议层标准化"，FC 是"单应用内机制"。

6. FDE 对客户长期成功负责（Ownership）：交付 Server 后客户自有团队可维护、可扩展（playbook the client owns）；写进我方产品则形成黑盒依赖，我方离场后集成就死了，且每个客户定制都会污染产品主干（one customer across many capabilities vs product for many）。

</details>
