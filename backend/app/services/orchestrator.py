# """
# Enhanced RAG Orchestrator with Intelligent Fallback
# Checks vector DB first, falls back to LLM general knowledge if not relevant
# """
# import logging
# from typing import Dict, Any, Optional, List
# from datetime import datetime
# import uuid

# from app.core.enums import RAGStrategy

# logger = logging.getLogger(__name__)


# class RAGOrchestrator:
#     """
#     Enhanced RAG Orchestrator with intelligent fallback:
#     1. Search vector database first
#     2. Check relevance of results (score threshold)
#     3. If not relevant, use LLM general knowledge
#     4. Generate answer from best available source
#     """
    
#     def __init__(self, relevance_threshold: float = 0.30):
#         logger.info("Initializing Enhanced RAG Orchestrator...")
        
#         from app.core.dependencies import get_llm_service, get_embedding_service, get_vectorstore
        
#         self.llm_service = get_llm_service()
#         self.embedding_service = get_embedding_service() 
#         self.vectorstore = get_vectorstore()
#         self.relevance_threshold = relevance_threshold
        
#         self.strategies = {
#             RAGStrategy.SIMPLE: self._simple_rag_strategy,
#             RAGStrategy.AGENTIC: self._agentic_rag_strategy,
#             RAGStrategy.AUTO: self._auto_rag_strategy
#         }
        
#         logger.info(f"[OK] Enhanced RAG Orchestrator initialized (threshold: {relevance_threshold})")
    
#     def _check_relevance(self, search_results: List[Dict]) -> tuple:
#         """
#         Check if search results are relevant
#         Returns: (is_relevant: bool, max_score: float, avg_score: float)
#         """
#         if not search_results:
#             return False, 0.0, 0.0
        
#         scores = [result.get("score", 0.0) for result in search_results]
#         max_score = max(scores)
#         avg_score = sum(scores) / len(scores)
        
#         is_relevant = max_score >= self.relevance_threshold
        
#         logger.info(f"[RELEVANCE CHECK] Max: {max_score:.4f}, Avg: {avg_score:.4f}, Threshold: {self.relevance_threshold}, Relevant: {is_relevant}")
        
#         return is_relevant, max_score, avg_score
    
#     async def _simple_rag_strategy(self, query: str, context: Dict) -> Dict[str, Any]:
#         """Simple RAG with intelligent fallback"""
#         doc_count = self.vectorstore.get_count()
#         document_id = context.get("document_id")
#         top_k = context.get("top_k", 5)
        
#         logger.info(f"[SIMPLE RAG] Query: {query[:100]}...")
#         logger.info(f"[SIMPLE RAG] Vector store: {doc_count} docs, Document ID: {document_id}, Top K: {top_k}")
        
#         # Step 1: Generate embedding
#         query_embedding = self.embedding_service.embed_text(query)
        
#         # Step 2: Search vector database
#         filter_params = {"document_id": document_id} if document_id else None
#         search_results = self.vectorstore.search_by_embedding(
#             query_embedding=query_embedding,
#             top_k=top_k,
#             filter=filter_params
#         )
        
#         logger.info(f"[SIMPLE RAG] Retrieved {len(search_results)} chunks")
        
#         # Step 3: Check relevance
#         is_relevant, max_score, avg_score = self._check_relevance(search_results)
        
#         # Step 4: Generate answer based on source
#         if is_relevant:
#             # Use vector database
#             logger.info(f"[SOURCE] Using VECTOR DATABASE (max score: {max_score:.4f})")
            
#             context_text = "\n\n".join([
#                 f"[Source {i+1}]: {result['document']}"
#                 for i, result in enumerate(search_results[:3])
#             ])
            
#             system_prompt = """You are a helpful AI assistant. Answer questions based on the provided context.
# Be concise, accurate, and cite sources when relevant."""
            
#             user_prompt = f"""Context from documents:
# {context_text}

# Question: {query}

# Provide a detailed answer based on the context above:"""
            
#             answer = await self.llm_service.generate(
#                 prompt=user_prompt,
#                 system_prompt=system_prompt
#             )
            
#             source_note = "✅ Answer based on your uploaded documents"
            
#         else:
#             # Fallback to general knowledge
#             logger.info(f"[SOURCE] Using GENERAL KNOWLEDGE (max score: {max_score:.4f} below threshold)")
            
#             system_prompt = """You are a knowledgeable AI assistant with expertise across many domains.
# Provide accurate, comprehensive answers based on your general knowledge."""
            
#             user_prompt = f"""Question: {query}

# Please provide a detailed, accurate answer based on your general knowledge.
# Structure your answer clearly with relevant details and examples where appropriate."""
            
#             answer = await self.llm_service.generate(
#                 prompt=user_prompt,
#                 system_prompt=system_prompt
#             )
            
#             # Add informative note
#             source_note = f"""ℹ️ **Information Source**: This answer is based on general knowledge.

# **Why?** No relevant documents were found in your database (relevance score: {max_score:.2f}, threshold: {self.relevance_threshold}).

# **💡 Tip**: Upload documents about "{query}" to get answers specific to your content."""
            
#             answer = f"{answer}\n\n---\n{source_note}"
            
