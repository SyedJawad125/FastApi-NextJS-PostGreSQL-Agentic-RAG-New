"""
Enhanced RAG Orchestrator with Agentic ReAct Pattern
Delegates query execution to Coordinator Agent
"""
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid

from app.core.enums import RAGStrategy
from app.services.agents.coordinator import CoordinatorAgent

logger = logging.getLogger(__name__)


class RAGOrchestrator:
    """
    Enhanced RAG Orchestrator with Agentic ReAct Pattern
    Uses Coordinator Agent to intelligently select tools and strategies
    """
    
    def __init__(self, relevance_threshold: float = 0.30):
        logger.info("Initializing Agentic RAG Orchestrator with ReAct Pattern...")
        
        from app.core.dependencies import get_llm_service, get_embedding_service, get_vectorstore
        
        self.llm_service = get_llm_service()
        self.embedding_service = get_embedding_service() 
        self.vectorstore = get_vectorstore()
        self.relevance_threshold = relevance_threshold
        
        # Initialize Coordinator Agent (ReAct brain)
        self.coordinator = CoordinatorAgent(
            llm_service=self.llm_service,
            embedding_service=self.embedding_service,
            vectorstore=self.vectorstore
        )
        
        # Strategy routing (for backward compatibility)
        self.strategies = {
            RAGStrategy.SIMPLE: self._simple_strategy,
            RAGStrategy.AGENTIC: self._agentic_strategy,
            RAGStrategy.AUTO: self._auto_strategy
        }
        
        logger.info(f"[OK] Agentic RAG Orchestrator initialized (ReAct Pattern enabled)")
    
    async def _simple_strategy(self, query: str, context: Dict) -> Dict[str, Any]:
        """Simple strategy using Coordinator Agent"""
        logger.info("[SIMPLE STRATEGY] Using Coordinator Agent (ReAct)")
        return await self.coordinator.execute(query, context)
    
    async def _agentic_strategy(self, query: str, context: Dict) -> Dict[str, Any]:
        """Agentic strategy using Coordinator Agent (same as simple, more logging)"""
        logger.info("[AGENTIC STRATEGY] Using Coordinator Agent (ReAct) with detailed logging")
        context["verbose"] = True
        return await self.coordinator.execute(query, context)
    
    async def _auto_strategy(self, query: str, context: Dict) -> Dict[str, Any]:
        """Auto strategy - let Coordinator decide"""
        logger.info("[AUTO STRATEGY] Letting Coordinator Agent decide approach")
        return await self.coordinator.execute(query, context)
    
    async def execute_query(
        self,
        query: str,
        top_k: int = 5,
        session_id: Optional[str] = None,
        document_id: Optional[str] = None,
        strategy: RAGStrategy = RAGStrategy.AUTO
    ) -> Dict[str, Any]:
        """
        Execute query using Coordinator Agent with ReAct pattern
        """
        start_time = datetime.now()
        
        logger.info(f"\n{'='*80}")
        logger.info(f"[ORCHESTRATOR] Query: {query}")
        logger.info(f"[ORCHESTRATOR] Strategy: {strategy.value}, Top-K: {top_k}")
        logger.info(f"{'='*80}")
        
        context = {
            "top_k": top_k,
            "session_id": session_id,
            "document_id": document_id,
            "query": query,
            "strategy": strategy
        }
        
        # Route to appropriate strategy (all use Coordinator Agent)
        strategy_func = self.strategies.get(strategy, self._auto_strategy)
        result = await strategy_func(query, context)
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        logger.info(f"\n{'='*80}")
        logger.info(f"[ORCHESTRATOR] Completed in {processing_time:.2f}s")
        logger.info(f"[ORCHESTRATOR] Source: {result.get('source')}")
        logger.info(f"[ORCHESTRATOR] Steps: {len(result.get('execution_steps', []))}")
        logger.info(f"{'='*80}\n")
        
        return {
            "answer": result["answer"],
            "strategy_used": strategy,
            "retrieved_chunks": result.get("retrieved_chunks", []),
            "confidence": result.get("confidence", 0.7),
            "processing_time": processing_time,
            "source": result.get("source", "coordinator_agent"),
            "execution_steps": result.get("execution_steps", []),
            "agent_type": result.get("agent_type", "coordinator_react"),
            "internet_sources": result.get("internet_sources", [])
        }
    
    async def process_document(
        self,
        filename: str,
        content: bytes,
        content_type: str
    ) -> Dict[str, Any]:
        """Process and index document (unchanged)"""
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
    """Get singleton RAG orchestrator with Agentic ReAct pattern"""
    global _rag_orchestrator
    if _rag_orchestrator is None:
        _rag_orchestrator = RAGOrchestrator(relevance_threshold=relevance_threshold)
    return _rag_orchestrator