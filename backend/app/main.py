# """
# ===================================================================
# app/main.py - Fixed FastAPI Application Entry Point
# ===================================================================
# """
# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.responses import JSONResponse
# from contextlib import asynccontextmanager
# import logging.config
# from pathlib import Path
# from datetime import datetime
# from app.routers.rag_router import router as rag_router
# from app.core.config import settings, init_db, engine

# # Configure logging
# Path(settings.LOG_FILE).parent.mkdir(parents=True, exist_ok=True)

# logging.config.dictConfig({
#     "version": 1,
#     "disable_existing_loggers": False,
#     "formatters": {
#         "default": {
#             "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
#         }
#     },
#     "handlers": {
#         "console": {
#             "class": "logging.StreamHandler",
#             "formatter": "default",
#             "stream": "ext://sys.stdout"
#         },
#         "file": {
#             "class": "logging.FileHandler",
#             "filename": settings.LOG_FILE,
#             "formatter": "default",
#             "mode": "a"
#         }
#     },
#     "root": {
#         "level": settings.LOG_LEVEL,
#         "handlers": ["console", "file"]
#     }
# })

# logger = logging.getLogger(__name__)


# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     """Application lifespan events"""
#     logger.info("=" * 60)
#     logger.info(f"Starting {settings.API_TITLE} v{settings.API_VERSION}")
#     logger.info("=" * 60)
    
#     # Create necessary directories
#     directories = [
#         "data/vectors",
#         "data/graphs",
#         "data/documents",
#         "logs",
#         "uploads"
#     ]
    
#     for directory in directories:
#         Path(directory).mkdir(parents=True, exist_ok=True)
#         logger.info(f"Directory created: {directory}/")
    
#     # Initialize database
#     try:
#         init_db()
#         logger.info("[OK] Database initialized successfully")
#     except Exception as e:
#         logger.error(f"[ERROR] Database initialization failed: {str(e)}")
#         raise
    
#     # Initialize orchestrator
#     try:
#         from app.core.dependencies import initialize_orchestrator
#         initialize_orchestrator()
#         logger.info("[OK] Orchestrator initialized")
#     except Exception as e:
#         logger.error(f"[ERROR] Orchestrator initialization failed: {str(e)}")
#         # Continue anyway - orchestrator is optional
    
#     # Check dependencies health
#     try:
#         from app.core.dependencies import check_dependencies_health
#         health = check_dependencies_health()
#         for service, status in health.items():
#             if status == "operational":
#                 logger.info(f"[OK] {service}: {status}")
#             elif status == "disabled":
#                 logger.info(f"[DISABLED] {service}: {status}")
#             else:
#                 logger.warning(f"[ERROR] {service}: {status}")
#     except Exception as e:
#         logger.error(f"Health check failed: {str(e)}")
    
#     logger.info("[OK] All services ready")
#     logger.info(f"[INFO] API Documentation: http://localhost:8000/docs")
#     logger.info("=" * 60)
    
#     yield
    
#     # Shutdown
#     logger.info("Shutting down application...")
#     try:
#         engine.dispose()
#         logger.info("[OK] Database connections closed")
#     except Exception as e:
#         logger.error(f"Error during shutdown: {str(e)}")


# # Create FastAPI app
# app = FastAPI(
#     title=settings.API_TITLE,
#     version=settings.API_VERSION,
#     description="""
#     Advanced Agentic RAG System with Multi-Agent Architecture

#     ## Features
#     * Document Processing: PDF, TXT, DOCX, MD
#     * Semantic Search: ChromaDB vector store with sentence-transformers
#     * Multiple RAG Strategies: Simple, Agentic, Multi-Agent, Auto
#     * Multi-Agent System: Researcher, Writer, Critic agents
#     * ReAct Pattern: Reasoning + Acting for intelligent responses
#     * Knowledge Graph: Optional graph-based RAG
#     * Session Management: Track conversations and context
#     * PostgreSQL: Persistent storage with full history

#     ## Quick Start
#     1. Upload a document: POST /api/rag/upload
#     2. Query the system: POST /api/rag/query
#     3. Multi-agent query: POST /api/rag/multi-agent-query
#     4. Check health: GET /api/rag/health
#     """,
#     lifespan=lifespan,
#     docs_url="/docs",
#     redoc_url="/redoc",
#     openapi_url="/openapi.json"
# )

# # Add CORS middleware
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=settings.CORS_ORIGINS,
#     allow_credentials=settings.CORS_CREDENTIALS,
#     allow_methods=settings.CORS_METHODS,
#     allow_headers=settings.CORS_HEADERS
# )