#             # Clear search results for general knowledge answers
#             search_results = []
        
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
#             "confidence": max_score if is_relevant else 0.7,
#             "source": "vector_database" if is_relevant else "general_knowledge",
#             "fallback_used": not is_relevant,
#             "max_relevance_score": max_score
#         }
    
#     async def _agentic_rag_strategy(self, query: str, context: Dict) -> Dict[str, Any]:
#         """Agentic RAG with intelligent fallback and detailed reasoning"""
#         doc_count = self.vectorstore.get_count()
#         document_id = context.get("document_id")
#         top_k = context.get("top_k", 8)
        
#         logger.info(f"[AGENTIC RAG] Query: {query[:100]}...")
#         logger.info(f"[AGENTIC RAG] Vector store: {doc_count} docs, Document ID: {document_id}")
        
#         # Step 1: Generate embedding
#         query_embedding = self.embedding_service.embed_text(query)
        
#         # Step 2: Search vector database
#         filter_params = {"document_id": document_id} if document_id else None
#         search_results = self.vectorstore.search_by_embedding(
#             query_embedding=query_embedding,
#             top_k=top_k,
#             filter=filter_params
#         )
        
#         logger.info(f"[AGENTIC RAG] Retrieved {len(search_results)} chunks")
        
#         # Step 3: Check relevance
#         is_relevant, max_score, avg_score = self._check_relevance(search_results)
        
#         # Step 4: Generate answer with agent reasoning
#         if is_relevant:
#             # Use vector database with agent reasoning
#             logger.info(f"[SOURCE] Using VECTOR DATABASE with agent reasoning (max score: {max_score:.4f})")
            
#             # Build rich context
#             context_parts = []
#             for i, result in enumerate(search_results[:5], 1):
#                 metadata = result.get("metadata", {})
#                 source = metadata.get("source", "Unknown")
#                 score = result.get("score", 0)
#                 content = result["document"]
                
#                 context_parts.append(f"""[Document {i} - {source} (relevance: {score:.2f})]
# {content}
# """)
            
#             context_text = "\n".join(context_parts)
            
#             system_prompt = """You are an expert AI assistant that provides comprehensive, well-reasoned answers.

# Your approach:
# 1. Analyze the provided context carefully
# 2. Extract key information relevant to the question
# 3. Synthesize a clear, detailed answer
# 4. Cite specific sources when making claims
# 5. Acknowledge any limitations or uncertainties

# Be thorough, accurate, and helpful."""
            
#             user_prompt = f"""Context from documents:
# {context_text}

# Question: {query}

# Please provide a comprehensive answer following these steps:
# 1. Analyze what the context tells us about this question
# 2. Synthesize the information into a clear answer
# 3. Include relevant details and examples
# 4. Cite sources where appropriate"""
            
#             answer = await self.llm_service.generate(
#                 prompt=user_prompt,
#                 system_prompt=system_prompt,
#                 temperature=0.7,
#                 max_tokens=2000
#             )
            
#             # Add metadata footer
#             doc_sources = set(r.get("metadata", {}).get("source", "Unknown") for r in search_results[:5])
#             footer = f"\n\n---\n✅ **Sources**: Based on {len(search_results)} relevant chunks from: {', '.join(list(doc_sources)[:3])}"
#             answer = f"{answer}{footer}"
            
#             source_note = "vector_database"
#             agent_steps = ["context_analysis", "information_synthesis", "answer_generation", "quality_assurance"]
            
#         else:
#             # Fallback to general knowledge with agent reasoning
#             logger.info(f"[SOURCE] Using GENERAL KNOWLEDGE with agent reasoning (max score: {max_score:.4f})")
            
#             system_prompt = """You are an expert AI assistant with broad knowledge across many domains.

# Your approach:
# 1. Understand the question thoroughly
# 2. Draw on your general knowledge
# 3. Provide accurate, well-structured information
# 4. Include relevant examples and context
# 5. Be clear about the nature of the information (general vs specific)

# Be comprehensive, accurate, and educational."""
            
#             user_prompt = f"""Question: {query}

# Please provide a detailed answer using your general knowledge:
# 1. Explain the topic clearly
# 2. Include relevant details and examples
# 3. Organize information logically
# 4. Mention any important related concepts"""
            
#             answer = await self.llm_service.generate(
#                 prompt=user_prompt,
#                 system_prompt=system_prompt,
#                 temperature=0.7,
#                 max_tokens=2000
#             )
            
#             # Add detailed informative note
#             source_note = f"""

# ---
# ℹ️ **Information Source**: General Knowledge

# **Analysis**: 
# - Searched your document database ({doc_count} documents indexed)
# - Found {len(search_results)} potential matches
# - Highest relevance score: {max_score:.2f} (threshold: {self.relevance_threshold})
# - **Conclusion**: No sufficiently relevant documents found

# **💡 Recommendation**: To get answers specific to your documents, try:
# 1. Uploading documents related to: "{query}"
# 2. Using more specific keywords that match your document content
# 3. Checking if documents were successfully indexed

# This answer is based on general AI knowledge and may not reflect your specific context."""
            
#             answer = f"{answer}{source_note}"
            
