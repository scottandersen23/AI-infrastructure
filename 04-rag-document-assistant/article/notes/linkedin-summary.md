# LinkedIn Summary

I built a **RAG Document Assistant** to explore how AI systems can answer questions using private documents.

The goal was not just to connect files to an LLM.

The goal was to build a simple pipeline that makes documents searchable, retrievable, and easier to trust.

This project uses FastAPI, Postgres, pgvector, document loading, text chunking, embeddings, vector search, and prompt templates.

The build includes:

* Uploading Markdown, text, and PDF files
* Breaking documents into smaller text chunks
* Creating embeddings for search
* Storing document vectors in Postgres with `pgvector`
* Searching documents through a `/search` endpoint
* Asking questions through an `/ask` endpoint
* Returning answers with source citations
* Handling cases where there is not enough information
* Measuring retrieval quality with basic search and citation metrics

The biggest takeaway:

RAG is not just about the AI model. It is about giving the model the right information.

A good answer depends on how the documents are loaded, split, searched, and passed into the prompt.

The model is important, but the system around the model is what makes the answer useful, grounded, and easier to verify.

This project helped me better understand how RAG turns private documents into reliable context for AI applications.

#RAG #AIInfrastructure #DataPlatform #pgvector #Postgres #FastAPI #LLM #VectorSearch #AIEngineering
