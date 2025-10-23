# # """
# # Simplified RAG Orchestrator - Windows Compatible (No Emojis)
# # """
# # import logging
# # from typing import Dict, Any, Optional, List
# # from datetime import datetime
# # import uuid

# # from app.core.enums import RAGStrategy
# # from app.models.rag_model import Session
# # from app.services.rag_service import graph_rag_query

# # logger = logging.getLogger(__name__)


# # class RAGOrchestrator:
# #     """
# #     Simplified orchestrator that works with current dependencies
# #     """
    
# #     def __init__(self):
# #         logger.info("Initializing RAG Orchestrator...")
        
# #         # Initialize core services from dependencies
# #         from app.core.dependencies import get_llm_service, get_embedding_service, get_vectorstore
        
# #         self.llm_service = get_llm_service()
# #         self.embedding_service = get_embedding_service() 
# #         self.vectorstore = get_vectorstore()
        
# #         # Strategy implementations
# #         self.strategies = {
# #             RAGStrategy.SIMPLE: self._simple_rag_strategy,
# #             RAGStrategy.AGENTIC: self._agentic_rag_strategy,
# #             RAGStrategy.AUTO: self._auto_rag_strategy
# #         }
        
# #         logger.info("[OK] RAG Orchestrator initialized successfully")
    
# #     async def _simple_rag_strategy(self, query: str, context: Dict) -> Dict[str, Any]:
# #         """Simple RAG implementation with document filtering"""
# #         try:
# #             # Generate embedding for query
# #             query_embedding = self.embedding_service.embed_text(query)
            
# #             # Prepare filter for document_id
# #             filter_params = {}
# #             document_id = context.get("document_id")
# #             if document_id:
# #                 filter_params = {"document_id": document_id}
# #                 logger.info(f"Filtering search by document_id: {document_id}")
            
# #             # Search vector store with filter
# #             search_results = self.vectorstore.search_by_embedding(
# #                 query_embedding=query_embedding,
# #                 top_k=context.get("top_k", 5),
# #                 filter=filter_params
# #             )
            
# #             # If no results with filter, try without filter
# #             if not search_results and document_id:
# #                 logger.info("No results with document filter, trying without filter")
# #                 search_results = self.vectorstore.search_by_embedding(
# #                     query_embedding=query_embedding,
# #                     top_k=context.get("top_k", 5)
# #                 )
            
# #             # Build context from retrieved chunks
# #             context_text = "\n\n".join([
# #                 f"Document {i+1}: {result['document']}"
# #                 for i, result in enumerate(search_results[:3])  # Use top 3
# #             ])
            
# #             # Generate answer using context
# #             if context_text.strip():
# #                 prompt = f"""Based on the following context, answer the question clearly and concisely.

# #     Context:
# #     {context_text}

# #     Question: {query}

# #     Provide a direct answer based on the context:"""
# #             else:
# #                 prompt = f"""Answer the following question based on your knowledge:

# #     Question: {query}

# #     Provide a clear and helpful answer:"""
            
# #             answer = await self.llm_service.generate(prompt)
            
# #             return {
# #                 "answer": answer,
# #                 "retrieved_chunks": [
# #                     {
# #                         "content": result["document"][:200] + "..." if len(result["document"]) > 200 else result["document"],
# #                         "metadata": result.get("metadata", {}),
# #                         "score": result.get("score", 0.5)
# #                     }
# #                     for result in search_results
# #                 ],
# #                 "confidence": min(0.95, 0.7 + (len(search_results) * 0.05))
# #             }
            
# #         except Exception as e:
# #             logger.error(f"Simple RAG strategy failed: {str(e)}")
# #             answer = await self.llm_service.generate(query)
# #             return {
# #                 "answer": f"{answer}\n\nNote: Used fallback mode due to processing error.",
# #                 "retrieved_chunks": [],
# #                 "confidence": 0.5
# #             }
        
# #     async def _agentic_rag_strategy(self, query: str, context: Dict) -> Dict[str, Any]:
# #         """Agentic RAG implementation with document filtering"""
# #         try:
# #             # Get relevant context with document filtering
# #             query_embedding = self.embedding_service.embed_text(query)
            
# #             # Prepare filter for document_id
# #             filter_params = {}
# #             document_id = context.get("document_id")
# #             if document_id:
# #                 filter_params = {"source": document_id}
# #                 logger.info(f"Agentic search filtering by document_id: {document_id}")
            
# #             search_results = self.vectorstore.search(
# #                 query_embedding=query_embedding,
# #                 top_k=context.get("top_k", 5),
# #                 filter=filter_params
# #             )
            
# #             # Fallback if no results with filter
# #             if not search_results and document_id:
# #                 logger.info("No results with document filter, trying without filter")
# #                 search_results = self.vectorstore.search(
# #                     query_embedding=query_embedding,
# #                     top_k=context.get("top_k", 5)
# #                 )
            
# #             context_text = "\n".join([
# #                 f"- {result['document']}"
# #                 for result in search_results
# #             ])
            
# #             # Enhanced prompt for agentic approach
# #             document_context = f" (from document: {document_id})" if document_id else ""
# #             prompt = f"""You are an AI research assistant. Analyze the question and provided context thoroughly.

# #     CONTEXT FROM KNOWLEDGE BASE{document_context}:
# #     {context_text if context_text.strip() else "No specific context available from knowledge base."}

# #     USER QUESTION: {query}

# #     Please provide a comprehensive answer that:
# #     1. Uses the context if relevant and available
# #     2. Acknowledges what information comes from the context vs. general knowledge
# #     3. Provides a well-structured, detailed response
# #     4. Notes any limitations or missing information

# #     ANSWER:"""
            