#             # Clear results for general knowledge
#             search_results = []
#             source_note = "general_knowledge"
#             agent_steps = ["query_analysis", "vector_search", "relevance_check", "fallback_to_general_knowledge", "answer_generation"]
        
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
#             "confidence": max_score if is_relevant else 0.75,
#             "source": source_note,
#             "fallback_used": not is_relevant,
#             "max_relevance_score": max_score,
#             "agent_steps": agent_steps
#         }
    
#     async def _auto_rag_strategy(self, query: str, context: Dict) -> Dict[str, Any]:
#         """Auto-select strategy based on query complexity"""
#         query_lower = query.lower()
        
#         # Use agentic for complex queries
#         complex_indicators = ["who is", "what are", "explain", "describe", "how does", "why", "analyze"]
        
#         if any(indicator in query_lower for indicator in complex_indicators):
#             logger.info("[AUTO] Selected AGENTIC strategy")
#             return await self._agentic_rag_strategy(query, context)
#         else:
#             logger.info("[AUTO] Selected SIMPLE strategy")
#             return await self._simple_rag_strategy(query, context)
    
#     async def execute_query(
#         self,
#         query: str,
#         top_k: int = 5,
#         session_id: Optional[str] = None,
#         document_id: Optional[str] = None,
#         strategy: RAGStrategy = RAGStrategy.AUTO
#     ) -> Dict[str, Any]:
#         """Execute query with intelligent fallback"""
#         start_time = datetime.now()
        
#         logger.info(f"\n{'='*80}")
#         logger.info(f"[EXECUTE QUERY] {query}")
#         logger.info(f"[PARAMETERS] Strategy: {strategy.value}, Top-K: {top_k}, Document ID: {document_id}")
#         logger.info(f"{'='*80}")
        
#         context = {
#             "top_k": top_k,
#             "session_id": session_id,
#             "document_id": document_id,
#             "query": query
#         }
        
#         strategy_func = self.strategies.get(strategy, self._auto_rag_strategy)
#         result = await strategy_func(query, context)
        
#         processing_time = (datetime.now() - start_time).total_seconds()
        
#         logger.info(f"[COMPLETED] Time: {processing_time:.2f}s, Source: {result.get('source', 'unknown')}, Fallback: {result.get('fallback_used', False)}")
        
#         return {
#             "answer": result["answer"],
#             "strategy_used": strategy,
#             "retrieved_chunks": result.get("retrieved_chunks", []),
#             "confidence": result.get("confidence", 0.7),
#             "processing_time": processing_time,
#             "source": result.get("source", "vector_database"),
#             "fallback_used": result.get("fallback_used", False),
#             "max_relevance_score": result.get("max_relevance_score", 0.0),
#             **({k: v for k, v in result.items() if k in ["agent_steps"]})
#         }

#     async def process_document(
#         self,
#         filename: str,
#         content: bytes,
#         content_type: str
#     ) -> Dict[str, Any]:
#         """Process and index document"""
#         start_time = datetime.now()
        
#         logger.info(f"\n{'='*80}")
#         logger.info(f"[DOCUMENT PROCESSING] {filename}")
#         logger.info(f"[INFO] Type: {content_type}, Size: {len(content)} bytes")
#         logger.info(f"{'='*80}")
        
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
#                 text = "Binary content - unable to extract text"
        
#         logger.info(f"[EXTRACTED] {len(text)} characters")
        
#         # Chunk text
#         chunks = self._chunk_text(text)
#         logger.info(f"[CHUNKED] {len(chunks)} chunks created")
        
#         if not chunks:
#             logger.warning("[SKIP] No text extracted from document")
#             return {
#                 "chunks_created": 0,
#                 "document_id": str(uuid.uuid4()),
#                 "processing_time": (datetime.now() - start_time).total_seconds(),
#                 "method": "skip",
#                 "message": "No text content found in document"
#             }
        
#         # Generate document ID
#         doc_id = str(uuid.uuid4())
#         logger.info(f"[DOCUMENT ID] {doc_id}")
        
#         # Generate embeddings
#         logger.info("[EMBEDDING] Generating embeddings...")
#         embeddings = self.embedding_service.embed_texts(chunks)
#         logger.info(f"[EMBEDDING] Generated {len(embeddings)} embeddings")
        
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
        
#         # Add to vector store
#         logger.info(f"[INDEXING] Adding {len(chunks)} chunks to vector store...")
#         self.vectorstore.add_documents(
#             documents=chunks,
#             embeddings=embeddings,
#             metadata=metadatas,
#             ids=[f"{doc_id}_chunk_{i}" for i in range(len(chunks))]
#         )
        
#         # Verify
#         total_docs = self.vectorstore.get_count()
#         verification = self.vectorstore.get_documents_by_id(doc_id)
#         logger.info(f"[VERIFICATION] Total docs in store: {total_docs}, Document chunks: {len(verification)}")
        
#         if len(verification) != len(chunks):
#             logger.warning(f"[MISMATCH] Expected {len(chunks)} chunks, found {len(verification)}")
        
#         processing_time = (datetime.now() - start_time).total_seconds()
#         logger.info(f"[SUCCESS] Processed in {processing_time:.2f}s")
#         logger.info(f"{'='*80}\n")
        
