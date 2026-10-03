embedder=HashingEmbedder  reranker=BM25Reranker
suite=common  题数=15  chunk_size=300  chunks=18

--- 单路基线 ---
dense                        R@1  93%  R@3 100%  MRR 0.967
sparse (BM25)                R@1 100%  R@3 100%  MRR 1.000

--- RRF 权重（w_sparse : w_dense）---
hybrid 1:1                   R@1 100%  R@3 100%  MRR 1.000
hybrid 2:1                   R@1 100%  R@3 100%  MRR 1.000
hybrid 3:1                   R@1 100%  R@3 100%  MRR 1.000
hybrid 1:0.5                 R@1 100%  R@3 100%  MRR 1.000
hybrid 1:0.25                R@1 100%  R@3 100%  MRR 1.000
hybrid 4:1                   R@1 100%  R@3 100%  MRR 1.000

--- 重排：候选集内重算 BM25（top-4 全重排）---
rerank base=0                R@1 100%  R@3 100%  MRR 1.000
rerank base=0.15             R@1 100%  R@3 100%  MRR 1.000
rerank base=0.3              R@1 100%  R@3 100%  MRR 1.000
rerank base=0.5              R@1 100%  R@3 100%  MRR 1.000
rerank base=0.7              R@1 100%  R@3 100%  MRR 1.000
rerank base=1                R@1 100%  R@3 100%  MRR 1.000