# #             answer = await self.llm_service.generate(prompt)
            
# #             return {
# #                 "answer": answer,
# #                 "retrieved_chunks": [
# #                     {
# #                         "content": result["document"][:150] + "..." if len(result["document"]) > 150 else result["document"],
# #                         "metadata": result.get("metadata", {}),
# #                         "score": 1 - result.get("distance", 0)
# #                     }
# #                     for result in search_results
# #                 ],
# #                 "confidence": min(0.9, 0.6 + (len(search_results) * 0.06)),
# #                 "agent_steps": ["context_analysis", "synthesis", "quality_assurance"]
# #             }
            
# #         except Exception as e:
# #             logger.error(f"Agentic RAG strategy failed: {str(e)}")
# #             answer = await self.llm_service.generate(query)
# #             return {
# #                 "answer": f"{answer}\n\nNote: Agentic processing unavailable, used standard response.",
# #                 "retrieved_chunks": [],
# #                 "confidence": 0.4,
# #                 "agent_steps": ["fallback"]
# #             }
    
# #     async def _auto_rag_strategy(self, query: str, context: Dict) -> Dict[str, Any]:
# #         """Auto strategy selector based on query complexity"""
# #         query_lower = query.lower()
        
# #         # Complex queries - use agentic
# #         complex_indicators = [
# #             "analyze", "compare", "evaluate", "critique", "explain in detail",
# #             "what are the advantages", "what are the disadvantages", "pros and cons"
# #         ]
        
# #         # Simple queries - use simple RAG
# #         simple_indicators = [
# #             "what is", "who is", "when was", "where is", "define"
# #         ]
        
# #         if any(indicator in query_lower for indicator in complex_indicators):
# #             logger.info("Auto-selected: agentic strategy (complex query)")
# #             return await self._agentic_rag_strategy(query, context)
# #         elif any(indicator in query_lower for indicator in simple_indicators):
# #             logger.info("Auto-selected: simple strategy (simple query)")
# #             return await self._simple_rag_strategy(query, context)
# #         else:
# #             logger.info("Auto-selected: agentic strategy (default)")
# #             return await self._agentic_rag_strategy(query, context)
    
# #     async def execute_query(
# #         self,
# #         query: str,
# #         top_k: int = 5,
# #         session_id: Optional[str] = None,
# #         document_id: Optional[str] = None,  # Add this parameter
# #         strategy: RAGStrategy = RAGStrategy.AUTO
# #     ) -> Dict[str, Any]:
# #         """Execute RAG query with specified strategy and document filtering"""
# #         start_time = datetime.now()
        
# #         logger.info(f"Executing query: '{query[:50]}...' with strategy: {strategy.value}, document_id: {document_id}")
        
# #         context = {
# #             "top_k": top_k,
# #             "session_id": session_id,
# #             "document_id": document_id,  # Pass to strategy functions
# #             "query": query
# #         }
        
# #         strategy_func = self.strategies.get(strategy, self._auto_rag_strategy)
# #         result = await strategy_func(query, context)
        
# #         processing_time = (datetime.now() - start_time).total_seconds()
        
# #         response = {
# #             "answer": result["answer"],
# #             "strategy_used": strategy,
# #             "retrieved_chunks": result.get("retrieved_chunks", []),
# #             "confidence": result.get("confidence", 0.7),
# #             "processing_time": processing_time
# #         }
        
# #         if "agent_steps" in result:
# #             response["agent_steps"] = result["agent_steps"]
            
# #         logger.info(f"Query completed in {processing_time:.2f}s with {len(response['retrieved_chunks'])} chunks")
        
# #         return response

# #     async def process_document(
# #         self,
# #         filename: str,
# #         content: bytes,
# #         content_type: str
# #     ) -> Dict[str, Any]:
# #         """Process and index document"""
# #         start_time = datetime.now()
        
# #         try:
# #             logger.info(f"Processing document: {filename}")
            
# #             # Extract text
# #             text = ""
# #             if content_type == "application/pdf" or filename.endswith(".pdf"):
# #                 text = self._extract_text_from_pdf(content)
# #             elif content_type == "text/plain" or filename.endswith(".txt"):
# #                 text = content.decode("utf-8")
# #             else:
# #                 try:
# #                     text = content.decode("utf-8")
# #                 except:
# #                     text = "Binary content - text extraction not supported"
            
# #             # Chunk text
# #             chunks = self._chunk_text(text)
            
# #             if chunks:
# #                 # Generate embeddings
# #                 embeddings = self.embedding_service.embed_texts(chunks)
                
# #                 # Generate document ID
# #                 doc_id = str(uuid.uuid4())
                
# #                 # Prepare metadata with document_id
# #                 metadatas = [
# #                     {
# #                         "source": filename,
# #                         "content_type": content_type,
# #                         "chunk_index": i,
# #                         "size": len(chunk),
# #                         "document_id": doc_id  # Add document_id to metadata
# #                     }
# #                     for i, chunk in enumerate(chunks)
# #                 ]
                
# #                 # Generate IDs
# #                 chunk_ids = [f"{doc_id}_chunk_{i}" for i in range(len(chunks))]
                
# #                 # Add to vector store
# #                 self.vectorstore.add_documents(
# #                     documents=chunks,
# #                     embeddings=embeddings,
# #                     metadata=metadatas,
# #                     ids=chunk_ids
# #                 )
                
# #                 processing_time = (datetime.now() - start_time).total_seconds()
                