#         return {
#             "chunks_created": len(chunks),
#             "document_id": doc_id,
#             "processing_time": processing_time,
#             "method": "vector_store",
#             "message": f"Successfully indexed {len(chunks)} chunks"
#         }
    
#     def _extract_text_from_pdf(self, content: bytes) -> str:
#         """Extract text from PDF"""
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
#             logger.error(f"[ERROR] PDF extraction failed: {str(e)}")
#             return f"Error extracting PDF: {str(e)}"
    
#     def _chunk_text(self, text: str, chunk_size: int = 800, chunk_overlap: int = 100) -> List[str]:
#         """Chunk text with overlap"""
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


# # ============================================
# # Global Singleton
# # ============================================

# _rag_orchestrator = None

# def get_rag_orchestrator(relevance_threshold: float = 0.30) -> RAGOrchestrator:
#     """Get singleton RAG orchestrator with configurable threshold"""
#     global _rag_orchestrator
#     if _rag_orchestrator is None:
#         _rag_orchestrator = RAGOrchestrator(relevance_threshold=relevance_threshold)
#     return _rag_orchestrator




"""
Enhanced RAG Orchestrator with Intelligent Relevance Detection & Internet Search
1. Check ChromaDB with SMART relevance detection
2. If not truly relevant, search the internet
3. Use Groq LLM to generate answer from best source
"""
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid
import httpx
import re

from app.core.enums import RAGStrategy

logger = logging.getLogger(__name__)