# # Import and include routers - CORRECTED ORDER
# logger.info("Loading routers...")

# # RAG Router - ADD PREFIX HERE
# try:
    
#     # ✅ CORRECTED: Include WITH prefix
#     app.include_router(rag_router)
#     logger.info("[OK] RAG router loaded")
    
#     # Debug: Print registered routes
#     for route in app.routes:
#         if hasattr(route, 'path') and '/api/rag' in route.path:
#             logger.info(f"  - {route.methods} {route.path}")
            
# except ImportError as e:
#     logger.error(f"[ERROR] RAG router not found: {e}")
#     import traceback
#     traceback.print_exc()
# except Exception as e:
#     logger.error(f"[ERROR] Failed to load RAG router: {e}")
#     import traceback
#     traceback.print_exc()

# # Agent Router
# try:
#     from app.routers.agent_router import agent_router
#     app.include_router(agent_router, prefix="/api/agent", tags=["Agent"])
#     logger.info("[OK] Agent router loaded")
# except ImportError as e:
#     logger.warning(f"Agent router not found: {e}")
# except Exception as e:
#     logger.warning(f"Failed to load agent router: {e}")

# # Graph Router
# try:
#     from app.routers.graph_router import graph_router
#     app.include_router(graph_router, prefix="/api/graph", tags=["Graph"])
#     logger.info("[OK] Graph router loaded")
# except ImportError as e:
#     logger.warning(f"Graph router not found: {e}")
# except Exception as e:
#     logger.warning(f"Failed to load graph router: {e}")

# # Document Router
# try:
#     from app.routers.document_router import document_router
#     app.include_router(document_router, prefix="/api/documents", tags=["Documents"])
#     logger.info("[OK] Document router loaded")
# except ImportError as e:
#     logger.warning(f"Document router not found: {e}")
# except Exception as e:
#     logger.warning(f"Failed to load document router: {e}")

# # Admin Router
# try:
#     from app.routers.admin_router import router as admin_router
#     app.include_router(admin_router, prefix="/api/admin", tags=["Admin"])
#     logger.info("[OK] Admin router loaded")
# except ImportError as e:
#     logger.warning(f"Admin router not found: {e}")
# except Exception as e:
#     logger.warning(f"Failed to load admin router: {e}")

# logger.info("All routers loaded")


# # Root endpoint
# @app.get("/", tags=["Root"])
# async def root():
#     """Root endpoint with API information"""
#     return {
#         "name": settings.API_TITLE,
#         "version": settings.API_VERSION,
#         "description": "Multi-agent RAG system with adaptive strategies",
#         "status": "operational",
#         "features": [
#             "Multi-Agent Collaboration (Researcher + Writer + Critic)",
#             "ReAct Pattern (Reasoning + Acting)",
#             "Adaptive RAG Strategy Selection",
#             "Knowledge Graph RAG",
#             "Multiple RAG Strategies",
#             "Conversation Memory",
#             "Document Processing (PDF, TXT, DOCX, MD)",
#             "PostgreSQL Storage",
#             "ChromaDB Vector Store"
#         ],
#         "endpoints": {
#             "documentation": "/docs",
#             "alternative_docs": "/redoc",
#             "health": "/health",
#             "rag_query": "/api/rag/query",
#             "multi_agent": "/api/rag/multi-agent-query",
#             "upload_document": "/api/rag/upload",
#             "list_documents": "/api/rag/documents",
#             "statistics": "/api/rag/stats"
#         },
#         "powered_by": {
#             "llm": f"Groq ({settings.LLM_MODEL})",
#             "embeddings": settings.EMBEDDING_MODEL,
#             "vector_store": settings.VECTOR_STORE_TYPE.upper(),
#             "database": "PostgreSQL",
#             "framework": "FastAPI"
#         }
#     }


# # Health check endpoint
# @app.get("/health", tags=["Root"])
# async def health_check():
#     """Comprehensive health check endpoint"""
#     try:
#         from app.core.dependencies import get_orchestrator
#         from sqlalchemy import text
        
#         # Check database
#         db_status = "operational"
#         try:
#             with engine.connect() as conn:
#                 conn.execute(text("SELECT 1"))
#         except Exception as e:
#             db_status = f"error: {str(e)}"
        
#         # Get orchestrator stats
#         try:
#             orchestrator = get_orchestrator()
#             stats = orchestrator.get_stats()
#         except Exception as e:
#             logger.error(f"Failed to get orchestrator stats: {e}")
#             stats = {
#                 "total_documents": 0,
#                 "total_chunks": 0,
#                 "graph_nodes": 0,
#                 "graph_edges": 0,
#                 "active_sessions": 0
#             }
        
