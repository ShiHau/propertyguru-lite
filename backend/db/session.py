from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.config import settings

# Create database engine with environment-specific configuration
engine = create_engine(
    settings.database_url,
    # SQLite requires check_same_thread=False for async/multi-threaded use
    connect_args={"check_same_thread": False}
    if settings.app_environment == "development"
    else {},
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Dependency injection for database sessions."""

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