class RAGOrchestrator:
    """
    Enhanced RAG Orchestrator with intelligent internet search fallback:
    1. Search vector database first
    2. Check REAL relevance (not just cosine similarity score)
    3. If not relevant, search the internet
    4. Generate answer from best available source
    """
    
    def __init__(self, relevance_threshold: float = 0.30):
        logger.info("Initializing Enhanced RAG Orchestrator with Smart Relevance Detection...")
        
        from app.core.dependencies import get_llm_service, get_embedding_service, get_vectorstore
        
        self.llm_service = get_llm_service()
        self.embedding_service = get_embedding_service() 
        self.vectorstore = get_vectorstore()
        self.relevance_threshold = relevance_threshold
        
        # Internet search configuration
        self.enable_internet_search = True
        
        self.strategies = {
            RAGStrategy.SIMPLE: self._simple_rag_strategy,
            RAGStrategy.AGENTIC: self._agentic_rag_strategy,
            RAGStrategy.AUTO: self._auto_rag_strategy
        }
        
        logger.info(f"[OK] Enhanced RAG Orchestrator initialized (threshold: {relevance_threshold}, internet: enabled)")
    
    def _check_basic_relevance(self, search_results: List[Dict]) -> tuple:
        """
        Check basic cosine similarity relevance
        Returns: (is_relevant: bool, max_score: float, avg_score: float)
        """
        if not search_results:
            return False, 0.0, 0.0
        
        scores = [result.get("score", 0.0) for result in search_results]
        max_score = max(scores)
        avg_score = sum(scores) / len(scores)
        
        is_relevant = max_score >= self.relevance_threshold
        
        return is_relevant, max_score, avg_score
    
    async def _check_semantic_relevance(self, query: str, top_chunks: List[Dict], max_chunks: int = 3) -> Dict[str, Any]:
        """
        Use LLM to verify if the retrieved chunks actually answer the query
        This prevents false positives from cosine similarity
        """
        if not top_chunks:
            return {
                "is_relevant": False,
                "confidence": 0.0,
                "reason": "No chunks retrieved"
            }
        
        # Take only top chunks for verification
        chunks_to_check = top_chunks[:max_chunks]
        
        # Build context from top chunks
        context_text = "\n\n".join([
            f"Chunk {i+1}: {chunk['document'][:300]}"
            for i, chunk in enumerate(chunks_to_check)
        ])
        
        # Ask LLM to verify relevance
        verification_prompt = f"""You are a relevance checker. Determine if the provided text chunks can answer the user's question.

Question: {query}

Retrieved Text Chunks:
{context_text}

Instructions:
1. Read the question carefully
2. Analyze if the chunks contain information that can answer the question
3. Respond with ONLY "RELEVANT" or "NOT_RELEVANT" followed by a brief reason

Format your response as:
VERDICT: [RELEVANT or NOT_RELEVANT]
REASON: [One sentence explaining why]

Example 1:
Question: "Tell me about AIR University in Islamabad"
Chunks: "Bahria University Islamabad... Bachelor of Sciences..."
VERDICT: NOT_RELEVANT
REASON: The chunks discuss Bahria University, not AIR University.

Example 2:
Question: "What is Django framework?"
Chunks: "Django is a Python web framework... used for building web applications..."
VERDICT: RELEVANT
REASON: The chunks directly explain what Django framework is.

Now analyze:"""

        try:
            llm_response = await self.llm_service.generate(
                prompt=verification_prompt,
                temperature=0.1,  # Low temperature for consistent verification
                max_tokens=150
            )
            
            # Parse LLM response
            llm_response_lower = llm_response.lower()
            
            # Extract verdict
            is_relevant = "relevant" in llm_response_lower and "not_relevant" not in llm_response_lower and "not relevant" not in llm_response_lower
            
            # Extract reason
            reason_match = re.search(r'reason:\s*(.+?)(?:\n|$)', llm_response, re.IGNORECASE)
            reason = reason_match.group(1).strip() if reason_match else "LLM verification completed"
            
            logger.info(f"[SEMANTIC CHECK] Query: '{query[:50]}...' -> {('RELEVANT' if is_relevant else 'NOT_RELEVANT')}")
            logger.info(f"[SEMANTIC CHECK] Reason: {reason}")
            
            return {
                "is_relevant": is_relevant,
                "confidence": 0.9 if is_relevant else 0.1,
                "reason": reason,
                "llm_response": llm_response
            }
            
        except Exception as e:
            logger.error(f"[SEMANTIC CHECK] Failed: {str(e)}")
            # Fallback to basic check if LLM verification fails
            return {
                "is_relevant": True,  # Conservative: assume relevant if check fails
                "confidence": 0.5,
                "reason": f"Verification failed: {str(e)}"
            }
    
    def _clean_llm_response(self, answer: str) -> str:
        """
        Remove hedging phrases from LLM responses
        Cleans up disclaimers like "I couldn't find", "I don't have information"
        """
        # Common hedging patterns to remove (more comprehensive)
        hedging_patterns = [
            # "I couldn't find..." patterns
            r"^I couldn't find (much |any )?information about.*?\.(\s*However,?)?\s*",
            r"^I could not find (much |any )?information about.*?\.(\s*However,?)?\s*",
            
            # "I don't have..." patterns
            r"^I don't have (much |any )?information about.*?\.(\s*However,?)?\s*",
            r"^I do not have (much |any )?information about.*?\.(\s*However,?)?\s*",
            
            # Other disclaimer patterns
            r"^I wasn't able to find.*?\.(\s*However,?)?\s*",
            r"^I don't know (much )?about.*?\.(\s*However,?)?\s*",
            r"^I'm not sure about.*?\.(\s*However,?)?\s*",
            r"^Based on my knowledge cutoff.*?\.(\s*However,?)?\s*",
            
            # Multi-sentence disclaimers (catches patterns like "I couldn't find X. However, I did find Y.")
            r"^I couldn't find.*?\.(\s+However,?)?\s+I did find.*?\.\s*",
            r"^I don't have.*?\.(\s+However,?)?\s+I did find.*?\.\s*",
        ]
        
        cleaned = answer
        
        # Apply all patterns
        for pattern in hedging_patterns:
            cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE | re.MULTILINE | re.DOTALL)
        
        # Additional cleanup for leftover phrases
        leftover_patterns = [
            r"^However,?\s+I did find information about.*?\.\s*",
            r"^However,?\s+",
            r"^It seems that you might be referring to",
        ]
        
        for pattern in leftover_patterns:
            cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE | re.MULTILINE)
        
        # Clean up any double spaces or newlines
        cleaned = re.sub(r'\n\n+', '\n\n', cleaned)
        cleaned = re.sub(r'  +', ' ', cleaned)
        
        # If the response starts with "the" after cleaning, capitalize it
        if cleaned and cleaned[0].islower():
            cleaned = cleaned[0].upper() + cleaned[1:]
        
        return cleaned.strip()
    
    async def _search_internet(self, query: str) -> Dict[str, Any]:
        """
        Search the internet for information using DuckDuckGo
        """
        try:
            logger.info(f"[INTERNET SEARCH] Searching for: {query}")
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    "https://api.duckduckgo.com/",
                    params={
                        "q": query,
                        "format": "json",
                        "no_html": 1,
                        "skip_disambig": 1
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    results = []
                    
                    # Abstract (main answer)
                    if data.get("Abstract"):
                        results.append({
                            "title": data.get("Heading", "Main Result"),
                            "snippet": data.get("Abstract"),
                            "source": data.get("AbstractSource", "DuckDuckGo"),
                            "url": data.get("AbstractURL", "")
                        })
                    
                    # Related topics
                    for topic in data.get("RelatedTopics", [])[:5]:
                        if isinstance(topic, dict) and topic.get("Text"):
                            results.append({
                                "title": topic.get("Text", "")[:100],
                                "snippet": topic.get("Text", ""),
                                "source": "DuckDuckGo",
                                "url": topic.get("FirstURL", "")
                            })
                    
                    if results:
                        logger.info(f"[INTERNET SEARCH] ✅ Found {len(results)} results")
                        return {
                            "success": True,
                            "results": results,
                            "source": "internet_search"
                        }
                    else:
                        logger.warning("[INTERNET SEARCH] ❌ No results from DuckDuckGo")
                        return {
                            "success": False,
                            "results": [],
                            "source": "internet_search",
                            "message": "No instant answers available"
                        }
                else:
                    logger.error(f"[INTERNET SEARCH] ❌ API error: {response.status_code}")
                    return {
                        "success": False,
                        "results": [],
                        "source": "internet_search",
                        "message": f"API error: {response.status_code}"
                    }
                    
        except Exception as e:
            logger.error(f"[INTERNET SEARCH] ❌ Error: {str(e)}")
            return {
                "success": False,
                "results": [],
                "source": "internet_search",
                "message": f"Search error: {str(e)}"
            }
    
    async def _generate_answer_from_internet(self, query: str, search_results: List[Dict]) -> str:
        """Generate answer using Groq LLM from internet search results"""
        
        if not search_results:
            # No search results, use general knowledge
            system_prompt = """You are a helpful AI assistant providing information to users.

IMPORTANT INSTRUCTIONS:
- Answer questions directly and confidently
- NEVER start with "I don't have", "I couldn't find", or "I don't know"
- If you have knowledge about the topic, share it immediately
- Be factual, comprehensive, and helpful"""
            
            user_prompt = f"""Question: {query}

Provide a comprehensive, informative answer. Start directly with the information, not with disclaimers."""
            
            answer = await self.llm_service.generate(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.6
            )
            
            # Clean up any hedging phrases
            answer = self._clean_llm_response(answer)
            
            return f"{answer}\n\n---\n🌐 **Source**: General AI Knowledge (internet search returned no results)"
        
        # Format search results for LLM
        context_parts = []
        for i, result in enumerate(search_results[:5], 1):
            title = result.get("title", "Unknown")
            snippet = result.get("snippet", "")
            source = result.get("source", "Internet")
            url = result.get("url", "")
            
            context_parts.append(f"""[Source {i}: {title}]
{snippet}
{f"URL: {url}" if url else ""}
""")
        
        context_text = "\n\n".join(context_parts)
        
        system_prompt = """You are a helpful AI assistant that provides accurate answers based on internet search results.

Your approach:
1. Analyze the search results carefully
2. Extract key information relevant to the question
3. Synthesize a clear, comprehensive answer
4. Be accurate and cite sources
5. If search results don't fully answer the question, supplement with your knowledge but make this clear"""
        
        user_prompt = f"""Internet search results for the question:

{context_text}

Question: {query}

Please provide a comprehensive answer based on these search results. Structure your answer clearly and cite sources."""
        
        answer = await self.llm_service.generate(
            prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=0.7,
            max_tokens=2000
        )
        
        # Add source attribution
        sources = list(set([r.get("source", "Internet") for r in search_results[:3]]))
        footer = f"\n\n---\n🌐 **Source**: Internet Search Results\n📚 **Based on**: {', '.join(sources)}"
        
        return f"{answer}{footer}"
    
    async def _simple_rag_strategy(self, query: str, context: Dict) -> Dict[str, Any]:
        """Simple RAG with intelligent semantic relevance checking"""
        doc_count = self.vectorstore.get_count()
        document_id = context.get("document_id")
        top_k = context.get("top_k", 5)
        
        logger.info(f"\n{'='*80}")
        logger.info(f"[SIMPLE RAG] Query: {query}")
        logger.info(f"[SIMPLE RAG] Vector store: {doc_count} docs")
        logger.info(f"{'='*80}")
        
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
        
        # Step 3: Check basic relevance (cosine similarity)
        is_basically_relevant, max_score, avg_score = self._check_basic_relevance(search_results)
        
        logger.info(f"[BASIC CHECK] Max score: {max_score:.4f}, Threshold: {self.relevance_threshold}, Pass: {is_basically_relevant}")
        
        # Step 4: If basic check passes, do semantic verification with LLM
        if is_basically_relevant and search_results:
            semantic_check = await self._check_semantic_relevance(query, search_results)
            is_truly_relevant = semantic_check["is_relevant"]
            
            logger.info(f"[SEMANTIC CHECK] Truly relevant: {is_truly_relevant}, Reason: {semantic_check['reason']}")
        else:
            is_truly_relevant = False
            semantic_check = {"reason": "Basic relevance check failed", "confidence": 0.0}
        
        # Step 5: Generate answer based on true relevance
        if is_truly_relevant:
            # ✅ Use vector database
            logger.info(f"[SOURCE] ✅ VECTOR DATABASE (semantically relevant)")
            
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
            
            answer = f"{answer}\n\n---\n✅ **Source**: Your Uploaded Documents"
            
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
                "confidence": max_score,
                "source": "vector_database",
                "fallback_used": False,
                "max_relevance_score": max_score,
                "semantic_check": semantic_check
            }
            
        else:
            # ❌ Not relevant, search internet
            logger.info(f"[SOURCE] 🌐 INTERNET SEARCH (documents not relevant)")
            logger.info(f"[REASON] {semantic_check.get('reason', 'Not relevant')}")
            
            if self.enable_internet_search:
                # Search the internet
                internet_results = await self._search_internet(query)
                
                if internet_results.get("success") and internet_results.get("results"):
                    # Generate answer from internet results
                    answer = await self._generate_answer_from_internet(
                        query,
                        internet_results["results"]
                    )
                    
                    source_info = f"""

---
ℹ️ **Information Flow**:

**Step 1: Document Database Search**
- ✅ Searched {doc_count} documents
- ✅ Found {len(search_results)} potential matches
- ✅ Max similarity score: {max_score:.2f}

**Step 2: Semantic Relevance Check**
- ❌ **Not truly relevant**: {semantic_check.get('reason', 'Documents do not answer the query')}

**Step 3: Internet Search**
- 🌐 Searched the internet
- ✅ Found {len(internet_results['results'])} sources
- 🤖 Generated answer using Groq LLM + internet data

💡 **Tip**: Upload documents about "{query}" to get answers from your own content."""
                    
                    return {
                        "answer": f"{answer}{source_info}",
                        "retrieved_chunks": [],
                        "confidence": 0.75,
                        "source": "internet_search",
                        "fallback_used": True,
                        "max_relevance_score": max_score,
                        "semantic_check": semantic_check,
                        "internet_results_count": len(internet_results["results"])
                    }
                else:
                    logger.warning("[FALLBACK] Internet search failed, using general knowledge")
            
            # Final fallback: general knowledge
            system_prompt = """You are a helpful AI assistant providing information to users.

IMPORTANT INSTRUCTIONS:
- Answer questions directly and confidently
- NEVER start with "I don't have", "I couldn't find", or "I don't know"
- If you have knowledge about the topic, share it immediately
- Be factual, comprehensive, and helpful"""
            
            user_prompt = f"""Question: {query}

Provide a comprehensive, informative answer. Start directly with the information, not with disclaimers."""
            
            answer = await self.llm_service.generate(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.6
            )
            
            # Clean up any hedging phrases
            answer = self._clean_llm_response(answer)
            
            source_note = f"""

---
ℹ️ **Information Source**: General AI Knowledge

**What happened**:
1. Searched your documents: Found {len(search_results)} results (max score: {max_score:.2f})
2. Relevance check: ❌ {semantic_check.get('reason', 'Not relevant')}
3. Internet search: {"Not enabled" if not self.enable_internet_search else "No results found"}
4. Used: General AI knowledge base

💡 **Recommendation**: Upload relevant documents about "{query}" for specific answers."""
            
            return {
                "answer": f"{answer}{source_note}",
                "retrieved_chunks": [],
                "confidence": 0.7,
                "source": "general_knowledge",
                "fallback_used": True,
                "max_relevance_score": max_score,
                "semantic_check": semantic_check
            }
    
    async def _agentic_rag_strategy(self, query: str, context: Dict) -> Dict[str, Any]:
        """Agentic RAG with semantic relevance checking"""
        doc_count = self.vectorstore.get_count()
        document_id = context.get("document_id")
        top_k = context.get("top_k", 8)
        
        logger.info(f"\n{'='*80}")
        logger.info(f"[AGENTIC RAG] Query: {query}")
        logger.info(f"{'='*80}")
        
        # Step 1: Search vector database
        query_embedding = self.embedding_service.embed_text(query)
        filter_params = {"document_id": document_id} if document_id else None
        search_results = self.vectorstore.search_by_embedding(
            query_embedding=query_embedding,
            top_k=top_k,
            filter=filter_params
        )
        
        logger.info(f"[AGENTIC RAG] Retrieved {len(search_results)} chunks")
        
        # Step 2: Check basic + semantic relevance
        is_basically_relevant, max_score, avg_score = self._check_basic_relevance(search_results)
        
        if is_basically_relevant and search_results:
            semantic_check = await self._check_semantic_relevance(query, search_results)
            is_truly_relevant = semantic_check["is_relevant"]
        else:
            is_truly_relevant = False
            semantic_check = {"reason": "Basic check failed", "confidence": 0.0}
        
        # Step 3: Generate answer with agent reasoning
        if is_truly_relevant:
            logger.info(f"[SOURCE] ✅ VECTOR DATABASE (semantically relevant)")
            
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
5. Acknowledge any limitations or uncertainties"""
            
            user_prompt = f"""Context from documents:
{context_text}

