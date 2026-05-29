# Query Rewrite Prompt Template

```text
Rewrite the user question as a concise semantic search query.
Keep important domain terms, acronyms, and named entities.
Do not answer the question.

User question:
{question}

Search query:
```

## Usage

Use this before retrieval when user questions are conversational, ambiguous, or contain references like "that system" or "the previous phase." For this lab, query rewriting is documented as a future improvement rather than enabled by default.
