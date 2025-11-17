"""
===================================================================
app/main.py - Fixed Unified FastAPI Application
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
import traceback

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
        logger.error(traceback.format_exc())
        # Don't raise - allow app to continue
    
    # =================================================================
    # INITIALIZE RAG ORCHESTRATOR
    # =================================================================
    try:
        from app.core.dependencies import initialize_orchestrator
        initialize_orchestrator()
        logger.info("[OK] RAG Orchestrator initialized")
    except Exception as e:
        logger.error(f"[ERROR] Orchestrator initialization failed: {str(e)}")
        logger.error(traceback.format_exc())
    
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
        logger.error(traceback.format_exc())
    
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
    allow_origins=["http://localhost:3000", "http://localhost:8000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# =================================================================
# STATIC FILES (mount after routers to avoid conflicts)
# =================================================================
# We'll mount this at the end

# =================================================================
# IMPORT AND REGISTER ROUTERS WITH DETAILED ERROR LOGGING
# =================================================================
logger.info("=" * 60)
logger.info("Loading routers...")
logger.info("=" * 60)

router_configs = [
    # HRM Routers
    ("app.routers.auth", "router", "/api/auth", ["Authentication"]),
    ("app.routers.user", "router", "/api/users", ["Users"]),
    ("app.routers.employee", "router", "/api/employees", ["Employees"]),
    ("app.routers.role", "router", "/api/roles", ["Roles"]),
    ("app.routers.permission", "router", "/api/permissions", ["Permissions"]),
    ("app.routers.image_category", "router", "/api/image-categories", ["ImageCategory"]),
    ("app.routers.image", "router", "/api/images", ["Images"]),
    
    # RAG Routers
    ("app.routers.rag_router", "router", "/api/rag", ["RAG System"]),
    # ("app.routers.agent_router", "agent_router", "/api/agent", ["Agent"]),
    # ("app.routers.graph_router", "graph_router", "/api/graph", ["Graph"]),
    # ("app.routers.document_router", "document_router", "/api/documents", ["Documents"]),
    # ("app.routers.admin_router", "router", "/api/admin", ["Admin"]),
]

loaded_routers = []
failed_routers = []

for module_path, router_name, prefix, tags in router_configs:
    try:
        # Dynamic import
        module = __import__(module_path, fromlist=[router_name])
        router = getattr(module, router_name)
        
        # Include router
        app.include_router(router, prefix=prefix, tags=tags)
        loaded_routers.append(f"{prefix} ({module_path})")
        logger.info(f"✓ [OK] Loaded: {prefix} from {module_path}")
        
    except ImportError as e:
        failed_routers.append(f"{prefix} - Import Error: {str(e)}")
        logger.error(f"✗ [IMPORT ERROR] {module_path}: {str(e)}")
        logger.error(traceback.format_exc())
        
    except AttributeError as e:
        failed_routers.append(f"{prefix} - Attribute Error: {str(e)}")
        logger.error(f"✗ [ATTRIBUTE ERROR] {module_path}.{router_name}: {str(e)}")
        logger.error(traceback.format_exc())
        
    except Exception as e:
        failed_routers.append(f"{prefix} - {type(e).__name__}: {str(e)}")
        logger.error(f"✗ [ERROR] {module_path}: {type(e).__name__} - {str(e)}")
        logger.error(traceback.format_exc())

logger.info("=" * 60)
logger.info(f"Router Loading Summary:")
logger.info(f"  ✓ Loaded: {len(loaded_routers)}")
logger.info(f"  ✗ Failed: {len(failed_routers)}")
logger.info("=" * 60)

if failed_routers:
    logger.warning("Failed routers:")
    for failed in failed_routers:
        logger.warning(f"  - {failed}")

# =================================================================
# MOUNT STATIC FILES (after routers)
# =================================================================
try:
    app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
    logger.info("[OK] Static files mounted at /uploads")
except Exception as e:
    logger.error(f"[ERROR] Failed to mount static files: {e}")

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
        "message": "API is running successfully",
        "loaded_routers": len(loaded_routers),
        "failed_routers": len(failed_routers),
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
            "routes": "/debug/routes",
            "auth": "/api/auth/login",
            "employees": "/api/employees",
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
            "routers": {
                "loaded": len(loaded_routers),
                "failed": len(failed_routers),
                "loaded_routes": loaded_routers,
                "failed_routes": failed_routers
            },
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
    return {"message": "Hello from Unified API!", "status": "working"}


@app.get("/ping", tags=["Root"])
async def ping():
    """Simple ping endpoint"""
    cnn_status = "loaded" if cnn_model and getattr(cnn_model, 'is_loaded', False) else "not_loaded"
    return {
        "status": "healthy", 
        "cnn_model_status": cnn_status,
        "message": "pong"
    }


@app.get("/test", tags=["Root"])
def test():
    """Test endpoint"""
    return {
        "status": "working",
        "routers_loaded": len(loaded_routers),
        "routers_failed": len(failed_routers)
    }


# =================================================================
# DEBUG ENDPOINTS
# =================================================================
@app.get("/debug/routes", tags=["Debug"])
async def list_routes():
    """List all registered routes (for debugging)"""
    routes = []
    for route in app.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            routes.append({
                "path": route.path,
                "methods": list(route.methods) if route.methods else [],
                "name": getattr(route, 'name', 'unknown'),
                "tags": getattr(route, 'tags', [])
            })
    
    # Group by prefix
    grouped = {}
    for route in routes:
        prefix = route['path'].split('/')[1] if len(route['path'].split('/')) > 1 else 'root'
        if prefix not in grouped:
            grouped[prefix] = []
        grouped[prefix].append(route)
    
    return {
        "total_routes": len(routes),
        "loaded_routers": len(loaded_routers),
        "failed_routers": len(failed_routers),
        "routes_by_prefix": grouped,
        "all_routes": routes,
        "failed_router_details": failed_routers
    }


@app.get("/debug/info", tags=["Debug"])
async def debug_info():
    """Detailed debug information"""
    return {
        "app_title": app.title,
        "app_version": app.version,
        "loaded_routers": loaded_routers,
        "failed_routers": failed_routers,
        "total_routes": len(app.routes),
        "settings": {
            "log_level": settings.LOG_LEVEL,
            "api_title": settings.API_TITLE,
            "api_version": settings.API_VERSION,
        }
    }


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
            "type": type(exc).__name__,
            "path": str(request.url),
            "timestamp": datetime.now().isoformat()
        }
    )


# =================================================================
# STARTUP EVENT - Print Route Summary
# =================================================================
@app.on_event("startup")
async def startup_event():
    """Additional startup logging"""
    logger.info("=" * 60)
    logger.info("Application Startup Complete")
    logger.info(f"Total Routes Registered: {len(app.routes)}")
    logger.info(f"Loaded Routers: {len(loaded_routers)}")
    logger.info(f"Failed Routers: {len(failed_routers)}")
    logger.info("=" * 60)


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


import logging
import sys

# Fix Unicode logging issue
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('logs/app.log', encoding='utf-8')
    ]
)

# """
# ===================================================================
# app/main.py - Fixed Unified FastAPI Application
# ===================================================================
# """
# # ============================================
# # CRITICAL: Fix encoding BEFORE any other imports
# # ============================================
# import sys
# import io