# #                 return {
# #                     "chunks_created": len(chunks),
# #                     "document_id": doc_id,
# #                     "processing_time": processing_time,
# #                     "method": "vector_store",
# #                     "message": f"Successfully processed {len(chunks)} chunks"
# #                 }
# #             else:
# #                 return {
# #                     "chunks_created": 0,
# #                     "document_id": str(uuid.uuid4()),
# #                     "processing_time": (datetime.now() - start_time).total_seconds(),
# #                     "method": "skip",
# #                     "message": "No text content extracted"
# #                 }
                
# #         except Exception as e:
# #             logger.error(f"Document processing failed: {str(e)}")
# #             return {
# #                 "chunks_created": 0,
# #                 "document_id": str(uuid.uuid4()),
# #                 "processing_time": (datetime.now() - start_time).total_seconds(),
# #                 "method": "error",
# #                 "message": f"Processing failed: {str(e)}"
# #             }
    
# #     def _extract_text_from_pdf(self, content: bytes) -> str:
# #         """Extract text from PDF content"""
# #         try:
# #             import PyPDF2
# #             from io import BytesIO
            
# #             pdf_file = BytesIO(content)
# #             pdf_reader = PyPDF2.PdfReader(pdf_file)
# #             text = ""
# #             for page in pdf_reader.pages:
# #                 text += page.extract_text() + "\n"
# #             return text
# #         except ImportError:
# #             return "PDF text extraction requires PyPDF2. Install with: pip install PyPDF2"
# #         except Exception as e:
# #             return f"PDF extraction error: {str(e)}"
    
# #     def _chunk_text(self, text: str, chunk_size: int = 800, chunk_overlap: int = 100) -> List[str]:
# #         """Simple text chunking implementation"""
# #         if not text or len(text.strip()) == 0:
# #             return []
            
# #         words = text.split()
# #         chunks = []
        
# #         if len(words) <= chunk_size:
# #             return [" ".join(words)]
        
# #         start = 0
# #         while start < len(words):
# #             end = start + chunk_size
# #             chunk = " ".join(words[start:end])
# #             chunks.append(chunk)
            
# #             if end >= len(words):
# #                 break
                
# #             start = end - chunk_overlap
            
# #         return chunks


# # # Global instance
# # _rag_orchestrator = None

# # def get_rag_orchestrator() -> RAGOrchestrator:
# #     """Get the global RAG orchestrator instance"""
# #     global _rag_orchestrator
# #     if _rag_orchestrator is None:
# #         _rag_orchestrator = RAGOrchestrator()
# #     return _rag_orchestrator

# # async def process_query(query_text: str, strategy: str, db: Session):
# #     if strategy == "graph_rag":
# #         context = await graph_rag_query(query_text, db)
# #     elif strategy == "hybrid":
# #         # Combine vector + graph
# #         vector_context = await vector_search(query_text, db)
# #         graph_context = await graph_rag_query(query_text, db)
# #         context = merge_contexts(vector_context, graph_context)
# #     else:
# #         context = await vector_search(query_text, db)
    
# #     # Generate answer using Groq
# #     answer = await generate_answer(query_text, context)
# #     return answer





# """
# Simplified RAG Orchestrator - Minimal Version for Debugging
# """
# import logging
# from typing import Dict, Any, Optional, List
# from datetime import datetime
# import uuid

# from app.core.enums import RAGStrategy

# logger = logging.getLogger(__name__)


# class RAGOrchestrator:
#     """Simplified orchestrator"""
    
#     def __init__(self):
#         logger.info("Initializing RAG Orchestrator...")
        
#         from app.core.dependencies import get_llm_service, get_embedding_service, get_vectorstore
        
#         self.llm_service = get_llm_service()
#         self.embedding_service = get_embedding_service() 
#         self.vectorstore = get_vectorstore()
        
#         self.strategies = {
#             RAGStrategy.SIMPLE: self._simple_rag_strategy,
#             RAGStrategy.AGENTIC: self._agentic_rag_strategy,
#             RAGStrategy.AUTO: self._auto_rag_strategy
#         }
        
#         logger.info("[OK] RAG Orchestrator initialized")
    
#     async def _simple_rag_strategy(self, query: str, context: Dict) -> Dict[str, Any]:
#         """Simple RAG - no exceptions, plain execution"""
#         # Get basic info
#         doc_count = self.vectorstore.get_count()
#         document_id = context.get("document_id")
#         top_k = context.get("top_k", 5)
        
#         print(f"\n{'='*80}")
#         print(f"[SIMPLE RAG EXECUTION]")
#         print(f"Vector Store Count: {doc_count}")
#         print(f"Vector Store Type: {type(self.vectorstore)}")
#         print(f"Vector Store Methods: {[method for method in dir(self.vectorstore) if not method.startswith('_')]}")
#         print(f"Query: {query}")
#         print(f"Document ID: {document_id}")
#         print(f"Top K: {top_k}")
#         print(f"{'='*80}\n")
        
#         # Check if search_by_embedding exists
#         if not hasattr(self.vectorstore, 'search_by_embedding'):
#             print("[ERROR] search_by_embedding method not found!")
#             print(f"Available methods: {[method for method in dir(self.vectorstore) if not method.startswith('_')]}")
#             answer = await self.llm_service.generate(query)
#             return {
#                 "answer": f"{answer}\n\n[DEBUG: Vector store method missing]",
#                 "retrieved_chunks": [],
#                 "confidence": 0.3
#             }
        
#         # Generate embedding
#         print("Generating embedding...")
#         query_embedding = self.embedding_service.embed_text(query)
#         print(f"Embedding dimension: {len(query_embedding)}")
        
#         # Prepare filter
#         filter_params = {"document_id": document_id} if document_id else None
#         print(f"Filter params: {filter_params}")
        
