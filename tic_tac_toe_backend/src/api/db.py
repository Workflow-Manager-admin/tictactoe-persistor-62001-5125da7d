# db.py - DB engine/session management and helpers

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .config import settings
from .models import Base

# Use env-derived SQLAlchemy database URI
SQLALCHEMY_DATABASE_URL = settings.sqlalchemy_db_uri()
engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


# PUBLIC_INTERFACE
def init_db():
    """Creates tables if not present (usually one-time or for development)."""
    Base.metadata.create_all(bind=engine)


# PUBLIC_INTERFACE
def get_db():
    """Dependency that provides a transactional scope for DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