# if sys.platform == 'win32':
#     if hasattr(sys.stdout, 'buffer'):
#         sys.stdout = io.TextIOWrapper(
#             sys.stdout.buffer, 
#             encoding='utf-8', 
#             errors='replace',
#             line_buffering=True
#         )
#     if hasattr(sys.stderr, 'buffer'):
#         sys.stderr = io.TextIOWrapper(
#             sys.stderr.buffer, 
#             encoding='utf-8', 
#             errors='replace',
#             line_buffering=True
#         )

# # NOW import everything else
# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.staticfiles import StaticFiles
# from fastapi.responses import JSONResponse
# from contextlib import asynccontextmanager
# import logging.config
# from pathlib import Path
# from datetime import datetime
# import os
# import traceback

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
#             "mode": "a",
#             "encoding": "utf-8"
#         }
#     },
#     "root": {
#         "level": settings.LOG_LEVEL,
#         "handlers": ["console", "file"]
#     }
# })

# logger = logging.getLogger(__name__)

# # Global CNN Model Instance
# cnn_model = None


# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     """Application lifespan events - startup and shutdown"""
#     global cnn_model
    
#     logger.info("=" * 60)
#     logger.info(f"Starting {settings.API_TITLE} v{settings.API_VERSION}")
#     logger.info("=" * 60)
    
#     # =================================================================
#     # DIRECTORY SETUP
#     # =================================================================
#     directories = [
#         "data/vectors",
#         "data/graphs",
#         "data/documents",
#         "logs",
#         "uploads",
#         "app/ml_models"
#     ]
    
#     for directory in directories:
#         Path(directory).mkdir(parents=True, exist_ok=True)
#         logger.info(f"Directory created: {directory}/")
    