#         return {
#             "status": "healthy" if db_status == "operational" else "degraded",
#             "timestamp": datetime.now().isoformat(),
#             "version": settings.API_VERSION,
#             "components": {
#                 "llm_service": "operational",
#                 "embedding_service": "operational",
#                 "vector_store": "operational",
#                 "knowledge_graph": "operational" if settings.ENABLE_GRAPH_RAG else "disabled",
#                 "database": db_status,
#                 "agents": "operational" if settings.ENABLE_MULTI_AGENT else "disabled",
#                 "memory": "operational"
#             },
#             "stats": stats,
#             "configuration": {
#                 "llm_model": settings.LLM_MODEL,
#                 "embedding_model": settings.EMBEDDING_MODEL,
#                 "vector_store": settings.VECTOR_STORE_TYPE,
#                 "graph_enabled": settings.ENABLE_GRAPH_RAG,
#                 "multi_agent_enabled": settings.ENABLE_MULTI_AGENT
#             }
#         }
#     except Exception as e:
#         logger.error(f"Health check failed: {e}")
#         return {
#             "status": "unhealthy",
#             "timestamp": datetime.now().isoformat(),
#             "error": str(e)
#         }


# # Global exception handler
# @app.exception_handler(Exception)
# async def global_exception_handler(request, exc):
#     """Handle all unhandled exceptions"""
#     logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
#     return JSONResponse(
#         status_code=500,
#         content={
#             "error": "Internal server error",
#             "message": str(exc),
#             "path": str(request.url),
#             "timestamp": datetime.now().isoformat()
#         }
#     )


# # Debug endpoint to list all routes
# @app.get("/debug/routes", tags=["Debug"])
# async def list_routes():
#     """List all registered routes (for debugging)"""
#     routes = []
#     for route in app.routes:
#         if hasattr(route, 'path') and hasattr(route, 'methods'):
#             routes.append({
#                 "path": route.path,
#                 "methods": list(route.methods),
#                 "name": route.name
#             })
#     return {"total_routes": len(routes), "routes": routes}


# if __name__ == "__main__":
#     import uvicorn
    
#     uvicorn.run(
#         "app.main:app",
#         host="0.0.0.0",
#         port=8000,
#         reload=True,
#         log_level=settings.LOG_LEVEL.lower()
#     )




