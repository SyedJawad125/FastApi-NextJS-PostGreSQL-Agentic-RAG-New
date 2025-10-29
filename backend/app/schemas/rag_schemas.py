# """
# ===================================================================
# app/schemas/rag_schemas.py - Complete RAG Schemas (FIXED)
# ===================================================================
# """
# from pydantic import BaseModel, Field
# from typing import Optional, List, Dict, Any
# from datetime import datetime


# # ============================================================
# # QUERY SCHEMAS
# # ============================================================

# class RAGQueryRequest(BaseModel):
#     """RAG query request schema"""
#     query: str
#     strategy: str = "simple"
#     top_k: int = 5
#     session_id: Optional[str] = None
#     document_id: Optional[str] = None  # Add this field
    
#     class Config:
#         json_schema_extra = {
#             "example": {
#                 "query": "What is AI?",
#                 "strategy": "simple",
#                 "top_k": 5,
#                 "session_id": "session-123",
#                 "document_id": "doc-456"
#             }
#         }


# class RAGQueryResponse(BaseModel):
#     """RAG query response schema"""
#     query: str
#     answer: str
#     strategy_used: str
#     processing_time: float
#     retrieved_chunks: List[Dict[str, Any]] = []
#     confidence_score: Optional[float] = None
    
#     class Config:
#         json_schema_extra = {
#             "example": {
#                 "query": "What is AI?",
#                 "answer": "Artificial Intelligence is a branch of computer science...",
#                 "strategy_used": "simple",
#                 "processing_time": 1.23,
#                 "retrieved_chunks": [],
#                 "confidence_score": 0.85
#             }
#         }


# # ============================================================
# # MULTI-AGENT SCHEMAS
# # ============================================================

# class MultiAgentQuery(BaseModel):
#     """Multi-agent query request"""
#     query: str = Field(..., min_length=1)
#     session_id: Optional[str] = None
#     include_research: bool = Field(default=True)
#     include_evaluation: bool = Field(default=True)
    
#     class Config:
#         json_schema_extra = {
#             "example": {
#                 "query": "Explain quantum computing",
#                 "session_id": None,
#                 "include_research": True,
#                 "include_evaluation": True
#             }
#         }


# class MultiAgentResponse(BaseModel):
#     """Multi-agent query response"""
#     query: str
#     answer: str
#     research: Optional[str] = None
#     evaluation: Optional[str] = None
#     score: Optional[float] = None
#     verdict: Optional[str] = None
#     processing_time: float
#     agents_used: List[str] = []
    
#     class Config:
#         json_schema_extra = {
#             "example": {
#                 "query": "Explain quantum computing",
#                 "answer": "Quantum computing is...",
#                 "research": "Research findings...",
#                 "evaluation": "The answer is comprehensive...",
#                 "score": 0.92,
#                 "verdict": "approved",
#                 "processing_time": 3.45,
#                 "agents_used": ["researcher", "writer", "critic"]
#             }
#         }


# # ============================================================
# # GRAPH SCHEMAS
# # ============================================================

# class GraphQuery(BaseModel):
#     """Graph-based RAG query"""
#     query: str = Field(..., min_length=1)
#     max_depth: int = Field(default=2, ge=1, le=5)
#     include_relationships: bool = Field(default=True)
    
#     class Config:
#         json_schema_extra = {
#             "example": {
#                 "query": "What is machine learning?",
#                 "max_depth": 2,
#                 "include_relationships": True
#             }
#         }


# class GraphQueryResponse(BaseModel):
#     """Graph query response"""
#     query: str
#     answer: str
#     entities_found: List[Dict[str, Any]] = []
#     relationships: List[Dict[str, Any]] = []
#     processing_time: float
    
#     class Config:
#         json_schema_extra = {
#             "example": {
#                 "query": "What is machine learning?",
#                 "answer": "Machine learning is...",
#                 "entities_found": [],
#                 "relationships": [],
#                 "processing_time": 1.5
#             }
#         }