#         # Search
#         print("Searching vector store...")
#         search_results = self.vectorstore.search_by_embedding(
#             query_embedding=query_embedding,
#             top_k=top_k,
#             filter=filter_params
#         )
        
#         print(f"Search results: {len(search_results)} chunks found")
        
#         # If no results with filter, try without
#         if not search_results and document_id:
#             print("No results with filter, trying without filter...")
#             search_results = self.vectorstore.search_by_embedding(
#                 query_embedding=query_embedding,
#                 top_k=top_k,
#                 filter=None
#             )
#             print(f"Search without filter: {len(search_results)} chunks found")
        
#         # Show first result
#         if search_results:
#             print(f"\nFirst result:")
#             print(f"  Metadata: {search_results[0].get('metadata')}")
#             print(f"  Score: {search_results[0].get('score')}")
#             print(f"  Content preview: {search_results[0].get('document', '')[:100]}...")
#         else:
#             print("WARNING: No search results found!")
        
#         # Build context
#         context_text = "\n\n".join([
#             f"[Chunk {i+1}]: {result['document']}"
#             for i, result in enumerate(search_results[:3])
#         ])
        
#         # Generate answer
#         if context_text.strip():
#             prompt = f"""Based on the following context, answer the question.

# Context:
# {context_text}

# Question: {query}

# Answer:"""
#         else:
#             prompt = f"Answer this question: {query}"
        
#         print("Generating answer...")
#         answer = await self.llm_service.generate(prompt)
#         print(f"Answer generated ({len(answer)} chars)")
        
#         return {
#             "answer": answer,
#             "retrieved_chunks": [
#                 {
#                     "content": result["document"][:200] + "...",
#                     "metadata": result.get("metadata", {}),
#                     "score": result.get("score", 0.5)
#                 }
#                 for result in search_results
#             ],
#             "confidence": min(0.95, 0.7 + (len(search_results) * 0.05))
#         }
    
#     async def _agentic_rag_strategy(self, query: str, context: Dict) -> Dict[str, Any]:
#         """Agentic RAG - with detailed logging"""
#         doc_count = self.vectorstore.get_count()
#         document_id = context.get("document_id")
#         top_k = context.get("top_k", 5)
        
#         print(f"\n{'='*80}")
#         print(f"[AGENTIC RAG EXECUTION]")
#         print(f"Vector Store Count: {doc_count}")
#         print(f"Query: {query}")
#         print(f"Document ID: {document_id}")
#         print(f"Top K: {top_k}")
#         print(f"{'='*80}\n")
        
#         # Check if vector store is empty
#         if doc_count == 0:
#             print("[ERROR] Vector store is empty!")
#             answer = await self.llm_service.generate(query)
#             return {
#                 "answer": f"{answer}\n\n[DEBUG: Vector store is empty - no documents indexed]",
#                 "retrieved_chunks": [],
#                 "confidence": 0.3,
#                 "agent_steps": ["fallback"]
#             }
        
#         # If document_id provided, verify it exists
#         if document_id:
#             doc_chunks = self.vectorstore.get_documents_by_id(document_id)
#             print(f"Document verification: {len(doc_chunks)} chunks found for document_id={document_id}")
            
#             if len(doc_chunks) == 0:
#                 print(f"[WARNING] No chunks found for document_id={document_id}")
#                 print("Available document_ids in vector store:")
#                 unique_ids = set(m.get('document_id') for m in self.vectorstore.metadata if m.get('document_id'))
#                 for uid in list(unique_ids)[:5]:
#                     print(f"  - {uid}")
        
#         # Generate embedding
#         print("Generating embedding...")
#         query_embedding = self.embedding_service.embed_text(query)
#         print(f"Embedding dimension: {len(query_embedding)}")
        
#         # Search with filter
#         filter_params = {"document_id": document_id} if document_id else None
#         print(f"Searching with filter: {filter_params}")
        
#         search_results = self.vectorstore.search_by_embedding(
#             query_embedding=query_embedding,
#             top_k=top_k,
#             filter=filter_params
#         )
        
#         print(f"Search results: {len(search_results)} chunks found")
        
#         # Fallback without filter
#         if not search_results and document_id:
#             print("No results with filter, trying without filter...")
#             search_results = self.vectorstore.search_by_embedding(
#                 query_embedding=query_embedding,
#                 top_k=top_k,
#                 filter=None
#             )
#             print(f"Search without filter: {len(search_results)} chunks found")
        
#         # Show results
#         if search_results:
#             print(f"\nFirst result:")
#             print(f"  Metadata: {search_results[0].get('metadata')}")
#             print(f"  Score: {search_results[0].get('score')}")
#             print(f"  Content: {search_results[0].get('document', '')[:150]}...")
        
#         # Build context
#         context_text = "\n".join([
#             f"- {result['document']}"
#             for result in search_results
#         ])
        
#         # Generate answer
#         doc_context = f" (from document: {document_id})" if document_id else ""
#         prompt = f"""You are an AI assistant. Answer the question using the context provided.

# CONTEXT{doc_context}:
# {context_text if context_text.strip() else "No context available."}

# QUESTION: {query}

# Provide a comprehensive answer based on the context:"""
        
#         print("Generating answer...")
#         answer = await self.llm_service.generate(prompt)
#         print(f"Answer generated ({len(answer)} chars)")
        
#         return {
#             "answer": answer,
#             "retrieved_chunks": [
#                 {
#                     "content": result["document"][:150] + "...",
#                     "metadata": result.get("metadata", {}),
#                     "score": result.get("score", 0.5)
#                 }
#                 for result in search_results
#             ],
#             "confidence": min(0.9, 0.6 + (len(search_results) * 0.06)),
#             "agent_steps": ["context_analysis", "synthesis", "quality_assurance"]
#         }
    