"""
===================================================================
app/main.py - Unified FastAPI Application (HRM + RAG + ML)
===================================================================
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging.config
from pathlib import Path
from datetime import datetime
import os

from app.core.config import settings, init_db, engine

# Configure logging
Path(settings.LOG_FILE).parent.mkdir(parents=True, exist_ok=True)

logging.config.dictConfig({
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "stream": "ext://sys.stdout"
        },
        "file": {
            "class": "logging.FileHandler",
            "filename": settings.LOG_FILE,
            "formatter": "default",
            "mode": "a"
        }
    },
    "root": {
        "level": settings.LOG_LEVEL,
        "handlers": ["console", "file"]
    }
})

logger = logging.getLogger(__name__)

# Global CNN Model Instance
cnn_model = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events - startup and shutdown"""
    global cnn_model
    
    logger.info("=" * 60)
    logger.info(f"Starting {settings.API_TITLE} v{settings.API_VERSION}")
    logger.info("=" * 60)
    
    # =================================================================
    # DIRECTORY SETUP
    # =================================================================
    directories = [
        "data/vectors",
        "data/graphs",
        "data/documents",
        "logs",
        "uploads",
        "app/ml_models"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        logger.info(f"Directory created: {directory}/")
    
    # =================================================================
    # DATABASE INITIALIZATION (HRM + RAG)
    # =================================================================
    try:
        # Import ORM models for HRM system
        from app.models.user import User
        from app.models.role import Role
        from app.models.permission import Permission
        from app.models.image_category import ImageCategory
        from app.models.image import Image
        
        # Import database setup
        from app.database import engine as hrm_engine, Base
        
        # Create HRM tables
        logger.info("Creating HRM database tables...")
        Base.metadata.create_all(bind=hrm_engine)
        logger.info("[OK] HRM database tables created")
        
        # Initialize RAG database
        init_db()
        logger.info("[OK] RAG database initialized successfully")
    except Exception as e:
        logger.error(f"[ERROR] Database initialization failed: {str(e)}")
        raise
    
    
    
    # =================================================================
    # INITIALIZE RAG ORCHESTRATOR
    # =================================================================
    try:
        from app.core.dependencies import initialize_orchestrator
        initialize_orchestrator()
        logger.info("[OK] RAG Orchestrator initialized")
    except Exception as e:
        logger.error(f"[ERROR] Orchestrator initialization failed: {str(e)}")
    
    # =================================================================
    # HEALTH CHECK
    # =================================================================
    try:
        from app.core.dependencies import check_dependencies_health
        health = check_dependencies_health()
        for service, status in health.items():
            if status == "operational":
                logger.info(f"[OK] {service}: {status}")
            elif status == "disabled":
                logger.info(f"[DISABLED] {service}: {status}")
            else:
                logger.warning(f"[ERROR] {service}: {status}")
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
    
    logger.info("[OK] All services ready")
    logger.info(f"[INFO] API Documentation: http://localhost:8000/docs")
    logger.info("=" * 60)
    
    yield
    
    # =================================================================
    # SHUTDOWN
    # =================================================================
    logger.info("Shutting down application...")
    try:
        engine.dispose()
        logger.info("[OK] Database connections closed")
    except Exception as e:
        logger.error(f"Error during shutdown: {str(e)}")


# =================================================================
# CREATE FASTAPI APP
# =================================================================
app = FastAPI(
    title="Unified HRM + ML + RAG System",
    version="2.0.0",
    description="""
    Comprehensive Business Intelligence Platform
    
    ## HRM System Features
    * User Management & Authentication
    * Employee Profile Management
    * Role-Based Access Control (RBAC)
    * Permission Management
    * Image & Document Management
    
    ## Machine Learning Models
    * House Price Prediction
    * Customer Churn Analysis
    * Car Price Estimation
    * CNN Image Classification (Cats vs Dogs)
    * NLP Sentiment Analysis
    * MNIST Digit Recognition
    * PCA Dimensionality Reduction
    
    ## RAG System Features
    * Document Processing (PDF, TXT, DOCX, MD)
    * Semantic Search with ChromaDB
    * Multiple RAG Strategies (Simple, Agentic, Multi-Agent)
    * Multi-Agent System (Researcher, Writer, Critic)
    * ReAct Pattern (Reasoning + Acting)
    * Knowledge Graph RAG
    * Session Management
    * PostgreSQL Persistence
    
    ## Quick Start
    1. Register/Login: POST /api/auth/register or /api/auth/login
    2. Upload documents: POST /api/rag/upload
    3. Query RAG: POST /api/rag/query
    4. Use ML models: POST /api/ml/{model}/predict
    """,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# =================================================================
# MIDDLEWARE
# =================================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# =================================================================
# STATIC FILES
# =================================================================
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# =================================================================
# IMPORT AND REGISTER ROUTERS
# =================================================================
logger.info("Loading routers...")

# -------------------- HRM ROUTERS --------------------
try:
    from app.routers import auth
    app.include_router(auth.router)
    logger.info("[OK] Auth router loaded")
except Exception as e:
    logger.warning(f"Auth router failed: {e}")

try:
    from app.routers import user
    app.include_router(user.router)
    logger.info("[OK] User router loaded")
except Exception as e:
    logger.warning(f"User router failed: {e}")

try:
    from app.routers import employee
    app.include_router(employee.router)
    logger.info("[OK] Employee router loaded")
except Exception as e:
    logger.warning(f"Employee router failed: {e}")

try:
    from app.routers import role
    app.include_router(role.router)
    logger.info("[OK] Role router loaded")
except Exception as e:
    logger.warning(f"Role router failed: {e}")

try:
    from app.routers import permission
    app.include_router(permission.router)
    logger.info("[OK] Permission router loaded")
except Exception as e:
    logger.warning(f"Permission router failed: {e}")

try:
    from app.routers import image_category
    app.include_router(image_category.router)
    logger.info("[OK] Image Category router loaded")
except Exception as e:
    logger.warning(f"Image Category router failed: {e}")

try:
    from app.routers import image
    app.include_router(image.router)
    logger.info("[OK] Image router loaded")
except Exception as e:
    logger.warning(f"Image router failed: {e}")

# -------------------- ML MODEL ROUTERS --------------------


# -------------------- RAG ROUTERS --------------------
try:
    from app.routers.rag_router import router as rag_router
    app.include_router(rag_router, prefix="/api/rag", tags=["RAG"])
    logger.info("[OK] RAG router loaded")
except Exception as e:
    logger.warning(f"RAG router failed: {e}")

try:
    from app.routers.agent_router import agent_router
    app.include_router(agent_router, prefix="/api/agent", tags=["Agent"])
    logger.info("[OK] Agent router loaded")
except Exception as e:
    logger.warning(f"Agent router failed: {e}")

try:
    from app.routers.graph_router import graph_router
    app.include_router(graph_router, prefix="/api/graph", tags=["Graph"])
    logger.info("[OK] Graph router loaded")
except Exception as e:
    logger.warning(f"Graph router failed: {e}")

try:
    from app.routers.document_router import document_router
    app.include_router(document_router, prefix="/api/documents", tags=["Documents"])
    logger.info("[OK] Document router loaded")
except Exception as e:
    logger.warning(f"Document router failed: {e}")

try:
    from app.routers.admin_router import router as admin_router
    app.include_router(admin_router, prefix="/api/admin", tags=["Admin"])
    logger.info("[OK] Admin router loaded")
except Exception as e:
    logger.warning(f"Admin router failed: {e}")

logger.info("All routers loaded successfully")

# =================================================================
# ROOT ENDPOINTS
# =================================================================
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with comprehensive API information"""
    return {
        "name": "Unified HRM + ML + RAG System",
        "version": "2.0.0",
        "status": "operational",
        "modules": {
            "hrm": {
                "description": "Human Resource Management System",
                "features": ["Authentication", "User Management", "Employee Profiles", "RBAC", "Image Management"]
            },
            "ml": {
                "description": "Machine Learning Models",
                "models": ["House Price", "Churn", "Car Price", "CNN", "MNIST", "NLP Sentiment"]
            },
            "rag": {
                "description": "Retrieval-Augmented Generation",
                "features": ["Multi-Agent", "Knowledge Graph", "Semantic Search", "Session Memory"]
            }
        },
        "endpoints": {
            "documentation": "/docs",
            "alternative_docs": "/redoc",
            "health": "/health",
            "auth": "/api/auth/login",
            "employees": "/api/employees",
            "ml_predict": "/api/ml/{model}/predict",
            "rag_query": "/api/rag/query",
            "upload": "/api/rag/upload"
        }
    }


@app.get("/health", tags=["Root"])
async def health_check():
    """Comprehensive health check for all systems"""
    try:
        from app.core.dependencies import get_orchestrator
        from sqlalchemy import text
        
        # Database health
        db_status = "operational"
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
        except Exception as e:
            db_status = f"error: {str(e)}"
        
        # RAG orchestrator stats
        try:
            orchestrator = get_orchestrator()
            stats = orchestrator.get_stats()
        except Exception:
            stats = {
                "total_documents": 0,
                "total_chunks": 0,
                "active_sessions": 0
            }
        
        # CNN model status
        cnn_status = "loaded" if cnn_model and getattr(cnn_model, 'is_loaded', False) else "not_loaded"
        
        return {
            "status": "healthy" if db_status == "operational" else "degraded",
            "timestamp": datetime.now().isoformat(),
            "version": "2.0.0",
            "components": {
                "hrm_system": "operational",
                "ml_models": "operational",
                "rag_system": "operational",
                "database": db_status,
                "cnn_model": cnn_status,
                "vector_store": "operational",
                "knowledge_graph": "operational" if settings.ENABLE_GRAPH_RAG else "disabled"
            },
            "stats": stats
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


@app.get("/api/hello", tags=["Root"])
def hello():
    """Simple hello endpoint"""
    return {"message": "Hello from Unified API!"}


@app.get("/ping", tags=["Root"])
async def ping():
    """Simple ping endpoint"""
    cnn_status = "loaded" if cnn_model and getattr(cnn_model, 'is_loaded', False) else "not_loaded"
    return {"status": "healthy", "cnn_model_status": cnn_status}


@app.get("/test", tags=["Root"])
def test():
    """Test endpoint"""
    return {"status": "working"}



# =================================================================
# DEBUG ENDPOINT
# =================================================================
@app.get("/debug/routes", tags=["Debug"])
async def list_routes():
    """List all registered routes (for debugging)"""
    routes = []
    for route in app.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            routes.append({
                "path": route.path,
                "methods": list(route.methods),
                "name": getattr(route, 'name', 'unknown')
            })
    return {"total_routes": len(routes), "routes": routes}


# =================================================================
# GLOBAL EXCEPTION HANDLER
# =================================================================
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Handle all unhandled exceptions"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc),
            "path": str(request.url),
            "timestamp": datetime.now().isoformat()
        }
    )


# =================================================================
# MAIN ENTRY POINT
# =================================================================
if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )