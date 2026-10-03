# 阶段 2：Prompt 与结构化输出

先懂四件事，再跑代码。

1. Prompt 四段式：指令、约束、示例、输出格式。本阶段 system 里用了指令+约束+Schema。
2. 「请输出 JSON」不可靠。生产做法：Schema → 解析 → Pydantic 校验 → 失败把错误塞回去重试。
3. 抽取任务 temperature=0。要的是稳定，不是文采。
4. 用户输入和知识库文档都不可信。提示注入 = 在不可信文本里夹「忽略系统指令」。

## 跑

在项目根目录：

```
.venv\Scripts\python -m pytest stage2/test_parser.py -q
.venv\Scripts\python stage2/run_eval.py
.venv\Scripts\python stage2/injection_demo.py
```

`run_eval.py` 会打 20 条简历，过关线 95%。大约 1–2 分钟。