#     async def _auto_rag_strategy(self, query: str, context: Dict) -> Dict[str, Any]:
#         """Auto selector"""
#         query_lower = query.lower()
        
#         if "who is" in query_lower or "what are" in query_lower:
#             return await self._agentic_rag_strategy(query, context)
#         else:
#             return await self._simple_rag_strategy(query, context)
    
#     async def execute_query(
#         self,
#         query: str,
#         top_k: int = 5,
#         session_id: Optional[str] = None,
#         document_id: Optional[str] = None,
#         strategy: RAGStrategy = RAGStrategy.AUTO
#     ) -> Dict[str, Any]:
#         """Execute query"""
#         start_time = datetime.now()
        
#         context = {
#             "top_k": top_k,
#             "session_id": session_id,
#             "document_id": document_id,
#             "query": query
#         }
        
#         strategy_func = self.strategies.get(strategy, self._auto_rag_strategy)
#         result = await strategy_func(query, context)
        
#         processing_time = (datetime.now() - start_time).total_seconds()
        
#         return {
#             "answer": result["answer"],
#             "strategy_used": strategy,
#             "retrieved_chunks": result.get("retrieved_chunks", []),
#             "confidence": result.get("confidence", 0.7),
#             "processing_time": processing_time,
#             **({k: v for k, v in result.items() if k in ["agent_steps"]})
#         }

#     async def process_document(
#         self,
#         filename: str,
#         content: bytes,
#         content_type: str
#     ) -> Dict[str, Any]:
#         """Process document"""
#         start_time = datetime.now()
        
#         print(f"\n{'='*80}")
#         print(f"[DOCUMENT PROCESSING]")
#         print(f"Filename: {filename}")
#         print(f"Content type: {content_type}")
#         print(f"Size: {len(content)} bytes")
#         print(f"{'='*80}\n")
        
#         # Extract text
#         text = ""
#         if content_type == "application/pdf" or filename.endswith(".pdf"):
#             text = self._extract_text_from_pdf(content)
#         elif content_type == "text/plain" or filename.endswith(".txt"):
#             text = content.decode("utf-8")
#         else:
#             try:
#                 text = content.decode("utf-8")
#             except:
#                 text = "Binary content"
        
#         print(f"Extracted text: {len(text)} characters")
        
#         # Chunk
#         chunks = self._chunk_text(text)
#         print(f"Created: {len(chunks)} chunks")
        
#         if not chunks:
#             return {
#                 "chunks_created": 0,
#                 "document_id": str(uuid.uuid4()),
#                 "processing_time": (datetime.now() - start_time).total_seconds(),
#                 "method": "skip",
#                 "message": "No text extracted"
#             }
        
#         # Generate document ID
#         doc_id = str(uuid.uuid4())
#         print(f"Document ID: {doc_id}")
        
#         # Generate embeddings
#         print("Generating embeddings...")
#         embeddings = self.embedding_service.embed_texts(chunks)
#         print(f"Generated {len(embeddings)} embeddings")
        
#         # Prepare metadata
#         metadatas = [
#             {
#                 "source": filename,
#                 "content_type": content_type,
#                 "chunk_index": i,
#                 "size": len(chunk),
#                 "document_id": doc_id
#             }
#             for i, chunk in enumerate(chunks)
#         ]
        
#         print(f"Sample metadata: {metadatas[0]}")
        
#         # Add to vector store
#         print(f"Adding {len(chunks)} documents to vector store...")
#         self.vectorstore.add_documents(
#             documents=chunks,
#             embeddings=embeddings,
#             metadata=metadatas,
#             ids=[f"{doc_id}_chunk_{i}" for i in range(len(chunks))]
#         )
        
#         # Verify
#         total = self.vectorstore.get_count()
#         verify = self.vectorstore.get_documents_by_id(doc_id)
#         print(f"Vector store total: {total}")
#         print(f"Verification: {len(verify)} chunks found for {doc_id}")
        
#         if len(verify) != len(chunks):
#             print(f"[WARNING] Mismatch! Added {len(chunks)} but found {len(verify)}")
        
#         processing_time = (datetime.now() - start_time).total_seconds()
        
#         print(f"{'='*80}\n")
        
#         return {
#             "chunks_created": len(chunks),
#             "document_id": doc_id,
#             "processing_time": processing_time,
#             "method": "vector_store",
#             "message": f"Successfully processed {len(chunks)} chunks"
#         }
    
#     def _extract_text_from_pdf(self, content: bytes) -> str:
#         """Extract PDF text"""
#         try:
#             import PyPDF2
#             from io import BytesIO
            
#             pdf_file = BytesIO(content)
#             pdf_reader = PyPDF2.PdfReader(pdf_file)
#             text = ""
#             for page in pdf_reader.pages:
#                 text += page.extract_text() + "\n"
#             return text
#         except Exception as e:
#             return f"PDF extraction error: {str(e)}"
    
#     def _chunk_text(self, text: str, chunk_size: int = 800, chunk_overlap: int = 100) -> List[str]:
#         """Chunk text"""
#         if not text or len(text.strip()) == 0:
#             return []
            
#         words = text.split()
#         if len(words) <= chunk_size:
#             return [" ".join(words)]
        
#         chunks = []
#         start = 0
#         while start < len(words):
#             end = start + chunk_size
#             chunk = " ".join(words[start:end])
#             chunks.append(chunk)
            
#             if end >= len(words):
#                 break
#             start = end - chunk_overlap
            
#         return chunks


# # Global instance
# _rag_orchestrator = None

