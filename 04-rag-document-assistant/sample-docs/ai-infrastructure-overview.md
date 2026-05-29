# AI Infrastructure Overview

AI infrastructure connects application APIs, document retrieval, model serving, observability, and deployment automation into a reliable system.

The local learning path starts with backend services and queues, then adds local LLM serving, retrieval-augmented generation, observability, benchmarking, and Kubernetes deployment.

Retrieval-augmented generation improves answer grounding by retrieving relevant document chunks before asking a language model to answer. A typical RAG flow embeds the user question, searches a vector database, injects retrieved context into a prompt, and returns an answer with source references.

Postgres with pgvector is useful for learning because it combines relational metadata, SQL filtering, and vector similarity search in one local database. This makes it easier to inspect source documents, chunks, metadata, and retrieval scores while building the system.

Good retrieval quality depends on document loading, chunk size, chunk overlap, embedding model quality, similarity thresholds, and prompt design. The assistant should say when retrieved context is insufficient instead of inventing an answer.