Question: {query}

Please provide a comprehensive answer following these steps:
1. Analyze what the context tells us
2. Synthesize the information
3. Include relevant details and examples
4. Cite sources appropriately"""
            
            answer = await self.llm_service.generate(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.7,
                max_tokens=2000
            )
            
            doc_sources = set(r.get("metadata", {}).get("source", "Unknown") for r in search_results[:5])
            footer = f"\n\n---\n✅ **Sources**: {len(search_results)} chunks from: {', '.join(list(doc_sources)[:3])}"
            
            return {
                "answer": f"{answer}{footer}",
                "retrieved_chunks": [
                    {
                        "content": result["document"][:200] + "...",
                        "metadata": result.get("metadata", {}),
                        "score": result.get("score", 0.5)
                    }
                    for result in search_results
                ],
                "confidence": max_score,
                "source": "vector_database",
                "fallback_used": False,
                "max_relevance_score": max_score,
                "agent_steps": ["document_search", "semantic_verification", "context_analysis", "answer_synthesis"],
                "semantic_check": semantic_check
            }
            
        else:
            # Use internet search
            logger.info(f"[SOURCE] 🌐 INTERNET SEARCH (documents not relevant)")
            
            if self.enable_internet_search:
                internet_results = await self._search_internet(query)
                
                if internet_results.get("success") and internet_results.get("results"):
                    answer = await self._generate_answer_from_internet(
                        query,
                        internet_results["results"]
                    )
                    
                    source_info = f"""