# def get_rag_orchestrator() -> RAGOrchestrator:
#     """Get singleton"""
#     global _rag_orchestrator
#     if _rag_orchestrator is None:
#         _rag_orchestrator = RAGOrchestrator()
#     return _rag_orchestrator






"""
Enhanced RAG Orchestrator with Intelligent Fallback
Checks vector DB first, falls back to LLM general knowledge if not relevant
"""
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid

from app.core.enums import RAGStrategy

logger = logging.getLogger(__name__)


class RAGOrchestrator:
    """
    Enhanced RAG Orchestrator with intelligent fallback:
    1. Search vector database first
    2. Check relevance of results (score threshold)
    3. If not relevant, use LLM general knowledge
    4. Generate answer from best available source
    """
    
    def __init__(self, relevance_threshold: float = 0.30):
        logger.info("Initializing Enhanced RAG Orchestrator...")
        
        from app.core.dependencies import get_llm_service, get_embedding_service, get_vectorstore
        
        self.llm_service = get_llm_service()
        self.embedding_service = get_embedding_service() 
        self.vectorstore = get_vectorstore()
        self.relevance_threshold = relevance_threshold
        
        self.strategies = {
            RAGStrategy.SIMPLE: self._simple_rag_strategy,
            RAGStrategy.AGENTIC: self._agentic_rag_strategy,
            RAGStrategy.AUTO: self._auto_rag_strategy
        }
        
        logger.info(f"[OK] Enhanced RAG Orchestrator initialized (threshold: {relevance_threshold})")
    
    def _check_relevance(self, search_results: List[Dict]) -> tuple:
        """
        Check if search results are relevant
        Returns: (is_relevant: bool, max_score: float, avg_score: float)
        """
        if not search_results:
            return False, 0.0, 0.0
        
        scores = [result.get("score", 0.0) for result in search_results]
        max_score = max(scores)
        avg_score = sum(scores) / len(scores)
        
        is_relevant = max_score >= self.relevance_threshold
        
        logger.info(f"[RELEVANCE CHECK] Max: {max_score:.4f}, Avg: {avg_score:.4f}, Threshold: {self.relevance_threshold}, Relevant: {is_relevant}")
        
        return is_relevant, max_score, avg_score
    
    async def _simple_rag_strategy(self, query: str, context: Dict) -> Dict[str, Any]:
        """Simple RAG with intelligent fallback"""
        doc_count = self.vectorstore.get_count()
        document_id = context.get("document_id")
        top_k = context.get("top_k", 5)
        
        logger.info(f"[SIMPLE RAG] Query: {query[:100]}...")
        logger.info(f"[SIMPLE RAG] Vector store: {doc_count} docs, Document ID: {document_id}, Top K: {top_k}")
        
        # Step 1: Generate embedding
        query_embedding = self.embedding_service.embed_text(query)
        
        # Step 2: Search vector database
        filter_params = {"document_id": document_id} if document_id else None
        search_results = self.vectorstore.search_by_embedding(
            query_embedding=query_embedding,
            top_k=top_k,
            filter=filter_params
        )
        
        logger.info(f"[SIMPLE RAG] Retrieved {len(search_results)} chunks")
        
        # Step 3: Check relevance
        is_relevant, max_score, avg_score = self._check_relevance(search_results)
        
        # Step 4: Generate answer based on source
        if is_relevant:
            # Use vector database
            logger.info(f"[SOURCE] Using VECTOR DATABASE (max score: {max_score:.4f})")
            
            context_text = "\n\n".join([
                f"[Source {i+1}]: {result['document']}"
                for i, result in enumerate(search_results[:3])
            ])
            
            system_prompt = """You are a helpful AI assistant. Answer questions based on the provided context.
Be concise, accurate, and cite sources when relevant."""
            
            user_prompt = f"""Context from documents:
{context_text}

Question: {query}

Provide a detailed answer based on the context above:"""
            
            answer = await self.llm_service.generate(
                prompt=user_prompt,
                system_prompt=system_prompt
            )
            
            source_note = "✅ Answer based on your uploaded documents"
            
        else:
            # Fallback to general knowledge
            logger.info(f"[SOURCE] Using GENERAL KNOWLEDGE (max score: {max_score:.4f} below threshold)")
            
            system_prompt = """You are a knowledgeable AI assistant with expertise across many domains.
Provide accurate, comprehensive answers based on your general knowledge."""
            
            user_prompt = f"""Question: {query}

Please provide a detailed, accurate answer based on your general knowledge.
Structure your answer clearly with relevant details and examples where appropriate."""
            
            answer = await self.llm_service.generate(
                prompt=user_prompt,
                system_prompt=system_prompt
            )
            
            # Add informative note
            source_note = f"""ℹ️ **Information Source**: This answer is based on general knowledge.

**Why?** No relevant documents were found in your database (relevance score: {max_score:.2f}, threshold: {self.relevance_threshold}).

**💡 Tip**: Upload documents about "{query}" to get answers specific to your content."""
            
            answer = f"{answer}\n\n---\n{source_note}"
            
            # Clear search results for general knowledge answers
            search_results = []
        
        return {
            "answer": answer,
            "retrieved_chunks": [
                {
                    "content": result["document"][:200] + "...",
                    "metadata": result.get("metadata", {}),
                    "score": result.get("score", 0.5)
                }
                for result in search_results
            ],
            "confidence": max_score if is_relevant else 0.7,
            "source": "vector_database" if is_relevant else "general_knowledge",
            "fallback_used": not is_relevant,
            "max_relevance_score": max_score
        }
    
    async def _agentic_rag_strategy(self, query: str, context: Dict) -> Dict[str, Any]:
        """Agentic RAG with intelligent fallback and detailed reasoning"""
        doc_count = self.vectorstore.get_count()
        document_id = context.get("document_id")
        top_k = context.get("top_k", 8)
        
        logger.info(f"[AGENTIC RAG] Query: {query[:100]}...")
        logger.info(f"[AGENTIC RAG] Vector store: {doc_count} docs, Document ID: {document_id}")
        
        # Step 1: Generate embedding
        query_embedding = self.embedding_service.embed_text(query)
        
        # Step 2: Search vector database
        filter_params = {"document_id": document_id} if document_id else None
        search_results = self.vectorstore.search_by_embedding(
            query_embedding=query_embedding,
            top_k=top_k,
            filter=filter_params
        )
        
        logger.info(f"[AGENTIC RAG] Retrieved {len(search_results)} chunks")
        
        # Step 3: Check relevance
        is_relevant, max_score, avg_score = self._check_relevance(search_results)
        
        # Step 4: Generate answer with agent reasoning
        if is_relevant:
            # Use vector database with agent reasoning
            logger.info(f"[SOURCE] Using VECTOR DATABASE with agent reasoning (max score: {max_score:.4f})")
            
            # Build rich context
            context_parts = []
            for i, result in enumerate(search_results[:5], 1):
                metadata = result.get("metadata", {})
                source = metadata.get("source", "Unknown")
                score = result.get("score", 0)
                content = result["document"]
                
                context_parts.append(f"""[Document {i} - {source} (relevance: {score:.2f})]
{content}
""")
            
            context_text = "\n".join(context_parts)
            
            system_prompt = """You are an expert AI assistant that provides comprehensive, well-reasoned answers.

Your approach:
1. Analyze the provided context carefully
2. Extract key information relevant to the question
3. Synthesize a clear, detailed answer
4. Cite specific sources when making claims
5. Acknowledge any limitations or uncertainties

Be thorough, accurate, and helpful."""
            
            user_prompt = f"""Context from documents:
{context_text}

Question: {query}

Please provide a comprehensive answer following these steps:
1. Analyze what the context tells us about this question
2. Synthesize the information into a clear answer
3. Include relevant details and examples
4. Cite sources where appropriate"""
            
            answer = await self.llm_service.generate(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.7,
                max_tokens=2000
            )
            
            # Add metadata footer
            doc_sources = set(r.get("metadata", {}).get("source", "Unknown") for r in search_results[:5])
            footer = f"\n\n---\n✅ **Sources**: Based on {len(search_results)} relevant chunks from: {', '.join(list(doc_sources)[:3])}"
            answer = f"{answer}{footer}"
            
            source_note = "vector_database"
            agent_steps = ["context_analysis", "information_synthesis", "answer_generation", "quality_assurance"]
            
        else:
            # Fallback to general knowledge with agent reasoning
            logger.info(f"[SOURCE] Using GENERAL KNOWLEDGE with agent reasoning (max score: {max_score:.4f})")
            
            system_prompt = """You are an expert AI assistant with broad knowledge across many domains.

Your approach:
1. Understand the question thoroughly
2. Draw on your general knowledge
3. Provide accurate, well-structured information
4. Include relevant examples and context
5. Be clear about the nature of the information (general vs specific)

Be comprehensive, accurate, and educational."""
            
            user_prompt = f"""Question: {query}

Please provide a detailed answer using your general knowledge:
1. Explain the topic clearly
2. Include relevant details and examples
3. Organize information logically
4. Mention any important related concepts"""
            
            answer = await self.llm_service.generate(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.7,
                max_tokens=2000
            )
            
            # Add detailed informative note
            source_note = f"""

---
ℹ️ **Information Source**: General Knowledge

**Analysis**: 
- Searched your document database ({doc_count} documents indexed)
- Found {len(search_results)} potential matches
- Highest relevance score: {max_score:.2f} (threshold: {self.relevance_threshold})
- **Conclusion**: No sufficiently relevant documents found

**💡 Recommendation**: To get answers specific to your documents, try:
1. Uploading documents related to: "{query}"
2. Using more specific keywords that match your document content
3. Checking if documents were successfully indexed

This answer is based on general AI knowledge and may not reflect your specific context."""
            
            answer = f"{answer}{source_note}"
            
            # Clear results for general knowledge
            search_results = []
            source_note = "general_knowledge"
            agent_steps = ["query_analysis", "vector_search", "relevance_check", "fallback_to_general_knowledge", "answer_generation"]
        
        return {
            "answer": answer,
            "retrieved_chunks": [
                {
                    "content": result["document"][:200] + "...",
                    "metadata": result.get("metadata", {}),
                    "score": result.get("score", 0.5)
                }
                for result in search_results
            ],
            "confidence": max_score if is_relevant else 0.75,
            "source": source_note,
            "fallback_used": not is_relevant,
            "max_relevance_score": max_score,
            "agent_steps": agent_steps
        }
    
    async def _auto_rag_strategy(self, query: str, context: Dict) -> Dict[str, Any]:
        """Auto-select strategy based on query complexity"""
        query_lower = query.lower()
        
        # Use agentic for complex queries
        complex_indicators = ["who is", "what are", "explain", "describe", "how does", "why", "analyze"]
        
        if any(indicator in query_lower for indicator in complex_indicators):
            logger.info("[AUTO] Selected AGENTIC strategy")
            return await self._agentic_rag_strategy(query, context)
        else:
            logger.info("[AUTO] Selected SIMPLE strategy")
            return await self._simple_rag_strategy(query, context)
    
    async def execute_query(
        self,
        query: str,
        top_k: int = 5,
        session_id: Optional[str] = None,
        document_id: Optional[str] = None,
        strategy: RAGStrategy = RAGStrategy.AUTO
    ) -> Dict[str, Any]:
        """Execute query with intelligent fallback"""
        start_time = datetime.now()
        
        logger.info(f"\n{'='*80}")
        logger.info(f"[EXECUTE QUERY] {query}")
        logger.info(f"[PARAMETERS] Strategy: {strategy.value}, Top-K: {top_k}, Document ID: {document_id}")
        logger.info(f"{'='*80}")
        
        context = {
            "top_k": top_k,
            "session_id": session_id,
            "document_id": document_id,
            "query": query
        }
        
        strategy_func = self.strategies.get(strategy, self._auto_rag_strategy)
        result = await strategy_func(query, context)
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        logger.info(f"[COMPLETED] Time: {processing_time:.2f}s, Source: {result.get('source', 'unknown')}, Fallback: {result.get('fallback_used', False)}")
        
        return {
            "answer": result["answer"],
            "strategy_used": strategy,
            "retrieved_chunks": result.get("retrieved_chunks", []),
            "confidence": result.get("confidence", 0.7),
            "processing_time": processing_time,
            "source": result.get("source", "vector_database"),
            "fallback_used": result.get("fallback_used", False),
            "max_relevance_score": result.get("max_relevance_score", 0.0),
            **({k: v for k, v in result.items() if k in ["agent_steps"]})
        }

    async def process_document(
        self,
        filename: str,
        content: bytes,
        content_type: str
    ) -> Dict[str, Any]:
        """Process and index document"""
        start_time = datetime.now()
        
        logger.info(f"\n{'='*80}")
        logger.info(f"[DOCUMENT PROCESSING] {filename}")
        logger.info(f"[INFO] Type: {content_type}, Size: {len(content)} bytes")
        logger.info(f"{'='*80}")
        
        # Extract text
        text = ""
        if content_type == "application/pdf" or filename.endswith(".pdf"):
            text = self._extract_text_from_pdf(content)
        elif content_type == "text/plain" or filename.endswith(".txt"):
            text = content.decode("utf-8")
        else:
            try:
                text = content.decode("utf-8")
            except:
                text = "Binary content - unable to extract text"
        
        logger.info(f"[EXTRACTED] {len(text)} characters")
        
        # Chunk text
        chunks = self._chunk_text(text)
        logger.info(f"[CHUNKED] {len(chunks)} chunks created")
        
        if not chunks:
            logger.warning("[SKIP] No text extracted from document")
            return {
                "chunks_created": 0,
                "document_id": str(uuid.uuid4()),
                "processing_time": (datetime.now() - start_time).total_seconds(),
                "method": "skip",
                "message": "No text content found in document"
            }
        
        # Generate document ID
        doc_id = str(uuid.uuid4())
        logger.info(f"[DOCUMENT ID] {doc_id}")
        
        # Generate embeddings
        logger.info("[EMBEDDING] Generating embeddings...")
        embeddings = self.embedding_service.embed_texts(chunks)
        logger.info(f"[EMBEDDING] Generated {len(embeddings)} embeddings")
        
        # Prepare metadata
        metadatas = [
            {
                "source": filename,
                "content_type": content_type,
                "chunk_index": i,
                "size": len(chunk),
                "document_id": doc_id
            }
            for i, chunk in enumerate(chunks)
        ]
        
        # Add to vector store
        logger.info(f"[INDEXING] Adding {len(chunks)} chunks to vector store...")
        self.vectorstore.add_documents(
            documents=chunks,
            embeddings=embeddings,
            metadata=metadatas,
            ids=[f"{doc_id}_chunk_{i}" for i in range(len(chunks))]
        )
        
        # Verify
        total_docs = self.vectorstore.get_count()
        verification = self.vectorstore.get_documents_by_id(doc_id)
        logger.info(f"[VERIFICATION] Total docs in store: {total_docs}, Document chunks: {len(verification)}")
        
        if len(verification) != len(chunks):
            logger.warning(f"[MISMATCH] Expected {len(chunks)} chunks, found {len(verification)}")
        
        processing_time = (datetime.now() - start_time).total_seconds()
        logger.info(f"[SUCCESS] Processed in {processing_time:.2f}s")
        logger.info(f"{'='*80}\n")
        
        return {
            "chunks_created": len(chunks),
            "document_id": doc_id,
            "processing_time": processing_time,
            "method": "vector_store",
            "message": f"Successfully indexed {len(chunks)} chunks"
        }
    
    def _extract_text_from_pdf(self, content: bytes) -> str:
        """Extract text from PDF"""
        try:
            import PyPDF2
            from io import BytesIO
            
            pdf_file = BytesIO(content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            logger.error(f"[ERROR] PDF extraction failed: {str(e)}")
            return f"Error extracting PDF: {str(e)}"
    
    def _chunk_text(self, text: str, chunk_size: int = 800, chunk_overlap: int = 100) -> List[str]:
        """Chunk text with overlap"""
        if not text or len(text.strip()) == 0:
            return []
        
        words = text.split()
        if len(words) <= chunk_size:
            return [" ".join(words)]
        
        chunks = []
        start = 0
        while start < len(words):
            end = start + chunk_size
            chunk = " ".join(words[start:end])
            chunks.append(chunk)
            
            if end >= len(words):
                break
            start = end - chunk_overlap
        
        return chunks


# ============================================
# Global Singleton
# ============================================

_rag_orchestrator = None

def get_rag_orchestrator(relevance_threshold: float = 0.30) -> RAGOrchestrator:
    """Get singleton RAG orchestrator with configurable threshold"""
    global _rag_orchestrator
    if _rag_orchestrator is None:
        _rag_orchestrator = RAGOrchestrator(relevance_threshold=relevance_threshold)
    return _rag_orchestrator