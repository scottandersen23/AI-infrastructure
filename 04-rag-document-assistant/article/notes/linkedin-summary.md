# LinkedIn Summary

The project uses FastAPI, Postgres, `pgvector`, document loading, chunking, embeddings, vector search, and prompt templates to show how retrieval-augmented generation works as a data platform pattern.

The key idea: RAG is not just a model feature. It is an architecture for turning private documents into retrievable, auditable, source-grounded context.

This project covers:

- Markdown, text, and PDF ingestion
- Overlapping text chunking
- Hash embeddings for local smoke tests
- Optional Ollama embeddings for stronger semantic retrieval
- Postgres + `pgvector` as the vector store
- `/search` for retrieval inspection
- `/ask` for source-grounded answers
- Prompt templates with citations and "not enough information" behavior
- Retrieval quality metrics like Recall@k, Precision@k, MRR, similarity score spread, and citation accuracy

From an AI architecture perspective, the biggest takeaway is that RAG quality depends on the full pipeline: document loading, chunking, embeddings, metadata, vector search, prompt construction, and evaluation.

The model is only one part of the system. The data architecture around the model determines whether the answer is grounded, traceable, and useful.

#RAG #AIInfrastructure #DataPlatform #pgvector #Postgres #FastAPI #LLM #VectorSearch #AIDesign #MachineLearning
