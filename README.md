RAG-based LLM System using Groq and Tavily

I developed a Retrieval-Augmented Generation (RAG) system that integrates Groq LLM with Tavily for a ReAct (Reasoning + Acting) pattern workflow.
The system performs two-tiered information retrieval:

Local Search – It first queries a ChromaDB vector store to find relevant context from previously stored documents.

Web Search – If sufficient context isn’t found locally, it fetches additional information from the internet using Tavily.

The backend is built with FastAPI, while the frontend is developed using Next.js. Data management and storage are handled through PostgreSQL.

This architecture allows the model to reason, retrieve, and respond intelligently by combining local knowledge with real-time external information, providing more accurate and context-aware answers.