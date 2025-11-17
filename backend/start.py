"""
Start script for FastAPI application with proper exclusions
"""
import uvicorn
import os
import sys
from dotenv import load_dotenv

# Fix Windows console encoding for emojis
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())

# Load environment variables
load_dotenv()

if __name__ == "__main__":
    # Get configuration from environment
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8000"))
    reload = os.getenv("RELOAD", "true").lower() == "true"
    
    print(f"""
╔═══════════════════════════════════════════════════════════╗
║        Advanced Agentic RAG System                        ║
║        Starting FastAPI Server...                         ║
╚═══════════════════════════════════════════════════════════╝

    Server: http://{host}:{port}
    Docs:   http://{host}:{port}/docs
    Reload: {reload}
    """)
    
    # Configure uvicorn with proper exclusions
    config = uvicorn.Config(
        "app.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info",
        reload_excludes=[
            "data/*",           # Exclude data directory (ChromaDB, graphs)
            "*.db",             # Exclude database files
            "*.db-shm",         # Exclude SQLite shared memory
            "*.db-wal",         # Exclude SQLite write-ahead log
            "logs/*",           # Exclude logs
            "uploads/*",        # Exclude uploads
            "*.pyc",            # Exclude Python cache
            "__pycache__/*",    # Exclude pycache
            ".pytest_cache/*",  # Exclude pytest cache
            "*.pkl",            # Exclude pickle files
        ]
    )
    
    server = uvicorn.Server(config)
    server.run()



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

# # Rest of your main.py code continues here...
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
#             "encoding": "utf-8"  # Add encoding here too
#         }
#     },
#     "root": {
#         "level": settings.LOG_LEVEL,
#         "handlers": ["console", "file"]
#     }
# })

# logger = logging.getLogger(__name__)

# # ... rest of your existing code ...