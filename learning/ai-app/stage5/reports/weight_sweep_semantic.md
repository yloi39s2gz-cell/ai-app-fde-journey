embedder=HashingEmbedder  reranker=BM25Reranker
suite=semantic  题数=15  chunk_size=300  chunks=18

--- 单路基线 ---
dense                        R@1  47%  R@3  80%  MRR 0.600
sparse (BM25)                R@1  87%  R@3 100%  MRR 0.933

--- RRF 权重（w_sparse : w_dense）---
hybrid 1:1                   R@1  67%  R@3  93%  MRR 0.789
hybrid 2:1                   R@1  80%  R@3  93%  MRR 0.867
hybrid 3:1                   R@1  80%  R@3  93%  MRR 0.867
hybrid 1:0.5                 R@1  80%  R@3  93%  MRR 0.867
hybrid 1:0.25                R@1  80%  R@3  93%  MRR 0.856
hybrid 4:1                   R@1  80%  R@3  93%  MRR 0.856

--- 重排：候选集内重算 BM25（top-4 全重排）---
rerank base=0                R@1  87%  R@3 100%  MRR 0.933
rerank base=0.15             R@1  87%  R@3 100%  MRR 0.933
rerank base=0.3              R@1  87%  R@3 100%  MRR 0.933
rerank base=0.5              R@1  87%  R@3 100%  MRR 0.933
rerank base=0.7              R@1  87%  R@3 100%  MRR 0.933
rerank base=1                R@1  87%  R@3 100%  MRR 0.933