---
🤖 **Agentic Analysis**:

**Step 1: Document Search**
- Searched {doc_count} documents
- Found {len(search_results)} potential matches (max score: {max_score:.2f})

**Step 2: Semantic Verification**
- ❌ Not truly relevant: {semantic_check.get('reason', 'Documents do not answer query')}

**Step 3: Internet Search**
- 🌐 Searched the internet
- ✅ Found {len(internet_results['results'])} sources

**Step 4: Answer Synthesis**
- Used Groq LLM to generate comprehensive answer from internet data

💡 Upload documents about "{query}" to get answers from your specific content."""
                    
                    return {
                        "answer": f"{answer}{source_info}",
                        "retrieved_chunks": [],
                        "confidence": 0.75,
                        "source": "internet_search",
                        "fallback_used": True,
                        "max_relevance_score": max_score,
                        "agent_steps": ["document_search", "semantic_verification", "internet_search", "answer_synthesis"],
                        "semantic_check": semantic_check,
                        "internet_results_count": len(internet_results["results"])
                    }
            
            # Fallback to general knowledge
            system_prompt = """You are a helpful AI assistant providing information to users.

IMPORTANT INSTRUCTIONS:
- Answer questions directly and confidently
- NEVER start with "I don't have", "I couldn't find", or "I don't know"
- If you have knowledge about the topic, share it immediately
- Be factual, comprehensive, and helpful"""
            
            user_prompt = f"""Question: {query}

Provide a comprehensive, informative answer. Start directly with the information, not with disclaimers."""
            
            answer = await self.llm_service.generate(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.6,
                max_tokens=2000
            )
            
            # Clean up any hedging phrases
            answer = self._clean_llm_response(answer)
            
            return {
                "answer": f"{answer}\n\n---\nℹ️ Source: General AI Knowledge",
                "retrieved_chunks": [],
                "confidence": 0.7,
                "source": "general_knowledge",
                "fallback_used": True,
                "max_relevance_score": max_score,
                "agent_steps": ["document_search", "semantic_verification", "internet_attempt", "general_knowledge"],
                "semantic_check": semantic_check
            }
    
    async def _auto_rag_strategy(self, query: str, context: Dict) -> Dict[str, Any]:
        """Auto-select strategy based on query complexity"""
        query_lower = query.lower()
        
        complex_indicators = ["who is", "what are", "explain", "describe", "how does", "why", "analyze", "tell me about"]
        
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
        """Execute query with smart relevance detection and internet fallback"""
        start_time = datetime.now()
        
        logger.info(f"\n{'='*80}")
        logger.info(f"[EXECUTE QUERY] {query}")
        logger.info(f"[PARAMETERS] Strategy: {strategy.value}, Top-K: {top_k}")
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
        
        logger.info(f"[COMPLETED] Time: {processing_time:.2f}s, Source: {result.get('source')}")
        logger.info(f"{'='*80}\n")
        
        return {
            "answer": result["answer"],
            "strategy_used": strategy,
            "retrieved_chunks": result.get("retrieved_chunks", []),
            "confidence": result.get("confidence", 0.7),
            "processing_time": processing_time,
            "source": result.get("source", "vector_database"),
            "fallback_used": result.get("fallback_used", False),
            "max_relevance_score": result.get("max_relevance_score", 0.0),
            **({k: v for k, v in result.items() if k in ["agent_steps", "internet_results_count", "semantic_check"]})
        }

    async def process_document(
        self,
        filename: str,
        content: bytes,
        content_type: str
    ) -> Dict[str, Any]:
        """Process and index document"""
        start_time = datetime.now()
        
        logger.info(f"[DOCUMENT PROCESSING] {filename}")
        
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
                text = "Binary content"
        
        # Chunk text
        chunks = self._chunk_text(text)
        
        if not chunks:
            return {
                "chunks_created": 0,
                "document_id": str(uuid.uuid4()),
                "processing_time": (datetime.now() - start_time).total_seconds(),
                "message": "No text content found"
            }
        
        # Generate document ID
        doc_id = str(uuid.uuid4())
        
        # Generate embeddings and add to vector store
        embeddings = self.embedding_service.embed_texts(chunks)
        
        metadatas = [
            {
                "source": filename,
                "content_type": content_type,
                "chunk_index": i,
                "document_id": doc_id
            }
            for i in range(len(chunks))
        ]
        
        self.vectorstore.add_documents(
            documents=chunks,
            embeddings=embeddings,
            metadata=metadatas,
            ids=[f"{doc_id}_chunk_{i}" for i in range(len(chunks))]
        )
        
        processing_time = (datetime.now() - start_time).total_seconds()
        logger.info(f"[SUCCESS] Processed {len(chunks)} chunks in {processing_time:.2f}s")
        
        return {
            "chunks_created": len(chunks),
            "document_id": doc_id,
            "processing_time": processing_time,
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
            logger.error(f"PDF extraction failed: {str(e)}")
            return ""
    
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


# Global singleton
_rag_orchestrator = None

def get_rag_orchestrator(relevance_threshold: float = 0.30) -> RAGOrchestrator:
    """Get singleton RAG orchestrator with smart relevance detection"""
    global _rag_orchestrator
    if _rag_orchestrator is None:
        _rag_orchestrator = RAGOrchestrator(relevance_threshold=relevance_threshold)
    return _rag_orchestrator