# # ============================================================
# # DOCUMENT SCHEMAS
# # ============================================================

# class DocumentUpload(BaseModel):
#     """Document upload request (used for additional metadata)"""
#     tags: Optional[List[str]] = []
#     metadata: Optional[Dict[str, Any]] = {}
    
#     class Config:
#         json_schema_extra = {
#             "example": {
#                 "tags": ["ml", "ai"],
#                 "metadata": {"author": "John Doe"}
#             }
#         }


# class DocumentUploadResponse(BaseModel):
#     """Document upload response"""
#     document_id: str
#     filename: str
#     status: str
#     chunks_created: int
#     message: str
#     processing_time: Optional[str] = None
    
#     class Config:
#         json_schema_extra = {
#             "example": {
#                 "document_id": "doc-123",
#                 "filename": "machine_learning.pdf",
#                 "status": "success",
#                 "chunks_created": 45,
#                 "message": "Document processed successfully",
#                 "processing_time": "5.2 seconds"
#             }
#         }


# class DocumentResponse(BaseModel):
#     """Single document response"""
#     id: str
#     filename: str
#     content_type: str
#     size: int
#     status: str
#     chunks_count: int
#     entities_count: Optional[int] = 0
#     relationships_count: Optional[int] = 0
#     uploaded_at: Optional[str] = None
#     processed_at: Optional[str] = None
#     metadata: Optional[Dict[str, Any]] = {}
    
#     class Config:
#         json_schema_extra = {
#             "example": {
#                 "id": "doc-123",
#                 "filename": "document.pdf",
#                 "content_type": "application/pdf",
#                 "size": 1024000,
#                 "status": "completed",
#                 "chunks_count": 45,
#                 "entities_count": 12,
#                 "relationships_count": 8,
#                 "uploaded_at": "2025-10-20T10:00:00",
#                 "processed_at": "2025-10-20T10:01:00",
#                 "metadata": {}
#             }
#         }


# class DocumentList(BaseModel):
#     """List of documents response"""
#     total: int
#     count: int
#     skip: int
#     limit: int
#     documents: List[DocumentResponse]
    
#     class Config:
#         json_schema_extra = {
#             "example": {
#                 "total": 100,
#                 "count": 10,
#                 "skip": 0,
#                 "limit": 10,
#                 "documents": []
#             }
#         }


# # ============================================================
# # HEALTH & STATS SCHEMAS
# # ============================================================

# class HealthCheck(BaseModel):
#     """Health check response"""
#     status: str
#     timestamp: datetime
#     version: str
#     components: Dict[str, str]
    
#     class Config:
#         json_schema_extra = {
#             "example": {
#                 "status": "healthy",
#                 "timestamp": "2025-10-20T10:00:00",
#                 "version": "1.0.0",
#                 "components": {
#                     "llm_service": "operational",
#                     "vector_store": "operational",
#                     "database": "operational"
#                 }
#             }
#         }


# class HealthCheckResponse(HealthCheck):
#     """Alias for HealthCheck"""
#     pass


# class SystemStats(BaseModel):
#     """System statistics response"""
#     total_documents: int
#     total_queries: int
#     total_chunks: int
#     average_processing_time: float
#     strategy_distribution: Dict[str, int]
    
#     class Config:
#         json_schema_extra = {
#             "example": {
#                 "total_documents": 150,
#                 "total_queries": 1250,
#                 "total_chunks": 6750,
#                 "average_processing_time": 1.45,
#                 "strategy_distribution": {
#                     "simple": 800,
#                     "agentic": 300,
#                     "auto": 150
#                 }
#             }
#         }


# # ============================================================
# # BACKWARD COMPATIBILITY ALIASES
# # ============================================================

# # These aliases ensure backward compatibility
# RAGQuery = RAGQueryRequest