#     # =================================================================
#     # DATABASE INITIALIZATION (HRM + RAG)
#     # =================================================================
#     try:
#         # Import ORM models for HRM system
#         from app.models.user import User
#         from app.models.role import Role
#         from app.models.permission import Permission
#         from app.models.image_category import ImageCategory
#         from app.models.image import Image
        
#         # Import database setup
#         from app.database import engine as hrm_engine, Base
        
#         # Create HRM tables
#         logger.info("Creating HRM database tables...")
#         Base.metadata.create_all(bind=hrm_engine)
#         logger.info("[OK] HRM database tables created")
        
#         # Initialize RAG database
#         init_db()
#         logger.info("[OK] RAG database initialized successfully")
#     except Exception as e:
#         logger.error(f"[ERROR] Database initialization failed: {str(e)}")
#         logger.error(traceback.format_exc())
#         # Don't raise - allow app to continue
    
#     # =================================================================
#     # INITIALIZE RAG ORCHESTRATOR
#     # =================================================================
#     try:
#         from app.core.dependencies import initialize_orchestrator
#         initialize_orchestrator()
#         logger.info("[OK] RAG Orchestrator initialized")
#     except Exception as e:
#         logger.error(f"[ERROR] Orchestrator initialization failed: {str(e)}")
#         logger.error(traceback.format_exc())
    
#     # =================================================================
#     # HEALTH CHECK
#     # =================================================================
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
#         logger.error(traceback.format_exc())
    
#     logger.info("[OK] All services ready")
#     logger.info(f"[INFO] API Documentation: http://localhost:8000/docs")
#     logger.info("=" * 60)
    
#     yield
    
#     # =================================================================
#     # SHUTDOWN
#     # =================================================================
#     logger.info("Shutting down application...")
#     try:
#         engine.dispose()
#         logger.info("[OK] Database connections closed")
#     except Exception as e:
#         logger.error(f"Error during shutdown: {str(e)}")


# # =================================================================
# # CREATE FASTAPI APP
# # =================================================================
# app = FastAPI(
#     title="Unified HRM + ML + RAG System",
#     version="2.0.0",
#     description="""
#     Comprehensive Business Intelligence Platform
    
#     ## HRM System Features
#     * User Management & Authentication
#     * Employee Profile Management
#     * Role-Based Access Control (RBAC)
#     * Permission Management
#     * Image & Document Management
    
#     ## Machine Learning Models
#     * House Price Prediction
#     * Customer Churn Analysis
#     * Car Price Estimation
#     * CNN Image Classification (Cats vs Dogs)
#     * NLP Sentiment Analysis
#     * MNIST Digit Recognition
#     * PCA Dimensionality Reduction
    
#     ## RAG System Features
#     * Document Processing (PDF, TXT, DOCX, MD)
#     * Semantic Search with ChromaDB
#     * Multiple RAG Strategies (Simple, Agentic, Multi-Agent)
#     * Multi-Agent System (Researcher, Writer, Critic)
#     * ReAct Pattern (Reasoning + Acting)
#     * Knowledge Graph RAG
#     * Session Management
#     * PostgreSQL Persistence
    
#     ## Quick Start
#     1. Register/Login: POST /api/auth/register or /api/auth/login
#     2. Upload documents: POST /api/rag/upload
#     3. Query RAG: POST /api/rag/query
#     4. Use ML models: POST /api/ml/{model}/predict
#     """,
#     lifespan=lifespan,
#     docs_url="/docs",
#     redoc_url="/redoc",
#     openapi_url="/openapi.json"
# )

# # =================================================================
# # MIDDLEWARE
# # =================================================================
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://localhost:3000", "http://localhost:8000", "*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"]
# )

# # =================================================================
# # STATIC FILES (mount after routers to avoid conflicts)
# # =================================================================
# # We'll mount this at the end

# # =================================================================
# # IMPORT AND REGISTER ROUTERS WITH DETAILED ERROR LOGGING
# # =================================================================
# logger.info("=" * 60)
# logger.info("Loading routers...")
# logger.info("=" * 60)

# router_configs = [
#     # HRM Routers
#     ("app.routers.auth", "router", "/api/auth", ["Authentication"]),
#     ("app.routers.user", "router", "/api/users", ["Users"]),
#     ("app.routers.employee", "router", "/api/employees", ["Employees"]),
#     ("app.routers.role", "router", "/api/roles", ["Roles"]),
#     ("app.routers.permission", "router", "/api/permissions", ["Permissions"]),
#     ("app.routers.image_category", "router", "/api/image-categories", ["ImageCategory"]),
#     ("app.routers.image", "router", "/api/images", ["Images"]),
    
