# import io
# import os
# import traceback
# from fastapi import APIRouter, BackgroundTasks, HTTPException, UploadFile, File, Depends
# from openai import BaseModel
# from sqlalchemy.orm import Session
# from typing import Dict
# import time
# from datetime import datetime
# import uuid
# import logging

# # Schemas - Updated with Agentic RAG support
# from app.schemas.rag_schemas import (
#     # Query schemas
#     RAGQueryRequest,
#     RAGQueryResponse,
    
#     # Multi-agent schemas
#     MultiAgentQuery,
#     MultiAgentResponse,
    
#     # Graph schemas
#     GraphQuery,
#     GraphQueryResponse,
    
#     # Document schemas
#     DocumentUpload,
#     DocumentUploadResponse,
#     DocumentResponse,
#     DocumentList,
    
#     # Agent execution schemas (NEW)
#     AgentExecutionDetail,
#     AgentExecutionSummary,
#     AgentExecutionListResponse,
    
#     # Health & Stats schemas
#     HealthCheck,
#     HealthCheckResponse,
#     SystemStats,
    
#     # Session schemas (NEW)
#     SessionCreate,
#     SessionResponse,
# )
# # Database
# from app.core.config import get_db
# from app.models.rag_model import (
#     Document,
#     DocumentChunk,
#     GraphEntity,
#     GraphRelationship,
#     Query as QueryModel,
#     Session as SessionModel
# )

# # Orchestrator service
# from app.core.dependencies import extract_text_from_docx_bytes, extract_text_from_pdf_bytes, extract_text_from_txt_bytes, get_rag_service
# from app.core.enums import RAGStrategy
# from app.services.chunking import chunk_text
# # from app.services.vectorstore import get_vector_store
# from app.core.dependencies import get_rag_service

# from app.models.rag_model import Query, Document, Session
# from app.services.vectorstore import get_vector_store

import io
import os
import traceback
from fastapi import APIRouter, BackgroundTasks, HTTPException, UploadFile, File, Depends
from sqlalchemy.orm import Session
from typing import Dict
import time
from datetime import datetime
import uuid
import logging

# ✅ Schemas - Updated with Agentic RAG support
from app.schemas.rag_schemas import (
    # Query schemas
    RAGQueryRequest,
    RAGQueryResponse,
    
    # Multi-agent schemas
    MultiAgentQuery,
    MultiAgentResponse,
    
    # Graph schemas
    GraphQuery,
    GraphQueryResponse,
    
    # Document schemas
    DocumentUpload,
    DocumentUploadResponse,
    DocumentResponse,
    DocumentList,
    
    # Agent execution schemas (NEW)
    AgentExecutionDetail,
    AgentExecutionSummary,
    AgentExecutionListResponse,
    
    # Health & Stats schemas
    HealthCheck,
    HealthCheckResponse,
    SystemStats,
    
    # Session schemas (NEW)
    SessionCreate,
    SessionResponse,
)

# Database
from app.core.config import get_db
from app.models.rag_model import (
    Document,
    DocumentChunk,
    GraphEntity,
    GraphRelationship,
    Query as QueryModel,
    Session as SessionModel
)

# Dependencies
from app.core.dependencies import (
    extract_text_from_docx_bytes,
    extract_text_from_pdf_bytes,
    extract_text_from_txt_bytes,
    get_rag_service,
    get_vectorstore,
    get_embedding_service
)
from app.core.enums import RAGStrategy
from app.services.chunking import chunk_text
from app.models.rag_model import Query
logger = logging.getLogger(__name__)

# ✅ Router prefix
router = APIRouter(tags=["RAG System"])




# ============================================================
# 🧠 RAG Query Endpoint (FIXED)
# ============================================================
from app.core.dependencies import get_vectorstore
# @router.post("/query", response_model=RAGQueryResponse)
# async def query_rag(request: RAGQueryRequest, db: Session = Depends(get_db)):
#     """Main RAG query endpoint with strategy support and data safety checks."""
#     try:
#         logger.info(f"[QUERY] Received query: {request.query[:50]}...")
#         start_time = time.time()

#         # ✅ CORRECT: Get the RAG orchestrator (not vector store directly!)
#         from app.services.orchestrator import get_rag_orchestrator
#         from app.core.enums import RAGStrategy
#         from app.services.vectorstore import get_vector_store
        
#         rag_service = get_rag_orchestrator()
#         vector_store = get_vectorstore()  # Just for safety checks
        
#         # ✅ CRITICAL SAFETY CHECK: Verify database AND vector store have data
#         total_docs = db.query(Document).count()
#         total_chunks = db.query(DocumentChunk).count()
#         vector_count = vector_store.get_count()
#         is_cleared = vector_store._is_cleared
        
#         logger.info(
#             f"[DATABASE] Current state: {total_docs} docs, {total_chunks} chunks, "
#             f"{vector_count} vectors (cleared={is_cleared})"
#         )
        
#         # ✅ IMMEDIATE REJECTION if no data exists
#         if (total_docs == 0 and total_chunks == 0) or vector_count == 0 or is_cleared:
#             logger.warning("[SAFETY] No documents/vectors in system - rejecting query")
#             return RAGQueryResponse(
#                 query=request.query,
#                 answer="No documents found in the system. Please upload CVs first.",
#                 strategy_used="direct",
#                 processing_time=0.1,
#                 retrieved_chunks=[],
#                 confidence_score=0.0
#             )

#         # ✅ Map strategy string to enum
#         strategy_map = {
#             "simple": RAGStrategy.SIMPLE,
#             "agentic": RAGStrategy.AGENTIC,
#             "auto": RAGStrategy.AUTO
#         }

#         if request.strategy not in strategy_map:
#             raise HTTPException(
#                 status_code=400,
#                 detail=f"Invalid strategy: {request.strategy}. Use: simple, agentic, or auto"
#             )

#         strategy = strategy_map[request.strategy]

#         # ✅ Validate document exists if document_id is provided
#         document_id = request.document_id
#         document = None
#         if document_id:
#             document = db.query(Document).filter(Document.id == document_id).first()
#             if not document:
#                 raise HTTPException(
#                     status_code=404,
#                     detail=f"Document with ID {document_id} not found"
#                 )
#             logger.info(f"[QUERY] Querying document: {document.filename}")

#         # ✅ Execute RAG query using YOUR orchestrator
#         result = await rag_service.execute_query(
#             query=request.query,
#             top_k=request.top_k,
#             session_id=request.session_id,
#             document_id=document_id,
#             strategy=strategy
#         )

#         processing_time = time.time() - start_time

#         # ✅ Enhanced logging for debugging
#         retrieved_chunks = result.get("retrieved_chunks", [])
#         logger.info(
#             f"[QUERY] Retrieved {len(retrieved_chunks)} chunks, "
#             f"processing time: {processing_time:.2f}s, "
#             f"source: {result.get('source', 'unknown')}, "
#             f"fallback: {result.get('fallback_used', False)}"
#         )

#         # ✅ Save query in DB with document_id and enhanced metadata
#         db_query = Query(
#             id=str(uuid.uuid4()),
#             query_text=request.query,
#             answer=result["answer"],
#             strategy_used=request.strategy,
#             processing_time=processing_time,
#             confidence_score=result.get("confidence", 0.85),
#             retrieved_chunks_count=len(retrieved_chunks),
#             session_id=request.session_id,
#             document_id=document_id,
#             metadata={
#                 "top_k": request.top_k,
#                 "chunk_count": len(retrieved_chunks),
#                 "document_id": document_id,
#                 "document_filename": document.filename if document else None,
#                 "database_docs_count": total_docs,
#                 "database_chunks_count": total_chunks,
#                 "vector_store_count": vector_count,
#                 "source": result.get("source", "vector_database"),
#                 "fallback_used": result.get("fallback_used", False),
#                 "max_relevance_score": result.get("max_relevance_score", 0.0),
#                 "agent_steps": result.get("agent_steps", [])
#             }
#         )
#         db.add(db_query)
#         db.commit()
#         db.refresh(db_query)

#         logger.info(f"[QUERY] Successfully processed query with {request.strategy} strategy")

#         return RAGQueryResponse(
#             query=request.query,
#             answer=result["answer"],
#             strategy_used=result["strategy_used"].value,
#             processing_time=processing_time,
#             retrieved_chunks=retrieved_chunks,
#             confidence_score=result.get("confidence", 0.85)
#         )

#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"[ERROR] Query processing failed: {str(e)}", exc_info=True)
#         db.rollback()
#         raise HTTPException(
#             status_code=500, 
#             detail=f"Query processing failed: {str(e)}"
#         )

