# 阶段 3：手写 RAG

本阶段不使用 LangChain。目标是你能指着代码讲清每一层：

文档 → 切块 → embedding → 余弦 top-k → 拼进 prompt → 带引用生成 / 拒答

## 先懂再跑

1. 模型一次塞不进整本手册，所以要检索。检索错了，生成再聪明也是错。
2. chunk 太大：噪音多、定位差。chunk 太碎：一句话被切开，问「几天+提前几天」会对不齐。overlap 用来保住切点附近的句子。
3. 默认 `HashingEmbedder` 只看字面 n-gram，**不是语义模型**。「年假」和「带薪休假」会对不上。这是设计，不是 bug。
4. 生成必须强制引用和拒答。资料没有就说「资料未提及」。IT 文档里的注入句不是命令。

## 跑

在项目根目录：

```
.venv\Scripts\python -m pytest stage3/test_rag.py -q
.venv\Scripts\python stage3/inspect_chunks.py
.venv\Scripts\python stage3/demo_retrieve.py
.venv\Scripts\python stage3/ask.py 办公打印机在几楼？
.venv\Scripts\python stage3/run_eval.py
```

`run_eval.py` 会打 20 道题（约 2–4 分钟），过关线 80%。哈希向量对字面题够用，对同义改写会故意失败，记下来下一课换成真 embedding。