#     # RAG Routers
#     ("app.routers.rag_router", "router", "/api/rag", ["RAG System"]),
#     # ("app.routers.agent_router", "agent_router", "/api/agent", ["Agent"]),
#     # ("app.routers.graph_router", "graph_router", "/api/graph", ["Graph"]),
#     # ("app.routers.document_router", "document_router", "/api/documents", ["Documents"]),
#     # ("app.routers.admin_router", "router", "/api/admin", ["Admin"]),
# ]

# loaded_routers = []
# failed_routers = []

# for module_path, router_name, prefix, tags in router_configs:
#     try:
#         # Dynamic import
#         module = __import__(module_path, fromlist=[router_name])
#         router = getattr(module, router_name)
        
#         # Include router
#         app.include_router(router, prefix=prefix, tags=tags)
#         loaded_routers.append(f"{prefix} ({module_path})")
#         logger.info(f"✓ [OK] Loaded: {prefix} from {module_path}")
        
#     except ImportError as e:
#         failed_routers.append(f"{prefix} - Import Error: {str(e)}")
#         logger.error(f"✗ [IMPORT ERROR] {module_path}: {str(e)}")
#         logger.error(traceback.format_exc())
        
#     except AttributeError as e:
#         failed_routers.append(f"{prefix} - Attribute Error: {str(e)}")
#         logger.error(f"✗ [ATTRIBUTE ERROR] {module_path}.{router_name}: {str(e)}")
#         logger.error(traceback.format_exc())
        
#     except Exception as e:
#         failed_routers.append(f"{prefix} - {type(e).__name__}: {str(e)}")
#         logger.error(f"✗ [ERROR] {module_path}: {type(e).__name__} - {str(e)}")
#         logger.error(traceback.format_exc())

# logger.info("=" * 60)
# logger.info(f"Router Loading Summary:")
# logger.info(f"  ✓ Loaded: {len(loaded_routers)}")
# logger.info(f"  ✗ Failed: {len(failed_routers)}")
# logger.info("=" * 60)

# if failed_routers:
#     logger.warning("Failed routers:")
#     for failed in failed_routers:
#         logger.warning(f"  - {failed}")

# # =================================================================
# # MOUNT STATIC FILES (after routers)
# # =================================================================
# try:
#     app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
#     logger.info("[OK] Static files mounted at /uploads")
# except Exception as e:
#     logger.error(f"[ERROR] Failed to mount static files: {e}")

# # =================================================================
# # ROOT ENDPOINTS
# # =================================================================
# @app.get("/", tags=["Root"])
# async def root():
#     """Root endpoint with comprehensive API information"""
#     return {
#         "name": "Unified HRM + ML + RAG System",
#         "version": "2.0.0",
#         "status": "operational",
#         "message": "API is running successfully",
#         "loaded_routers": len(loaded_routers),
#         "failed_routers": len(failed_routers),
#         "modules": {
#             "hrm": {
#                 "description": "Human Resource Management System",
#                 "features": ["Authentication", "User Management", "Employee Profiles", "RBAC", "Image Management"]
#             },
#             "ml": {
#                 "description": "Machine Learning Models",
#                 "models": ["House Price", "Churn", "Car Price", "CNN", "MNIST", "NLP Sentiment"]
#             },
#             "rag": {
#                 "description": "Retrieval-Augmented Generation",
#                 "features": ["Multi-Agent", "Knowledge Graph", "Semantic Search", "Session Memory"]
#             }
#         },
#         "endpoints": {
#             "documentation": "/docs",
#             "alternative_docs": "/redoc",
#             "health": "/health",
#             "routes": "/debug/routes",
#             "auth": "/api/auth/login",
#             "employees": "/api/employees",
#             "rag_query": "/api/rag/query",
#             "upload": "/api/rag/upload"
#         }
#     }


# @app.get("/health", tags=["Root"])
# async def health_check():
#     """Comprehensive health check for all systems"""
#     try:
#         from app.core.dependencies import get_orchestrator
#         from sqlalchemy import text
        
#         # Database health
#         db_status = "operational"
#         try:
#             with engine.connect() as conn:
#                 conn.execute(text("SELECT 1"))
#         except Exception as e:
#             db_status = f"error: {str(e)}"
        
#         # RAG orchestrator stats
#         try:
#             orchestrator = get_orchestrator()
#             stats = orchestrator.get_stats()
#         except Exception:
#             stats = {
#                 "total_documents": 0,
#                 "total_chunks": 0,
#                 "active_sessions": 0
#             }
        
#         # CNN model status
#         cnn_status = "loaded" if cnn_model and getattr(cnn_model, 'is_loaded', False) else "not_loaded"
        