@router.post("/query", response_model=RAGQueryResponse)
async def query_rag(request: RAGQueryRequest, db: Session = Depends(get_db)):
    """Main RAG query endpoint with Agentic ReAct Pattern"""
    try:
        logger.info(f"[QUERY] Received query: {request.query[:50]}...")
        start_time = time.time()

        # Get the RAG orchestrator (now with Agentic ReAct)
        from app.services.orchestrator import get_rag_orchestrator
        from app.core.enums import RAGStrategy
        from app.core.dependencies import get_vectorstore
        
        rag_service = get_rag_orchestrator()
        vector_store = get_vectorstore()
        
        # Log current state
        total_docs = db.query(Document).count()
        total_chunks = db.query(DocumentChunk).count()
        vector_count = vector_store.get_count()
        
        logger.info(
            f"[DATABASE] Current state: {total_docs} docs, {total_chunks} chunks, "
            f"{vector_count} vectors in ChromaDB"
        )
        
        # Map strategy string to enum
        strategy_map = {
            "simple": RAGStrategy.SIMPLE,
            "agentic": RAGStrategy.AGENTIC,
            "auto": RAGStrategy.AUTO
        }

        if request.strategy not in strategy_map:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid strategy: {request.strategy}. Use: simple, agentic, or auto"
            )

        strategy = strategy_map[request.strategy]

        # Validate document exists if document_id is provided
        document_id = request.document_id
        document = None
        if document_id:
            document = db.query(Document).filter(Document.id == document_id).first()
            if not document:
                raise HTTPException(
                    status_code=404,
                    detail=f"Document with ID {document_id} not found"
                )
            logger.info(f"[QUERY] Querying document: {document.filename}")

        # ⭐ Execute query using Agentic ReAct Coordinator
        result = await rag_service.execute_query(
            query=request.query,
            top_k=request.top_k,
            session_id=request.session_id,
            document_id=document_id,
            strategy=strategy
        )

        processing_time = time.time() - start_time

        # Enhanced logging with agent steps
        retrieved_chunks = result.get("retrieved_chunks", [])
        execution_steps = result.get("execution_steps", [])
        
        logger.info(
            f"[QUERY] Retrieved {len(retrieved_chunks)} chunks, "
            f"processing time: {processing_time:.2f}s, "
            f"source: {result.get('source', 'unknown')}, "
            f"agent_steps: {len(execution_steps)}"
        )
        # Save query in DB with enhanced metadata
        db_query = Query(
            id=str(uuid.uuid4()),
            query_text=request.query,
            answer=result["answer"],
            strategy_used=request.strategy,
            processing_time=processing_time,
            confidence_score=result.get("confidence", 0.85),
            retrieved_chunks_count=len(retrieved_chunks),
            session_id=request.session_id,
            document_id=document_id,
            agent_steps_count=len(execution_steps),  # ⭐ New field
            meta_data={
                "top_k": request.top_k,
                "chunk_count": len(retrieved_chunks),
                "document_id": document_id,
                "document_filename": document.filename if document else None,
                "database_docs_count": total_docs,
                "database_chunks_count": total_chunks,
                "vector_store_count": vector_count,
                "source": result.get("source", "coordinator_agent"),
                "agent_type": result.get("agent_type", "coordinator_react"),
                "execution_steps": execution_steps,  # ⭐ ReAct trace
                "internet_sources": result.get("internet_sources", []),  # ⭐ Tavily sources
                "agent_steps_count": len(execution_steps)
            }
        )
        db.add(db_query)
        db.commit()
        db.refresh(db_query)

        logger.info(f"[QUERY] Successfully processed query with {request.strategy} strategy using ReAct Agent")
        
        # return RAGQueryResponse(
        #     query=request.query,
        #     answer=result["answer"],
        #     strategy_used=result["strategy_used"].value,
        #     processing_time=processing_time,
        #     retrieved_chunks=retrieved_chunks,
        #     confidence_score=result.get("confidence", 0.85)
        # )
        return RAGQueryResponse(
            query=request.query,
            answer=result["answer"],
            strategy_used=result["strategy_used"].value,
            processing_time=processing_time,
            retrieved_chunks=retrieved_chunks,
            confidence_score=result.get("confidence", 0.85),
            # ⭐ Add the missing agent metadata
            source=result.get("source"),
            agent_type=result.get("agent_type"),
            execution_steps=result.get("execution_steps"),
            internet_sources=result.get("internet_sources"),
            agent_steps_count=len(result.get("execution_steps", [])),
            relevance_check=None,  # Not needed in response
            fallback_used=result.get("fallback_used", False)
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[ERROR] Query processing failed: {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=500, 
            detail=f"Query processing failed: {str(e)}"
        )

        # Save query in DB with enhanced metadata
# ============================================================
# 🧹 Clear All Documents Endpoint (FIXED)
# ============================================================
# @router.delete("/documents/clear")
# async def clear_all_documents(db: Session = Depends(get_db)):
#     """
#     [DANGER] Danger Zone: Permanently delete all uploaded documents 
#     and clear vector stores.
#     """
#     try:
#         from app.models.rag_model import Query
#         from app.services.vectorstore import get_vector_store, reset_vector_store
        
#         # Count before deleting
#         total_docs = db.query(Document).count()
#         total_chunks = db.query(DocumentChunk).count()
#         total_queries = db.query(Query).count()
        
#         logger.info(f"[STATS] Before deletion: {total_docs} docs, {total_chunks} chunks, {total_queries} queries")
        
#         # 🧠 STEP 1: Clear vector stores
#         vector_count_before = 0
#         # 🧹 STEP 1: Clear vector stores - ENHANCED
#         try:
#             logger.info("[CLEAR] Step 1: Clearing vector stores...")
            
#             # Get vector store and count
#             vector_store = get_vector_store()
#             vector_count_before = vector_store.get_count()
            
#             logger.info(f"[VECTOR_STORE] Vector count before clear: {vector_count_before}")
            
#             # Clear using the fixed method
#             vector_store.clear()
            
#             # Force a completely new instance to be sure
#             reset_vector_store(force_new=True)
            
#             # Verify it's actually cleared
#             vector_store = get_vector_store()
#             vector_count_after = vector_store.get_count()
            
#             logger.info(f"[VECTOR_STORE] Vector count after clear: {vector_count_after}")
            
#             if vector_count_after != 0:
#                 logger.error(f"[ERROR] Vector store not fully cleared! Still has {vector_count_after} items")
#                 raise Exception(f"Vector store clear incomplete: {vector_count_after} items remain")
            
#             logger.info(f"[SUCCESS] Vector store cleared: {vector_count_before} vectors removed")
            
#         except Exception as e:
#             logger.error(f"[ERROR] Vector store clear failed: {str(e)}", exc_info=True)
#             raise HTTPException(
#                 status_code=500,
#                 detail=f"Failed to clear vector store: {str(e)}"
#             )
        
#         # 🧹 STEP 2: Delete from database
#         deleted_docs = 0
#         deleted_chunks = 0
#         deleted_queries = 0
        
#         try:
#             logger.info("[CLEAR] Step 2: Deleting from database...")
            
#             # Delete queries FIRST (no foreign keys pointing to it)
#             logger.info(f"[DELETE] Deleting {total_queries} queries...")
#             deleted_queries = db.query(Query).delete(synchronize_session=False)
#             db.flush()
#             logger.info(f"[SUCCESS] Deleted {deleted_queries} queries")
            
#             # Delete chunks (has foreign key to documents)
#             logger.info(f"[DELETE] Deleting {total_chunks} chunks...")
#             deleted_chunks = db.query(DocumentChunk).delete(synchronize_session=False)
#             db.flush()
#             logger.info(f"[SUCCESS] Deleted {deleted_chunks} chunks")
            
#             # Delete documents (must be last)
#             logger.info(f"[DELETE] Deleting {total_docs} documents...")
#             deleted_docs = db.query(Document).delete(synchronize_session=False)
#             db.flush()
#             logger.info(f"[SUCCESS] Deleted {deleted_docs} documents")
            
#             # Commit all changes
#             db.commit()
#             logger.info("[SUCCESS] All database deletions committed")
            
#         except Exception as e:
#             db.rollback()
#             logger.error(f"[ERROR] Database deletion failed: {str(e)}", exc_info=True)
#             raise HTTPException(
#                 status_code=500,
#                 detail=f"Failed to delete from database: {str(e)}"
#             )
        
#         # 📊 STEP 3: Final verification
#         remaining_docs = db.query(Document).count()
#         remaining_chunks = db.query(DocumentChunk).count()
#         remaining_queries = db.query(Query).count()
#         remaining_vectors = get_vector_store().get_count()
        
#         logger.info(
#             f"[STATS] After deletion: {remaining_docs} docs, "
#             f"{remaining_chunks} chunks, {remaining_queries} queries, "
#             f"{remaining_vectors} vectors"
#         )
        
#         # Check if anything remains
#         if any([remaining_docs, remaining_chunks, remaining_queries, remaining_vectors]):
#             logger.warning("[WARN] Incomplete deletion detected!")
#             return {
#                 "status": "partial_success",
#                 "message": "Some data may not have been fully cleared",
#                 "deleted": {
#                     "documents": deleted_docs,
#                     "chunks": deleted_chunks,
#                     "queries": deleted_queries,
#                     "vectors": vector_count_before
#                 },
#                 "remaining": {
#                     "documents": remaining_docs,
#                     "chunks": remaining_chunks,
#                     "queries": remaining_queries,
#                     "vectors": remaining_vectors
#                 }
#             }
        
#         # Success response
#         return {
#             "status": "success",
#             "message": (
#                 f"Successfully cleared all data: {deleted_docs} documents, "
#                 f"{deleted_chunks} chunks, {deleted_queries} queries, "
#                 f"{vector_count_before} vectors"
#             ),
#             "deleted": {
#                 "documents": deleted_docs,
#                 "chunks": deleted_chunks,
#                 "queries": deleted_queries,
#                 "vectors": vector_count_before
#             },
#             "remaining": {
#                 "documents": 0,
#                 "chunks": 0,
#                 "queries": 0,
#                 "vectors": 0
#             }
#         }
        
#     except HTTPException:
#         raise
#     except Exception as e:
#         db.rollback()
#         logger.error(f"[ERROR] Failed to clear documents: {str(e)}", exc_info=True)
#         raise HTTPException(
#             status_code=500,
#             detail=f"Failed to clear documents: {str(e)}"
#         )
@router.delete("/documents/clear")
async def clear_all_documents(db: Session = Depends(get_db)):
    """
    [DANGER] Danger Zone: Permanently delete all uploaded documents 
    and clear ChromaDB vector store.
    """
    try:
        from app.models.rag_model import Query
        from app.core.dependencies import get_vectorstore  # ✅ Use ChromaDB
        
        # Count before deleting
        total_docs = db.query(Document).count()
        total_chunks = db.query(DocumentChunk).count()
        total_queries = db.query(Query).count()
        
        logger.info(f"[STATS] Before deletion: {total_docs} docs, {total_chunks} chunks, {total_queries} queries")
        
        # 🧹 STEP 1: Clear ChromaDB
        try:
            logger.info("[CLEAR] Step 1: Clearing ChromaDB vector store...")
            
            # Get ChromaDB vector store
            vector_store = get_vectorstore()
            vector_count_before = vector_store.get_count()
            
            logger.info(f"[CHROMA_DB] Vector count before clear: {vector_count_before}")
            
            # Clear ChromaDB collection
            vector_store.reset_collection()
            
            # Verify it's actually cleared
            vector_count_after = vector_store.get_count()
            logger.info(f"[CHROMA_DB] Vector count after clear: {vector_count_after}")
            
            if vector_count_after != 0:
                logger.error(f"[ERROR] ChromaDB not fully cleared! Still has {vector_count_after} items")
                raise Exception(f"ChromaDB clear incomplete: {vector_count_after} items remain")
            
            logger.info(f"[SUCCESS] ChromaDB cleared: {vector_count_before} vectors removed")
            
        except Exception as e:
            logger.error(f"[ERROR] ChromaDB clear failed: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Failed to clear vector store: {str(e)}"
            )
        
        # 🧹 STEP 2: Delete from database (your existing code)
        deleted_docs = 0
        deleted_chunks = 0
        deleted_queries = 0
        
        try:
            logger.info("[CLEAR] Step 2: Deleting from database...")
            
            # Delete queries FIRST (no foreign keys pointing to it)
            logger.info(f"[DELETE] Deleting {total_queries} queries...")
            deleted_queries = db.query(Query).delete(synchronize_session=False)
            db.flush()
            logger.info(f"[SUCCESS] Deleted {deleted_queries} queries")
            
            # Delete chunks (has foreign key to documents)
            logger.info(f"[DELETE] Deleting {total_chunks} chunks...")
            deleted_chunks = db.query(DocumentChunk).delete(synchronize_session=False)
            db.flush()
            logger.info(f"[SUCCESS] Deleted {deleted_chunks} chunks")
            
            # Delete documents (must be last)
            logger.info(f"[DELETE] Deleting {total_docs} documents...")
            deleted_docs = db.query(Document).delete(synchronize_session=False)
            db.flush()
            logger.info(f"[SUCCESS] Deleted {deleted_docs} documents")
            
            # Commit all changes
            db.commit()
            logger.info("[SUCCESS] All database deletions committed")
            
        except Exception as e:
            db.rollback()
            logger.error(f"[ERROR] Database deletion failed: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Failed to delete from database: {str(e)}"
            )
        
        # 📊 STEP 3: Final verification
        remaining_docs = db.query(Document).count()
        remaining_chunks = db.query(DocumentChunk).count()
        remaining_queries = db.query(Query).count()
        remaining_vectors = get_vectorstore().get_count()
        
        logger.info(
            f"[STATS] After deletion: {remaining_docs} docs, "
            f"{remaining_chunks} chunks, {remaining_queries} queries, "
            f"{remaining_vectors} vectors"
        )
        
        # Check if anything remains
        if any([remaining_docs, remaining_chunks, remaining_queries, remaining_vectors]):
            logger.warning("[WARN] Incomplete deletion detected!")
            return {
                "status": "partial_success",
                "message": "Some data may not have been fully cleared",
                "deleted": {
                    "documents": deleted_docs,
                    "chunks": deleted_chunks,
                    "queries": deleted_queries,
                    "vectors": vector_count_before
                },
                "remaining": {
                    "documents": remaining_docs,
                    "chunks": remaining_chunks,
                    "queries": remaining_queries,
                    "vectors": remaining_vectors
                }
            }
        
        # Success response
        return {
            "status": "success",
            "message": (
                f"Successfully cleared all data: {deleted_docs} documents, "
                f"{deleted_chunks} chunks, {deleted_queries} queries, "
                f"{vector_count_before} vectors"
            ),
            "deleted": {
                "documents": deleted_docs,
                "chunks": deleted_chunks,
                "queries": deleted_queries,
                "vectors": vector_count_before
            },
            "remaining": {
                "documents": 0,
                "chunks": 0,
                "queries": 0,
                "vectors": 0
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"[ERROR] Failed to clear documents: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to clear documents: {str(e)}"
        )


# # ============================================================
# # 📤 Document Upload Endpoint
# # ============================================================
# from PyPDF2 import PdfReader

# try:
#     import docx  # python-docx
# except Exception:
#     docx = None


# def extract_text_from_pdf_bytes(pdf_bytes):
#     """Extract text from PDF bytes with enhanced error handling"""
#     try:
#         reader = PdfReader(io.BytesIO(pdf_bytes))
#         text = ""
#         for page_num, page in enumerate(reader.pages):
#             try:
#                 page_text = page.extract_text() or ""
#                 text += page_text
#                 logger.debug(f"[DEBUG] Extracted {len(page_text)} chars from page {page_num + 1}")
#             except Exception as e:
#                 logger.warning(f"[WARN] Failed to extract text from page {page_num + 1}: {str(e)}")
#                 continue
#         return text
#     except Exception as e:
#         logger.error(f"[ERROR] PDF extraction failed: {str(e)}")
#         raise RuntimeError(f"Failed to extract text from PDF: {str(e)}")


# def extract_text_from_docx_bytes(file_bytes: bytes) -> str:
#     """Extract text from DOCX bytes with enhanced error handling"""
#     if docx is None:
#         raise RuntimeError("python-docx is not installed. Install with: pip install python-docx")
    
#     try:
#         doc = docx.Document(io.BytesIO(file_bytes))
#         paragraphs = [p.text for p in doc.paragraphs if p.text]
#         text = "\n".join(paragraphs)
        
#         # Also extract text from tables
#         for table in doc.tables:
#             for row in table.rows:
#                 for cell in row.cells:
#                     if cell.text and cell.text.strip():
#                         text += "\n" + cell.text
        
#         return text.strip()
#     except Exception as e:
#         logger.error(f"[ERROR] DOCX extraction failed: {str(e)}")
#         raise RuntimeError(f"Failed to extract text from DOCX: {str(e)}")


# def extract_text_from_txt_bytes(file_bytes: bytes) -> str:
#     """Extract text from TXT bytes with enhanced encoding detection"""
#     encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1', 'utf-16']
    
#     for encoding in encodings:
#         try:
#             text = file_bytes.decode(encoding)
#             # Validate that we got meaningful text
#             if text.strip() and any(char.isalnum() for char in text):
#                 logger.debug(f"[DEBUG] Successfully decoded with {encoding}")
#                 return text
#         except UnicodeDecodeError:
#             continue
#         except Exception as e:
#             logger.warning(f"[WARN] Encoding {encoding} failed: {str(e)}")
#             continue
    
#     # Fallback: decode with utf-8 ignoring errors
#     logger.warning("[WARN] All encodings failed, using utf-8 with ignore errors")
#     return file_bytes.decode("utf-8", errors="ignore")


# # ✅ Update the response model to include processing_time as string
# class DocumentUploadResponse(BaseModel):
#     document_id: str
#     filename: str
#     status: str
#     chunks_created: int
#     message: str
#     processing_time: str


# @router.post("/upload", response_model=DocumentUploadResponse)
# async def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db)):
#     """Upload and process document for RAG (PDF, TXT, DOCX) with enhanced monitoring and error handling."""
#     start_time = time.time()
#     processing_metrics = {
#         'extraction_time': 0,
#         'chunking_time': 0,
#         'db_operations_time': 0,
#         'vector_store_time': 0,
#         'total_chars_processed': 0
#     }
    
#     try:
#         logger.info(f"[UPLOAD] Received file upload: {file.filename} (Size: {file.size or 'unknown'})")

#         # Validate file type
#         allowed_types = [
#             "application/pdf",
#             "text/plain",
#             "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
#         ]
        
#         if file.content_type not in allowed_types:
#             # Also check by file extension as fallback
#             file_extension = file.filename.lower().split('.')[-1] if '.' in file.filename else ''
#             if file_extension not in ['pdf', 'txt', 'docx']:
#                 raise HTTPException(
#                     status_code=400,
#                     detail=f"File type not supported. Allowed: PDF, TXT, DOCX. Got: {file.content_type}"
#                 )
#             else:
#                 logger.info(f"[INFO] Using file extension {file_extension} for content type detection")

#         # Read bytes
#         content = await file.read()
#         if len(content) == 0:
#             raise HTTPException(status_code=400, detail="Uploaded file is empty")

#         file_size_mb = len(content) / (1024 * 1024)
#         logger.info(f"[FILE] File size: {len(content)} bytes ({file_size_mb:.2f} MB)")

#         # Extract text based on content type with timing
#         extraction_start = time.time()
#         try:
#             if file.content_type == "application/pdf":
#                 text = extract_text_from_pdf_bytes(content)
#             elif file.content_type == "text/plain":
#                 text = extract_text_from_txt_bytes(content)
#             elif file.content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
#                 text = extract_text_from_docx_bytes(content)
#             else:
#                 # Fallback: try to detect by extension
#                 if file.filename.lower().endswith('.pdf'):
#                     text = extract_text_from_pdf_bytes(content)
#                 elif file.filename.lower().endswith('.docx'):
#                     text = extract_text_from_docx_bytes(content)
#                 else:
#                     text = extract_text_from_txt_bytes(content)
#         except Exception as e:
#             raise HTTPException(status_code=400, detail=f"Text extraction failed: {str(e)}")
        
#         processing_metrics['extraction_time'] = time.time() - extraction_start

#         # Enhanced text validation
#         if not text or text.strip() == "":
#             logger.warning(f"[WARN] No extractable text found in {file.filename}, content type: {file.content_type}")
#             raise HTTPException(status_code=400, detail="No extractable text found in uploaded document")

#         # Check if text is meaningful (not just whitespace/formatting)
#         clean_text = text.strip()
#         if len(clean_text) < 10:
#             logger.warning(f"[WARN] Very little text extracted from {file.filename}: {len(clean_text)} chars")
#             raise HTTPException(status_code=400, detail="Extracted text appears to be too short or invalid")

#         processing_metrics['total_chars_processed'] = len(clean_text)
#         logger.info(f"[TEXT] Extracted {len(clean_text)} characters from document")

#         # Chunk the extracted text with timing
#         chunking_start = time.time()
#         chunks = chunk_text(clean_text)
#         processing_metrics['chunking_time'] = time.time() - chunking_start

#         # Validate chunks
#         if not isinstance(chunks, list):
#             raise HTTPException(status_code=500, detail="chunk_text did not return a list of chunks")

#         if not chunks:
#             raise HTTPException(status_code=400, detail="No chunks generated from document text")

#         if len(chunks) == 0:
#             raise HTTPException(status_code=400, detail="Empty chunks list generated")

#         logger.info(f"[CHUNKS] Generated {len(chunks)} chunks for file {file.filename}")

#         # Calculate chunk statistics
#         chunk_sizes = []
#         for chunk in chunks:
#             chunk_text_content = chunk.get("content") if isinstance(chunk, dict) else chunk
#             if chunk_text_content:
#                 chunk_sizes.append(len(chunk_text_content))

#         if chunk_sizes:
#             logger.info(f"[STATS] Chunk sizes: min={min(chunk_sizes)}, max={max(chunk_sizes)}, avg={sum(chunk_sizes)/len(chunk_sizes):.0f}")

#         # ✅ Create document ID and DB record within transaction
#         doc_id = str(uuid.uuid4())
#         db_operations_start = time.time()
        
#         try:
#             db_doc = Document(
#                 id=doc_id,
#                 filename=file.filename,
#                 content_type=file.content_type,
#                 size=len(content),
#                 status="processing",
#                 chunks_count=0,
#                 uploaded_at=datetime.utcnow(),
#                 meta_data={
#                     "original_size": len(content),
#                     "processing_method": "local_extraction",
#                     "extracted_chars": len(clean_text),
#                     "chunks_generated": len(chunks)
#                 }
#             )
#             db.add(db_doc)
#             db.flush()

#             # Add chunks to vector store and database
#             vector_store = get_vector_store()
#             vector_store_start = time.time()
            
#             chunks_created = 0
#             failed_chunks = 0
#             chunk_details = []

#             for idx, chunk in enumerate(chunks):
#                 try:
#                     chunk_text_content = chunk.get("content") if isinstance(chunk, dict) else chunk
#                     if not chunk_text_content or not chunk_text_content.strip():
#                         logger.warning(f"[WARN] Skipping empty chunk at index {idx}")
#                         failed_chunks += 1
#                         continue

#                     chunk_id = str(uuid.uuid4())

#                     # Create database chunk record
#                     db_chunk = DocumentChunk(
#                         id=chunk_id,
#                         document_id=doc_id,
#                         content=chunk_text_content,
#                         chunk_index=idx,
#                         meta_data={
#                             "source": file.filename,
#                             "content_type": file.content_type,
#                             "chunk_size": len(chunk_text_content),
#                             "chunk_chars": len(chunk_text_content)
#                         },
#                         created_at=datetime.utcnow()
#                     )
#                     db.add(db_chunk)

#                     # Add to vector store
#                     vector_store.add_document(
#                         text=chunk_text_content,
#                         metadata={
#                             "chunk_id": chunk_id,
#                             "chunk_index": idx,
#                             "document_id": doc_id,
#                             "source": file.filename,
#                             "content_type": file.content_type,
#                             "chunk_size": len(chunk_text_content)
#                         }
#                     )
#                     chunks_created += 1
#                     chunk_details.append({
#                         "index": idx,
#                         "size": len(chunk_text_content),
#                         "status": "success"
#                     })

#                 except Exception as e:
#                     logger.error(f"[ERROR] Failed to process chunk {idx}: {str(e)}")
#                     failed_chunks += 1
#                     chunk_details.append({
#                         "index": idx,
#                         "size": len(chunk_text_content) if chunk_text_content else 0,
#                         "status": "failed",
#                         "error": str(e)
#                     })
#                     continue

#             processing_metrics['vector_store_time'] = time.time() - vector_store_start

#             # Update document record
#             db_doc.status = "completed" if chunks_created > 0 else "failed"
#             db_doc.chunks_count = chunks_created
#             db_doc.processed_at = datetime.utcnow()
#             db_doc.meta_data.update({
#                 "chunks_created": chunks_created,
#                 "chunks_failed": failed_chunks,
#                 "processing_metrics": processing_metrics,
#                 "chunk_details": chunk_details
#             })

#             processing_metrics['db_operations_time'] = time.time() - db_operations_start

#             # Commit transaction
#             db.commit()
#             db.refresh(db_doc)

#         except Exception as e:
#             db.rollback()
#             logger.error(f"[ERROR] Database transaction failed: {str(e)}")
#             raise HTTPException(status_code=500, detail=f"Database operation failed: {str(e)}")

#         # Log final statistics
#         total_processing_time = time.time() - start_time
#         logger.info(f"[SUCCESS] Upload complete: {chunks_created} chunks created, {failed_chunks} failed")
#         logger.info(f"[TIME] Processing times - Total: {total_processing_time:.2f}s, "
#                    f"Extraction: {processing_metrics['extraction_time']:.2f}s, "
#                    f"Chunking: {processing_metrics['chunking_time']:.2f}s, "
#                    f"DB: {processing_metrics['db_operations_time']:.2f}s, "
#                    f"Vector: {processing_metrics['vector_store_time']:.2f}s")

#         # Optional: get vector count
#         try:
#             vector_count = vector_store.get_count()
#             logger.info(f"[VECTOR] Vector store now contains {vector_count} total vectors")
#         except Exception as e:
#             logger.warning(f"[WARN] Could not retrieve vector count: {str(e)}")

#         # ✅ Format processing time as "4.4 seconds"
#         formatted_time = f"{total_processing_time:.1f} seconds"

#         # ✅ Return the response with processing_time as formatted string
#         return DocumentUploadResponse(
#             document_id=db_doc.id,
#             filename=file.filename,
#             status="success",
#             chunks_created=chunks_created,
#             message=f"Document '{file.filename}' processed successfully with {chunks_created} chunks",
#             processing_time=formatted_time
#         )

#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"[ERROR] Document upload failed: {str(e)}", exc_info=True)
#         try:
#             db.rollback()
#         except Exception:
#             pass  # Already rolled back or no transaction
#         raise HTTPException(status_code=500, detail=f"Document upload failed: {str(e)}")
    
from app.core.dependencies import get_vectorstore, get_embedding_service
@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Upload and process document for RAG (PDF, TXT, DOCX) - FIXED for ChromaDB"""
    start_time = time.time()
    processing_metrics = {
        'extraction_time': 0,
        'chunking_time': 0,
        'db_operations_time': 0,
        'vector_store_time': 0,
        'total_chars_processed': 0
    }
    
    try:
        logger.info(f"[UPLOAD] Received file upload: {file.filename} (Size: {file.size or 'unknown'})")

        # Validate file type
        allowed_types = [
            "application/pdf",
            "text/plain",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        ]
        
        if file.content_type not in allowed_types:
            file_extension = file.filename.lower().split('.')[-1] if '.' in file.filename else ''
            if file_extension not in ['pdf', 'txt', 'docx']:
                raise HTTPException(
                    status_code=400,
                    detail=f"File type not supported. Allowed: PDF, TXT, DOCX. Got: {file.content_type}"
                )

        # Read bytes
        content = await file.read()
        if len(content) == 0:
            raise HTTPException(status_code=400, detail="Uploaded file is empty")

        file_size_mb = len(content) / (1024 * 1024)
        logger.info(f"[FILE] File size: {len(content)} bytes ({file_size_mb:.2f} MB)")

        # Extract text based on content type
        extraction_start = time.time()
        try:
            if file.content_type == "application/pdf":
                text = extract_text_from_pdf_bytes(content)
            elif file.content_type == "text/plain":
                text = extract_text_from_txt_bytes(content)
            elif file.content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                text = extract_text_from_docx_bytes(content)
            else:
                # Fallback: try to detect by extension
                if file.filename.lower().endswith('.pdf'):
                    text = extract_text_from_pdf_bytes(content)
                elif file.filename.lower().endswith('.docx'):
                    text = extract_text_from_docx_bytes(content)
                else:
                    text = extract_text_from_txt_bytes(content)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Text extraction failed: {str(e)}")
        
        processing_metrics['extraction_time'] = time.time() - extraction_start

        # Enhanced text validation
        if not text or text.strip() == "":
            logger.warning(f"[WARN] No extractable text found in {file.filename}")
            raise HTTPException(status_code=400, detail="No extractable text found in uploaded document")

        clean_text = text.strip()
        if len(clean_text) < 10:
            logger.warning(f"[WARN] Very little text extracted from {file.filename}: {len(clean_text)} chars")
            raise HTTPException(status_code=400, detail="Extracted text appears to be too short or invalid")

        processing_metrics['total_chars_processed'] = len(clean_text)
        logger.info(f"[TEXT] Extracted {len(clean_text)} characters from document")

        # Chunk the extracted text
        chunking_start = time.time()
        chunks = chunk_text(clean_text)
        processing_metrics['chunking_time'] = time.time() - chunking_start

        # Validate chunks
        if not isinstance(chunks, list) or not chunks:
            raise HTTPException(status_code=400, detail="No chunks generated from document text")

        logger.info(f"[CHUNKS] Generated {len(chunks)} chunks for file {file.filename}")

        # ✅ CRITICAL FIX: Use ChromaDB vector store instead of in-memory
        
        
        vector_store = get_vectorstore()  # ✅ ChromaDB
        embedding_service = get_embedding_service()
        
        # ✅ DEBUG: Check current ChromaDB state
        chroma_count_before = vector_store.get_count()
        logger.info(f"[CHROMA_DEBUG] ChromaDB count before upload: {chroma_count_before}")

        # Create document ID and DB record
        doc_id = str(uuid.uuid4())
        db_operations_start = time.time()
        
        try:
            db_doc = Document(
                id=doc_id,
                filename=file.filename,
                content_type=file.content_type,
                size=len(content),
                status="processing",
                chunks_count=0,
                uploaded_at=datetime.utcnow(),
                meta_data={
                    "original_size": len(content),
                    "processing_method": "chromadb_extraction",
                    "extracted_chars": len(clean_text),
                    "chunks_generated": len(chunks)
                }
            )
            db.add(db_doc)
            db.flush()

            # ✅ FIXED: Generate embeddings and add to ChromaDB
            vector_store_start = time.time()
            
            chunks_created = 0
            failed_chunks = 0
            chunk_details = []

            # Prepare data for ChromaDB batch upload
            documents_to_add = []
            embeddings_to_add = []
            metadatas_to_add = []
            ids_to_add = []

            for idx, chunk in enumerate(chunks):
                try:
                    chunk_text_content = chunk.get("content") if isinstance(chunk, dict) else chunk
                    if not chunk_text_content or not chunk_text_content.strip():
                        logger.warning(f"[WARN] Skipping empty chunk at index {idx}")
                        failed_chunks += 1
                        continue

                    chunk_id = str(uuid.uuid4())

                    # Create database chunk record
                    db_chunk = DocumentChunk(
                        id=chunk_id,
                        document_id=doc_id,
                        content=chunk_text_content,
                        chunk_index=idx,
                        meta_data={
                            "source": file.filename,
                            "content_type": file.content_type,
                            "chunk_size": len(chunk_text_content),
                            "chunk_chars": len(chunk_text_content)
                        },
                        created_at=datetime.utcnow()
                    )
                    db.add(db_chunk)

                    # Prepare for ChromaDB batch upload
                    documents_to_add.append(chunk_text_content)
                    metadatas_to_add.append({
                        "chunk_id": chunk_id,
                        "chunk_index": idx,
                        "document_id": doc_id,
                        "source": file.filename,
                        "content_type": file.content_type,
                        "chunk_size": len(chunk_text_content)
                    })
                    ids_to_add.append(chunk_id)
                    
                    chunks_created += 1
                    chunk_details.append({
                        "index": idx,
                        "size": len(chunk_text_content),
                        "status": "success"
                    })

                except Exception as e:
                    logger.error(f"[ERROR] Failed to process chunk {idx}: {str(e)}")
                    failed_chunks += 1
                    chunk_details.append({
                        "index": idx,
                        "size": len(chunk_text_content) if chunk_text_content else 0,
                        "status": "failed",
                        "error": str(e)
                    })
                    continue

            # ✅ Generate embeddings and add to ChromaDB in batch
            if documents_to_add:
                logger.info(f"[CHROMA] Generating embeddings for {len(documents_to_add)} chunks...")
                embeddings_to_add = embedding_service.embed_texts(documents_to_add)
                
                logger.info(f"[CHROMA] Adding {len(documents_to_add)} chunks to ChromaDB...")
                vector_store.add_documents(
                    documents=documents_to_add,
                    embeddings=embeddings_to_add,
                    metadata=metadatas_to_add,
                    ids=ids_to_add
                )
                logger.info(f"[CHROMA] Successfully added {len(documents_to_add)} chunks to ChromaDB")

            processing_metrics['vector_store_time'] = time.time() - vector_store_start

            # Update document record
            db_doc.status = "completed" if chunks_created > 0 else "failed"
            db_doc.chunks_count = chunks_created
            db_doc.processed_at = datetime.utcnow()
            db_doc.meta_data.update({
                "chunks_created": chunks_created,
                "chunks_failed": failed_chunks,
                "processing_metrics": processing_metrics,
                "chunk_details": chunk_details
            })

            processing_metrics['db_operations_time'] = time.time() - db_operations_start

            # Commit transaction
            db.commit()
            db.refresh(db_doc)

            # ✅ VERIFICATION: Check ChromaDB after upload
            chroma_count_after = vector_store.get_count()
            doc_chunks_in_chroma = vector_store.get_documents_by_id(doc_id)
            
            logger.info(f"[CHROMA_VERIFY] ChromaDB count after upload: {chroma_count_after}")
            logger.info(f"[CHROMA_VERIFY] Document chunks in ChromaDB: {len(doc_chunks_in_chroma)}")

        except Exception as e:
            db.rollback()
            logger.error(f"[ERROR] Database transaction failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Database operation failed: {str(e)}")

        # Log final statistics
        total_processing_time = time.time() - start_time
        logger.info(f"[SUCCESS] Upload complete: {chunks_created} chunks created, {failed_chunks} failed")
        logger.info(f"[TIME] Processing times - Total: {total_processing_time:.2f}s")

        # ✅ Format processing time as "4.4 seconds"
        formatted_time = f"{total_processing_time:.1f} seconds"

        return DocumentUploadResponse(
            document_id=db_doc.id,
            filename=file.filename,
            status="success",
            chunks_created=chunks_created,
            message=f"Document '{file.filename}' processed successfully with {chunks_created} chunks",
            processing_time=formatted_time
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[ERROR] Document upload failed: {str(e)}", exc_info=True)
        try:
            db.rollback()
        except Exception:
            pass
        raise HTTPException(status_code=500, detail=f"Document upload failed: {str(e)}")



    

@router.get("/debug/rag-service")
async def debug_rag_service():
    """Debug the RAG service to see what vector store it uses"""
    rag_service = get_rag_service()
    
    debug_info = {
        "rag_service_type": type(rag_service).__name__,
        "rag_service_module": rag_service.__module__,
    }
    
    # Check if RAG service has a vector store attribute
    if hasattr(rag_service, 'vector_store'):
        vs = rag_service.vector_store
        debug_info["vector_store_info"] = {
            "type": type(vs).__name__,
            "count": getattr(vs, 'get_count', lambda: 'unknown')(),
            "documents_count": len(getattr(vs, 'documents', [])),
            "module": vs.__module__
        }
    
    # Check for other common vector store attributes
    for attr in ['vs', 'vectorstore', 'store', 'embedding_store']:
        if hasattr(rag_service, attr):
            vs = getattr(rag_service, attr)
            debug_info[f"vector_store_{attr}"] = {
                "type": type(vs).__name__,
                "count": getattr(vs, 'get_count', lambda: 'unknown')(),
                "module": vs.__module__
            }
    
    return debug_info



@router.get("/debug/vector-store")
async def debug_vector_store():
    """Debug endpoint to check vector store state"""
    from app.services.vectorstore import get_vector_store
    
    vector_store = get_vector_store()
    
    return {
        "vector_store_instance_id": id(vector_store),
        "in_memory_documents_count": len(vector_store.documents),
        "in_memory_embeddings_count": len(vector_store.embeddings),
        "in_memory_metadata_count": len(vector_store.metadata),
        "get_count_result": vector_store.get_count(),
        "documents_sample": vector_store.documents[:2] if vector_store.documents else [],
        "is_faiss_used": vector_store.index is not None
    }

@router.get("/debug/database-chunks")
async def debug_database_chunks(db: Session = Depends(get_db)):
    """Check if there are any document chunks in the database"""
    chunks = db.query(DocumentChunk).all()
    
    return {
        "total_chunks": len(chunks),
        "chunks_sample": [
            {
                "id": chunk.id,
                "document_id": chunk.document_id,
                "content_preview": chunk.content[:100] + "..." if chunk.content else "",
                "created_at": chunk.created_at
            } for chunk in chunks[:5]  # First 5 chunks
        ] if chunks else []
    }
# ============================================================
# 📄 Document Management
# ============================================================
@router.get("/documents")
async def list_documents(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    try:
        documents = db.query(Document).offset(skip).limit(limit).all()
        total_count = db.query(Document).count()
        return {
            "total": total_count,
            "count": len(documents),
            "documents": [
                {
                    "id": d.id,
                    "filename": d.filename,
                    "content_type": d.content_type,
                    "size": d.size,
                    "status": d.status,
                    "chunks_count": d.chunks_count,
                    "uploaded_at": d.uploaded_at.isoformat() if d.uploaded_at else None,
                    "processed_at": d.processed_at.isoformat() if d.processed_at else None
                }
                for d in documents
            ]
        }
    except Exception as e:
        logger.error(f"[ERROR] Failed to fetch documents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/documents/{document_id}")
async def get_document(document_id: str, db: Session = Depends(get_db)):
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return {
        "id": document.id,
        "filename": document.filename,
        "content_type": document.content_type,
        "size": document.size,
        "status": document.status,
        "chunks_count": document.chunks_count,
        "uploaded_at": document.uploaded_at,
        "processed_at": document.processed_at,
        "metadata": document.metadata
    }


@router.delete("/documents/{document_id}")
async def delete_document(document_id: str, db: Session = Depends(get_db)):
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    filename = document.filename
    db.delete(document)
    db.commit()
    return {"status": "success", "message": f"Document '{filename}' deleted successfully"}


# ============================================================
# 📝 Query History
# ============================================================
@router.get("/queries")
async def list_queries(limit: int = 10, skip: int = 0, db: Session = Depends(get_db)):
    queries = db.query(QueryModel).order_by(QueryModel.created_at.desc()).offset(skip).limit(limit).all()
    total = db.query(QueryModel).count()
    return {
        "total": total,
        "count": len(queries),
        "queries": [
            {
                "id": q.id,
                "query": q.query_text,
                "answer": (q.answer[:200] + "...") if q.answer and len(q.answer) > 200 else q.answer,
                "strategy": q.strategy_used,
                "processing_time": q.processing_time,
                "confidence_score": q.confidence_score,
                "created_at": q.created_at.isoformat() if q.created_at else None
            }
            for q in queries
        ]
    }


@router.get("/queries/{query_id}")
async def get_query(query_id: str, db: Session = Depends(get_db)):
    query = db.query(QueryModel).filter(QueryModel.id == query_id).first()
    if not query:
        raise HTTPException(status_code=404, detail="Query not found")
    return {
        "id": query.id,
        "query_text": query.query_text,
        "answer": query.answer,
        "strategy_used": query.strategy_used,
        "processing_time": query.processing_time,
        "confidence_score": query.confidence_score,
        "created_at": query.created_at
    }


# ============================================================
# 🧪 Health & Stats
# ============================================================
@router.get("/health", response_model=HealthCheckResponse)
async def health_check(db: Session = Depends(get_db)):
    """
    Comprehensive health check including Tavily API
    """
    from sqlalchemy import text
    import os

    components = {
        "database": "unknown",
        "llm_service": "unknown",
        "embedding_service": "unknown",
        "vector_store": "unknown",
        "tavily_api": "unknown",  # ⭐ New component
        "coordinator_agent": "unknown",  # ⭐ New component
    }

    all_healthy = True

    # 1. Test Database
    try:
        db.execute(text("SELECT 1"))
        components["database"] = "operational"
    except Exception as e:
        components["database"] = f"error: {str(e)}"
        all_healthy = False

    # 2. Test LLM Service (Groq)
    rag_service = None
    try:
        rag_service = get_rag_service()
        test_response = await rag_service.llm_service.generate(
            "Say 'OK' if you can read this.",
            temperature=0.1,
            max_tokens=10
        )

        if test_response and len(test_response) > 0:
            components["llm_service"] = "operational"
        else:
            components["llm_service"] = "error: empty response"
            all_healthy = False

    except Exception as e:
        components["llm_service"] = f"error: {str(e)}"
        all_healthy = False

    # 3. Test Embedding Service
    try:
        if rag_service:
            test_embedding = rag_service.embedding_service.embed_text("test")
            if test_embedding and len(test_embedding) > 0:
                components["embedding_service"] = "operational"
            else:
                components["embedding_service"] = "error: no embedding generated"
                all_healthy = False
    except Exception as e:
        components["embedding_service"] = f"error: {str(e)}"
        all_healthy = False

    # 4. Test Vector Store
    try:
        if rag_service:
            _ = rag_service.vectorstore.get_count()
            components["vector_store"] = "operational"
    except Exception as e:
        components["vector_store"] = f"error: {str(e)}"
        all_healthy = False

    # 5. ⭐ Test Tavily API
    try:
        tavily_key = os.getenv("TAVILY_API_KEY")
        if tavily_key:
            from tavily import TavilyClient
            tavily_client = TavilyClient(api_key=tavily_key)
            
            # Quick test search
            test_result = tavily_client.search(
                query="test",
                search_depth="basic",
                max_results=1
            )
            
            if test_result:
                components["tavily_api"] = "operational"
            else:
                components["tavily_api"] = "error: no response"
        else:
            components["tavily_api"] = "disabled: no API key"
    except Exception as e:
        components["tavily_api"] = f"error: {str(e)}"
        # Don't mark as unhealthy - Tavily is optional

    # 6. ⭐ Test Coordinator Agent
    try:
        from app.services.orchestrator import get_rag_orchestrator
        orchestrator = get_rag_orchestrator()
        
        if orchestrator and orchestrator.coordinator:
            components["coordinator_agent"] = "operational"
        else:
            components["coordinator_agent"] = "error: not initialized"
            all_healthy = False
    except Exception as e:
        components["coordinator_agent"] = f"error: {str(e)}"
        all_healthy = False

    # Overall status
    status = "healthy" if all_healthy else "degraded"

    return HealthCheckResponse(
        status=status,
        timestamp=datetime.now(),
        version="2.1.0-agentic",  # ⭐ Updated version
        components=components
    )

@router.get("/health/detailed")
async def detailed_health_check(db: Session = Depends(get_db)):
    """
    Detailed health check with performance metrics
    """
    from sqlalchemy import text
    import time
    
    results = {
        "overall_status": "checking...",
        "timestamp": datetime.now().isoformat(),
        "checks": {}
    }
    
    # Database Check
    db_start = time.time()
    try:
        db.execute(text("SELECT 1"))
        results["checks"]["database"] = {
            "status": "healthy",
            "response_time_ms": round((time.time() - db_start) * 1000, 2),
            "message": "Database connection successful"
        }
    except Exception as e:
        results["checks"]["database"] = {
            "status": "unhealthy",
            "response_time_ms": round((time.time() - db_start) * 1000, 2),
            "error": str(e)
        }
    
    # LLM Service Check (Groq)
    llm_start = time.time()
    try:
        rag_service = get_rag_service()
        test_response = await rag_service.llm_service.generate(
            "Respond with exactly: 'Health check OK'",
            temperature=0,
            max_tokens=20
        )
        
        results["checks"]["llm_service"] = {
            "status": "healthy",
            "response_time_ms": round((time.time() - llm_start) * 1000, 2),
            "model": os.getenv("LLM_MODEL", "llama-3.1-8b-instant"),
            "provider": "Groq",
            "test_response": test_response[:50] if test_response else None,
            "message": "LLM API responding correctly"
        }
    except Exception as e:
        results["checks"]["llm_service"] = {
            "status": "unhealthy",
            "response_time_ms": round((time.time() - llm_start) * 1000, 2),
            "error": str(e),
            "message": "Failed to connect to Groq API"
        }
    
    # Embedding Service Check
    embed_start = time.time()
    try:
        test_text = "Health check test"
        embedding = rag_service.embedding_service.embed_text(test_text)
        
        results["checks"]["embedding_service"] = {
            "status": "healthy",
            "response_time_ms": round((time.time() - embed_start) * 1000, 2),
            "model": os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"),
            "embedding_dimension": len(embedding) if embedding else 0,
            "message": "Embedding service working"
        }
    except Exception as e:
        results["checks"]["embedding_service"] = {
            "status": "unhealthy",
            "response_time_ms": round((time.time() - embed_start) * 1000, 2),
            "error": str(e)
        }
    
    # Vector Store Check
    vector_start = time.time()
    try:
        count = rag_service.vectorstore.get_count()
        
        # Try a test search
        test_embedding = rag_service.embedding_service.embed_text("test query")
        search_results = rag_service.vectorstore.search(test_embedding, top_k=1)
        
        results["checks"]["vector_store"] = {
            "status": "healthy",
            "response_time_ms": round((time.time() - vector_start) * 1000, 2),
            "total_documents": count,
            "search_working": len(search_results) >= 0,
            "message": f"Vector store operational with {count} documents"
        }
    except Exception as e:
        results["checks"]["vector_store"] = {
            "status": "unhealthy",
            "response_time_ms": round((time.time() - vector_start) * 1000, 2),
            "error": str(e)
        }
    
    # RAG Pipeline End-to-End Test
    rag_start = time.time()
    try:
        # Only test if we have documents
        if rag_service.vectorstore.get_count() > 0:
            test_result = await rag_service.execute_query(
                query="test health check",
                top_k=1,
                strategy=RAGStrategy.SIMPLE
            )
            
            results["checks"]["rag_pipeline"] = {
                "status": "healthy",
                "response_time_ms": round((time.time() - rag_start) * 1000, 2),
                "answer_generated": len(test_result.get("answer", "")) > 0,
                "chunks_retrieved": len(test_result.get("retrieved_chunks", [])),
                "message": "Full RAG pipeline working"
            }
        else:
            results["checks"]["rag_pipeline"] = {
                "status": "ready",
                "response_time_ms": 0,
                "message": "No documents indexed yet - upload documents to test"
            }
    except Exception as e:
        results["checks"]["rag_pipeline"] = {
            "status": "unhealthy",
            "response_time_ms": round((time.time() - rag_start) * 1000, 2),
            "error": str(e)
        }
    
    # Determine overall status
    unhealthy_count = sum(
        1 for check in results["checks"].values() 
        if check.get("status") == "unhealthy"
    )
    
    if unhealthy_count == 0:
        results["overall_status"] = "healthy"
    elif unhealthy_count <= 2:
        results["overall_status"] = "degraded"
    else:
        results["overall_status"] = "unhealthy"
    
    # Add system stats
    results["statistics"] = {
        "total_documents": db.query(Document).count(),
        "total_queries": db.query(QueryModel).count(),
        "total_chunks": rag_service.vectorstore.get_count(),
        "active_sessions": db.query(SessionModel).filter(SessionModel.is_active == True).count()
    }
    
    return results


@router.get("/health/quick")
async def quick_health_check():
    """
    Quick health check without testing external services
    Useful for load balancers
    """
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "service": "RAG System",
        "version": "2.0.0"
    }


@router.get("/stats")
async def get_statistics(db: Session = Depends(get_db)):
    from sqlalchemy import func
    total_docs = db.query(Document).count()
    total_queries = db.query(QueryModel).count()
    total_chunks = db.query(func.sum(Document.chunks_count)).scalar() or 0
    avg_time = db.query(func.avg(QueryModel.processing_time)).scalar() or 0
    strategy_stats = db.query(
        QueryModel.strategy_used,
        func.count(QueryModel.id)
    ).group_by(QueryModel.strategy_used).all()

    return {
        "total_documents": total_docs,
        "total_queries": total_queries,
        "total_chunks": int(total_chunks),
        "average_processing_time": float(avg_time),
        "strategy_distribution": {s: c for s, c in strategy_stats}
    }


# ============================================================
# 💬 Session Endpoints
# ============================================================
@router.post("/sessions")
async def create_session(user_id: str = None, db: Session = Depends(get_db)):
    session = SessionModel(
        id=str(uuid.uuid4()),
        user_id=user_id,
        started_at=datetime.utcnow(),
        last_activity=datetime.utcnow(),
        is_active=True
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return {
        "session_id": session.id,
        "user_id": session.user_id,
        "started_at": session.started_at.isoformat(),
        "status": "active"
    }


@router.get("/sessions/{session_id}")
async def get_session(session_id: str, db: Session = Depends(get_db)):
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    queries = db.query(QueryModel).filter(
        QueryModel.session_id == session_id
    ).order_by(QueryModel.created_at.asc()).all()

    return {
        "session_id": session.id,
        "user_id": session.user_id,
        "started_at": session.started_at.isoformat(),
        "last_activity": session.last_activity.isoformat(),
        "is_active": session.is_active,
        "queries": [
            {
                "id": q.id,
                "query": q.query_text,
                "answer": q.answer,
                "timestamp": q.created_at.isoformat() if q.created_at else None
            }
            for q in queries
        ]
    }


# ============================================================
# 🧪 Test
# ============================================================
@router.get("/test")
async def test_endpoint():
    return {"message": "[SUCCESS] RAG router is working!"}


@router.get("/debug/vectorstore")
async def debug_vectorstore():
    """[DEBUG] Debug endpoint to check vector store state"""
    try:
        from app.services.vectorstore import get_vector_store
        
        vector_store = get_vector_store()
        
        return {
            "status": "ok",
            "vector_count": vector_store.get_count(),
            "faiss_index_total": vector_store.index.ntotal,
            "dimension": vector_store.dimension,
            "documents_sample": vector_store.documents[:3] if len(vector_store.documents) > 0 else [],
            "metadata_sample": vector_store.metadata[:3] if len(vector_store.metadata) > 0 else [],
            "documents_list_length": len(vector_store.documents),
            "metadata_list_length": len(vector_store.metadata)
        }
    except Exception as e:
        logger.error(f"[ERROR] Debug endpoint failed: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "error": str(e),
            "traceback": traceback.format_exc()
        }
    
    
# In routers/rag_router.py

@router.get("/graph/{document_id}")
async def get_document_graph(document_id: str, db: Session = Depends(get_db)):
    """
    Get graph structure for a document
    """
    entities = db.query(GraphEntity).filter(
        GraphEntity.properties["document_id"].astext == document_id
    ).all()
    
    relationships = db.query(GraphRelationship).join(
        GraphEntity, GraphEntity.id == GraphRelationship.source_id
    ).filter(
        GraphEntity.properties["document_id"].astext == document_id
    ).all()
    
    return {
        "nodes": [
            {
                "id": e.id,
                "name": e.name,
                "type": e.type,
                "description": e.description
            } for e in entities
        ],
        "edges": [
            {
                "source": r.source_id,
                "target": r.target_id,
                "relation": r.relation_type,
                "weight": r.weight
            } for r in relationships
        ]
    }


@router.get("/debug/vector-store-detailed")
async def debug_vector_store_detailed():
    """Detailed debug endpoint for vector store"""
    from app.services.vectorstore import get_vector_store, _vector_store_instance
    
    vector_store = get_vector_store()
    
    # Get detailed internal state
    detailed_info = {
        "vector_store_instance_id": id(vector_store),
        "singleton_instance_id": id(_vector_store_instance) if _vector_store_instance else None,
        "is_same_instance": vector_store is _vector_store_instance,
        "_is_cleared": vector_store._is_cleared,
        "documents_count": len(vector_store.documents),
        "metadata_count": len(vector_store.metadata),
        "embeddings_count": len(vector_store.embeddings),
        "index_exists": vector_store.index is not None,
        "get_count_result": vector_store.get_count(),
    }
    
    # Document sources analysis
    sources = {}
    for i, meta in enumerate(vector_store.metadata):
        source = meta.get("source", "unknown")
        if source not in sources:
            sources[source] = 0
        sources[source] += 1
    
    detailed_info["sources_breakdown"] = sources
    
    # Sample of actual document content
    sample_docs = []
    for i, doc in enumerate(vector_store.documents[:3]):  # First 3 docs
        sample_docs.append({
            "index": i,
            "content_preview": doc[:100] + "..." if len(doc) > 100 else doc,
            "source": vector_store.metadata[i].get("source", "unknown") if i < len(vector_store.metadata) else "unknown"
        })
    
    detailed_info["documents_sample"] = sample_docs
    
    return detailed_info


@router.get("/debug/vector-store-detailed")
async def debug_vector_store_detailed():
    """Detailed debug endpoint for ChromaDB vector store"""
    from app.core.dependencies import get_vectorstore  # ✅ Use ChromaDB
    
    vector_store = get_vectorstore()
    
    # Get ChromaDB detailed information
    detailed_info = {
        "vector_store_type": "ChromaDB",
        "vector_store_instance_id": id(vector_store),
        "collection_name": vector_store.collection_name,
        "persist_directory": vector_store.persist_directory,
        "total_documents_count": vector_store.get_count(),
    }
    
    # Try to get sample documents from ChromaDB
    try:
        # Get a sample of documents to see what's actually stored
        results = vector_store.collection.get(limit=10)
        
        if results and results.get('documents'):
            detailed_info["chroma_documents_count"] = len(results['documents'])
            detailed_info["chroma_metadatas_count"] = len(results.get('metadatas', []))
            detailed_info["chroma_ids_count"] = len(results.get('ids', []))
            
            # Analyze sources
            sources = {}
            if results.get('metadatas'):
                for meta in results['metadatas']:
                    if meta and 'source' in meta:
                        source = meta['source']
                        if source not in sources:
                            sources[source] = 0
                        sources[source] += 1
            
            detailed_info["sources_breakdown"] = sources
            
            # Sample of actual document content
            sample_docs = []
            for i, doc in enumerate(results['documents'][:3]):
                sample_docs.append({
                    "index": i,
                    "content_preview": doc[:100] + "..." if len(doc) > 100 else doc,
                    "source": results['metadatas'][i].get('source', 'unknown') if i < len(results.get('metadatas', [])) else 'unknown',
                    "document_id": results['metadatas'][i].get('document_id', 'unknown') if i < len(results.get('metadatas', [])) else 'unknown'
                })
            
            detailed_info["documents_sample"] = sample_docs
        else:
            detailed_info["chroma_documents_count"] = 0
            detailed_info["sources_breakdown"] = {}
            detailed_info["documents_sample"] = []
            
    except Exception as e:
        detailed_info["chroma_error"] = str(e)
    
    return detailed_info


@router.get("/debug/chromadb-status")
async def debug_chromadb_status():
    """Comprehensive ChromaDB status check"""
    try:
        from app.core.dependencies import get_vectorstore
        
        vector_store = get_vectorstore()
        
        status = {
            "vector_store_type": "ChromaDB",
            "collection_name": vector_store.collection_name,
            "persist_directory": vector_store.persist_directory,
            "total_documents": vector_store.get_count(),
        }
        
        # Get detailed collection info
        try:
            # Get all documents to analyze
            all_docs = vector_store.collection.get()
            
            if all_docs and all_docs.get('documents'):
                status["actual_document_count"] = len(all_docs['documents'])
                status["actual_metadata_count"] = len(all_docs.get('metadatas', []))
                status["actual_ids_count"] = len(all_docs.get('ids', []))
                
                # Group by document_id to see how many chunks per document
                doc_chunks = {}
                if all_docs.get('metadatas'):
                    for meta in all_docs['metadatas']:
                        if meta and 'document_id' in meta:
                            doc_id = meta['document_id']
                            if doc_id not in doc_chunks:
                                doc_chunks[doc_id] = 0
                            doc_chunks[doc_id] += 1
                
                status["documents_with_chunks"] = doc_chunks
                
                # List all unique sources
                sources = set()
                if all_docs.get('metadatas'):
                    for meta in all_docs['metadatas']:
                        if meta and 'source' in meta:
                            sources.add(meta['source'])
                
                status["all_sources"] = list(sources)
                
                # Sample of documents
                sample_docs = []
                for i in range(min(3, len(all_docs['documents']))):
                    sample_docs.append({
                        "id": all_docs['ids'][i] if i < len(all_docs.get('ids', [])) else f"index_{i}",
                        "content_preview": all_docs['documents'][i][:100] + "..." if len(all_docs['documents'][i]) > 100 else all_docs['documents'][i],
                        "source": all_docs['metadatas'][i].get('source', 'unknown') if i < len(all_docs.get('metadatas', [])) else 'unknown',
                        "document_id": all_docs['metadatas'][i].get('document_id', 'unknown') if i < len(all_docs.get('metadatas', [])) else 'unknown'
                    })
                
                status["sample_documents"] = sample_docs
                
            else:
                status["actual_document_count"] = 0
                status["documents_with_chunks"] = {}
                status["all_sources"] = []
                status["sample_documents"] = []
                
        except Exception as e:
            status["collection_error"] = str(e)
        
        return status
        
    except Exception as e:
        return {"error": f"Failed to get ChromaDB status: {str(e)}"}

@router.get("/debug/chromadb-collection-info")
async def debug_chromadb_collection_info():
    """Get raw ChromaDB collection information"""
    try:
        from app.core.dependencies import get_vectorstore
        
        vector_store = get_vectorstore()
        
        info = {
            "collection_name": vector_store.collection_name,
            "persist_directory": vector_store.persist_directory,
            "total_count": vector_store.get_count(),
        }
        
        # Try to get raw collection data
        try:
            collection_data = vector_store.collection.get()
            info["raw_collection_keys"] = list(collection_data.keys()) if collection_data else []
            
            if collection_data and 'documents' in collection_data:
                info["documents_count"] = len(collection_data['documents'])
                info["metadatas_count"] = len(collection_data.get('metadatas', []))
                info["ids_count"] = len(collection_data.get('ids', []))
                
                # Show first few document IDs and sources
                if collection_data.get('metadatas'):
                    sources_summary = []
                    for i, meta in enumerate(collection_data['metadatas'][:5]):
                        if meta:
                            sources_summary.append({
                                "index": i,
                                "source": meta.get('source', 'unknown'),
                                "document_id": meta.get('document_id', 'unknown'),
                                "chunk_index": meta.get('chunk_index', 'unknown')
                            })
                    info["first_five_documents"] = sources_summary
                    
        except Exception as e:
            info["collection_error"] = str(e)
        
        return info
        
    except Exception as e:
        return {"error": f"Failed to get collection info: {str(e)}"}
    

@router.get("/debug/chromadb-contents")
async def debug_chromadb_contents():
    """Show EVERYTHING in ChromaDB"""
    try:
        from app.core.dependencies import get_vectorstore
        
        vector_store = get_vectorstore()
        
        # Get ALL documents
        all_data = vector_store.collection.get()
        
        result = {
            "total_chunks": len(all_data.get('documents', [])),
            "all_sources": [],
            "all_document_ids": []
        }
        
        # List all sources and document IDs
        if all_data.get('metadatas'):
            for meta in all_data['metadatas']:
                if meta:
                    source = meta.get('source', 'unknown')
                    doc_id = meta.get('document_id', 'unknown')
                    
                    if source not in result["all_sources"]:
                        result["all_sources"].append(source)
                    
                    if doc_id not in result["all_document_ids"]:
                        result["all_document_ids"].append(doc_id)
        
        return result
        
    except Exception as e:
        return {"error": str(e)}
    


@router.get("/debug/agent-execution/{query_id}")
async def debug_agent_execution(query_id: str, db: Session = Depends(get_db)):
    """
    View detailed ReAct agent execution steps for a specific query
    """
    query = db.query(QueryModel).filter(QueryModel.id == query_id).first()
    
    if not query:
        raise HTTPException(status_code=404, detail="Query not found")
    
    metadata = query.meta_data or {}
    execution_steps = metadata.get("execution_steps", [])
    
    # Format execution trace
    formatted_steps = []
    for i, step in enumerate(execution_steps, 1):
        formatted_steps.append({
            "step_number": i,
            "type": step.get("type"),
            "content": step.get("content"),
            "timestamp": step.get("timestamp")
        })
    
    return {
        "query_id": query.id,
        "query_text": query.query_text,
        "answer_preview": query.answer[:200] + "..." if query.answer else "",
        "strategy_used": query.strategy_used,
        "source": metadata.get("source"),
        "agent_type": metadata.get("agent_type"),
        "total_steps": len(execution_steps),
        "execution_trace": formatted_steps,
        "internet_sources": metadata.get("internet_sources", []),
        "processing_time": query.processing_time,
        "confidence_score": query.confidence_score
    }


@router.get("/debug/latest-agent-execution")
async def debug_latest_agent_execution(db: Session = Depends(get_db)):
    """
    View the most recent agent execution trace
    """
    latest_query = db.query(QueryModel).order_by(
        QueryModel.created_at.desc()
    ).first()
    
    if not latest_query:
        return {"message": "No queries found"}
    
    return await debug_agent_execution(latest_query.id, db)

@router.get("/agent-executions")
async def list_agent_executions(
    limit: int = 10, 
    skip: int = 0, 
    db: Session = Depends(get_db)
):
    """
    List recent agent executions with execution statistics
    """
    queries = db.query(QueryModel).order_by(
        QueryModel.created_at.desc()
    ).offset(skip).limit(limit).all()
    
    executions = []
    for query in queries:
        metadata = query.meta_data or {}
        execution_steps = metadata.get("execution_steps", [])
        
        # Count step types
        step_counts = {}
        for step in execution_steps:
            step_type = step.get("type", "UNKNOWN")
            step_counts[step_type] = step_counts.get(step_type, 0) + 1
        
        executions.append({
            "query_id": query.id,
            "query_text": query.query_text[:100] + "..." if len(query.query_text) > 100 else query.query_text,
            "strategy": query.strategy_used,
            "source": metadata.get("source", "unknown"),
            "agent_type": metadata.get("agent_type", "unknown"),
            "total_steps": len(execution_steps),
            "step_breakdown": step_counts,
            "processing_time": query.processing_time,
            "confidence_score": query.confidence_score,
            "created_at": query.created_at.isoformat() if query.created_at else None,
            "used_internet": len(metadata.get("internet_sources", [])) > 0
        })
    
    return {
        "total": db.query(QueryModel).count(),
        "showing": len(executions),
        "executions": executions
    }