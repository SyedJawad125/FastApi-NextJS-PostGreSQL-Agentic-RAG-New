# app/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from contextlib import contextmanager
from app.core.config import settings  # or from app.config import settings (depending on your project)
import logging

# -------------------------------------------------------------------
# 🔧 Logging configuration
# -------------------------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -------------------------------------------------------------------
# 🗄️ Database configuration
# -------------------------------------------------------------------
# PostgreSQL database URL from your settings or .env file
DATABASE_URL = getattr(settings, "SQLALCHEMY_DATABASE_URL", None)

if not DATABASE_URL:
    raise ValueError("❌ DATABASE_URL or SQLALCHEMY_DATABASE_URL not found in settings!")

# Create SQLAlchemy engine for PostgreSQL
engine = create_engine(
    DATABASE_URL,
    echo=True,                # Show SQL queries (set False in production)
    pool_pre_ping=True,       # Checks connection before using it
    pool_size=10,
    max_overflow=20
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

# -------------------------------------------------------------------
# ⚙️ Database utility functions
# -------------------------------------------------------------------
def init_db():
    """Initialize all database tables."""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created successfully.")
    except Exception as e:
        logger.error(f"❌ Error creating database tables: {e}")
        raise

def get_db() -> Session:
    """FastAPI dependency - provide DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@contextmanager
def get_db_context():
    """Context manager for DB session."""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

# -------------------------------------------------------------------
# 🔍 Verify connection at startup
# -------------------------------------------------------------------
try:
    with engine.connect() as conn:
        logger.info(f"✅ Connected to PostgreSQL at: {DATABASE_URL}")
except Exception as e:
    logger.error(f"❌ Failed to connect to PostgreSQL: {e}")
    raise