#         return {
#             "status": "healthy" if db_status == "operational" else "degraded",
#             "timestamp": datetime.now().isoformat(),
#             "version": "2.0.0",
#             "routers": {
#                 "loaded": len(loaded_routers),
#                 "failed": len(failed_routers),
#                 "loaded_routes": loaded_routers,
#                 "failed_routes": failed_routers
#             },
#             "components": {
#                 "hrm_system": "operational",
#                 "ml_models": "operational",
#                 "rag_system": "operational",
#                 "database": db_status,
#                 "cnn_model": cnn_status,
#                 "vector_store": "operational",
#                 "knowledge_graph": "operational" if settings.ENABLE_GRAPH_RAG else "disabled"
#             },
#             "stats": stats
#         }
#     except Exception as e:
#         logger.error(f"Health check failed: {e}")
#         return {
#             "status": "unhealthy",
#             "error": str(e),
#             "timestamp": datetime.now().isoformat()
#         }


# @app.get("/api/hello", tags=["Root"])
# def hello():
#     """Simple hello endpoint"""
#     return {"message": "Hello from Unified API!", "status": "working"}


# @app.get("/ping", tags=["Root"])
# async def ping():
#     """Simple ping endpoint"""
#     cnn_status = "loaded" if cnn_model and getattr(cnn_model, 'is_loaded', False) else "not_loaded"
#     return {
#         "status": "healthy", 
#         "cnn_model_status": cnn_status,
#         "message": "pong"
#     }


# @app.get("/test", tags=["Root"])
# def test():
#     """Test endpoint"""
#     return {
#         "status": "working",
#         "routers_loaded": len(loaded_routers),
#         "routers_failed": len(failed_routers)
#     }


# # =================================================================
# # DEBUG ENDPOINTS
# # =================================================================
# @app.get("/debug/routes", tags=["Debug"])
# async def list_routes():
#     """List all registered routes (for debugging)"""
#     routes = []
#     for route in app.routes:
#         if hasattr(route, 'path') and hasattr(route, 'methods'):
#             routes.append({
#                 "path": route.path,
#                 "methods": list(route.methods) if route.methods else [],
#                 "name": getattr(route, 'name', 'unknown'),
#                 "tags": getattr(route, 'tags', [])
#             })
    
#     # Group by prefix
#     grouped = {}
#     for route in routes:
#         prefix = route['path'].split('/')[1] if len(route['path'].split('/')) > 1 else 'root'
#         if prefix not in grouped:
#             grouped[prefix] = []
#         grouped[prefix].append(route)
    
#     return {
#         "total_routes": len(routes),
#         "loaded_routers": len(loaded_routers),
#         "failed_routers": len(failed_routers),
#         "routes_by_prefix": grouped,
#         "all_routes": routes,
#         "failed_router_details": failed_routers
#     }


# @app.get("/debug/info", tags=["Debug"])
# async def debug_info():
#     """Detailed debug information"""
#     return {
#         "app_title": app.title,
#         "app_version": app.version,
#         "loaded_routers": loaded_routers,
#         "failed_routers": failed_routers,
#         "total_routes": len(app.routes),
#         "settings": {
#             "log_level": settings.LOG_LEVEL,
#             "api_title": settings.API_TITLE,
#             "api_version": settings.API_VERSION,
#         }
#     }


# # =================================================================
# # GLOBAL EXCEPTION HANDLER
# # =================================================================
# @app.exception_handler(Exception)
# async def global_exception_handler(request, exc):
#     """Handle all unhandled exceptions"""
#     logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
#     return JSONResponse(
#         status_code=500,
#         content={
#             "error": "Internal server error",
#             "message": str(exc),
#             "type": type(exc).__name__,
#             "path": str(request.url),
#             "timestamp": datetime.now().isoformat()
#         }
#     )


# # =================================================================
# # STARTUP EVENT - Print Route Summary
# # =================================================================
# @app.on_event("startup")
# async def startup_event():
#     """Additional startup logging"""
#     logger.info("=" * 60)
#     logger.info("Application Startup Complete")
#     logger.info(f"Total Routes Registered: {len(app.routes)}")
#     logger.info(f"Loaded Routers: {len(loaded_routers)}")
#     logger.info(f"Failed Routers: {len(failed_routers)}")
#     logger.info("=" * 60)


# # =================================================================
# # MAIN ENTRY POINT
# # =================================================================
# if __name__ == "__main__":
#     import uvicorn
    
#     uvicorn.run(
#         "app.main:app",
#         host="0.0.0.0",
#         port=8000,
#         reload=True,
#         log_level="info"
#     )