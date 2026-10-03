# 阶段 1：把 LLM 调用做成工程客户端

阶段 0 的 `chat()` 能跑 Demo，但上不了班：

- 每次调用都 `OpenAI()` 一次
- 网络闪一下就崩，没有重试
- 没有超时，请求可能挂死
- 不能流式，界面只能干等
- 不知道花了多少 token，成本两眼一抹黑

本阶段你要自己把 `llm_client.py` 填完。测试我写好了。

## 你要先懂的 5 个概念

1. **OpenAI 兼容协议**：DeepSeek / 通义 / 本地 vLLM 都走 `chat.completions.create`。差的是 `base_url`、`api_key`、`model`。
2. **超时**：网络请求必须设上限，否则线程会一直等。
3. **重试**：只重试「过一会儿可能好」的错误（超时、连接断开、429、5xx）。用户参数写错（400）重试没有意义。
4. **流式**：模型一个 token 一个 token 吐。`stream=True` 时返回的是迭代器，每片在 `chunk.choices[0].delta.content`。
5. **usage**：`prompt_tokens` 是你塞进去的，`completion_tokens` 是它生成的。钱和延迟主要看这两项。

## 你要做的事

1. 打开 `stage1/llm_client.py`，按文件里的中文步骤填空（所有 `raise NotImplementedError` 都要干掉）。
2. 在项目根目录跑测试：

```powershell
.\.venv\Scripts\python.exe -m pytest stage1\test_llm_client.py -v
```

3. 测试全绿后，跑一次真流式（会花一点点额度）：

```powershell
.\.venv\Scripts\python.exe stage1\demo_stream.py
```

4. 用自己的话填 `stage1/notes.md`。

不要先看我怎么写实现。卡住了把报错贴过来。
