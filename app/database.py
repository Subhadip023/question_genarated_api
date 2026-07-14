"""
Database configuration — SQLAlchemy engine, session factory, and declarative Base.
The DATABASE_URL is built from MYSQL_* env vars via app.config.settings.

pool_pre_ping=True   → tests every connection before use; silently reconnects if stale
pool_recycle=55      → recycles connections every 55s (below freesqldatabase.com's ~60s timeout)
pool_size / max_overflow → safe limits for a free-tier DB with max 1 concurrent connection
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,      # ping before each use — auto-reconnects on stale connections
    pool_recycle=55,         # recycle connections every 55s (MySQL drops idle after ~60s)
    pool_size=2,             # max persistent connections in pool
    max_overflow=3,          # extra connections allowed under peak load
    pool_timeout=30,         # seconds to wait for a connection before raising an error
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass
