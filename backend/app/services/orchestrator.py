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