"""
===================================================================
app/schemas/rag_schemas.py - Complete RAG Schemas with Agentic ReAct Pattern
===================================================================
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# ============================================================
# ENUMS
# ============================================================

class RAGStrategyEnum(str, Enum):
    """RAG strategy options"""
    SIMPLE = "simple"
    AGENTIC = "agentic"
    AUTO = "auto"


class SourceType(str, Enum):
    """Source of the answer"""
    CHROMADB = "chromadb"
    VECTOR_DATABASE = "vector_database"
    INTERNET = "internet"
    GENERAL_KNOWLEDGE = "general_knowledge"
    COORDINATOR_AGENT = "coordinator_agent"
    ERROR = "error"


class AgentStepType(str, Enum):
    """Types of agent execution steps (ReAct pattern)"""
    THOUGHT = "THOUGHT"
    ACTION = "ACTION"
    OBSERVATION = "OBSERVATION"
    ERROR = "ERROR"


# ============================================================
# QUERY SCHEMAS
# ============================================================

class RAGQueryRequest(BaseModel):
    """RAG query request schema with agentic support"""
    query: str = Field(..., min_length=1, max_length=2000, description="The question or query to process")
    strategy: str = Field(default="auto", description="RAG strategy: simple, agentic, or auto")
    top_k: int = Field(default=5, ge=1, le=20, description="Number of chunks to retrieve")
    session_id: Optional[str] = Field(default=None, description="Session ID for conversation tracking")
    document_id: Optional[str] = Field(default=None, description="Specific document ID to search")
    
    @validator('strategy')
    def validate_strategy(cls, v):
        if v not in ['simple', 'agentic', 'auto']:
            raise ValueError('Strategy must be: simple, agentic, or auto')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "What are the key skills mentioned in the CV?",
                "strategy": "agentic",
                "top_k": 5,
                "session_id": "session-123",
                "document_id": "doc-456"
            }
        }


class RetrievedChunk(BaseModel):
    """Schema for a retrieved document chunk"""
    content: str = Field(..., description="Chunk content (may be truncated)")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Chunk metadata")
    score: float = Field(..., ge=0.0, le=1.0, description="Relevance score")
    
    class Config:
        json_schema_extra = {
            "example": {
                "content": "John Doe has 5 years of experience in Python...",
                "metadata": {
                    "source": "john_cv.pdf",
                    "chunk_index": 2,
                    "document_id": "doc-123"
                },
                "score": 0.89
            }
        }


class InternetSource(BaseModel):
    """Schema for an internet search result from Tavily"""
    title: str = Field(..., description="Title of the source")
    snippet: str = Field(..., description="Content snippet from the source")
    url: str = Field(..., description="URL of the source")
    source: str = Field(..., description="Domain/source name")
    score: Optional[float] = Field(default=None, description="Relevance score")
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Machine Learning Basics | IBM",
                "snippet": "Machine learning is a branch of AI...",
                "url": "https://www.ibm.com/topics/machine-learning",
                "source": "ibm.com",
                "score": 0.95
            }
        }


class AgentExecutionStep(BaseModel):
    """Schema for a single ReAct agent execution step"""
    step_number: Optional[int] = Field(default=None, description="Step sequence number")
    type: str = Field(..., description="Step type: THOUGHT, ACTION, OBSERVATION, ERROR")
    content: str = Field(..., description="Step content/description")
    timestamp: str = Field(..., description="ISO timestamp of the step")
    
    class Config:
        json_schema_extra = {
            "example": {
                "step_number": 1,
                "type": "THOUGHT",
                "content": "Analyzing query - likely needs internet search",
                "timestamp": "2025-01-09T10:30:00.123Z"
            }
        }


class RelevanceCheck(BaseModel):
    """Schema for semantic relevance verification"""
    is_relevant: bool = Field(..., description="Whether results are truly relevant")
    verdict: str = Field(..., description="RELEVANT, NOT_RELEVANT, or CHECK_FAILED")
    reason: str = Field(..., description="Explanation for the verdict")
    score: float = Field(..., ge=0.0, le=1.0, description="Relevance score")
    
    class Config:
        json_schema_extra = {
            "example": {
                "is_relevant": False,
                "verdict": "NOT_RELEVANT",
                "reason": "Chunks discuss Bahria University, not AIR University",
                "score": 0.75
            }
        }


class RAGQueryResponse(BaseModel):
    """Enhanced RAG query response with Agentic ReAct support"""
    query: str = Field(..., description="Original query")
    answer: str = Field(..., description="Generated answer")
    strategy_used: str = Field(..., description="Strategy that was used")
    processing_time: float = Field(..., ge=0.0, description="Total processing time in seconds")
    retrieved_chunks: List[Dict[str, Any]] = Field(default_factory=list, description="Chunks from ChromaDB")
    confidence_score: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Confidence score")
    
    # ⭐ New Agentic RAG fields
    source: Optional[str] = Field(default=None, description="Answer source: chromadb, internet, general_knowledge")
    agent_type: Optional[str] = Field(default=None, description="Agent type: coordinator_react, simple, etc.")
    execution_steps: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="ReAct agent execution trace (THOUGHT → ACTION → OBSERVATION)"
    )
    internet_sources: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Internet sources from Tavily (if used)"
    )
    agent_steps_count: Optional[int] = Field(default=None, description="Total agent execution steps")
    relevance_check: Optional[Dict[str, Any]] = Field(default=None, description="Semantic relevance result")
    fallback_used: Optional[bool] = Field(default=None, description="Whether fallback was used")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "What is machine learning?",
                "answer": "Machine learning is a branch of AI...",
                "strategy_used": "agentic",
                "processing_time": 4.52,
                "retrieved_chunks": [],
                "confidence_score": 0.85,
                "source": "internet",
                "agent_type": "coordinator_react",
                "execution_steps": [
                    {
                        "step_number": 1,
                        "type": "THOUGHT",
                        "content": "Analyzing query...",
                        "timestamp": "2025-01-09T10:30:00.000Z"
                    }
                ],
                "internet_sources": [
                    {
                        "title": "What is ML? | IBM",
                        "snippet": "Machine learning...",
                        "url": "https://ibm.com/ml",
                        "source": "ibm.com",
                        "score": 0.95
                    }
                ],
                "agent_steps_count": 8,
                "fallback_used": True
            }
        }


# ============================================================
# MULTI-AGENT SCHEMAS
# ============================================================

class MultiAgentQuery(BaseModel):
    """Multi-agent query request"""
    query: str = Field(..., min_length=1)
    session_id: Optional[str] = None
    include_research: bool = Field(default=True)
    include_evaluation: bool = Field(default=True)
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "Explain quantum computing",
                "session_id": None,
                "include_research": True,
                "include_evaluation": True
            }
        }


class MultiAgentResponse(BaseModel):
    """Multi-agent query response"""
    query: str
    answer: str
    research: Optional[str] = None
    evaluation: Optional[str] = None
    score: Optional[float] = None
    verdict: Optional[str] = None
    processing_time: float
    agents_used: List[str] = []
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "Explain quantum computing",
                "answer": "Quantum computing is...",
                "research": "Research findings...",
                "evaluation": "The answer is comprehensive...",
                "score": 0.92,
                "verdict": "approved",
                "processing_time": 3.45,
                "agents_used": ["researcher", "writer", "critic"]
            }
        }


# ============================================================
# GRAPH SCHEMAS
# ============================================================

class GraphQuery(BaseModel):
    """Graph-based RAG query"""
    query: str = Field(..., min_length=1)
    max_depth: int = Field(default=2, ge=1, le=5)
    include_relationships: bool = Field(default=True)
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "What is machine learning?",
                "max_depth": 2,
                "include_relationships": True
            }
        }


class GraphQueryResponse(BaseModel):
    """Graph query response"""
    query: str
    answer: str
    entities_found: List[Dict[str, Any]] = []
    relationships: List[Dict[str, Any]] = []
    processing_time: float
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "What is machine learning?",
                "answer": "Machine learning is...",
                "entities_found": [],
                "relationships": [],
                "processing_time": 1.5
            }
        }


# ============================================================
# DOCUMENT SCHEMAS
# ============================================================

class DocumentUpload(BaseModel):
    """Document upload request (used for additional metadata)"""
    tags: Optional[List[str]] = []
    metadata: Optional[Dict[str, Any]] = {}
    
    class Config:
        json_schema_extra = {
            "example": {
                "tags": ["ml", "ai"],
                "metadata": {"author": "John Doe"}
            }
        }


class DocumentUploadResponse(BaseModel):
    """Document upload response"""
    document_id: str
    filename: str
    status: str
    chunks_created: int
    message: str
    processing_time: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "document_id": "doc-123",
                "filename": "machine_learning.pdf",
                "status": "success",
                "chunks_created": 45,
                "message": "Document processed successfully",
                "processing_time": "5.2 seconds"
            }
        }


class DocumentResponse(BaseModel):
    """Single document response"""
    id: str
    filename: str
    content_type: str
    size: int
    status: str
    chunks_count: int
    entities_count: Optional[int] = 0
    relationships_count: Optional[int] = 0
    uploaded_at: Optional[str] = None
    processed_at: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = {}
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "doc-123",
                "filename": "document.pdf",
                "content_type": "application/pdf",
                "size": 1024000,
                "status": "completed",
                "chunks_count": 45,
                "entities_count": 12,
                "relationships_count": 8,
                "uploaded_at": "2025-10-20T10:00:00",
                "processed_at": "2025-10-20T10:01:00",
                "metadata": {}
            }
        }


class DocumentList(BaseModel):
    """List of documents response"""
    total: int
    count: int
    skip: int
    limit: int
    documents: List[DocumentResponse]
    
    class Config:
        json_schema_extra = {
            "example": {
                "total": 100,
                "count": 10,
                "skip": 0,
                "limit": 10,
                "documents": []
            }
        }


# ============================================================
# AGENT EXECUTION DEBUG SCHEMAS
# ============================================================

class AgentExecutionDetail(BaseModel):
    """Detailed agent execution information for debugging"""
    query_id: str = Field(..., description="Query ID")
    query_text: str = Field(..., description="Original query")
    answer_preview: str = Field(..., description="Preview of the answer")
    strategy_used: str = Field(..., description="Strategy used")
    source: str = Field(..., description="Answer source")
    agent_type: str = Field(..., description="Agent type")
    total_steps: int = Field(..., ge=0, description="Total execution steps")
    execution_trace: List[AgentExecutionStep] = Field(..., description="Full ReAct trace")
    internet_sources: List[InternetSource] = Field(default_factory=list)
    processing_time: float = Field(..., description="Processing time in seconds")
    confidence_score: float = Field(..., description="Confidence score")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query_id": "query-abc-123",
                "query_text": "What is Python?",
                "answer_preview": "Python is a high-level programming language...",
                "strategy_used": "agentic",
                "source": "internet",
                "agent_type": "coordinator_react",
                "total_steps": 8,
                "execution_trace": [],
                "internet_sources": [],
                "processing_time": 4.5,
                "confidence_score": 0.85
            }
        }


class AgentExecutionSummary(BaseModel):
    """Summary of an agent execution"""
    query_id: str
    query_text: str
    strategy: str
    source: str
    agent_type: str
    total_steps: int
    step_breakdown: Dict[str, int] = Field(
        default_factory=dict,
        description="Count of each step type (THOUGHT, ACTION, etc.)"
    )
    processing_time: float
    confidence_score: float
    created_at: str
    used_internet: bool = Field(..., description="Whether internet search was used")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query_id": "query-abc-123",
                "query_text": "What is machine learning?",
                "strategy": "agentic",
                "source": "internet",
                "agent_type": "coordinator_react",
                "total_steps": 8,
                "step_breakdown": {
                    "THOUGHT": 3,
                    "ACTION": 3,
                    "OBSERVATION": 2
                },
                "processing_time": 4.5,
                "confidence_score": 0.85,
                "created_at": "2025-01-09T10:30:00.000Z",
                "used_internet": True
            }
        }


class AgentExecutionListResponse(BaseModel):
    """List of agent executions"""
    total: int = Field(..., ge=0, description="Total executions")
    showing: int = Field(..., ge=0, description="Executions in this response")
    executions: List[AgentExecutionSummary] = Field(..., description="List of executions")
    
    class Config:
        json_schema_extra = {
            "example": {
                "total": 150,
                "showing": 10,
                "executions": []
            }
        }


# ============================================================
# HEALTH & STATS SCHEMAS
# ============================================================

class HealthCheck(BaseModel):
    """Health check response"""
    status: str
    timestamp: datetime
    version: str
    components: Dict[str, str]
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "timestamp": "2025-10-20T10:00:00",
                "version": "2.1.0-agentic",
                "components": {
                    "database": "operational",
                    "llm_service": "operational",
                    "embedding_service": "operational",
                    "vector_store": "operational",
                    "tavily_api": "operational",
                    "coordinator_agent": "operational"
                }
            }
        }


class HealthCheckResponse(HealthCheck):
    """Alias for HealthCheck"""
    pass


class SystemStats(BaseModel):
    """Enhanced system statistics with agent metrics"""
    total_documents: int
    total_queries: int
    total_chunks: int
    average_processing_time: float
    strategy_distribution: Dict[str, int]
    
    # ⭐ New agent-related stats
    source_distribution: Optional[Dict[str, int]] = Field(
        default=None,
        description="Distribution of answer sources (chromadb, internet, general_knowledge)"
    )
    agent_usage: Optional[Dict[str, int]] = Field(
        default=None,
        description="Usage count of different agent types"
    )
    internet_search_count: Optional[int] = Field(
        default=None,
        description="Number of queries that used internet search"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_documents": 150,
                "total_queries": 1250,
                "total_chunks": 6750,
                "average_processing_time": 1.45,
                "strategy_distribution": {
                    "simple": 800,
                    "agentic": 300,
                    "auto": 150
                },
                "source_distribution": {
                    "chromadb": 800,
                    "internet": 350,
                    "general_knowledge": 100
                },
                "agent_usage": {
                    "coordinator_react": 1250
                },
                "internet_search_count": 350
            }
        }


# ============================================================
# SESSION SCHEMAS
# ============================================================

class SessionCreate(BaseModel):
    """Schema for creating a new session"""
    user_id: Optional[str] = Field(default=None, description="User ID")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user-123"
            }
        }


class SessionResponse(BaseModel):
    """Session response schema"""
    session_id: str
    user_id: Optional[str]
    started_at: str
    status: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "session-abc-123",
                "user_id": "user-123",
                "started_at": "2025-01-09T10:30:00.000Z",
                "status": "active"
            }
        }


# ============================================================
# ERROR SCHEMAS
# ============================================================

class ErrorResponse(BaseModel):
    """Error response schema"""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(default=None, description="Detailed error information")
    timestamp: str = Field(..., description="Error timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "Query processing failed",
                "detail": "Vector store is not initialized",
                "timestamp": "2025-01-09T10:30:00.000Z"
            }
        }


# ============================================================
# BACKWARD COMPATIBILITY ALIASES
# ============================================================

# These aliases ensure backward compatibility
RAGQuery = RAGQueryRequest
RAGStatistics = SystemStats