# Retrieval Quality Notes

Phase 4 deliverable for evaluating RAG retrieval quality with Postgres and `pgvector`.

## What Good Retrieval Looks Like

A retrieval layer is working well when the top chunks are:

- Relevant to the user's question
- Specific enough to support an answer
- Diverse enough to avoid repeating the same passage
- Grounded with source metadata
- Ranked in a way that matches human judgment

## Metrics To Track

| Metric                   | Meaning                                                 | How To Use                              |
| ------------------------ | ------------------------------------------------------- | --------------------------------------- |
| Recall@k                 | Whether a relevant chunk appears in the top `k` results | Test with known-answer questions        |
| Precision@k              | How many top `k` chunks are actually useful             | Manually label retrieved chunks         |
| MRR                      | How high the first relevant chunk appears               | Useful for question-answering workflows |
| Similarity score spread  | Difference between top result and lower results         | Helps tune thresholds                   |
| Answer citation accuracy | Whether the answer cites the right sources              | Check generated answer against chunks   |

## Quality Checklist

1. Create 10-20 representative questions for the indexed documents.
2. Label the chunks that should answer each question.
3. Run `/search` with `limit=5`.
4. Record whether the expected chunk appears in the top results.
5. Inspect whether the chunk boundaries contain enough surrounding context.
6. Tune `CHUNK_SIZE`, `CHUNK_OVERLAP`, and `SIMILARITY_THRESHOLD`.

## Chunking Tradeoffs

| Choice         | Benefit                 | Risk                                |
| -------------- | ----------------------- | ----------------------------------- |
| Smaller chunks | More precise retrieval  | Answers may lack context            |
| Larger chunks  | More context per result | Similarity signal gets diluted      |
| More overlap   | Fewer boundary misses   | More duplicate retrieval results    |
| Less overlap   | Smaller index           | Higher chance of splitting concepts |

## pgvector Notes

This lab uses cosine distance:

```sql
1 - (embedding <=> query_embedding) AS similarity
```

The `ivfflat` index is included for the learning path. For small local datasets, sequential scan may be just as fast. For larger collections, tune `lists`, run `ANALYZE`, and benchmark query latency.

## Embedding Notes

The default `hash` embedding provider is deterministic and dependency-light. It is useful for smoke tests, but it is not semantically strong enough for production-quality retrieval.

For better retrieval quality, switch to Ollama embeddings:

```bash
ollama pull nomic-embed-text
EMBEDDING_PROVIDER=ollama
OLLAMA_EMBEDDING_MODEL=nomic-embed-text
EMBEDDING_DIMENSION=768
```

After changing embedding dimension or provider, recreate the database volume so the `vector(n)` column matches the embedding size.

## Failure Modes

| Failure               | Likely Cause                               | Fix                                       |
| --------------------- | ------------------------------------------ | ----------------------------------------- |
| No results            | Threshold too high or no documents indexed | Lower threshold, ingest docs              |
| Repetitive results    | Chunk overlap too high                     | Lower overlap or add diversity reranking  |
| Wrong source cited    | Retrieved context is weak                  | Improve embeddings or add query rewriting |
| Good chunk ranked low | Chunk too large or query too vague         | Tune chunk size or rewrite query          |
| Slow search           | Large index without tuning                 | Tune `ivfflat`, add filters, benchmark    |
